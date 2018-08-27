"""
All functionality relating to searching package databases
"""
from io import BytesIO
import logging
from tarfile import TarError, open as tar_open
from typing import Iterable, Optional, NamedTuple

from requests import get, RequestException

from fastpac.database import Repo
from fastpac.util import aslist

log = logging.getLogger(__name__)


def gen_dbs(name, url):
    """
    Return a generator with different names the repo databases goes by
    """
    for db_name in [".db.tar.gz", ".files.tar.gz", ".db", ".files"]:
        yield url + name + db_name


def download_tar(url):
    # Why this small function?
    # Unit testing and future centralized downloader
    # TODO: Centralized downloading
    try:
        return tar_open(fileobj=BytesIO(get(url).content))
    except (TarError, RequestException) as e:
        log.info('Got error while downloading %r', url, exc_info=e)


def fetch_repo(repo_name, mirrors):
    """
    Download a repository database
    """
    for mirror in mirrors:
        db_directory = "/".join(e.strip("/") for e in [mirror, repo_name, "os/x86_64"]) + "/"
        for repo_url in gen_dbs(repo_name, db_directory):
            log.info("Downloading %r", repo_url)
            repo = download_tar(repo_url)
            if repo:
                return RepoMeta(name=repo_name, mirror=mirror, db=Repo(repo))


@aslist
def download_repos(repos, mirrors):
    """
    Download multiple repositories
    """
    for repo in repos:
        yield fetch_repo(repo, mirrors)


class RepoMeta(NamedTuple):
    name: str
    mirror: str
    db: Repo


class PackageInfo(NamedTuple):
    mirror: str
    repo: str
    name: str
    filename: str
    size: int


def find_package(name: str, repos: Iterable[RepoMeta], limit: int = -1) -> Optional[PackageInfo]:
    """
    Find a package filename and repo

    Arguments:
        name: package name
        repos: a list of repo data (or a generator that is indexable. See hybrid.HybridGenerator)
        limit: limit the number of repos to search
    """
    for repo in repos:
        if limit == 0:
            break

        if name in repo.db:
            info = PackageInfo(
                mirror=repo.mirror,
                repo=repo.name,
                name=name,
                filename=repo.db[name]["filename"],
                size=repo.db[name]["csize"]
            )
            return info
        limit -= 1
    return None
