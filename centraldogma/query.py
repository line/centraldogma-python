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

from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeVar, Generic, Any, List


class QueryType(Enum):
    IDENTITY = auto()
    IDENTITY_TEXT = auto()
    IDENTITY_JSON = auto()
    JSON_PATH = auto()


T = TypeVar("T")


@dataclass
class Query(Generic[T]):
    """
    A query on a file.
    """

    path: str
    query_type: QueryType
    expressions: List[str]

    @staticmethod
    def identity(path: str) -> Query[str]:
        """
        Returns a newly-created ``Query`` that retrieves the content as it is.

        :param path: the path of a file being queried on
        """
        return Query(path=path, query_type=QueryType.IDENTITY, expressions=[])

    @staticmethod
    def text(path: str) -> Query[str]:
        """
        Returns a newly-created ``Query`` that retrieves the textual content as it is.

        :param path: the path of a file being queried on
        """
        return Query(path=path, query_type=QueryType.IDENTITY_TEXT, expressions=[])

    @staticmethod
    def json(path: str) -> Query[Any]:
        """
        Returns a newly-created ``Query`` that retrieves the JSON content as it is.

        :param path: the path of a file being queried on
        """
        return Query(path=path, query_type=QueryType.IDENTITY_JSON, expressions=[])

    @staticmethod
    def json_path(path: str, json_paths: List[str]) -> Query[Any]:
        """
        Returns a newly-created ``Query`` that applies a series of
        `JSON path expressions <https://github.com/json-path/JsonPath/blob/master/README.md>`_ to the content.

        :param path: the path of a file being queried on
        :param json_paths: the JSON path expressions to apply
        """
        return Query(path=path, query_type=QueryType.JSON_PATH, expressions=json_paths)
