import requests
from pytest import approx
from pytest import raises

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
