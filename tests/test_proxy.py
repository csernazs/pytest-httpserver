
import requests


def test_proxy_http(httpproxy):
    httpproxy.expect_request("/proxy/http://example.com/path/file.html").respond_with_data("Hello world!")

    with requests.Session() as session:
        session.proxies = {"http": httpproxy.url_for("")}
        resp = session.get("http://example.com/path/file.html", )
        assert resp.status_code == 200
        assert resp.text == "Hello world!"


def test_proxy_https(httpproxy, tmp_path):
    httpproxy.expect_request("/proxy/https://example.com/path/file.html").respond_with_data("Hello world!")

    with requests.Session() as session:
        session.verify = httpproxy.proxy_options["ca_file_cache"]
        session.proxies = {"https": httpproxy.url_for("")}

        resp = session.get("https://example.com/path/file.html")
        assert resp.status_code == 200
        assert resp.text == "Hello world!"
