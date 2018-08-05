

import pytest
from .httpserver import HTTPServer


class Plugin:
    SERVER = None


@pytest.fixture
def httpserver():
    if Plugin.SERVER is None:
        server = HTTPServer()
        server.start()
        Plugin.SERVER = server
    else:
        server = Plugin.SERVER

    server.clear()
    yield server


def pytest_sessionfinish(session, exitstatus):
    if Plugin.SERVER is not None:
        Plugin.SERVER.clear()
        Plugin.SERVER.stop()
        Plugin.SERVER = None
