import requests
from pytest import approx, raises

from pytest_httpserver import HTTPServer


def test_querystring_str(httpserver: HTTPServer):
    httpserver.expect_request("/foobar", query_string="foo=bar", method="GET").respond_with_data(
        "example_response"
    )
    response = requests.get(httpserver.url_for("/foobar?foo=bar"))
    httpserver.check_assertions()
    assert response.text == "example_response"
    assert response.status_code == 200

def test_querystring_bytes(httpserver: HTTPServer):
    httpserver.expect_request("/foobar", query_string=b"foo=bar", method="GET").respond_with_data(
        "example_response"
    )
    response = requests.get(httpserver.url_for("/foobar?foo=bar"))
    httpserver.check_assertions()
    assert response.text == "example_response"
    assert response.status_code == 200
