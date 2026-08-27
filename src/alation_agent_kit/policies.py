"""Provision business policies and CDE overlay standards.

Higher stakes than anything else in this kit: it writes governance objects into
a customer's catalog. Four rules:

1. **`plan` before `apply`.** Nothing is created until a human has seen the list.
2. **Namespace prefix on everything created.** Not cosmetic — see the id-recovery
   note below. It is how we know which policy is ours.
3. **Every created object recorded by ID** in the deployment state file.
4. **`destroy` deletes by recorded ID, never by name.** If it is not in the state
   file, we did not create it and we do not touch it.

## What the API actually looks like

Verified against developer.alation.com and Allie-SDK's working client (the docs
and the SDK disagree in one place; the SDK wins — see `_GROUP_PATHS`).

| Object | Endpoint | Notes |
|---|---|---|
| Policy group | `GET /integration/v1/policy_group` | **GET only. No create.** |
| Business policy | `GET/POST/PUT/DELETE /integration/v1/business_policies/` | bulk; body is a bare array |
| Overlay standard | `POST /cde-service/integration/standard/` | `CDEToken` header, not the bearer |

**It is v1, not v2.** No `v2` policy path exists on any version; a `v2` request
404s with an HTML error page from the Django router.

**Policy groups cannot be created.** So a group is a declared prerequisite:
we resolve its title to an id and fail with an instruction if it is absent.
Association is then set from the policy side via `policy_group_ids`.

**Policy create is async and does not return ids.** `POST` answers 202 with
`{"task": {"id": N, ...}}`; polling `GET /api/v1/bulk_metadata/job/?id=N` returns
prose only — *"Successfully processed 2 items"* — with no object ids. Documents
and terms return ids; policies do not. So ids are recovered by searching for the
namespaced title afterwards, which is why the prefix matters: without it we
cannot tell our "Risk Data Completeness" from one the customer already had.

**PUT is not shaped like POST.** On update, `id` is required and
`policy_group_ids` becomes `{"add": [], "remove": [], "replace": []}` rather than
a flat list. We do not update policies today; if that changes, this is the trap.

**Omit empty keys.** The bulk endpoints reject a body carrying nulls or empty
values, so `_clean()` strips them.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from .client import AlationClient, AlationError
from .state import DeploymentState

# Allie-SDK carries an explicit comment that this path must NOT have a trailing
# slash, dated Jan 2024, while the OpenAPI spec shows one. Working code beats the
# spec, but the comment may be stale — so try both and remember which worked.
_GROUP_PATHS = ("/integration/v1/policy_group", "/integration/v1/policy_group/")
POLICIES = "/integration/v1/business_policies/"
JOB = "/api/v1/bulk_metadata/job/"
CDE_AUTH = "/cde-service/integration/auth/"
STANDARDS = "/cde-service/integration/standard/"

KIND_ORDER = ["policy", "standard"]   # reverse of creation order for teardown


def _clean(body: dict) -> dict:
    """Drop null/empty values — the bulk endpoints reject them."""
    return {k: v for k, v in body.items() if v not in (None, "", [], {})}


@dataclass
class Action:
    verb: str          # create | skip | prerequisite | unsupported
    kind: str
    ref: str
    name: str
    reason: str = ""

    def __str__(self) -> str:
        mark = {"create": "+", "skip": "=", "prerequisite": "?", "unsupported": "!"}
        tail = f"   ({self.reason})" if self.reason else ""
        return f"  {mark[self.verb]} {self.kind:13} {self.name}{tail}"


class PolicyProvisioner:
    def __init__(self, client: AlationClient, state: DeploymentState,
                 prefix: str = ""):
        self.c = client
        self.state = state
        self.prefix = prefix or ""
        self._cde_token: str | None = None
        self._group_path: str | None = None

    def prefixed(self, name: str) -> str:
        return f"{self.prefix}{name}" if self.prefix else name

    # -- policy groups: read-only, therefore a prerequisite ----------------
    def _list_groups(self) -> list[dict]:
        """Try both path spellings once, then remember which worked."""
        paths = (self._group_path,) if self._group_path else _GROUP_PATHS
        last: Exception | None = None
        for path in paths:
            try:
                resp = self.c.get(f"{path}?limit=500")
            except (AlationError, RuntimeError) as err:
                last = err
                continue
            self._group_path = path
            if isinstance(resp, list):
                return resp
            for key in ("results", "items", "data", "policy_groups"):
                if isinstance(resp, dict) and isinstance(resp.get(key), list):
                    return resp[key]
            return []
        raise RuntimeError(
            f"Could not list policy groups at any of {_GROUP_PATHS}. Last error: {last}"
        )

    def resolve_group(self, title: str) -> int | None:
        want = title.strip().lower()
        for g in self._list_groups():
            if (g.get("title") or "").strip().lower() == want:
                return g.get("id")
        return None

    # -- policies ----------------------------------------------------------
    def _list_policies(self, search: str | None = None) -> list[dict]:
        path = f"{POLICIES}?limit=500" + (f"&search={search}" if search else "")
        resp = self.c.get(path)
        if isinstance(resp, list):
            return resp
        for key in ("results", "items", "data", "policies"):
            if isinstance(resp, dict) and isinstance(resp.get(key), list):
                return resp[key]
        return []

    def find_policy(self, title: str) -> dict | None:
        want = title.strip().lower()
        for p in self._list_policies(search=title):
            if (p.get("title") or "").strip().lower() == want:
                return p
        return None

    # -- CDE service -------------------------------------------------------
    def cde_token(self) -> str:
        if self._cde_token:
            return self._cde_token
        legacy = self.c.s.access_token
        if not legacy:
            raise RuntimeError(
                "CDE standards need ALATION_ACCESS_TOKEN (a legacy API token) in "
                ".env — the CDE service does not accept the OAuth bearer. Policies "
                "work without it; use --only policy to skip standards."
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
        try:
            self.c.get(f"{STANDARDS}?limit=1",
                       extra_headers={"CDEToken": self.cde_token()})
            return True, "reachable"
        except (AlationError, RuntimeError) as err:
            return False, str(err)[:180]

    # -- plan --------------------------------------------------------------
    def plan(self, spec: dict) -> list[Action]:
        """Reads only. Nothing is created."""
        actions: list[Action] = []

        group = spec.get("policy_group")
        group_id = None
        if group:
            title = group["title"]           # NOT prefixed: it is the customer's
            group_id = self.resolve_group(title)
            if group_id:
                actions.append(Action("skip", "policy_group", group["ref"],
                                      title, f"exists, id={group_id}"))
            else:
                actions.append(Action(
                    "prerequisite", "policy_group", group["ref"], title,
                    "MISSING — policy groups have no create API; make it in the UI"))

        for p in spec.get("policies") or []:
            name = self.prefixed(p["title"])
            if self.state.id_for("policy", p["ref"]):
                actions.append(Action("skip", "policy", p["ref"], name,
                                      "already created by this kit"))
            elif self.find_policy(name):
                actions.append(Action("skip", "policy", p["ref"], name,
                                      "exists on the instance, not ours"))
            else:
                actions.append(Action("create", "policy", p["ref"], name))

        if spec.get("standards"):
            ok, why = self.verify_standards_api()
            for s in spec["standards"]:
                src = s.get("from_policy")
                title = next((p["title"] for p in spec.get("policies") or []
                              if p["ref"] == src), src or "?")
                name = self.prefixed(title)      # standards inherit the policy name
                if not ok:
                    actions.append(Action("unsupported", "standard", s["ref"], name,
                                          f"CDE standards API: {why}"))
                elif self.state.id_for("standard", s["ref"]):
                    actions.append(Action("skip", "standard", s["ref"], name,
                                          "already created by this kit"))
                else:
                    actions.append(Action("create", "standard", s["ref"], name))
        return actions

    # -- apply -------------------------------------------------------------
    def apply(self, spec: dict, only: set[str] | None = None) -> list[str]:
        log: list[str] = []
        want = only or {"policy", "standard"}

        group_id = None
        group = spec.get("policy_group")
        if group:
            group_id = self.resolve_group(group["title"])
            if group_id:
                log.append(f"  = policy_group {group['title']} (id={group_id})")
            else:
                log.append(
                    f"  ? policy_group {group['title']!r} does not exist. Policy "
                    f"groups have no create API — create it in the UI, then re-run. "
                    f"Proceeding without a group.")

        created_refs: dict[str, str] = {}
        if "policy" in want:
            for p in spec.get("policies") or []:
                pid = self._ensure_policy(p, group_id, log)
                if pid:
                    created_refs[p["ref"]] = pid

        if "standard" in want and spec.get("standards"):
            ok, why = self.verify_standards_api()
            if not ok:
                log.append(f"  ! skipping standards — {why}")
                log.append("    Create them in the UI; they become a prerequisite.")
            else:
                for s in spec["standards"]:
                    self._ensure_standard(s, spec, created_refs, log)
        return log

    def _ensure_policy(self, p: dict, group_id: int | None,
                       log: list[str]) -> str | None:
        name = self.prefixed(p["title"])

        recorded = self.state.id_for("policy", p["ref"])
        if recorded:
            log.append(f"  = policy {name} (already ours: {recorded})")
            return recorded

        found = self.find_policy(name)
        if found:
            log.append(f"  = policy {name} (pre-existing, id={found.get('id')} — "
                       f"NOT recorded, so destroy will not remove it)")
            return str(found.get("id"))

        body = _clean({
            "title": name,
            "description": p.get("description"),
            "policy_group_ids": [group_id] if group_id else None,
            "template_id": p.get("template_id"),
            "fields": p.get("fields"),
        })
        resp = self.c.post(POLICIES, json_body=[body])   # bulk: bare array

        task_id = None
        if isinstance(resp, dict):
            task_id = (resp.get("task") or {}).get("id") or resp.get("job_id")
        if task_id:
            state = self._await_job(task_id, log)
            if state and state not in ("successful", "partially_successful"):
                log.append(f"  ! policy {name}: job {task_id} ended {state}")
                return None

        # The job carries no object ids, so recover by the namespaced title.
        pid = None
        for _ in range(6):
            found = self.find_policy(name)
            if found and found.get("id"):
                pid = str(found["id"])
                break
            time.sleep(2)

        if pid:
            self.state.record("policy", p["ref"], pid, name,
                              policy_group_id=group_id)
            log.append(f"  + policy {name} -> {pid}")
        else:
            log.append(f"  ! policy {name}: created but its id could not be "
                       f"recovered by search. It may exist un-recorded — check the "
                       f"UI before re-running, or destroy cannot remove it.")
        return pid

    def _ensure_standard(self, s: dict, spec: dict,
                         policy_ids: dict[str, str], log: list[str]) -> str | None:
        src_ref = s.get("from_policy")
        src_id = policy_ids.get(src_ref) or self.state.id_for("policy", src_ref)
        title = next((p["title"] for p in spec.get("policies") or []
                      if p["ref"] == src_ref), None)
        if not src_id or not title:
            log.append(f"  ! standard {s['ref']}: source policy {src_ref!r} not "
                       f"available — a standard needs exactly one source policy")
            return None

        name = self.prefixed(title)
        if self.state.id_for("standard", s["ref"]):
            log.append(f"  = standard {name} (already ours)")
            return self.state.id_for("standard", s["ref"])

        body = _clean({
            "name": name,
            "purpose": s.get("purpose"),
            "scope": s.get("scope"),
            "derived_requirements": s.get("derived_requirements"),
            "options": {"allow_duplicates": False},
        })
        try:
            resp = self.c.post(STANDARDS, json_body=body,
                               extra_headers={"CDEToken": self.cde_token()})
        except (AlationError, RuntimeError) as err:
            log.append(f"  ! standard {name}: {str(err)[:160]}")
            return None

        sid = None
        if isinstance(resp, dict):
            sid = resp.get("id") or resp.get("key")
        if sid:
            self.state.record("standard", s["ref"], str(sid), name,
                              source_policy_id=src_id)
            log.append(f"  + standard {name} -> {sid}")
        else:
            log.append(f"  ! standard {name}: no id/key returned ({resp})")
        return sid

    def _await_job(self, task_id: Any, log: list[str],
                   attempts: int = 15, wait: float = 2.0) -> str | None:
        """Poll the bulk job. Note the path is /api/v1/, not /integration/."""
        for _ in range(attempts):
            try:
                resp = self.c.get(f"{JOB}?id={task_id}")
            except (AlationError, RuntimeError):
                return None
            if isinstance(resp, list) and resp:
                resp = resp[0]
            status = str((resp or {}).get("status") or "").lower()
            if status in ("successful", "partially_successful", "failed"):
                return status
            time.sleep(wait)
        log.append(f"    (job {task_id} still running after "
                   f"{attempts * wait:.0f}s; continuing)")
        return None

    # -- destroy -----------------------------------------------------------
    def destroy(self, dry_run: bool = True) -> list[str]:
        """Delete only recorded objects, in reverse dependency order, by ID."""
        log: list[str] = []
        records = self.state.teardown_order(KIND_ORDER)
        if not records:
            return ["  nothing recorded — this kit has created nothing to remove"]

        standards = [r for r in records if r["kind"] == "standard"]
        policies = [r for r in records if r["kind"] == "policy"]
        other = [r for r in records if r["kind"] not in ("standard", "policy")]

        for rec in standards:
            if dry_run:
                log.append(f"  - would delete standard {rec['name']} (id={rec['id']})")
                continue
            try:
                self.c.delete(f"{STANDARDS}{rec['id']}/",
                              extra_headers={"CDEToken": self.cde_token()})
            except (AlationError, RuntimeError) as err:
                log.append(f"  ! standard {rec['name']}: {str(err)[:140]}")
                continue
            self.state.forget("standard", rec["ref"])
            log.append(f"  - deleted standard {rec['name']} (id={rec['id']})")

        if policies:
            ids = [int(r["id"]) for r in policies if str(r["id"]).isdigit()]
            if dry_run:
                for r in policies:
                    log.append(f"  - would delete policy {r['name']} (id={r['id']})")
            elif ids:
                # DELETE is synchronous and takes {"ids": [...]} — one call.
                try:
                    self.c.request("DELETE", POLICIES, json_body={"ids": ids})
                except (AlationError, RuntimeError) as err:
                    log.append(f"  ! deleting policies {ids}: {str(err)[:160]}")
                else:
                    for r in policies:
                        self.state.forget("policy", r["ref"])
                        log.append(f"  - deleted policy {r['name']} (id={r['id']})")

        for rec in other:
            log.append(f"  ? {rec['kind']} {rec['name']}: no delete rule, left alone")

        log.append("")
        log.append("  Policy groups are never deleted: this kit cannot create them, "
                   "so it does not own them.")
        return log
