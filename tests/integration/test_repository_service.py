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
from centraldogma.dogma import Dogma
from centraldogma.exceptions import BadRequestException, NotFoundException, RepositoryNotFoundException
import pytest
import os

dogma = Dogma()
project_name = "TestProject"
repo_name = "TestRepository"


@pytest.fixture(scope="module")
def run_around_test():
    dogma.create_project(project_name)
    yield
    dogma.remove_project(project_name)
    dogma.purge_project(project_name)


@pytest.mark.skipif(
    os.getenv("INTEGRATION_TEST", "false").lower() != "true",
    reason="Integration tests are disabled. Use `INTEGRATION_TEST=true pytest` to enable them.",
)
@pytest.mark.integration
def test_repository(run_around_test):
    with pytest.raises(BadRequestException):
        dogma.create_repository(project_name, "Test repo")

    len_repo = len(dogma.list_repositories(project_name))
    len_removed_repo = len(dogma.list_repositories(project_name, removed=True))

    try:
        repo = dogma.create_repository(project_name, repo_name)
        assert repo.name == repo_name
        validate_len(len_repo + 1, len_removed_repo)

        with pytest.raises(RepositoryNotFoundException):
            dogma.remove_repository(project_name, "Non-existent")

        dogma.remove_repository(project_name, repo_name)
        validate_len(len_repo, len_removed_repo + 1)

        with pytest.raises(RepositoryNotFoundException):
            dogma.unremove_repository(project_name, "Non-existent")

        unremoved = dogma.unremove_repository(project_name, repo_name)
        assert unremoved.name == repo_name
        validate_len(len_repo + 1, len_removed_repo)

    finally:
        dogma.remove_repository(project_name, repo_name)
        dogma.purge_repository(project_name, repo_name)
        validate_len(len_repo, len_removed_repo)


def validate_len(expected_len, expected_removed_len):
    repos = dogma.list_repositories(project_name)
    removed_repos = dogma.list_repositories(project_name, removed=True)
    assert len(repos) == expected_len
    assert len(removed_repos) == expected_removed_len
