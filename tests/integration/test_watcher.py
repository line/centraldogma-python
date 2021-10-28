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
from concurrent.futures import Future
from concurrent.futures import TimeoutError
from typing import Any

import pytest

from centraldogma.data import Commit, Change, ChangeType
from centraldogma.data.revision import Revision
from centraldogma.query import Query
from centraldogma.watcher import Watcher
from centraldogma.dogma import Dogma

dogma = Dogma()
project_name = "TestProject"
repo_name = "TestRepository"


@pytest.fixture(scope="module")
def run_around_test():
    try:
        dogma.remove_project(project_name)
    except:
        print()
    try:
        dogma.purge_project(project_name)
    except:
        print()

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
def test_repository_watcher(run_around_test):
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


@pytest.mark.skipif(
    os.getenv("INTEGRATION_TEST", "false").lower() != "true",
    reason="Integration tests are disabled. Use `INTEGRATION_TEST=true pytest` to enable them.",
)
@pytest.mark.integration
def test_file_watcher(run_around_test):

    commit = Commit("Upsert1 test.json")
    upsert_text = Change("/test.json", ChangeType.UPSERT_JSON, {"a": 1, "b": 2, "c": 3})
    result = dogma.push(project_name, repo_name, commit, [upsert_text])

    watcher: Watcher[str] = dogma.file_watcher(
        project_name,
        repo_name,
        Query.json_path("/test.json", ["$.a"]),
        lambda j: json.dumps(j),
    )
    with watcher:
        future: Future[Revision] = Future()

        def listener(revision1: Revision, _: str) -> None:
            future.set_result(revision1)

        watcher.watch(listener)
        commit = Commit("Upsert1 test.json")
        upsert_text = Change(
            "/test.json", ChangeType.UPSERT_JSON, {"a": 1, "b": 12, "c": 3}
        )
        dogma.push(project_name, repo_name, commit, [upsert_text])

        with pytest.raises(TimeoutError):
            future.result(timeout=0.5)

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

        future = Future()
        commit = Commit("Upsert3 test.json")
        upsert_text = Change(
            "/test.json", ChangeType.UPSERT_JSON, {"a": 21, "b": 22, "c": 33}
        )
        dogma.push(project_name, repo_name, commit, [upsert_text])
        with pytest.raises(TimeoutError):
            future.result(timeout=0.5)
