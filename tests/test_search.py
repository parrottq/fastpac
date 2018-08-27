import pytest

import fastpac.search as search
from fastpac.search import RepoMeta, PackageInfo
from fastpac.database import Repo

# Tests should not sent requests
@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


def test_search_fetch_repo(monkeypatch):
    input_var = ""
    output_var = b""
    def mockdownload(url):
        assert url == input_var
        return output_var

    monkeypatch.setattr(search, "download_tar", mockdownload)

    input_var = "https://test/core/os/x86_64/core.db.tar.gz"
    output_var = {"package": {"filename": "package1.tar"}}
    result = search.fetch_repo("core", ["https://test"])
    assert result.name == "core"
    assert result.mirror == "https://test"
    assert result.db == Repo(output_var)


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


def test_search_gen_dbs():
    gen = search.gen_dbs("core", "https://a.com/")

    # Compressed first
    assert next(gen) == "https://a.com/core.db.tar.gz"
    assert next(gen) == "https://a.com/core.files.tar.gz"

    # Uncompressed
    assert next(gen) == "https://a.com/core.db"
    assert next(gen) == "https://a.com/core.files"
