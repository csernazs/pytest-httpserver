import requests

from pytest_httpserver import HTTPServer


def test_oneshot(httpserver: HTTPServer):
    httpserver.expect_oneshot_request("/foobar").respond_with_data("OK foobar")
    httpserver.expect_oneshot_request("/foobaz").respond_with_data("OK foobaz")

    assert len(httpserver.oneshot_handlers) == 2

    # first requests should pass
    response = requests.get(httpserver.url_for("/foobaz"))
    httpserver.check_assertions()
    assert response.status_code == 200
    assert response.text == "OK foobaz"

    response = requests.get(httpserver.url_for("/foobar"))
    httpserver.check_assertions()
    assert response.status_code == 200
    assert response.text == "OK foobar"

    assert len(httpserver.oneshot_handlers) == 0

    # second requests should fail due to 'oneshot' type
    assert requests.get(httpserver.url_for("/foobar")).status_code == 500
    assert requests.get(httpserver.url_for("/foobaz")).status_code == 500


def test_oneshot_any_method(httpserver: HTTPServer):
    for _ in range(5):
        httpserver.expect_oneshot_request("/foobar").respond_with_data("OK")

    response = requests.post(httpserver.url_for("/foobar"))
    assert response.text == "OK"
    assert response.status_code == 200

    response = requests.get(httpserver.url_for("/foobar"))
    assert response.text == "OK"
    assert response.status_code == 200

    response = requests.delete(httpserver.url_for("/foobar"))
    assert response.text == "OK"
    assert response.status_code == 200

    response = requests.put(httpserver.url_for("/foobar"))
    assert response.text == "OK"
    assert response.status_code == 200

    response = requests.patch(httpserver.url_for("/foobar"))
    assert response.text == "OK"
    assert response.status_code == 200

    assert len(httpserver.oneshot_handlers) == 0
