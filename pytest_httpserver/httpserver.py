
import threading
import json
from typing import Mapping, Optional, Union, Callable

from werkzeug.wrappers import Request, Response
from werkzeug.serving import make_server

URI_DEFAULT = ""
METHOD_ALL = "__ALL"


class Error(Exception):
    """
    Base class for all exception defined in this package.
    """

    pass


class NoHandlerError(Error):
    """
    Raised when a :py:class:`RequestHandler` has no registered method to serve the request.
    """

    pass


class HTTPServerError(Error):
    """
    Raised when there's a problem with HTTP server.
    """

    pass


class RequestMatcher:
    """
    Matcher object for the incoming request.

    It defines various parameters to match the incoming request.

    :param uri: URI of the request. This must be an absolute path starting with ``/``.
    :param method: HTTP method of the request. If not specified (or `METHOD_ALL`
        specified), all HTTP requests will match.
    :param data: payload of the HTTP request. This could be a string (utf-8 encoded
        by default, see `data_encoding`) or a bytes object.
    :param data_encoding: the encoding used for data parameter if data is a string.
    :param headers: dictionary of the headers of the request to be matched
    :param query_string: the http query string starting with ``?``, such as ``?username=user``
    """

    def __init__(
            self,
            uri: str,
            method: str = METHOD_ALL,
            data: Union[str, bytes, None] = None,
            data_encoding: str = "utf-8",
            headers: Optional[Mapping[str, str]] = None,
            query_string: Optional[str] = None):

        self.uri = uri
        self.method = method
        self.query_string = query_string

        if headers is None:
            self.headers = {}
        else:
            self.headers = headers

        if isinstance(data, str):
            data = data.encode(data_encoding)

        self.data = data

    def __repr__(self):
        """
        Returns the string representation of the object, with the known parameters.
        """

        class_name = self.__class__.__name__
        retval = "<{} ".format(class_name)
        retval += "uri={uri!r} method={method!r} query_string={query_string!r} headers={headers!r} data={data!r}>".format_map(self.__dict__)
        return retval

    def match_data(self, request: Request) -> bool:
        """
        Matches the data part of the request

        :param request: the HTTP request
        :return: `True` when the data is matched or no matching is required. `False` otherwise.
        """

        if self.data is None:
            return True
        return request.data == self.data

    def difference(self, request: Request) -> list:
        """
        Calculates the difference between the matcher and the request.

        Returns a list of fields where there's a difference between the request and the matcher.
        The returned list may have zero or more elements, each element is a three-element tuple
        containing the field name, the request value, and the matcher value.

        If zero-length list is returned, this means that there's no difference, so the request
        matches the fields set in the matcher object.
        """

        retval = []
        if self.uri != URI_DEFAULT and request.path != self.uri:
            retval.append(("uri", request.path, self.uri))

        if self.method != METHOD_ALL and self.method != request.method:
            retval.append(("method", request.method, self.method))

        if self.query_string is not None and self.query_string != request.query_string:
            retval.append(("query_string", request.query_string, self.query_string))

        request_headers = {}
        expected_headers = {}
        for key, value in self.headers.items():
            if request.headers.get(key) != value:
                request_headers[key] = request.headers.get(key)
                expected_headers[key] = value

        if request_headers and expected_headers:
            retval.append(("headers", request_headers, expected_headers))

        if not self.match_data(request):
            retval.append(("data", request.data, self.data))

        return retval

    def match(self, request: Request) -> bool:
        """
        Returns whether the request matches the parameters set in the matcher
        object or not. `True` value is returned when it matches, `False` otherwise.
        """

        difference = self.difference(request)
        return not difference


class RequestHandler:
    """
    Represents a response function and a :py:class:`RequestHandler` object.

    This class connects the matcher object with the function responsible for the response.

    :param matcher: the matcher object
    """

    def __init__(self, matcher: RequestMatcher):
        self.matcher = matcher
        self.request_handler = None

    def respond(self, request: Request) -> Response:
        """
        Calls the request handler registered for this object.

        If no request handler was specified previously, it raises
        :py:class:`NoHandlerError` exception.

        :param request: the incoming request object
        :return: the response object
        """

        if self.request_handler is None:
            raise NoHandlerError("No handler found for request: {} {}".format(request.method, request.path))
        else:
            return self.request_handler(request)

    def respond_with_json(
            self,
            response_json,
            status: int = 200,
            headers: Optional[Mapping[str, str]] = None,
            content_type: str = "application/json"):
        """
        Registers a respond handler function which responds with a serialized JSON object.

        :param response_json: a JSON-serializable python object
        :param status: the HTTP status of the response
        :param headers: the HTTP headers to be sent (excluding the Content-Type header)
        :param content_type: the content type header to be sent
        """
        response_data = json.dumps(response_json, indent=4)
        self.respond_with_data(response_data, status, headers, content_type=content_type)

    def respond_with_data(
            self,
            response_data: Union[str, bytes] = "",
            status: int = 200,
            headers: Optional[Mapping[str, str]] = None,
            mimetype: Optional[str] = None,
            content_type: Optional[str] = None):
        """
        Registers a respond handler function which responds raw data.

        For detailed description please see the :py:class:`Response` object as the
        parameters are analogue.

        :param response_data: a string or bytes object representing the body of the response
        :param status: the HTTP status of the response
        :param headers: the HTTP headers to be sent (excluding the Content-Type header)
        :param content_type: the content type header to be sent
        :param mimetype: the mime type of the request

        """
        def handler(request):  # pylint: disable=unused-argument
            return Response(response_data, status, headers, mimetype, content_type)

        self.request_handler = handler

    def respond_with_response(self, response: Response):
        """
        Registers a respond handler function which responds the specified response object.

        :param response: the response object which will be responded

        """
        self.request_handler = lambda request: response

    def respond_with_handler(self, func: Callable[[Request], Response]):
        """
        Registers the specified function as a responder.

        The function will receive the request object and must return with the response object.
        """
        self.request_handler = func


class RequestHandlerList(list):
    """
    Represents a list of :py:class:`RequestHandler` objects.

    """

    def match(self, request: Request) -> RequestHandler:
        """
        Returns the first request handler which matches the specified request. Otherwise, it returns `None`.
        """
        for requesthandler in self:
            if requesthandler.matcher.match(request):
                return requesthandler
        return None


class HTTPServer:   # pylint: disable=too-many-instance-attributes
    """
    Server instance which manages handlers to serve pre-defined requests.

    :param host: the host or IP where the server will listen
    :param port: the TCP port where the server will listen
    """

    def __init__(self, host="localhost", port=4000):
        """
        Initializes the instance.

        """
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.assertions = []
        self.log = []
        self.ordered_handlers = []
        self.oneshot_handlers = RequestHandlerList()
        self.handlers = RequestHandlerList()
        self.permanently_failed = False

    def clear(self):
        """
        Clears and resets the state attributes of the object.

        This method is useful when the object needs to be re-used but stopping the server is not feasible.

        """
        self.clear_assertions()
        self.clear_log()
        self.clear_all_handlers()
        self.permanently_failed = False

    def clear_assertions(self):
        """
        Clears the list of assertions
        """

        self.assertions = []

    def clear_log(self):
        """
        Clears the list of log entries
        """

        self.log = []

    def clear_all_handlers(self):
        """
        Clears all types of the handlers (ordered, oneshot, permanent)
        """

        self.ordered_handlers = []
        self.oneshot_handlers = RequestHandlerList()
        self.handlers = RequestHandlerList()

    def url_for(self, suffix: str):
        """
        Return an url for a given suffix.

        This basically means that it prepends the string ``http://$HOST:$PORT/`` to the `suffix` parameter
        (where $HOST and $PORT are the parameters given to the constructor).

        :param suffix: the suffix which will be added to the base url. It can start with ``/`` (slash) or
            not, the url will be the same.
        :return: the full url which refers to the server
        """

        if not suffix.startswith("/"):
            suffix = "/" + suffix

        return "http://{}:{}{}".format(self.host, self.port, suffix)

    def create_matcher(self, *args, **kwargs) -> RequestMatcher:
        """
        Creates a :py:class:`RequestMatcher` instance with the specified parameters.

        This method can be overridden if you want to use your own matcher.
        """

        return RequestMatcher(*args, **kwargs)

    def expect_oneshot_request(
            self,
            uri: str,
            method: str = METHOD_ALL,
            data: Union[str, bytes, None] = None,
            data_encoding: str = "utf-8",
            headers: Optional[Mapping[str, str]] = None,
            query_string: Optional[str] = None,
            *,
            ordered=False) -> RequestHandler:
        """
        Create and register a oneshot request handler.

        This handler can be only used once. Once the server serves a response for this handler,
        the handler will be dropped.

        Ordered handler (when `ordered` parameter is `True`) also determines the
        order of the requests to be served. For example if there are two ordered handlers
        registered, the first request must hit the first handler, and the second request must hit the
        second one, and not vica versa.

        If one or more ordered handler defined, those must be exhausted first.

        :param uri: URI of the request. This must be an absolute path starting with ``/``.
        :param method: HTTP method of the request. If not specified (or `METHOD_ALL`
            specified), all HTTP requests will match.
        :param data: payload of the HTTP request. This could be a string (utf-8 encoded
            by default, see `data_encoding`) or a bytes object.
        :param data_encoding: the encoding used for data parameter if data is a string.
        :param headers: dictionary of the headers of the request to be matched
        :param query_string: the http query string starting with ``?``, such as ``?username=user``
        :param ordered: specifies whether to create an ordered handler or not. See above for details.

        :return: Created and register :py:class:`RequestHandler`.
        """

        matcher = self.create_matcher(uri, method=method, data=data, data_encoding=data_encoding, headers=headers, query_string=query_string)
        request_handler = RequestHandler(matcher)
        if ordered:
            self.ordered_handlers.append(request_handler)
        else:
            self.oneshot_handlers.append(request_handler)

        return request_handler

    def expect_request(
            self,
            uri: str,
            method: str = METHOD_ALL,
            data: Union[str, bytes, None] = None,
            data_encoding: str = "utf-8",
            headers: Optional[Mapping[str, str]] = None,
            query_string: Optional[str] = None) -> RequestHandler:
        """
        Create and register a permanent request handler.

        This handler can be used as many times as the request matches it, but ordered handlers
        have higher priority so if there's one or more ordered handler registered, those must be used first.

        :param uri: URI of the request. This must be an absolute path starting with ``/``.
        :param method: HTTP method of the request. If not specified (or `METHOD_ALL`
            specified), all HTTP requests will match.
        :param data: payload of the HTTP request. This could be a string (utf-8 encoded
            by default, see `data_encoding`) or a bytes object.
        :param data_encoding: the encoding used for data parameter if data is a string.
        :param headers: dictionary of the headers of the request to be matched
        :param ordered: specifies whether to create an ordered handler or not. See above for details.

        :return: Created and register :py:class:`RequestHandler`.
        """

        matcher = self.create_matcher(uri, method=method, data=data, data_encoding=data_encoding, headers=headers, query_string=query_string)
        request_handler = RequestHandler(matcher)
        self.handlers.append(request_handler)
        return request_handler

    def thread_target(self):
        """
        This method serves as a thread target when the server is started.

        This should not be called directly, but can be overriden to tailor it to your needs.
        """

        self.server.serve_forever()

    def is_running(self) -> bool:
        """
        Returns `True` when the server is running, otherwise `False`.
        """
        return bool(self.server)

    def start(self):
        """
        Start the server in a thread.

        This method returns immediately (e.g. does not block), and it's the caller's
        responsibility to stop the server (by calling :py:meth:`stop`) when it is no longer needed).

        If the sever is not stopped by the caller and execution reaches the end, the
        program needs to be terminated by Ctrl+C or by signal as it will not terminate until
        the thred is stopped.

        If the sever is already running :py:class`HTTPServerError` will be raised. If you are
        unsure, call :py:meth`is_running` first.

        There's a context interface of this class which stops the server when the context block ends.
        """
        if self.is_running():
            raise HTTPServerError("Server is already running")

        self.server = make_server(self.host, self.port, self.application)
        self.server_thread = threading.Thread(target=self.thread_target)
        self.server_thread.start()

    def stop(self):
        """
        Stop the running server.

        Notifies the server thread about the intention of the stopping, and the thread will
        terminate itself. This needs about 0.5 seconds in worst case.

        Only a running server can be stopped. If the sever is not runnig, :py:class`HTTPServerError`
        will be raised.
        """
        if not self.is_running():
            raise HTTPServerError("Server is not running")
        self.server.shutdown()
        self.server_thread.join()
        self.server = None
        self.server_thread = None

    def add_assertion(self, obj):
        """
        Add a new assertion

        Assertions can be added here, and when :py:meth:`check_assertions` is called,
        it will raise AssertionError for pytest with the object specified here.

        :param obj: An object which will be passed to AssertionError.
        """
        self.assertions.append(obj)

    def check_assertions(self):
        """
        Raise AssertionError when at least one assertion added

        The first assertion added by :py:meth:`add_assertion` will be raised and
        it will be removed from the list.

        This method can be useful to get some insights into the errors happened in
        the sever, and to have a proper error reporting in pytest.
        """

        if self.assertions:
            raise AssertionError(self.assertions.pop(0))

    def format_matchers(self) -> str:
        """
        Return a string representation of the matchers

        This method returns a human-readable string representation of the matchers
        registered. You can observe which requests will be served, etc.

        This method is primairly used when reporting errors.
        """
        def format_handlers(handlers):
            if handlers:
                return ["    {!r}".format(handler.matcher) for handler in handlers]
            else:
                return ["    none"]

        lines = []
        lines.append("Ordered matchers:")
        lines.extend(format_handlers(self.ordered_handlers))
        lines.append("")
        lines.append("Oneshot matchers:")
        lines.extend(format_handlers(self.oneshot_handlers))
        lines.append("")
        lines.append("Persistent matchers:")
        lines.extend(format_handlers(self.handlers))

        return "\n".join(lines)

    def respond_nohandler(self, request: Request):
        """
        Add a 'no handler' assertion.

        This method is called when the server wasn't able to find any handler to serve the request.
        As the result, there's an assertion added (which can be raised by :py:meth:`check_assertions`).

        """
        text = "No handler found for request {!r}.\n".format(request)
        self.add_assertion(text + self.format_matchers())
        return Response("No handler found for this request", 500)

    def respond_permanent_failure(self):
        """
        Add a 'permanent failure' assertion.

        This assertion means that no further requests will be handled. This is the resuld of missing
        an ordered matcher.

        """

        self.add_assertion("All requests will be permanently failed due failed ordered handler")
        return Response("No handler found for this request", 500)

    def dispatch(self, request: Request) -> Response:
        """
        Dispatch a request to the appropriate request handler.

        This method tries to find the request handler whose matcher matches the request, and
        then calls it in order to serve the request.

        First, the request is checked for the ordered matchers. If there's an ordered matcher,
        it must match the request, otherwise the server will be put into a `permanent failure`
        mode in which it makes all request failed - this is the intended way of working of ordered
        matchers.

        Then oneshot handlers, and the permanent handlers are looked up.

        :param request: the request object from the werkzeug library
        :return: the response object what the handler responded, or a response which contains the error
        """

        if self.permanently_failed:
            return self.respond_permanent_failure()

        handler = None
        if self.ordered_handlers:
            handler = self.ordered_handlers[0]
            if not handler.matcher.match(request):
                self.permanently_failed = True
                response = self.respond_nohandler(request)
                return response

            self.ordered_handlers.pop(0)

        if not handler:
            handler = self.oneshot_handlers.match(request)
            if handler:
                self.oneshot_handlers.remove(handler)
            else:
                handler = self.handlers.match(request)

            if not handler:
                return self.respond_nohandler(request)

        response = handler.respond(request)

        if response is None:
            response = Response("")
        if isinstance(response, str):
            response = Response(response)

        return response

    @Request.application
    def application(self, request: Request):
        """
        Entry point of werkzeug.

        This method is called for each request, and it then calls the undecorated
        :py:meth:`dispatch` method to serve the request.

        :param request: the request object from the werkzeug library
        :return: the response object what the dispatch returned
        """
        request.get_data()
        response = self.dispatch(request)
        self.log.append((request, response))
        return response

    def __enter__(self):
        """
        Provide the context API

        It starts the server in a thread if the server is not already running.
        """

        if not self.is_running():
            self.start()
        return self

    def __exit__(self, *args, **kwargs):
        """
        Provide the context API

        It stops the server if the server is running.
        Please note that depending on the internal things of werkzeug, it may take 0.5 seconds.
        """
        if self.is_running():
            self.stop()
