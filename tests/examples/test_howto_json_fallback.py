import re

import requests

from pytest_httpserver import HTTPServer


def test_json_fallback(httpserver: HTTPServer) -> None:
    httpserver.expect_request("/known").respond_with_json({"message": "found"})

    # Persistent handlers are checked in registration order: put this last.
    httpserver.expect_request(re.compile(".*")).respond_with_json({"error": "not found"}, status=404)

    known = requests.get(httpserver.url_for("/known"))
    assert known.status_code == 200
    assert known.json() == {"message": "found"}

    missing = requests.get(httpserver.url_for("/dynamic/missing"))
    assert missing.status_code == 404
    assert missing.json() == {"error": "not found"}
    assert missing.headers["Content-Type"] == "application/json"

    # The fallback is a matching handler, so these requests are not errors.
    httpserver.check_assertions()
