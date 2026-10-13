import pytest
import requests

from pytest_httpserver import HeaderValueMatcher
from pytest_httpserver import HTTPServer


def header_matcher(header_name: str, actual: str | None, expected: str) -> bool:
    if header_name.lower() == "authorization":
        return HeaderValueMatcher.authorization_header_value_matcher(actual, expected)

    return actual == expected


@pytest.mark.parametrize(
    "header_name",
    [
        "foo",
        "Foo",
        "FOO",
        "FoO",
    ],
)
def test_case_insensitive_header_matcher(httpserver: HTTPServer, header_name: str):
    server = httpserver.bake(header_value_matcher=header_matcher)
    server.expect_request("/foo", headers={"Foo": "bar"}).respond_with_data("OK")

    assert requests.get(server.url_for("/foo"), headers={header_name: "bar"}).text == "OK"


def test_authorization_headers(httpserver: HTTPServer):
    server = httpserver.bake(header_value_matcher=header_matcher)
    headers_with_values_in_direct_order = {
        "AuTHoRIZation": (
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
    response = requests.get(httpserver.url_for("/"), headers=headers_with_values_in_direct_order)
    assert response.status_code == 200
    assert response.text == "OK"
