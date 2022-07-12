import json

import pytest
import requests

from pytest_httpserver import HTTPServer


def test_json_matcher(httpserver: HTTPServer):
    httpserver.expect_request("/foo", json={"foo": "bar"}).respond_with_data("Hello world!")
    assert requests.get(httpserver.url_for("/foo")).status_code == 500
    resp = requests.get(httpserver.url_for("/foo"), json={"foo": "bar"})
    assert resp.status_code == 200
    assert resp.text == "Hello world!"
    assert requests.get(httpserver.url_for("/foo"), json={"foo": "bar", "foo2": "bar2"}).status_code == 500


def test_json_matcher_with_none(httpserver: HTTPServer):
    httpserver.expect_request("/foo", json=None).respond_with_data("Hello world!")
    resp = requests.get(httpserver.url_for("/foo"), data=json.dumps(None), headers={"content-type": "application/json"})
    assert resp.status_code == 200
    assert resp.text == "Hello world!"


def test_json_matcher_without_content_type(httpserver: HTTPServer):
    httpserver.expect_request("/foo", json={"foo": "bar"}).respond_with_data("Hello world!")
    assert requests.get(httpserver.url_for("/foo"), json={"foo": "bar"}).status_code == 200
    assert requests.get(httpserver.url_for("/foo"), data=json.dumps({"foo": "bar"})).status_code == 200


def test_json_matcher_with_invalid_json(httpserver: HTTPServer):
    httpserver.expect_request("/foo", json={"foo": "bar"}).respond_with_data("Hello world!")
    assert requests.get(httpserver.url_for("/foo"), data="invalid-json").status_code == 500
    assert requests.get(httpserver.url_for("/foo"), data='{"invalid": "json"').status_code == 500
    assert requests.get(httpserver.url_for("/foo"), data=b"non-text\x1f\x8b").status_code == 500


def test_data_and_json_mutually_exclusive(httpserver: HTTPServer):
    with pytest.raises(ValueError):
        httpserver.expect_request("/foo", json={}, data="foo")
