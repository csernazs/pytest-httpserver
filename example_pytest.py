# Run this code as 'pytest example_pytest.py'

import pytest
import requests

from pytest_httpserver import HTTPServer


# specify where the server should bind to
# you can return 0 as the port, in this case it will bind to a free (ephemeral) TCP port
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


# specify httpserver fixture
def test_oneshot_and_permanent_happy_path1(httpserver: HTTPServer):
    # define some request handlers
    # more details in the documentation
    httpserver.expect_request("/permanent").respond_with_data("OK permanent")
    httpserver.expect_oneshot_request("/oneshot1").respond_with_data("OK oneshot1")
    httpserver.expect_oneshot_request("/oneshot2").respond_with_data("OK oneshot2")

    # query those handlers with a real HTTP client (requests in this example but could by anything)
    # the 'url_for' method  formats the final URL, so there's no need to wire-in any ports
    assert requests.get(httpserver.url_for("/permanent")).text == "OK permanent"
    assert requests.get(httpserver.url_for("/oneshot1")).text == "OK oneshot1"
    assert requests.get(httpserver.url_for("/oneshot2")).text == "OK oneshot2"
    assert requests.get(httpserver.url_for("/permanent")).text == "OK permanent"

    assert len(httpserver.oneshot_handlers) == 0
