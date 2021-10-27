#  Copyright 2021 LINE Corporation
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
from __future__ import annotations

from enum import Enum, auto
from typing import TypeVar, Generic, Any, List


class QueryType(Enum):
    IDENTITY = auto()
    IDENTITY_TEXT = auto()
    IDENTITY_JSON = auto()
    JSON_PATH = auto()


T = TypeVar('T')


class Query(Generic[T]):

    @staticmethod
    def identity(path: str) -> Query[str]:
        return Query(path=path, query_type=QueryType.IDENTITY, expressions=[])

    @staticmethod
    def text(path: str) -> Query[str]:
        return Query(path=path, query_type=QueryType.IDENTITY_TEXT, expressions=[])

    @staticmethod
    def json(path: str) -> Query[Any]:
        return Query(path=path, query_type=QueryType.IDENTITY_JSON, expressions=[])

    @staticmethod
    def json_path(path: str, json_paths: List[str]) -> Query[Any]:
        return Query(path=path, query_type=QueryType.JSON_PATH, expressions=json_paths)

    def __init__(self, path: str, query_type: QueryType, expressions: List[str]):
        self.path = path
        self.query_type = query_type
        self.expressions = expressions
