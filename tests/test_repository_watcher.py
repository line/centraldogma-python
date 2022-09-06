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

from centraldogma.data.revision import Revision
from centraldogma.query import Query
from centraldogma.repository_watcher import RepositoryWatcher, FileWatcher
from centraldogma.watcher import Latest

import pytest


@pytest.fixture()
def repo_watcher(mocker):
    return RepositoryWatcher(
        content_service=mocker.MagicMock(),
        project_name="project",
        repo_name="repo",
        path_pattern="/test",
        timeout_millis=1 * 60 * 1000,
        function=lambda x: x,
    )


@pytest.fixture()
def file_watcher(mocker):
    return FileWatcher(
        content_service=mocker.MagicMock(),
        project_name="project",
        repo_name="repo",
        query=Query.text("test.txt"),
        timeout_millis=5000,
        function=lambda x: x,
    )


def test_repository_watch(repo_watcher, mocker):
    revision = Revision.init()
    latest = Latest(revision, repo_watcher.function(revision))
    mocker.patch.object(repo_watcher, "_do_watch", return_value=latest)

    response = repo_watcher._watch(0)
    assert response == 0
    assert repo_watcher.latest() is latest


def test_repository_watch_with_none_revision(repo_watcher, mocker):
    mocker.patch.object(repo_watcher, "_do_watch", return_value=None)

    response = repo_watcher._watch(0)
    assert response == 0
    assert repo_watcher.latest() is None


def test_repository_watch_with_exception(repo_watcher, mocker):
    mocker.patch.object(
        repo_watcher, "_do_watch", side_effect=Exception("test exception")
    )

    response = repo_watcher._watch(0)
    assert response == 1
    assert repo_watcher.latest() is None


def test_file_watch(file_watcher, mocker):
    revision = Revision.init()
    latest = Latest(revision, file_watcher.function(revision))
    mocker.patch.object(file_watcher, "_do_watch", return_value=latest)

    response = file_watcher._watch(0)
    assert response == 0
    assert file_watcher.latest() is latest


def test_file_watch_with_none_revision(file_watcher, mocker):
    mocker.patch.object(file_watcher, "_do_watch", return_value=None)

    response = file_watcher._watch(0)
    assert response == 0
    assert file_watcher.latest() is None


def test_file_watch_with_exception(file_watcher, mocker):
    mocker.patch.object(
        file_watcher, "_do_watch", side_effect=Exception("test exception")
    )

    response = file_watcher._watch(0)
    assert response == 1
    assert file_watcher.latest() is None
