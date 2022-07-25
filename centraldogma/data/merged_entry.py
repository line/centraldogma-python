#  Copyright 2022 LINE Corporation
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
from typing import Generic, TypeVar, List, Any

from centraldogma import util
from centraldogma.data.entry import EntryType
from centraldogma.data.revision import Revision
from centraldogma.exceptions import CentralDogmaException, EntryNoContentException

T = TypeVar("T")


class MergedEntry(Generic[T]):

    @staticmethod
    def from_dict(json: Any):
        paths: List[str] = json["paths"]
        if len(paths) == 0:
            raise CentralDogmaException(f"paths is unexpectedly empty for json: {json}")
        revision = Revision(json["revision"])
        entry_type = EntryType[json["type"]]
        content = json["content"]
        # TODO: validate that entry_type matches content
        return MergedEntry(revision, paths, entry_type, content)

    def __init__(
        self, revision: Revision, paths: List[str], entry_type: EntryType, content: T
    ):
        self.revision = revision
        self.paths = paths
        self.entry_type = entry_type
        self._content = content

    @property
    def content(self) -> T:
        """
        Returns the content.

        :exception EntryNoContentException if the content is ``None``
        """
        if not self._content:
            raise EntryNoContentException(
                f"{self.paths} (type: {self.entry_type}, revision: {self.revision.major})"
            )

        return self._content

    def __str__(self) -> str:
        return util.to_string(self)
