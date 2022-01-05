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
from centraldogma.data import (
    DATE_FORMAT_ISO8601,
    DATE_FORMAT_ISO8601_MS,
    Change,
    ChangeType,
    Commit,
    Content,
    Creator,
    Project,
    Repository,
)
from centraldogma.dogma import Dogma
from centraldogma.exceptions import (
    BadRequestException,
    UnknownException,
    ProjectExistsException,
    RepositoryExistsException,
)
from datetime import datetime
from http import HTTPStatus
from httpx import Response
import pytest

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
mock_push_result = {
    "revision": 2,
    "pushedAt": "2021-10-28T15:33:35.123Z",
}


def test_list_projects(respx_mock):
    url = "http://baseurl/api/v1/projects"
    route = respx_mock.get(url).mock(
        return_value=Response(200, json=[mock_project, mock_project])
    )
    projects = client.list_projects()

    assert route.called
    assert len(projects) == 2
    for project in projects:
        assert project.name == mock_project["name"]
        assert project.creator == Creator.from_dict(mock_project["creator"])
        assert project.url == mock_project["url"]
        assert project.created_at == datetime.strptime(
            mock_project["createdAt"], DATE_FORMAT_ISO8601
        )


def test_list_projects_removed(respx_mock):
    url = "http://baseurl/api/v1/projects"
    route = respx_mock.get(url).mock(return_value=Response(HTTPStatus.NO_CONTENT))
    projects = client.list_projects(removed=True)

    assert route.called
    assert respx_mock.calls.last.request.url == (url + "?status=removed")
    assert projects == []


def test_create_project(respx_mock):
    url = "http://baseurl/api/v1/projects"
    route = respx_mock.post(url).mock(
        return_value=Response(HTTPStatus.CREATED, json=mock_project)
    )
    project = client.create_project("newProject")

    assert route.called
    request = respx_mock.calls.last.request
    assert request.url == url
    assert request._content == b'{"name": "newProject"}'
    assert project == Project.from_dict(mock_project)


def test_create_project_failed(respx_mock):
    url = "http://baseurl/api/v1/projects"
    response_body = {
        "exception": "com.linecorp.centraldogma.common.ProjectExistsException",
        "message": "Project 'newProject' exists already.",
    }
    route = respx_mock.post(url).mock(
        return_value=Response(HTTPStatus.CONFLICT, json=response_body)
    )
    with pytest.raises(ProjectExistsException) as cause:
        client.create_project("newProject")
    assert response_body["message"] == str(cause.value)

    assert route.called
    request = respx_mock.calls.last.request
    assert request.url == url
    assert request._content == b'{"name": "newProject"}'


def test_remove_project(respx_mock):
    url = "http://baseurl/api/v1/projects/project1"
    route = respx_mock.delete(url).mock(return_value=Response(HTTPStatus.NO_CONTENT))
    client.remove_project("project1")

    assert route.called
    assert respx_mock.calls.last.request.url == url


def test_remove_project_failed(respx_mock):
    url = "http://baseurl/api/v1/projects/project1"
    route = respx_mock.delete(url).mock(return_value=Response(HTTPStatus.BAD_REQUEST))
    with pytest.raises(BadRequestException):
        client.remove_project("project1")

    assert route.called
    assert respx_mock.calls.last.request.url == url


def test_unremove_project(respx_mock):
    url = "http://baseurl/api/v1/projects/project1"
    route = respx_mock.patch(url).mock(
        return_value=Response(HTTPStatus.OK, json=mock_project)
    )
    project = client.unremove_project("project1")

    assert route.called
    request = respx_mock.calls.last.request
    assert request.url == url
    assert (
        request._content == b'[{"op": "replace", "path": "/status", "value": "active"}]'
    )
    assert project == Project.from_dict(mock_project)


def test_unremove_project_failed(respx_mock):
    url = "http://baseurl/api/v1/projects/project1"
    route = respx_mock.patch(url).mock(
        return_value=Response(HTTPStatus.SERVICE_UNAVAILABLE)
    )
    with pytest.raises(UnknownException):
        client.unremove_project("project1")

    assert route.called
    request = respx_mock.calls.last.request
    assert request.url == url
    assert (
        request._content == b'[{"op": "replace", "path": "/status", "value": "active"}]'
    )


def test_purge_project(respx_mock):
    url = "http://baseurl/api/v1/projects/project1/removed"
    route = respx_mock.delete(url).mock(return_value=Response(HTTPStatus.NO_CONTENT))
    client.purge_project("project1")

    assert route.called
    assert respx_mock.calls.last.request.url == url


def test_purge_project_failed(respx_mock):
    url = "http://baseurl/api/v1/projects/project1/removed"
    route = respx_mock.delete(url).mock(return_value=Response(HTTPStatus.FORBIDDEN))
    with pytest.raises(UnknownException):
        client.purge_project("project1")

    assert route.called
    assert respx_mock.calls.last.request.url == url


def test_list_repositories(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos"
    route = respx_mock.get(url).mock(
        return_value=Response(HTTPStatus.OK, json=[mock_repository, mock_repository])
    )
    repos = client.list_repositories("myproject")

    assert route.called
    assert respx_mock.calls.last.request.url == url
    assert len(repos) == 2
    for repo in repos:
        assert repo.name == mock_repository["name"]
        assert repo.creator == Creator.from_dict(mock_repository["creator"])
        assert repo.head_revision == mock_repository["headRevision"]
        assert repo.url == mock_repository["url"]
        assert repo.created_at == datetime.strptime(
            mock_repository["createdAt"], DATE_FORMAT_ISO8601
        )


def test_list_repositories_removed(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos"
    route = respx_mock.get(url).mock(return_value=Response(HTTPStatus.NO_CONTENT))
    repos = client.list_repositories("myproject", removed=True)

    assert route.called
    assert respx_mock.calls.last.request.url == (url + "?status=removed")
    assert repos == []


def test_create_repository(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos"
    route = respx_mock.post(url).mock(
        return_value=Response(HTTPStatus.CREATED, json=mock_repository)
    )
    repo = client.create_repository("myproject", "newRepo")

    assert route.called
    request = respx_mock.calls.last.request
    assert request.url == url
    assert request._content == b'{"name": "newRepo"}'
    assert repo == Repository.from_dict(mock_repository)


def test_create_repository_failed(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos"
    response_body = {
        "exception": "com.linecorp.centraldogma.common.RepositoryExistsException",
        "message": "Respository 'myproject/newRepo' exists already.",
    }
    route = respx_mock.post(url).mock(
        return_value=Response(HTTPStatus.CONFLICT, json=response_body)
    )
    with pytest.raises(RepositoryExistsException):
        client.create_repository("myproject", "newRepo")

    assert route.called
    request = respx_mock.calls.last.request
    assert request.url == url
    assert request._content == b'{"name": "newRepo"}'


def test_remove_repository(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo"
    route = respx_mock.delete(url).mock(return_value=Response(HTTPStatus.NO_CONTENT))
    client.remove_repository("myproject", "myrepo")

    assert route.called
    assert respx_mock.calls.last.request.url == url


def test_remove_repository_failed(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo"
    route = respx_mock.delete(url).mock(return_value=Response(HTTPStatus.FORBIDDEN))
    with pytest.raises(UnknownException):
        client.remove_repository("myproject", "myrepo")

    assert route.called
    assert respx_mock.calls.last.request.url == url


def test_unremove_repository(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo"
    route = respx_mock.patch(url).mock(
        return_value=Response(HTTPStatus.OK, json=mock_repository)
    )
    repo = client.unremove_repository("myproject", "myrepo")

    assert route.called
    request = respx_mock.calls.last.request
    assert request.url == url
    assert (
        request._content == b'[{"op": "replace", "path": "/status", "value": "active"}]'
    )
    assert repo == Repository.from_dict(mock_repository)


def test_unremove_repository_failed(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo"
    route = respx_mock.patch(url).mock(return_value=Response(HTTPStatus.BAD_REQUEST))
    with pytest.raises(BadRequestException):
        client.unremove_repository("myproject", "myrepo")

    assert route.called
    request = respx_mock.calls.last.request
    assert request.url == url
    assert (
        request._content == b'[{"op": "replace", "path": "/status", "value": "active"}]'
    )


def test_purge_repository(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/removed"
    route = respx_mock.delete(url).mock(return_value=Response(HTTPStatus.NO_CONTENT))
    client.purge_repository("myproject", "myrepo")

    assert route.called
    assert respx_mock.calls.last.request.url == url


def test_purge_repository_failed(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/removed"
    route = respx_mock.delete(url).mock(return_value=Response(HTTPStatus.FORBIDDEN))
    with pytest.raises(UnknownException):
        client.purge_repository("myproject", "myrepo")

    assert route.called
    assert respx_mock.calls.last.request.url == url


def test_normalize_repository_revision(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/revision/3"
    route = respx_mock.get(url).mock(
        return_value=Response(HTTPStatus.OK, json={"revision": 3})
    )
    revision = client.normalize_repository_revision("myproject", "myrepo", 3)

    assert route.called
    assert respx_mock.calls.last.request.url == url
    assert revision == 3


def test_normalize_repository_revision_failed(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/revision/3"
    route = respx_mock.get(url).mock(return_value=Response(HTTPStatus.BAD_REQUEST))
    with pytest.raises(BadRequestException):
        client.normalize_repository_revision("myproject", "myrepo", 3)

    assert route.called
    assert respx_mock.calls.last.request.url == url


def test_list_files(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/list"
    route = respx_mock.get(url).mock(
        return_value=Response(
            HTTPStatus.OK, json=[mock_content_text, mock_content_text]
        )
    )
    files = client.list_files("myproject", "myrepo")

    assert route.called
    assert respx_mock.calls.last.request.url == url
    assert len(files) == 2
    for file in files:
        assert file.path == mock_content_text["path"]
        assert file.type == mock_content_text["type"]
        assert file.url == mock_content_text["url"]


def test_list_files_pattern(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/list/foo/*.json"
    route = respx_mock.get(url).mock(return_value=Response(HTTPStatus.NO_CONTENT))
    files = client.list_files("myproject", "myrepo", "/foo/*.json")

    assert route.called
    assert respx_mock.calls.last.request.url == url
    assert files == []


def test_list_files_revision(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/list/*.json"
    route = respx_mock.get(url).mock(return_value=Response(HTTPStatus.NO_CONTENT))
    files = client.list_files("myproject", "myrepo", "*.json", 3)

    assert route.called
    assert respx_mock.calls.last.request.url == (url + "?revision=3")
    assert files == []


def test_get_files(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents"
    route = respx_mock.get(url).mock(
        return_value=Response(
            HTTPStatus.OK, json=[mock_content_text, mock_content_text]
        )
    )
    files = client.get_files("myproject", "myrepo")

    assert route.called
    assert respx_mock.calls.last.request.url == url
    assert len(files) == 2
    for file in files:
        assert file == Content.from_dict(mock_content_text)


def test_get_files_pattern(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents/foo/*.json"
    route = respx_mock.get(url).mock(return_value=Response(HTTPStatus.NO_CONTENT))
    files = client.get_files("myproject", "myrepo", "/foo/*.json")

    assert route.called
    assert respx_mock.calls.last.request.url == url
    assert files == []


def test_get_files_revision(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents/*.json"
    route = respx_mock.get(url).mock(return_value=Response(HTTPStatus.NO_CONTENT))
    files = client.get_files("myproject", "myrepo", "*.json", 3)

    assert route.called
    assert respx_mock.calls.last.request.url == (url + "?revision=3")
    assert files == []


def test_get_file_text(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents/foo.text"
    route = respx_mock.get(url).mock(
        return_value=Response(HTTPStatus.OK, json=mock_content_text)
    )
    file = client.get_file("myproject", "myrepo", "foo.text")

    assert route.called
    assert respx_mock.calls.last.request.url == url
    assert file.path == mock_content_text["path"]
    assert file.type == mock_content_text["type"]
    assert isinstance(file.content, str)
    assert file.content == mock_content_text["content"]
    assert file.revision == mock_content_text["revision"]
    assert file.url == mock_content_text["url"]


def test_get_file_json(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents/foo.json"
    route = respx_mock.get(url).mock(
        return_value=Response(HTTPStatus.OK, json=mock_content_json)
    )
    file = client.get_file("myproject", "myrepo", "foo.json", 3)

    assert route.called
    assert respx_mock.calls.last.request.url == (url + "?revision=3")
    assert file.path == mock_content_json["path"]
    assert file.type == mock_content_json["type"]
    assert isinstance(file.content, dict) or isinstance(file.content, list)
    assert file.content == mock_content_json["content"]
    assert file.revision == mock_content_json["revision"]
    assert file.url == mock_content_json["url"]


def test_get_file_json_path(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents/foo.json"
    route = respx_mock.get(url).mock(
        return_value=Response(HTTPStatus.OK, json=mock_content_json)
    )
    file = client.get_file("myproject", "myrepo", "foo.json", 3, "$.a")

    assert route.called
    assert respx_mock.calls.last.request.url == (url + "?revision=3&jsonpath=%24.a")
    assert file.path == mock_content_json["path"]
    assert file.type == mock_content_json["type"]
    assert isinstance(file.content, dict) or isinstance(file.content, list)
    assert file.content == mock_content_json["content"]
    assert file.revision == mock_content_json["revision"]
    assert file.url == mock_content_json["url"]


def test_push(respx_mock):
    url = "http://baseurl/api/v1/projects/myproject/repos/myrepo/contents"
    route = respx_mock.post(url).mock(
        return_value=Response(HTTPStatus.OK, json=mock_push_result)
    )
    commit = Commit("Upsert test.json")
    upsert_json = Change("/test.json", ChangeType.UPSERT_JSON, {"foo": "bar"})
    ret = client.push("myproject", "myrepo", commit, [upsert_json])

    assert route.called
    request = respx_mock.calls.last.request
    assert request.url == url
    payload = (
        '{"commitMessage": {"summary": "Upsert test.json", "detail": null, "markup": null}, '
        '"changes": [{"path": "/test.json", "type": "UPSERT_JSON", "content": {"foo": "bar"}}]}'
    )
    assert request._content == bytes(str(payload), "utf-8")
    assert ret.pushed_at == datetime.strptime(
        mock_push_result["pushedAt"], DATE_FORMAT_ISO8601_MS
    )


def test_push_format():
    mock_push_result = {
        "revision": 2,
        "pushedAt": "2021-10-28T15:33:35.123Z",
    }
