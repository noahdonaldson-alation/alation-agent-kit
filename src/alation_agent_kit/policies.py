"""Provision policy groups, business policies and CDE overlay standards.

Higher stakes than anything else in this kit: it writes governance objects into
a customer's catalog. So it is built around four rules.

1. **`plan` before `apply`.** Nothing is created until a human has seen the list.
2. **Namespace prefix on everything created**, so our objects stay visually and
   programmatically separable from the customer's own.
3. **Every created object recorded by ID** in the deployment state file.
4. **`destroy` deletes by recorded ID, never by name.** If it is not in the
   state file, we did not create it and we do not touch it.

Two API surfaces, and they differ in more than the path:

| Object | Endpoint | Auth | Notes |
|---|---|---|---|
| Policy group | `/integration/v2/policy_group/` | OAuth bearer | |
| Business policy | `/integration/v2/business_policies/` | OAuth bearer | array body, 202 + async job |
| Overlay standard | `/cde-service/integration/standard/` | **`CDEToken` header** | needs a source policy; inherits its name |

The CDE service uses a token from `POST /cde-service/integration/auth/` sent as
`CDEToken`, not the OAuth bearer. Alation's product docs claim there is no REST
API for standards; developer.alation.com documents one. Treat standards as
unverified until `verify_standards_api()` says otherwise.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from .client import AlationClient, AlationError
from .state import DeploymentState

POLICY_GROUP = "/integration/v2/policy_group/"
POLICIES = "/integration/v2/business_policies/"
CDE_AUTH = "/cde-service/integration/auth/"
STANDARDS = "/cde-service/integration/standard/"

# Reverse of creation order. A standard depends on its policy; a policy on its
# group. Teardown must run the other way.
KIND_ORDER = ["policy_group", "policy", "standard"]


@dataclass
class Action:
    verb: str          # create | skip | unsupported
    kind: str
    ref: str
    name: str
    reason: str = ""

    def __str__(self) -> str:
        mark = {"create": "+", "skip": "=", "unsupported": "!"}[self.verb]
        tail = f"   ({self.reason})" if self.reason else ""
        return f"  {mark} {self.kind:13} {self.name}{tail}"


class PolicyProvisioner:
    def __init__(self, client: AlationClient, state: DeploymentState,
                 prefix: str = ""):
        self.c = client
        self.state = state
        self.prefix = prefix if prefix is not None else state.prefix
        self._cde_token: str | None = None

    # -- naming ------------------------------------------------------------
    def prefixed(self, name: str) -> str:
        """Namespace everything we create, so it is separable from the
        customer's own objects and safe to remove."""
        return f"{self.prefix}{name}" if self.prefix else name

    # -- CDE service auth --------------------------------------------------
    def cde_token(self) -> str:
        """The CDE service wants its own token in a `CDEToken` header, obtained
        with the legacy API token — not the OAuth bearer used everywhere else."""
        if self._cde_token:
            return self._cde_token
        legacy = self.c.s.access_token
        if not legacy:
            raise RuntimeError(
                "CDE standards need ALATION_ACCESS_TOKEN (a legacy API token) in "
                ".env — the CDE service does not accept the OAuth bearer. Policies "
                "and groups work without it; run with --skip standards to proceed."
            )
        resp = self.c.request("POST", CDE_AUTH, None,
                              extra_headers={"Token": legacy})
        tok = resp if isinstance(resp, str) else (
            resp.get("token") or resp.get("access_token"))
        if not tok:
            raise RuntimeError(f"CDE auth returned no token: {resp}")
        self._cde_token = tok
        return tok

    def verify_standards_api(self) -> tuple[bool, str]:
        """Can standards be created here at all? Read-only probe, safe to run."""
        try:
            self.c.request("GET", f"{STANDARDS}?limit=1",
                           extra_headers={"CDEToken": self.cde_token()})
            return True, "reachable"
        except RuntimeError as err:
            return False, str(err)[:200]

    # -- read --------------------------------------------------------------
    def _list(self, path: str, extra_headers: dict | None = None) -> list[dict]:
        resp = self.c.request("GET", f"{path}?limit=500", extra_headers=extra_headers)
        if isinstance(resp, list):
            return resp
        for key in ("results", "items", "data", "policies", "standards"):
            if isinstance(resp, dict) and isinstance(resp.get(key), list):
                return resp[key]
        return []

    def find_by_title(self, path: str, title: str,
                      extra_headers: dict | None = None) -> dict | None:
        want = title.strip().lower()
        for row in self._list(path, extra_headers):
            for field in ("title", "name"):
                if (row.get(field) or "").strip().lower() == want:
                    return row
        return None

    # -- plan --------------------------------------------------------------
    def plan(self, spec: dict) -> list[Action]:
        """What would happen. Reads only.

        An object already recorded in state, or already present under the same
        prefixed title, is a skip — apply is idempotent and never duplicates.
        """
        actions: list[Action] = []

        group = spec.get("policy_group")
        if group:
            name = self.prefixed(group["title"])
            if self.state.id_for("policy_group", group["ref"]):
                actions.append(Action("skip", "policy_group", group["ref"], name,
                                      "already created by this kit"))
            elif self.find_by_title(POLICY_GROUP, name):
                actions.append(Action("skip", "policy_group", group["ref"], name,
                                      "exists on the instance"))
            else:
                actions.append(Action("create", "policy_group", group["ref"], name))

        for p in spec.get("policies") or []:
            name = self.prefixed(p["title"])
            if self.state.id_for("policy", p["ref"]):
                actions.append(Action("skip", "policy", p["ref"], name,
                                      "already created by this kit"))
            elif self.find_by_title(POLICIES, name):
                actions.append(Action("skip", "policy", p["ref"], name,
                                      "exists on the instance"))
            else:
                actions.append(Action("create", "policy", p["ref"], name))

        standards = spec.get("standards") or []
        if standards:
            ok, why = self.verify_standards_api()
            for s in standards:
                # A standard inherits its source policy's name, so it is not
                # separately titled.
                src = s.get("from_policy")
                name = self.prefixed(
                    next((p["title"] for p in spec.get("policies") or []
                          if p["ref"] == src), src or "?"))
                if not ok:
                    actions.append(Action("unsupported", "standard", s["ref"], name,
                                          f"CDE standards API unreachable: {why}"))
                elif self.state.id_for("standard", s["ref"]):
                    actions.append(Action("skip", "standard", s["ref"], name,
                                          "already created by this kit"))
                else:
                    actions.append(Action("create", "standard", s["ref"], name))
        return actions

    # -- apply -------------------------------------------------------------
    def apply(self, spec: dict, only: set[str] | None = None) -> list[str]:
        """Create what the plan says, in dependency order. Returns a log."""
        log: list[str] = []
        want = only or {"policy_group", "policy", "standard"}

        group_id = None
        group = spec.get("policy_group")
        if group and "policy_group" in want:
            group_id = self._ensure_group(group, log)

        policy_ids: dict[str, str] = {}
        if "policy" in want:
            for p in spec.get("policies") or []:
                pid = self._ensure_policy(p, group_id, log)
                if pid:
                    policy_ids[p["ref"]] = pid

        if "standard" in want and spec.get("standards"):
            ok, why = self.verify_standards_api()
            if not ok:
                log.append(f"  ! skipping standards — API unreachable: {why}")
                log.append("    Create them in the UI; they become a prerequisite.")
            else:
                for s in spec["standards"]:
                    self._ensure_standard(s, spec, policy_ids, log)
        return log

    def _ensure_group(self, group: dict, log: list[str]) -> str | None:
        name = self.prefixed(group["title"])
        existing_id = self.state.id_for("policy_group", group["ref"])
        if existing_id:
            log.append(f"  = policy_group {name} (already ours: {existing_id})")
            return existing_id
        found = self.find_by_title(POLICY_GROUP, name)
        if found:
            log.append(f"  = policy_group {name} (pre-existing, not recorded — "
                       f"will NOT be removed by destroy)")
            return str(found.get("id"))

        resp = self.c.post(POLICY_GROUP, json_body={
            "title": name, "description": group.get("description", "")})
        gid = _first_id(resp)
        if gid:
            self.state.record("policy_group", group["ref"], gid, name)
            log.append(f"  + policy_group {name} -> {gid}")
        else:
            log.append(f"  ! policy_group {name}: no id returned ({resp})")
        return gid

    def _ensure_policy(self, p: dict, group_id: str | None,
                       log: list[str]) -> str | None:
        name = self.prefixed(p["title"])
        existing_id = self.state.id_for("policy", p["ref"])
        if existing_id:
            log.append(f"  = policy {name} (already ours: {existing_id})")
            return existing_id
        found = self.find_by_title(POLICIES, name)
        if found:
            log.append(f"  = policy {name} (pre-existing, not recorded — "
                       f"will NOT be removed by destroy)")
            return str(found.get("id"))

        body: dict[str, Any] = {"title": name,
                                "description": p.get("description", "")}
        if group_id:
            body["policy_group_ids"] = [group_id]
        if p.get("fields"):
            body["fields"] = p["fields"]

        # The policy API takes an array and answers 202 with an async job.
        resp = self.c.post(POLICIES, json_body=[body])
        pid = _first_id(resp)
        if not pid:
            pid = self._await_by_title(POLICIES, name, log)
        if pid:
            self.state.record("policy", p["ref"], pid, name,
                              policy_group_id=group_id)
            log.append(f"  + policy {name} -> {pid}")
        else:
            log.append(f"  ! policy {name}: created but no id resolved ({resp})")
        return pid

    def _ensure_standard(self, s: dict, spec: dict,
                         policy_ids: dict[str, str], log: list[str]) -> str | None:
        src_ref = s.get("from_policy")
        src_id = policy_ids.get(src_ref) or self.state.id_for("policy", src_ref)
        title = next((p["title"] for p in spec.get("policies") or []
                      if p["ref"] == src_ref), None)
        if not src_id or not title:
            log.append(f"  ! standard {s['ref']}: source policy {src_ref!r} not "
                       f"available — a standard requires exactly one source policy")
            return None

        name = self.prefixed(title)   # inherited from the policy
        if self.state.id_for("standard", s["ref"]):
            log.append(f"  = standard {name} (already ours)")
            return self.state.id_for("standard", s["ref"])

        body = {
            "name": name,
            "purpose": s.get("purpose", ""),
            "scope": s.get("scope", ""),
            "derived_requirements": s.get("derived_requirements") or [],
            "options": {"allow_duplicates": False},
        }
        try:
            resp = self.c.post(STANDARDS, json_body=body,
                               extra_headers={"CDEToken": self.cde_token()})
        except AlationError as err:
            log.append(f"  ! standard {name}: {err}")
            return None
        sid = _first_id(resp) or (resp.get("key") if isinstance(resp, dict) else None)
        if sid:
            self.state.record("standard", s["ref"], sid, name,
                              source_policy_id=src_id)
            log.append(f"  + standard {name} -> {sid}")
        else:
            log.append(f"  ! standard {name}: no id/key returned ({resp})")
        return sid

    def _await_by_title(self, path: str, title: str, log: list[str],
                        attempts: int = 6, wait: float = 2.0) -> str | None:
        """The policy API is async, so the id may not come back on the response.
        Poll the list until the object appears."""
        for i in range(attempts):
            time.sleep(wait)
            found = self.find_by_title(path, title)
            if found and found.get("id"):
                return str(found["id"])
        log.append(f"    (waited {attempts * wait:.0f}s for {title!r} to appear)")
        return None

    # -- destroy -----------------------------------------------------------
    def destroy(self, dry_run: bool = True) -> list[str]:
        """Delete only what this kit recorded creating, in reverse dependency
        order, by ID. Never matches on name."""
        log: list[str] = []
        records = self.state.teardown_order(KIND_ORDER)
        if not records:
            return ["  nothing recorded — this kit has created nothing to remove"]

        for rec in records:
            kind, oid, name = rec["kind"], rec["id"], rec["name"]
            if dry_run:
                log.append(f"  - would delete {kind:13} {name} (id={oid})")
                continue
            try:
                if kind == "standard":
                    self.c.delete(f"{STANDARDS}{oid}/",
                                  extra_headers={"CDEToken": self.cde_token()})
                elif kind == "policy":
                    # array body, consistent with create
                    self.c.request("DELETE", POLICIES, json_body=[{"id": oid}])
                elif kind == "policy_group":
                    self.c.delete(f"{POLICY_GROUP}{oid}/")
                else:
                    log.append(f"  ? {kind} {name}: no delete rule, left in place")
                    continue
            except (AlationError, RuntimeError) as err:
                log.append(f"  ! {kind} {name} (id={oid}): {str(err)[:140]}")
                continue
            self.state.forget(kind, rec["ref"])
            log.append(f"  - deleted {kind:13} {name} (id={oid})")
        return log


def _first_id(resp: Any) -> str | None:
    """Pull an id out of a response that may be an object, a list, or a job."""
    if isinstance(resp, dict):
        for key in ("id", "policy_id", "group_id", "key"):
            if resp.get(key):
                return str(resp[key])
        for key in ("result", "data", "policies"):
            nested = resp.get(key)
            if nested:
                return _first_id(nested)
    if isinstance(resp, list) and resp:
        return _first_id(resp[0])
    return None
