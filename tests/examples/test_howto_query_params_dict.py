import requests


def test_query_params(httpserver):
    httpserver.expect_request("/foo", query_string={"user": "user1", "group": "group1"}).respond_with_data("OK")

    assert requests.get(httpserver.url_for("/foo?user=user1&group=group1")).status_code == 200
    assert requests.get(httpserver.url_for("/foo?group=group1&user=user1")).status_code == 200
