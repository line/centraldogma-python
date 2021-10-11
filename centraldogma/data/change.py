from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from typing import Optional, Union


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
    content: Optional[Union[map, str]]
