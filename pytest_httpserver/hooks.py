import os
import time
from typing import Callable

from werkzeug import Request
from werkzeug import Response


class Chain:
    def __init__(self, *args: Callable[[Request, Response], Response]):
        self._hooks = args

    def __call__(self, request: Request, response: Response) -> Response:
        for hook in self._hooks:
            response = hook(request, response)
        return response


class Delay:
    def __init__(self, seconds: float):
        self._seconds = seconds

    def _sleep(self):
        time.sleep(self._seconds)

    def __call__(self, _request: Request, response: Response) -> Response:
        self._sleep()
        return response


class Garbage:
    def __init__(self, size: int = 16 * 1024):
        self._size = size

    def _get_garbage_bytes(self) -> bytes:
        return os.urandom(self._size)

    def __call__(self, _request: Request, response: Response) -> Response:
        garbage = self._get_garbage_bytes()
        response.set_data(garbage + response.get_data())
        return response
