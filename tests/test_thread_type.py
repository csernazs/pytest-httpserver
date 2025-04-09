from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import requests
from werkzeug import Response

if TYPE_CHECKING:
    from werkzeug import Request

    from pytest_httpserver import HTTPServer


def test_server_thread_is_daemon(httpserver: HTTPServer):
    def handler(_request: Request):
        return Response(f"{threading.current_thread().daemon}")

    httpserver.expect_request("/foo").respond_with_handler(handler)

    assert requests.get(httpserver.url_for("/foo")).text == "True"
