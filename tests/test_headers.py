import http.client
from collections import defaultdict

import pytest
import requests
from werkzeug.datastructures import Headers
from werkzeug.http import parse_dict_header

from pytest_httpserver import CaseInsensitiveHeaderValueMatcher
from pytest_httpserver import HTTPServer
from pytest_httpserver import RequestMatcher
from pytest_httpserver.httpserver import HeaderValueMatcher
from pytest_httpserver.httpserver import NoMethodFoundForMatchingHeaderValueError


def test_case_insensitive_header_matcher_fallback_does_not_cache_header_names():
    comparators = iter(
        [HeaderValueMatcher.default_header_value_matcher, lambda actual, expected: actual == expected.upper()]
    )
    matchers = defaultdict(lambda: next(comparators))
    matcher = CaseInsensitiveHeaderValueMatcher(matchers)

    assert matcher("x-custom", "value", "value")
    assert matcher("x-custom", "VALUE", "value")
    assert not matchers


@pytest.mark.parametrize("mapping_class", [dict, defaultdict])
def test_case_insensitive_header_matcher_without_default(mapping_class):
    matchers = mapping_class()
    matchers["x-custom"] = HeaderValueMatcher.default_header_value_matcher
    matcher = CaseInsensitiveHeaderValueMatcher(matchers)

    assert matcher("X-CUSTOM", "value", "value")
    assert not matcher("X-CUSTOM", "VALUE", "value")
    with pytest.raises(NoMethodFoundForMatchingHeaderValueError, match="X-Missing"):
        matcher("X-Missing", "value", "value")


def test_case_insensitive_header_matcher_copies_comparators():
    matchers = {"X-Custom": HeaderValueMatcher.default_header_value_matcher}
    first = CaseInsensitiveHeaderValueMatcher(matchers)
    matchers["X-Custom"] = lambda actual, expected: actual == expected.upper()
    second = CaseInsensitiveHeaderValueMatcher(matchers)

    assert first("X-CUSTOM", "value", "value")
    assert not first("X-CUSTOM", "VALUE", "value")
    assert second("x-custom", "VALUE", "value")
    assert not second("x-custom", "value", "value")


def test_case_insensitive_header_matcher_duplicate_names():
    matcher = CaseInsensitiveHeaderValueMatcher(
        {
            "X-Custom": HeaderValueMatcher.default_header_value_matcher,
            "x-CUSTOM": lambda actual, expected: actual == expected.upper(),
        }
    )

    assert matcher("x-custom", "VALUE", "value")
    assert not matcher("X-Custom", "value", "value")


def test_case_insensitive_header_matcher_independent_defaults(monkeypatch):
    legacy_matchers = {"X-Custom": lambda actual, expected: actual == expected.upper()}
    monkeypatch.setattr(HeaderValueMatcher, "DEFAULT_MATCHERS", legacy_matchers)
    customized = CaseInsensitiveHeaderValueMatcher(legacy_matchers)

    assert customized("x-custom", "VALUE", "value")
    for matcher in (CaseInsensitiveHeaderValueMatcher(), CaseInsensitiveHeaderValueMatcher()):
        assert matcher("x-custom", "value", "value")
        assert not matcher("x-custom", "VALUE", "value")
        assert not matcher("x-custom", None, "value")
        assert matcher("authorization", 'Digest a="1", b="2"', 'Digest b="2", a="1"')
        assert not matcher("AUTHORIZATION", None, 'Digest a="1"')

    assert list(legacy_matchers) == ["X-Custom"]
    default_matcher = RequestMatcher("/").header_value_matcher
    assert isinstance(default_matcher, HeaderValueMatcher)
    assert default_matcher.matchers is legacy_matchers


def test_legacy_header_matcher_preserves_case_sensitive_lookup():
    matcher = HeaderValueMatcher({"X-Custom": HeaderValueMatcher.default_header_value_matcher})

    assert matcher("X-Custom", "value", "value")
    with pytest.raises(NoMethodFoundForMatchingHeaderValueError, match="x-custom"):
        matcher("x-custom", "value", "value")


def test_legacy_header_matcher_preserves_defaultdict_lookup():
    matchers = defaultdict(lambda: HeaderValueMatcher.default_header_value_matcher)
    matcher = HeaderValueMatcher(matchers)

    assert matcher("x-custom", "value", "value")
    assert matchers["x-custom"] is HeaderValueMatcher.default_header_value_matcher
    matchers["X-Custom"] = lambda actual, expected: actual == expected.upper()
    assert not matcher("x-custom", "VALUE", "value")


def test_case_insensitive_header_matcher_bake_is_opt_in(httpserver: HTTPServer):
    matcher = CaseInsensitiveHeaderValueMatcher(
        {"x-CUSTOM": lambda actual, expected: actual is not None and actual.lower() == expected.lower()}
    )
    server = httpserver.bake(header_value_matcher=matcher)
    server.expect_request("/opt-in", headers={"X-Custom": "value"}).respond_with_data("OK")
    httpserver.expect_request("/default", headers={"X-Custom": "value"}).respond_with_data("OK")

    assert requests.get(server.url_for("/opt-in"), headers={"X-Custom": "VALUE"}).status_code == 200
    assert requests.get(httpserver.url_for("/default"), headers={"X-Custom": "VALUE"}).status_code == 500


@pytest.mark.parametrize(
    ("matcher_class", "comparator_name", "header_name"),
    [
        (HeaderValueMatcher, "Custom", "Custom"),
        (CaseInsensitiveHeaderValueMatcher, "Custom", "Custom"),
        (CaseInsensitiveHeaderValueMatcher, "CuStOm", "custom"),
        (CaseInsensitiveHeaderValueMatcher, "custom", "CUSTOM"),
    ],
)
def test_custom_headers(httpserver: HTTPServer, matcher_class, comparator_name: str, header_name: str):
    headers_with_values_in_direct_order = {header_name: 'Scheme key0="value0", key1="value1"'}
    httpserver.expect_request(uri="/", headers=headers_with_values_in_direct_order).respond_with_data("OK")
    response = requests.get(httpserver.url_for("/"), headers=headers_with_values_in_direct_order)
    assert response.status_code == 200
    assert response.text == "OK"

    # By default different order of items in header value dicts means different header values
    headers_with_values_in_modified_order = {"Custom": 'Scheme key1="value1", key0="value0"'}
    response = requests.get(httpserver.url_for("/"), headers=headers_with_values_in_modified_order)
    assert response.status_code == 500

    # Define header_value_matcher that ignores the order of items in header value dict
    def custom_header_value_matcher(actual: str | None, expected: str) -> bool:
        if actual is None:
            return False
        actual_scheme, _, actual_dict_str = actual.partition(" ")
        expected_scheme, _, expected_dict_str = expected.partition(" ")
        actual_dict = parse_dict_header(actual_dict_str)
        expected_dict = parse_dict_header(expected_dict_str)
        return actual_scheme == expected_scheme and actual_dict == expected_dict

    header_value_matcher = matcher_class({comparator_name: custom_header_value_matcher})

    httpserver.handlers.clear()
    httpserver.expect_request(
        uri="/", headers=headers_with_values_in_direct_order, header_value_matcher=header_value_matcher
    ).respond_with_data("OK")
    response = requests.get(httpserver.url_for("/"), headers=headers_with_values_in_modified_order)
    assert response.status_code == 200
    assert response.text == "OK"


# See https://en.wikipedia.org/wiki/Digest_access_authentication
@pytest.mark.parametrize(
    ("header_name", "case_insensitive"),
    [
        ("Authorization", False),
        ("Authorization", True),
        ("authorization", True),
        ("AUTHORIZATION", True),
        ("aUtHoRiZaTiOn", True),
    ],
)
def test_authorization_headers(httpserver: HTTPServer, header_name: str, *, case_insensitive: bool):
    server = (
        httpserver.bake(header_value_matcher=CaseInsensitiveHeaderValueMatcher()) if case_insensitive else httpserver
    )
    headers_with_values_in_direct_order = {
        header_name: (
            'Digest username="Mufasa",'
            'realm="testrealm@host.com",'
            'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",'
            'uri="/dir/index.html",'
            "qop=auth,"
            "nc=00000001,"
            'cnonce="0a4f113b",'
            'response="6629fae49393a05397450978507c4ef1",'
            'opaque="5ccc069c403ebaf9f0171e9517f40e41"'
        )
    }
    server.expect_request(uri="/", headers=headers_with_values_in_direct_order).respond_with_data("OK")
    response = requests.get(server.url_for("/"), headers=headers_with_values_in_direct_order)
    assert response.status_code == 200
    assert response.text == "OK"

    headers_with_values_in_modified_order = {
        "Authorization": (
            "Digest qop=auth,"
            'username="Mufasa",'
            'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",'
            'uri="/dir/index.html",'
            "nc=00000001,"
            'realm="testrealm@host.com",'
            'response="6629fae49393a05397450978507c4ef1",'
            'cnonce="0a4f113b",'
            'opaque="5ccc069c403ebaf9f0171e9517f40e41"'
        )
    }
    response = requests.get(server.url_for("/"), headers=headers_with_values_in_modified_order)
    assert response.status_code == 200
    assert response.text == "OK"


def test_header_one_key_multiple_values(httpserver: HTTPServer):
    httpserver.expect_request(uri="/t1").respond_with_data(headers=[("X-Foo", "123"), ("X-Foo", "456")])
    httpserver.expect_request(uri="/t2").respond_with_data(headers={"X-Foo": ["123", "456"]})

    headers = Headers()
    headers.add("X-Foo", "123")
    headers.add("X-Foo", "456")

    httpserver.expect_request(uri="/t3").respond_with_data(headers=headers)

    for uri in ("/t1", "/t2", "/t3"):
        conn = http.client.HTTPConnection("localhost:{}".format(httpserver.port))
        conn.request("GET", uri)
        response = conn.getresponse()
        conn.close()

        assert response.status == 200
        assert response.headers.get_all("X-Foo") == ["123", "456"]
