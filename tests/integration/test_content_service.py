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
from centraldogma.dogma import Change, ChangeType, Commit, Dogma
from centraldogma.exceptions import ConflictException
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
    commit = Commit("Upsert test.json")
    jsonChange = Change("/test.json", ChangeType.UPSERT_JSON, {"foo": "bar"})
    dogma.push_changes(project_name, repo_name, commit, [jsonChange])

    with pytest.raises(ConflictException):
        dogma.push_changes(project_name, repo_name, commit, [jsonChange])

    commit = Commit("Upsert test.txt")
    textChange = Change("/path/test.txt", ChangeType.UPSERT_TEXT, "foo")
    dogma.push_changes(project_name, repo_name, commit, [textChange])

    commit = Commit("Upsert both json and txt")
    jsonChange = Change("/test.json", ChangeType.UPSERT_JSON, {"foo": "bar2"})
    textChange = Change("/path/test.txt", ChangeType.UPSERT_TEXT, "foo2")
    dogma.push_changes(project_name, repo_name, commit, [jsonChange, textChange])
