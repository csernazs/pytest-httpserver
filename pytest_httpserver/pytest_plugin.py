

import os

import pytest
from .httpserver import HTTPServer, HTTPProxy


class Plugin:
    SERVER = None
    PROXY = None


class PluginHTTPServer(HTTPServer):
    def start(self):
        super().start()
        Plugin.SERVER = self

    def stop(self):
        super().stop()
        Plugin.SERVER = None


class PluginHTTPProxy(HTTPProxy):
    def start(self):
        super().start()
        Plugin.PROXY = self

    def stop(self):
        super().stop()
        Plugin.PROXY = None


def get_httpserver_listen_address():
    listen_host = os.environ.get("PYTEST_HTTPSERVER_HOST")
    listen_port = os.environ.get("PYTEST_HTTPSERVER_PORT")
    if listen_port:
        listen_port = int(listen_port)

    return (listen_host, listen_port)


@pytest.fixture
def httpserver_listen_address():
    return get_httpserver_listen_address()


@pytest.fixture
def httpserver(httpserver_listen_address):
    if Plugin.SERVER:
        Plugin.SERVER.clear()
        yield Plugin.SERVER
        return

    host, port = httpserver_listen_address
    if not host:
        host = HTTPServer.DEFAULT_LISTEN_HOST
    if not port:
        port = HTTPServer.DEFAULT_LISTEN_PORT

    server = PluginHTTPServer(host=host, port=port)
    server.start()
    yield server


@pytest.fixture
def httpproxy(httpserver_listen_address, tmp_path):
    if Plugin.PROXY:
        Plugin.PROXY.clear()
        yield Plugin.PROXY
        return

    host, port = httpserver_listen_address
    if not host:
        host = HTTPProxy.DEFAULT_LISTEN_HOST
    if not port:
        port = HTTPProxy.DEFAULT_LISTEN_PORT

    ca_dir = tmp_path.joinpath("httpproxy_ca")
    ca_dir.mkdir(exist_ok=True)
    server = PluginHTTPProxy(host=host, port=port, proxy_options={"ca_file_cache": str(ca_dir.joinpath("wsgiprox-ca.pem"))})
    server.start()
    yield server


def pytest_sessionfinish(session, exitstatus):  # pylint: disable=unused-argument
    for instance in (Plugin.SERVER, Plugin.PROXY):
        if instance is not None:
            instance.clear()
            if instance.is_running():
                instance.stop()
