def test_query_params(httpserver):
    expected_query = {"user": "user1"}
    httpserver.expect_request("/foo", query_string=expected_query).respond_with_data("OK")
