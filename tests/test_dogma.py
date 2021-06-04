from centraldogma.data import DATE_FORMAT_ISO8601, Content, Creator, Project, Repository
from centraldogma.dogma import Dogma
from datetime import datetime
from http import HTTPStatus
import json
import requests_mock


client = Dogma("http://baseurl", "token")

mock_project = {
    "name": "project1",
    "creator": {"name": "admin", "email": "admin@centraldogma.com"},
    "url": "/api/v1/projects/myproject",
    "createdAt": "2017-09-28T15:33:35Z",
}
mock_repository = {
    "name": "repository1",
    "creator": {"name": "admin", "email": "admin@centraldogma.com"},
    "headRevision": 3,
    "url": "/api/v1/projects/myproject/repos/myrepo",
    "createdAt": "2017-09-28T15:33:35Z",
}
mock_content_text = {
    "path": "/fooDir/foo.txt",
    "type": "TEXT",
    "content": "foofoofoofoobarbar",
    "revision": 3,
    "url": "/projects/myPro/repos/myRepo/contents/fooDir/foo.txt",
}
mock_content_json = {
    "path": "/fooDir/foo.txt",
    "type": "JSON",
    "content": {"foo": "bar", "bar": ["foo", "foo"]},
    "revision": 3,
    "url": "/projects/myPro/repos/myRepo/contents/fooDir/foo.txt",
}


def test_list_projects():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects"
        matcher = m.get(url, json=[mock_project, mock_project])
        projects = client.list_projects()

        assert matcher.last_request.url == url
        assert len(projects) == 2
        for project in projects:
            assert project.name == mock_project["name"]
            assert project.creator == Creator.from_json(
                json.dumps(mock_project["creator"])
            )
            assert project.url == mock_project["url"]
            assert project.created_at == datetime.strptime(
                mock_project["createdAt"], DATE_FORMAT_ISO8601
            )


def test_list_projects_removed():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects"
        matcher = m.get(url, status_code=HTTPStatus.NO_CONTENT)
        projects = client.list_projects(removed=True)

        assert matcher.last_request.url == (url + "?status=removed")
        assert projects == []


def test_create_project():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects"
        matcher = m.post(url, json=mock_project, status_code=HTTPStatus.CREATED)
        project = client.create_project("newProject")

        assert matcher.last_request.url == url
        assert matcher.last_request.body == b'{"name": "newProject"}'
        assert project == Project.from_json(json.dumps(mock_project))


def test_create_project_failed():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects"
        matcher = m.post(url, status_code=HTTPStatus.BAD_REQUEST)
        project = client.create_project("newProject")

        assert matcher.last_request.url == url
        assert matcher.last_request.body == b'{"name": "newProject"}'
        assert project == None


def test_remove_project():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/project1"
        matcher = m.delete(url, status_code=HTTPStatus.NO_CONTENT)
        removed = client.remove_project("project1")

        assert matcher.last_request.url == url
        assert removed == True


def test_remove_project_failed():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/project1"
        matcher = m.delete(url, status_code=HTTPStatus.BAD_REQUEST)
        removed = client.remove_project("project1")

        assert matcher.last_request.url == url
        assert removed == False


def test_unremove_project():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/project1"
        matcher = m.patch(url, json=mock_project, status_code=HTTPStatus.OK)
        project = client.unremove_project("project1")

        request = matcher.last_request
        assert request.url == url
        assert (
            request.body == b'[{"op": "replace", "path": "/status", "value": "active"}]'
        )
        assert project == Project.from_json(json.dumps(mock_project))


def test_unremove_project_failed():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/project1"
        matcher = m.patch(url, status_code=HTTPStatus.SERVICE_UNAVAILABLE)
        project = client.unremove_project("project1")

        request = matcher.last_request
        assert request.url == url
        assert (
            request.body == b'[{"op": "replace", "path": "/status", "value": "active"}]'
        )
        assert project == None


def test_purge_project():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/project1/removed"
        matcher = m.delete(url, status_code=HTTPStatus.NO_CONTENT)
        purged = client.purge_project("project1")

        assert matcher.last_request.url == url
        assert purged == True


def test_purge_project_failed():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/project1/removed"
        matcher = m.delete(url, status_code=HTTPStatus.FORBIDDEN)
        purged = client.purge_project("project1")

        assert matcher.last_request.url == url
        assert purged == False


def test_list_repositories():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos"
        matcher = m.get(url, json=[mock_repository, mock_repository])
        repos = client.list_repositories("myproject")

        assert matcher.last_request.url == url
        assert len(repos) == 2
        for repo in repos:
            assert repo.name == mock_repository["name"]
            assert repo.creator == Creator.from_json(
                json.dumps(mock_repository["creator"])
            )
            assert repo.head_revision == mock_repository["headRevision"]
            assert repo.url == mock_repository["url"]
            assert repo.created_at == datetime.strptime(
                mock_repository["createdAt"], DATE_FORMAT_ISO8601
            )


def test_list_repositories_removed():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos"
        matcher = m.get(url, status_code=HTTPStatus.NO_CONTENT)
        repos = client.list_repositories("myproject", removed=True)

        assert matcher.last_request.url == (url + "?status=removed")
        assert repos == []


def test_create_repository():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos"
        matcher = m.post(url, json=mock_repository, status_code=HTTPStatus.CREATED)
        repo = client.create_repository("myproject", "newRepo")

        assert matcher.last_request.url == url
        assert matcher.last_request.body == b'{"name": "newRepo"}'
        assert repo == Repository.from_json(json.dumps(mock_repository))


def test_create_repository_failed():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos"
        matcher = m.post(url, status_code=HTTPStatus.BAD_REQUEST)
        repo = client.create_repository("myproject", "newRepo")

        assert matcher.last_request.url == url
        assert matcher.last_request.body == b'{"name": "newRepo"}'
        assert repo == None


def test_remove_repository():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo"
        matcher = m.delete(url, status_code=HTTPStatus.NO_CONTENT)
        removed = client.remove_repository("myproject", "myrepo")

        assert matcher.last_request.url == url
        assert removed == True


def test_remove_repository_failed():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo"
        matcher = m.delete(url, status_code=HTTPStatus.FORBIDDEN)
        removed = client.remove_repository("myproject", "myrepo")

        assert matcher.last_request.url == url
        assert removed == False


def test_unremove_repository():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo"
        matcher = m.patch(url, json=mock_repository)
        repo = client.unremove_repository("myproject", "myrepo")

        request = matcher.last_request
        assert request.url == url
        assert (
            request.body == b'[{"op": "replace", "path": "/status", "value": "active"}]'
        )
        assert repo == Repository.from_json(json.dumps(mock_repository))


def test_unremove_repository_failed():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo"
        matcher = m.patch(url, status_code=HTTPStatus.BAD_REQUEST)
        repo = client.unremove_repository("myproject", "myrepo")

        request = matcher.last_request
        assert request.url == url
        assert (
            request.body == b'[{"op": "replace", "path": "/status", "value": "active"}]'
        )
        assert repo == None


def test_purge_repository():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/removed"
        matcher = m.delete(url, status_code=HTTPStatus.NO_CONTENT)
        perged = client.purge_repository("myproject", "myrepo")

        assert matcher.last_request.url == url
        assert perged == True


def test_purge_repository_failed():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/removed"
        matcher = m.delete(url, status_code=HTTPStatus.FORBIDDEN)
        perged = client.purge_repository("myproject", "myrepo")

        assert matcher.last_request.url == url
        assert perged == False


def test_normalize_repository_revision():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/revision/3"
        matcher = m.get(url, json={"revision": 3})
        revision = client.normalize_repository_revision("myproject", "myrepo", 3)

        assert matcher.last_request.url == url
        assert revision == 3


def test_normalize_repository_revision_failed():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/revision/3"
        matcher = m.get(url, status_code=HTTPStatus.BAD_REQUEST)
        revision = client.normalize_repository_revision("myproject", "myrepo", 3)

        assert matcher.last_request.url == url
        assert revision == None


def test_list_files():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/list"
        matcher = m.get(url, json=[mock_content_text, mock_content_text])
        files = client.list_files("myproject", "myrepo")

        assert matcher.last_request.url == url
        assert len(files) == 2
        for file in files:
            assert file.path == mock_content_text["path"]
            assert file.type == mock_content_text["type"]
            assert file.url == mock_content_text["url"]


def test_list_files_pattern():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/list/foo/*.json"
        matcher = m.get(url, status_code=HTTPStatus.NO_CONTENT)
        files = client.list_files("myproject", "myrepo", "/foo/*.json")

        assert matcher.last_request.url == url
        assert files == []


def test_list_files_revision():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/list/*.json"
        matcher = m.get(url, status_code=HTTPStatus.NO_CONTENT)
        files = client.list_files("myproject", "myrepo", "*.json", 3)

        assert matcher.last_request.url == (url + "?revision=3")
        assert files == []


def test_get_files():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents"
        matcher = m.get(url, json=[mock_content_text, mock_content_text])
        files = client.get_files("myproject", "myrepo")

        assert matcher.last_request.url == url
        assert len(files) == 2
        for file in files:
            assert file == Content.from_json(json.dumps(mock_content_text))


def test_get_files_pattern():
    with requests_mock.mock() as m:
        url = (
            "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents/foo/*.json"
        )
        matcher = m.get(url, status_code=HTTPStatus.NO_CONTENT)
        files = client.get_files("myproject", "myrepo", "/foo/*.json")

        assert matcher.last_request.url == url
        assert files == []


def test_get_files_revision():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents/*.json"
        matcher = m.get(url, status_code=HTTPStatus.NO_CONTENT)
        files = client.get_files("myproject", "myrepo", "*.json", 3)

        assert matcher.last_request.url == (url + "?revision=3")
        assert files == []


def test_get_file_text():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents/foo.text"
        matcher = m.get(url, json=mock_content_text)
        file = client.get_file("myproject", "myrepo", "foo.text")

        assert matcher.last_request.url == url
        assert file.path == mock_content_text["path"]
        assert file.type == mock_content_text["type"]
        assert isinstance(file.content, str)
        assert file.content == mock_content_text["content"]
        assert file.revision == mock_content_text["revision"]
        assert file.url == mock_content_text["url"]


def test_get_file_json():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents/foo.json"
        matcher = m.get(url, json=mock_content_json)
        file = client.get_file("myproject", "myrepo", "foo.json", 3)

        assert matcher.last_request.url == (url + "?revision=3")
        assert file.path == mock_content_json["path"]
        assert file.type == mock_content_json["type"]
        assert isinstance(file.content, dict) or isinstance(file.content, list)
        assert file.content == mock_content_json["content"]
        assert file.revision == mock_content_json["revision"]
        assert file.url == mock_content_json["url"]


def test_get_file_json_path():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents/foo.json"
        matcher = m.get(url, json=mock_content_json)
        file = client.get_file("myproject", "myrepo", "foo.json", 3, "$.a")

        assert matcher.last_request.url == (url + "?revision=3&jsonpath=%24.a")
        assert file.path == mock_content_json["path"]
        assert file.type == mock_content_json["type"]
        assert isinstance(file.content, dict) or isinstance(file.content, list)
        assert file.content == mock_content_json["content"]
        assert file.revision == mock_content_json["revision"]
        assert file.url == mock_content_json["url"]
