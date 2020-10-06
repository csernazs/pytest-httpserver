
import requests
from pytest_httpserver import HTTPProxy

def test_proxy_http(httpproxy: HTTPProxy):
    httpproxy.expect_request("/proxy/http://example.com/path/file.html").respond_with_data("Hello world!")

    with requests.Session() as session:
        session.proxies = {"http": httpproxy.get_proxy_url()}
        resp = session.get("http://example.com/path/file.html", )
        assert resp.status_code == 200
        assert resp.text == "Hello world!"


def test_proxy_https(httpproxy: HTTPProxy):
    httpproxy.expect_request("/proxy/https://example.com/path/file.html").respond_with_data("Hello world!")

    with requests.Session() as session:
        session.verify = httpproxy.ca_cert
        session.proxies = {"https": httpproxy.get_proxy_url()}

        resp = session.get("https://example.com/path/file.html")
        assert resp.status_code == 200
        assert resp.text == "Hello world!"
