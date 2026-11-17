import pytest
import requests
from werkzeug.datastructures import MultiDict

from pytest_httpserver import HTTPServer
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


@pytest.mark.parametrize("query_string", [{"flag": ""}, MultiDict([("flag", ""), ("flag", "value")])])
def test_querystring_empty_value(httpserver: HTTPServer, query_string):
    httpserver.expect_request("/foobar", query_string=query_string).respond_with_data("example_response")
    response = requests.get(
        httpserver.url_for("/foobar"),
        params=query_string.items(multi=True) if isinstance(query_string, MultiDict) else query_string,
    )
    httpserver.check_assertions()
    assert response.status_code == 200
    assert response.text == "example_response"


def test_querystring_empty_value_does_not_match_missing(httpserver: HTTPServer):
    httpserver.expect_request("/foobar", query_string={}).respond_with_data("example_response")
    response = requests.get(httpserver.url_for("/foobar"), params={"flag": ""})
    assert response.status_code == 500
    with pytest.raises(AssertionError, match="No handler found"):
        httpserver.check_assertions()


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Blank query values must be included in the expected dictionary",
)
def test_querystring_dict_ignores_empty_value(httpserver: HTTPServer):
    httpserver.expect_request("/foobar", query_string={"foo": "123"}).respond_with_data("example_response")
    response = requests.get(httpserver.url_for("/foobar?flag=&foo=123"))
    httpserver.check_assertions()
    assert response.status_code == 200
    assert response.text == "example_response"


@pytest.mark.parametrize(
    ("query_string", "raw_query", "decoded"),
    [
        ({"foo": "bar%20baz"}, "foo=bar%20baz", "[('foo', 'bar baz')]"),
        ("foo=bar baz", "foo=bar%20baz", "[('foo', 'bar baz')]"),
        (b"q=a+b", "q=a%2Bb", "[('q', 'a+b')]"),
        (
            MultiDict([("q", "first"), ("q", "other"), ("empty", "")]),
            "q=first&q=second&empty",
            "[('q', 'first'), ('q', 'second'), ('empty', '')]",
        ),
        ({"näme": "other"}, "n%C3%A4me=J%C3%B6rg", "[('näme', 'Jörg')]"),
        ({"q": "other"}, "q=%FF", "[('q', '�')]"),
    ],
)
def test_no_handler_query_diagnostics(httpserver: HTTPServer, query_string, raw_query, decoded):
    httpserver.expect_request("/query", query_string=query_string).respond_with_data("OK")

    response = requests.get(httpserver.url_for("/query") + "?" + raw_query)
    assert response.status_code == 500
    with pytest.raises(AssertionError) as exc_info:
        httpserver.check_assertions()

    for detail in (f"Query string: {raw_query.encode()!r}", f"Decoded query parameters: {decoded}"):
        assert detail in str(exc_info.value)
        assert detail in response.text


def test_no_handler_without_query(httpserver: HTTPServer):
    httpserver.expect_request("/expected").respond_with_data("OK")
    response = requests.get(httpserver.url_for("/other"))
    assert response.status_code == 500
    with pytest.raises(AssertionError) as exc_info:
        httpserver.check_assertions()

    assert "No handler found" in str(exc_info.value)
    assert "Query string:" not in str(exc_info.value)
    assert "Decoded query parameters:" not in response.text


def test_query_diagnostics_do_not_repeat_custom_matcher(httpserver: HTTPServer):
    class CountingQueryMatcher(QueryMatcher):
        calls = 0

        def get_comparing_values(self, request_query_string):
            self.calls += 1
            return request_query_string, b"other"

    matcher = CountingQueryMatcher()
    httpserver.expect_request("/query", query_string=matcher).respond_with_data("OK")
    response = requests.get(httpserver.url_for("/query?q=value"))
    assert response.status_code == 500
    with pytest.raises(AssertionError, match="No handler found"):
        httpserver.check_assertions()
    assert matcher.calls == 1
