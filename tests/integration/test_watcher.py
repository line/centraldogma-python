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
import json
import os
import time
from concurrent.futures import Future
from concurrent.futures import TimeoutError

import pytest

from centraldogma.data import Commit, Change, ChangeType
from centraldogma.data.revision import Revision
from centraldogma.dogma import Dogma
from centraldogma.query import Query
from centraldogma.watcher import Watcher, Latest

dogma = Dogma()
project_name = "TestProject"
repo_name = "TestRepository"


@pytest.fixture(scope="module")
def run_around_test():
    dogma.create_project(project_name)
    dogma.create_repository(project_name, repo_name)
    yield
    dogma.remove_repository(project_name, repo_name)
    dogma.purge_repository(project_name, repo_name)
    dogma.remove_project(project_name)
    dogma.purge_project(project_name)


@pytest.mark.skipif(
    os.getenv("INTEGRATION_TEST", "false").lower() != "true",
    reason="Integration tests are disabled. Use `INTEGRATION_TEST=true pytest` to enable them.",
)
@pytest.mark.integration
class TestWatcher:
    def test_repository_watcher(self, run_around_test):
        watcher: Watcher[Revision] = dogma.repository_watcher(
            project_name, repo_name, "/**"
        )
        with watcher:
            future: Future[Revision] = Future()

            def listener(revision1: Revision, _: Revision) -> None:
                future.set_result(revision1)

            watcher.watch(listener)
            commit = Commit("Upsert1 test.txt")
            upsert_text = Change("/path/test.txt", ChangeType.UPSERT_TEXT, "foo")
            result = dogma.push(project_name, repo_name, commit, [upsert_text])
            watched_revision = future.result()
            assert result.revision == watched_revision.major

            future = Future()
            commit = Commit("Upsert2 test.txt")
            upsert_text = Change("/path/test.txt", ChangeType.UPSERT_TEXT, "bar")
            result = dogma.push(project_name, repo_name, commit, [upsert_text])
            watched_revision = future.result()
            assert result.revision == watched_revision.major

            future = Future()
            commit = Commit("Upsert3 test.txt")
            upsert_text = Change("/path/test.txt", ChangeType.UPSERT_TEXT, "qux")
            result = dogma.push(project_name, repo_name, commit, [upsert_text])
            watched_revision = future.result()
            assert result.revision == watched_revision.major

    def test_file_watcher(self, run_around_test):

        commit = Commit("Upsert1 test.json")
        upsert_text = Change(
            "/test.json", ChangeType.UPSERT_JSON, {"a": 1, "b": 2, "c": 3}
        )
        dogma.push(project_name, repo_name, commit, [upsert_text])

        with dogma.file_watcher(
            project_name,
            repo_name,
            Query.json_path("/test.json", ["$.a"]),
            lambda j: json.dumps(j),
        ) as watcher:
            future: Future[Revision] = Future()

            def listener(revision1: Revision, _: str) -> None:
                future.set_result(revision1)

            watcher.watch(listener)
            commit = Commit("Upsert1 test.json")
            upsert_text = Change(
                "/test.json", ChangeType.UPSERT_JSON, {"b": 12, "c": 3}
            )
            dogma.push(project_name, repo_name, commit, [upsert_text])

            with pytest.raises(TimeoutError):
                future.result(timeout=1)

            upsert_text = Change(
                "/test.json", ChangeType.UPSERT_JSON, {"a": 11, "b": 12, "c": 33}
            )
            result = dogma.push(project_name, repo_name, commit, [upsert_text])
            watched_revision = future.result()
            assert result.revision == watched_revision.major

            future = Future()
            commit = Commit("Upsert2 test.json")
            upsert_text = Change(
                "/test.json", ChangeType.UPSERT_JSON, {"a": 21, "b": 12, "c": 33}
            )
            result = dogma.push(project_name, repo_name, commit, [upsert_text])
            watched_revision = future.result()
            assert result.revision == watched_revision.major

            # As the content of 'a' has not been changed, the push event should not trigger 'listener'.
            future = Future()
            commit = Commit("Upsert3 test.json")
            upsert_text = Change(
                "/test.json", ChangeType.UPSERT_JSON, {"a": 21, "b": 22, "c": 33}
            )
            dogma.push(project_name, repo_name, commit, [upsert_text])
            with pytest.raises(TimeoutError):
                future.result(timeout=1)

    def test_file_watcher_multiple_json_path(self):
        commit = Commit("Upsert test.json")
        upsert_json = Change("/test.json", ChangeType.UPSERT_JSON, {"b": 2})
        dogma.push(project_name, repo_name, commit, [upsert_json])

        with dogma.file_watcher(
            project_name,
            repo_name,
            # Applies a series of JSON patches that will be translated to '$.a.c'
            Query.json_path("/test.json", ["$.a", "$.c"]),
            lambda j: json.dumps(j),
        ) as watcher:
            future: Future[Revision] = Future()

            def listener(revision1: Revision, _: str) -> None:
                future.set_result(revision1)

            watcher.watch(listener)
            # Entity not found.
            with pytest.raises(TimeoutError):
                future.result(timeout=2)

            future: Future[Revision] = Future()
            json_patch = Change(
                "/test.json",
                ChangeType.APPLY_JSON_PATCH,
                [{"op": "replace", "path": "/b", "value": 12}],
            )
            dogma.push(project_name, repo_name, commit, [json_patch])

            # $.a.c has not changed.
            with pytest.raises(TimeoutError):
                future.result(timeout=2)

            future: Future[Revision] = Future()
            json_patch = Change(
                "/test.json",
                ChangeType.APPLY_JSON_PATCH,
                [{"op": "add", "path": "/a", "value": {"a": 1}}],
            )
            dogma.push(project_name, repo_name, commit, [json_patch])

            # $.a.c has not changed.
            with pytest.raises(TimeoutError):
                future.result(timeout=2)

            future: Future[Revision] = Future()
            json_patch = Change(
                "/test.json",
                ChangeType.APPLY_JSON_PATCH,
                [{"op": "add", "path": "/a", "value": {"c": 3}}],
            )
            result = dogma.push(project_name, repo_name, commit, [json_patch])
            watched_revision = future.result()
            assert result.revision == watched_revision.major

    def test_await_init_value(self, run_around_test):
        with dogma.file_watcher(
            project_name,
            repo_name,
            Query.json("/foo.json"),
            lambda j: json.dumps(j),
        ) as watcher:

            future: Future[Latest[str]] = watcher.initial_value_future()
            with pytest.raises(TimeoutError):
                future.result(timeout=1)
            assert not watcher.latest()

            commit = Commit("Upsert foo.json")
            upsert_text = Change("/foo.json", ChangeType.UPSERT_JSON, {"a": 1})
            dogma.push(project_name, repo_name, commit, [upsert_text])
            latest: Latest[str] = future.result()
            assert latest.value == '{"a": 1}'
            assert watcher.latest() == latest

    def test_not_modified_repository_watcher(self, run_around_test):
        """It verifies that a watcher keep watching well even after `NOT_MODIFIED`."""
        timeout_millis = 1000
        timeout_second = timeout_millis / 1000

        # pass short timeout millis for testing purpose.
        watcher: Watcher[Revision] = dogma.repository_watcher(
            project_name, repo_name, "/**", timeout_millis=timeout_millis
        )

        # wait until watcher get `NOT_MODIFIED` at least once.
        time.sleep(4 * timeout_second)

        commit = Commit("Upsert modify.txt")
        upsert_text = Change("/path/modify.txt", ChangeType.UPSERT_TEXT, "modified")
        result = dogma.push(project_name, repo_name, commit, [upsert_text])

        # wait until watcher watch latest.
        time.sleep(4 * timeout_second)

        assert result.revision == watcher.latest().revision.major
