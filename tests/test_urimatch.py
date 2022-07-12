import re

import requests

from pytest_httpserver import HTTPServer
from pytest_httpserver import URIPattern


class PrefixMatch(URIPattern):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def match(self, uri):
        return uri.startswith(self.prefix)


class PrefixMatchEq:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def __eq__(self, uri):
        return uri.startswith(self.prefix)


def test_uripattern_object(httpserver: HTTPServer):
    httpserver.expect_request(PrefixMatch("/foo")).respond_with_json({"foo": "bar"})
    assert requests.get(httpserver.url_for("/foo")).json() == {"foo": "bar"}
    assert requests.get(httpserver.url_for("/foobar")).json() == {"foo": "bar"}
    assert requests.get(httpserver.url_for("/foobaz")).json() == {"foo": "bar"}

    assert requests.get(httpserver.url_for("/barfoo")).status_code == 500

    assert len(httpserver.assertions) == 1


def test_regexp(httpserver: HTTPServer):
    httpserver.expect_request(re.compile(r"/foo/\d+/bar/")).respond_with_json({"foo": "bar"})
    assert requests.get(httpserver.url_for("/foo/123/bar/")).json() == {"foo": "bar"}
    assert requests.get(httpserver.url_for("/foo/9999/bar/")).json() == {"foo": "bar"}

    assert requests.get(httpserver.url_for("/foo/bar/")).status_code == 500

    assert len(httpserver.assertions) == 1


def test_object_with_eq(httpserver: HTTPServer):
    httpserver.expect_request(PrefixMatchEq("/foo")).respond_with_json({"foo": "bar"})  # type: ignore
    assert requests.get(httpserver.url_for("/foo")).json() == {"foo": "bar"}
    assert requests.get(httpserver.url_for("/foobar")).json() == {"foo": "bar"}
    assert requests.get(httpserver.url_for("/foobaz")).json() == {"foo": "bar"}

    assert requests.get(httpserver.url_for("/barfoo")).status_code == 500

    assert len(httpserver.assertions) == 1
