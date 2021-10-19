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
]

from .httpserver import HTTPServer
from .httpserver import HTTPServerError, Error, NoHandlerError
from .httpserver import WaitingSettings, HeaderValueMatcher, RequestHandler
from .httpserver import URIPattern, URI_DEFAULT, METHOD_ALL
