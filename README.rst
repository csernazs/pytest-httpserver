|build| |doc|


pytest_httpserver
=================
HTTP server for pytest


Nutshell
--------

This library is designed to help to test http clients without contacting the real http server.
In other words, it is a fake http server which is accessible via localhost can be started with
the pre-defined expected http requests and their responses.

Example
-------

.. code-block:: python

    def test_my_client(httpserver): # httpserver is a pytest fixture which starts the server
        # set up the server to serve /foobar with the json
        httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
        # check that the request is served
        assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}


You can also use the library without pytest. There's a with statement to ensure that the server is stopped.


.. code-block:: python

    with HTTPServer() as httpserver:
        # set up the server to serve /foobar with the json
        httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
        # check that the request is served
        print(requests.get(httpserver.url_for("/foobar")).json())


Features
--------
You can set up a dozen of expectations for the requests, and also what response should be sent by the server to the client.


Requests
~~~~~~~~
There are three different types:

- **permanent**: this will be always served when there's match for this request, you can make as many HTTP requests as you want
- **oneshot**: this will be served only once when there's a match for this request, you can only make 1 HTTP request
- **ordered**: same as oneshot but the order must be strictly matched to the order of setting up

You can also fine-tune the expected request. The following can be specified:

- URI (this is a must)
- HTTP method
- headers
- query string
- data (HTTP payload of the request)


Responses
~~~~~~~~~

Once you have the expectations for the request set up, you should also define the response you want to send back.
The following is supported currently:

- respond arbitrary data (string or bytearray)
- respond a json (a python dict converted in-place to json)
- respond a Response object of werkzeug
- use your own function

Similar to requests, you can fine-tune what response you want to send:

- HTTP status
- headers
- data


Missing features
----------------
* HTTP/2
* Keepalive
* TLS


.. |build| image:: https://travis-ci.org/csernazs/pytest-httpserver.svg?branch=master
    :target: https://travis-ci.org/csernazs/pytest-httpserver

.. |doc| image:: https://readthedocs.org/projects/pytest-httpserver/badge/?version=latest
    :target: https://pytest-httpserver.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
