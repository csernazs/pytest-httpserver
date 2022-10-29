from typing import Optional

import requests

from pytest_httpserver import HTTPServer


def case_insensitive_matcher(header_name: str, actual: Optional[str], expected: str) -> bool:
    if actual is None:
        return False

    if header_name == "X-Foo":
        return actual.lower() == expected.lower()
    else:
        return actual == expected


def test_case_insensitive_matching(httpserver: HTTPServer):
    httpserver.expect_request(
        "/", header_value_matcher=case_insensitive_matcher, headers={"X-Foo": "bar"}
    ).respond_with_data("OK")

    assert requests.get(httpserver.url_for("/"), headers={"X-Foo": "bar"}).status_code == 200
    assert requests.get(httpserver.url_for("/"), headers={"X-Foo": "BAR"}).status_code == 200
