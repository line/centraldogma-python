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
from centraldogma.data import Project
from http import HTTPStatus
from typing import List


class ProjectService:
    def __init__(self, client: BaseClient):
        self.client = client

    def list(self, removed: bool) -> List[Project]:
        params = {"status": "removed"} if removed else None
        resp = self.client.request("get", "/projects", params=params)
        if resp.status_code == HTTPStatus.NO_CONTENT:
            return []
        return [Project.from_dict(project) for project in resp.json()]

    def create(self, name: str) -> Project:
        resp = self.client.request("post", "/projects", json={"name": name})
        if resp.status_code != HTTPStatus.CREATED:
            return None
        return Project.from_dict(resp.json())

    def remove(self, name: str) -> bool:
        resp = self.client.request("delete", f"/projects/{name}")
        return True if resp.status_code == HTTPStatus.NO_CONTENT else False

    def unremove(self, name: str) -> Project:
        body = [{"op": "replace", "path": "/status", "value": "active"}]
        resp = self.client.request("patch", f"/projects/{name}", json=body)
        if resp.status_code != HTTPStatus.OK:
            return None
        return Project.from_dict(resp.json())

    def purge(self, name: str) -> bool:
        resp = self.client.request("delete", f"/projects/{name}/removed")
        return True if resp.status_code == HTTPStatus.NO_CONTENT else False
