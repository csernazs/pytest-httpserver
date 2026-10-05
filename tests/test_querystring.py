import pytest
import requests
from werkzeug.datastructures import MultiDict

from pytest_httpserver import HTTPServer


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
