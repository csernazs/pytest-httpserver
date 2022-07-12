import pytest
import requests

from pytest_httpserver import HTTPServer


def _setup_oneshot(server: HTTPServer):
    server.expect_request("/permanent").respond_with_data("OK permanent")
    server.expect_oneshot_request("/oneshot1").respond_with_data("OK oneshot1")
    server.expect_oneshot_request("/oneshot2").respond_with_data("OK oneshot2")


def _setup_ordered(server: HTTPServer):
    server.expect_ordered_request("/ordered1").respond_with_data("OK ordered1")
    server.expect_ordered_request("/ordered2").respond_with_data("OK ordered2")


def _setup_all(server: HTTPServer):
    _setup_oneshot(server)
    _setup_ordered(server)


def test_oneshot_and_permanent_happy_path1(httpserver: HTTPServer):
    _setup_oneshot(httpserver)
    assert requests.get(httpserver.url_for("/permanent")).text == "OK permanent"
    assert requests.get(httpserver.url_for("/oneshot1")).text == "OK oneshot1"
    assert requests.get(httpserver.url_for("/oneshot2")).text == "OK oneshot2"
    assert requests.get(httpserver.url_for("/permanent")).text == "OK permanent"

    assert len(httpserver.oneshot_handlers) == 0


def test_oneshot_and_permanent_happy_path2(httpserver: HTTPServer):
    _setup_oneshot(httpserver)
    assert requests.get(httpserver.url_for("/permanent")).text == "OK permanent"
    assert requests.get(httpserver.url_for("/oneshot2")).text == "OK oneshot2"
    assert requests.get(httpserver.url_for("/oneshot1")).text == "OK oneshot1"
    assert requests.get(httpserver.url_for("/permanent")).text == "OK permanent"

    assert len(httpserver.oneshot_handlers) == 0


def test_all_happy_path1(httpserver: HTTPServer):
    _setup_all(httpserver)

    # ordered must go first
    assert requests.get(httpserver.url_for("/ordered1")).text == "OK ordered1"
    assert requests.get(httpserver.url_for("/ordered2")).text == "OK ordered2"
    assert requests.get(httpserver.url_for("/permanent")).text == "OK permanent"
    assert requests.get(httpserver.url_for("/oneshot2")).text == "OK oneshot2"
    assert requests.get(httpserver.url_for("/oneshot1")).text == "OK oneshot1"
    assert requests.get(httpserver.url_for("/permanent")).text == "OK permanent"

    assert len(httpserver.oneshot_handlers) == 0
    assert len(httpserver.ordered_handlers) == 0


def test_all_ordered_missing(httpserver: HTTPServer):
    _setup_all(httpserver)

    # ordered is missing so everything must fail
    # a.k.a. permanently fail

    requests.get(httpserver.url_for("/permanent"))
    with pytest.raises(AssertionError):
        httpserver.check_assertions()

    requests.get(httpserver.url_for("/oneshot2"))
    with pytest.raises(AssertionError):
        httpserver.check_assertions()

    requests.get(httpserver.url_for("/oneshot1"))
    with pytest.raises(AssertionError):
        httpserver.check_assertions()

    requests.get(httpserver.url_for("/permanent"))
    with pytest.raises(AssertionError):
        httpserver.check_assertions()

    # handlers must be still intact but as the ordered are failed
    # everything will fail
    assert len(httpserver.ordered_handlers) == 2
    assert len(httpserver.oneshot_handlers) == 2
    assert len(httpserver.handlers) == 1
