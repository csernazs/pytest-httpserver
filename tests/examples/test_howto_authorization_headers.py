import requests

from pytest_httpserver import HTTPServer


def test_authorization_headers(httpserver: HTTPServer):
    headers_with_values_in_direct_order = {
        "Authorization": (
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
    httpserver.expect_request(uri="/", headers=headers_with_values_in_direct_order).respond_with_data("OK")
    response = requests.get(httpserver.url_for("/"), headers=headers_with_values_in_direct_order)
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
    response = requests.get(httpserver.url_for("/"), headers=headers_with_values_in_modified_order)
    assert response.status_code == 200
    assert response.text == "OK"
