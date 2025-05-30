from pathlib import Path
import urllib
import subprocess as sp
import urllib.parse
from lgmproxies.logs import logger
from lgmproxies.config import get_datapath
from lgmproxies.datasets.datamanager import register_dataset, require_dataset, download


def get_repo_path(repo_url: str) -> Path:
    """
    Parses the repository URL and returns the local path where it should be stored.
    """
    # https://github.com/jesstierney/BAYSPLINE -> jesstierney/BAYSPLINE
    parsed = urllib.parse.urlparse(repo_url)
    if parsed.scheme in ("http", "https"):
        # e.g. https://github.com/jesstierney/BAYSPLINE
        repo_path = parsed.path.lstrip("/")
    elif "@" in repo_url and ":" in repo_url:
        # e.g. git@github.com:jesstierney/BAYSPLINE
        repo_path = repo_url.split(":", 1)[1]
    else:
        # fallback: treat as already in "user/repo" form
        repo_path = repo_url
    repo_path = Path(repo_path)
    return get_datapath(repo_path.parent / repo_path.stem)


def download_repository(repo_url: str, destination: str="", update: bool=False) -> None:
    """
    Downloads a Git repository to the specified destination.

    Args:
        repo_url (str): The URL of the Git repository to download.
        destination (str): The local path where the repository should be cloned.
    """
    if not repo_url.startswith("https://") and not repo_url.startswith("git@"):
        repo_url = f"git@github.com:{repo_url}.git"

    if not destination:
        destination = str(get_repo_path(repo_url))

    if Path(destination).exists():
        if update:
            logger.info(f"Updating repository at {destination}...")
            sp.run(["git", "-C", destination, "pull"], check=True)
        else:
            logger.info(f"Repository already exists at {destination}. Use 'update=True' to update it.")
        return

    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    sp.run(["git", "clone", repo_url, destination], check=True)


def download_repositories(repos: list=[], update: bool=False) -> None:
    """
    Downloads multiple Git repositories.

    Args:
        repos (list): A list of repository URLs to download.
        update (bool): If True, updates existing repositories instead of cloning them again.
    """
    for repo in repos:
        try:
            download_repository(repo, update=update)
        except sp.CalledProcessError as e:
            logger.error(f"Failed to download repository {repo}: {e}")


def main():
    """
    Main function to download all repositories.
    """
    import argparse
    from lgmproxies.datasets.tierney import TIERNEY_REPOS
    import lgmproxies.datasets.catalogue # register datasets into DATASET_REGISTER
    from lgmproxies.datasets.datamanager import (
        DATASET_REGISTER,
        expand_names,
        download_by_names)

    ALL_REPOS = TIERNEY_REPOS
    ALL_DATASETS = [r['name'] for r in DATASET_REGISTER['records']]

    parser = argparse.ArgumentParser(description="Download datasets.")
    parser.add_argument("--update", action="store_true", help="Update existing repositories instead of cloning them again.")
    parser.add_argument("--repos", nargs='*', default=ALL_REPOS, help="List of repositories to download. Defaults to all repositories: %(default)s")
    parser.add_argument("--datasets", nargs='*', default=ALL_DATASETS, help="List of repositories to download. Defaults to all repositories: %(default)s")
    parser.add_argument("--force", action="store_true", help="Force download of datasets even if they already exist.")
    args = parser.parse_args()

    download_repositories(args.repos, update=args.update)

    expanded_names = expand_names(args.datasets)
    download_by_names(expanded_names, force_download=args.force)

if __name__ == "__main__":
    main()