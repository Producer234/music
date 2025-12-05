import asyncio
import shlex
import shutil
from typing import Tuple

try:
    from git import Repo
    from git.exc import GitCommandError, InvalidGitRepositoryError
except ImportError:
    Repo = None

import config
from ..logging import LOGGER


def install_req(cmd: str) -> Tuple[str, str, int, int]:
    """Install requirements asynchronously."""
    async def install_requirements():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return asyncio.get_event_loop().run_until_complete(install_requirements())


def git():
    """Safely initialize and update repo if Git is available."""
    # Skip entirely if Git or GitPython is not available
    if not shutil.which("git") or Repo is None:
        LOGGER(__name__).info("Git not found, skipping upstream updates.")
        return

    REPO_LINK = config.UPSTREAM_REPO
    if config.GIT_TOKEN:
        GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
        TEMP_REPO = REPO_LINK.split("https://")[1]
        UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
    else:
        UPSTREAM_REPO = REPO_LINK

    try:
        repo = Repo()
        LOGGER(__name__).info("Git Client Found [VPS DEPLOYER]")
    except GitCommandError:
        LOGGER(__name__).info("Invalid Git Command")
    except InvalidGitRepositoryError:
        # Initialize repo safely
        try:
            repo = Repo.init()
            origin = repo.remotes.origin if "origin" in repo.remotes else repo.create_remote("origin", UPSTREAM_REPO)
            origin.fetch()
            repo.create_head(config.UPSTREAM_BRANCH, origin.refs[config.UPSTREAM_BRANCH])
            repo.heads[config.UPSTREAM_BRANCH].set_tracking_branch(origin.refs[config.UPSTREAM_BRANCH])
            repo.heads[config.UPSTREAM_BRANCH].checkout(True)
            try:
                origin.fetch(config.UPSTREAM_BRANCH)
                origin.pull(config.UPSTREAM_BRANCH)
            except GitCommandError:
                repo.git.reset("--hard", "FETCH_HEAD")
            install_req("pip3 install --no-cache-dir -r requirements.txt")
            LOGGER(__name__).info("Fetching updates from upstream repository...")
        except Exception as e:
            LOGGER(__name__).warning(f"Failed to update repository: {e}")
