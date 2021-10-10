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
from centraldogma.data.change import Change
from centraldogma.data.commit import Commit
from centraldogma.base_client import BaseClient
from centraldogma.data import Content
from http import HTTPStatus
from typing import List, Optional


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
        return [Content.from_dict(content) for content in resp.json()]

    def get_file(
        self,
        project_name: str,
        repo_name: str,
        file_path: str,
        revision: Optional[int],
        json_path: Optional[str],
    ) -> Content:
        params = {}
        if revision:
            params["revision"] = revision
        if json_path:
            params["jsonpath"] = json_path
        if not file_path.startswith("/"):
            file_path = "/" + file_path
        path = f"/projects/{project_name}/repos/{repo_name}/contents{file_path}"
        resp = self.client.request("get", path, params=params)
        if resp.status_code != HTTPStatus.OK:
            # TODO(@hexoul): Instead of returning None, raise a proper exception like Java client.
            return None
        return Content.from_dict(resp.json())

    def push_changes(
        self,
        commit: Commit,
        changes: List[Change],
    ):
        pass
