import os

import pytest
from pytest_httpserver import HTTPServer


def get_httpserver_listen_address():
    listen_host = os.environ.get("PYTEST_HTTPSERVER_HOST")
    listen_port = os.environ.get("PYTEST_HTTPSERVER_PORT")
    if listen_port:
        listen_port = int(listen_port)

    return listen_host, listen_port


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return get_httpserver_listen_address()


@pytest.fixture(scope="session")
def _httpserver(httpserver_listen_address):
    host, port = httpserver_listen_address
    if not host:
        host = HTTPServer.DEFAULT_LISTEN_HOST
    if not port:
        port = HTTPServer.DEFAULT_LISTEN_PORT

    server = HTTPServer(host=host, port=port)
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


@pytest.fixture
def httpserver(_httpserver):
    yield _httpserver
    _httpserver.clear()
