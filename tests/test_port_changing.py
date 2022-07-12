import os

import pytest

from pytest_httpserver import HTTPServer
from pytest_httpserver.pytest_plugin import get_httpserver_listen_address

PORT_KEY = "PYTEST_HTTPSERVER_PORT"
HOST_KEY = "PYTEST_HTTPSERVER_HOST"


@pytest.fixture
def tmpenv():
    old_vars = {}
    for key in (HOST_KEY, PORT_KEY):
        old_vars[key] = os.environ.get(key)

    os.environ[HOST_KEY] = "5.5.5.5"
    os.environ[PORT_KEY] = "12345"

    yield

    for key, value in old_vars.items():
        if value:
            os.environ[key] = value
        else:
            del os.environ[key]


@pytest.mark.skipif(HOST_KEY not in os.environ, reason="requires {} environment variable".format(HOST_KEY))
def test_host_changing_by_environment(httpserver: HTTPServer):
    assert httpserver.host == os.environ[HOST_KEY]


@pytest.mark.skipif(PORT_KEY not in os.environ, reason="requires {} environment variable".format(PORT_KEY))
def test_port_changing_by_environment(httpserver: HTTPServer):
    assert httpserver.port == int(os.environ[PORT_KEY])


def test_get_httpserver_listen_address_with_env(tmpenv):
    address = get_httpserver_listen_address()
    assert address[0] == "5.5.5.5"
    assert address[1] == 12345
