#  Copyright 2021 LINE Corporation
#
#  LINE Corporation licenses this file to you under the Apache License,
#  version 2.0 (the "License"); you may not use this file except in compliance
#  with the License. You may obtain a copy of the License at:
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
import itertools
import logging
import math
import threading
import time
from concurrent.futures import Future
from enum import Enum, auto
from random import randrange
from threading import Thread, Lock
from typing import TypeVar, Callable, Optional, List

from centraldogma.data.revision import Revision
from centraldogma.dogma import Dogma
from centraldogma.query import Query
from centraldogma.watcher import Watcher, Latest

S = TypeVar("S")
T = TypeVar("T")


class WatchState(Enum):
    INIT = auto()
    STARTED = auto()
    STOPPED = auto()


_DELAY_ON_SUCCESS_MILLIS = 1000  # 1 second
_MIN_INTERVAL_MILLIS = _DELAY_ON_SUCCESS_MILLIS * 2  # 2 seconds
_MAX_INTERVAL_MILLIS = 1 * 60 * 1000  # 1 minute
_JITTER_RATE = 0.2
_THREAD_ID = itertools.count()


class AbstractWatcher(Watcher[T]):
    _latest: Optional[Latest[T]] = None
    _state: WatchState = WatchState.INIT
    _initial_value_future = Future()
    _update_listeners: List[Callable[[Revision, T], None]] = []
    _thread: Optional[threading.Thread] = None
    _lock: Lock = threading.Lock()

    def __init__(
        self,
        dogma: Dogma,
        project_name: str,
        repo_name: str,
        path_pattern: str,
        function: Callable[[S], T],
    ):
        self.dogma = dogma
        self.project_name = project_name
        self.repo_name = repo_name
        self.path_pattern = path_pattern
        self.function = function

    def start(self):
        with self._lock:
            if self._state == WatchState.INIT:
                # FIXME(ikhoon): Replace Thread with Coroutine of asyncio once AsyncClient is implemented.
                self._thread = Thread(
                    target=self._schedule_watch,
                    args=(0,),
                    name=f"centraldogma-watcher-{next(_THREAD_ID)}",
                    daemon=True,
                )
                self._thread.start()

    def close(self) -> None:
        self._state = WatchState.STOPPED

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def latest(self) -> Latest[T]:
        return self._latest

    def watch(self, listener: Callable[[Revision, T], None]) -> None:
        self._update_listeners.append(listener)

        if self._latest:
            listener(self._latest.revision, self._latest.value)

    def _schedule_watch(self, num_attempts_so_far: int) -> None:
        if self._is_stopped():
            return

        if num_attempts_so_far == 0:
            delay = _DELAY_ON_SUCCESS_MILLIS if self._latest is None else 0
        else:
            delay = self._next_delay_millis(num_attempts_so_far)

        # FIXME(ikhoon): Replace asyncio.sleep() after AsyncClient is implemented.
        time.sleep(delay / 1000)
        self._watch(num_attempts_so_far)
        return None

    def _watch(self, num_attempts_so_far: int) -> None:
        if self._is_stopped():
            return

        last_known_revision = self._latest.revision if self._latest else Revision.init()
        try:
            new_latest = self._do_watch(last_known_revision)
            if new_latest:
                old_latest = self._latest
                self._latest = new_latest
                logging.debug(
                    f"watcher noticed updated file %s/%s%s: rev=%s",
                    self.project_name,
                    self.repo_name,
                    self.path_pattern,
                    new_latest.revision,
                )
                self.notify_listeners()
                if not old_latest:
                    self._initial_value_future.set_result(new_latest)

                # Watch again for the next change.
                self._schedule_watch(0)
        except Exception as ex:
            logged = False
            # TODO(ikhoon): Leave proper log messages

            if not logged:
                logging.warning(
                    "Failed to watch a file (%s/%s%s) at Central Dogma; trying again\n%s",
                    self.project_name,
                    self.repo_name,
                    self.path_pattern,
                    ex,
                )
            self._schedule_watch(num_attempts_so_far + 1)
            return

    def _do_watch(self, last_known_revision) -> Optional[Latest[T]]:
        pass

    def notify_listeners(self):
        if self._is_stopped():
            # Do not notify after stopped.
            return

        latest = self._latest
        for listener in self._update_listeners:
            try:
                listener(latest.revision, latest.value)
            except Exception as ex:
                logging.warning(
                    "Exception thrown for watcher (%s/%s%s): rev=%s\n%s",
                    self.project_name,
                    self.repo_name,
                    self.path_pattern,
                    latest.revision,
                    ex,
                )

    def _is_stopped(self) -> bool:
        return self._state == WatchState.STOPPED

    @staticmethod
    def _next_delay_millis(num_attempts_so_far: int) -> int:
        if num_attempts_so_far == 1:
            next_delay_millis = _MIN_INTERVAL_MILLIS
        else:
            delay = _MIN_INTERVAL_MILLIS * math.pow(2.0, num_attempts_so_far - 1)
            next_delay_millis = min(delay, _MAX_INTERVAL_MILLIS)

        min_jitter = int(next_delay_millis * (1 - _JITTER_RATE))
        max_jitter = int(next_delay_millis * (1 + _JITTER_RATE))
        bound = max_jitter - min_jitter + 1
        jitter = randrange(bound)
        return max(0, min_jitter + jitter)


class FileWatcher(AbstractWatcher[T]):
    def __init__(
        self,
        dogma: Dogma,
        project_name: str,
        repo_name: str,
        query: Query[T],
        function: Callable[[S], T],
    ):
        super().__init__(dogma, project_name, repo_name, query.path, function)
        self.query = query

    def _do_watch(self, last_known_revision) -> Optional[Latest[T]]:
        result = self.dogma.watch_file(
            self.project_name, self.repo_name, last_known_revision, self.query
        )
        if not result:
            return None
        return Latest(result.revision, self.function(result.content))


class RepositoryWatcher(AbstractWatcher[T]):
    def __init__(
        self,
        dogma: Dogma,
        project_name: str,
        repo_name: str,
        path_pattern: str,
        function: Callable[[Revision], T],
    ):
        super().__init__(dogma, project_name, repo_name, path_pattern, function)

    def _do_watch(self, last_known_revision) -> Optional[Latest[T]]:
        revision = self.dogma.watch_repository(
            self.project_name, self.repo_name, last_known_revision, self.path_pattern
        )
        if not revision:
            return None
        return Latest(revision, self.function(revision))
