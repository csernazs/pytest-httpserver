from pytest_httpserver import HTTPServer


def test_server_with_statement():
    with HTTPServer(port=4001):
        pass
