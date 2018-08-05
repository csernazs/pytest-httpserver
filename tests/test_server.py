
import requests
import pytest
import coverage


from pytest_httpserver.httpserver import HTTPServer
from werkzeug.wrappers import Response

JSON_STRING = '{"foo": "bar"}'


def test_expected_request_json(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}


def test_expected_request_data(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_data(JSON_STRING)
    assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}


def test_expected_request_handler(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_handler(lambda request: JSON_STRING)
    assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}


def test_expected_request_response(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_response(Response(JSON_STRING))
    assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}


def test_expected_request_response_as_string(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_response(JSON_STRING)
    assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}


def test_request_post(httpserver: HTTPServer):
    httpserver.expect_request("/foobar", data='{"request": "example"}', method="POST").respond_with_data("example_response")
    response = requests.post(httpserver.url_for("/foobar"), json={"request": "example"})
    httpserver.check_assertions()
    assert response.text == "example_response"
    assert response.status_code == 200


def test_unexpected_request(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    requests.get(httpserver.url_for("/nonexists"))
    with pytest.raises(AssertionError):
        httpserver.check_assertions()


def test_server_cleared_for_each_test(httpserver: HTTPServer):
    assert httpserver.log == []
    assert httpserver.assertions == []
    assert httpserver.ordered_handlers == []
    assert httpserver.oneshot_handlers == []
    assert httpserver.handlers == []


def test_server_with_statement():
    with HTTPServer(port=4001):
        pass


def test_oneshot(httpserver: HTTPServer):
    httpserver.expect_oneshot_request("/foobar").respond_with_data("OK foobar")
    httpserver.expect_oneshot_request("/foobaz").respond_with_data("OK foobaz")

    assert len(httpserver.oneshot_handlers) == 2

    # first requests should pass
    response = requests.get(httpserver.url_for("/foobaz"))
    httpserver.check_assertions()
    assert response.status_code == 200
    assert response.text == "OK foobaz"

    response = requests.get(httpserver.url_for("/foobar"))
    httpserver.check_assertions()
    assert response.status_code == 200
    assert response.text == "OK foobar"

    assert len(httpserver.oneshot_handlers) == 0

    # second requests should fail due to 'oneshot' type
    assert requests.get(httpserver.url_for("/foobar")).status_code == 500
    assert requests.get(httpserver.url_for("/foobaz")).status_code == 500


def test_ordered_ok(httpserver: HTTPServer):
    httpserver.expect_oneshot_request("/foobar", ordered=True).respond_with_data("OK foobar")
    httpserver.expect_oneshot_request("/foobaz", ordered=True).respond_with_data("OK foobaz")

    assert len(httpserver.ordered_handlers) == 2

    # first requests should pass
    response = requests.get(httpserver.url_for("/foobar"))
    httpserver.check_assertions()
    assert response.status_code == 200
    assert response.text == "OK foobar"

    response = requests.get(httpserver.url_for("/foobaz"))
    httpserver.check_assertions()
    assert response.status_code == 200
    assert response.text == "OK foobaz"

    assert len(httpserver.ordered_handlers) == 0

    # second requests should fail due to 'oneshot' type
    assert requests.get(httpserver.url_for("/foobar")).status_code == 500
    assert requests.get(httpserver.url_for("/foobaz")).status_code == 500


def test_ordered_invalid_order(httpserver: HTTPServer):
    httpserver.expect_oneshot_request("/foobar", ordered=True).respond_with_data("OK foobar")
    httpserver.expect_oneshot_request("/foobaz", ordered=True).respond_with_data("OK foobaz")

    assert len(httpserver.ordered_handlers) == 2

    # these would not pass as the order is different
    response = requests.get(httpserver.url_for("/foobaz"))
    assert response.status_code == 500

    response = requests.get(httpserver.url_for("/foobar"))
    assert response.status_code == 500

    assert len(httpserver.ordered_handlers) == 0
