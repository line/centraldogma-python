#  Copyright 2021 LINE Corporation
#
#  LINE Corporation licenses this file to you under the Apache License,
#  version 2.0 (the "License"); you may not use this file except in compliance
#  with the License. You may obtain a copy of the License at:
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
from __future__ import annotations

import json
from enum import Enum
from typing import TypeVar, Generic, Any

from centraldogma import util
from centraldogma.data.revision import Revision
from centraldogma.exceptions import EntryNoContentException


class EntryType(Enum):
    JSON = "JSON"
    TEXT = "TEXT"
    DIRECTORY = "DIRECTORY"


T = TypeVar("T")


class Entry(Generic[T]):
    """A file or a directory in a repository."""

    @staticmethod
    def text(revision: Revision, path: str, content: str) -> Entry[str]:
        """Returns a newly-created ``Entry`` of a text file.

        :param revision: the revision of the text file
        :param path: the path of the text file
        :param content: the content of the text file
        """
        return Entry(revision, path, EntryType.TEXT, content)

    @staticmethod
    def json(revision: Revision, path: str, content: Any) -> Entry[Any]:
        """Returns a newly-created ``Entry`` of a JSON file.

        :param revision: the revision of the JSON file
        :param path: the path of the JSON file
        :param content: the content of the JSON file
        """
        if type(content) is str:
            content = json.loads(content)
        return Entry(revision, path, EntryType.JSON, content)

    @staticmethod
    def directory(revision: Revision, path: str) -> Entry[None]:
        """Returns a newly-created ``Entry`` of a directory.

        :param revision: the revision of the directory
        :param path: the path of the directory
        """
        return Entry(revision, path, EntryType.DIRECTORY, None)

    def __init__(
        self, revision: Revision, path: str, entry_type: EntryType, content: T
    ):
        self.revision = revision
        self.path = path
        self.entry_type = entry_type
        self._content = content
        self._content_as_text = None

    def has_content(self) -> bool:
        """Returns if this ``Entry`` has content, which is always ``True`` if it's not a directory."""
        return self.content is not None

    @property
    def content(self) -> T:
        """Returns the content.

        :raises EntryNoContentException: it occurs if the content is ``None``
        """
        if not self._content:
            raise EntryNoContentException(
                f"{self.path} (type: {self.entry_type}, revision: {self.revision.major})"
            )

        return self._content

    def content_as_text(self) -> str:
        """Returns the textual representation of the specified content.

        :raises EntryNoContentException: it occurs if the content is ``None``
        """
        if self._content_as_text:
            return self._content_as_text

        content = self.content
        if self.entry_type == EntryType.TEXT:
            self._content_as_text = content
        else:
            self._content_as_text = json.dumps(self.content)

        return self._content_as_text

    def __str__(self) -> str:
        return util.to_string(self)

    def __repr__(self) -> str:
        return self.__str__()
