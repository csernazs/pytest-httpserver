from contextlib import closing
from http.client import HTTPConnection
from threading import Event

import requests
from pytest import approx
from pytest import mark
from pytest import raises
from werkzeug import Request
from werkzeug import Response

from pytest_httpserver import HTTPServer


def test_wait_success(httpserver: HTTPServer):
    waiting_timeout = 0.1

    with httpserver.wait(stop_on_nohandler=False, timeout=waiting_timeout) as waiting:
        requests.get(httpserver.url_for("/foobar"))
        httpserver.expect_oneshot_request("/foobar").respond_with_data("OK foobar")
        requests.get(httpserver.url_for("/foobar"))
    assert waiting.result

    httpserver.expect_oneshot_request("/foobar").respond_with_data("OK foobar")
    httpserver.expect_oneshot_request("/foobaz").respond_with_data("OK foobaz")
    with httpserver.wait(timeout=waiting_timeout) as waiting:
        requests.get(httpserver.url_for("/foobar"))
        requests.get(httpserver.url_for("/foobaz"))
    assert waiting.result


def test_wait_unexpected_request(httpserver: HTTPServer):
    def make_unexpected_request_and_wait() -> None:
        with raises(AssertionError) as error:
            waiting_timeout = 0.1
            with httpserver.wait(raise_assertions=True, stop_on_nohandler=True, timeout=waiting_timeout) as waiting:
                requests.get(httpserver.url_for("/foobaz"))
            assert not waiting.result
        no_handler_text = "No handler found for request"
        assert no_handler_text in str(error.value)

    make_unexpected_request_and_wait()

    httpserver.expect_ordered_request("/foobar").respond_with_data("OK foobar")
    httpserver.expect_ordered_request("/foobaz").respond_with_data("OK foobaz")
    make_unexpected_request_and_wait()


def test_wait_timeout(httpserver: HTTPServer):
    httpserver.expect_oneshot_request("/foobar").respond_with_data("OK foobar")
    httpserver.expect_oneshot_request("/foobaz").respond_with_data("OK foobaz")
    waiting_timeout = 1
    with raises(AssertionError) as error:
        with httpserver.wait(raise_assertions=True, timeout=waiting_timeout) as waiting:
            requests.get(httpserver.url_for("/foobar"))
        assert not waiting.result
        waiting_time_error = 0.1
        assert waiting.elapsed_time == approx(waiting_timeout, abs=waiting_time_error)
    assert "Wait timeout occurred, but some handlers left" in str(error.value)


def test_wait_raise_assertion_false(httpserver: HTTPServer):
    waiting_timeout = 0.1

    try:
        with httpserver.wait(raise_assertions=False, stop_on_nohandler=True, timeout=waiting_timeout) as waiting:
            requests.get(httpserver.url_for("/foobaz"))
    except AssertionError as error:
        raise AssertionError("raise_assertions was set to False, but assertion was raised: {}".format(error))
    assert not waiting.result

    try:
        with httpserver.wait(raise_assertions=False, stop_on_nohandler=True, timeout=waiting_timeout) as waiting:
            pass
    except AssertionError as error:
        raise AssertionError("raise_assertions was set to False, but assertion was raised: {}".format(error))
    assert not waiting.result
    waiting_time_error = 0.1
    assert waiting.elapsed_time == approx(waiting_timeout, abs=waiting_time_error)


@mark.parametrize("ordered", [False, True])
def test_wait_does_not_finish_while_last_handler_is_running(httpserver: HTTPServer, *, ordered: bool):
    entered = Event()
    release = Event()

    def respond(_request: Request) -> Response:
        entered.set()
        assert release.wait(5)
        return Response("finished")

    handler = httpserver.expect_ordered_request("/") if ordered else httpserver.expect_oneshot_request("/")
    handler.respond_with_handler(respond)
    with closing(HTTPConnection(httpserver.host, httpserver.port, timeout=5)) as connection:
        try:
            with httpserver.wait(timeout=0.01, raise_assertions=False) as waiting:
                connection.request("GET", "/")
                assert entered.wait(5)
            assert not waiting.result
        finally:
            release.set()
            assert connection.getresponse().read() == b"finished"


@mark.parametrize("ordered", [False, True])
def test_wait_tracks_other_callbacks_after_handler_lists_are_empty(*, ordered: bool):
    entered = [Event(), Event()]
    release = [Event(), Event()]

    def respond(request: Request) -> Response:
        index = int(request.path[1:])
        entered[index].set()
        assert release[index].wait(5)
        return Response("finished")

    with HTTPServer(threaded=True) as server:
        for index in range(2):
            handler = (
                server.expect_ordered_request(f"/{index}") if ordered else server.expect_oneshot_request(f"/{index}")
            )
            handler.respond_with_handler(respond)

        with (
            closing(HTTPConnection(server.host, server.port, timeout=5)) as first,
            closing(HTTPConnection(server.host, server.port, timeout=5)) as second,
        ):
            try:
                with server.wait(timeout=0.01, raise_assertions=False) as waiting:
                    first.request("GET", "/0")
                    assert entered[0].wait(5)
                    second.request("GET", "/1")
                    assert entered[1].wait(5)
                    release[1].set()
                    assert second.getresponse().read() == b"finished"
                assert not waiting.result
            finally:
                release[0].set()
                release[1].set()
                assert first.getresponse().read() == b"finished"
