
import pytest
import requests


@pytest.fixture
def endpoint_url(httpserver):
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    return httpserver.url_for("/foobar")


@pytest.fixture
def handler(httpserver, endpoint_url):
    return httpserver.handlers[0]


def test_calls_are_recorded(handler, endpoint_url):
    requests.post(endpoint_url, json={'foo': 'bar'})
    requests.post(endpoint_url, data='something')
    assert handler.calls == ['{"foo": "bar"}', 'something']


def test_calls_when_nothing_happened_yet(handler):
    assert handler.calls == []


def test_requests_without_body_are_not_recorded(handler, endpoint_url):
    requests.get(endpoint_url)
    assert handler.calls == [None]


def test_calls_are_accessible_as_json(handler, endpoint_url):
    requests.post(endpoint_url, json={'foo': 'bar'})
    assert handler.calls_json == [{"foo": "bar"}]


def test_multiple_calls(handler, endpoint_url):
    requests.post(endpoint_url, json={'foo': 'bar'})
    requests.get(endpoint_url)
    requests.post(endpoint_url, json={'foo2': 'bar2'})
    assert handler.calls_json == [{"foo": "bar"}, None, {"foo2": "bar2"}]
    assert handler.calls == ['{"foo": "bar"}', None, '{"foo2": "bar2"}']
