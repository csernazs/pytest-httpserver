import requests
from werkzeug import Request

from pytest_httpserver import HTTPServer
from pytest_httpserver import RequestMatcher


class MyMatcher(RequestMatcher):
    def match(self, request: Request) -> bool:
        match = super().match(request)
        if not match:  # existing parameters didn't match -> return with False
            return match

        # match the json's "value" key: if it is an integer and it is an even
        # number, it returns True
        json = request.json
        if isinstance(json, dict) and isinstance(json.get("value"), int):
            return json["value"] % 2 == 0

        return False


def test_custom_request_matcher(httpserver: HTTPServer):
    httpserver.expect(MyMatcher("/foo")).respond_with_data("OK")

    # with even number it matches the request
    resp = requests.post(httpserver.url_for("/foo"), json={"value": 42})
    resp.raise_for_status()
    assert resp.text == "OK"

    resp = requests.post(httpserver.url_for("/foo"), json={"value": 198})
    resp.raise_for_status()
    assert resp.text == "OK"

    # with an odd number, it does not match the request
    resp = requests.post(httpserver.url_for("/foo"), json={"value": 43})
    assert resp.status_code == 500
