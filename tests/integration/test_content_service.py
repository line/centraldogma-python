# Copyright 2021 LINE Corporation
#
# LINE Corporation licenses this file to you under the Apache License,
# version 2.0 (the "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at:
#
#   https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional, Any

import pytest

from centraldogma.data.entry import Entry, EntryType
from centraldogma.data.merge_source import MergeSource
from centraldogma.data.revision import Revision
from centraldogma.dogma import Change, ChangeType, Commit, Dogma
from centraldogma.exceptions import (
    BadRequestException,
    RedundantChangeException,
    ChangeConflictException,
    CentralDogmaException,
    EntryNotFoundException,
    QueryExecutionException,
)
from centraldogma.query import Query

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
class TestContentService:
    def test_content(self, run_around_test):
        files = dogma.list_files(project_name, repo_name)
        assert len(files) == 0

        commit = Commit("Upsert test.json")
        upsert_json = Change("/test .json", ChangeType.UPSERT_JSON, {"foo": "bar"})
        with pytest.raises(BadRequestException):
            dogma.push(project_name, repo_name, commit, [upsert_json])
        upsert_json = Change("/test.json", ChangeType.UPSERT_JSON, {"foo": "bar"})
        ret = dogma.push(project_name, repo_name, commit, [upsert_json])
        assert ret.revision == 2

        with pytest.raises(RedundantChangeException):
            dogma.push(project_name, repo_name, commit, [upsert_json])

        commit = Commit("Upsert test.txt")
        upsert_text = Change("/path/test.txt", ChangeType.UPSERT_TEXT, "foo")
        ret = dogma.push(project_name, repo_name, commit, [upsert_text])
        assert ret.revision == 3

        commit = Commit("Upsert both json and txt")
        upsert_json = Change("/test.json", ChangeType.UPSERT_JSON, {"foo": "bar2"})
        upsert_text = Change("/path/test.txt", ChangeType.UPSERT_TEXT, "foo2")
        ret = dogma.push(project_name, repo_name, commit, [upsert_json, upsert_text])
        assert ret.revision == 4

        commit = Commit("Rename the json")
        rename_json = Change("/test2.json", ChangeType.RENAME, "/test3.json")
        with pytest.raises(ChangeConflictException):
            dogma.push(project_name, repo_name, commit, [rename_json])
        rename_json = Change("/test.json", ChangeType.RENAME, "")

        with pytest.raises(BadRequestException):
            dogma.push(project_name, repo_name, commit, [rename_json])
        rename_json = Change("/test.json", ChangeType.RENAME, "/test2.json")
        ret = dogma.push(project_name, repo_name, commit, [rename_json])
        assert ret.revision == 5

        files = dogma.list_files(project_name, repo_name)
        assert len(files) == 2
        assert set(map(lambda x: x.path, files)) == {"/path", "/test2.json"}
        assert set(map(lambda x: x.type, files)) == {"DIRECTORY", "JSON"}

        commit = Commit("Remove the json")
        remove_json = Change("/test.json", ChangeType.REMOVE)
        with pytest.raises(ChangeConflictException):
            dogma.push(project_name, repo_name, commit, [remove_json])
        remove_json = Change("/test2.json", ChangeType.REMOVE)
        ret = dogma.push(project_name, repo_name, commit, [remove_json])
        assert ret.revision == 6

        with pytest.raises(ChangeConflictException):
            dogma.push(project_name, repo_name, commit, [remove_json])

        files = dogma.list_files(project_name, repo_name)
        assert len(files) == 1

        commit = Commit("Remove the folder")
        remove_folder = Change("/path", ChangeType.REMOVE)
        ret = dogma.push(project_name, repo_name, commit, [remove_folder])
        assert ret.revision == 7

        files = dogma.list_files(project_name, repo_name)
        assert len(files) == 0

    def test_watch_repository(self, run_around_test):
        commit = Commit("Upsert test.json")
        upsert_json = Change("/test.json", ChangeType.UPSERT_JSON, {"foo": "bar"})
        ret = dogma.push(project_name, repo_name, commit, [upsert_json])

        start = datetime.now()
        revision = dogma.watch_repository(
            project_name, repo_name, Revision(ret.revision), "/**", 2000
        )
        end = datetime.now()
        assert not revision  # Not modified
        assert (end - start).seconds >= 1

        with ThreadPoolExecutor(max_workers=1) as e:
            e.submit(self.push_later)
        start = datetime.now()
        revision = dogma.watch_repository(
            project_name, repo_name, Revision(ret.revision), "/**", 4000
        )
        end = datetime.now()
        assert revision.major == ret.revision + 1
        assert (end - start).seconds < 3

    def test_watch_file(self, run_around_test):
        commit = Commit("Upsert test.json")
        upsert_json = Change("/test.json", ChangeType.UPSERT_JSON, {"foo": "bar"})
        ret = dogma.push(project_name, repo_name, commit, [upsert_json])

        start = datetime.now()
        entry: Optional[Entry[Any]] = dogma.watch_file(
            project_name,
            repo_name,
            Revision(ret.revision),
            Query.json("/test.json"),
            2000,
        )
        end = datetime.now()
        assert not entry  # Not modified
        assert (end - start).seconds >= 1

        with ThreadPoolExecutor(max_workers=1) as e:
            e.submit(self.push_later)
        start = datetime.now()
        entry = dogma.watch_file(
            project_name,
            repo_name,
            Revision(ret.revision),
            Query.json("/test.json"),
            4000,
        )
        end = datetime.now()
        assert entry.revision.major == ret.revision + 1
        assert entry.content == {"foo": "qux"}
        assert (end - start).seconds < 3

    def test_invalid_entry_type(self, run_around_test):
        commit = Commit("Upsert test.txt")
        upsert_text = Change("/test.txt", ChangeType.UPSERT_TEXT, "foo")
        ret = dogma.push(project_name, repo_name, commit, [upsert_text])

        upsert_text = Change("/test.txt", ChangeType.UPSERT_TEXT, "bar")
        dogma.push(project_name, repo_name, commit, [upsert_text])

        with pytest.raises(CentralDogmaException) as ex:
            dogma.watch_file(
                project_name,
                repo_name,
                Revision(ret.revision),
                Query.json("/test.txt"),  # A wrong JSON query for a text
                2000,
            )
        assert (
            "invalid entry type. entry type: EntryType.TEXT (expected: QueryType.IDENTITY_JSON)"
            in str(ex.value)
        )

    def test_merge_files(self, run_around_test):
        commit = Commit("Upsert test.json")
        upsert_json = Change("/test.json", ChangeType.UPSERT_JSON, {"foo": "bar"})
        dogma.push(project_name, repo_name, commit, [upsert_json])
        upsert_json = Change("/test2.json", ChangeType.UPSERT_JSON, {"foo2": "bar2"})
        dogma.push(project_name, repo_name, commit, [upsert_json])
        upsert_json = Change(
            "/test3.json",
            ChangeType.UPSERT_JSON,
            {"inner": {"inner2": {"foo3": "bar3"}}},
        )
        dogma.push(project_name, repo_name, commit, [upsert_json])

        merge_sources = [
            MergeSource("/nonexisting.json", False),
        ]
        with pytest.raises(EntryNotFoundException):
            dogma.merge_files(project_name, repo_name, merge_sources)

        merge_sources = [
            MergeSource("/test.json", True),
            MergeSource("/test2.json", True),
            MergeSource("/test3.json", True),
        ]
        ret = dogma.merge_files(project_name, repo_name, merge_sources)
        assert ret.entry_type == EntryType.JSON
        assert ret.content == {
            "foo": "bar",
            "foo2": "bar2",
            "inner": {"inner2": {"foo3": "bar3"}},
        }

        with pytest.raises(QueryExecutionException):
            dogma.merge_files(project_name, repo_name, merge_sources, ["$.inner2"])

        ret = dogma.merge_files(project_name, repo_name, merge_sources, ["$.inner"])
        assert ret.entry_type == EntryType.JSON
        assert ret.content == {"inner2": {"foo3": "bar3"}}

        ret = dogma.merge_files(
            project_name, repo_name, merge_sources, ["$.inner", "$.inner2"]
        )
        assert ret.entry_type == EntryType.JSON
        assert ret.content == {"foo3": "bar3"}

    @staticmethod
    def push_later():
        time.sleep(1)
        commit = Commit("Upsert test.json")
        upsert_json = Change("/test.json", ChangeType.UPSERT_JSON, {"foo": "qux"})
        dogma.push(project_name, repo_name, commit, [upsert_json])
