
import ssl
import os
from os.path import join as pjoin

import pytest
import requests
from werkzeug.wrappers import Response

from pytest_httpserver import HTTPServer

test_dir = os.path.dirname(os.path.realpath(__file__))
assets_dir = pjoin(test_dir, "assets")


def test_ssl():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_crt = pjoin(assets_dir, "server.crt")
    server_key = pjoin(assets_dir, "server.key")
    root_ca = pjoin(assets_dir, "rootCA.crt")
    context.load_cert_chain(server_crt, server_key)

    with HTTPServer(ssl_context=context, port=4433) as httpserver:
        httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
        assert httpserver.is_running()
        assert requests.get(httpserver.url_for("/foobar"), verify=root_ca).json() == {'foo': 'bar'}
