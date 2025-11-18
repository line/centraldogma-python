import os
import re
import subprocess
import sys
from pathlib import Path


def run_command(command, check=True):
    print(f"Executing: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, check=check)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.stdout.strip()


def main():
    release_version = os.getenv("RELEASE_VERSION")
    next_version = os.getenv("NEXT_VERSION")

    if not release_version or not next_version:
        print(
            "Error: RELEASE_VERSION and NEXT_VERSION environment variables must be set.",
            file=sys.stderr,
        )
        sys.exit(1)

    git_status = run_command(["git", "status", "--porcelain"])
    if git_status:
        print(f"Error: Git repository is not clean.\n{git_status}", file=sys.stderr)
        sys.exit(1)

    project_root = Path(__file__).parent.parent.parent
    version_file = project_root / "centraldogma" / "__init__.py"

    if not version_file.exists():
        print(f"Error: '{version_file}' not found.", file=sys.stderr)
        sys.exit(1)

    original_content = version_file.read_text()

    version_pattern = re.compile(r'^__version__\s*=\s*".*"', re.MULTILINE)

    print(f"Updating version to {release_version}")
    release_content = version_pattern.sub(
        f'__version__ = "{release_version}"', original_content
    )
    version_file.write_text(release_content)

    tag = f"centraldogma-python-{release_version}"

    run_command(["git", "add", str(version_file)])
    run_command(["git", "commit", "-m", f"Release {tag}"])
    run_command(["git", "tag", "-m", f"Release {tag}", tag])

    if next_version.lower() != "skip":
        print(f"Updating version to {next_version} for next development cycle")

        run_command(["git", "reset", "--hard", "HEAD^"])

        next_dev_content = version_pattern.sub(
            f'__version__ = "{next_version}.dev"', original_content
        )
        version_file.write_text(next_dev_content)

        run_command(["git", "add", str(version_file)])
        run_command(["git", "commit", "-m", f"Update the version to {next_version}"])

        print("Pushing next version commit to remote")
        current_branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        run_command(["git", "push", "origin", current_branch])
    else:
        print("Skipped pushing the commit for updating the next version")

    print("Pushing tag to remote")
    run_command(["git", "push", "origin", tag])

    print("\nRelease process completed successfully!")
    print(f"Tagged: {tag}")


if __name__ == "__main__":
    main()
