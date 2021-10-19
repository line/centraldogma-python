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
import json
from dataclasses import dataclass
from http import HTTPStatus
from json import JSONDecodeError
from typing import Dict, Any, Callable

from dataclasses_json import dataclass_json
from requests import Response


class CentralDogmaException(Exception):
    pass


class UnauthorizedException(CentralDogmaException):
    pass


class BadRequestException(CentralDogmaException):
    pass


class NotFoundException(CentralDogmaException):
    pass


class UnknownException(CentralDogmaException):
    pass


class ProjectExistsException(CentralDogmaException):
    pass


class ProjectNotFoundException(CentralDogmaException):
    pass


class QueryExecutionException(CentralDogmaException):
    pass


class RedundantChangeException(CentralDogmaException):
    pass


class RevisionNotFoundException(CentralDogmaException):
    pass


class EntryNotFoundException(CentralDogmaException):
    pass


class ChangeConflictException(CentralDogmaException):
    pass


class RepositoryNotFoundException(CentralDogmaException):
    pass


class AuthorizationException(CentralDogmaException):
    pass


class ShuttingDownException(CentralDogmaException):
    pass


class RepositoryExistsException(CentralDogmaException):
    pass


_EXCEPTION_FACTORIES: dict[str, Callable[[str], CentralDogmaException]] = {
    "com.linecorp.centraldogma.common." + exception.__name__: exception for exception in
    [ProjectExistsException, ProjectNotFoundException, QueryExecutionException, RedundantChangeException,
     RevisionNotFoundException, EntryNotFoundException, ChangeConflictException, RepositoryNotFoundException,
     AuthorizationException, ShuttingDownException, RepositoryExistsException]
}


def to_exception(response: Response) -> CentralDogmaException:
    try:
        body = response.json()
    except JSONDecodeError:
        return UnknownException(response.text)

    exception = body["exception"]
    if exception is not None:
        exception_type = _EXCEPTION_FACTORIES.get(exception)
        if exception_type is not None:
            return exception_type(body["message"])

    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise UnauthorizedException(response)
    elif response.status_code == HTTPStatus.BAD_REQUEST:
        raise BadRequestException(response)
    elif response.status_code == HTTPStatus.NOT_FOUND:
        raise NotFoundException(response)
    else:
        raise UnknownException(response.text)
