

import pytest
from .httpserver import Server


@pytest.fixture
def server():
    retval = Server()
    retval.start()
    yield retval
    retval.stop()
