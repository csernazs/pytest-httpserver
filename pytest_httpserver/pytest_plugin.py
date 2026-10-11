from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from .httpserver import HTTPServer
from .httpserver import HTTPServerBase

if TYPE_CHECKING:
    from collections.abc import Generator
    from ssl import SSLContext

REPORT_SECTION_TITLE = "pytest-httpserver report"

SERVERS_STASH_KEY = pytest.StashKey[list[HTTPServerBase]]()


class Plugin:
    SERVER: PluginHTTPServer | None = None


class PluginHTTPServer(HTTPServer):
    def start(self) -> None:
        super().start()
        Plugin.SERVER = self

    def stop(self) -> None:
        super().stop()
        Plugin.SERVER = None


def register_server(request: pytest.FixtureRequest, server: HTTPServerBase) -> None:
    """
    Registers the server for the test currently being set up.

    Registered servers are inspected when the test fails: pending server-side
    assertions (such as the one added when the server received a request which
    was not matching any of the registered handlers) and the errors collected
    from the request handlers are attached to the test report to make the
    debugging of the failed test easier.

    The fixtures provided by this plugin call this method automatically but it
    can be also called from a custom fixture (with the ``request`` fixture as
    the first parameter) to get the same report behavior for other server
    objects, such as a :py:class:`pytest_httpserver.BlockingHTTPServer`.

    :param request: the ``request`` fixture (or a :py:class:`pytest.FixtureRequest` object)
    :param server: the server object to register
    """
    node = request.node
    servers = node.stash.get(SERVERS_STASH_KEY, None)
    if servers is None:
        servers = []
        node.stash[SERVERS_STASH_KEY] = servers
    if server not in servers:
        servers.append(server)


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
def make_httpserver(
    httpserver_listen_address: tuple[str | None, int | None],
    httpserver_ssl_context: SSLContext | None,
) -> Generator[HTTPServer, None, None]:
    host, port = httpserver_listen_address
    if not host:
        host = HTTPServer.DEFAULT_LISTEN_HOST
    if not port:
        port = HTTPServer.DEFAULT_LISTEN_PORT

    server = HTTPServer(host=host, port=port, ssl_context=httpserver_ssl_context)
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
def httpserver(make_httpserver: HTTPServer, request: pytest.FixtureRequest) -> HTTPServer:
    server = make_httpserver
    server.clear()
    register_server(request, server)
    return server


@pytest.fixture(scope="session")
def make_httpserver_ipv4(
    httpserver_ssl_context: SSLContext | None,
) -> Generator[HTTPServer, None, None]:
    server = HTTPServer(host="127.0.0.1", port=0, ssl_context=httpserver_ssl_context)
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


@pytest.fixture
def httpserver_ipv4(make_httpserver_ipv4: HTTPServer, request: pytest.FixtureRequest) -> HTTPServer:
    server = make_httpserver_ipv4
    server.clear()
    register_server(request, server)
    return server


@pytest.fixture(scope="session")
def make_httpserver_ipv6(
    httpserver_ssl_context: SSLContext | None,
) -> Generator[HTTPServer, None, None]:
    server = HTTPServer(host="::1", port=0, ssl_context=httpserver_ssl_context)
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


@pytest.fixture
def httpserver_ipv6(make_httpserver_ipv6: HTTPServer, request: pytest.FixtureRequest) -> HTTPServer:
    server = make_httpserver_ipv6
    server.clear()
    register_server(request, server)
    return server


def _format_server_findings(server: HTTPServerBase) -> list[str]:
    """
    Formats the pending (not yet raised) errors of the specified server.

    :param server: the server object
    :return: list of the report lines, empty list if there's nothing to report
    """

    lines: list[str] = []

    assertions = list(server.assertions)
    if assertions:
        lines.append("Pending server-side assertions:")
        lines.append("")
        for index, assertion in enumerate(assertions, start=1):
            lines.append("{}. {}".format(index, assertion))
            lines.append("")

    handler_errors = list(server.handler_errors)
    if handler_errors:
        lines.append("Errors raised by request handlers:")
        lines.append("")
        for index, error in enumerate(handler_errors, start=1):
            lines.append("{}. {!r}".format(index, error))
            lines.append("")

    return lines


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],  # noqa: ARG001
) -> Generator[None, object, object]:
    """
    Adds the pending server-side errors to the report of the failed test.

    When a test fails, there can be errors collected by the httpserver(s) used
    by the test which were not raised during the test run. This typically
    happens when the server receives a request which does not match any of the
    registered handlers (so the server has no clue how to serve it), and the
    test does not call :py:meth:`pytest_httpserver.HTTPServer.check` (or
    similar methods) to raise them.

    To make the debugging easier in these cases, the errors are attached to
    the report of the failed test (as a report section), as they may explain
    why the test failed.
    """
    report = yield
    if isinstance(report, pytest.TestReport) and report.failed:
        servers = item.stash.get(SERVERS_STASH_KEY, None)
        if servers:
            section_lines: list[str] = []
            for server in servers:
                server_lines = _format_server_findings(server)
                if server_lines:
                    section_lines.append("--- {}".format(server))
                    section_lines.extend(server_lines)
            if section_lines:
                section_lines.insert(
                    0, "Server-side errors collected by pytest-httpserver (not raised during the test):"
                )
                section_lines.append(
                    "Note: these errors were not raised because the test did not call the check "
                    "methods of the server (for example HTTPServer.check())."
                )
                report.sections.append((REPORT_SECTION_TITLE, "\n".join(section_lines)))
    return report
