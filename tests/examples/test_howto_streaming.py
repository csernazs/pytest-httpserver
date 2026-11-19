from collections.abc import Iterator
from threading import Event

import requests
from werkzeug import Request
from werkzeug import Response

from pytest_httpserver import HTTPServer


def test_streaming_response(httpserver: HTTPServer) -> None:
    release = Event()
    finished = Event()

    def events() -> Iterator[bytes]:
        yield b"data: first\n\n"
        assert release.wait(5), "The client did not release the second event"
        yield b"data: [DONE]\n\n"
        finished.set()

    def handler(_request: Request) -> Response:
        return Response(events(), mimetype="text/event-stream")

    httpserver.expect_request("/events").respond_with_handler(handler)
    try:
        with requests.get(httpserver.url_for("/events"), stream=True, timeout=10) as response:
            response.raise_for_status()
            lines = response.iter_lines(chunk_size=1)
            assert next(lines) == b"data: first"
            assert next(lines) == b""
            assert not finished.is_set()
            release.set()
            assert list(lines) == [b"data: [DONE]", b""]
    finally:
        release.set()
    httpserver.check()
