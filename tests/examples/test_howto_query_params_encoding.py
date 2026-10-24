import requests


def test_encoded_query_string(httpserver):
    httpserver.expect_request("/search", query_string="q=hello%20world").respond_with_data("OK")

    assert requests.get(httpserver.url_for("/search") + "?q=hello%20world").status_code == 200
    httpserver.check()


def test_decoded_query_mapping(httpserver):
    httpserver.expect_request("/search", query_string={"q": "hello world"}).respond_with_data("OK")

    assert requests.get(httpserver.url_for("/search") + "?q=hello%20world").status_code == 200
    assert requests.get(httpserver.url_for("/search"), params={"q": "hello world"}).status_code == 200
    httpserver.check()


def test_literal_plus_and_percent(httpserver):
    httpserver.expect_request("/search", query_string={"q": "a+b", "literal": "hello%20world"}).respond_with_data("OK")

    response = requests.get(httpserver.url_for("/search") + "?q=a%2Bb&literal=hello%2520world")
    assert response.status_code == 200
    httpserver.check()
