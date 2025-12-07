# Copyright 2025 LINE Corporation
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

import os
import subprocess
import sys
from glob import glob
from pathlib import Path

import unasync


def cleanup(source_dir: Path, output_dir: Path, patterns: list[str]):
    for file in glob("*.py", root_dir=source_dir):
        path = output_dir / file
        for pattern in patterns:
            subprocess.check_call(["sed", "-i.bak", pattern, str(path)])
        subprocess.check_call(["rm", f"{path}.bak"])


def run(
    rule: unasync.Rule,
    cleanup_patterns: list[str] = [],
    check: bool = False,
):
    root_dir = Path(__file__).absolute().parent.parent
    source_dir = root_dir / rule.fromdir.lstrip("/")
    output_dir = check_dir = root_dir / rule.todir.lstrip("/")
    if check:
        rule.todir += "_sync_check/"
        output_dir = root_dir / rule.todir.lstrip("/")

    filepaths = []
    for root, _, filenames in os.walk(source_dir):
        for filename in filenames:
            if filename.rpartition(".")[-1] in {
                "py",
                "pyi",
            } and not filename.startswith("utils.py"):
                filepaths.append(os.path.join(root, filename))

    unasync.unasync_files(filepaths, [rule])

    if cleanup_patterns:
        cleanup(source_dir, output_dir, cleanup_patterns)

    if check:
        subprocess.check_call(["black", output_dir])
        # Make sure there are no differences between _sync and _sync_check
        for file in glob(f"{output_dir}/*.py"):
            file_name = file.split("/")[-1]
            subprocess.check_call(
                [
                    "diff",
                    f"{check_dir}/{file_name}",
                    f"{output_dir}/{file_name}",
                ]
            )
        subprocess.check_call(["rm", "-rf", output_dir])


def main(check: bool = False):
    run(
        rule=unasync.Rule(
            fromdir="/centraldogma/_async/",
            todir="/centraldogma/_sync/",
            additional_replacements={
                "AsyncClient": "Client",
                "AsyncDogma": "Dogma",
                "AsyncRetrying": "Retrying",
                "__aenter__": "__enter__",
                "__aexit__": "__exit__",
                "aclose": "close",
            },
        ),
        check=check,
    )


if __name__ == "__main__":
    main(check="--check" in sys.argv)
