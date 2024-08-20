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
from http import HTTPStatus

from centraldogma.exceptions import UnauthorizedException, NotFoundException
from centraldogma.base_client import BaseClient
from httpx import Response
import pytest

client = BaseClient("http://baseurl", "token")

configs = {
    "auth": None,
    "cookies": None,
    "verify": None,
    "cert": None,
    "proxies": None,
    "mounts": None,
    "timeout": 5,
    "retries": 10,
    "max_connections": 50,
    "max_keepalive_connections": 10,
    "max_redirects": 1,
    "event_hooks": None,
    "transport": None,
    "app": None,
    "trust_env": True,
}
client_with_configs = BaseClient("http://baseurl", "token", **configs)

ok_handler = {HTTPStatus.OK: lambda resp: resp}


def test_set_request_headers():
    for method in ["get", "post", "delete", "patch"]:
        kwargs = client_with_configs._set_request_headers(
            method, params={"a": "b"}, follow_redirects=True
        )
        content_type = (
            "application/json-patch+json" if method == "patch" else "application/json"
        )
        assert kwargs["headers"] == {
            "Authorization": "bearer token",
            "Content-Type": content_type,
        }
        assert kwargs["params"] == {"a": "b"}
        assert kwargs["follow_redirects"]
        assert "limits" not in kwargs
        assert "event_hooks" not in kwargs
        assert "transport" not in kwargs
        assert "app" not in kwargs
        assert "trust_env" not in kwargs


def test_request_with_configs(respx_mock):
    methods = ["get", "post", "put", "delete", "patch", "options"]
    for method in methods:
        getattr(respx_mock, method)("http://baseurl/api/v1/path").mock(
            return_value=Response(200, text="success")
        )
        client.request(
            method,
            "/path",
            timeout=5,
            cookies=None,
            auth=None,
        )
        client.request(method, "/path", timeout=(3.05, 27))
        client_with_configs.request(method, "/path")
    assert respx_mock.calls.call_count == len(methods) * 3


def test_delete(respx_mock):
    route = respx_mock.delete("http://baseurl/api/v1/path").mock(
        return_value=Response(200, text="success")
    )
    resp = client.request("delete", "/path", params={"a": "b"})

    assert route.called
    assert resp.request.headers["Authorization"] == "bearer token"
    assert resp.request.headers["Content-Type"] == "application/json"
    assert resp.request.url.params.multi_items() == [("a", "b")]


def test_delete_exception_authorization(respx_mock):
    with pytest.raises(UnauthorizedException):
        respx_mock.delete("http://baseurl/api/v1/path").mock(return_value=Response(401))
        client.request("delete", "/path", handler=ok_handler)


def test_get(respx_mock):
    route = respx_mock.get("http://baseurl/api/v1/path").mock(
        return_value=Response(200, text="success")
    )
    resp = client.request("get", "/path", params={"a": "b"}, handler=ok_handler)

    assert route.called
    assert resp.request.headers["Authorization"] == "bearer token"
    assert resp.request.headers["Content-Type"] == "application/json"
    assert resp.request.url.params.multi_items() == [("a", "b")]


def test_get_exception_authorization(respx_mock):
    with pytest.raises(UnauthorizedException):
        respx_mock.get("http://baseurl/api/v1/path").mock(return_value=Response(401))
        client.request("get", "/path", handler=ok_handler)


def test_get_exception_not_found(respx_mock):
    with pytest.raises(NotFoundException):
        respx_mock.get("http://baseurl/api/v1/path").mock(return_value=Response(404))
        client.request("get", "/path", handler=ok_handler)


def test_patch(respx_mock):
    route = respx_mock.patch("http://baseurl/api/v1/path").mock(
        return_value=Response(200, text="success")
    )
    resp = client.request("patch", "/path", json={"a": "b"}, handler=ok_handler)

    assert route.called
    assert resp.request.headers["Authorization"] == "bearer token"
    assert resp.request.headers["Content-Type"] == "application/json-patch+json"
    assert resp.request._content == b'{"a": "b"}'


def test_patch_exception_authorization(respx_mock):
    with pytest.raises(UnauthorizedException):
        respx_mock.patch("http://baseurl/api/v1/path").mock(return_value=Response(401))
        client.request("patch", "/path", json={"a": "b"}, handler=ok_handler)


def test_post(respx_mock):
    route = respx_mock.post("http://baseurl/api/v1/path").mock(
        return_value=Response(200, text="success")
    )
    resp = client.request("post", "/path", json={"a": "b"}, handler=ok_handler)

    assert route.called
    assert resp.request.headers["Authorization"] == "bearer token"
    assert resp.request.headers["Content-Type"] == "application/json"
    assert resp.request._content == b'{"a": "b"}'


def test_post_exception_authorization(respx_mock):
    with pytest.raises(UnauthorizedException):
        respx_mock.post("http://baseurl/api/v1/path").mock(return_value=Response(401))
        client.request("post", "/path", handler=ok_handler)
