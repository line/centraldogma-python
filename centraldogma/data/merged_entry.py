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
from typing import List, Union

from dataclasses_json.core import Json

from centraldogma import util
from centraldogma.data.entry import EntryType
from centraldogma.data.revision import Revision
from centraldogma.exceptions import EntryNoContentException


class MergedEntry:
    @staticmethod
    def from_dict(json: Json):
        paths: List[str] = json["paths"]
        revision = Revision(json["revision"])
        entry_type = EntryType[json["type"]]
        content = json["content"]
        return MergedEntry(revision, paths, entry_type, content)

    def __init__(
        self, revision: Revision, paths: List[str], entry_type: EntryType, content: Json
    ):
        self.revision = revision
        self.paths = paths
        self.entry_type = entry_type
        self._content = content

    @property
    def content(self) -> Union[str, dict]:
        """Returns the content.

        :raises EntryNoContentException: it occurs if the content is ``None``
        """
        if not self._content:
            raise EntryNoContentException(
                f"{self.paths} (type: {self.entry_type}, revision: {self.revision.major})"
            )

        return self._content

    def __str__(self) -> str:
        return util.to_string(self)
