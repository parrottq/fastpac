import pytest

import fastpac.database as database
import requests
import tarfile
import io


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


def create_tar(args):
    """
    Create a tar file that simulates the structure of a repo.db in memory
    """
    tar = tarfile.TarFile(fileobj=io.BytesIO(), mode='w')
    for arg in args:

        # Create the desc file
        file_contents = ""
        for key, value in arg.items():
            file_contents += f"%{key.upper()}%\n{value}\n"
        #print("*" + file_contents)

        # Prepare the information about this file
        content_info = tarfile.TarInfo(name=arg["name"] + "/desc")
        content_info.size = len(file_contents)

        # Put desc entry into tar file
        tar.addfile(content_info, fileobj=io.BytesIO(file_contents.encode()))

    #[print(a.name) for a in tar.getmembers()]

    # This writes the contents to the buffer then returns it
    tar.close()
    return tar.fileobj.getvalue()

def test_database_repo_create_tar():
    # Create the tar object
    raw_tar = create_tar([
        {"name": "test1", "wow": "also"},
        {"name": "test2"}])
    tar = tarfile.TarFile(fileobj=io.BytesIO(raw_tar))

    repo = database.Repo(tar)
    assert list(repo) == ["test1", "test2"]


def test_database_repo_create_artificial():
    """
    Create the repo without the overhead of a tar file
    """
    repo = database.Repo({"test1": {"filename": "test1-1.0.0"}})

    assert list(repo) == ["test1"]
    assert repo["test1"] == {"filename": "test1-1.0.0"}


def test_database_repo_search():
    repo = database.Repo({"test1": "wow", "test2": "wow2"})

    assert "test1" in repo
    assert not "test3" in repo


def test_database_repo_equal():
    a = {"package": {"filename": "package.tar"}}

    assert database.Repo(a) == database.Repo(a)


def test_database_package_parse():
    """
    Parsing package/desc files
    """
    # Basic parsing
    assert database.package_desc2dict(b"""
    %FILENAME%
    package-1.0.0

    %NAME%
    package
    """) == {"package": {"filename": "package-1.0.0"}}

    # List items parsing
    assert database.package_desc2dict(b"""
    %NAME%
    package

    %MULTI%
    name1
    name2
    name3
    """) == {"package": {"multi": "name1\nname2\nname3"}}
