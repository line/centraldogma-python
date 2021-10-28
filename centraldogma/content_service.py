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
from dataclasses import asdict
from enum import Enum
from http import HTTPStatus
from typing import List, Optional, TypeVar, Any

from urllib.parse import quote

from httpx import Response

from centraldogma.base_client import BaseClient
from centraldogma.data.change import Change
from centraldogma.data.commit import Commit
from centraldogma.data.content import Content
from centraldogma.data.entry import Entry, EntryType
from centraldogma.data.push_result import PushResult
from centraldogma.data.revision import Revision
from centraldogma.exceptions import CentralDogmaException
from centraldogma.query import Query, QueryType

T = TypeVar("T")


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
        return Content.from_dict(resp.json())

    def push(
        self,
        project_name: str,
        repo_name: str,
        commit: Commit,
        changes: List[Change],
    ) -> PushResult:
        params = {
            "commitMessage": asdict(commit),
            "changes": [
                asdict(change, dict_factory=self._change_dict) for change in changes
            ],
        }
        path = f"/projects/{project_name}/repos/{repo_name}/contents"
        resp = self.client.request("post", path, json=params)
        json: object = resp.json()
        return PushResult.from_dict(json)

    def watch_repository(
        self,
        project_name: str,
        repo_name: str,
        last_known_revision: Revision,
        path_pattern: str,
        timeout_millis: int,
    ) -> Optional[Revision]:
        path = f"/projects/{project_name}/repos/{repo_name}/contents"
        if path_pattern[0] != "/":
            path += "/**/"

        if path_pattern in " ":
            path_pattern = path_pattern.replace(" ", "%20")
        path += path_pattern

        response = self._watch(last_known_revision, timeout_millis, path)
        if response.status_code == HTTPStatus.OK:
            json = response.json()
            return Revision(json["revision"])
        elif response.status_code == HTTPStatus.NOT_MODIFIED:
            return None
        else:
            # TODO(ikhoon): Handle excepitons after https://github.com/line/centraldogma-python/pull/11/ is merged.
            pass

    def watch_file(
        self,
        project_name: str,
        repo_name: str,
        last_known_revision: Revision,
        query: Query[T],
        timeout_millis,
    ) -> Optional[Entry[T]]:
        path = f"/projects/{project_name}/repos/{repo_name}/contents/{query.path}"
        if query.query_type == QueryType.JSON_PATH:
            queries = [f"jsonpath={quote(expr)}" for expr in query.expressions]
            path = f"{path}?{'&'.join(queries)}"

        response = self._watch(last_known_revision, timeout_millis, path)
        if response.status_code == HTTPStatus.OK:
            json = response.json()
            revision = Revision(json["revision"])
            return self._to_entry(revision, json["entry"], query.query_type)
        elif response.status_code == HTTPStatus.NOT_MODIFIED:
            return None
        else:
            # TODO(ikhoon): Handle excepitons after https://github.com/line/centraldogma-python/pull/11/ is merged.
            pass

    @staticmethod
    def _to_entry(revision: Revision, json: Any, query_type: QueryType) -> Entry:
        entry_path = json["path"]
        received_entry_type = EntryType[json["type"]]
        content = json["content"]
        if query_type == QueryType.IDENTITY_TEXT:
            return Entry.text(revision, entry_path, content)
        elif query_type == QueryType.IDENTITY or query_type == QueryType.JSON_PATH:
            if received_entry_type != EntryType.JSON:
                raise CentralDogmaException(
                    f"invalid entry type. entry type: {received_entry_type} (expected: {query_type})"
                )

            return Entry.json(revision, entry_path, content)
        else:  # query_type == QueryType.IDENTITY
            if received_entry_type == EntryType.JSON:
                return Entry.json(revision, entry_path, content)
            elif received_entry_type == EntryType.TEXT:
                return Entry.text(revision, entry_path, content)
            else:  # received_entry_type == EntryType.DIRECTORY
                return Entry.directory(revision, entry_path)

    def _watch(
        self, last_known_revision: Revision, timeout_millis: int, path: str
    ) -> Response:
        normalized_timeout = (timeout_millis + 999) // 1000
        headers = {
            "if-none-match": f"{last_known_revision.major}",
            "prefer": f"wait={normalized_timeout}",
        }
        return self.client.request(
            "get", path, headers=headers, timeout=normalized_timeout
        )

    def _change_dict(self, data):
        return {
            field: value.value if isinstance(value, Enum) else value
            for field, value in data
        }
