import requests


def test_ipv4(httpserver_ipv4):
    httpserver_ipv4.expect_request("/").respond_with_data("OK")
    assert httpserver_ipv4.host == "127.0.0.1"

    response = requests.get(httpserver_ipv4.url_for("/"))
    assert response.text == "OK"


def test_ipv6(httpserver_ipv6):
    httpserver_ipv6.expect_request("/").respond_with_data("OK")
    assert httpserver_ipv6.host == "::1"
    assert httpserver_ipv6.url_for("/") == f"http://[::1]:{httpserver_ipv6.port}/"

    response = requests.get(httpserver_ipv6.url_for("/"))
    assert response.text == "OK"
