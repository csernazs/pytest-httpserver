import os
import ssl
from os.path import join as pjoin

import pytest
import requests

from pytest_httpserver import HTTPServer

pytestmark = pytest.mark.ssl

test_dir = os.path.dirname(os.path.realpath(__file__))
assets_dir = pjoin(test_dir, "assets")


@pytest.fixture(scope="session")
def httpserver_ssl_context():
    protocol = None
    for name in ("PROTOCOL_TLS_SERVER", "PROTOCOL_TLS", "PROTOCOL_TLSv1_2"):
        if hasattr(ssl, name):
            protocol = getattr(ssl, name)
            break

    assert protocol is not None, "Unable to obtain TLS protocol"

    return ssl.SSLContext(protocol)


def test_ssl(httpserver: HTTPServer):
    server_crt = pjoin(assets_dir, "server.crt")
    server_key = pjoin(assets_dir, "server.key")
    root_ca = pjoin(assets_dir, "rootCA.crt")

    assert (
        httpserver.ssl_context is not None
    ), "SSLContext not set. The session was probably started with a test that did not define an SSLContext."

    httpserver.ssl_context.load_cert_chain(server_crt, server_key)
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})

    assert httpserver.is_running()

    assert httpserver.url_for("/").startswith("https://")

    # ensure we are using "localhost" and not "127.0.0.1" to pass cert verification
    url = f"https://localhost:{httpserver.port}/foobar"

    assert requests.get(url, verify=root_ca).json() == {"foo": "bar"}
