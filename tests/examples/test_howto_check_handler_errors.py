import pytest
import requests

from pytest_httpserver import HTTPServer


def test_check_assertions_raises_handler_assertions(httpserver: HTTPServer):
    def handler(_):
        assert 1 == 2

    httpserver.expect_request("/foobar").respond_with_handler(handler)

    requests.get(httpserver.url_for("/foobar"))

    # if you leave this "with" statement out, check_assertions() will break
    # the test by re-raising the assertion error caused by the handler
    # pytest will pick this exception as it was happened in the main thread
    with pytest.raises(AssertionError):
        httpserver.check_assertions()

    httpserver.check_handler_errors()


def test_check_handler_errors_raises_handler_error(httpserver: HTTPServer):
    def handler(_):
        raise ValueError("should be propagated")

    httpserver.expect_request("/foobar").respond_with_handler(handler)

    requests.get(httpserver.url_for("/foobar"))

    httpserver.check_assertions()

    # if you leave this "with" statement out, check_handler_errors() will
    # break the test with the original exception
    with pytest.raises(ValueError):
        httpserver.check_handler_errors()
