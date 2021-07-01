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
import json


class RepositoryService:
    def __init__(self, client: BaseClient):
        self.client = client

    def list(self, project_name: str, removed: bool) -> List[Repository]:
        params = {"status": "removed"} if removed else None
        resp = self.client.request(
            "get", f"/projects/{project_name}/repos", params=params
        )
        if resp.status_code == HTTPStatus.NO_CONTENT:
            return []
        return [Repository.from_json(json.dumps(repo)) for repo in resp.json()]

    def create(self, project_name: str, name: str) -> Repository:
        resp = self.client.request(
            "post", f"/projects/{project_name}/repos", json={"name": name}
        )
        if resp.status_code != HTTPStatus.CREATED:
            return None
        return Repository.from_json(json.dumps(resp.json()))

    def remove(self, project_name: str, name: str) -> bool:
        resp = self.client.request("delete", f"/projects/{project_name}/repos/{name}")
        return True if resp.status_code == HTTPStatus.NO_CONTENT else False

    def unremove(self, project_name: str, name: str) -> Repository:
        body = [{"op": "replace", "path": "/status", "value": "active"}]
        resp = self.client.request(
            "patch", f"/projects/{project_name}/repos/{name}", json=body
        )
        if resp.status_code != HTTPStatus.OK:
            return None
        return Repository.from_json(json.dumps(resp.json()))

    def purge(self, project_name: str, name: str) -> bool:
        resp = self.client.request(
            "delete", f"/projects/{project_name}/repos/{name}/removed"
        )
        return True if resp.status_code == HTTPStatus.NO_CONTENT else False

    def normalize_revision(self, project_name: str, name: str, revision: int) -> int:
        resp = self.client.request(
            "get", f"/projects/{project_name}/repos/{name}/revision/{revision}"
        )
        return resp.json()["revision"] if resp.status_code == HTTPStatus.OK else None
