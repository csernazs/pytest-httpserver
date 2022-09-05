=============
Release Notes
=============

.. _Release Notes_1.0.6:

1.0.6
=====

.. _Release Notes_1.0.6_New Features:

New Features
------------

- Add a new way of running tests with the blocking mode. In this mode, the
  http server is synchronized to the main thread and the client code is run in
  a separate thread.


.. _Release Notes_1.0.6_Bug Fixes:

Bug Fixes
---------

- Python version classifier updated in pyproject.toml (which updates pypi also)


.. _Release Notes_1.0.5:

1.0.5
=====

.. _Release Notes_1.0.5_Bug Fixes:

Bug Fixes
---------

- Packaging of sdist and the wheel fixed by adding the extra files only to the sdist and not to the wheel.


.. _Release Notes_1.0.4:

1.0.4
=====

.. _Release Notes_1.0.4_Bug Fixes:

Bug Fixes
---------

- Fixed type hinting of ``HeaderValueMatcher.DEFAULT_MATCHERS``, which did
  not allow modifications, however it is explicitly allowed in the documentation.


.. _Release Notes_1.0.4_Other Notes:

Other Notes
-----------

- Version of flake8 library updated to require 4.0.0+ at minimum. This is
  required to make flake8 working on recent python versions.


.. _Release Notes_1.0.3:

1.0.3
=====

.. _Release Notes_1.0.3_New Features:

New Features
------------

- Additional type hints improvements to make the library more mypy compliant.
  Imports in `__init__.py` have been updated to indicate that this is a
  namespace package.


.. _Release Notes_1.0.3_Other Notes:

Other Notes
-----------

- Package deployment and CI has been migrated to poetry. poetry.lock will be kept
  up to date. Make target "quick-test" renamed to "test". Also, minor adjustments
  were made regarding documentation generation. Make targets should be identical.
  Build results like sdist, and wheel are almost identical to the one which was
  made by setuptools.


.. _Release Notes_1.0.2:

1.0.2
=====

.. _Release Notes_1.0.2_New Features:

New Features
------------

- Type hints updated to conform to 'mypy' type checking tool.
  Also, py.typed file is added as package data according to PEP 561.


.. _Release Notes_1.0.2_Deprecation Notes:

Deprecation Notes
-----------------

- Python 3.4 and 3.5 versions have been deprecated in order to support type
  hints in the source code. Users using 3.5 and earlier releases encouraged
  to upgrade to later versions. Please node that 3.5 reached EOL in September
  of 2020 and no longer receives security fixes.


.. _Release Notes_1.0.1:

1.0.1
=====

.. _Release Notes_1.0.1_New Features:

New Features
------------

- Improved error handling of custom request handlers. Request handlers added
  with ``respond_with_handler`` now can use the ``assert`` statement. Those
  errors will be reported when a further ``check_assertions()`` call is made.
  Also, unhandled exceptions raised in the request handlers can be re-raised
  by calling the new ``check_handler_errors()`` method. A new method called
  ``check()`` has been added which calls these two in sequence.


.. _Release Notes_1.0.0:

1.0.0
=====

.. _Release Notes_1.0.0_Prelude:

Prelude
-------

Functionally the same as 1.0.0rc1. For the list of changes between 0.3.8 and 1.0.0 see the changelist for 1.0.0rc1.


.. _Release Notes_1.0.0rc1:

1.0.0rc1
========

.. _Release Notes_1.0.0rc1_New Features:

New Features
------------

- Added a new session scoped fixture ``make_httpserver`` which creates the
  object for the ``httpserver`` fixture. It can be overridden to add further
  customizations and it must yield a ``HTTPServer`` object - see
  ``pytest_plugin.py`` for an implementation. As this fixture is session
  scoped, it will be called only once when the first test using httpserver is
  started. This addition also deprecates the use of ``PluginHTTPServer`` which was
  used in earlier versions as a way to customize server object creation.
  ``PluginHTTPServer`` can still be used but it may be subject to deprecation
  in the future.

- Added a new session scoped fixture ``httpserver_ssl_context`` which provides
  the SSL context for the server. By default it returns ``None``, so SSL is
  not enabled, but can be overridden to return a valid ``ssl.SSLContext``
  object which will be used for SSL connections. See test_ssl.py for example.


.. _Release Notes_1.0.0rc1_Upgrade Notes:

Upgrade Notes
-------------

- **Breaking change**: The scope of ``httpserver_listen_address`` fixture changed from **function**
  to **session**. This is a requirement to implement the other features listed
  in this release. See the `upgrade guide
  <https://pytest-httpserver.readthedocs.io/en/latest/upgrade.html>`_ for the
  details.


.. _Release Notes_0.3.8:

0.3.8
=====

.. _Release Notes_0.3.8_Deprecation Notes:

Deprecation Notes
-----------------

- Deprecation warnings were added to prepare changes to 1.0.0. More details:
  https://pytest-httpserver.readthedocs.io/en/latest/upgrade.html


.. _Release Notes_0.3.7:

0.3.7
=====

.. _Release Notes_0.3.7_Other Notes:

Other Notes
-----------

- Removed pytest-runner from setup.py as it is deprecated and makes packaging inconvenient
  as it needs to be installed before running setup.py.


.. _Release Notes_0.3.6:

0.3.6
=====

.. _Release Notes_0.3.6_New Features:

New Features
------------

- HTTP methods are case insensitive. The HTTP method specified is converted to
  uppercase in the library.

- It is now possible to specify a JSON-serializable python value (such as
  dict, list, etc) and match the request to it as JSON. The request's body
  is loaded as JSON and it will be compared to the expected value.

- The http response code sent when no handler is found for the
  request can be changed. It is set to 500 by default.


.. _Release Notes_0.3.5:

0.3.5
=====

.. _Release Notes_0.3.5_New Features:

New Features
------------

- Extend URI matching by allowing to specify URIPattern object or a compiled
  regular expression, which will be matched against the URI. URIPattern class
  is defined as abstract in the library so the user need to implement a new
  class based on it.


.. _Release Notes_0.3.4:

0.3.4
=====

.. _Release Notes_0.3.4_Bug Fixes:

Bug Fixes
---------

- Fix the tests assets created for SSL/TLS tests by extending their expiration time. Also
  update the Makefile which can be used to update these assets.


.. _Release Notes_0.3.3:

0.3.3
=====

.. _Release Notes_0.3.3_New Features:

New Features
------------

- Besides bytes and string, dict and MultiDict objects can be specified as query_string.
  When these objects are used, the query string gets parsed into a dict (or MultiDict),
  and comparison is made accordingly. This enables the developer to ignore the order of
  the keys in the query_string when expecting a request.


.. _Release Notes_0.3.3_Bug Fixes:

Bug Fixes
---------

- Fixed issue \#16 by converting string object passed as query_string
  to bytes which is the type of the query string in werkzeug, and also allowing
  bytes as the parameter.

- Fix release tagging. 0.3.2 was released in a mistake by tagging 3.0.2 to the branch.


.. _Release Notes_0.3.3_Other Notes:

Other Notes
-----------

- Add more files to source distribution (sdist). It now contains tests,
  assets, examples and other files.


.. _Release Notes_0.3.1:

0.3.1
=====

.. _Release Notes_0.3.1_New Features:

New Features
------------

- Add httpserver_listen_address fixture which is used to set up the bind address and port
  of the server. Setting bind address and port is possible by overriding this fixture.


.. _Release Notes_0.3.0:

0.3.0
=====

.. _Release Notes_0.3.0_New Features:

New Features
------------

- Support ephemeral port. This can be used by specify 0 as the port number
  to the HTTPServer instance. In such case, an unused port will be picked up
  and the server will start listening on that port. Querying the port attribute
  after server start reveals the real port where the server is actually listening.

- Unify request functions of the HTTPServer class to make the API more straightforward to use.


.. _Release Notes_0.3.0_Upgrade Notes:

Upgrade Notes
-------------

- The default port has been changed to 0, which results that the server will be staring
  on an ephemeral port.

- The following methods of HTTPServer have been changed in a backward-incompatible way:
    * :py:meth:`pytest_httpserver.HTTPServer.expect_request` becomes a general function accepting handler_type parameter so it can create any kind of request handlers
    * :py:meth:`pytest_httpserver.HTTPServer.expect_oneshot_request` no longer accepts the ordered parameter, and it creates an unordered oneshot request handler
    * :py:meth:`pytest_httpserver.HTTPServer.expect_ordered_request` is a new method creating an ordered request handler


.. _Release Notes_0.2.2:

0.2.2
=====

.. _Release Notes_0.2.2_New Features:

New Features
------------

- Make it possible to intelligently compare headers. To accomplish that
  HeaderValueMatcher was added. It already contains logic to compare
  unknown headers and authorization headers. Patch by Roman Inflianskas.


.. _Release Notes_0.2.1:

0.2.1
=====

.. _Release Notes_0.2.1_Prelude:

Prelude
-------

Minor fixes in setup.py and build environment. No actual code change in library .py files.


.. _Release Notes_0.2:

0.2
===

.. _Release Notes_0.2_New Features:

New Features
------------

- When using pytest plugin, specifying the bind address and bind port can also be possible via environment
  variables. Setting PYTEST_HTTPSERVER_HOST and PYTEST_HTTPSERVER_PORT will change the bind host and bind
  port, respectively.

- SSL/TLS support added with using the SSL/TLS support provided by werkzeug.
  This is based on the ssl module from the standard library.


.. _Release Notes_0.1.1:

0.1.1
=====

.. _Release Notes_0.1.1_Prelude:

Prelude
-------

Minor fixes in setup.py and build environment. No actual code change in library .py files.


.. _Release Notes_0.1:

0.1
===

.. _Release Notes_0.1_Prelude:

Prelude
-------

First release
