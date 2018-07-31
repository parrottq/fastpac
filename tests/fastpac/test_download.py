import pytest

import fastpac.download as download


def test_download_assemble_package_url():
    assert download.assemble_package_url(
            {"repo": "core", "filename": "package.tar"}, "https://a/") == "https://a/core/os/x86_64/package.tar"
    assert download.assemble_package_url(
            {"repo": "extra", "filename": "package.tar.gz"}, "https://b") == "https://b/extra/os/x86_64/package.tar.gz"
