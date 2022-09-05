
.. _api-documentation:

API documentation
=================

pytest_httpserver
-----------------

.. automodule:: pytest_httpserver

HTTPServer
~~~~~~~~~~

    .. autoclass:: HTTPServer
        :members:
        :inherited-members:

RequestHandler
~~~~~~~~~~~~~~

    .. autoclass:: RequestHandler
        :members:
        :inherited-members:


BlockingHTTPServer
~~~~~~~~~~~~~~~~~~

    .. autoclass:: BlockingHTTPServer
        :members:
        :inherited-members:

BlockingRequestHandler
~~~~~~~~~~~~~~~~~~~~~~

    .. autoclass:: BlockingRequestHandler
        :members:
        :inherited-members:

WaitingSettings
~~~~~~~~~~~~~~~

    .. autoclass:: WaitingSettings
        :members:

HeaderValueMatcher
~~~~~~~~~~~~~~~~~~

    .. autoclass:: HeaderValueMatcher
        :members:

URIPattern
~~~~~~~~~~

    .. autoclass:: URIPattern
        :members:

HTTPServerError
~~~~~~~~~~~~~~~

    .. autoclass:: HTTPServerError
        :members:

NoHandlerError
~~~~~~~~~~~~~~

    .. autoclass:: NoHandlerError
        :members:


pytest_httpserver.httpserver
----------------------------
This module contains some internal classes which are normally not instantiated
by the user.

.. automodule:: pytest_httpserver.httpserver

    .. autoclass:: RequestMatcher
        :members:

    .. autoclass:: pytest_httpserver.httpserver.HTTPServerBase
        :members:

    .. autoclass:: pytest_httpserver.httpserver.Error
        :members:

    .. autoclass:: pytest_httpserver.httpserver.NoHandlerError
        :members:

    .. autoclass:: pytest_httpserver.httpserver.HTTPServerError
        :members:

    .. autoclass:: pytest_httpserver.httpserver.RequestHandlerList
        :members:
