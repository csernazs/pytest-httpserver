
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
    assert len(handler.calls)
    assert handler.calls[0].data == b'{"foo": "bar"}'
    assert handler.calls[1].data == b'something'


def test_calls_when_nothing_happened_yet(handler):
    assert handler.calls == []


def test_calls_are_accessible_as_json(handler, endpoint_url):
    requests.post(endpoint_url, json={'foo': 'bar'})
    assert handler.calls_data() == [{"foo": "bar"}]


def test_calls_data_with_empty_json_returns_none(handler, endpoint_url):
    requests.post(endpoint_url, json=None)
    assert handler.calls_data() == [None]


def test_multiple_calls(handler, endpoint_url):
    requests.post(endpoint_url, json={'foo': 'bar'})
    requests.get(endpoint_url)
    requests.post(endpoint_url, json={'foo2': 'bar2'})
    assert handler.calls_data() == [{"foo": "bar"}, None, {"foo2": "bar2"}]
    assert handler.calls_data(auto_load=False) == [b'{"foo": "bar"}', b'', b'{"foo2": "bar2"}']
