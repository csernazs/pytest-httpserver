
import requests
from pytest_httpserver import HTTPServer


def test_ordered_ok(httpserver: HTTPServer):
    httpserver.expect_ordered_request("/foobar").respond_with_data("OK foobar")
    httpserver.expect_ordered_request("/foobaz").respond_with_data("OK foobaz")

    assert len(httpserver.ordered_handlers) == 2

    # first requests should pass
    response = requests.get(httpserver.url_for("/foobar"))
    httpserver.check_assertions()
    assert response.status_code == 200
    assert response.text == "OK foobar"

    response = requests.get(httpserver.url_for("/foobaz"))
    httpserver.check_assertions()
    assert response.status_code == 200
    assert response.text == "OK foobaz"

    assert len(httpserver.ordered_handlers) == 0

    # second requests should fail due to 'oneshot' type
    assert requests.get(httpserver.url_for("/foobar")).status_code == 500
    assert requests.get(httpserver.url_for("/foobaz")).status_code == 500


def test_ordered_invalid_order(httpserver: HTTPServer):
    httpserver.expect_ordered_request("/foobar").respond_with_data("OK foobar")
    httpserver.expect_ordered_request("/foobaz").respond_with_data("OK foobaz")

    assert len(httpserver.ordered_handlers) == 2

    # these would not pass as the order is different
    # this mark the whole thing 'permanently failed' so no further requests must pass
    response = requests.get(httpserver.url_for("/foobaz"))
    assert response.status_code == 500

    response = requests.get(httpserver.url_for("/foobar"))
    assert response.status_code == 500

    # as no ordered handlers are triggered yet, these must be intact..
    assert len(httpserver.ordered_handlers) == 2
