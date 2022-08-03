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

from concurrent.futures import Future
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

from centraldogma.data.revision import Revision

T = TypeVar("T")


@dataclass
class Latest(Generic[T]):
    """A holder of the latest known value and its `Revision` retrieved by `Watcher`."""

    revision: Revision
    value: T


class Watcher(Generic[T]):
    """Watches the changes of a repository or a file."""

    def latest(self) -> Latest[T]:
        """Returns the latest ``Revision`` and value of ``watch_file()`` result."""
        pass

    # TODO(ikhoon): Use Generic `Future[Latest[T]]` when the Python 3.9 becomes the baseline.
    # https://github.com/python/typing/issues/446#issuecomment-623251451
    def initial_value_future(self) -> Future:
        """Returns the ``Future`` which completes a ``Latest[T]`` when the initial value retrieval is done
        successfully.
        """
        pass

    def await_initial_value(self) -> Latest[T]:
        """Waits for the initial value to be available."""
        return self.initial_value_future().result()

    def watch(self, listener: Callable[[Revision, T], None]) -> None:
        """Registers a listener that will be invoked when the value of the watched entry becomes
        available or changes.
        """
        pass

    def close(self) -> None:
        """Stops watching the file specified in the ``Query`` or the path pattern in the repository."""
        pass
