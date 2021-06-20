from centraldogma.base_client import BaseClient
from centraldogma.data import Content
from http import HTTPStatus
from typing import List, Optional
import json


class ContentService:
    def __init__(self, client: BaseClient):
        self.client = client

    def get_files(
        self,
        project_name: str,
        repo_name: str,
        path_pattern: Optional[str],
        revision: Optional[int],
        include_content: bool = False,
    ) -> List[Content]:
        params = {"revision": revision} if revision else None
        path = f"/projects/{project_name}/repos/{repo_name}/"
        path += "contents" if include_content else "list"
        if path_pattern:
            if path_pattern.startswith("/"):
                path += path_pattern
            else:
                path += "/" + path_pattern
        resp = self.client.request("get", path, params=params)
        if resp.status_code == HTTPStatus.NO_CONTENT:
            return []
        return [Content.from_json(json.dumps(content)) for content in resp.json()]

    def get_file(
        self,
        project_name: str,
        repo_name: str,
        file_path: str,
        revision: Optional[int],
        json_path: Optional[str],
    ) -> Content:
        params = {}
        params["revision"] = revision if revision else None
        params["jsonpath"] = json_path if json_path else None
        if not file_path.startswith("/"):
            file_path = "/" + file_path
        path = f"/projects/{project_name}/repos/{repo_name}/contents{file_path}"
        resp = self.client.request("get", path, params=params)
        if resp.status_code != HTTPStatus.OK:
            # TODO(@hexoul): Instead of returning None, raise a proper exception like Java client.
            return None
        return Content.from_json(json.dumps(resp.json()))
