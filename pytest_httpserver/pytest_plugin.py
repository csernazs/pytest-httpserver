

import pytest
from .httpserver import HTTPServer


@pytest.fixture
def httpserver():
    retval = HTTPServer()
    retval.start()
    yield retval
    retval.stop()
