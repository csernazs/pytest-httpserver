from __future__ import annotations

import contextlib
import socket
import time

import pytest
import requests
from requests.exceptions import Timeout

from pytest_httpserver import HTTPServer


def test_server_ready_immediately_after_start() -> None:
    """Test that the server accepts connections immediately after start() returns."""
    server = HTTPServer(host="localhost", port=0)
    server.expect_request("/").respond_with_data("ok")
    server.start()
    try:
        # Attempt to connect immediately - should not fail
        sock = socket.create_connection((server.host, server.port), timeout=1)
        sock.close()
    finally:
        server.stop()


def test_server_ready_under_load() -> None:
    """Test that the server is ready even when started multiple times in succession."""
    for _ in range(10):
        server = HTTPServer(host="localhost", port=0)
        server.expect_request("/").respond_with_data("ok")
        server.start()
        try:
            sock = socket.create_connection((server.host, server.port), timeout=1)
            sock.close()
        finally:
            server.stop()


class SlowStartServer(HTTPServer):
    """A server subclass that simulates slow startup."""

    def thread_target(self) -> None:
        time.sleep(0.5)  # Simulate slow initialization
        self._server_ready_event.set()
        assert self.server is not None
        self.server.serve_forever()


class NoReadyEventServer(HTTPServer):
    """A server subclass that never signals readiness."""

    def thread_target(self) -> None:
        assert self.server is not None
        self.server.serve_forever()


def test_slow_start_server_waits_for_ready() -> None:
    """Test that start() waits for slow thread_target implementations."""
    server = SlowStartServer(host="localhost", port=0)
    server.expect_request("/").respond_with_data("ok")

    start_time = time.monotonic()
    server.start()
    elapsed = time.monotonic() - start_time

    try:
        # Should have waited at least 0.5 seconds
        assert elapsed >= 0.5
        # Server should be ready
        sock = socket.create_connection((server.host, server.port), timeout=1)
        sock.close()
    finally:
        server.stop()


def test_new_event_created_for_each_start() -> None:
    """Test that a new event is created for each start() to isolate retries."""
    server = HTTPServer(host="localhost", port=0)
    server.expect_request("/").respond_with_data("ok")

    original_event = server._server_ready_event  # noqa: SLF001

    server.start()
    first_start_event = server._server_ready_event  # noqa: SLF001
    server.stop()

    server.start()
    second_start_event = server._server_ready_event  # noqa: SLF001
    server.stop()

    # Each start() should create a new event
    assert first_start_event is not original_event
    assert second_start_event is not first_start_event


def test_warns_when_ready_event_not_set() -> None:
    """Test that a warning is emitted when the ready event is never set."""
    server = NoReadyEventServer(host="localhost", port=0, startup_timeout=0.0)
    server.expect_request("/").respond_with_data("ok")

    with pytest.warns(UserWarning, match="ready event was not set"):
        server.start()

    try:
        deadline = time.time() + 1
        while time.time() < deadline:
            with contextlib.suppress(OSError):
                sock = socket.create_connection((server.host, server.port), timeout=0.1)
                sock.close()
                break
            time.sleep(0.01)
        else:
            raise AssertionError("Server did not accept connections within 1 second")
    finally:
        server.stop()


class SlowServeServer(HTTPServer):
    """A server that delays serve_forever() but does not set ready event early.

    This simulates the scenario where:
    - bind() and listen() complete (TCP connections queue in backlog)
    - But serve_forever() hasn't started yet (no HTTP responses)
    """

    def thread_target(self) -> None:
        assert self.server is not None
        # Delay before serve_forever - connections will queue but not be processed
        time.sleep(3.0)
        self._server_ready_event.set()
        self.server.serve_forever()


def test_http_request_fails_before_serve_forever_without_wait() -> None:
    """
    Demonstrate the race condition: TCP connects but HTTP times out.

    This test shows why waiting for server readiness matters:
    - After start(), TCP connections succeed (queued in backlog)
    - But HTTP requests timeout because serve_forever() hasn't started
    - With short client timeouts (common in production), this causes failures
    """
    # Use startup_timeout=0 to NOT wait for ready event (old behavior)
    server = SlowServeServer(host="localhost", port=0, startup_timeout=0.0)
    server.expect_request("/ping").respond_with_data("pong")

    with pytest.warns(UserWarning, match="ready event was not set"):
        server.start()

    try:
        # TCP connection succeeds (proves Zsolt's point about backlog)
        sock = socket.create_connection((server.host, server.port), timeout=1)
        sock.close()

        # But HTTP request with short timeout fails!
        # This is the actual problem in containerized environments
        with pytest.raises(Timeout):
            requests.get(server.url_for("/ping"), timeout=(0.5, 0.5))
    finally:
        server.stop()


def test_http_request_succeeds_when_waiting_for_ready() -> None:
    """
    Demonstrate that waiting for ready event fixes the race condition.

    With startup_timeout enabled (default), start() waits until
    serve_forever() begins, so HTTP requests succeed immediately.
    """
    # Use default startup_timeout to wait for ready event
    server = SlowServeServer(host="localhost", port=0)  # default startup_timeout=10.0
    server.expect_request("/ping").respond_with_data("pong")

    start_time = time.monotonic()
    server.start()
    elapsed = time.monotonic() - start_time

    try:
        # Should have waited for the slow startup
        assert elapsed >= 3.0, f"Expected to wait >= 3.0s, but only waited {elapsed}s"

        # HTTP request succeeds because serve_forever() has started
        response = requests.get(server.url_for("/ping"), timeout=(0.5, 0.5))
        assert response.status_code == 200
        assert response.text == "pong"
    finally:
        server.stop()
