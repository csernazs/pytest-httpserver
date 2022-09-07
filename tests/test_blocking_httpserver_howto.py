import threading
from queue import Queue

import pytest
import requests

from pytest_httpserver import BlockingHTTPServer

# override httpserver fixture


@pytest.fixture
def httpserver():
    server = BlockingHTTPServer(timeout=1)
    server.start()

    yield server

    server.clear()
    if server.is_running():
        server.stop()

    # this is to check if the client has made any request where no
    # `assert_request` was called on it from the test

    server.check_assertions()
    server.clear()


def test_simplified(httpserver: BlockingHTTPServer):
    def client(response_queue: Queue):
        response = requests.get(httpserver.url_for("/foobar"), timeout=10)
        response_queue.put(response)

    # start the client, server is not yet configured
    # it will block until we add a request handler to the server
    # (see the timeout parameter of the http server)
    response_queue: Queue[requests.models.Response] = Queue(maxsize=1)
    thread = threading.Thread(target=client, args=(response_queue,))
    thread.start()

    try:
        # check that the request is for /foobar and it is a GET method
        # if this does not match, it will raise AssertionError and test will fail
        client_connection = httpserver.assert_request(uri="/foobar", method="GET")

        # with the received client_connection, we now need to send back the response
        # this makes the request.get() call in client() to return
        client_connection.respond_with_json({"foo": "bar"})

    finally:
        # wait for the client thread to complete
        thread.join(timeout=1)
        assert not thread.is_alive()  # check if join() has not timed out

    # check the response the client received
    response = response_queue.get(timeout=1)
    assert response.status_code == 200
    assert response.json() == {"foo": "bar"}
