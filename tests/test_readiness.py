from collections.abc import Generator

import pytest
import requests

from pytest_httpserver.httpserver import HTTPServer


@pytest.fixture
def httpserver() -> Generator[HTTPServer, None, None]:
    server = HTTPServer(startup_timeout=10)
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


def test_httpserver_readiness(httpserver: HTTPServer):
    assert httpserver.startup_timeout == 10
    httpserver.expect_request("/").respond_with_data("Hello, world!")
    resp = requests.get(httpserver.url_for("/"))
    assert resp.status_code == 200
    assert resp.text == "Hello, world!"
