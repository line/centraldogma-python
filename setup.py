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
from setuptools import setup


def get_long_description():
    with open("README.md", "r") as f:
        return f.read()


def get_install_requires():
    install_requires = []
    with open("requirements.txt", "r") as f:
        for line in f:
            dependency = line.rstrip()
            if not dependency:
                break
            install_requires.append(dependency)
    return install_requires


setup(
    name="centraldogma-python",
    version="0.4.0",
    description="Python client library for Central Dogma",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/line/centraldogma-python",
    author="Central Dogma Team",
    author_email="dl_centraldogma@linecorp.com",
    license="Apache License 2.0",
    packages=["centraldogma", "centraldogma.data"],
    install_requires=get_install_requires(),
    python_requires=">=3.8",
    keywords="centraldogma",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
