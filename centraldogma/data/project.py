from centraldogma.data.constants import DATE_FORMAT_ISO8601
from centraldogma.data.creator import Creator
from dataclasses import dataclass, field
from dataclasses_json import LetterCase, config, dataclass_json
from datetime import datetime
from marshmallow import fields


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Project:
    name: str
    creator: Creator
    url: str
    created_at: datetime = field(
        metadata=config(
            decoder=lambda x: datetime.strptime(x, DATE_FORMAT_ISO8601),
            mm_field=fields.DateTime(format=DATE_FORMAT_ISO8601),
        )
    )
