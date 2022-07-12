import os
import ssl
from os.path import join as pjoin

import pytest
import requests

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


def test_ssl(httpserver):
    server_crt = pjoin(assets_dir, "server.crt")
    server_key = pjoin(assets_dir, "server.key")
    root_ca = pjoin(assets_dir, "rootCA.crt")
    context = httpserver.ssl_context

    assert (
        context is not None
    ), "SSLContext not set. The session was probably started with a test that did not define an SSLContext."

    httpserver.ssl_context.load_cert_chain(server_crt, server_key)
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})

    assert httpserver.is_running()
    assert requests.get(httpserver.url_for("/foobar"), verify=root_ca).json() == {"foo": "bar"}
