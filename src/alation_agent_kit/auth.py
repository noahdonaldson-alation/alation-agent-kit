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
    pre-existing shell vars, which is the opposite of the usual setdefault trap."""
    p = Path(path)
    if not p.exists():
        return
    seen: set[str] = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        # Last assignment wins, which means a duplicated key silently overrides
        # an earlier one — including a filled value being blanked by a leftover
        # empty line further down. Say so rather than letting it puzzle someone.
        if key in seen:
            import warnings

            warnings.warn(
                f"{p}: {key} is set more than once; the last assignment wins "
                f"({'empty' if not val else 'non-empty'}). Delete the duplicate.",
                stacklevel=2,
            )
        seen.add(key)
        os.environ[key] = val


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
    refresh_token: str | None = None
    user_id: int | None = None
    # Send the legacy TOKEN header on /integration/ paths. Off by default: the
    # OAuth bearer works there, and adding a TOKEN switches authentication to
    # that token's user, which is a way to break a working call. Needed on
    # instances that cannot issue OAuth clients (documented Cloud-only).
    force_catalog_token: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        base = os.environ.get("ALATION_BASE_URL", "").strip().rstrip("/")
        if not base:
            raise RuntimeError("ALATION_BASE_URL is not set. Copy .env.example to .env.")

        raw_cache = os.environ.get("AGENTKIT_TOKEN_CACHE", "~/.alation/agent-kit-tokens.json").strip()
        cache = None if raw_cache.lower() == "none" else Path(raw_cache).expanduser()

        # A non-numeric user id used to fall back to None silently, which made a
        # configured refresh token look like no credential at all — the failure
        # surfaced three layers away as "set ALATION_REFRESH_TOKEN". Fail here.
        uid = os.environ.get("ALATION_USER_ID", "").strip()
        if uid and not uid.isdigit():
            raise RuntimeError(
                f"ALATION_USER_ID must be the numeric Alation user id, got "
                f"{uid[:8]}… ({len(uid)} chars). It is not the token, the token "
                f"name, or a UUID. Find it in the createRefreshToken response, or "
                f"in the UI URL when viewing your own profile."
            )
        return cls(
            base_url=base,
            client_id=os.environ.get("ALATION_CLIENT_ID", "").strip(),
            client_secret=os.environ.get("ALATION_CLIENT_SECRET", "").strip(),
            access_token=os.environ.get("ALATION_ACCESS_TOKEN", "").strip() or None,
            verify_ssl=not _flag("SKIP_SSL_VERIFY"),
            token_cache=cache,
            refresh_token=os.environ.get("ALATION_REFRESH_TOKEN", "").strip() or None,
            user_id=int(uid) if uid.isdigit() else None,
            force_catalog_token=_flag("ALATION_FORCE_CATALOG_TOKEN"),
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


CATALOG_TOKEN_PATH = "/integration/v1/createAPIAccessToken/"
VALIDATE_REFRESH_PATH = "/integration/v1/validateRefreshToken/"
CREATE_REFRESH_PATH = "/integration/v1/createRefreshToken/"


def create_refresh_token(base_url: str, username: str, password: str,
                         name: str = "alation-agent-kit",
                         verify_ssl: bool = True) -> dict:
    """Mint a refresh token from username + password.

    Returns the response dict, which carries both `refresh_token` and `user_id`
    — the only documented way to learn your numeric user id without admin
    rights, and it removes the copy-paste step entirely.

    **SSO users have no password and will get a 401 here**; they must create the
    token in the UI (Account Settings -> Authentication).

    Note this REVOKES any previous refresh token for this user, so anything
    else using one will stop working.
    """
    resp = requests.post(
        f"{base_url.rstrip('/')}{CREATE_REFRESH_PATH}",
        json={"username": username, "password": password, "name": name},
        headers={"Accept": "application/json"},
        timeout=30,
        verify=verify_ssl,
    )
    try:
        body = resp.json()
    except ValueError:
        body = {"raw": resp.text[:300]}
    if not resp.ok:
        hint = ""
        if resp.status_code in (401, 403):
            hint = (" — if you sign in through SSO you have no password to send; "
                    "create the token in the UI instead: Account Settings -> "
                    "Authentication -> Create Refresh Token.")
        raise RuntimeError(
            f"createRefreshToken failed ({resp.status_code}): {body}{hint}"
        )
    return body


def _parse_expiry(value: str | None) -> float | None:
    """`token_expires_at` is an absolute ISO-8601 instant, not a duration."""
    if not value:
        return None
    try:
        from datetime import datetime, timezone

        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except (ValueError, TypeError):
        return None


class CatalogTokenProvider:
    """The legacy `TOKEN` header the catalog APIs want.

    The `/integration/v1/...` catalog endpoints answer the OAuth bearer with
    `403 "Authentication credentials were not provided"`. They want an Alation
    **API access token** in a `TOKEN` header (documented uppercase).

    Access tokens live ~24h, so pasting one into `.env` means it stops working
    tomorrow. Better: put the long-lived **refresh token** in `.env` plus your
    numeric user id, and mint access tokens from it.

    Getting a refresh token: `POST /integration/v1/createRefreshToken/` with
    `{username, password, name}`, whose response carries both `refresh_token`
    and the `user_id` you need. **SSO users have no password and cannot use
    that endpoint** — create the token in the UI instead, under Account
    Settings → Authentication → Create Refresh Token.

    Verified against developer.alation.com/dev/docs/authentication-into-alation-apis:
    request body is `{refresh_token, user_id}`; the response field is
    `api_access_token`, and `token_expires_at` is an **absolute ISO-8601
    instant**, not a relative `expires_in`.

    Caching is not just an optimisation. Creating an access token is documented
    as revoking the other active tokens minted from the same refresh token, so
    minting per process would knock out your own previous run.

    Cached to disk alongside the OAuth token, keyed separately so the two never
    collide.
    """

    def __init__(self, settings: Settings):
        self.s = settings
        self._key = f"catalog|{settings.base_url}|{settings.user_id}"

    def token(self, force_refresh: bool = False) -> str | None:
        """The legacy access token, minted and cached as needed.

        `force_refresh` exists because a cached token can be revoked out from
        under us: minting an access token revokes the others from the same
        refresh token, so any other process — another shell, the UI, a colleague
        sharing the account — silently invalidates ours while the cache still
        looks valid. The cure is to re-mint on rejection rather than to trust
        the expiry we recorded.
        """
        # An explicitly supplied access token wins — useful for a one-off.
        if self.s.access_token:
            return self.s.access_token
        if not (self.s.refresh_token and self.s.user_id):
            return None

        if not force_refresh:
            cached = self._read_cache()
            if cached:
                return cached

        resp = requests.post(
            f"{self.s.base_url}{CATALOG_TOKEN_PATH}",
            json={"refresh_token": self.s.refresh_token, "user_id": self.s.user_id},
            headers={"Accept": "application/json"},
            timeout=30,
            verify=self.s.verify_ssl,
        )
        if not resp.ok:
            # "Refresh token provided is invalid" is validated as a PAIR: a good
            # token with the wrong user_id reports the token as invalid. So the
            # user id is the first thing to suspect, not the token.
            hint = (
                f"ALATION_USER_ID is currently {self.s.user_id}. Alation validates "
                f"the token and the user id together, so a mismatched id reports "
                f"the TOKEN as invalid. Confirm the id with "
                f"`agentkit userid <your-email>` before replacing the token.\n"
                f"If the id is right, the refresh token has expired or been "
                f"revoked — minting a new refresh token invalidates the old one. "
                f"Create a fresh one: Alation UI → Account Settings → "
                f"Authentication. Also check you did not paste an *access* token "
                f"into ALATION_REFRESH_TOKEN; they look alike."
                if resp.status_code == 401 else
                "Check ALATION_REFRESH_TOKEN and ALATION_USER_ID in .env."
            )
            raise RuntimeError(
                f"Could not mint a catalog API token ({resp.status_code}): "
                f"{resp.text[:200]}\n{hint}"
            )
        payload = resp.json()
        tok = payload.get("api_access_token") or payload.get("token")
        if not tok:
            raise RuntimeError(f"Token response had no api_access_token: {payload}")
        status = str(payload.get("token_status", "")).lower()
        if status and status != "active":
            raise RuntimeError(
                f"Minted catalog token has status {payload.get('token_status')!r}. "
                f"The refresh token may be expired or revoked — create a new one."
            )

        # token_expires_at is absolute ISO-8601. Fall back to a conservative
        # hour if it is missing or unparseable rather than trusting a default.
        expires_at = _parse_expiry(payload.get("token_expires_at")) or (time.time() + 3600)
        self._write_cache(tok, expires_at)
        return tok

    def fingerprint(self) -> str:
        """Non-secret shape of the configured refresh token.

        Length alone settles "did .env actually get updated?" — the tokens
        Alation issues here are 87 chars, and a 43-char value is an *access*
        token in the wrong slot. Printing four leading characters is enough to
        tell two tokens apart without exposing either.
        """
        t = self.s.refresh_token
        if not t:
            return "not set"
        return f"{len(t)} chars, starts {t[:4]}…"

    def diagnose(self) -> dict:
        """Test the refresh token by doing the thing we actually need with it.

        An earlier version gated on `validateRefreshToken`, whose request shape
        was never verified against docs — and it returned "invalid or malformed"
        for a token Alation had just issued and reported ACTIVE. A probe that
        can fail while the real call succeeds is worse than no probe, so the
        authority here is `createAPIAccessToken`; validate is advisory only.

        Never raises. Keys: ok, status, detail, fingerprint.
        """
        out = {"fingerprint": self.fingerprint()}
        if not self.s.refresh_token:
            return {**out, "ok": False, "status": "absent",
                    "detail": "ALATION_REFRESH_TOKEN is not set"}
        if self.s.user_id is None:
            return {**out, "ok": False, "status": "absent",
                    "detail": "ALATION_USER_ID is not set (must be numeric)"}

        try:
            resp = requests.post(
                f"{self.s.base_url}{CATALOG_TOKEN_PATH}",
                json={"refresh_token": self.s.refresh_token,
                      "user_id": self.s.user_id},
                headers={"Accept": "application/json"},
                timeout=30,
                verify=self.s.verify_ssl,
            )
        except requests.RequestException as exc:
            return {**out, "ok": False, "status": "unreachable",
                    "detail": str(exc)[:200]}

        try:
            body = resp.json()
        except ValueError:
            body = {"raw": resp.text[:200]}

        if resp.ok and (body.get("api_access_token") or body.get("token")):
            # Cache it: this WAS a real mint, and minting again would revoke it.
            tok = body.get("api_access_token") or body["token"]
            self._write_cache(
                tok,
                _parse_expiry(body.get("token_expires_at")) or (time.time() + 3600),
            )
            return {**out, "ok": True, "status": "active",
                    "detail": {"token_expires_at": body.get("token_expires_at")}}

        return {**out, "ok": False, "status": f"http {resp.status_code}",
                "detail": body}

    def _read_cache(self) -> str | None:
        if not self.s.token_cache or not self.s.token_cache.exists():
            return None
        try:
            entry = json.loads(self.s.token_cache.read_text()).get(self._key)
        except (json.JSONDecodeError, OSError):
            return None
        if entry and entry.get("expires_at", 0) - _REFRESH_MARGIN_SEC > time.time():
            return entry["access_token"]
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
