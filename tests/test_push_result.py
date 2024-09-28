#  Copyright 2022 LINE Corporation
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
from dateutil import parser

from centraldogma.data import PushResult


def test_decode_push_result_with_iso8601():
    push_result_with_millis = {
        "revision": 2,
        "pushedAt": "2021-10-28T15:33:35.123Z",
    }

    push_result: PushResult = PushResult.from_dict(push_result_with_millis)
    assert push_result.revision == 2
    assert push_result.pushed_at == parser.parse(push_result_with_millis["pushedAt"])

    push_result_without_millis = {
        "revision": 3,
        "pushedAt": "2021-10-28T15:33:35Z",
    }

    push_result: PushResult = PushResult.from_dict(push_result_without_millis)
    assert push_result.revision == 3
    assert push_result.pushed_at == parser.parse(push_result_without_millis["pushedAt"])

    push_result_with_date = {
        "revision": 3,
        "pushedAt": "2021-10-28",
    }
    push_result: PushResult = PushResult.from_dict(push_result_with_date)
    assert push_result.revision == 3
    assert push_result.pushed_at == parser.parse(push_result_with_date["pushedAt"])
