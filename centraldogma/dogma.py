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
from centraldogma.content_service import ContentService
from centraldogma.data import Change, ChangeType, Commit, Content, Project, Repository
from centraldogma.project_service import ProjectService
from centraldogma.repository_service import RepositoryService
from typing import List, Optional
import os


class Dogma:
    DEFAULT_BASE_URL = "http://localhost:36462"
    DEFAULT_TOKEN = "anonymous"

    def __init__(self, base_url: str = None, token: str = None, **configs):
        """A Central Dogma API client using requests.

        : param base_url: a base URL indicating Central Dogma server such as domain.
        : param token: a token for authorization.
        : param configs: (optional) configurations for an HTTP client.
            For example, cert and timeout can be applied by using it.
        """
        if base_url is None:
            env_host = os.getenv("CENTRAL_DOGMA_HOST")
            base_url = env_host if env_host else self.DEFAULT_BASE_URL
        if token is None:
            env_token = os.getenv("CENTRAL_DOGMA_TOKEN")
            token = env_token if env_token else self.DEFAULT_TOKEN
        self.base_client = BaseClient(base_url, token, **configs)
        self.project_service = ProjectService(self.base_client)
        self.repository_service = RepositoryService(self.base_client)
        self.content_service = ContentService(self.base_client)

    def list_projects(self, removed: bool = False) -> List[Project]:
        """Lists all projects, in the order that they were created on the Central Dogma server."""
        return self.project_service.list(removed)

    def create_project(self, name: str) -> Project:
        """Creates a project. The creator of the project will become the owner of the project."""
        return self.project_service.create(name)

    def remove_project(self, name: str) -> bool:
        """Removes a project. Only the owner and an admin can remove the project."""
        return self.project_service.remove(name)

    def unremove_project(self, name: str) -> Project:
        """Unremoves a project which is removed before. Only an admin can unremove the project."""
        return self.project_service.unremove(name)

    def purge_project(self, name: str) -> bool:
        """Purges a project. Only the owner and an admin can purge the project removed before."""
        return self.project_service.purge(name)

    def list_repositories(
        self, project_name: str, removed: bool = False
    ) -> List[Repository]:
        """Lists all repositories, in the order that they were created on the Central Dogma server."""
        return self.repository_service.list(project_name, removed)

    def create_repository(self, project_name: str, name: str) -> Repository:
        """Creates a repository. Only the owner and an admin can create."""
        return self.repository_service.create(project_name, name)

    def remove_repository(self, project_name: str, name: str) -> bool:
        """Removes a repository. Only the owner and an admin can remove."""
        return self.repository_service.remove(project_name, name)

    def unremove_repository(self, project_name: str, name: str) -> Repository:
        """Unremoves a repository. Only the owner and an admin can unremove."""
        return self.repository_service.unremove(project_name, name)

    def purge_repository(self, project_name: str, name: str) -> bool:
        """Purges a repository. Only the owner and an admin can purge a repository removed before."""
        return self.repository_service.purge(project_name, name)

    def normalize_repository_revision(
        self, project_name: str, name: str, revision: int
    ) -> int:
        """Normalizes the revision into an absolute revision."""
        return self.repository_service.normalize_revision(project_name, name, revision)

    def list_files(
        self,
        project_name: str,
        repo_name: str,
        path_pattern: Optional[str] = None,
        revision: Optional[int] = None,
    ) -> List[Content]:
        """Lists files. The user should have read permission at least.

        :param path_pattern: A path pattern is a variant of glob as follows.
            "/**" - find all files recursively
            "*.json" - find all JSON files recursively
            "/foo/*.json" - find all JSON files under the directory /foo
            "/*/foo.txt" - find all files named foo.txt at the second depth level
            "*.json,/bar/*.txt" - use comma to match any patterns
            This will bring all of the files in the repository, if unspecified.
        :param revision: The revision of the list to get. If not specified, gets the list of
            the latest revision.
        """
        return self.content_service.get_files(
            project_name, repo_name, path_pattern, revision, include_content=False
        )

    def get_files(
        self,
        project_name: str,
        repo_name: str,
        path_pattern: Optional[str] = None,
        revision: Optional[int] = None,
    ) -> List[Content]:
        """Gets files. The user should have read permission at least. The difference from
            the API List files is that this includes the content of the files.

        :param path_pattern: A path pattern is a variant of glob as follows.
            "/**" - find all files recursively
            "*.json" - find all JSON files recursively
            "/foo/*.json" - find all JSON files under the directory /foo
            "/*/foo.txt" - find all files named foo.txt at the second depth level
            "*.json,/bar/*.txt" - use comma to match any patterns
            This will bring all of the files in the repository, if unspecified.
        :param revision: The revision of the list to get. If not specified, gets the list of
            the latest revision.
        """
        return self.content_service.get_files(
            project_name, repo_name, path_pattern, revision, include_content=True
        )

    def get_file(
        self,
        project_name: str,
        repo_name: str,
        file_path: str,
        revision: Optional[int] = None,
        json_path: Optional[str] = None,
    ) -> Content:
        """Gets a file. The user should have read permission at least.

        :param revision: The revision of the file to get. If not specified, gets the file of
            the latest revision.
        :param json_path: The JSON path expressions.
        """
        return self.content_service.get_file(
            project_name, repo_name, file_path, revision, json_path
        )

    def push_changes(
        self,
        project_name: str,
        repo_name: str,
        commit: Commit,
        changes: List[Change],
    ):
        """Creates, replaces, renames or deletes files. The user should have write permission.

        :param commit:
        :param changes:
        """
        return self.content_service.push_changes(
            project_name, repo_name, commit, changes
        )
