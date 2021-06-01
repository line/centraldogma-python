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
