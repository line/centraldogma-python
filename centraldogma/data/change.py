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
from enum import Enum
from typing import Optional, Any

from dataclasses_json import dataclass_json
from pydantic.dataclasses import dataclass


class ChangeType(Enum):
    UPSERT_JSON = "UPSERT_JSON"
    UPSERT_TEXT = "UPSERT_TEXT"
    REMOVE = "REMOVE"
    RENAME = "RENAME"
    APPLY_JSON_PATCH = "APPLY_JSON_PATCH"
    APPLY_TEXT_PATCH = "APPLY_TEXT_PATCH"


@dataclass_json
@dataclass
class Change:
    path: str
    type: ChangeType
    content: Optional[Any] = None
