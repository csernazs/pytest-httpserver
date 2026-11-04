from __future__ import annotations

from typing import TYPE_CHECKING

# requests is imported (although not used directly here) so the inner pytest
# runs performed by the pytester fixture use the same module instance.
# Otherwise the sys.modules cleanup done by the pytester between the runs
# results in mixed module identities (causing weird errors in the requests
# library)
import requests  # noqa: F401

if TYPE_CHECKING:
    import pytest

pytester_args = ("-p", "pytest_httpserver")


def test_unmatched_request_shown_in_failed_report(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import requests

        def test_unmatched(httpserver):
            httpserver.expect_request("/expected").respond_with_data("OK")
            requests.get(httpserver.url_for("/unexpected"))
            assert False, "test failed"
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        [
            "*pytest-httpserver report*",
            "*No handler found for request*unexpected*",
            "*Persistent matchers:*",
            "*uri='/expected'*",
        ]
    )


def test_unmatched_request_not_shown_in_passed_report(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import requests

        def test_unmatched(httpserver):
            requests.get(httpserver.url_for("/unexpected"))
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(passed=1)
    result.stdout.no_fnmatch_line("*pytest-httpserver report*")


def test_no_section_when_no_pending_errors(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import requests

        def test_ok_request_but_failing_assertion(httpserver):
            httpserver.expect_request("/expected").respond_with_data("OK")
            requests.get(httpserver.url_for("/expected"))
            assert False, "test failed"
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(failed=1)
    result.stdout.no_fnmatch_line("*pytest-httpserver report*")


def test_checked_assertion_not_reported_twice(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import pytest
        import requests

        def test_checked(httpserver):
            requests.get(httpserver.url_for("/unexpected"))
            with pytest.raises(AssertionError):
                httpserver.check_assertions()
            assert False, "test failed"
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(failed=1)
    # the assertion was already raised (and shown in the traceback) so the
    # report section must not contain it again
    result.stdout.no_fnmatch_line("*pytest-httpserver report*")


def test_multiple_unmatched_requests_all_reported(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import requests

        def test_multiple_unmatched(httpserver):
            requests.get(httpserver.url_for("/unexpected1"))
            requests.get(httpserver.url_for("/unexpected2"))
            assert False, "test failed"
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        [
            "*pytest-httpserver report*",
            "*No handler found for request*unexpected1*",
            "*No handler found for request*unexpected2*",
        ]
    )


def test_handler_error_shown_in_failed_report(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import requests

        def test_handler_error(httpserver):
            def handler(_):
                raise ValueError("handler is broken")

            httpserver.expect_request("/error").respond_with_handler(handler)
            requests.get(httpserver.url_for("/error"))
            assert False, "test failed"
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        [
            "*pytest-httpserver report*",
            "*Errors raised by request handlers:*",
            "*ValueError('handler is broken')*",
        ]
    )


def test_error_in_setup_shows_report(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import pytest
        import requests

        @pytest.fixture
        def client(httpserver):
            requests.get(httpserver.url_for("/unexpected"))
            raise RuntimeError("error in the fixture")

        def test_setup_error(client):
            assert client == "client"
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(
        [
            "*pytest-httpserver report*",
            "*No handler found for request*unexpected*",
        ]
    )


def test_server_state_not_leaked_between_tests(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import requests

        def test_unmatched_but_passing(httpserver):
            requests.get(httpserver.url_for("/unexpected"))

        def test_failing_without_httpserver():
            assert False, "test failed"
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(passed=1, failed=1)
    # the second test does not use the httpserver fixture so the pending
    # assertion of the first test must not leak into its report
    result.stdout.fnmatch_lines(["*test_failing_without_httpserver*"])
    result.stdout.no_fnmatch_line("*pytest-httpserver report*")


def test_ipv4_server_reported(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import requests

        def test_unmatched(httpserver_ipv4):
            requests.get(httpserver_ipv4.url_for("/unexpected"))
            assert False, "test failed"
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        [
            "*pytest-httpserver report*",
            "*No handler found for request*unexpected*",
        ]
    )


def test_no_duplication_when_setup_and_teardown_fails(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import pytest
        import requests

        @pytest.fixture
        def client(httpserver):
            requests.get(httpserver.url_for("/unexpected_setup"))
            raise RuntimeError("error in setup")

        @pytest.fixture
        def teardown_error():
            yield
            raise RuntimeError("error in teardown")

        def test_setup_and_teardown_error(teardown_error, client):
            pass
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(errors=2)
    # the same pending assertion must be attached to one report only
    title_lines = [line for line in result.stdout.lines if "pytest-httpserver report" in line]
    assert len(title_lines) == 1
    result.stdout.fnmatch_lines(
        [
            "*pytest-httpserver report*",
            "*No handler found for request*unexpected_setup*",
        ]
    )


def test_errors_made_in_teardown_reported_once(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import pytest
        import requests

        @pytest.fixture
        def client(httpserver):
            yield "client"
            requests.get(httpserver.url_for("/unexpected_teardown"))
            raise RuntimeError("error in teardown")

        def test_teardown_error(client, httpserver):
            requests.get(httpserver.url_for("/unexpected_call"))
            assert False, "test failed"
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(failed=1, errors=1)
    # each error is reported in the report of the phase where it was collected
    title_lines = [line for line in result.stdout.lines if "pytest-httpserver report" in line]
    assert len(title_lines) == 2
    result.stdout.fnmatch_lines(
        [
            "*No handler found for request*unexpected_teardown*",
            "*No handler found for request*unexpected_call*",
        ]
    )


def test_registered_custom_server_reported(pytester: pytest.Pytester):
    pytester.makepyfile("""
        import pytest
        import requests
        from pytest_httpserver import BlockingHTTPServer
        from pytest_httpserver.pytest_plugin import register_server

        @pytest.fixture
        def blocking_httpserver(request):
            server = BlockingHTTPServer(timeout=1)
            server.start()
            register_server(request, server)
            yield server
            server.clear()
            if server.is_running():
                server.stop()

        def test_registered(blocking_httpserver):
            requests.get(blocking_httpserver.url_for("/unexpected"), timeout=5)
            assert False, "test failed"
        """)
    result = pytester.runpytest(*pytester_args)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        [
            "*pytest-httpserver report*",
            "*No handler found for request*unexpected*",
        ]
    )
