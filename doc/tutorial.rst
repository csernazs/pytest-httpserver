
.. _tutorial:

Tutorial
========

If you haven't worked with this library yet, this document is for you.

Writing your first test
-----------------------

With pytest-httpserver, a test looks like this:

.. code:: python

    import requests


    def test_json_client(httpserver: HTTPServer):
        httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
        assert requests.get(httpserver.url_for("/foobar")).json() == {"foo": "bar"}

In the first line of the code, we are setting up an expectation. The
expectation contains the http request which is expected to be made:

.. code:: python

    httpserver.expect_request("/foobar")

This code tells that the httpserver, which is started automatically and running
on localhost, should accept the request "http://localhost/foobar". Configuring
how to handle this request is then done with the following method:

.. code:: python

    respond_with_json({"foo": "bar"})

This tells that when the request arrives to the *http://localhost/foobar* URL,
it must respond with the provided json. The library accepts here any python
object which is json serializable. Here, a dict is provided.

In the next line, an http request is sent with the *requests* library:

.. code:: python

    assert requests.get(httpserver.url_for("/foobar")).json() == {"foo": "bar"}


There's no customization (such as mocking) to be made. You don't need to
figure out the port number where the server is running, as there's the
``url_for()`` method provided to format the URL.

As you can see there are two different part of the httpserver configuration:

1. setting up what kind of request we are expecting

2. telling how the request should be handled and which content should
   be responded.

Important note on server port number
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The test should be run with an unprivileged user. As it is not possible to bind
to the default http port (80), the library binds the server to an available port
which is higher than 1024. In the examples on this page when we are referring to
the url *http://localhost/...* it is assumed that the url contains the http port
also.

It is advised to use the ``url_for()`` method to construct an URL as it will
always contain the correct port number in the URL.

If you need the http port as an integer, you can get is by the ``port``
attribute of the ``httpserver`` object.


How to test your http client
----------------------------

.. note::

    This section describes the various ways of http client testing. If you are
    sure that pytest-httpserver is the right library for you, you can skip this
    section.


You've written your first http client application and you want to write a test
for it. You have the following options:

1. Test your application against the production http server

2. Mock your http calls, so they won't reach any real server

3. Run a fake http server listening on localhost behaving like the real http
   server

pytest-httpserver provides API for the 3rd option: it runs a real http
server on localhost so you can test your client connecting to it.

However, there's no silver bullet and the possibilities above have their pros
and cons.


Test your application against the production http server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pros:

* It needs almost no change in the source code and you can run the tests with no
  issues.

* Writing tests is simple.

Cons:

* The tests will use a real connection to the real server, it will generate
  some load on the server, which may be acceptable or not. If the real server is
  down or you have some connectivity issue, you can't run tests.

* If the server has some state, for example, a backend database with user data,
  authentication, etc, you have to solve the *shared resource* problem if you want
  to allow multiple test runnings on different hosts. For example, if there are
  more than one developers and/or testers.

* Ensuring that there's no crosstalk is very important: if there's some
  change made by one instance, it should be invisible to the other. It
  should either revert the changes or do it in a separate namespace which
  will be cleaned up by some other means such as periodic jobs. Also, the test
  should not have inconsistent state behind.


Mock your http calls, so they won't reach any real server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pros:

* It needs almost no change in the source code and you can run the tests with no
  issues.

* There are excellent libraries supporting mocking such as **responses** and
  **pytest-vcr**.

* No need to ensure crosstalk or manage shared resources.

* Tests work offline.

Cons:

* No actual http requests are sent. It needs great effort to mock the
  existing behavior of the original library (such as **requests**) and you
  need to keep the two libraries in sync.

* Mocking must support the http client library of your choice. Eg. if you
  use **requests** you need to use **responses**. If you are using different
  libraries, the complexity raises.

* At some point, it is not like black-box testing as you need to know the
  implementation details of the original code.

* It is required to set up the expected requests and their responses. If the
  server doesn't work like your setup, the code will break when it is run with
  the real server.


Run a fake http server listening on localhost
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pros:

* Writing tests is simple.

* No need to ensure crosstalk or manage shared resources.

* Tests work offline.

* Actual http requests are sent. There's a real http server running speaking
  http protocol so you can test all the special cases you need. You
  can customize every http request expectations and their responses
  to the end.

* Testing connectivity issues is possible.

* There's no mocking, no code injection or class replacement.

* It is black-box testing as there's no need to know anything about the
  original code.

Cons:

* Some code changes required in the original source code. The code should
  accept the server endpoint (host and port) as a parameter or by some means
  of configuration. This endpoint will be set to localhost during the test
  running. If it is not possible, you need to tweak name resolution.

* It is required to set up the expected requests and their responses. If the
  server doesn't work like your setup, the code will break when it is run with
  the real server.

* Setting up TLS/SSL requires additional knowledge (cert generation, for
  example)


Specifying the expectations and constraints
-------------------------------------------

In the above code, the most simple case was shown. The library provides many ways
to customize the expectations.

In the example above, the code expected a request to */foobar* with any method
(such as *GET*, *PUT*, *POST*, *DELETE*). If you want to limit the method to the *GET*
method only, you can specify:

.. code:: python

    httpserver.expect_request("/foobar", method="GET")

Similarly, specifying the query parameters is possible:

.. code:: python

    httpserver.expect_request("/foobar", query_string="user=user1", method="GET")

This will match the GET request made to the http://localhost/foobar?user=user1
URL. If more constraint is specified to the ``expect_request()`` method, the
expectation will be narrower, eg. it is similar when using logical AND.

If you want, you can specify the query string as a dictionary so the order
of the key-value pairs does not matter:

.. code:: python

    httpserver.expect_request(
        "/foobar", query_string={"user": "user1", "group": "group1"}, method="GET"
    )

Similar to query parameters, it is possible to specify constraints for http
headers also.

For many parameters, you can specify either string or some expression (such
as the dict in the example above).

For example, specifying a regexp pattern for the URI Is also possible by specifying a
compiled regexp object:

.. code:: python

    httpserver.expect_request(
        re.compile("^/foo"), query_string={"user": "user1", "group": "group1"}, method="GET"
    )

The above will match every URI starting with "/foo".

All of these are documented in the :ref:`api-documentation`.


Specifying responses
--------------------

Once you have set up the expected request, it is required to set up the
response which will be returned to the client.

In the example we used ``respond_with_json()`` but it is also possible to
respond with an arbitrary content.

.. code:: python

    respond_with_data("Hello world!", content_type="text/plain")

In the example above, we are responding a text/plain content.
You can specify the status also:

.. code:: python

    respond_with_data("Not found", status=404, content_type="text/plain")


With this method, it is possible to set the response headers, mime type.

In some cases you need to create your own Response instance (which is the
Response object from the underlying werkzeug library), so you can respond
with it. This allows more customization, however, in most cases the
respond_with_data is sufficient:

.. code:: python

    respond_with_response(Response("Hello world!"))
    # same as
    respond_with_data("Hello world!")

If you need to produce dynamic content, use the ``respond_with_handler``
method, which accepts a callable (eg. a python function):

.. code:: python

    def my_handler(request):
        # here, examine the request object
        return Response("Hello world!")


    respond_with_handler(my_handler)


Ordered and oneshot expectations
--------------------------------

In the above examples, we used ``expect_request()`` method, which registered the
request to be handled. During the test running you can issue requests to
this endpoint as many times as you want, and you will get the same response
(unless you used the ``respond_with_handler()`` method, detailed above).

There are two other additional limitations which can be used:

* ordered handling, which specifies the order of the requests
* oneshot handling, which specifies the lifetime of the handlers for only
  one request

Ordered handling
~~~~~~~~~~~~~~~~

The ordered handling specifies the order of the requests. It must be the same
as the order of the registration:

.. code:: python

    def test_ordered(httpserver: HTTPServer):
        httpserver.expect_ordered_request("/foobar").respond_with_data("OK foobar")
        httpserver.expect_ordered_request("/foobaz").respond_with_data("OK foobaz")

        requests.get(httpserver.url_for("/foobar"))
        requests.get(httpserver.url_for("/foobaz"))


The above code passes the test running. The first request matches the first
handler, and the second request matches the second one.

When making the requests in a reverse order, it will fail:

.. code:: python

    def test_ordered(httpserver: HTTPServer):
        httpserver.expect_ordered_request("/foobar").respond_with_data("OK foobar")
        httpserver.expect_ordered_request("/foobaz").respond_with_data("OK foobaz")

        requests.get(httpserver.url_for("/foobaz"))
        requests.get(httpserver.url_for("/foobar"))  # <- fail?

If you run the above code you will notice that no test failed. This is
because the http server is running in its own thread, separately from the
client code. It has no way to raise an assertion error in the client thread.

However, this test checks nothing but runs two subsequent queries and that's it.
Checking the http status code would make it fail:

.. code:: python

    def test_ordered(httpserver: HTTPServer):
        httpserver.expect_ordered_request("/foobar").respond_with_data("OK foobar")
        httpserver.expect_ordered_request("/foobaz").respond_with_data("OK foobaz")

        assert requests.get(httpserver.url_for("/foobaz")).status_code == 200
        assert requests.get(httpserver.url_for("/foobar")).status_code == 200  # <- fail!


For further details about error handling, please read the
:ref:`handling-test-errors` chapter.


Oneshot handling
~~~~~~~~~~~~~~~~

Oneshot handling is useful when you want to ensure that the client makes only
one request to the specified URI. Once the request is handled and the response
is sent, the handler is no longer registered and a further call to the same URL
will be erroneous.

.. code:: python

    def test_oneshot(httpserver: HTTPServer):
        httpserver.expect_oneshot_request("/foobar").respond_with_data("OK")

        requests.get(httpserver.url_for("/foobar"))
        requests.get(httpserver.url_for("/foobar"))  # this will get http status 500


If you run the above code you will notice that no test failed. This is
because the http server is running in its own thread, separately from the
client code. It has no way to raise an assertion error in the client thread.

However, this test checks nothing but runs two subsequent queries and that's it.
Checking the http status code would make it fail:

.. code:: python

    def test_oneshot(httpserver: HTTPServer):
        httpserver.expect_oneshot_request("/foobar").respond_with_data("OK")

        assert requests.get(httpserver.url_for("/foobar")).status_code == 200
        assert requests.get(httpserver.url_for("/foobar")).status_code == 200  # fail!


For further details about error handling, please read the
:ref:`handling-test-errors` chapter.

.. _handling-test-errors:

Handling test errors
~~~~~~~~~~~~~~~~~~~~

If you look at carefully at the test running, you realize that the second
request (and all further requests) will get an http status 500 code,
explaining the issue in the response body. When a properly written http
client gets http status 500, it should raise an exception, which will be
unhandled and in the end the test will be failed.

In some cases, however, you want to make sure that everything is ok so far,
and raise AssertionError when something is not good. Call the
``check_assertions()`` method of the httpserver object, and this will look at
the server's internal state (which is running in the other thread) and if
there's something not right (such as the order of the requests not matching,
or there was a non-matching request), it will raise an AssertionError and
your test will properly fail:

.. code:: python

    def test_ordered_ok(httpserver: HTTPServer):
        httpserver.expect_ordered_request("/foobar").respond_with_data("OK foobar")
        httpserver.expect_ordered_request("/foobaz").respond_with_data("OK foobaz")

        requests.get(httpserver.url_for("/foobaz"))
        requests.get(httpserver.url_for("/foobar"))  # gets 500

        httpserver.check_assertions()  # this will raise AssertionError and make the test failing


The server writes a log about the requests and responses which were
processed. This can be accessed in the `log` attribute of the http server.
This log is a python list with 2-element tuples (request, response).


Server lifetime
~~~~~~~~~~~~~~~

Http server is started when the first test uses the `httpserver` fixture,
and it will be running for the rest of the session. The server is not
stopped and started between the tests as it is an expensive operation, it
takes up to 1 second to properly stop the server.

To avoid crosstalk (eg one test leaving its state behind), the server's
state is cleaned up between test runnings.

Debugging
~~~~~~~~~

If you having multiple requests for the server, adding the call to
``check_assertions()`` may to debug as it will make the test failed as
soon as possible.

.. code:: python

    import requests


    def test_json_client(httpserver: HTTPServer):
        httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
        requests.get(httpserver.url_for("/foo"))
        requests.get(httpserver.url_for("/bar"))
        requests.get(httpserver.url_for("/foobar"))

        httpserver.check_assertions()

In the above code, the first request (to **/foo**) is not successful (it gets
http status 500), but as the response status is not checked (or any of the
response), and there's no call to ``check_assertions()``, the test continues the
running. It gets through the **/bar** request, which is also not successful
(and gets http status 500 also like the first one), then goes the last request
which is successful (as there's a handler defined for it)

In the end, when checking the check_assertions() raise the error for the first
request, but it is a bit late: figuring out the request which caused the problem
could be troublesome. Also, it will report the problem for the first request only.

Adding more call of ``check_assertions()`` will help.


.. code:: python

    import requests


    def test_json_client(httpserver: HTTPServer):
        httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
        requests.get(httpserver.url_for("/foo"))
        httpserver.check_assertions()

        requests.get(httpserver.url_for("/bar"))
        httpserver.check_assertions()

        requests.get(httpserver.url_for("/foobar"))
        httpserver.check_assertions()


In the above code, the test will fail after the first request.

In case you do not want to fail the test, you can use any of these options:

* ``assertions`` attribute of the ``httpserver`` object is a list of the
  known errors. If it is non-empty, then there was an issue.

* ``format_matchers()`` method of the ``httpserver`` object returns which
  handlers have been registered to the server. In some cases, registering
  non-matching handlers causes the problem so printing this string can help
  to diagnose the problem.


Advanced topics
---------------

This is the end of the tutorial, however, not everything is covered here and
this library offers a lot more.

Further readings:

* :ref:`api-documentation`
* :ref:`howto`
