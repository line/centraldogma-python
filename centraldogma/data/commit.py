from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional


@dataclass_json
@dataclass
class Commit:
    summary: str
    detail: Optional[str] = None
    markup: Optional[str] = None
