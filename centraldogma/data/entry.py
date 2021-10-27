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
from enum import Enum, auto
from typing import TypeVar, Generic, Any

from centraldogma.data.revision import Revision
from centraldogma.exceptions import EntryNoContentException


class EntryType(Enum):
    JSON = auto()
    TEXT = auto()
    DIRECTORY = auto()


T = TypeVar('T')


class Entry(Generic[T]):

    @staticmethod
    def text(revision: Revision, path: str, content: str) -> Entry[str]:
        return Entry(revision, path, EntryType.TEXT, content)

    @staticmethod
    def json(revision: Revision, path: str, content: Any) -> Entry[Any]:
        if type(content) is str:
            content = json.loads(content)
        return Entry(revision, path, EntryType.JSON, content)

    @staticmethod
    def directory(revision: Revision, path: str) -> Entry[None]:
        return Entry(revision, path, EntryType.DIRECTORY, None)

    def __init__(self, revision: Revision, path: str, entry_type: EntryType, content: T):
        self.revision = revision
        self.path = path
        self.entry_type = entry_type
        self._content = content
        self._content_as_text = None

    def has_content(self) -> bool:
        return self.content is not None

    @property
    def content(self) -> T:
        if self._content is None:
            raise EntryNoContentException(f"{self.path} (type: {self.entry_type}, revision: {self.revision.major})")

        return self._content

    def content_as_text(self) -> str:
        if self._content_as_text is not None:
            return self._content_as_text

        if self.entry_type == EntryType.TEXT:
            self._content_as_text = self.content
        elif self.entry_type == EntryType.DIRECTORY:
            self._content_as_text = ''
        else:
            self._content_as_text = json.dumps(self.content)

        return self._content_as_text
