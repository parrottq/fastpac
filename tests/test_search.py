import pytest

import fastpac.search as search
from fastpac.search import RepoMeta, PackageInfo
from fastpac.database import Repo

# Tests should not sent requests
@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")

# TODO: Test this with a generator
def test_search_find_package():
    # Repos data
    data = [
            RepoMeta(**{"name": "core", "mirror": "https://a", "db": Repo({"package": {"filename": "package.tar", "csize": "2"}})}),
            RepoMeta(**{"name": "core2", "mirror": "https://b", "db": Repo({"package2": {"filename": "package2.tar", "csize": "1"}})})
        ]

    assert search.find_package("package", data) == PackageInfo(**{
            "mirror": "https://a", "repo": "core", "filename": "package.tar", "name": "package", "size": "2"})

    assert search.find_package("package2", data) == PackageInfo(**{
            "mirror": "https://b", "repo": "core2", "filename": "package2.tar", "name": "package2", "size": "1"})

    assert search.find_package("package_does_not_exist", data) == None

def test_search_find_package_limit():
    data = [
            RepoMeta(**{"name": "core1", "mirror": "https://a", "db": Repo({"package1": {"filename": "package1.tar", "csize": "2"}})}),
            RepoMeta(**{"name": "core2", "mirror": "https://b", "db": Repo({"package2": {"filename": "package2.tar", "csize": "1"}})}),
            RepoMeta(**{"name": "core3", "mirror": "https://c", "db": Repo({"package3": {"filename": "package3.tar", "csize": "1"}})})
            ]

    assert search.find_package("package2", data, limit=1) == None
    assert search.find_package("package3", data, limit=2) == None

def test_search_repos_provider(monkeypatch):
    repo_gen = search.repos_provider(["https://a", "https://b"], ["core", "extra"])

    input_var = ""
    output_var = b""
    def mockdownload(url):
        assert url == input_var
        return output_var

    monkeypatch.setattr(search, "download_tar", mockdownload)

    input_var = "https://a/core/os/x86_64/core.db.tar.gz"
    output_var = {"package1": {"filename": "package1.tar"}}
    info_var = RepoMeta(**{"name": "core", "mirror": "https://a", "db": Repo({"package1": {"filename": "package1.tar"}})})
    new = next(repo_gen)
    assert new == info_var

    input_var = "https://a/extra/os/x86_64/extra.db.tar.gz"
    output_var = {"package2": {"filename": "package2.tar"}}
    info_var = RepoMeta(**{"name": "extra", "mirror": "https://a", "db": Repo({"package2": {"filename": "package2.tar"}})})
    new = next(repo_gen)
    assert new == info_var

    input_var = "https://b/core/os/x86_64/core.db.tar.gz"
    output_var = {"package3": {"filename": "package3.tar"}}
    info_var = RepoMeta(**{"name": "core", "mirror": "https://b", "db": Repo({"package3": {"filename": "package3.tar"}})})
    new = next(repo_gen)
    assert new == info_var

    input_var = "https://b/extra/os/x86_64/extra.db.tar.gz"
    output_var = {"package4": {"filename": "package4.tar"}}
    info_var = RepoMeta(**{"name": "extra", "mirror": "https://b", "db": Repo({"package4": {"filename": "package4.tar"}})})
    new = next(repo_gen)
    assert new == info_var

# Return types
# Repos
# Caching
# gen_dbs in search
# Failed download
def test_search_find_package_cache_access():
    """
    Access the cache to find some package info
    """
    engine = search.Search(["https://a", "https://b"], ["core"])
    # Add some info to cache
    engine.repo_cache = [
            {"name": "core", "mirror": "https://a", "db": Repo({"package": {"filename": "package-1.0.tar"}})},
            {"name": "core", "mirror": "https://b", "db": Repo({"package1": {"filename": "package1-1.0.tar"}})}
            ]

    # Package found in the first cache
    assert engine.find_package("package") == {
            "mirror": "https://a", "repo": "core", "filename": "package-1.0.tar", "name": "package"}
    # Package found in the second cache
    assert engine.find_package("package1") == {
            "mirror": "https://b", "repo": "core", "filename": "package1-1.0.tar", "name": "package1"}


def test_search_find_package_not_in_cache(monkeypatch):
    """
    The cache does not have our package, so we must download it
    """
    engine = search.Search(["https://b"], ["core"])
    # Add a repo to cache
    engine.repo_cache = [
            {"name": "core", "mirror": "https://a", "db": Repo({"package": {"filename": "package-1.0.tar"}})},
            ]

    # Mock download
    def mocktardownload(url):
        # TODO: Get url from function
        assert url == "https://b/core/os/x86_64/core.db.tar.gz"
        # This should return a tar but Repo accepts
        # either a tar file or a dict
        # see database.Repo.__init__
        return {"package1": {"filename": "package1-1.0.tar"}}
    monkeypatch.setattr(search, "download_tar", mocktardownload)

    # Test the downloading
    assert engine.find_package("package1") == {
            "mirror": "https://b", "repo": "core", "filename": "package1-1.0.tar", "name": "package1"}

    # Fetching the same package again should yield the same result but from cache
    assert engine.find_package("package1") == {
            "mirror": "https://b", "repo": "core", "filename": "package1-1.0.tar", "name": "package1"}

def test_search_find_package_limit_repos_fetch():
    """
    Limit the number of repos find_package check for the package
    """
    engine = search.Search([], ["core"])
    engine.repo_cache = [
            {"name": "core", "mirror": "https://a", "db": Repo({"package1": {"filename": "package-1"}})},
            {"name": "core", "mirror": "https://a", "db": Repo({"package2": {"filename": "package-2"}})},
            {"name": "core", "mirror": "https://a", "db": Repo({"package3": {"filename": "package-3"}})},
            ]

    assert engine.find_package("package2", max_repos=1) == None
    assert engine.find_package("package2", max_repos=2)["filename"] == "package-2"

    assert engine.find_package("package3", max_repos=2) == None
    assert engine.find_package("package3", max_repos=3)["filename"] == "package-3"

    # No arg test
    assert engine.find_package("package3")["filename"] == "package-3"


def test_search_gen_repos():
    mirrors = ["https://a.com/", "https://b.com"]
    repos = ["a", "b", "c"]
    gen = search.gen_repos(mirrors, repos)

    assert next(gen) == ["https://a.com/a/os/x86_64/", "a", "https://a.com"]
    assert next(gen) == ["https://a.com/b/os/x86_64/", "b", "https://a.com"]
    assert next(gen) == ["https://a.com/c/os/x86_64/", "c", "https://a.com"]
    assert next(gen) == ["https://b.com/a/os/x86_64/", "a", "https://b.com"]
    assert next(gen) == ["https://b.com/b/os/x86_64/", "b", "https://b.com"]
    assert next(gen) == ["https://b.com/c/os/x86_64/", "c", "https://b.com"]


def test_search_gen_dbs():
    gen = search.gen_dbs("core", "https://a.com/")

    # Compressed first
    assert next(gen) == "https://a.com/core.db.tar.gz"
    assert next(gen) == "https://a.com/core.files.tar.gz"

    # Uncompressed
    assert next(gen) == "https://a.com/core.db"
    assert next(gen) == "https://a.com/core.files"
