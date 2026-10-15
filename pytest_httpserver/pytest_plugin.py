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


class _ServerRegistry:
    """
    Registry of the servers used by a test.

    It keeps track of the server findings (assertions and handler errors):

    * which findings were already attached to a test report, so a finding is
      never added to more than one report, even if the test fails in multiple
      phases (setup, call and teardown),

    * a snapshot of the findings taken when the fixtures of the test are torn
      down (see :py:meth:`snapshot`), so the findings collected during the
      teardown phase can be attached to the teardown report even if the
      server's state is cleared by another (for example session scoped)
      fixture finalizer before the report is made.
    """

    def __init__(self) -> None:
        self._servers: list[HTTPServerBase] = []
        self._reported_findings: list[object] = []
        self._snapshotted_findings: list[tuple[HTTPServerBase, str, object]] = []

    def register(self, server: HTTPServerBase) -> bool:
        """
        Registers the server.

        :param server: the server object
        :return: ``True`` if the server was not registered before, ``False`` otherwise
        """
        if server in self._servers:
            return False
        self._servers.append(server)
        return True

    def snapshot(self, server: HTTPServerBase) -> None:
        """
        Copies the not yet reported findings of the server to the registry.

        This is called from a finalizer of the fixture which registered the
        server, so the findings collected during the teardown phase of the test
        are copied before any other (typically session scoped) fixture
        finalizer clears the state of the server.

        :param server: the server object
        """
        for kind, finding in self._iter_findings(server):
            if not self._is_reported(finding):
                self._snapshotted_findings.append((server, kind, finding))

    def _is_reported(self, finding: object) -> bool:
        return any(finding is reported for reported in self._reported_findings)

    def _iter_findings(self, server: HTTPServerBase) -> Generator[tuple[str, object], None, None]:
        for assertion in server.assertions:
            yield ("assertion", assertion)
        for handler_error in server.handler_errors:
            yield ("error", handler_error)

    def collect_findings(self) -> list[str]:
        """
        Returns the report lines of the findings which were not reported yet.

        The returned findings are marked as reported so subsequent calls won't
        include them again.

        :return: list of the report lines, empty list if there's nothing to report
        """

        section_lines: list[str] = []

        for server in self._servers:
            server_lines: list[str] = []
            new_assertions: list[object] = []
            new_handler_errors: list[object] = []

            candidates: list[tuple[str, object]] = list(self._iter_findings(server))
            candidates.extend(
                (kind, finding)
                for snapshotted_server, kind, finding in self._snapshotted_findings
                if snapshotted_server is server
            )

            for kind, finding in candidates:
                if self._is_reported(finding):
                    continue
                if kind == "assertion":
                    new_assertions.append(finding)
                else:
                    new_handler_errors.append(finding)
                self._reported_findings.append(finding)

            if new_assertions:
                server_lines.append("Pending server-side assertions:")
                server_lines.append("")
                for index, assertion in enumerate(new_assertions, start=1):
                    server_lines.append("{}. {}".format(index, assertion))
                    server_lines.append("")

            if new_handler_errors:
                server_lines.append("Errors raised by request handlers:")
                server_lines.append("")
                for index, error in enumerate(new_handler_errors, start=1):
                    server_lines.append("{}. {!r}".format(index, error))
                    server_lines.append("")

            if server_lines:
                section_lines.append("--- {}".format(server))
                section_lines.extend(server_lines)

        return section_lines


SERVERS_STASH_KEY = pytest.StashKey[_ServerRegistry]()


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
    registry = node.stash.get(SERVERS_STASH_KEY, None)
    if registry is None:
        registry = _ServerRegistry()
        node.stash[SERVERS_STASH_KEY] = registry

    def snapshot() -> None:
        registry.snapshot(server)

    if registry.register(server):
        # copy the findings of the server before the state of the server is
        # cleared (which may happen in another fixture finalizer), so the
        # findings collected during the teardown phase of the test can be
        # attached to the report of the teardown phase
        request.addfinalizer(snapshot)


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


def _format_report_section(section_lines: list[str]) -> str:
    section_lines.insert(0, "Server-side errors collected by pytest-httpserver (not raised during the test):")
    section_lines.append(
        "Note: these errors were not raised because the test did not call the check "
        "methods of the server (for example HTTPServer.check())."
    )
    return "\n".join(section_lines)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],
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

    Each error is attached to one report only, so if the test fails in
    multiple phases (such as setup and teardown), the errors are not
    duplicated - errors collected after a failed phase are added to the
    report of the next failed phase.

    The registry of the servers is removed from the test item when the report
    of the teardown phase is made, so neither the servers nor their state
    (such as the log of the requests) outlives the test.
    """
    report = yield
    if isinstance(report, pytest.TestReport):
        registry = item.stash.get(SERVERS_STASH_KEY, None)
        if registry is not None:
            if report.failed:
                section_lines = registry.collect_findings()
                if section_lines:
                    report.sections.append((REPORT_SECTION_TITLE, _format_report_section(section_lines)))
            if call.when == "teardown":
                # this is the last report of the test, drop the registry to
                # not keep the server objects (and their state) alive
                del item.stash[SERVERS_STASH_KEY]
    return report
