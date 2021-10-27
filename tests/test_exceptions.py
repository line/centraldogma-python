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
import json
from http import HTTPStatus
from typing import Any

import pytest

from centraldogma.exceptions import to_exception, ProjectExistsException, InvalidResponseException, \
    ProjectNotFoundException, QueryExecutionException, RedundantChangeException, RevisionNotFoundException, \
    EntryNotFoundException, ChangeConflictException, RepositoryNotFoundException, AuthorizationException, \
    ShuttingDownException, RepositoryExistsException, BadRequestException, UnauthorizedException, NotFoundException, \
    UnknownException


@pytest.mark.parametrize("exception,expected_type",
                         [("ProjectExistsException", ProjectExistsException),
                          ("ProjectNotFoundException", ProjectNotFoundException),
                          ("QueryExecutionException", QueryExecutionException),
                          ("RedundantChangeException", RedundantChangeException),
                          ("RevisionNotFoundException", RevisionNotFoundException),
                          ("EntryNotFoundException", EntryNotFoundException),
                          ("ChangeConflictException", ChangeConflictException),
                          ("RepositoryNotFoundException", RepositoryNotFoundException),
                          ("AuthorizationException", AuthorizationException),
                          ("ShuttingDownException", ShuttingDownException),
                          ("RepositoryExistsException", RepositoryExistsException)])
def test_repository_exists_exception(exception, expected_type):
    class MockResponse:
        def json(self) -> Any:
            return {
                "exception": f"com.linecorp.centraldogma.common.{exception}",
                "message": "foobar",
            }

    # noinspection PyTypeChecker
    exception = to_exception(MockResponse())
    assert isinstance(exception, expected_type)
    assert str(exception) == "foobar"


@pytest.mark.parametrize("status,expected_type", [(HTTPStatus.UNAUTHORIZED, UnauthorizedException),
                                                  (HTTPStatus.BAD_REQUEST, BadRequestException),
                                                  (HTTPStatus.NOT_FOUND, NotFoundException),
                                                  (HTTPStatus.GATEWAY_TIMEOUT, UnknownException)])
def test_http_status_exception(status, expected_type):
    class MockResponse:
        status_code = status

        def json(self) -> Any:
            return {
                "exception": "com.linecorp.centraldogma.common.unknown",
                "message": "foobar",
            }

    # noinspection PyTypeChecker
    exception = to_exception(MockResponse())
    assert isinstance(exception, expected_type)
    assert str(exception) == "foobar"


def test_invalid_response_exception():
    class MockResponse:
        def json(self) -> Any:
            return json.loads(self.text())

        def text(self):
            return '{"foo":'

    # noinspection PyTypeChecker
    exception: InvalidResponseException = to_exception(MockResponse())
    assert isinstance(exception, InvalidResponseException)
