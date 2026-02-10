from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    import sys
    from re import Pattern
    from types import TracebackType

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

    if sys.version_info >= (3, 12):
        from typing import Unpack
    else:
        from typing_extensions import Unpack

    from .httpserver import HTTPServer
    from .httpserver import RequestHandler
    from .httpserver import RequestMatcherKwargs
    from .httpserver import URIPattern


class BakedHTTPServer:
    """
    A proxy for :py:class:`HTTPServer` with pre-configured defaults for
    ``expect_request()`` and related methods.

    Created via :py:meth:`HTTPServer.bake`. Keyword arguments stored at bake
    time are merged with arguments provided at call time using last-wins
    semantics: if the same keyword appears in both, the call-time value is
    used.

    Any attribute not explicitly defined here is delegated to the wrapped
    :py:class:`HTTPServer`, so ``url_for()``, ``check_assertions()``, etc.
    work transparently.
    """

    def __init__(self, server: HTTPServer, **kwargs: Unpack[RequestMatcherKwargs]) -> None:
        self._server = server
        self._defaults = kwargs
        self._context_depth: int = 0
        self._started_server: bool = False

    def __enter__(self) -> Self:
        if self._context_depth == 0:
            self._started_server = not self._server.is_running()
            self._server.__enter__()
        self._context_depth += 1
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._context_depth -= 1
        if self._started_server and self._context_depth == 0:
            self._server.__exit__(exc_type, exc_value, traceback)
            self._started_server = False

    def __getattr__(self, name: str) -> Any:
        return getattr(self._server, name)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} defaults={self._defaults!r} server={self._server!r}>"

    def _merge_kwargs(self, kwargs: RequestMatcherKwargs) -> RequestMatcherKwargs:
        return self._defaults | kwargs

    def bake(self, **kwargs: Unpack[RequestMatcherKwargs]) -> Self:
        """
        Create a new :py:class:`BakedHTTPServer` by further layering defaults.

        The new proxy merges the current defaults with the new ``kwargs``.
        """
        return self.__class__(self._server, **self._merge_kwargs(kwargs))

    def expect_request(
        self,
        uri: str | URIPattern | Pattern[str],
        **kwargs: Unpack[RequestMatcherKwargs],
    ) -> RequestHandler:
        """Create and register a request handler, using baked defaults."""
        return self._server.expect_request(uri, **self._merge_kwargs(kwargs))

    def expect_oneshot_request(
        self,
        uri: str | URIPattern | Pattern[str],
        **kwargs: Unpack[RequestMatcherKwargs],
    ) -> RequestHandler:
        """Create and register a oneshot request handler, using baked defaults."""
        return self._server.expect_oneshot_request(uri, **self._merge_kwargs(kwargs))

    def expect_ordered_request(
        self,
        uri: str | URIPattern | Pattern[str],
        **kwargs: Unpack[RequestMatcherKwargs],
    ) -> RequestHandler:
        """Create and register an ordered request handler, using baked defaults."""
        return self._server.expect_ordered_request(uri, **self._merge_kwargs(kwargs))
