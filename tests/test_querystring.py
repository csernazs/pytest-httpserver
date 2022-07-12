import requests

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
