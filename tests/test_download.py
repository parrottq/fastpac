import pytest

import fastpac.download as download
from fastpac.search import PackageInfo


def test_download_assemble_package_url():
    assert download.assemble_package_url(
            PackageInfo(**{'mirror': '', 'name': '', 'size': 0, "repo": "core", "filename": "package.tar"}), "https://a/") == "https://a/core/os/x86_64/package.tar"
    assert download.assemble_package_url(
            PackageInfo(**{'mirror': '', 'name': '', 'size': 0, "repo": "extra", "filename": "package.tar.gz"}), "https://b") == "https://b/extra/os/x86_64/package.tar.gz"
