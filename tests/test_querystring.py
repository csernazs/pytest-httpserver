from __future__ import annotations

import typing
import urllib

import requests

if typing.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

from pytest_httpserver.httpserver import MappingQueryMatcher
from pytest_httpserver.httpserver import QueryMatcher


def test_querystring_str(httpserver: HTTPServer):
    httpserver.expect_request("/foobar", query_string="foo=bar", method="GET").respond_with_data("example_response")
    response = requests.get(httpserver.url_for("/foobar?foo=bar"))
    httpserver.check_assertions()
    assert response.text == "example_response"
    assert response.status_code == 200


def test_querystring_bytes(httpserver: HTTPServer):
    httpserver.expect_request("/foobar", query_string=b"foo=bar", method="GET").respond_with_data("example_response")
    response = requests.get(httpserver.url_for("/foobar?foo=bar"))
    httpserver.check_assertions()
    assert response.text == "example_response"
    assert response.status_code == 200


def test_querystring_dict(httpserver: HTTPServer):
    httpserver.expect_request("/foobar", query_string={"k1": "v1", "k2": "v2"}, method="GET").respond_with_data(
        "example_response"
    )
    response = requests.get(httpserver.url_for("/foobar?k1=v1&k2=v2"))
    httpserver.check_assertions()
    assert response.text == "example_response"
    assert response.status_code == 200

    response = requests.get(httpserver.url_for("/foobar?k2=v2&k1=v1"))
    httpserver.check_assertions()
    assert response.text == "example_response"
    assert response.status_code == 200


class MyQueryStringMatcher(QueryMatcher):
    def __init__(self, expected_string: str):
        parsed = urllib.parse.parse_qsl(expected_string)  # Parse query string into key-value pairs
        self._encoded_query_string = urllib.parse.urlencode(parsed, quote_via=urllib.parse.quote)

    def get_comparing_values(self, request_query_string: bytes) -> tuple:
        return (self._encoded_query_string, request_query_string.decode("utf-8"))


def test_query_string_with_spaces_string_fails(httpserver: HTTPServer):
    httpserver.expect_request("/test", query_string=MyQueryStringMatcher("foo=bar baz")).respond_with_data("OK")

    url = httpserver.url_for("/test") + "?foo=bar baz"
    requests.get(url)
    httpserver.check_assertions()


def test_query_string_is_encoded_string_passes(httpserver: HTTPServer):
    httpserver.expect_request("/test", query_string="foo=bar%20baz").respond_with_data("OK")

    url = httpserver.url_for("/test") + "?foo=bar baz"
    requests.get(url)
    httpserver.check_assertions()


def test_query_string_with_spaces_dict_passes(httpserver: HTTPServer):
    httpserver.expect_request("/test", query_string={"foo": "bar baz"}).respond_with_data("OK")

    url = httpserver.url_for("/test") + "?foo=bar baz"
    requests.get(url)
    httpserver.check_assertions()


class QuotedDictMatcher(MappingQueryMatcher):
    def __init__(self, query_dict: dict[str, str]):
        unquoted_dict = {k: urllib.parse.unquote(v) for k, v in query_dict.items()}
        super().__init__(unquoted_dict)


def test_query_string_is_encoded_dict_fails(httpserver: HTTPServer):
    httpserver.expect_request("/test", query_string=QuotedDictMatcher({"foo": "bar%20baz"})).respond_with_data("OK")

    url = httpserver.url_for("/test") + "?foo=bar baz"
    requests.get(url)
    httpserver.check_assertions()
