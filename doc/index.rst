.. pytest_httpserver documentation master file, created by
   sphinx-quickstart on Sat Aug 11 08:07:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


User's Guide
------------
pytest-httpserver is a python package which allows you to start a real HTTP server
for your tests. The server can be configured programmatically to how to respond to
requests.

The aim of this project is to provide an easy to use API to start the server, configure
the request handlers and then shut it down gracefully. All of these without touching
a configuration file or dealing with daemons.

As the HTTP server is spawned in a different thread and listening on a TCP port, you
can use any HTTP client. This library also helps you migrating to a different HTTP
client library without the need to re-write any test for your client application.

This library can be used with pytest in the most convenient way but if you prefer to use
other test frameworks, you can still use it with the context API or by writing a wrapper
for it.

Example with pytest
-------------------

.. code:: python

    import requests

    def test_json_client(httpserver: HTTPServer):
        httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
        assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}


Example without pytest
----------------------

.. code:: python

    import requests
    import unittest
    from pytest_httpserver import HTTPServer

    class TestJSONClient(unittest.TestCase):
        def setUp(self):
            self.httpserver = HTTPServer()
            self.httpserver.start()

        def test_json_client(self):
            self.httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
            self.assertEqual(requests.get(self.httpserver.url_for("/foobar")).json(), {'foo': 'bar'})

        def tearDown(self):
            self.httpserver.stop()


API Reference
-------------

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
