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
from centraldogma.dogma import Change, ChangeType, Commit, Dogma, PushResult
from centraldogma.exceptions import BadRequestException, ConflictException
import pytest
import os

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
def test_content(run_around_test):
    files = dogma.list_files(project_name, repo_name)
    assert len(files) == 0

    commit = Commit("Upsert test.json")
    upsertJson = Change("/test.json", ChangeType.UPSERT_JSON, {"foo": "bar"})
    ret = dogma.push_changes(project_name, repo_name, commit, [upsertJson])
    assert ret.revision == 2

    with pytest.raises(ConflictException):
        dogma.push_changes(project_name, repo_name, commit, [upsertJson])

    commit = Commit("Upsert test.txt")
    upsertText = Change("/path/test.txt", ChangeType.UPSERT_TEXT, "foo")
    ret = dogma.push_changes(project_name, repo_name, commit, [upsertText])
    assert ret.revision == 3

    commit = Commit("Upsert both json and txt")
    upsertJson = Change("/test.json", ChangeType.UPSERT_JSON, {"foo": "bar2"})
    upsertText = Change("/path/test.txt", ChangeType.UPSERT_TEXT, "foo2")
    ret = dogma.push_changes(project_name, repo_name, commit, [upsertJson, upsertText])
    assert ret.revision == 4

    commit = Commit("Rename the json")
    renameJson = Change("/test2.json", ChangeType.RENAME, "/test3.json")
    with pytest.raises(ConflictException):
        dogma.push_changes(project_name, repo_name, commit, [renameJson])
    renameJson = Change("/test.json", ChangeType.RENAME, "")
    with pytest.raises(BadRequestException):
        dogma.push_changes(project_name, repo_name, commit, [renameJson])
    renameJson = Change("/test.json", ChangeType.RENAME, "/test2.json")
    ret = dogma.push_changes(project_name, repo_name, commit, [renameJson])
    assert ret.revision == 5

    files = dogma.list_files(project_name, repo_name)
    assert len(files) == 2
    assert set(map(lambda x: x.path, files)) == {"/path", "/test2.json"}
    assert set(map(lambda x: x.type, files)) == {"DIRECTORY", "JSON"}

    commit = Commit("Remove the json")
    removeJson = Change("/test.json", ChangeType.REMOVE)
    with pytest.raises(ConflictException):
        dogma.push_changes(project_name, repo_name, commit, [removeJson])
    removeJson = Change("/test2.json", ChangeType.REMOVE)
    ret = dogma.push_changes(project_name, repo_name, commit, [removeJson])
    assert ret.revision == 6

    with pytest.raises(ConflictException):
        dogma.push_changes(project_name, repo_name, commit, [removeJson])

    files = dogma.list_files(project_name, repo_name)
    assert len(files) == 1

    commit = Commit("Remove the folder")
    removeFolder = Change("/path", ChangeType.REMOVE)
    ret = dogma.push_changes(project_name, repo_name, commit, [removeFolder])
    assert ret.revision == 7

    files = dogma.list_files(project_name, repo_name)
    assert len(files) == 0
