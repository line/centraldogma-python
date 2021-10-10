from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional


@dataclass_json
@dataclass
class Change:
    path: str
    type: str
    content: Optional[str]
