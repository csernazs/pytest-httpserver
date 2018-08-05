#!.venv/bin/python3

from pytest_httpserver.httpserver import HTTPServer
import time
import urllib.request
import urllib.error


def foobar(request):
    return "Hello world!"


server = HTTPServer()
server.expect_request("/foobar").respond_with_json({"foo": "bar"})
server.start()
try:
    print(urllib.request.urlopen("http://localhost:4000/foobar?name=John%20Smith&age=123").read())
except urllib.error.HTTPError as err:
    print(err)

server.stop()
