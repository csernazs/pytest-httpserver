
import requests
from pytest_httpserver import HTTPProxy


def test_proxy():
    proxy = HTTPProxy(port=8080)
    proxy.expect_request("/proxy/http://example.com/path/file.html").respond_with_data("Hello world!")

    proxy.start()
    try:
        resp = requests.get("http://example.com/path/file.html", proxies={"http": "http://localhost:8080/"})
        assert resp.status_code == 200
        assert resp.text == "Hello world!"
    finally:
        proxy.stop()
