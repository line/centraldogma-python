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
from centraldogma.base_client import BaseClient
from centraldogma.data import Repository
from http import HTTPStatus
from typing import List

from centraldogma.exceptions import to_exception


class RepositoryService:
    def __init__(self, client: BaseClient):
        self.client = client

    def list(self, project_name: str, removed: bool) -> List[Repository]:
        params = {"status": "removed"} if removed else None
        resp = self.client.request(
            "get", f"/projects/{project_name}/repos", params=params
        )
        if resp.status_code == HTTPStatus.OK:
            return [Repository.from_dict(repo) for repo in resp.json()]
        elif resp.status_code == HTTPStatus.NO_CONTENT:
            return []
        else:
            raise to_exception(resp)

    def create(self, project_name: str, name: str) -> Repository:
        resp = self.client.request(
            "post", f"/projects/{project_name}/repos", json={"name": name}
        )
        if resp.status_code == HTTPStatus.CREATED:
            return Repository.from_dict(resp.json())
        raise to_exception(resp)

    def remove(self, project_name: str, name: str) -> None:
        resp = self.client.request("delete", f"/projects/{project_name}/repos/{name}")

        if resp.status_code == HTTPStatus.NO_CONTENT:
            return None
        raise to_exception(resp)

    def unremove(self, project_name: str, name: str) -> Repository:
        body = [{"op": "replace", "path": "/status", "value": "active"}]
        resp = self.client.request(
            "patch", f"/projects/{project_name}/repos/{name}", json=body
        )
        if resp.status_code == HTTPStatus.OK:
            return Repository.from_dict(resp.json())
        raise to_exception(resp)

    def purge(self, project_name: str, name: str) -> None:
        resp = self.client.request(
            "delete", f"/projects/{project_name}/repos/{name}/removed"
        )
        if resp.status_code == HTTPStatus.NO_CONTENT:
            return None
        raise to_exception(resp)

    def normalize_revision(self, project_name: str, name: str, revision: int) -> int:
        resp = self.client.request(
            "get", f"/projects/{project_name}/repos/{name}/revision/{revision}"
        )
        if resp.status_code == HTTPStatus.OK:
            return resp.json()["revision"]
        raise to_exception(resp)
