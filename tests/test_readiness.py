from collections.abc import Generator
from typing import Any

import pytest
import requests

from pytest_httpserver.httpserver import HTTPServer
from pytest_httpserver.httpserver import HTTPServerError


@pytest.fixture
def httpserver() -> Generator[HTTPServer, None, None]:
    server = HTTPServer(startup_timeout=10)
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


def test_httpserver_readiness(httpserver: HTTPServer):
    assert httpserver.startup_timeout == 10
    httpserver.expect_request("/").respond_with_data("Hello, world!")
    resp = requests.get(httpserver.url_for("/"))
    assert resp.status_code == 200
    assert resp.text == "Hello, world!"


class RecordingHTTPServer(HTTPServer):
    """HTTPServer subclass that records wait_for_server_ready() calls."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.wait_for_ready_call_count = 0
        self.readiness_pending_before_wait: list[bool] = []
        self.readiness_pending_after_wait: list[bool] = []

    def wait_for_server_ready(self) -> None:
        self.wait_for_ready_call_count += 1
        self.readiness_pending_before_wait.append(self._readiness_check_pending)
        super().wait_for_server_ready()
        self.readiness_pending_after_wait.append(self._readiness_check_pending)


@pytest.fixture
def recording_server_with_timeout() -> Generator[RecordingHTTPServer]:
    with RecordingHTTPServer(startup_timeout=10) as server:
        yield server


@pytest.fixture
def recording_server_without_timeout() -> Generator[RecordingHTTPServer]:
    with RecordingHTTPServer() as server:
        yield server


def test_wait_for_server_ready_called_with_timeout(
    recording_server_with_timeout: RecordingHTTPServer,
) -> None:
    assert recording_server_with_timeout.wait_for_ready_call_count == 1
    assert recording_server_with_timeout.readiness_pending_before_wait == [True]
    assert recording_server_with_timeout.readiness_pending_after_wait == [False]


def test_wait_for_server_ready_called_without_timeout(
    recording_server_without_timeout: RecordingHTTPServer,
) -> None:
    assert recording_server_without_timeout.wait_for_ready_call_count == 1
    assert recording_server_without_timeout.readiness_pending_before_wait == [False]
    assert recording_server_without_timeout.readiness_pending_after_wait == [False]


def test_wait_for_server_ready_called_each_start_stop_cycle() -> None:
    server = RecordingHTTPServer(startup_timeout=5)
    try:
        for i in range(3):
            server.start()
            assert server.wait_for_ready_call_count == i + 1
            server.clear()
            server.stop()
    finally:
        if server.is_running():
            server.clear()
            server.stop()

    assert server.readiness_pending_before_wait == [True, True, True]
    assert server.readiness_pending_after_wait == [False, False, False]


def test_double_start_does_not_poison_readiness_flag() -> None:
    server = HTTPServer(startup_timeout=5)
    server.start()
    try:
        with pytest.raises(HTTPServerError, match="already running"):
            server.start()

        assert server._readiness_check_pending is False  # noqa: SLF001

        server.expect_request("/test").respond_with_data("normal response")
        resp = requests.get(server.url_for("/test"))
        assert resp.status_code == 200
        assert resp.text == "normal response"
    finally:
        server.clear()
        if server.is_running():
            server.stop()


class FailingReadinessServer(HTTPServer):
    """HTTPServer subclass whose readiness check always fails."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def wait_for_server_ready(self) -> None:
        raise HTTPServerError("Simulated readiness failure")


def test_readiness_failure_stops_server() -> None:
    server = FailingReadinessServer(startup_timeout=5)
    with pytest.raises(HTTPServerError, match="Simulated readiness failure"):
        server.start()

    assert not server.is_running()
