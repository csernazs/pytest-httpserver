pytest_httpserver
~~~~~~~~~~~~~~~~~
HTTP server for pytest


Nutshell
--------

This library is designed to help to test http clients without contacting the real http server.
In other words, it is a fake http server which is accessible via localhost can be started with
the pre-defined expected http requests and their responses.

Example
-------

.. code-block:: python

    def test_my_client(server): # server is a pytest fixture which starts the server
        # set up the server to serve /foobar with the json
        server.expect_request("/foobar").respond_with_json({"foo": "bar"})
        # check sthat it is served
        assert requests.get(server.url_for("/foobar")).json() == {'foo': 'bar'}

