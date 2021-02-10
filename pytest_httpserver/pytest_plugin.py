import os
import warnings

import pytest
from .httpserver import HTTPServer


class Plugin:
    SERVER = None


class PluginHTTPServer(HTTPServer):
    def start(self):
        super().start()
        Plugin.SERVER = self

    def stop(self):
        super().stop()
        Plugin.SERVER = None


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
def _httpserver(httpserver_listen_address):
    host, port = httpserver_listen_address
    if not host:
        host = HTTPServer.DEFAULT_LISTEN_HOST
    if not port:
        port = HTTPServer.DEFAULT_LISTEN_PORT

    server = HTTPServer(host=host, port=port)
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


def pytest_sessionfinish(session, exitstatus):  # pylint: disable=unused-argument
    if Plugin.SERVER is not None:
        Plugin.SERVER.clear()
        if Plugin.SERVER.is_running():
            Plugin.SERVER.stop()


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):  # pylint: disable=unused-argument
    if fixturedef.argname == 'httpserver_listen_address' and fixturedef.scope != 'session':
        warnings.warn("httpserver_listen_address fixture will be converted to session scope in version 1.0.0. "
                      "Details: https://pytest-httpserver.readthedocs.io/en/latest/upgrade.html",
                      DeprecationWarning)
        yield
    else:
        yield


@pytest.fixture
def httpserver(_httpserver):
    yield _httpserver
    _httpserver.clear()
