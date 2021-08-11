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
from centraldogma.exceptions import BadRequestException
import pytest
import os

dogma = Dogma()


@pytest.mark.skipif(
    os.getenv("INTEGRATION_TEST") is None, reason="Integration tests are optional"
)
@pytest.mark.integration
def test_project():
    projects = dogma.list_projects()
    assert len(projects) == 0

    with pytest.raises(BadRequestException):
        dogma.create_project("Test project")

    project_name = "TestProject"
    new_project = dogma.create_project(project_name)
    assert new_project.name == project_name

    projects = dogma.list_projects()
    assert len(projects) == 1

    removed = dogma.remove_project("TestProject")
    assert removed == True

    projects = dogma.list_projects(removed=True)
    assert len(projects) == 1

    projects = dogma.list_projects()
    assert len(projects) == 0
