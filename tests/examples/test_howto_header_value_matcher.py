from typing import Optional

import requests

from pytest_httpserver import HeaderValueMatcher
from pytest_httpserver import HTTPServer


def case_insensitive_compare(actual: Optional[str], expected: str) -> bool:
    # actual is `None` if it is not specified
    if actual is None:
        return False
    return actual.lower() == expected.lower()


def test_own_matcher_object(httpserver: HTTPServer):
    matcher = HeaderValueMatcher({"X-Bar": case_insensitive_compare})

    httpserver.expect_request("/", headers={"X-Bar": "bar"}, header_value_matcher=matcher).respond_with_data("OK")

    assert requests.get(httpserver.url_for("/"), headers={"X-Bar": "bar"}).status_code == 200
    assert requests.get(httpserver.url_for("/"), headers={"X-Bar": "BAR"}).status_code == 200
