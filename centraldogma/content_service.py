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
from typing import List, Optional, TypeVar, Any, Callable, Dict
from urllib.parse import quote

from httpx import Response

from centraldogma.base_client import BaseClient
from centraldogma.data import Content
from centraldogma.data.change import Change
from centraldogma.data.commit import Commit
from centraldogma.data.entry import Entry, EntryType
from centraldogma.data.merge_source import MergeSource
from centraldogma.data.merged_entry import MergedEntry
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

        handler = {
            HTTPStatus.OK: lambda resp: [
                Content.from_dict(content) for content in resp.json()
            ],
            HTTPStatus.NO_CONTENT: lambda resp: [],
        }
        return self.client.request("get", path, params=params, handler=handler)

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

        handler = {HTTPStatus.OK: lambda resp: Content.from_dict(resp.json())}
        return self.client.request("get", path, params=params, handler=handler)

    def push(
        self,
        project_name: str,
        repo_name: str,
        commit: Commit,
        # TODO(ikhoon): Make changes accept varargs?
        changes: List[Change],
    ) -> PushResult:
        params = {
            "commitMessage": asdict(commit),
            "changes": [
                asdict(change, dict_factory=self._change_dict) for change in changes
            ],
        }
        path = f"/projects/{project_name}/repos/{repo_name}/contents"
        handler = {HTTPStatus.OK: lambda resp: PushResult.from_dict(resp.json())}
        return self.client.request("post", path, json=params, handler=handler)

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

        path += quote(path_pattern)

        handler = {
            HTTPStatus.OK: lambda resp: Revision(resp.json()["revision"]),
            HTTPStatus.NOT_MODIFIED: lambda resp: None,
        }
        return self._watch(last_known_revision, timeout_millis, path, handler)

    def watch_file(
        self,
        project_name: str,
        repo_name: str,
        last_known_revision: Revision,
        query: Query[T],
        timeout_millis: int,
    ) -> Optional[Entry[T]]:
        path = f"/projects/{project_name}/repos/{repo_name}/contents/{query.path}"
        if query.query_type == QueryType.JSON_PATH:
            queries = [f"jsonpath={quote(expr)}" for expr in query.expressions]
            path = f"{path}?{'&'.join(queries)}"

        def on_ok(response: Response) -> Entry:
            json = response.json()
            revision = Revision(json["revision"])
            return self._to_entry(revision, json["entry"], query.query_type)

        handler = {HTTPStatus.OK: on_ok, HTTPStatus.NOT_MODIFIED: lambda resp: None}
        return self._watch(last_known_revision, timeout_millis, path, handler)

    def merge_files(
        self,
        project_name: str,
        repo_name: str,
        merge_sources: List[MergeSource],
        json_paths: Optional[List[str]],
        revision: Optional[int],
    ) -> MergedEntry:
        if not merge_sources:
            raise ValueError("at least one MergeSource is required")
        path = f"/projects/{project_name}/repos/{repo_name}/merge"
        queries = []
        if revision:
            queries.append(f"revision={revision}")
        for merge_source in merge_sources:
            query = (
                f"optional_path={merge_source.path}"
                if merge_source.optional
                else f"path={merge_source.path}"
            )
            queries.append(query)
        for json_path in json_paths:
            queries.append(f"jsonpath={json_path}")
        path = f"{path}?{'&'.join(queries)}"
        handler = {HTTPStatus.OK: lambda resp: MergedEntry.from_dict(resp.json())}
        return self.client.request("get", path, handler=handler)

    def _watch(
        self,
        last_known_revision: Revision,
        timeout_millis: int,
        path: str,
        handler: Dict[int, Callable[[Response], T]],
    ) -> T:
        normalized_timeout = (timeout_millis + 999) // 1000
        headers = {
            "if-none-match": f"{last_known_revision.major}",
            "prefer": f"wait={normalized_timeout}",
        }
        return self.client.request(
            "get", path, handler=handler, headers=headers, timeout=normalized_timeout
        )

    @staticmethod
    def _to_entry(revision: Revision, json: Any, query_type: QueryType) -> Entry:
        entry_path = json["path"]
        received_entry_type = EntryType[json["type"]]
        content = json["content"]
        if query_type == QueryType.IDENTITY_TEXT:
            return Entry.text(revision, entry_path, content)
        elif query_type == QueryType.IDENTITY_JSON or query_type == QueryType.JSON_PATH:
            if received_entry_type != EntryType.JSON:
                raise CentralDogmaException(
                    f"invalid entry type. entry type: {received_entry_type} (expected: {query_type})"
                )

            return Entry.json(revision, entry_path, content)
        elif query_type == QueryType.IDENTITY:
            if received_entry_type == EntryType.JSON:
                return Entry.json(revision, entry_path, content)
            elif received_entry_type == EntryType.TEXT:
                return Entry.text(revision, entry_path, content)
            elif received_entry_type == EntryType.DIRECTORY:
                return Entry.directory(revision, entry_path)

    @staticmethod
    def _change_dict(data):
        return {
            field: value.value if isinstance(value, Enum) else value
            for field, value in data
        }
