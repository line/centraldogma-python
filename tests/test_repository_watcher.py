#  Copyright 2022 LINE Corporation
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

from unittest.mock import Mock

from centraldogma.data.revision import Revision
from centraldogma.repository_watcher import RepositoryWatcher
from centraldogma.watcher import Latest


def test__watch():
    watcher = create_watcher()
    revision = Revision.init()
    latest = Latest(revision, watcher.function(revision))
    watcher._do_watch = Mock(return_value=latest)

    response = watcher._watch(0)
    assert response == 0
    assert watcher.latest() == latest


def test__watch_with_none_revision():
    watcher = create_watcher()
    watcher._do_watch = Mock(return_value=None)

    response = watcher._watch(0)
    assert response == 0
    assert watcher.latest() is None


def test__watch_with_exception():
    watcher = create_watcher()
    watcher._do_watch = Mock(side_effect=Exception("test exception"))
    response = watcher._watch(0)
    assert response == 1
    assert watcher.latest() is None


def create_watcher():
    return RepositoryWatcher(
        content_service=Mock(),
        project_name="project",
        repo_name="repo",
        path_pattern="/test",
        timeout_millis=1 * 60 * 1000,
        function=lambda x: x,
    )
