import pytest

import fastpac.mirror as mirror
import requests
import json

# Make sure no requests are sent
@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


def test_is_mirror_https():
    assert mirror.is_mirror_https({'url': 'https://example.com'}) == True
    assert mirror.is_mirror_https({'url': 'http://example.com'}) == False

    # With protocol arg
    assert mirror.is_mirror_https({'protocol': 'https'}) == True
    assert mirror.is_mirror_https({'protocol': 'http'}) == False


def test_get_mirrorlist_online_return(monkeypatch):
    def mockrequests(url):
        assert url == "example.com"
        # If no protocol is given for that specific mirror check url
        return json.dumps({'urls': [{"url": "https://example.com"}]})

    monkeypatch.setattr(mirror, "get", mockrequests)
    assert list(mirror.get_mirrorlist_online("example.com")) == ["https://example.com"]


def test_get_mirrorlist_online_https_arg_true(monkeypatch):
    def mockrequest(url):
        return json.dumps(
            {'urls':
                [
                    {'url': "https://example1.com", 'protocol': 'https'},
                    {'url': "https://example2.com"},
                    {'url': "http://example3.com", 'protocol': 'http'},
                    {'url': "rsync://example4.com", 'protocol': 'rsync'}
                ]
            })
    monkeypatch.setattr(mirror, "get", mockrequest)
    assert list(mirror.get_mirrorlist_online("example.com", https=True, sort=None)) == ["https://example1.com", "https://example2.com"]


def test_get_mirrorlist_online_https_arg_false(monkeypatch):
    def mockrequest(url):
        return json.dumps(
            {'urls':
                [
                    {'url': "https://example1.com", 'protocol': 'https'},
                    {'url': "https://example2.com"},
                    {'url': "http://example3.com", 'protocol': 'http'},
                    {'url': "rsync://example4.com", 'protocol': 'rsync'}
                ]
            })
    monkeypatch.setattr(mirror, "get", mockrequest)
    assert list(mirror.get_mirrorlist_online("example.com", https=False, sort=None)) == [
        "https://example1.com", "https://example2.com", "http://example3.com"]


def test_get_mirrorlist_online_sort(monkeypatch):
    urls = json.dumps({'urls': [{'url': 'https://b', 'score': 2.0}, {'url': 'https://a', 'score': 1.0}, {'url': 'https://c', 'score': 3}]})
    def mockrequest(url):
        return urls

    monkeypatch.setattr(mirror, "get", mockrequest)
    assert list(mirror.get_mirrorlist_online("example.com", sort="score")) == ["https://a", "https://b", "https://c"]


def test_mirror_parse_mirrorlist():
    assert mirror.parse_mirrorlist(
            "\n# Random comment\nServer = http://wow/$repo/os/$arch\nServer = https://wow2/sub/sub/$repo/os/$arch"
            ) == ["http://wow/", "https://wow2/sub/sub/"]

def test_mirror_aslist():
    def mockgenerator(num):
        for e in range(num):
            yield e

    a = mirror.aslist(mockgenerator)

    assert a(3) == list(range(3))
    assert a(5) == list(range(5))
    assert a(0) == []
