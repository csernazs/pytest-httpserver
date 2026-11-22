from collections.abc import Callable

import pytest
import requests

from pytest_httpserver import BakedHTTPServer
from pytest_httpserver import HTTPServer
from pytest_httpserver import RequestMatcherKwargs
from pytest_httpserver import WaitingSettings


def test_bake_with_headers(httpserver: HTTPServer) -> None:
    server = httpserver.bake(headers={"Content-Type": "application/json"})
    server.expect_request("/foo").respond_with_json({"result": "ok"})

    response = requests.get(
        httpserver.url_for("/foo"),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.json() == {"result": "ok"}


def test_bake_with_form(httpserver: HTTPServer) -> None:
    server = httpserver.bake(method="POST", data_form={"foo": "bar"})
    server.expect_request("/form").respond_with_data("ok")

    response = requests.post(server.url_for("/form"), data={"foo": "bar"})

    assert response.status_code == 200
    assert response.text == "ok"
    httpserver.check()


@pytest.mark.parametrize(
    ("bake_chain", "expect_kwargs", "request_method"),
    [
        pytest.param(
            lambda s: s.bake(method="POST"),
            {},
            "POST",
            id="bake-default",
        ),
        pytest.param(
            lambda s: s.bake(method="GET"),
            {"method": "POST"},
            "POST",
            id="call-time-override",
        ),
        pytest.param(
            lambda s: s.bake(method="GET").bake(method="POST"),
            {},
            "POST",
            id="chained-override",
        ),
    ],
)
def test_bake_method_resolution(
    httpserver: HTTPServer,
    bake_chain: Callable[[HTTPServer], BakedHTTPServer],
    expect_kwargs: RequestMatcherKwargs,
    request_method: str,
) -> None:
    server = bake_chain(httpserver)
    server.expect_request("/endpoint", **expect_kwargs).respond_with_data("ok")

    response = requests.request(request_method, httpserver.url_for("/endpoint"))
    assert response.status_code == 200
    assert response.text == "ok"


def test_bake_chained(httpserver: HTTPServer) -> None:
    server = httpserver.bake(method="POST").bake(headers={"X-Custom": "value"})
    server.expect_request("/chain").respond_with_data("chained")

    response = requests.post(
        httpserver.url_for("/chain"),
        headers={"X-Custom": "value"},
    )
    assert response.status_code == 200
    assert response.text == "chained"


def test_bake_oneshot(httpserver: HTTPServer) -> None:
    server = httpserver.bake(method="PUT")
    server.expect_oneshot_request("/once").respond_with_data("once")

    response = requests.put(httpserver.url_for("/once"))
    assert response.status_code == 200
    assert response.text == "once"

    response = requests.put(httpserver.url_for("/once"))
    assert response.status_code == 500


def test_bake_ordered(httpserver: HTTPServer) -> None:
    server = httpserver.bake(method="GET")
    server.expect_ordered_request("/first").respond_with_data("1")
    server.expect_ordered_request("/second").respond_with_data("2")

    response = requests.get(httpserver.url_for("/first"))
    assert response.status_code == 200
    assert response.text == "1"

    response = requests.get(httpserver.url_for("/second"))
    assert response.status_code == 200
    assert response.text == "2"


def test_bake_delegates_url_for(httpserver: HTTPServer) -> None:
    server = httpserver.bake(method="GET")
    assert server.url_for("/path") == httpserver.url_for("/path")


def test_bake_context_manager() -> None:
    server = HTTPServer()
    baked = server.bake(method="GET")
    with baked:
        assert server.is_running()
        baked.expect_request("/ctx").respond_with_data("ok")
        response = requests.get(baked.url_for("/ctx"))
        assert response.status_code == 200
        assert response.text == "ok"
    assert not server.is_running()


def test_bake_nested_context_manager() -> None:
    server = HTTPServer()
    with server:
        with server.bake(method="GET"):
            assert server.is_running()
        assert server.is_running()  # inner exit must not stop the server
    assert not server.is_running()


def test_bake_reentrant_context_manager() -> None:
    server = HTTPServer()
    baked = server.bake(method="GET")
    with baked:
        assert server.is_running()
        with baked:
            assert server.is_running()
        assert server.is_running()  # inner exit must not stop the server
    assert not server.is_running()  # outer exit must stop the server


def test_bake_from_server_returns_new_object(httpserver: HTTPServer) -> None:
    assert httpserver.bake(method="GET") is not httpserver.bake(method="GET")


def test_bake_from_baked_returns_new_object(httpserver: HTTPServer) -> None:
    baked = httpserver.bake(method="GET")
    assert baked.bake(headers={"X": "1"}) is not baked


def test_bake_repr() -> None:
    server = HTTPServer(host="localhost", port=12345)
    baked = server.bake(method="GET")
    assert repr(baked) == "<BakedHTTPServer defaults={'method': 'GET'} server=<HTTPServer host=localhost port=12345>>"


@pytest.mark.parametrize(
    "bake_chain",
    [
        pytest.param(lambda s: s.bake(method="GET"), id="single"),
        pytest.param(lambda s: s.bake(method="GET").bake(headers={"X-Foo": "bar"}), id="chained"),
    ],
)
def test_bake_returns_baked_type(
    httpserver: HTTPServer,
    bake_chain: Callable[[HTTPServer], BakedHTTPServer],
) -> None:
    server = bake_chain(httpserver)
    assert isinstance(server, BakedHTTPServer)


def test_bake_assigns_server_status_code(httpserver: HTTPServer) -> None:
    baked = httpserver.bake(method="GET")
    sibling = httpserver.bake(method="POST")
    chained = baked.bake(headers={"X-Request": "test"})

    baked.no_handler_status_code = 404

    assert requests.get(baked.url_for("/unmatched")).status_code == 404
    assert httpserver.no_handler_status_code == 404
    assert sibling.no_handler_status_code == 404
    assert chained.no_handler_status_code == 404

    httpserver.clear()
    assert baked.no_handler_status_code == 500
    assert sibling.no_handler_status_code == 500
    assert chained.no_handler_status_code == 500


def test_bake_assigns_server_address() -> None:
    server = HTTPServer()
    baked = server.bake(method="GET")

    baked.host = "127.0.0.1"
    baked.port = 12345

    assert baked.url_for("/path") == "http://127.0.0.1:12345/path"
    assert server.host == "127.0.0.1"
    assert server.port == 12345


def test_bake_assigns_waiting_settings() -> None:
    server = HTTPServer()
    baked = server.bake(method="GET")
    settings = WaitingSettings(timeout=0.5)

    baked.default_waiting_settings = settings

    assert server.default_waiting_settings is settings
    assert baked.default_waiting_settings is settings
    assert baked.bake().default_waiting_settings is settings


def test_bake_assigns_server_descriptor_without_reading() -> None:
    class CustomServer(HTTPServer):
        @property
        def setting(self) -> str:
            raise RuntimeError("setting must not be read")

        @setting.setter
        def setting(self, value: str) -> None:
            self.host = value

    server = CustomServer()
    baked = server.bake()

    baked.setting = "127.0.0.1"

    assert server.host == "127.0.0.1"
    assert "setting" not in vars(baked)


def test_bake_preserves_read_only_server_descriptors() -> None:
    class CustomServer(HTTPServer):
        @property
        def setting(self) -> str:
            return "read only"

    baked = CustomServer().bake()

    with pytest.raises(AttributeError, match="setting"):
        baked.setting = "replacement"

    assert baked.setting == "read only"


def test_bake_keeps_custom_attributes_local() -> None:
    server = HTTPServer()
    baked = server.bake()

    baked.label = "first"
    baked.label = "second"

    assert baked.label == "second"
    assert not hasattr(server, "label")
    # An existing local attribute keeps its original ownership even if the
    # wrapped server subsequently gains an attribute with the same name.
    server.label = "server"  # type: ignore[attr-defined]
    baked.label = "third"
    assert server.label == "server"  # type: ignore[attr-defined]
    assert baked.label == "third"


def test_bake_keeps_subclass_descriptors_local() -> None:
    class CustomBakedServer(BakedHTTPServer):
        @property
        def host(self) -> str:
            return self._local_host

        @host.setter
        def host(self, value: str) -> None:
            self._local_host = value

    server = HTTPServer(host="localhost")
    baked = CustomBakedServer(server)

    baked.host = "proxy"

    assert baked.host == "proxy"
    assert server.host == "localhost"
