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


@dataclass
class Revision:
    def __init__(self, major):
        self.major = major

    @staticmethod
    def init() -> Revision:
        return _INIT

    @staticmethod
    def head() -> Revision:
        return _HEAD


_INIT = Revision(1)
_HEAD = Revision(-1)
