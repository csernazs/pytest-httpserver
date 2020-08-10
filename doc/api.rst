
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

WaitingSettings
~~~~~~~~~~~~~~~

    .. autoclass:: WaitingSettings
        :members:

HeaderValueMatcher
~~~~~~~~~~~~~~~~~~

    .. autoclass:: HeaderValueMatcher
        :members:

RequestHandler
~~~~~~~~~~~~~~

    .. autoclass:: RequestHandler
        :members:


pytest_httpserver.httpserver
----------------------------
This module contains some internal classes which are normally not instantiated
by the user.

.. automodule:: pytest_httpserver.httpserver

    .. autoclass:: RequestMatcher
        :members:

    .. autoclass:: pytest_httpserver.httpserver.Error
        :members:

    .. autoclass:: pytest_httpserver.httpserver.NoHandlerError
        :members:

    .. autoclass:: pytest_httpserver.httpserver.HTTPServerError
        :members:

    .. autoclass:: pytest_httpserver.httpserver.RequestHandlerList
        :members:

