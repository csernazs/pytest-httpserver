import requests

from pytest_httpserver import HTTPServer
from pytest_httpserver import RequestMatcher


def test_log_querying_example(httpserver: HTTPServer):
    # set up the handler for the request
    httpserver.expect_request("/foo").respond_with_data("OK")

    # make a request matching the handler
    assert requests.get(httpserver.url_for("/foo")).text == "OK", "Response should be 'OK'"

    # make another request non-matching and handler
    assert (
        requests.get(httpserver.url_for("/no_match")).status_code == 500
    ), "Response code should be 500 for non-matched requests"

    # you can query the log directly
    # log will contain all request-response pair, including non-matching
    # requests and their response as well
    assert len(httpserver.log) == 2, "2 request-response pairs should be in the log"

    # there are the following methods to query the log
    #
    # each one uses the matcher we created for the handler in the very beginning
    # of this test, RequestMatcher accepts the same parameters what you were
    # specifying to the `expect_request` (and similar) methods.

    # 1. get counts
    # (returns 0 for non-matches)
    httpserver.get_matching_requests_count(
        RequestMatcher("/foo")
    ) == 1, "There should be one request matching the the /foo request"

    # 2. assert for matching request counts
    # by default it asserts for exactly 1 matches
    # it is roughly the same as:
    # ```
    # assert httpserver.get_matching_requests_count(...) == 1
    # ```
    # assertion text will be a fully-detailed explanation about the error, including
    # the similar handlers (which might have been inproperly configured)
    httpserver.assert_request_made(RequestMatcher("/foo"))

    # you can also specify the counts
    # if you want, you can specify 0 to check for non-matching requests

    # there should have been 0 requests for /bar
    httpserver.assert_request_made(RequestMatcher("/bar"), count=0)

    # 3. iterate over the matching request-response pairs
    # this provides you greater flexibility
    for request, response in httpserver.iter_matching_requests(RequestMatcher("/foo")):
        assert request.url == httpserver.url_for("/foo")
        assert response.get_data() == b"OK"
