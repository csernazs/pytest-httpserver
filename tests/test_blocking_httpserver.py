from contextlib import contextmanager
from copy import deepcopy
from multiprocessing.pool import ThreadPool
from urllib.parse import urlparse

import pytest
import requests

from pytest_httpserver import BlockingHTTPServer


@contextmanager
def when_a_request_is_being_sent_to_the_server(request):
    with ThreadPool(1) as pool:
        yield pool.apply_async(requests.request, kwds=request)


def then_the_server_gets_the_request(server, request):
    request = deepcopy(request)
    replace_url_with_uri(request)

    return server.assert_request(**request)


def replace_url_with_uri(request):
    request["uri"] = get_uri(request["url"])
    del request["url"]


def get_uri(url):
    url = urlparse(url)
    return "?".join(item for item in [url.path, url.query] if item)


def when_the_server_responds_to(client_connection, response):
    client_connection.respond_with_json(response)


def then_the_response_is_got_from(server_connection, response):
    assert server_connection.get(timeout=9).json() == response


@pytest.fixture
def httpserver():
    server = BlockingHTTPServer(timeout=1)
    server.start()

    yield server

    server.clear()
    if server.is_running():
        server.stop()


def test_behave_workflow(httpserver: BlockingHTTPServer):
    request = dict(
        method="GET",
        url=httpserver.url_for("/my/path"),
    )

    with when_a_request_is_being_sent_to_the_server(request) as server_connection:

        client_connection = then_the_server_gets_the_request(httpserver, request)

        response = {"foo": "bar"}

        when_the_server_responds_to(client_connection, response)

        then_the_response_is_got_from(server_connection, response)


def test_raises_assertion_error_when_request_does_not_match(httpserver: BlockingHTTPServer):
    request = dict(
        method="GET",
        url=httpserver.url_for("/my/path"),
    )

    with when_a_request_is_being_sent_to_the_server(request):

        with pytest.raises(AssertionError) as exc:
            httpserver.assert_request(uri="/not/my/path/")

        assert "/not/my/path/" in str(exc)
        assert "does not match" in str(exc)


def test_raises_assertion_error_when_request_was_not_sent(httpserver: BlockingHTTPServer):
    with pytest.raises(AssertionError) as exc:
        httpserver.assert_request(uri="/my/path/", timeout=1)

    assert "/my/path/" in str(exc)
    assert "timed out" in str(exc)


def test_ignores_when_request_is_not_asserted(httpserver: BlockingHTTPServer):
    request = dict(
        method="GET",
        url=httpserver.url_for("/my/path"),
    )

    with when_a_request_is_being_sent_to_the_server(request) as server_connection:

        assert server_connection.get(timeout=9).text == "No handler found for this request"


def test_raises_assertion_error_when_request_was_not_responded(httpserver: BlockingHTTPServer):
    request = dict(
        method="GET",
        url=httpserver.url_for("/my/path"),
    )

    with when_a_request_is_being_sent_to_the_server(request):

        then_the_server_gets_the_request(httpserver, request)

        httpserver.stop()  # waiting for timeout of waiting for the response

        with pytest.raises(AssertionError) as exc:
            httpserver.check_assertions()

        assert "/my/path" in str(exc)
        assert "no response" in str(exc).lower()
