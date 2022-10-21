def test_query_params(httpserver):
    httpserver.expect_request("/foo", query_string={"user": "user1"}).respond_with_data("OK")
