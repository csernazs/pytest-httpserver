import requests

from pytest_httpserver import HTTPServer


def test_wait_success(httpserver: HTTPServer):
    waiting_timeout = 0.1

    with httpserver.wait(stop_on_nohandler=False, timeout=waiting_timeout) as waiting:
        requests.get(httpserver.url_for("/foobar"))
        httpserver.expect_oneshot_request("/foobar").respond_with_data("OK foobar")
        requests.get(httpserver.url_for("/foobar"))
    assert waiting.result

    httpserver.expect_oneshot_request("/foobar").respond_with_data("OK foobar")
    httpserver.expect_oneshot_request("/foobaz").respond_with_data("OK foobaz")
    with httpserver.wait(timeout=waiting_timeout) as waiting:
        requests.get(httpserver.url_for("/foobar"))
        requests.get(httpserver.url_for("/foobaz"))
    assert waiting.result
