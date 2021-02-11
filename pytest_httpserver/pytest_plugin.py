import os

import pytest
from .httpserver import HTTPServer


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
def httpserver_ssl_context():
    return None


@pytest.fixture(scope="session")
def make_httpserver(httpserver_listen_address, httpserver_ssl_context):
    host, port = httpserver_listen_address
    if not host:
        host = HTTPServer.DEFAULT_LISTEN_HOST
    if not port:
        port = HTTPServer.DEFAULT_LISTEN_PORT

    server = HTTPServer(host=host, port=port, ssl_context=httpserver_ssl_context)
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


@pytest.fixture
def httpserver(make_httpserver):
    server = make_httpserver
    yield server
    server.clear()
