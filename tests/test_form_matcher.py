import pytest
import requests
from werkzeug import Request
from werkzeug import Response
from werkzeug.datastructures import MultiDict

from pytest_httpserver import HTTPServer
from pytest_httpserver.httpserver import RequestMatcher


@pytest.mark.parametrize("expect_method", ["expect_request", "expect_oneshot_request", "expect_ordered_request"])
def test_form_matcher_request(httpserver: HTTPServer, expect_method: str):
    form = MultiDict([("tag", "first"), ("tag", "second"), ("name", "José + %"), ("flag", "")])
    expect = getattr(httpserver, expect_method)
    expect("/form", method="POST", data_form=form).respond_with_data("ok")

    response = requests.post(httpserver.url_for("/form"), data=list(form.items(multi=True)))

    assert response.status_code == 200
    assert response.text == "ok"
    httpserver.check()


@pytest.mark.parametrize(
    ("expected", "body", "matches"),
    [
        ({"foo": "bar"}, "foo=bar&foo=other", True),
        ({"foo": "other"}, "foo=bar&foo=other", False),
        ({"foo": "bar"}, "foo=bar&extra=value", False),
        ({"flag": ""}, "flag=", True),
        ({"flag": ""}, "", False),
        ({}, "", True),
        (MultiDict([("tag", "first"), ("tag", "second")]), "tag=first&tag=second", True),
        (MultiDict([("tag", "first"), ("tag", "second")]), "tag=first", False),
    ],
)
def test_form_matcher_values(expected, body: str, matches: bool):  # noqa: FBT001
    request = Request.from_values(method="POST", data=body, content_type="application/x-www-form-urlencoded")
    matcher = RequestMatcher("/", data_form=expected)

    assert matcher.match(request) is matches
    if not matches:
        assert matcher.difference(request) == [("data_form", request.form, expected)]
        assert "data_form=" in repr(matcher)


def test_form_matcher_needs_form_content_type():
    request = Request.from_values(method="POST", data="foo=bar", content_type="text/plain")
    assert not RequestMatcher("/", data_form={"foo": "bar"}).match(request)


def test_form_matcher_preserves_request_body(httpserver: HTTPServer):
    def handler(request: Request) -> Response:
        assert request.form["foo"] == "bar"
        return Response(request.get_data())

    httpserver.expect_request("/form", data_form={"foo": "bar"}).respond_with_handler(handler)

    response = requests.post(httpserver.url_for("/form"), data={"foo": "bar"})

    assert response.status_code == 200
    assert response.content == b"foo=bar"
    httpserver.check()


@pytest.mark.parametrize("other_body", [{"data": "foo=bar"}, {"json": {}}])
def test_form_matcher_body_parameters_mutually_exclusive(httpserver: HTTPServer, other_body):
    with pytest.raises(ValueError, match="mutually exclusive"):
        httpserver.expect_request("/form", data_form={}, **other_body)
