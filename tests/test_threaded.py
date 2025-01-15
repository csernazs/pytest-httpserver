import http.client
import threading
import time
from collections.abc import Iterable

import pytest
from werkzeug import Request
from werkzeug import Response

from pytest_httpserver import HTTPServer


@pytest.fixture
def threaded() -> Iterable[HTTPServer]:
    server = HTTPServer(threaded=True)
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


def test_threaded(threaded: HTTPServer):
    sleep_time = 0.5

    def handler(_request: Request):
        # allow some time to the client to have multiple pending request
        # handlers running in parallel
        time.sleep(sleep_time)

        # send back thread id
        return Response(f"{threading.get_ident()}")

    threaded.expect_request("/foo").respond_with_handler(handler)

    number_of_connections = 5
    conns = [http.client.HTTPConnection(threaded.host, threaded.port) for _ in range(number_of_connections)]

    for conn in conns:
        conn.request("GET", "/foo", headers={"Host": threaded.host})

    thread_ids: list[int] = []
    for conn in conns:
        response = conn.getresponse()

        assert response.status == 200
        thread_ids.append(int(response.read()))

    for conn in conns:
        conn.close()

    assert len(thread_ids) == len(set(thread_ids)), "thread ids returned should be unique"
