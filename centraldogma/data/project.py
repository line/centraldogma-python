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
