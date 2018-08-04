
from pytest_httpserver.httpserver import Server

import requests
import pytest


def test_expected_request(server):
    server.expect_request("/foobar").respond_with_json({"foo": "bar"})
    assert requests.get(server.url_for("/foobar")).json() == {'foo': 'bar'}


def test_unexpected_request(server: Server):
    server.expect_request("/foobar").respond_with_json({"foo": "bar"})
    requests.get(server.url_for("/nonexists"))
    server.check_assertions()
