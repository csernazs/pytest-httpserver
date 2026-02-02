from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from .httpserver import ExtraOptions
from .httpserver import HTTPServer

if TYPE_CHECKING:
    from collections.abc import Generator
    from ssl import SSLContext


class Plugin:
    SERVER: PluginHTTPServer | None = None


class PluginHTTPServer(HTTPServer):
    def start(self) -> None:
        super().start()
        Plugin.SERVER = self

    def stop(self) -> None:
        super().stop()
        Plugin.SERVER = None


def get_httpserver_listen_address() -> tuple[str | None, int | None]:
    listen_host = os.environ.get("PYTEST_HTTPSERVER_HOST")
    listen_port_str = os.environ.get("PYTEST_HTTPSERVER_PORT")
    listen_port: int | None = int(listen_port_str) if listen_port_str else None

    return listen_host, listen_port


@pytest.fixture(scope="session")
def httpserver_listen_address() -> tuple[str | None, int | None]:
    return get_httpserver_listen_address()


@pytest.fixture(scope="session")
def httpserver_ssl_context() -> None:
    return None


@pytest.fixture(scope="session")
def httpserver_extra_options() -> ExtraOptions:
    return ExtraOptions()


@pytest.fixture(scope="session")
def make_httpserver(
    httpserver_listen_address: tuple[str | None, int | None],
    httpserver_ssl_context: SSLContext | None,
    httpserver_extra_options: ExtraOptions,
) -> Generator[HTTPServer, None, None]:
    host, port = httpserver_listen_address
    if not host:
        host = HTTPServer.DEFAULT_LISTEN_HOST
    if not port:
        port = HTTPServer.DEFAULT_LISTEN_PORT

    server = HTTPServer.with_extra_options(
        host=host,
        port=port,
        ssl_context=httpserver_ssl_context,
        extra_options=httpserver_extra_options,
    )
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    if Plugin.SERVER is not None:
        Plugin.SERVER.clear()
        if Plugin.SERVER.is_running():
            Plugin.SERVER.stop()


@pytest.fixture
def httpserver(make_httpserver: HTTPServer) -> HTTPServer:
    server = make_httpserver
    server.clear()
    return server


@pytest.fixture(scope="session")
def make_httpserver_ipv4(
    httpserver_ssl_context: SSLContext | None,
    httpserver_extra_options: ExtraOptions,
) -> Generator[HTTPServer, None, None]:
    server = HTTPServer.with_extra_options(
        host="127.0.0.1",
        port=0,
        ssl_context=httpserver_ssl_context,
        extra_options=httpserver_extra_options,
    )
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


@pytest.fixture
def httpserver_ipv4(make_httpserver_ipv4: HTTPServer) -> HTTPServer:
    server = make_httpserver_ipv4
    server.clear()
    return server


@pytest.fixture(scope="session")
def make_httpserver_ipv6(
    httpserver_ssl_context: SSLContext | None,
    httpserver_extra_options: ExtraOptions,
) -> Generator[HTTPServer, None, None]:
    server = HTTPServer.with_extra_options(
        host="::1",
        port=0,
        ssl_context=httpserver_ssl_context,
        extra_options=httpserver_extra_options,
    )
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


@pytest.fixture
def httpserver_ipv6(make_httpserver_ipv6: HTTPServer) -> HTTPServer:
    server = make_httpserver_ipv6
    server.clear()
    return server
