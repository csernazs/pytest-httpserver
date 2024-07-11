from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import requests

from pytest_httpserver.hooks import Chain
from pytest_httpserver.hooks import Delay
from pytest_httpserver.hooks import Garbage

if TYPE_CHECKING:
    from werkzeug import Request
    from werkzeug import Response

    from pytest_httpserver import HTTPServer


class MyDelay(Delay):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.evidence: int | None = None

    def _sleep(self):
        assert self.evidence is None, "_sleep should be called only once"
        self.evidence = self._seconds


def suffix_hook_factory(suffix: bytes):
    def hook(_request: Request, response: Response) -> Response:
        response.set_data(response.get_data() + suffix)
        return response

    return hook


def test_hook(httpserver: HTTPServer):
    my_hook = suffix_hook_factory(b"-SUFFIX")
    httpserver.expect_request("/foo").with_post_hook(my_hook).respond_with_data("OK")

    assert requests.get(httpserver.url_for("/foo")).text == "OK-SUFFIX"


def test_delay_hook(httpserver: HTTPServer):
    delay = MyDelay(10)
    httpserver.expect_request("/foo").with_post_hook(delay).respond_with_data("OK")
    assert requests.get(httpserver.url_for("/foo")).text == "OK"
    assert delay.evidence == 10


def test_garbage_hook(httpserver: HTTPServer):
    httpserver.expect_request("/prefix").with_post_hook(Garbage(prefix_size=128)).respond_with_data("OK")
    httpserver.expect_request("/suffix").with_post_hook(Garbage(suffix_size=128)).respond_with_data("OK")
    httpserver.expect_request("/both").with_post_hook(Garbage(prefix_size=128, suffix_size=128)).respond_with_data("OK")
    httpserver.expect_request("/large_prefix").with_post_hook(Garbage(prefix_size=10 * 1024 * 1024)).respond_with_data(
        "OK"
    )

    resp_content = requests.get(httpserver.url_for("/prefix")).content
    assert len(resp_content) == 130
    assert resp_content[128:] == b"OK"

    resp_content = requests.get(httpserver.url_for("/large_prefix")).content
    assert len(resp_content) == 10 * 1024 * 1024 + 2
    assert resp_content[10 * 1024 * 1024 :] == b"OK"

    resp_content = requests.get(httpserver.url_for("/suffix")).content
    assert len(resp_content) == 130
    assert resp_content[:2] == b"OK"

    resp_content = requests.get(httpserver.url_for("/both")).content
    assert len(resp_content) == 258
    assert resp_content[128:130] == b"OK"

    with pytest.raises(AssertionError, match="prefix_size should be positive integer"):
        Garbage(-10)

    with pytest.raises(AssertionError, match="suffix_size should be positive integer"):
        Garbage(10, -10)


def test_chain(httpserver: HTTPServer):
    delay = MyDelay(10)
    httpserver.expect_request("/foo").with_post_hook(Chain(delay, Garbage(128))).respond_with_data("OK")
    assert len(requests.get(httpserver.url_for("/foo")).content) == 130
    assert delay.evidence == 10


def test_multiple_hooks(httpserver: HTTPServer):
    delay = MyDelay(10)
    httpserver.expect_request("/foo").with_post_hook(delay).with_post_hook(Garbage(128)).respond_with_data("OK")
    assert len(requests.get(httpserver.url_for("/foo")).content) == 130
    assert delay.evidence == 10


def test_multiple_hooks_correct_order(httpserver: HTTPServer):
    hook1 = suffix_hook_factory(b"-S1")
    hook2 = suffix_hook_factory(b"-S2")

    httpserver.expect_request("/foo").with_post_hook(hook1).with_post_hook(hook2).respond_with_data("OK")

    assert requests.get(httpserver.url_for("/foo")).text == "OK-S1-S2"
