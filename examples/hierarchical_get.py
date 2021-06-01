from centraldogma.api_client import ApiClient

client = ApiClient("https://dogma.yourdomain.com", "token")

# List projects
projects = client.list_projects()
print("List projects----------------------")
if len(projects) < 1:
    print("No content")
    exit()
for project in projects:
    print(project)

# List repos
project_name = projects[0].name
repos = client.list_repositories(project_name)
print("\nList repositories------------------")
if len(repos) < 1:
    print("No content")
    exit()
for repo in repos:
    print(repo)

# List files
repo_name = repos[0].name
files = client.list_files(project_name, repo_name)
print("\nList files-------------------------")
if len(files) < 1:
    print("No content")
    exit()
for file in files:
    print(file)

# Get files
repo_name = repos[0].name
files = client.get_files(project_name, repo_name)
print("\nGet files-------------------------")
if len(files) < 1:
    print("No content")
    exit()
for file in files:
    print(file)
