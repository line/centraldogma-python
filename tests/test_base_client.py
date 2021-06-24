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
from centraldogma.exceptions import AuthorizationException, NotFoundException
from centraldogma.base_client import BaseClient
import pytest
import requests_mock


client = BaseClient("http://baseurl", "token")

configs = {
    "timeout": 5,
    "cookies": None,
    "auth": None,
    "allow_redirects": False,
    "proxies": None,
    "hooks": None,
    "stream": None,
    "cert": None,
}
client_with_configs = BaseClient("http://baseurl", "token", **configs)


def test_get_kwargs():
    for method in ["get", "post", "delete", "patch"]:
        kwargs = client_with_configs._get_kwargs(method, a="b")
        content_type = (
            "application/json-patch+json" if method == "patch" else "application/json"
        )
        assert kwargs["headers"] == {
            "Authorization": "bearer token",
            "Content-Type": content_type,
        }
        assert kwargs["timeout"] == 5
        assert kwargs["cookies"] == None
        assert kwargs["auth"] == None
        assert kwargs["allow_redirects"] == False
        assert kwargs["proxies"] == None
        assert kwargs["hooks"] == None
        assert kwargs["stream"] == None
        assert kwargs["cert"] == None


def test_request_with_configs():
    with requests_mock.mock() as m:
        m.get("http://baseurl/api/v1/path", text="success")
        for method in ["get", "post", "delete", "patch"]:
            getattr(m, method)("http://baseurl/api/v1/path", text="success")
            client.request(
                method,
                "/path",
                timeout=5,
                cookies=None,
                auth=None,
                allow_redirects=False,
                proxies=None,
                hooks=None,
                stream=None,
                cert=None,
            )
            client.request(method, "/path", timeout=(3.05, 27))
            client_with_configs.request(method, "/path")


def test_delete():
    with requests_mock.mock() as m:
        matcher = m.delete("http://baseurl/api/v1/path", text="success")
        client.request("delete", "/path", params={"a": "b"})

        request = matcher.last_request
        assert request.headers["Authorization"] == "bearer token"
        assert request.headers["Content-Type"] == "application/json"
        assert request.url.endswith("?a=b")


def test_delete_exception_authorization():
    with pytest.raises(AuthorizationException):
        with requests_mock.mock() as m:
            m.delete("http://baseurl/api/v1/path", status_code=401)
            client.request("delete", "/path")


def test_get():
    with requests_mock.mock() as m:
        matcher = m.get("http://baseurl/api/v1/path", text="success")
        client.request("get", "/path", params={"a": "b"})

        request = matcher.last_request
        assert request.headers["Authorization"] == "bearer token"
        assert request.headers["Content-Type"] == "application/json"
        assert request.url.endswith("?a=b")


def test_get_exception_authorization():
    with pytest.raises(AuthorizationException):
        with requests_mock.mock() as m:
            m.get("http://baseurl/api/v1/path", status_code=401, json={"message": ""})
            client.request("get", "/path")


def test_get_exception_not_found():
    with pytest.raises(NotFoundException):
        with requests_mock.mock() as m:
            m.get("http://baseurl/api/v1/path", status_code=404, json={"message": ""})
            client.request("get", "/path")


def test_patch():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/path"
        matcher = m.patch(url, text="success")
        client.request("patch", "/path", json={"a": "b"})

        request = matcher.last_request
        assert request.headers["Authorization"] == "bearer token"
        assert request.headers["Content-Type"] == "application/json-patch+json"
        assert request.url == url
        assert request.body == b'{"a": "b"}'


def test_patch_exception_authorization():
    with pytest.raises(AuthorizationException):
        with requests_mock.mock() as m:
            m.patch("http://baseurl/api/v1/path", status_code=401)
            client.request("patch", "/path", json={"a": "b"})


def test_post():
    with requests_mock.mock() as m:
        url = "http://baseurl/api/v1/path"
        matcher = m.post(url, text="success")
        client.request("post", "/path", json={"a": "b"})

        request = matcher.last_request
        assert request.headers["Authorization"] == "bearer token"
        assert request.headers["Content-Type"] == "application/json"
        assert request.url == url
        assert request.body == b'{"a": "b"}'


def test_post_exception_authorization():
    with pytest.raises(AuthorizationException):
        with requests_mock.mock() as m:
            m.post("http://baseurl/api/v1/path", status_code=401)
            client.request("post", "/path")
