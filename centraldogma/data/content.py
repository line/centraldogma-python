from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Any, Optional


@dataclass_json
@dataclass
class Content:
    path: str
    type: str
    url: str
    revision: int
    content: Optional[Any] = None
