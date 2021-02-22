
.. _fixtures:

Fixtures
========

pytest-httpserver provides the following pytest fixtures. These fixtures can be
overridden the usual name, by defining a fixture with the same name. Make sure
that you are defining the fixture with the same scope as the original one. For
more details, read the related part of the `pytest howto`_.

httpserver
----------

Scope
    function

Type
    :py:class:`pytest_httpserver.HTTPServer`


This fixture provides the main functionality for the library. It is a httpserver
instance where you can add your handlers and expectations. It is a function
scoped fixture as the server's state needs to be cleared between the tests.



httpserver_listen_address
-------------------------

Scope
    session (in 1.0.0 and above, *function* otherwise)

Type:
    ``Tuple[str, int]``

Default:
    ``("localhost", 0)``

This fixture can return the address and port where the server will bind. If port
is given is 0, the server to an ephemeral port, which is an available randomly
selected port. If you run your tests in parallel, this should be used so
multiple servers can be started.


httpserver_listen_address


httpserver_ssl_context
----------------------
Scope
    session

Type:
    ``ssl.SSLContext``

Default:
    ``None``


This fixture should return the ssl context which will be used to run a https
server. For more details please see the `ssl`_ module documentation of the
standard library.


make_httpserver
---------------
Scope
    session

Type:
    :py:class:`pytest_httpserver.HTTPServer`

Default:
    A running :py:class:`pytest_httpserver.HTTPServer` instance.


This is a factory fixture which creates the instance of the httpserver which
will be used by the ``httpserver`` fixture. By default, it uses the
``httpserver_listen_address`` and the ``httpserver_ssl_context`` fixtures but
can be overridden to add more customization.

It yields a running HTTPServer instance and also stops it when it is no longer
needed at the end of the session. If you want to customize this fixture it is
highly recommended to look at its definition in `pytest_plugin.py`_.



.. _pytest_plugin.py:
    https://github.com/csernazs/pytest-httpserver/blob/master/pytest_httpserver/pytest_plugin.py

.. _pytest howto:
    https://docs.pytest.org/en/documentation-restructure/how-to/fixture.html#overriding-fixtures-on-various-levels

.. _ssl:
    https://docs.python.org/3/library/ssl.html
