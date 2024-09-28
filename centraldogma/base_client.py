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
from typing import Dict, Union, Callable, TypeVar, Optional

from httpx import Client, HTTPTransport, Limits, Response
from tenacity import stop_after_attempt, Retrying

from centraldogma.exceptions import to_exception

T = TypeVar("T")


class BaseClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        http2: bool = True,
        retries: int = 1,
        max_connections: int = 10,
        max_keepalive_connections: int = 2,
        **configs,
    ):
        base_url = base_url[:-1] if base_url[-1] == "/" else base_url

        for key in ["transport", "limits"]:
            if key in configs:
                del configs[key]

        self.retries = retries
        self.client = Client(
            base_url=f"{base_url}/api/v1",
            http2=http2,
            transport=HTTPTransport(retries=retries),
            limits=Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
            ),
            **configs,
        )
        self.token = token
        self.headers = self._get_headers(token)
        self.patch_headers = self._get_patch_headers(token)

    def request(
        self,
        method: str,
        path: str,
        handler: Optional[Dict[int, Callable[[Response], T]]] = None,
        **kwargs,
    ) -> Union[Response, T]:
        kwargs = self._set_request_headers(method, **kwargs)
        retryer = Retrying(stop=stop_after_attempt(self.retries), reraise=True)
        return retryer(self._request, method, path, handler, **kwargs)

    def _set_request_headers(self, method: str, **kwargs) -> Dict:
        default_headers = self.patch_headers if method == "patch" else self.headers
        kwargs["headers"] = {**default_headers, **(kwargs.get("headers") or {})}
        return kwargs

    def _request(
        self,
        method: str,
        path: str,
        handler: Optional[Dict[int, Callable[[Response], T]]] = None,
        **kwargs,
    ):
        resp = self.client.request(method, path, **kwargs)
        if handler:
            converter = handler.get(resp.status_code)
            if converter:
                return converter(resp)
            else:  # Unexpected response status
                raise to_exception(resp)
        return resp

    @staticmethod
    def _get_headers(token: str) -> Dict:
        return {
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _get_patch_headers(token: str) -> Dict:
        return {
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json-patch+json",
        }
