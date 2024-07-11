import requests

from pytest_httpserver import HTTPServer
from pytest_httpserver.hooks import Delay


def test_delay(httpserver: HTTPServer):
    # this adds 0.5 seconds delay to the server response
    httpserver.expect_request("/foo").with_post_hook(Delay(0.5)).respond_with_json({"example": "foo"})

    assert requests.get(httpserver.url_for("/foo")).json() == {"example": "foo"}
