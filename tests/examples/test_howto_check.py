import pytest
import requests

from pytest_httpserver import HTTPServer


@pytest.mark.xfail
def test_check_assertions(httpserver: HTTPServer):
    def handler(_):
        assert 1 == 2

    httpserver.expect_request("/foobar").respond_with_handler(handler)

    requests.get(httpserver.url_for("/foobar"))

    # this will raise AssertionError:
    httpserver.check()
