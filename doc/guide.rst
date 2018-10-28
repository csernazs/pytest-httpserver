
User's Guide
============

Starting and stopping
---------------------
The server can be started by instatiating it and then calling the
:py:meth:`pytest_httpserver.HTTPServer.start` method. This will start the server in a separate
thread, so you will need to make sure that the :py:meth:`pytest_httpserver.HTTPServer.stop` method
is called before your code exits.

A free TCP port needs to be specified when instantiating the server, where no other daemon is listening.

If you are using the pytest plugin it is done automatically by the plugin. Possibility to change
the TCP port is TBD.

When using pytest plugin, specifying the bind address and bind port can also be possible via environment
variables. Setting PYTEST_HTTPSERVER_HOST and PYTEST_HTTPSERVER_PORT will change the bind host and bind
port, respectively.

If pytest plugin is not used, the DEFAULT_LISTEN_HOST and DEFAULT_LISTEN_PORT class attributes can be set
on the HTTPServer class.

Configuring
-----------
By configuring the server means registering handlers for specific requests. Once a request matches
with the configuration the specified response handler is fired and the reponse is served.

Requests
~~~~~~~~
When registering a :py:class:`pytest_httpserver.server.RequestMatcher`, it can use various parts
of the HTTP request to be matched: URI, method, data, headers, and query string can be specified.
All of these are based on simple qeuality checking, with the exception of method and URI where a special
value specifying `any` can be given (variables `URI_DEFAULT` and `METHOD_ALL`, respectively).

:py:class:`pytest_httpserver.server.HTTPServer` also determines how these matchers are looked up and
what their lifetime is. You can register handlers which handle any amount of requests, but you can also
register one-shot handlers which only handle one request and then they disappear.

Also, there's ordered handlers which also specify the order of the requests to be handled. Not matching
the order of their registration, the server will refuse to serve any further requests.

With all of these, you can create a server with very permissive to very strict request handling.

Responses
~~~~~~~~~
Once the request is matched with one of the matchers, the handler gets fired, which can return a static
response or you can create a function which can return a dynamic response.
When dealing with static responses you can determine all parts of the http response (status, headers,
content, etc), and you can also specify a JSON-serializable object to be returned as a json.


Debugging errors while testing
------------------------------
When the tests are running against the server and no matcher can be found for the given request, the server
replies with HTTP status 500, and a short error text. This is not very helpful in most cases so if you want
to check what is the situation, you should call :py:meth:`pytest_httpserver.HTTPServer.format_matchers` or
:py:meth:`pytest_httpserver.HTTPServer.check_assertions` methods. The first one returns a human-readable
string representation of the matchers registered. The second one raises `AssertionError` with the errors
happened during the testing in the server.

Also there's a :py:attr:`pytest_httpserver.HTTPServer.log` attribute which contains the request-reponse
object pairs what the server handled.
