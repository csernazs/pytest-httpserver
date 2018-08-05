
import threading
import json

from werkzeug.wrappers import Request, Response
from werkzeug.serving import make_server

URI_DEFAULT = ""
METHOD_ALL = "__ALL"


class Error(Exception):
    pass


class NoHandlerError(Error):
    pass


class HTTPServerError(Error):
    pass


class RequestMatcher:
    def __init__(self, uri, method="GET", data=None, data_encoding="utf-8", headers=None, query_string=None):
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
        class_name = self.__class__.__name__
        retval = "<{} ".format(class_name)
        retval += "uri={uri!r} method={method!r} query_string={query_string!r} headers={headers!r} data={data!r}>".format_map(self.__dict__)
        return retval

    def match_data(self, request):
        if self.data is None:
            return True
        return request.data == self.data

    def difference(self, request: Request):
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

    def match(self, request: Request):
        difference = self.difference(request)
        return not difference


class RequestHandler:
    def __init__(self, matcher: RequestMatcher):
        self.matcher = matcher
        self.request_handler = None

    def respond(self, request):
        if self.request_handler is None:
            raise NoHandlerError("No handler found for request: {} {}".format(request.method, request.path))
        else:
            return self.request_handler(request)

    def respond_with_json(self, response_json, status=200, headers=None, content_type="application/json"):
        response_data = json.dumps(response_json, indent=4)
        self.respond_with_data(response_data, status, headers, content_type=content_type)

    def respond_with_data(self, response_data="", status=200, headers=None, mimetype=None, content_type=None):
        def handler(request):
            return Response(response_data, status, headers, mimetype, content_type)

        self.request_handler = handler

    def respond_with_response(self, response):
        self.request_handler = lambda request: response

    def respond_with_handler(self, func):
        self.request_handler = func


class RequestHandlerList(list):
    def match(self, request):
        for requesthandler in self:
            if requesthandler.matcher.match(request):
                return requesthandler
        return None


class HTTPServer:
    def __init__(self, host="localhost", port=4000):
        self.host = host
        self.port = port
        self.assertions = []
        self.server = None
        self.server_thread = None
        self.log = []
        self.ordered_handlers = []
        self.oneshot_handlers = RequestHandlerList()
        self.handlers = RequestHandlerList()

    def clear(self):
        self.clear_assertions()
        self.clear_log()
        self.clear_all_handlers()

    def clear_assertions(self):
        self.assertions = []

    def clear_log(self):
        self.log = []

    def clear_all_handlers(self):
        self.ordered_handlers = []
        self.oneshot_handlers = RequestHandlerList()
        self.handlers = RequestHandlerList()

    def url_for(self, suffix: str):
        if not suffix.startswith("/"):
            suffix = "/" + suffix

        return "http://{}:{}{}".format(self.host, self.port, suffix)

    def create_matcher(self, *args, **kwargs):
        return RequestMatcher(*args, **kwargs)

    def expect_oneshot_request(self, uri, method="GET", data=None, data_encoding="utf-8", headers=None, ordered=False):
        matcher = self.create_matcher(uri, method=method, data=data, data_encoding=data_encoding, headers=headers)
        request_handler = RequestHandler(matcher)
        if ordered:
            self.ordered_handlers.append(request_handler)
        else:
            self.oneshot_handlers.append(request_handler)

        return request_handler

    def expect_request(self, uri, method="GET", data=None, data_encoding="utf-8", headers=None) -> RequestHandler:
        matcher = self.create_matcher(uri, method=method, data=data, data_encoding=data_encoding, headers=headers)
        request_handler = RequestHandler(matcher)
        self.handlers.append(request_handler)
        return request_handler

    def thread_target(self):
        self.server.serve_forever()

    def is_running(self):
        return bool(self.server)

    def start(self):
        if self.is_running():
            raise HTTPServerError("Server is already running")

        self.server = make_server(self.host, self.port, self.application)
        self.server_thread = threading.Thread(target=self.thread_target)
        self.server_thread.start()

    def stop(self):
        if not self.is_running():
            raise HTTPServerError("Server is not running")
        self.server.shutdown()
        self.server_thread.join()
        self.server = None
        self.server_thread = None

    def add_assertion(self, obj):
        self.assertions.append(obj)

    def check_assertions(self):
        if self.assertions:
            raise AssertionError(self.assertions.pop(0))

    def format_matchers(self):
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
        text = "No handler found for request {!r}.\n".format(request)
        self.add_assertion(text + self.format_matchers())
        return Response("No handler found for this request", 500)

    def dispatch(self, request):
        if self.ordered_handlers:
            handler = self.ordered_handlers.pop()
            if not handler.matcher.match(request):
                return self.respond_nohandler(request)

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
        request.get_data()
        response = self.dispatch(request)
        self.log.append((request, response))
        return response

    def __enter__(self):
        if not self.is_running():
            self.start()
        return self

    def __exit__(self, *args, **kwargs):
        if self.is_running():
            self.stop()
