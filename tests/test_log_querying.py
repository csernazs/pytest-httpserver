import pytest
import requests

from pytest_httpserver import HTTPServer
from pytest_httpserver import RequestMatcher


def test_verify(httpserver: HTTPServer):
    httpserver.expect_request("/foo").respond_with_data("OK")
    httpserver.expect_request("/bar").respond_with_data("OKOK")

    assert list(httpserver.iter_matching_requests(httpserver.create_matcher("/foo"))) == []
    assert requests.get(httpserver.url_for("/foo")).text == "OK"
    assert requests.get(httpserver.url_for("/bar")).text == "OKOK"

    matching_log = list(httpserver.iter_matching_requests(httpserver.create_matcher("/foo")))
    assert len(matching_log) == 1

    request, response = matching_log[0]

    assert request.url == httpserver.url_for("/foo")
    assert response.get_data() == b"OK"

    assert httpserver.get_matching_requests_count(httpserver.create_matcher("/foo")) == 1
    httpserver.assert_request_made(httpserver.create_matcher("/foo"))
    httpserver.assert_request_made(httpserver.create_matcher("/no_match"), count=0)

    with pytest.raises(AssertionError):
        assert httpserver.assert_request_made(httpserver.create_matcher("/no_match"))

    with pytest.raises(AssertionError):
        assert httpserver.assert_request_made(httpserver.create_matcher("/foo"), count=2)


def test_verify_assert_msg(httpserver: HTTPServer):
    httpserver.no_handler_status_code = 404
    httpserver.expect_request("/foo", json={"foo": "bar"}, method="POST").respond_with_data("OK")
    assert requests.get(httpserver.url_for("/foo"), headers={"User-Agent": "requests"}).status_code == 404

    with pytest.raises(AssertionError) as err:
        httpserver.assert_request_made(RequestMatcher("/foo", json={"foo": "bar"}, method="POST"))

    expected_message = f"""Matching request found 0 times but expected 1 times.
Expected request: <RequestMatcher uri='/foo' method='POST' query_string=None headers={{}} data=None json={{'foo': 'bar'}}>
Found 1 similar request(s):
--- Similar Request Start
Path: /foo
Method: GET
Body: b''
Headers: Host: localhost:{httpserver.port}\r
User-Agent: requests\r
Accept-Encoding: gzip, deflate\r
Accept: */*\r
Connection: keep-alive\r
\r

Query String: ''
--- Similar Request End
"""  # noqa: E501
    assert str(err.value) == expected_message


def test_verify_assert_msg_no_similar_requests(httpserver: HTTPServer):
    httpserver.expect_request("/foo", json={"foo": "bar"}, method="POST").respond_with_data("OK")

    with pytest.raises(AssertionError) as err:
        httpserver.assert_request_made(RequestMatcher("/foo", json={"foo": "bar"}, method="POST"))

    expected_message = """Matching request found 0 times but expected 1 times.
Expected request: <RequestMatcher uri='/foo' method='POST' query_string=None headers={} data=None json={'foo': 'bar'}>
No similar requests found.
"""
    assert str(err.value) == expected_message
