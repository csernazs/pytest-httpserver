def test_query_params(httpserver):
    httpserver.expect_request("/foo?user=bar")  # never do this
