import requests

from pytest_httpserver import HTTPServer


def test_expect_method(httpserver: HTTPServer):
    expected_response = "OK"
    matcher = httpserver.create_matcher(uri="/test", method="POST")
    httpserver.expect(matcher).respond_with_data(expected_response)
    resp = requests.post(httpserver.url_for("/test"), json={"list": [1, 2, 3, 4]})
    assert resp.text == expected_response
