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
        function=lambda x: x
    )
