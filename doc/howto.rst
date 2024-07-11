
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

.. literalinclude :: ../tests/examples/test_howto_query_params_never_do_this.py
   :language: python

There's an explicit place where the query string should go:

.. literalinclude :: ../tests/examples/test_howto_query_params_proper_use.py
   :language: python

The ``query_string`` is the parameter which does not contain the leading
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


.. literalinclude :: ../tests/examples/test_howto_query_params_dict.py
   :language: python

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

.. literalinclude :: ../tests/examples/test_howto_regexp.py
   :language: python

The above will match every URI starting with "/foo".

There's an additional way to extend this functionality. You can specify your own
method which will receive the URI. All you need is to subclass from the
``URIPattern`` class and define the ``match()`` method which will get the uri as
string and should return a boolean value.


.. literalinclude :: ../tests/examples/test_howto_url_matcher.py
   :language: python


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

.. literalinclude :: ../tests/examples/test_howto_authorization_headers.py
   :language: python

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

.. literalinclude :: ../tests/examples/test_howto_json_matcher.py
   :language: python

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

.. literalinclude :: ../tests/examples/test_howto_case_insensitive_matcher.py
   :language: python

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

        assert (
            requests.get(httpserver.url_for("/"), headers={"X-Foo": "bar"}).status_code
            == 200
        )
        assert (
            requests.get(httpserver.url_for("/"), headers={"X-Foo": "BAR"}).status_code
            == 200
        )


In case you don't want to change the defaults, you can provide the
``HeaderValueMatcher`` object itself.

.. literalinclude :: ../tests/examples/test_howto_header_value_matcher.py
   :language: python

Using custom request handler
----------------------------
In the case the response is not static, for example it depends on the request,
you can pass a function to the ``respond_with_handler`` function. This function
will be called with a request object and it should return a Response object.


.. literalinclude :: ../tests/examples/test_howto_custom_handler.py
   :language: python

The above code implements a handler which returns a random number between 1 and
10. Not particularly useful but shows that the handler can return any computed
or derived value.

In the response handler you can also use the ``assert`` statement, similar to
the tests, but there's a big difference. As the server is running in its own
thread, this will cause a HTTP 500 error returned, and the exception registered
into a list. To get that error, you need to call ``check_assertions()`` method
of the httpserver.

In case you want to ensure that there was no other exception raised which was
unhandled, you can call the ``check_handler_errors()`` method of the httpserver.

Two notable examples for this:

.. literalinclude :: ../tests/examples/test_howto_check_handler_errors.py
   :language: python

If you want to call both methods (``check_handler_errors()`` and
``check_assertions()``) you can call the ``check()`` method, which will call
these.

.. literalinclude :: ../tests/examples/test_howto_check.py
   :language: python

.. note::
    The scope of the errors checked by the ``check()`` method may
    change in the future - it is added to check all possible errors happened in
    the server.


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

.. literalinclude :: ../tests/examples/test_howto_wait_success.py
   :language: python

In the above code, all the request.get() calls could be in a different thread,
eg. running in parallel, but the exit condition of the context object is to wait
for the specified conditions.


Emulating connection refused error
----------------------------------

If by any chance, you want to emulate network errors such as *Connection reset
by peer* or *Connection refused*, you can simply do it by connecting to a random
port number where no service is listening:

.. literalinclude :: ../tests/examples/test_howto_timeout_requests.py
   :language: python

However, connecting to the port where the httpserver had been started will still
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
        httpserver.stop()  # stop the server explicitly
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


Running an HTTPS server
-----------------------

To run an https server, `trustme` can be used to do the heavy lifting:

.. code-block:: python

    @pytest.fixture(scope="session")
    def ca():
        return trustme.CA()


    @pytest.fixture(scope="session")
    def httpserver_ssl_context(ca):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        localhost_cert = ca.issue_cert("localhost")
        localhost_cert.configure_cert(context)
        return context


    @pytest.fixture(scope="session")
    def httpclient_ssl_context(ca):
        with ca.cert_pem.tempfile() as ca_temp_path:
            return ssl.create_default_context(cafile=ca_temp_path)


    @pytest.mark.asyncio
    async def test_aiohttp(httpserver, httpclient_ssl_context):
        import aiohttp

        httpserver.expect_request("/").respond_with_data("hello world!")
        connector = aiohttp.TCPConnector(ssl=httpclient_ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(httpserver.url_for("/")) as result:
                assert (await result.text()) == "hello world!"


    def test_requests(httpserver, ca):
        import requests

        httpserver.expect_request("/").respond_with_data("hello world!")
        with ca.cert_pem.tempfile() as ca_temp_path:
            result = requests.get(httpserver.url_for("/"), verify=ca_temp_path)
        assert result.text == "hello world!"


    def test_httpx(httpserver, httpclient_ssl_context):
        import httpx

        httpserver.expect_request("/").respond_with_data("hello world!")
        result = httpx.get(httpserver.url_for("/"), verify=httpclient_ssl_context)
        assert result.text == "hello world!"


Using httpserver on a dual-stack (IPv4 and IPv6) system
-------------------------------------------------------

*pytest-httpserver* can only listen on one address and it also means that
address family is determined by that. As it relies on *Werkzeug*, it passes the
provided host parameter to it and then it is up to *Werkzeug* how the port
binding is done.

*Werkzeug* determines the address family by examining the string provided. If it
contains a colon (``:``) then it will be an IPv6 (``AF_INET6``) socket, otherwise, it
will be an IPv4 (``AF_INET``) socket. The default string in *pytest-httpserver* is
``localhost`` so by default, the httpserver listens on IPv4. If you want it to
listen on IPv6 address, provide an IPv6 address (``::1`` for example) to it.

It should be noted that dual-stack systems are still working with
*pytest-httpserver* because the clients obtain the possible addresses for the a
given name by calling ``getaddrinfo()`` or similar function which returns the
addresses together with address families, and the client iterates over this
list. In the case when *pytest-httpserver* is listening on ``127.0.0.1``, and
the client uses ``localhost`` name in the url, it will try ``::1`` first, and
then it will move on to ``127.0.0.1``, which will succeed, or vica-versa, where
``127.0.0.1`` will be successful first.

If you want to test a connection error case in your test (such as TLS error),
the client can fail in a strange way as we seen in `this issue
<https://github.com/csernazs/pytest-httpserver/issues/61>`_. In such case,
client tries with ``127.0.0.1`` first, then reaches a TLS error (which is normal
as the test case is about testing for the TLS issue), then it moves on to
``::1``, then it fails with ``Connection reset``. In such case fixing the bind
address to ``127.0.0.1`` (and thereby fixing the host part of the URL returned
by the `url_for` call) solves the issue as the client will receive the address
(``127.0.0.1``) instead of the name (``localhost``) so it won't move on to the
IPv6 address.

Running httpserver in blocking mode
-----------------------------------

In this mode, the code which is being tested (the client) is executed in a
background thread, while the server events are synchronized to the main thread,
so it looks like it is running in the main thread. This allows to catch the
assertions occured on the server side synchronously, and assertions are raised
to the main thread. You need to call `check_assertions` at the end for only the
unexpected requests.

This is an experimental feature so *pytest-httpserver* has no fixture for it
yet. If you find this feature useful any you have ideas or suggestions related
to this, feel free to open an issue.

Example:

.. literalinclude :: ../tests/examples/test_example_blocking_httpserver.py
   :language: python


Querying the log
----------------

*pytest-httpserver* keeps a log of request-response pairs in a python list. This
log can be accessed by the ``log`` attibute of the httpserver instance, but
there are methods made specifically to query the log.

Each of the log querying methods accepts a
:py:class:`pytest_httpserver.RequestMatcher` object which uses the same matching
logic which is used by the server itself. Its parameters are the same to the
parameters specified for the server's `except_request` (and the similar) methods.

The methods for querying:

* :py:meth:`pytest_httpserver.HTTPServer.get_matching_requests_count` returns
  how many requests are matching in the log as an int

* :py:meth:`pytest_httpserver.HTTPServer.assert_request_made` asserts the given
  amount of requests are matching in the log. By default it checks for one (1)
  request but other value can be specified. For example, 0 can be specified to
  check for requests not made.

* :py:meth:`pytest_httpserver.HTTPServer.iter_matching_requests` is a generator
  yielding Request-Response tuples of the matching entries in the log. This
  offers greater flexibility (compared to the other methods)

Example:

.. literalinclude :: ../tests/examples/test_howto_log_querying.py
   :language: python


Serving requests in parallel
----------------------------

*pytest-httpserver*  serves the request in a single-threaded, blocking way. That
means that if multiple requests are made to it, those will be served one by one.

There can be cases where parallel processing is required, for those cases
*pytest-httpserver* allows running a server which start one thread per request
handler, so the requests are served in parallel way (depending on Global
Interpreter Lock this is not truly parallel, but from the I/O point of view it
is).

To set this up, you have two possibilities.


Overriding httpserver fixture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One is to customize how the HTTPServer object is created. This is possible by
defining the following fixture:

.. code:: python

    @pytest.fixture(scope="session")
    def make_httpserver() -> Iterable[HTTPServer]:
        server = HTTPServer(threaded=True)  # set threaded=True to enable thread support
        server.start()
        yield server
        server.clear()
        if server.is_running():
            server.stop()


This will override the ``httpserver`` fixture in your tests.

Creating a different httpserver fixture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This way, you can create a different httpserver fixture and you can use it
besides the main one.

.. code:: python

    @pytest.fixture()
    def threaded() -> Iterable[HTTPServer]:
        server = HTTPServer(threaded=True)
        server.start()
        yield server
        server.clear()
        if server.is_running():
            server.stop()


    def test_threaded(threaded: HTTPServer): ...


This will start and stop the server for each tests, which causes about 0.5
seconds waiting when the server is stopped. It won't override the ``httpserver``
fixture so you can keep the original single-threaded behavior.

.. warning::
    Handler threads which are still running when the test is finished, will be
    left behind and won't be join()ed between the tests. If you want to ensure
    that all threads are properly cleaned up and you want to wait for them,
    consider using the second option (:ref:`Creating a different httpserver fixture`)
    described above.


Adding side effects
-------------------

Sometimes there's a need to add side effects to the handling of the requests.
Such side effect could be adding some amount of delay to the serving or adding
some garbage to response data.

While these can be achieved by using
:py:meth:`pytest_httpserver.RequestHandler.respond_with_handler` where you can
implement your own function to serve the request, *pytest-httpserver* provides a
hooks API where you can add side effects to request handlers such as
:py:meth:`pytest_httpserver.RequestHandler.respond_with_json` and others.
This allows to use the existing API of registering handlers.

Example:

.. literalinclude :: ../tests/examples/test_howto_hooks.py
    :language: python

:py:mod:`pytest_httpserver.hooks` module provides some pre-defined hooks to
use.

You can implement your own hook as well. The requirement is to have a callable
object (a function) ``Callable[[Request, Response], Response]``. In details:

* Parameter :py:class:`werkzeug.Request` which represents the request
  sent by the client.

* Parameter :py:class:`werkzeug.Response` which represents the response
  made by the handler.

* Returns a :py:class:`werkzeug.Response` object which represents the
  response will be returned to the client.


Example:

.. literalinclude :: ../tests/examples/test_howto_custom_hooks.py
    :language: python

``with_post_hook`` can be called multiple times, in this case *pytest-httpserver*
will register the hooks, and hooks will be called sequentially, one by one. Each
hook will receive the response what the previous hook returned, and the last
hook called will return the final response which will be sent back to the client.
