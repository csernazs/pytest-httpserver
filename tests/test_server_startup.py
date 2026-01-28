from __future__ import annotations

import contextlib
import socket
import time

import pytest

from pytest_httpserver import HTTPServer


def test_server_ready_immediately_after_start():
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


def test_server_ready_under_load():
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

    def thread_target(self):
        time.sleep(0.5)  # Simulate slow initialization
        self._server_ready_event.set()
        assert self.server is not None
        self.server.serve_forever()


class NoReadyEventServer(HTTPServer):
    """A server subclass that never signals readiness."""

    def thread_target(self):
        assert self.server is not None
        self.server.serve_forever()


def test_slow_start_server_waits_for_ready():
    """Test that start() waits for slow thread_target implementations."""
    server = SlowStartServer(host="localhost", port=0)
    server.expect_request("/").respond_with_data("ok")

    start_time = time.time()
    server.start()
    elapsed = time.time() - start_time

    try:
        # Should have waited at least 0.5 seconds
        assert elapsed >= 0.5
        # Server should be ready
        sock = socket.create_connection((server.host, server.port), timeout=1)
        sock.close()
    finally:
        server.stop()


def test_new_event_created_for_each_start():
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


def test_warns_when_ready_event_not_set():
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
