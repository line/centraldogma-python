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
from requests import Response


class Error(Exception):
    def __init__(self, response: Response):
        try:
            self.response = response.json()
            self.exception = self.response["exception"]
            self.message = self.response["message"]
        except:
            print("The response format is not expected")

    def __str__(self):
        return str(self.response)


class AuthorizationError(Error):
    pass


class BadRequestError(Error):
    pass


class NotFoundError(Error):
    pass


class UnknownError(Error):
    pass
