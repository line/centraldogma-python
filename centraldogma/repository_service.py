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
from typing import List

from centraldogma.base_client import BaseClient
from centraldogma.data import Repository


class RepositoryService:
    def __init__(self, client: BaseClient):
        self.client = client

    def list(self, project_name: str, removed: bool) -> List[Repository]:
        params = {"status": "removed"} if removed else None
        handler = {
            HTTPStatus.OK: lambda resp: [
                Repository.from_dict(repo) for repo in resp.json()
            ],
            HTTPStatus.NO_CONTENT: lambda resp: [],
        }
        return self.client.request(
            "get", f"/projects/{project_name}/repos", params=params, handler=handler
        )

    def create(self, project_name: str, name: str) -> Repository:
        handler = {HTTPStatus.CREATED: lambda resp: Repository.from_dict(resp.json())}
        return self.client.request(
            "post",
            f"/projects/{project_name}/repos",
            json={"name": name},
            handler=handler,
        )

    def remove(self, project_name: str, name: str) -> None:
        handler = {HTTPStatus.NO_CONTENT: lambda resp: None}
        return self.client.request(
            "delete", f"/projects/{project_name}/repos/{name}", handler=handler
        )

    def unremove(self, project_name: str, name: str) -> Repository:
        body = [{"op": "replace", "path": "/status", "value": "active"}]
        handler = {HTTPStatus.OK: lambda resp: Repository.from_dict(resp.json())}
        return self.client.request(
            "patch",
            f"/projects/{project_name}/repos/{name}",
            json=body,
            handler=handler,
        )

    def purge(self, project_name: str, name: str) -> None:
        handler = {HTTPStatus.NO_CONTENT: lambda resp: None}
        return self.client.request(
            "delete", f"/projects/{project_name}/repos/{name}/removed", handler=handler
        )

    def normalize_revision(self, project_name: str, name: str, revision: int) -> int:
        handler = {HTTPStatus.OK: lambda resp: resp.json()["revision"]}
        return self.client.request(
            "get",
            f"/projects/{project_name}/repos/{name}/revision/{revision}",
            handler=handler,
        )
