#!.venv/bin/python3

import urllib.error
import urllib.request

from pytest_httpserver import HTTPServer

server = HTTPServer(port=4000)
server.expect_request("/foobar").respond_with_json({"foo": "bar"})
server.start()
try:
    print(urllib.request.urlopen("http://localhost:4000/foobar?name=John%20Smith&age=123").read())
except urllib.error.HTTPError as err:
    print(err)

server.stop()
