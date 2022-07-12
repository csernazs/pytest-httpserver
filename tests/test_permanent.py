import pytest
import requests
from werkzeug.wrappers import Response

from pytest_httpserver import HTTPServer

JSON_STRING = '{"foo": "bar"}'


def test_expected_request_json(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    assert requests.get(httpserver.url_for("/foobar")).json() == {"foo": "bar"}


def test_expected_request_data(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_data(JSON_STRING)
    assert requests.get(httpserver.url_for("/foobar")).json() == {"foo": "bar"}


def test_expected_request_handler(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_handler(lambda request: JSON_STRING)  # type: ignore
    assert requests.get(httpserver.url_for("/foobar")).json() == {"foo": "bar"}


def test_expected_request_response(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_response(Response(JSON_STRING))
    assert requests.get(httpserver.url_for("/foobar")).json() == {"foo": "bar"}


def test_expected_request_response_as_string(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_response(JSON_STRING)  # type: ignore
    assert requests.get(httpserver.url_for("/foobar")).json() == {"foo": "bar"}


def test_request_post(httpserver: HTTPServer):
    httpserver.expect_request("/foobar", data='{"request": "example"}', method="POST").respond_with_data(
        "example_response"
    )
    response = requests.post(httpserver.url_for("/foobar"), json={"request": "example"})
    httpserver.check_assertions()
    assert response.text == "example_response"
    assert response.status_code == 200


def test_request_post_case_insensitive_method(httpserver: HTTPServer):
    httpserver.expect_request("/foobar", data='{"request": "example"}', method="post").respond_with_data(
        "example_response"
    )
    response = requests.post(httpserver.url_for("/foobar"), json={"request": "example"})
    httpserver.check_assertions()
    assert response.text == "example_response"
    assert response.status_code == 200


def test_request_any_method(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_data("OK")
    response = requests.post(httpserver.url_for("/foobar"))
    assert response.text == "OK"
    assert response.status_code == 200

    response = requests.delete(httpserver.url_for("/foobar"))
    assert response.text == "OK"
    assert response.status_code == 200

    response = requests.put(httpserver.url_for("/foobar"))
    assert response.text == "OK"
    assert response.status_code == 200

    response = requests.patch(httpserver.url_for("/foobar"))
    assert response.text == "OK"
    assert response.status_code == 200

    response = requests.get(httpserver.url_for("/foobar"))
    assert response.text == "OK"
    assert response.status_code == 200


def test_unexpected_request(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    requests.get(httpserver.url_for("/nonexists"))
    with pytest.raises(AssertionError):
        httpserver.check_assertions()


def test_no_handler_status_code(httpserver: HTTPServer):
    httpserver.no_handler_status_code = 404
    assert requests.get(httpserver.url_for("/foobar")).status_code == 404


def test_server_cleared_for_each_test(httpserver: HTTPServer):
    assert httpserver.log == []
    assert httpserver.assertions == []
    assert httpserver.ordered_handlers == []
    assert httpserver.oneshot_handlers == []
    assert httpserver.handlers == []
