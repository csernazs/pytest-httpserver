from random import randint

from werkzeug import Request
from werkzeug import Response

from pytest_httpserver import HTTPServer


def test_expected_request_handler(httpserver: HTTPServer):
    def handler(request: Request):
        return Response(str(randint(1, 10)))

    httpserver.expect_request("/foobar").respond_with_handler(handler)
