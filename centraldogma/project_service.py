from centraldogma.base_client import BaseClient
from centraldogma.data import Project
from http import HTTPStatus
from typing import List
import json


class ProjectService:
    def __init__(self, client: BaseClient):
        self.client = client

    def list(self, removed: bool) -> List[Project]:
        params = {"status": "removed"} if removed else None
        resp = self.client.request("get", "/projects", params=params)
        if resp.status_code == HTTPStatus.NO_CONTENT:
            return []
        return [Project.from_json(json.dumps(project)) for project in resp.json()]

    def create(self, name: str) -> Project:
        resp = self.client.request("post", "/projects", json={"name": name})
        if resp.status_code != HTTPStatus.CREATED:
            return None
        return Project.from_json(json.dumps(resp.json()))

    def remove(self, name: str) -> bool:
        resp = self.client.request("delete", f"/projects/{name}")
        return True if resp.status_code == HTTPStatus.NO_CONTENT else False

    def unremove(self, name: str) -> Project:
        body = [{"op": "replace", "path": "/status", "value": "active"}]
        resp = self.client.request("patch", f"/projects/{name}", json=body)
        if resp.status_code != HTTPStatus.OK:
            return None
        return Project.from_json(json.dumps(resp.json()))

    def purge(self, name: str) -> bool:
        resp = self.client.request("delete", f"/projects/{name}/removed")
        return True if resp.status_code == HTTPStatus.NO_CONTENT else False
