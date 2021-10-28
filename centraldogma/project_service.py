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
from centraldogma.data import Project


class ProjectService:
    def __init__(self, client: BaseClient):
        self.client = client

    def list(self, removed: bool) -> List[Project]:
        params = {"status": "removed"} if removed else None
        handler = {
            HTTPStatus.OK: lambda resp: [
                Project.from_dict(project) for project in resp.json()
            ],
            HTTPStatus.NO_CONTENT: lambda resp: [],
        }
        return self.client.request("get", "/projects", params=params, handler=handler)

    def create(self, name: str) -> Project:
        handler = {HTTPStatus.CREATED: lambda resp: Project.from_dict(resp.json())}
        return self.client.request(
            "post", "/projects", json={"name": name}, handler=handler
        )

    def remove(self, name: str) -> None:
        handler = {HTTPStatus.NO_CONTENT: lambda resp: None}
        return self.client.request("delete", f"/projects/{name}", handler=handler)

    def unremove(self, name: str) -> Project:
        body = [{"op": "replace", "path": "/status", "value": "active"}]
        handler = {HTTPStatus.OK: lambda resp: Project.from_dict(resp.json())}
        return self.client.request(
            "patch", f"/projects/{name}", json=body, handler=handler
        )

    def purge(self, name: str) -> None:
        handler = {HTTPStatus.NO_CONTENT: lambda resp: None}
        return self.client.request(
            "delete", f"/projects/{name}/removed", handler=handler
        )
