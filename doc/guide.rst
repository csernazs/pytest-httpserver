
User's Guide
============

Starting and stopping the server
--------------------------------
The server can be started by instatiating it and then calling the
:py:meth:`pytest_httpserver.HTTPServer.start` method. This will start the server in a separate
thread, so you will need to make sure that the :py:meth:`pytest_httpserver.HTTPServer.stop` method
is called before your code exits.

A free TCP port needs to be specified when instantiating the server, where no other daemon is listening.

If you are using the pytest plugin it is done automatically by the plugin. Possibility to change
the TCP port in this case is TBD.

