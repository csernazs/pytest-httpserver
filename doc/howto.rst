
.. _howto:

Howto
=====

This documentation is a collection of the most common use cases, and their
solutions. If you have not used this library before, it may be better to read
the :ref:`tutorial` first.


Matching query parameters
-------------------------

To match query parameters, you must not included them to the URI, as this will
not work:

.. code-block:: python

    def test_query_params(httpserver):
        httpserver.expect_request("/foo?user=bar") # never do this

There's an explicit place where the query string should go:

.. code-block:: python

    def test_query_params(httpserver):
        httpserver.expect_request("/foo", query_string="user=bar")

The ``query_string`` is the parameter which does not contains the leading
question mark ``?``.

.. note::

    The reason behind this is the underlying http server library *werkzeug*,
    which provides the ``Request`` object which is used for the matching the
    request with the handlers. This object has the ``query_string`` attribute
    which contains the query.


As the order of the parameters in the query string usually does not matter, you
can specify a dict for the ``query_string`` parameter (the naming may look a bit
strange but we wanted to keep API compatibility and this dict matching feature
was added later).

.. code-block:: python

    def test_query_params(httpserver):
        httpserver.expect_request("/foo", query_string={"user": "user1", "group": "group1"}).respond_with_data("OK")

        assert requests.get("/foo?user=user1&group=group1").status_code == 200
        assert requests.get("/foo?group=group1&user=user1").status_code == 200

In the example above, both requests pass the test as we specified the expected
query string as a dictionary.

Behind the scenes an additional step is done by the library: it parses up the
query_string into the dict and then compares it with the dict provided.


URI matching
------------

The simplest form of URI matching is providing as a string. This is a equality
match, if the URI of the request is not equal with the specified one, the
request will not be handled.

If this is not desired, you can specify a regexp object (returned by the
``re.compile()`` call).

.. code:: python

    httpserver.expect_request(re.compile("^/foo"), method="GET")

The above will match every URI starting with "/foo".

There's an additional way to extend this functionality. You can specify your own
method which will receive the URI. All you need is to subclass from the
``URIPattern`` class and define the ``match()`` method which will get the uri as
string and should return a boolean value.


.. code:: python

    class PrefixMatch(URIPattern):
        def __init__(self, prefix: str):
            self.prefix = prefix

        def match(self, uri):
            return uri.startswith(self.prefix)

    def test_uripattern_object(httpserver: HTTPServer):
        httpserver.expect_request(PrefixMatch("/foo")).respond_with_json({"foo": "bar"})

Authentication
--------------

When doing http digest authentication, the client may send a request like this:

.. code::

    GET /dir/index.html HTTP/1.0
    Host: localhost
    Authorization: Digest username="Mufasa",
                        realm="testrealm@host.com",
                        nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
                        uri="/dir/index.html",
                        qop=auth,
                        nc=00000001,
                        cnonce="0a4f113b",
                        response="6629fae49393a05397450978507c4ef1",
                        opaque="5ccc069c403ebaf9f0171e9517f40e41"


Implementing a matcher is difficult for this request as the order of the
parameters in the ``Authorization`` header value is arbitrary.

By default, pytest-httpserver includes an Authorization header parser so the
order of the parameters in the ``Authorization`` header does not matter.

.. code:: python

    def test_authorization_headers(httpserver: HTTPServer):
        headers_with_values_in_direct_order = {
            'Authorization': ('Digest username="Mufasa",'
                            'realm="testrealm@host.com",'
                            'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",'
                            'uri="/dir/index.html",'
                            'qop=auth,'
                            'nc=00000001,'
                            'cnonce="0a4f113b",'
                            'response="6629fae49393a05397450978507c4ef1",'
                            'opaque="5ccc069c403ebaf9f0171e9517f40e41"')
        }
        httpserver.expect_request(uri='/', headers=headers_with_values_in_direct_order).respond_with_data('OK')
        response = requests.get(httpserver.url_for('/'), headers=headers_with_values_in_direct_order)
        assert response.status_code == 200
        assert response.text == 'OK'

        headers_with_values_in_modified_order = {
            'Authorization': ('Digest qop=auth,'
                            'username="Mufasa",'
                            'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",'
                            'uri="/dir/index.html",'
                            'nc=00000001,'
                            'realm="testrealm@host.com",'
                            'response="6629fae49393a05397450978507c4ef1",'
                            'cnonce="0a4f113b",'
                            'opaque="5ccc069c403ebaf9f0171e9517f40e41"')
        }
        response = requests.get(httpserver.url_for('/'), headers=headers_with_values_in_modified_order)
        assert response.status_code == 200
        assert response.text == 'OK'


JSON matching
-------------

Matching the request data can be done in two different ways. One way is to
provide a python string (or bytes object) whose value will be compared to the
request body.

When the request contains a json, matching to will be error prone as an object
can be represented as json in different ways, for example when different length
of indentation is used.

To match the body as json, you need to add the python data structure (which
could be dict, list or anything which can be the result of `json.loads()` call).
The request's body will be loaded as json and the result will be compared to the
provided object. If the request's body cannot be loaded as json, the matcher
will fail and *pytest-httpserver* will proceed with the next registered matcher.

Example:

.. code:: python

    def test_json_matcher(httpserver: HTTPServer):
        httpserver.expect_request("/foo", json={"foo": "bar"}).respond_with_data("Hello world!")
        resp = requests.get(httpserver.url_for("/foo"), json={"foo": "bar"})
        assert resp.status_code == 200
        assert resp.text == "Hello world!"


.. note::
    JSON requests usually come with ``Content-Type: application/json`` header.
    *pytest-httpserver* provides the *headers* parameter to match the headers of
    the request, however matching json body does not imply matching the
    *Content-Type* header. If matching the header is intended, specify the expected
    *Content-Type* header and its value to the headers parameter.

.. note::
    *json* and *data* parameters are mutually exclusive so both of then cannot
    be specified as in such case the behavior is ambiguous.

.. note::
    The request body is decoded by using the *data_encoding* parameter, which is
    default to *utf-8*. If the request comes in a different encoding, and the
    decoding fails, the request won't match with the expected json.


Advanced header matching
------------------------

For each http header, you can specify a callable object (eg. a python function)
which will be called with the header name, header actual value and the expected
value, and will be able to determine the matching.

You need to implement such a function and then use it:

.. code:: python

    def case_insensitive_matcher(header_name: str, actual: str, expected: str) -> bool:
        if header_name == "X-Foo":
            return actual.lower() == expected.lower()
        else:
            return actual == expected


    def test_case_insensitive_matching(httpserver: HTTPServer):
        httpserver.expect_request("/", header_value_matcher=case_insensitive_matcher, headers={"X-Foo": "bar"}).respond_with_data("OK")

        assert requests.get(httpserver.url_for("/"), headers={"X-Foo": "bar"}).status_code == 200
        assert requests.get(httpserver.url_for("/"), headers={"X-Foo": "BAR"}).status_code == 200


.. note::
    Header value matcher is the basis of the ``Authorization`` header parsing.


If you want to change the matching of only one header, you may want to use the
``HeaderValueMatcher`` class.

In case you want to do it globally, you can add the header name and the callable
to the ``HeaderValueMatcher.DEFAULT_MATCHERS`` dict.


.. code:: python

    from pytest_httpserver import HeaderValueMatcher

    def case_insensitive_compare(actual: str, expected: str) -> bool:
        return actual.lower() == expected.lower()

    HeaderValueMatcher.DEFAULT_MATCHERS["X-Foo"] = case_insensitive_compare

    def test_case_insensitive_matching(httpserver: HTTPServer):
        httpserver.expect_request("/", headers={"X-Foo": "bar"}).respond_with_data("OK")

        assert requests.get(httpserver.url_for("/"), headers={"X-Foo": "bar"}).status_code == 200
        assert requests.get(httpserver.url_for("/"), headers={"X-Foo": "BAR"}).status_code == 200


In case you don't want to change the defaults, you can provide the
``HeaderValueMatcher`` object itself.

.. code:: python

    from pytest_httpserver import HeaderValueMatcher

    def case_insensitive_compare(actual: str, expected: str) -> bool:
        return actual.lower() == expected.lower()

    def test_own_matcher_object(httpserver: HTTPServer):
        matcher = HeaderValueMatcher({"X-Bar": case_insensitive_compare})

        httpserver.expect_request("/", headers={"X-Bar": "bar"}, header_value_matcher=matcher).respond_with_data("OK")

        assert requests.get(httpserver.url_for("/"), headers={"X-Bar": "bar"}).status_code == 200
        assert requests.get(httpserver.url_for("/"), headers={"X-Bar": "BAR"}).status_code == 200

Customizing host and port
-------------------------

By default, the server run by pytest-httpserver will listen on localhost on a
random available port. In most cases it works well as you want to test your app
in the local environment.

If you need to change this behavior, there are a plenty of options. It is very
important to make these changes before starting the server, eg. before running
any test using the httpserver fixture.

Use IP address *0.0.0.0* to listen globally.

.. warning::
    You should be careful when listening on a non-local ip (such as *0.0.0.0*). In this
    case anyone knowing your machine's IP address and the port can connect to the
    server.

Environment variables
~~~~~~~~~~~~~~~~~~~~~

Set ``PYTEST_HTTPSERVER_HOST`` and/or ``PYTEST_HTTPSERVER_PORT`` environment
variables to the desired values.


Class attributes
~~~~~~~~~~~~~~~~

Changing ``HTTPServer.DEFAULT_LISTEN_HOST`` and
``HTTPServer.DEFAULT_LISTEN_PORT`` attributes. Make sure that you do this before
running any test requiring the ``httpserver`` fixture. One ideal place for this
is putting it into ``conftest.py``.

Fixture
~~~~~~~

Overriding the ``httpserver_listen_address`` fixture. Similar to the solutions
above, this needs to be done before starting the server (eg. before referencing
the ``httpserver`` fixture).

.. code-block:: python

    import pytest

    @pytest.fixture(scope="session")
    def httpserver_listen_address():
        return ("127.0.0.1", 8000)


Multi-threading support
-----------------------

When your client runs in a thread, everything completes without waiting for the
first response. To overcome this problem, you can wait until all the handlers
have been served or there's some error happened.

This is available only for oneshot and ordered handlers, as
permanent handlers last forever.

To have this feature enabled, use the context object returned by the ``wait()``
method of the ``httpserver`` object.

This method accepts the following parameters:

* raise_assertions: whether raise assertions on unexpected request or timeout or
  not

* stop_on_nohandler: whether stop on unexpected request or not

* timeout: time (in seconds) until time is out

Behind the scenes it synchronizes the state of the server with the main thread.

Last, you need to assert on the ``result`` attribute of the context object.

.. code-block:: python

    def test_wait_success(httpserver: HTTPServer):
        waiting_timeout = 0.1

        with httpserver.wait(stop_on_nohandler=False, timeout=waiting_timeout) as waiting:
            requests.get(httpserver.url_for("/foobar"))
            httpserver.expect_oneshot_request("/foobar").respond_with_data("OK foobar")
            requests.get(httpserver.url_for("/foobar"))
        assert waiting.result

        httpserver.expect_oneshot_request("/foobar").respond_with_data("OK foobar")
        httpserver.expect_oneshot_request("/foobaz").respond_with_data("OK foobaz")
        with httpserver.wait(timeout=waiting_timeout) as waiting:
            requests.get(httpserver.url_for("/foobar"))
            requests.get(httpserver.url_for("/foobaz"))
        assert waiting.result


In the above code, all the request.get() calls could be in a different thread,
eg. running in parallel, but the exit condition of the context object is to wait
for the specified conditions.


Emulating connection refused error
----------------------------------

If by any chance, you want to emulate network errors such as *Connection reset
by peer* or *Connection refused*, you can simply do it by connecting to a random
port number where no service is listening:

.. code-block:: python

    import pytest
    import requests

    def test_connection_refused():
        # assumes that there's no server listening at localhost:1234
        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get("http://localhost:1234")


However connecting to the port where the httpserver had been started will still
succeed as the server is running continuously. This is working by design as
starting/stopping the server is costly.

.. code-block:: python

    import pytest
    import requests

    # setting a fixed port for httpserver
    @pytest.fixture(scope="session")
    def httpserver_listen_address():
        return ("127.0.0.1", 8000)

    # this test will pass
    def test_normal_connection(httpserver):
        httpserver.expect_request("/foo").respond_with_data("foo")
        assert requests.get("http://localhost:8000/foo").text == "foo"


    # this tess will FAIL, as httpserver started in test_normal_connection is
    # still running
    def test_connection_refused():
        with pytest.raises(requests.exceptions.ConnectionError):
            # this won't get Connection refused error as the server is still
            # running.
            # it will get HTTP status 500 as the handlers registered in
            # test_normal_connection have been removed
            requests.get("http://localhost:8000/foo")



To solve the issue, the httpserver can be stopped explicitly. It will start
implicitly when the first test starts to use it. So the
``test_connection_refused`` test can be re-written to this:

.. code-block:: python

    def test_connection_refused(httpserver):
        httpserver.stop() # stop the server explicitly
        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get("http://localhost:8000/foo")


Emulating timeout
-----------------

To emulate timeout, there's one way to register a handler function which will sleep for a
given amount of time.

.. code-block:: python

    import time
    from pytest_httpserver import HTTPServer
    import pytest
    import requests


    def sleeping(request):
        time.sleep(2)  # this should be greater than the client's timeout parameter


    def test_timeout(httpserver: HTTPServer):
        httpserver.expect_request("/baz").respond_with_handler(sleeping)
        with pytest.raises(requests.exceptions.ReadTimeout):
            assert requests.get(httpserver.url_for("/baz"), timeout=1)


There's one drawback though: the test takes 2 seconds to run as it waits the
handler thread to be completed.
