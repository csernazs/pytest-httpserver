from pytest_httpserver import HTTPServer
from pytest_httpserver import URIPattern


class PrefixMatch(URIPattern):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def match(self, uri):
        return uri.startswith(self.prefix)


def test_uripattern_object(httpserver: HTTPServer):
    httpserver.expect_request(PrefixMatch("/foo")).respond_with_json({"foo": "bar"})
