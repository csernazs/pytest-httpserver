import requests

from pytest_httpserver import HTTPServer


def test_json_matcher(httpserver: HTTPServer):
    httpserver.expect_request("/foo", json={"foo": "bar"}).respond_with_data("Hello world!")
    resp = requests.get(httpserver.url_for("/foo"), json={"foo": "bar"})
    assert resp.status_code == 200
    assert resp.text == "Hello world!"
