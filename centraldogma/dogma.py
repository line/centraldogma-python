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
import os
from typing import List, Optional, TypeVar, Callable

from centraldogma.base_client import BaseClient
from centraldogma.content_service import ContentService

# noinspection PyUnresolvedReferences
from centraldogma.data import (
    Change,
    Commit,
    Content,
    ChangeType,
    Project,
    PushResult,
    Repository,
)
from centraldogma.data.entry import Entry
from centraldogma.data.merge_source import MergeSource
from centraldogma.data.merged_entry import MergedEntry
from centraldogma.data.revision import Revision
from centraldogma.project_service import ProjectService
from centraldogma.query import Query
from centraldogma.repository_service import RepositoryService
from centraldogma.repository_watcher import RepositoryWatcher, FileWatcher
from centraldogma.watcher import Watcher

T = TypeVar("T")
U = TypeVar("U")

_DEFAULT_WATCH_TIMEOUT_MILLIS = 1 * 60 * 1000  # 1 minute


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

    def remove_project(self, name: str) -> None:
        """Removes a project. Only the owner and an admin can remove the project."""
        return self.project_service.remove(name)

    def unremove_project(self, name: str) -> Project:
        """Unremoves a project which is removed before. Only an admin can unremove the project."""
        return self.project_service.unremove(name)

    def purge_project(self, name: str) -> None:
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

    def remove_repository(self, project_name: str, name: str) -> None:
        """Removes a repository. Only the owner and an admin can remove."""
        return self.repository_service.remove(project_name, name)

    def unremove_repository(self, project_name: str, name: str) -> Repository:
        """Unremoves a repository. Only the owner and an admin can unremove."""
        return self.repository_service.unremove(project_name, name)

    def purge_repository(self, project_name: str, name: str) -> None:
        """Purges a repository. Only the owner and an admin can purge a repository removed before."""
        return self.repository_service.purge(project_name, name)

    # TODO(ikhoon): Use `Revision` class instead of int
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

        :param path_pattern: A path pattern is a variant of glob as follows. |br|
            "/\*\*" - find all files recursively |br|
            "\*.json" - find all JSON files recursively |br|
            "/foo/\*.json" - find all JSON files under the directory /foo |br|
            "/\*/foo.txt" - find all files named foo.txt at the second depth level |br|
            "\*.json,/bar/\*.txt" - use comma to match any patterns |br|
            This will bring all of the files in the repository, if unspecified. |br|
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

        :param path_pattern: A path pattern is a variant of glob as follows. |br|
            "/\*\*" - find all files recursively |br|
            "\*.json" - find all JSON files recursively |br|
            "/foo/\*.json" - find all JSON files under the directory /foo |br|
            "/\*/foo.txt" - find all files named foo.txt at the second depth level |br|
            "\*.json,/bar/\*.txt" - use comma to match any patterns
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

    def push(
        self,
        project_name: str,
        repo_name: str,
        commit: Commit,
        changes: List[Change],
    ) -> PushResult:
        """Creates, replaces, renames or deletes files. The user should have write permission.

        :param commit: A commit message for changes.
        :param changes: Detailed changes including path, type and content.
            If the type is REMOVE, the content should be empty. If the type is RENAME,
            the content is supposed to be the new name.
        """
        return self.content_service.push(project_name, repo_name, commit, changes)

    def watch_repository(
        self,
        project_name: str,
        repo_name: str,
        last_known_revision: Revision,
        path_pattern: str,
        timeout_millis: int = _DEFAULT_WATCH_TIMEOUT_MILLIS,
    ) -> Optional[Revision]:
        """
        Waits for the files matched by the specified ``path_pattern`` to be changed since the specified
        ``last_known_revision``. If no changes were made within the specified ``timeout_millis``,
        ``None`` will be returned.
        It is recommended to specify the largest ``timeout_millis`` allowed by the server. If unsure, use
        the default watch timeout.

        :return: the latest known ``Revision`` which contains the changes for the matched files.
                 ``None`` if the files were not changed for ``timeout_millis`` milliseconds
                 since the invocation of this method.
        """
        return self.content_service.watch_repository(
            project_name, repo_name, last_known_revision, path_pattern, timeout_millis
        )

    def watch_file(
        self,
        project_name: str,
        repo_name: str,
        last_known_revision: Revision,
        query: Query[T],
        timeout_millis: int = _DEFAULT_WATCH_TIMEOUT_MILLIS,
    ) -> Optional[Entry[T]]:
        """
        Waits for the file matched by the specified ``Query`` to be changed since the specified
        ``last_known_revision``. If no changes were made within the specified ``timeout_millis``,
        ``None`` will be returned.
        It is recommended to specify the largest ``timeout_millis`` allowed by the server. If unsure, use
        the default watch timeout.

        :return: the ``Entry`` which contains the latest known ``Query`` result.
                 ``None`` if the file was not changed for ``timeout_millis`` milliseconds
                 since the invocation of this method.
        """
        return self.content_service.watch_file(
            project_name, repo_name, last_known_revision, query, timeout_millis
        )

    def repository_watcher(
        self,
        project_name: str,
        repo_name: str,
        path_pattern: str,
        function: Callable[[Revision], T] = lambda x: x,
        timeout_millis: int = _DEFAULT_WATCH_TIMEOUT_MILLIS,
    ) -> Watcher[T]:
        """
        Returns a ``Watcher`` which notifies its listeners when the specified repository has a new commit
        that contains the changes for the files matched by the given ``path_pattern``. e.g::
            def get_files(revision: Revision) -> List[Content]:
                return dogma.get_files("foo_project", "bar_repo", revision, "/*.json")

            with dogma.repository_watcher("foo_project", "bar_repo", "/*.json", get_files) as watcher:

                def listener(revision: Revision, contents: List[Content]) -> None:
                    ...

                watcher.watch(listener)

        Note that you may get ``RevisionNotFoundException`` during the ``get_files()`` call and
        may have to retry in the above example due to `a known issue`_.

        :param path_pattern: the path pattern to match files in the repository.
        :param function: the function to convert the given `Revision` into another.
        :param timeout_millis: the timeout millis for the watching request.

        .. _a known issue:
            https://github.com/line/centraldogma/issues/40
        """
        watcher = RepositoryWatcher(
            self.content_service,
            project_name,
            repo_name,
            path_pattern,
            timeout_millis,
            function,
        )
        watcher.start()
        return watcher

    def file_watcher(
        self,
        project_name: str,
        repo_name: str,
        query: Query[T],
        function: Callable[[T], U] = lambda x: x,
    ) -> Watcher[U]:
        """
        Returns a ``Watcher`` which notifies its listeners after applying the specified ``function`` when the result
        of the given ``Query`` becomes available or changes. e.g::

           with dogma.file_watcher("foo_project", "bar_repo", Query.json("/baz.json"),
                                   lambda content: MyType.from_dict(content)) as watcher:

               def listener(revision: Revision, value: MyType) -> None:
                   ...

               watcher.watch(listener)

        :param query: the query to watch a file or a content in the repository.
        :param function: the function to convert the given content into another.
        """
        watcher = FileWatcher(
            self.content_service,
            project_name,
            repo_name,
            query,
            _DEFAULT_WATCH_TIMEOUT_MILLIS,
            function,
        )
        watcher.start()
        return watcher

    def merge_files(
        self,
        project_name: str,
        repo_name: str,
        merge_sources: List[MergeSource],
        json_paths: Optional[List[str]] = None,
        revision: Optional[int] = None,
    ) -> MergedEntry:
        """Returns the merged result of files represented by ``MergeSource``. Each ``MergeSource``
        can be optional, indicating that no error should be thrown even if the path doesn't exist.
        If ``json_paths`` is specified, each ``json_path`` is applied recursively on the merged
        result. If any of the ``json_path``s is invalid, a ``QueryExecutionException`` is thrown.

        :raises ValueError: If the provided ``merge_sources`` is empty.
        :return: the ``MergedEntry`` which contains the merged content for the given query.
        """
        return self.content_service.merge_files(
            project_name, repo_name, merge_sources, json_paths or [], revision
        )
