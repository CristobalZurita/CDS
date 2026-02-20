from __future__ import annotations

from typing import Any, Mapping
import threading

import anyio
import httpx


class CompatTestClient:
    """
    Minimal TestClient compatible wrapper for environments where
    starlette/fastapi TestClient blocks on AnyIO blocking portal.
    """

    def __init__(
        self,
        app: Any,
        base_url: str = "http://testserver",
        raise_server_exceptions: bool = True,
        root_path: str = "",
        backend: str = "asyncio",
        backend_options: Mapping[str, Any] | None = None,
        cookies: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        follow_redirects: bool = True,
        **_: Any,
    ) -> None:
        self.app = app
        self.base_url = base_url
        self.raise_server_exceptions = raise_server_exceptions
        self.root_path = root_path
        self.backend = backend
        self.backend_options = dict(backend_options or {})
        self._cookies = dict(cookies or {})
        self._headers = dict(headers or {})
        self.follow_redirects = follow_redirects
        self.client = ("127.0.0.1", 123)

    def __enter__(self) -> "CompatTestClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def close(self) -> None:
        return None

    def _merge_headers(self, headers: Mapping[str, str] | None) -> dict[str, str]:
        merged = dict(self._headers)
        if headers:
            merged.update(headers)
        return merged

    def _merge_cookies(self, cookies: Mapping[str, Any] | None) -> dict[str, Any]:
        merged = dict(self._cookies)
        if cookies:
            merged.update(cookies)
        return merged

    async def _request_async(self, method: str, url: str, request_kwargs: dict[str, Any]) -> httpx.Response:
        request_headers = self._merge_headers(request_kwargs.pop("headers", None))
        request_cookies = self._merge_cookies(request_kwargs.pop("cookies", None))

        transport = httpx.ASGITransport(
            app=self.app,
            raise_app_exceptions=self.raise_server_exceptions,
            root_path=self.root_path,
            client=self.client,
        )

        async with httpx.AsyncClient(
            transport=transport,
            base_url=self.base_url,
            headers=request_headers,
            cookies=request_cookies,
            follow_redirects=self.follow_redirects,
        ) as async_client:
            return await async_client.request(method=method, url=url, **request_kwargs)

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        explicit_timeout = "timeout" in kwargs
        max_attempts = 1 if explicit_timeout else 2
        last_exc: Exception | None = None

        for attempt in range(max_attempts):
            request_kwargs = dict(kwargs)
            if "timeout" not in request_kwargs:
                request_kwargs["timeout"] = 20.0

            timeout_seconds = float(request_kwargs.get("timeout") or 20.0)
            outcome: dict[str, Any] = {}

            def _run_request() -> None:
                try:
                    outcome["response"] = anyio.run(self._request_async, method, url, request_kwargs)
                except Exception as exc:
                    outcome["error"] = exc

            thread = threading.Thread(target=_run_request, daemon=True)
            thread.start()
            thread.join(timeout_seconds)

            if thread.is_alive():
                last_exc = httpx.TimeoutException(f"Test request timeout after {timeout_seconds}s: {method} {url}")
                if attempt + 1 >= max_attempts:
                    raise last_exc
                continue

            try:
                if "error" in outcome:
                    raise outcome["error"]
                return outcome["response"]
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt + 1 >= max_attempts:
                    raise
                continue

        assert last_exc is not None
        raise last_exc

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("DELETE", url, **kwargs)

    def options(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("OPTIONS", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("HEAD", url, **kwargs)
    __test__ = False
