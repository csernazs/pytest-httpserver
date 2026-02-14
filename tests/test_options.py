from inspect import signature

from pytest_httpserver import HTTPServer
from pytest_httpserver import ServerOptions
from pytest_httpserver import WaitingSettings


def test_httpserver_options():
    options = ServerOptions(
        startup_timeout=60,
        threaded=True,
        default_waiting_settings=WaitingSettings(timeout=5),
    )

    server = HTTPServer.with_options(
        host="localhost",
        port=0,
        ssl_context=None,
        options=options,
    )

    assert server.startup_timeout == 60
    assert server.threaded is True
    assert server.default_waiting_settings.timeout == 5


def test_constructor_signature_matches_with_extra_options():
    # compares that ServerOptions default values matches with HTTPServer
    # constructor defaults

    httpserver_sig = signature(HTTPServer.__init__)
    options_sig = signature(ServerOptions.__init__)
    for param_name, options_param in options_sig.parameters.items():
        if param_name == "self":
            continue
        httpserver_param = httpserver_sig.parameters.get(param_name)
        assert httpserver_param is not None, f"Parameter {param_name} missing in HTTPServer"
        assert httpserver_param.default == options_param.default, (
            f"Default value for parameter {param_name} does not match: "
            f"{httpserver_param.default} != {options_param.default}"
        )
