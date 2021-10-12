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
from centraldogma.data.constants import DATE_FORMAT_ISO8601
from centraldogma.data.creator import Creator
from dataclasses import dataclass, field
from dataclasses_json import LetterCase, config, dataclass_json
from datetime import datetime
from marshmallow import fields
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Project:
    name: str
    creator: Optional[Creator] = None
    created_at: Optional[datetime] = field(
        default=None,
        metadata=config(
            decoder=lambda x: datetime.strptime(x, DATE_FORMAT_ISO8601) if x else None,
            mm_field=fields.DateTime(format=DATE_FORMAT_ISO8601),
        ),
    )
    url: Optional[str] = None
