from collections.abc import Generator

import pytest
import requests

from pytest_httpserver import HTTPServer

# By overriding make_httpserver fixture, you can override the object which is
# used by the httpserver fixture. You can put this to your conftest.py so in
# that case it will be used for all tests in the project, or you can put it to a
# test file if you want to use it only for that file.


@pytest.fixture(scope="session")
def make_httpserver() -> Generator[HTTPServer, None, None]:
    server = HTTPServer(startup_timeout=10)  # wait for 10 seconds for the server to be ready
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


def test_example(httpserver: HTTPServer):
    # the server is ready at this point, you can add request handlers and start sending requests
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})

    response = requests.get(httpserver.url_for("/foobar"))
    assert response.status_code == 200
    assert response.json() == {"foo": "bar"}
