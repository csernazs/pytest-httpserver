import pytest
import requests
import werkzeug

from pytest_httpserver import HTTPServer


def test_check_assertions_raises_handler_assertions(httpserver: HTTPServer):
    def handler(_):
        assert False  # noqa: PT015

    httpserver.expect_request("/foobar").respond_with_handler(handler)

    requests.get(httpserver.url_for("/foobar"))

    with pytest.raises(AssertionError):
        httpserver.check_assertions()

    httpserver.check_handler_errors()


def test_check_handler_errors_raises_handler_error(httpserver: HTTPServer):
    def handler(_) -> werkzeug.Response:
        raise ValueError("should be propagated")

    httpserver.expect_request("/foobar").respond_with_handler(handler)

    requests.get(httpserver.url_for("/foobar"))

    httpserver.check_assertions()

    with pytest.raises(ValueError):  # noqa: PT011
        httpserver.check_handler_errors()


def test_check_handler_errors_correct_order(httpserver: HTTPServer):
    def handler1(_) -> werkzeug.Response:
        raise ValueError("should be propagated")

    def handler2(_) -> werkzeug.Response:
        raise OSError("should be propagated")

    httpserver.expect_request("/foobar1").respond_with_handler(handler1)
    httpserver.expect_request("/foobar2").respond_with_handler(handler2)

    requests.get(httpserver.url_for("/foobar1"))
    requests.get(httpserver.url_for("/foobar2"))

    httpserver.check_assertions()

    with pytest.raises(ValueError):  # noqa: PT011
        httpserver.check_handler_errors()

    with pytest.raises(OSError):  # noqa: PT011
        httpserver.check_handler_errors()

    httpserver.check_handler_errors()


def test_missing_matcher_raises_exception(httpserver):
    requests.get(httpserver.url_for("/foobar"))

    # missing handlers should not raise handler exception here
    httpserver.check_handler_errors()

    with pytest.raises(AssertionError):
        httpserver.check_assertions()


def test_check_raises_errors_in_order(httpserver):
    def handler1(_):
        assert False  # noqa: PT015

    def handler2(_):
        pass  # does nothing

    def handler3(_):
        raise ValueError

    httpserver.expect_request("/foobar1").respond_with_handler(handler1)
    httpserver.expect_request("/foobar2").respond_with_handler(handler2)
    httpserver.expect_request("/foobar3").respond_with_handler(handler3)

    requests.get(httpserver.url_for("/foobar1"))
    requests.get(httpserver.url_for("/foobar2"))
    requests.get(httpserver.url_for("/foobar3"))

    with pytest.raises(AssertionError):
        httpserver.check()

    with pytest.raises(ValueError):  # noqa: PT011
        httpserver.check()


def test_with_check_success(httpserver: HTTPServer):
    httpserver.expect_ordered_request("/first").respond_with_data(status=204)
    httpserver.expect_ordered_request("/second").respond_with_data(status=204)

    with httpserver.with_check() as server:
        assert server is httpserver
        assert requests.get(server.url_for("/first")).status_code == 204
        assert requests.get(server.url_for("/second")).status_code == 204


def test_with_check_unexpected_request_after_expected_requests(httpserver: HTTPServer):
    httpserver.expect_ordered_request("/first").respond_with_data(status=204)
    httpserver.expect_ordered_request("/second").respond_with_data(status=204)

    with pytest.raises(AssertionError, match="No handler found for request"), httpserver.with_check():
        assert requests.get(httpserver.url_for("/first")).status_code == 204
        assert requests.get(httpserver.url_for("/second")).status_code == 204
        assert requests.get(httpserver.url_for("/unexpected")).status_code == 500


def test_with_check_propagates_handler_error(httpserver: HTTPServer):
    handler_error = ValueError("handler failed")

    def handler(_) -> werkzeug.Response:
        raise handler_error

    httpserver.expect_request("/error").respond_with_handler(handler)

    with pytest.raises(ValueError, match="handler failed") as error, httpserver.with_check():
        assert requests.get(httpserver.url_for("/error")).status_code == 500

    assert error.value is handler_error


def test_with_check_preserves_body_exception(httpserver: HTTPServer):
    body_error = RuntimeError("client failed")

    with pytest.raises(RuntimeError, match="client failed") as error, httpserver.with_check():
        assert requests.get(httpserver.url_for("/unexpected")).status_code == 500
        raise body_error

    assert error.value is body_error
