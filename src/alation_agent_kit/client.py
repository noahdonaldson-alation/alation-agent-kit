"""Thin HTTP client for the Alation AI API (Agent Studio) and catalog APIs.

Paths are passed in full so both surfaces are reachable from one client:
    AI_V1 + "/config/agent"                 -> Agent Studio
    "/integration/v2/business_policies/"    -> catalog
"""

from __future__ import annotations

import json
from typing import Any

import requests

from .auth import Settings, TokenProvider

AI_V1 = "/ai/api/v1"


class AlationError(RuntimeError):
    def __init__(self, method: str, url: str, status: int, body: Any):
        self.status = status
        self.body = body
        snippet = body if isinstance(body, str) else json.dumps(body, default=str)
        super().__init__(f"{method} {url} -> {status}: {snippet[:500]}")


class AlationClient:
    def __init__(self, settings: Settings | None = None):
        self.s = settings or Settings.from_env()
        self._tokens = TokenProvider(self.s)
        self._session = requests.Session()
        self._session.verify = self.s.verify_ssl

    # -- plumbing ----------------------------------------------------------
    def _headers(self, extra: dict | None = None) -> dict:
        h = {
            "Authorization": f"Bearer {self._tokens.token()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if extra:
            h.update(extra)
        return h

    def request(
        self,
        method: str,
        path: str,
        json_body: Any = None,
        params: dict | None = None,
        timeout: int = 120,
        extra_headers: dict | None = None,
        retry_auth: bool = True,
    ) -> Any:
        url = f"{self.s.base_url}{path}"
        resp = self._session.request(
            method,
            url,
            json=json_body,
            params=params,
            headers=self._headers(extra_headers),
            timeout=timeout,
        )

        # A cached token can be invalidated out from under us (another process
        # minted one). Force-refresh once before giving up.
        if resp.status_code == 401 and retry_auth:
            self._tokens.token(force_refresh=True)
            return self.request(
                method, path, json_body, params, timeout, extra_headers, retry_auth=False
            )

        try:
            payload = resp.json() if resp.text else {}
        except ValueError:
            payload = resp.text

        if not resp.ok:
            raise AlationError(method, url, resp.status_code, payload)
        return payload

    # -- streaming ---------------------------------------------------------
    def stream_lines(self, path: str, json_body: Any = None, timeout: int = 600):
        """POST and yield raw SSE lines.

        Used for agent invocation. The task-polling alternative is unusable:
        `GET /task/{id}` returns 404 once the task succeeds ("Successfully
        completed tasks are deleted"), so a fast agent finishes before the first
        poll and looks like a failure.
        """
        url = f"{self.s.base_url}{path}"
        headers = self._headers({"Accept": "text/event-stream"})
        with self._session.post(
            url, json=json_body, headers=headers, timeout=timeout, stream=True
        ) as resp:
            if resp.status_code == 401:
                self._tokens.token(force_refresh=True)
                headers = self._headers({"Accept": "text/event-stream"})
                with self._session.post(
                    url, json=json_body, headers=headers, timeout=timeout, stream=True
                ) as retry:
                    if not retry.ok:
                        raise AlationError("POST", url, retry.status_code, retry.text[:500])
                    yield from retry.iter_lines(decode_unicode=True)
                    return
            if not resp.ok:
                raise AlationError("POST", url, resp.status_code, resp.text[:500])
            # text/event-stream carries no charset, so requests falls back to
            # ISO-8859-1 and every multi-byte character arrives double-encoded:
            # "¶" becomes "Â¶", "—" becomes "â\x80\x94". That silently corrupts
            # the paragraph citations this output depends on. Force UTF-8.
            resp.encoding = "utf-8"
            yield from resp.iter_lines(decode_unicode=True)

    # -- convenience -------------------------------------------------------
    def get(self, path: str, **kw) -> Any:
        return self.request("GET", path, **kw)

    def post(self, path: str, json_body: Any = None, **kw) -> Any:
        return self.request("POST", path, json_body=json_body, **kw)

    def patch(self, path: str, json_body: Any = None, **kw) -> Any:
        return self.request("PATCH", path, json_body=json_body, **kw)

    def put(self, path: str, json_body: Any = None, **kw) -> Any:
        return self.request("PUT", path, json_body=json_body, **kw)

    def delete(self, path: str, **kw) -> Any:
        return self.request("DELETE", path, **kw)
