# this is required to make sphinx able to find references for classes put inside
# typing.TYPE_CHECKING block

from ssl import SSLContext

from werkzeug.wrappers import Request
from werkzeug.wrappers import Response

import pytest_httpserver.blocking_httpserver
import pytest_httpserver.httpserver

pytest_httpserver.httpserver.SSLContext = SSLContext
pytest_httpserver.blocking_httpserver.SSLContext = SSLContext

pytest_httpserver.blocking_httpserver.Request = Request
pytest_httpserver.blocking_httpserver.Response = Response
