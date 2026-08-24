"""Config loading and M2M OAuth with an on-disk token cache.

Why the cache matters: Alation invalidates the previous access token whenever a
new one is issued. Without caching, every process start kills the token held by
your last run (or your open browser session). We therefore reuse a cached token
until it is close to expiry, and only then mint a new one.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import requests

TOKEN_PATH = "/oauth/v2/token/"
_REFRESH_MARGIN_SEC = 300  # re-mint when under 5 minutes remain


def load_dotenv(path: str | Path = ".env") -> None:
    """Minimal .env loader. Unlike os.environ.setdefault, the file WINS over
    pre-existing shell vars — that surprise cost the masterclass script a day."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        os.environ[key.strip()] = val


def _flag(name: str, default: bool = False) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in {"1", "true", "yes", "y", "on"} if v else default


@dataclass
class Settings:
    base_url: str
    client_id: str
    client_secret: str
    access_token: str | None
    verify_ssl: bool
    token_cache: Path | None

    @classmethod
    def from_env(cls) -> "Settings":
        base = os.environ.get("ALATION_BASE_URL", "").strip().rstrip("/")
        if not base:
            raise RuntimeError("ALATION_BASE_URL is not set. Copy .env.example to .env.")

        raw_cache = os.environ.get("AGENTKIT_TOKEN_CACHE", "~/.alation/agent-kit-tokens.json").strip()
        cache = None if raw_cache.lower() == "none" else Path(raw_cache).expanduser()

        return cls(
            base_url=base,
            client_id=os.environ.get("ALATION_CLIENT_ID", "").strip(),
            client_secret=os.environ.get("ALATION_CLIENT_SECRET", "").strip(),
            access_token=os.environ.get("ALATION_ACCESS_TOKEN", "").strip() or None,
            verify_ssl=not _flag("SKIP_SSL_VERIFY"),
            token_cache=cache,
        )


class TokenProvider:
    """Client-credentials token with disk caching keyed by (base_url, client_id)."""

    def __init__(self, settings: Settings):
        self.s = settings
        if not (self.s.client_id and self.s.client_secret):
            raise RuntimeError(
                "ALATION_CLIENT_ID and ALATION_CLIENT_SECRET are required for Agent Studio. "
                "Ask a Server Admin to create an OAuth client at /admin/auth/."
            )
        self._key = f"{self.s.base_url}|{self.s.client_id}"

    # -- cache -------------------------------------------------------------
    def _read_cache(self) -> dict | None:
        if not self.s.token_cache or not self.s.token_cache.exists():
            return None
        try:
            entry = json.loads(self.s.token_cache.read_text()).get(self._key)
        except (json.JSONDecodeError, OSError):
            return None
        if entry and entry.get("expires_at", 0) - _REFRESH_MARGIN_SEC > time.time():
            return entry
        return None

    def _write_cache(self, token: str, expires_at: float) -> None:
        if not self.s.token_cache:
            return
        self.s.token_cache.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = json.loads(self.s.token_cache.read_text())
        except (json.JSONDecodeError, OSError, FileNotFoundError):
            data = {}
        data[self._key] = {"access_token": token, "expires_at": expires_at}
        self.s.token_cache.write_text(json.dumps(data, indent=2))
        os.chmod(self.s.token_cache, 0o600)

    # -- mint --------------------------------------------------------------
    def token(self, force_refresh: bool = False) -> str:
        if not force_refresh:
            cached = self._read_cache()
            if cached:
                return cached["access_token"]

        url = f"{self.s.base_url}{TOKEN_PATH}"
        body = {
            "grant_type": "client_credentials",
            "client_id": self.s.client_id,
            "client_secret": self.s.client_secret,
        }
        resp = requests.post(
            url,
            data=body,
            headers={"Accept": "application/json"},
            timeout=30,
            verify=self.s.verify_ssl,
        )
        if resp.status_code == 401:
            # Some deployments want HTTP basic instead of body credentials.
            resp = requests.post(
                url,
                data={"grant_type": "client_credentials"},
                auth=(self.s.client_id, self.s.client_secret),
                headers={"Accept": "application/json"},
                timeout=30,
                verify=self.s.verify_ssl,
            )
        if not resp.ok:
            raise RuntimeError(f"OAuth token request failed {resp.status_code}: {resp.text[:300]}")

        payload = resp.json()
        token = payload.get("access_token")
        if not token:
            raise RuntimeError(f"OAuth response had no access_token: {payload}")

        expires_in = int(payload.get("expires_in", 3600))
        self._write_cache(token, time.time() + expires_in)
        return token
