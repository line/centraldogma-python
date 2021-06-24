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
from http import HTTPStatus
from typing import Dict
import requests


class BaseClient:
    PATH_PREFIX = "api/v1"

    def __init__(self, base_url: str, token: str, **configs):
        self.base_url = base_url
        self.token = token
        self.headers = self._get_headers(token)
        self.patch_headers = self._get_patch_headers(token)
        self.configs = configs

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs = self._get_kwargs(method, **kwargs)
        return self._request(method, self._create_url(path), **kwargs)

    def _create_url(self, path) -> str:
        return self.base_url + "/" + self.PATH_PREFIX + path

    def _get_kwargs(self, method: str, **kwargs) -> Dict:
        kwargs["headers"] = self.patch_headers if method == "patch" else self.headers
        kwargs.update(self.configs)
        return kwargs

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        return self._handle_response(getattr(requests, method)(url, **kwargs))

    @staticmethod
    def _get_headers(token: str) -> Dict:
        return {
            "Authorization": "bearer " + token,
            "Content-Type": "application/json",
        }

    @staticmethod
    def _get_patch_headers(token: str) -> Dict:
        return {
            "Authorization": "bearer " + token,
            "Content-Type": "application/json-patch+json",
        }

    @staticmethod
    def _handle_response(response: requests.Response):
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            BaseClient._handle_exception(response)
        return response

    @staticmethod
    def _handle_exception(response: requests.Response):
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise AuthorizationException(response)
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundException(response)
