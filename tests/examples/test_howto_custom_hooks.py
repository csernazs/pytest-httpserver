import requests
from werkzeug import Request
from werkzeug import Response

from pytest_httpserver import HTTPServer


def my_hook(_request: Request, response: Response) -> Response:
    # add a new header value to the response
    response.headers["X-Example"] = "Example"
    return response


def test_custom_hook(httpserver: HTTPServer):
    httpserver.expect_request("/foo").with_post_hook(my_hook).respond_with_data(b"OK")

    assert requests.get(httpserver.url_for("/foo")).headers["X-Example"] == "Example"
