"""
This is package provides the main API for the pytest_httpserver package.

"""
__all__ = [
    "HTTPServer",
    "HTTPServerError",
    "Error",
    "NoHandlerError",
    "WaitingSettings",
    "HeaderValueMatcher",
    "RequestHandler",
    "URIPattern",
    "URI_DEFAULT",
    "METHOD_ALL",
    "BlockingHTTPServer",
    "BlockingRequestHandler",
]

from .blocking_httpserver import BlockingHTTPServer
from .blocking_httpserver import BlockingRequestHandler
from .httpserver import METHOD_ALL
from .httpserver import URI_DEFAULT
from .httpserver import Error
from .httpserver import HeaderValueMatcher
from .httpserver import HTTPServer
from .httpserver import HTTPServerError
from .httpserver import NoHandlerError
from .httpserver import RequestHandler
from .httpserver import URIPattern
from .httpserver import WaitingSettings
