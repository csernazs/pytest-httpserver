import re

import requests


def test_httpserver_with_regexp(httpserver):
    httpserver.expect_request(re.compile("^/foo"), method="GET")
    requests.get(httpserver.url_for("/foobar"))
