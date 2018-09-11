
import os
import pytest
from pytest_httpserver import HTTPServer

PORT_KEY = "PYTEST_HTTPSERVER_PORT"
HOST_KEY = "PYTEST_HTTPSERVER_HOST"


@pytest.mark.skipif(HOST_KEY not in os.environ,
                    reason="requires {} environment variable".format(HOST_KEY))
def test_host_changing_by_environment(httpserver: HTTPServer):
    assert httpserver.host == os.environ[HOST_KEY]


@pytest.mark.skipif(PORT_KEY not in os.environ,
                    reason="requires {} environment variable".format(PORT_KEY))
def test_port_changing_by_environment(httpserver: HTTPServer):
    assert httpserver.port == int(os.environ[PORT_KEY])
