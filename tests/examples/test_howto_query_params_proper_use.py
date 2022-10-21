def test_query_params(httpserver):
    httpserver.expect_request("/foo", query_string="user=bar")
