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
from centraldogma.exceptions import BadRequestException, NotFoundException, ProjectNotFoundException
import pytest
import os

dogma = Dogma()
project_name = "TestProject"


@pytest.mark.skipif(
    os.getenv("INTEGRATION_TEST", "false").lower() != "true",
    reason="Integration tests are disabled. Use `INTEGRATION_TEST=true pytest` to enable them.",
)
@pytest.mark.integration
def test_project():
    with pytest.raises(BadRequestException):
        dogma.create_project("Test project")

    len_project = len(dogma.list_projects())
    len_removed_project = len(dogma.list_projects(removed=True))

    try:
        new_project = dogma.create_project(project_name)
        assert new_project.name == project_name
        validate_len(len_project + 1, len_removed_project)

        with pytest.raises(ProjectNotFoundException):
            dogma.remove_project("Non-existent")

        dogma.remove_project(project_name)
        validate_len(len_project, len_removed_project + 1)

        with pytest.raises(ProjectNotFoundException):
            dogma.unremove_project("Non-existent")

        unremoved = dogma.unremove_project(project_name)
        assert unremoved.name == project_name
        validate_len(len_project + 1, len_removed_project)

    finally:
        dogma.remove_project(project_name)
        dogma.purge_project(project_name)
        validate_len(len_project, len_removed_project)


def validate_len(expected_len, expected_removed_len):
    projects = dogma.list_projects()
    removed_projects = dogma.list_projects(removed=True)
    assert len(projects) == expected_len
    assert len(removed_projects) == expected_removed_len
