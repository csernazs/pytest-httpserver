from itertools import cycle

import pytest
import requests
from werkzeug import Request
from werkzeug import Response

from pytest_httpserver import HTTPServer


def test_multiple_responses(httpserver: HTTPServer):
    httpserver.expect_request("/retry").respond_multiple(
        [
            Response("unavailable", status=503),
            Response("OK", headers={"X-Result": "success"}),
        ]
    )
    first = requests.get(httpserver.url_for("/retry"))
    second = requests.get(httpserver.url_for("/retry"))
    assert (first.status_code, first.text) == (503, "unavailable")
    assert (second.status_code, second.text) == (200, "OK")
    assert second.headers["X-Result"] == "success"
    httpserver.check()


@pytest.mark.parametrize("responses", [[], [Response("OK")]])
def test_exhausted_responses(httpserver: HTTPServer, responses):
    httpserver.expect_request("/").respond_multiple(responses)
    for _ in responses:
        assert requests.get(httpserver.url_for("/")).status_code == 200
    assert requests.get(httpserver.url_for("/")).status_code == 500
    with pytest.raises(AssertionError, match="No responses left for matching request: GET /"):
        httpserver.check()
    httpserver.check_handler_errors()


def test_lazy_generator_and_matching(httpserver: HTTPServer):
    consumed = []

    def responses():
        for text in ["first", "second"]:
            consumed.append(text)
            yield Response(text)

    httpserver.expect_request("/sequence").respond_multiple(responses())
    httpserver.expect_request("/other").respond_with_data("other")
    assert consumed == []
    requests.get(httpserver.url_for("/other"))
    assert consumed == []
    assert requests.get(httpserver.url_for("/sequence")).text == "first"
    assert consumed == ["first"]
    assert requests.get(httpserver.url_for("/sequence")).text == "second"
    httpserver.check()


def test_infinite_responses_and_post_hook(httpserver: HTTPServer):
    def hook(_request: Request, response: Response) -> Response:
        response.headers["X-Hook"] = "called"
        return response

    httpserver.expect_request("/").with_post_hook(hook).respond_multiple(cycle([Response("a"), Response("b")]))
    results = [requests.get(httpserver.url_for("/")) for _ in range(5)]
    assert [response.text for response in results] == ["a", "b", "a", "b", "a"]
    assert all(response.headers["X-Hook"] == "called" for response in results)
    httpserver.check()


def test_invalid_response(httpserver: HTTPServer):
    httpserver.expect_request("/").respond_multiple(iter([None]))  # type: ignore[arg-type]
    assert requests.get(httpserver.url_for("/")).status_code == 500
    with pytest.raises(TypeError, match="respond_multiple expects Werkzeug Response objects"):
        httpserver.check_handler_errors()


@pytest.mark.parametrize("method", ["expect_oneshot_request", "expect_ordered_request"])
def test_single_use_handlers(httpserver: HTTPServer, method):
    getattr(httpserver, method)("/").respond_multiple([Response("first"), Response("second")])
    httpserver.expect_request("/").respond_with_data("fallback")
    assert requests.get(httpserver.url_for("/")).text == "first"
    assert requests.get(httpserver.url_for("/")).text == "fallback"
    httpserver.check()
