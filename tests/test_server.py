
import requests
import pytest
import coverage


from pytest_httpserver.httpserver import Server
from werkzeug.wrappers import Response

JSON_STRING = '{"foo": "bar"}'


def test_expected_request_json(server: Server):
    server.expect_request("/foobar").respond_with_json({"foo": "bar"})
    assert requests.get(server.url_for("/foobar")).json() == {'foo': 'bar'}


def test_expected_request_data(server: Server):
    server.expect_request("/foobar").respond_with_data(JSON_STRING)
    assert requests.get(server.url_for("/foobar")).json() == {'foo': 'bar'}


def test_expected_request_handler(server: Server):
    server.expect_request("/foobar").respond_with_handler(lambda request: JSON_STRING)
    assert requests.get(server.url_for("/foobar")).json() == {'foo': 'bar'}


def test_expected_request_response(server: Server):
    server.expect_request("/foobar").respond_with_response(Response(JSON_STRING))
    assert requests.get(server.url_for("/foobar")).json() == {'foo': 'bar'}


def test_expected_request_response_as_string(server: Server):
    server.expect_request("/foobar").respond_with_response(JSON_STRING)
    assert requests.get(server.url_for("/foobar")).json() == {'foo': 'bar'}


def test_request_post(server: Server):
    server.expect_request("/foobar", data='{"request": "example"}', method="POST").respond_with_data("example_response")
    response = requests.post(server.url_for("/foobar"), json={"request": "example"})
    print(server.log[0])
    server.check_assertions()
    assert response.text == "example_response"
    assert response.status_code == 200


def test_unexpected_request(server: Server):
    server.expect_request("/foobar").respond_with_json({"foo": "bar"})
    requests.get(server.url_for("/nonexists"))
    with pytest.raises(AssertionError):
        server.check_assertions()
