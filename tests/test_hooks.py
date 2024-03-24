from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import requests
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response

from pytest_httpserver.hooks import Chain
from pytest_httpserver.hooks import Delay
from pytest_httpserver.hooks import Garbage

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer


class MyDelay(Delay):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.evidence: int | None = None

    def _sleep(self):
        assert self.evidence is None, "_sleep should be called only once"
        self.evidence = self._seconds


def my_hook(_request: Request, response: Response) -> Response:
    return Response(response.get_data() + b"-SUFFIX", status=response.status)


def test_hook(httpserver: HTTPServer):

    httpserver.expect_request("/foo").with_hook(my_hook).respond_with_data("OK")

    assert requests.get(httpserver.url_for("/foo")).text == "OK-SUFFIX"


def test_hook_no_overwrite(httpserver: HTTPServer):
    with pytest.raises(AssertionError, match="Hook should not be set already"):
        httpserver.expect_request("/foo").with_hook(my_hook).with_hook(my_hook).respond_with_data("OK")


def test_delay_hook(httpserver: HTTPServer):
    delay = MyDelay(10)
    httpserver.expect_request("/foo").with_hook(delay).respond_with_data("OK")
    assert requests.get(httpserver.url_for("/foo")).text == "OK"
    assert delay.evidence == 10


def test_garbage_hook(httpserver: HTTPServer):
    httpserver.expect_request("/foo").with_hook(Garbage(128)).respond_with_data("OK")
    assert len(requests.get(httpserver.url_for("/foo")).content) == 130


def test_chain(httpserver: HTTPServer):
    delay = MyDelay(10)
    httpserver.expect_request("/foo").with_hook(Chain(delay, Garbage(128))).respond_with_data("OK")
    assert len(requests.get(httpserver.url_for("/foo")).content) == 130
    assert delay.evidence == 10
