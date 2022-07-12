.. _upgrade:

Upgrade guides
==============

The following document describes how to upgrade to a given version of the
library which introduces breaking changes.

Introducing breaking changes
----------------------------
When a breaking change is about to be made in the library, an intermediate
release is released which generates deprecation warnings when the functionality
to be removed is used. This does not break any functionality but shows a
warning instead.

Together with this intermediate release, a new *pre-release* is released to
*pypi*. This release removes the functionality described by the warning, but
*pip* does not install this version unless you specify the *--pre* parameter to
*pip install*.

Once you made the required changes to make your code compatible with the new
version, you can install the new version by *pip install --pre
pytest-httpserver*.

After a given time period, a new non-pre release is released, this will be
installed by pip similar to other releases and it will break your code if you
have not made the required changes. If this happens, you can still pin the
version in requirements.txt or other places. Usually specifying the version with
`==` operator fixes the version, but for more details please read the
documentation of the tool you are using in manage dependencies.


1.0.0
-----

In pytest-httpserver 1.0.0 the following breaking changes were made.

* The scope of ``httpserver_listen_address`` fixture changed from **function** to **session**

In order to make your code compatible with the new version of pytest-httpserver,
you need to specify the `session` scope explicitly.

Example
~~~~~~~

Old code:

.. code-block:: python

    import pytest


    @pytest.fixture
    def httpserver_listen_address():
        return ("127.0.0.1", 8888)

New code:

.. code-block:: python

    import pytest


    @pytest.fixture(scope="session")
    def httpserver_listen_address():
        return ("127.0.0.1", 8888)


As this fixture is now defined with session scope, it will be called only once,
when it is first referenced by a test or by another fixture.

.. note::

   There were other, non-breaking changes introduced to 1.0.0. For details,
   please read the :ref:`changes`.
