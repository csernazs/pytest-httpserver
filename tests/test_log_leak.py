import pytest
import requests

from pytest_httpserver import HTTPServer


class Client:
    def __init__(self) -> None:
        self.url: str | None = None

    def get(self):
        if self.url:
            requests.get(self.url)


@pytest.fixture
def my_fixture():
    client = Client()
    yield client
    client.get()


def test_1(my_fixture: Client, httpserver: HTTPServer):
    httpserver.expect_request("/foo").respond_with_data("OK")
    my_fixture.url = httpserver.url_for("/foo")


def test_2(httpserver: HTTPServer):
    assert httpserver.log == []
