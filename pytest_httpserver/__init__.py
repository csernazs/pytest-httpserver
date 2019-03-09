"""
This is package provides the main API for the pytest_httpserver package.

"""

from .httpserver import HTTPServer
from .httpserver import HTTPServerError, Error, NoHandlerError
from .httpserver import WaitingSettings, HeaderValueMatcher, RequestHandler
from .httpserver import URI_DEFAULT, METHOD_ALL
