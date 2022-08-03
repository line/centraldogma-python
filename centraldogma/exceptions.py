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
from http import HTTPStatus
from json import JSONDecodeError
from typing import Callable, Dict

from httpx import Response


class CentralDogmaException(Exception):
    """An exception that is raised when failed to access Central Dogma."""

    pass


class BadRequestException(CentralDogmaException):
    """An exception indicating a 400 Bad Client Request."""

    pass


class NotFoundException(CentralDogmaException):
    """An exception indicating a 404 Not Found."""

    pass


class UnauthorizedException(CentralDogmaException):
    """An exception indicating a 401 Unauthorized."""

    pass


class ForbiddenException(CentralDogmaException):
    """An exception indicating that an access to a resource requested by a client has been forbidden
    by the Central Dogma.
    """

    pass


class UnknownException(CentralDogmaException):
    """An exception used for reporting unknown exceptions."""

    pass


class InvalidResponseException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when a client received an invalid response."""

    pass


# The exceptions defined in upstream. The following types will be populated from an error response with
# _EXCEPTION_FACTORIES.
# https://github.com/line/centraldogma/blob/b167d594af5abc06af30d7d6d7d8b68b320861d8/client/java-armeria/src/main/java/com/linecorp/centraldogma/client/armeria/ArmeriaCentralDogma.java#L119-L132
class ProjectExistsException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when attempted to create a project with an existing project name."""

    pass


class ProjectNotFoundException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when attempted to access a non-existent project."""

    pass


class QueryExecutionException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when the evaluation of a `Query` has failed."""

    pass


class RedundantChangeException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when attempted to push a commit without effective changes."""

    pass


class RevisionNotFoundException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when attempted to access a non-existent revision."""

    pass


class EntryNotFoundException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when attempted to access a non-existent entry in a repository."""

    pass


class ChangeConflictException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when attempted to push a commit which cannot be applied
    without a conflict.
    """

    pass


class RepositoryNotFoundException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when attempted to access a non-existent repository."""

    pass


class AuthorizationException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when a client failed to authenticate or attempted to
    perform an unauthorized operation.
    """

    pass


class ShuttingDownException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when Central Dogma cannot handle a request
    because it's shutting down.
    """

    pass


class RepositoryExistsException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when attempted to create a repository
    with an existing repository name.
    """

    pass


class EntryNoContentException(CentralDogmaException):
    """A ``CentralDogmaException`` that is raised when attempted to retrieve the content from a directory entry."""

    pass


_EXCEPTION_FACTORIES: Dict[str, Callable[[str], CentralDogmaException]] = {
    "com.linecorp.centraldogma.common." + exception.__name__: exception
    for exception in [
        ProjectExistsException,
        ProjectNotFoundException,
        QueryExecutionException,
        RedundantChangeException,
        RevisionNotFoundException,
        EntryNotFoundException,
        ChangeConflictException,
        RepositoryNotFoundException,
        AuthorizationException,
        ShuttingDownException,
        RepositoryExistsException,
    ]
}


def to_exception(response: Response) -> CentralDogmaException:
    if not response.text:
        return _to_status_exception(response.status_code, "")

    try:
        body = response.json()
    except JSONDecodeError:
        return InvalidResponseException(response.text)

    exception = body.get("exception")
    message = body.get("message") or response.text
    if exception:
        exception_type = _EXCEPTION_FACTORIES.get(exception)
        if exception_type:
            return exception_type(message)

    return _to_status_exception(response.status_code, message)


def _to_status_exception(status: int, message: str) -> CentralDogmaException:
    if status == HTTPStatus.UNAUTHORIZED:
        return UnauthorizedException(message)
    elif status == HTTPStatus.BAD_REQUEST:
        return BadRequestException(message)
    elif status == HTTPStatus.NOT_FOUND:
        return NotFoundException(message)
    else:
        return UnknownException(message)
