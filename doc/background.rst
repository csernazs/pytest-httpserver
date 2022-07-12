.. _background:

Background
==========

This document describes what design decisions were made during the development
of this library. It also describes how the library works in detail.

This document assumes that you can use the library and have at least limited
knowledge about the source code. If you feel that it is not true for you, you
may want to read the :ref:`tutorial` and :ref:`howto`.


API design
----------

The API should be simple for use to simple cases, but also provide great
flexibility for the advanced cases. When increasing flexibility of the API it
should not change the simple API unless it is absolutely required.

API compatibility is paramount. API breaking is only allowed when it is on par
with the gain of the new functionality.

Adding new parameters to functions which have default value is not considered a
breaking API change.


Simple API
~~~~~~~~~~

API should be kept as simple as possible. It means that describing an expected
request and its response should be trivial for the user. For this reason, the
API is flat: it contains a handful of functions which have many parameters
accepting built-in python types (such as bytes, string, int, etc) in contrast
to more classes and functions with less arguments.

This API allows to define an expected request and the response which will be
sent back to the client in a single line. This is one of the key features so
using the library is not complicated.

Example:

.. code-block:: python

    def test_query_params(httpserver):
        httpserver.expect_request("/foo", query_string={"user": "user1"}).respond_with_data(
            "OK"
        )

It is simple in the most simple cases, but once the expectation is more
specific, the line can grow significantly, so here the user is expected to put
the literals into variables:

.. code-block:: python

    def test_query_params(httpserver):
        httpserver.expect_request("/foo", query_string=expected_query).respond_with_data(
            "OK"
        )


If the user wants something more complex, classes are available for this which
can be instantiated and then specified for the parameters normally accepting
only built-in types.

The easy case should be made easy, with the possibility of making advanced
things in a bit more complex way.

Flexible API
~~~~~~~~~~~~

The API should be also made flexible as possible but it should not break the
simple API and not make the simple API complicated. A good example for this is
the `respond_with_handler` method, which accepts a callable object (eg. a
function) which receives the request object and returns the response object.

The user can implement the required logic there.

Adding this flexibility however did not cause any change in the simple API, the
simple cases can be still used as before.


Higher-level API
~~~~~~~~~~~~~~~~

In the early days of this library, it wanted to support the low-level http
protocol elements: request status, headers, etc to provide full coverage for the
protocol itself. This was made in order to make the most advanced customizations
possible.

Then the project received a few PRs adding `HeaderValueMatcher` and support for
authorization which relied on the low-level API to add a higher-level API
without breaking it. In the opposite case, adding a low-level API to a
high-level would not be possible.

Transparency
~~~~~~~~~~~~

The API provided by *pytest-httpserver* is transparent. That means that the
objects (most importantly the `Request` and `Response` objects) defined by
*werkzeug* are visible by the user of *pytest-httpserver*, there is no wrapping
made. This is done by the sake of simplicity.

As *werkzeug* provides a stable API, there's no need to change this in the
future, however this also limits the library to stick with *werkzeug* in the
long term. Replacing *werkzeug* to something else would break the API due to
this transparency.

Requirements
------------

This section describes how to work with pytest-httpserver's requirements.
These are the packages used by the library.

Number of requirements
~~~~~~~~~~~~~~~~~~~~~~

It is required to keep the requirements at minimum. When adding a new library to
the package requirements, research in the following topics should be done:

* code quality
* activity of the development and maintenance
* number of open issues, and their content
* how many people using that library
* python interpreter versions supported
* amount of API breaking changes
* license

Sometimes, it is better to have the own implementation instead of having a tiny
library added to the requirements, which may cause compatibility issues.


Requirements version restrictions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general, the package requirements should have no version restrictions. For
example, the *werkzeug* library has no restrictions, which means that if a new
version comes out of it, it is assumed that *pytest-httpserver* will be able to
run with it.

Many people uses this library in an environment having full of other packages
and limiting version here will limit their versions in their requirements also.
For example if there's a software using *werkzeug* `1.0.0` and our requirements
have `<0.9` specified it will make *pytest-httpserver* incompatible with their
software.


Requirements testing
~~~~~~~~~~~~~~~~~~~~

Currently it is required to test with only the latest version of the required
packages. However, if there's an API breaking change which affects
*pytest-httpserver*, a decision should be made:

* apply version restrictions, possibly making *pytest-httpserver* incompatible
  with some other software

* add workaround to *pytest-httpserver* to support both APIs


HTTP server
-----------

The chosen HTTP server which drives this library is implemented by the *werkzeug*
library. The reason behind this decision is that *werkzeug* is used by Flask, a
very popular web framework and it provides a proven, stable API in the long
term.

Supported python versions
-------------------------

Supporting the latest python versions (such as 3.7 and 3.8 at the time of
writing this), is a must. Supporting the older versions is preferred, following
the state of the officially supported python versions by PSF.

The library should be tested periodically on the supported versions.

Dropping support for old python versions is possible if supporting would cause
an issue or require extensive workaround. Currently, 3.4 is still supported by
the library, however it is deprecated by PSF. As it causes no problems for
*pytest-httpserver* (there's an additional requirement for this in the setup.py,
but that's all), the support for this version will be maintained as long as
possible. Once a new change is added to the library which require great effort
to maintain compatibility with 3.4, the support for it will be dropped.


Testing and coverage
--------------------

It is not required to have 100% test coverage but all possible use-cases should
be covered. Github actions is used to test the library on all the supported
python versions, and tox.ini is provided if local testing is desired.

When a bug is reported, there should be a test for it, which would re-produce
the error and it should pass with the fix.

Server starting and stopping
----------------------------

The server is started when the first test is run which uses the httpserver
fixture. It will be running till the end of the session, and new tests will use
the same instance. A cleanup is done between the tests which restores the clean
state (no handlers registered, empty log, etc) to avoid cross-talk.

The reason behind this is the time required to stop the server. For some reason,
*werkzeug* (the http server used) needs about 1 second to stop itself. Adding this
time to each test is not acceptable in most of the cases.

Note that it is still compatible with *pytest-xdist* (a popular pytest extension
to run the tests in parallel) as in such case, distinct test sessions will be
run and those will have their own http server instance.


Fixture scope
-------------

Due to the nature of the http server (it is run only once), it seems to be a
good recommendation to keep the httpserver fixture session scoped, not function
scoped. The problem is that the cleanup which needs to be done between the
tests (as the server is run only once, see above), and that cleanup needs to be
attached to a function scoped fixture.

HTTP port selection
-------------------

In early versions of the library, the user had to specify which port the server
should be bound. This later changed to have an so-called ephemeral port, which
is a random free port number chosen by the kernel. It is good because it
guarantees that it will be available and it allows parallel test runnings for
example.

In some cases it is not desired (eg if the code being tested has wired-in port
number), in such cases it is still possible to specify the port number.

Also, the host can be specified which allows to bind on "0.0.0.0" so the server
is accessible from the network in case you want to test a javascript code
running on a different server in a browser.
