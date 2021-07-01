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
from centraldogma.dogma import Dogma

dogma = Dogma("https://dogma.yourdomain.com", "token")

# List projects
projects = dogma.list_projects()
print("List projects----------------------")
if len(projects) < 1:
    print("No content")
    exit()
for project in projects:
    print(project)

# List repos
project_name = projects[0].name
repos = dogma.list_repositories(project_name)
print("\nList repositories------------------")
if len(repos) < 1:
    print("No content")
    exit()
for repo in repos:
    print(repo)

# List files
repo_name = repos[0].name
files = dogma.list_files(project_name, repo_name)
print("\nList files-------------------------")
if len(files) < 1:
    print("No content")
    exit()
for file in files:
    print(file)

# Get files
repo_name = repos[0].name
files = dogma.get_files(project_name, repo_name)
print("\nGet files-------------------------")
if len(files) < 1:
    print("No content")
    exit()
for file in files:
    print(file)
