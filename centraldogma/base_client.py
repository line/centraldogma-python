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
from centraldogma.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthorizedException,
    UnknownException,
)
from http import HTTPStatus
from httpx import Client, Response
from typing import Dict, Union


class BaseClient:
    PATH_PREFIX = "/api/v1"

    def __init__(self, base_url: str, token: str, http2: bool = True, **configs):
        base_url = base_url[:-1] if base_url[-1] == "/" else base_url
        self.client = Client(
            base_url=f"{base_url}{self.PATH_PREFIX}", http2=http2, **configs
        )
        self.token = token
        self.headers = self._get_headers(token)
        self.patch_headers = self._get_patch_headers(token)

    def request(self, method: str, path: str, **kwargs) -> Union[Response]:
        kwargs = self._set_request_headers(method, **kwargs)
        return self._httpx_request(method, path, **kwargs)

    def _set_request_headers(self, method: str, **kwargs) -> Dict:
        default_headers = self.patch_headers if method == "patch" else self.headers
        headers = kwargs.get("headers")
        kwargs["headers"] = dict(list(default_headers.items()) + list(headers.items())) if headers else default_headers
        return kwargs

    def _httpx_request(self, method: str, url: str, **kwargs) -> Response:
        return self._handle_response(self.client.request(method, url, **kwargs))

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

    @staticmethod
    def _handle_response(response: Response):
        if response.is_error:
            BaseClient._handle_exception(response)
        return response

    @staticmethod
    def _handle_exception(response: Response):
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise UnauthorizedException(response)
        elif response.status_code == HTTPStatus.BAD_REQUEST:
            raise BadRequestException(response)
        elif response.status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundException(response)
        elif response.status_code == HTTPStatus.CONFLICT:
            raise ConflictException(response)
        else:
            raise UnknownException(response)
