import pytest
import requests

from pytest_httpserver import HTTPServer


@pytest.fixture
def httpserver1():
    host, port = ('localhost', 8001)
    if not host:
        host = HTTPServer.DEFAULT_LISTEN_HOST
    if not port:
        port = HTTPServer.DEFAULT_LISTEN_PORT

    server = HTTPServer(host=host, port=port)
    server.start()
    try:
        yield server
    finally:
        server.stop()


@pytest.fixture
def httpserver2():
    host, port = ('localhost', 9000)
    if not host:
        host = HTTPServer.DEFAULT_LISTEN_HOST
    if not port:
        port = HTTPServer.DEFAULT_LISTEN_PORT

    server = HTTPServer(host=host, port=port)
    server.start()
    try:
        yield server
    finally:
        server.stop()


def test_multi(httpserver1: HTTPServer, httpserver2: HTTPServer):
    assert ':8001/' in httpserver1.url_for("/foobar")
    assert ':9000/' in httpserver2.url_for("/foobar")

    httpserver1.expect_request("/foobar").respond_with_data("OK foobar 1")
    httpserver2.expect_request("/foobar").respond_with_data("OK foobar 2")

    assert "OK foobar 1" == requests.get(httpserver1.url_for("/foobar")).text
    assert "OK foobar 2" == requests.get(httpserver2.url_for("/foobar")).text
