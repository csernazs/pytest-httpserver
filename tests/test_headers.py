import requests
from pytest_httpserver import HTTPServer
from werkzeug.http import parse_dict_header

from pytest_httpserver.httpserver import HeaderValueMatcher


def test_custom_headers(httpserver: HTTPServer):
    headers_with_values_in_direct_order = {'Custom': 'Scheme key0="value0", key1="value1"'}
    httpserver.expect_request(uri='/', headers=headers_with_values_in_direct_order).respond_with_data('OK')
    response = requests.get(httpserver.url_for('/'), headers=headers_with_values_in_direct_order)
    assert response.status_code == 200
    assert response.text == 'OK'

    # By default different order of items in header value dicts means different header values
    headers_with_values_in_modified_order = {'Custom': 'Scheme key1="value1", key0="value0"'}
    response = requests.get(httpserver.url_for('/'), headers=headers_with_values_in_modified_order)
    assert response.status_code == 500

    # Define header_value_matcher that ignores the order of items in header value dict
    def custom_header_value_matcher(actual: str, expected: str) -> bool:
        actual_scheme, _, actual_dict_str = actual.partition(' ')
        expected_scheme, _, expected_dict_str = expected.partition(' ')
        actual_dict = parse_dict_header(actual_dict_str)
        expected_dict = parse_dict_header(expected_dict_str)
        return actual_scheme == expected_scheme and actual_dict == expected_dict

    matchers = HeaderValueMatcher.DEFAULT_MATCHERS.copy()
    matchers['Custom'] = custom_header_value_matcher
    header_value_matcher = HeaderValueMatcher(matchers)

    httpserver.handlers.clear()
    httpserver.expect_request(
        uri='/',
        headers=headers_with_values_in_direct_order,
        header_value_matcher=header_value_matcher
    ).respond_with_data('OK')
    response = requests.get(httpserver.url_for('/'), headers=headers_with_values_in_modified_order)
    assert response.status_code == 200
    assert response.text == 'OK'


# See https://en.wikipedia.org/wiki/Digest_access_authentication
def test_authorization_headers(httpserver: HTTPServer):
    headers_with_values_in_direct_order = {
        'Authorization': ('Digest username="Mufasa",'
                          'realm="testrealm@host.com",'
                          'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",'
                          'uri="/dir/index.html",'
                          'qop=auth,'
                          'nc=00000001,'
                          'cnonce="0a4f113b",'
                          'response="6629fae49393a05397450978507c4ef1",'
                          'opaque="5ccc069c403ebaf9f0171e9517f40e41"')
    }
    httpserver.expect_request(uri='/', headers=headers_with_values_in_direct_order).respond_with_data('OK')
    response = requests.get(httpserver.url_for('/'), headers=headers_with_values_in_direct_order)
    assert response.status_code == 200
    assert response.text == 'OK'

    headers_with_values_in_modified_order = {
        'Authorization': ('Digest qop=auth,'
                          'username="Mufasa",'
                          'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",'
                          'uri="/dir/index.html",'
                          'nc=00000001,'
                          'realm="testrealm@host.com",'
                          'response="6629fae49393a05397450978507c4ef1",'
                          'cnonce="0a4f113b",'
                          'opaque="5ccc069c403ebaf9f0171e9517f40e41"')
    }
    response = requests.get(httpserver.url_for('/'), headers=headers_with_values_in_modified_order)
    assert response.status_code == 200
    assert response.text == 'OK'
