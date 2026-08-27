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

import json
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

# Standard status is a state machine, not a field you set. Verified by
# experiment 2026-08-27: DRAFT -> PUBLISHED is refused with
# "Invalid target status for Standard status transition: PolicyStatus.PUBLISHED"
# — publishing must route through PENDING_APPROVAL. IN_REVIEW is in the
# PolicyStatus enum but is NOT settable via this endpoint, so it can only be a
# state we observe (the approval workflow puts it there), never one we request.
STATUS_EDGES = {
    "DRAFT": {"PENDING_APPROVAL"},
    "PENDING_APPROVAL": {"PUBLISHED", "DRAFT"},
    "IN_REVIEW": {"PUBLISHED", "DRAFT"},
    "PUBLISHED": {"DRAFT"},
}


def status_path(current: str, target: str) -> list[str] | None:
    """Shortest legal sequence of status hops, or None if unreachable."""
    cur = (current or "").upper()
    tgt = (target or "").upper()
    if cur == tgt:
        return []
    seen, queue = {cur}, [(cur, [])]
    while queue:
        node, path = queue.pop(0)
        for nxt in sorted(STATUS_EDGES.get(node, ())):
            if nxt in seen:
                continue
            if nxt == tgt:
                return path + [nxt]
            seen.add(nxt)
            queue.append((nxt, path + [nxt]))
    return None

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
        # Same legacy credential the catalog APIs use — either pasted as
        # ALATION_ACCESS_TOKEN or minted from ALATION_REFRESH_TOKEN. Ask the
        # client rather than reading the setting, or a configured refresh token
        # looks like no credential at all.
        legacy = self.c.catalog_token()
        if not legacy:
            raise RuntimeError(
                "CDE standards need a legacy API token — the CDE service does not "
                "accept the OAuth bearer. Set ALATION_REFRESH_TOKEN and "
                "ALATION_USER_ID (or ALATION_ACCESS_TOKEN) in .env. Policies work "
                "without it; use --only policy to skip standards."
            )
        # Docs write this header uppercase; HTTP is case-insensitive but match them.
        resp = self.c.request("POST", CDE_AUTH, None,
                              extra_headers={"TOKEN": legacy})
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

        # Schema verified against the CDE OpenAPI spec (StandardCreationRequest,
        # CDE 2026.4.0-0). Required: name, purpose, scope, derived_requirements.
        # A field's allowed values live under `allowed_values` — `accepted_values`
        # was our invention and is what the 400 was rejecting.
        #
        # `sources` is optional in OpenAPI but a Template Overlay standard is
        # documented as deriving FROM a policy, and the whole point here is the
        # BCBS 239 traceability, so always send it. source_key is the documented
        # alation:// URN form.
        body = _clean({
            "name": name,
            "purpose": s.get("purpose"),
            "scope": s.get("scope"),
            "derived_requirements": s.get("derived_requirements"),
            "sources": [{
                "id": int(src_id),
                "name": name,
                "source_key": f"alation://business_policy/{src_id}",
            }],
            "options": {"allow_duplicates": False},
        })
        try:
            resp = self.c.post(STANDARDS, json_body=body,
                               extra_headers={"CDEToken": self.cde_token()})
        except (AlationError, RuntimeError) as err:
            # Do NOT truncate a structural rejection. The CDE service names the
            # exact sub-object it dislikes, and clipping it to 160 chars throws
            # away the only part that says why.
            detail = getattr(err, "body", None)
            log.append(f"  ! standard {name} rejected:")
            log.append(f"      {json.dumps(detail, default=str, indent=6)}"
                       if detail is not None else f"      {err}")
            log.append(f"      request body we sent:")
            log.append(f"      {json.dumps(body, default=str)[:2000]}")
            return None

        # StandardResponse carries BOTH `id` (int primary key) and `key` (UUID).
        # /standard/{id}/ takes the integer, so prefer it — recording the UUID
        # would give us a teardown that cannot delete.
        sid = None
        if isinstance(resp, dict):
            sid = resp.get("id")
            if sid is None and resp.get("key"):
                log.append(f"      ! no integer id returned, falling back to key "
                           f"{resp['key']} — delete by id may not work")
                sid = resp["key"]
        if sid:
            self.state.record("standard", s["ref"], str(sid), name,
                              source_policy_id=src_id)
            log.append(f"  + standard {name} -> {sid}")
        else:
            log.append(f"  ! standard {name}: no id/key returned ({resp})")
        return sid

    def _await_job(self, task_id: Any, log: list[str],
                   attempts: int = 60, wait: float = 2.0) -> str | None:
        """Poll the bulk job to a terminal state.

        Giving up early is worse than waiting: the id-recovery search that
        follows only finds the object once the job has actually committed it, so
        a premature "continuing" produces a spurious "created but id could not
        be recovered" — and an unrecorded object is one teardown cannot remove.
        Two minutes of patience beats a bad state file.
        """
        last = None
        for _ in range(attempts):
            try:
                resp = self.c.get(f"{JOB}?id={task_id}")
            except (AlationError, RuntimeError) as err:
                log.append(f"    (job {task_id} status unreadable: {str(err)[:120]})")
                return None
            if isinstance(resp, list) and resp:
                resp = resp[0]
            last = resp or {}
            status = str(last.get("status") or "").lower()
            if status in ("successful", "partially_successful", "failed"):
                if status != "successful":
                    # The job body carries per-row errors; without them a
                    # partial success is indistinguishable from a full one.
                    detail = last.get("result") or last.get("msg") or last
                    log.append(f"    (job {task_id} {status}: "
                               f"{json.dumps(detail, default=str)[:300]})")
                return status
            time.sleep(wait)
        log.append(f"    (job {task_id} STILL not terminal after "
                   f"{attempts * wait:.0f}s — last status "
                   f"{str((last or {}).get('status'))!r}. Anything it creates "
                   f"after this point will be un-recorded.)")
        return None

    def dump_standards(self) -> Any:
        """Return existing overlay standards verbatim.

        Written because our `derived_requirements` shape was invented from the
        policy design doc, not from the API. When the service says "Invalid
        structure", an existing object is the cheapest authoritative schema.
        """
        return self.c.get(f"{STANDARDS}?limit=50",
                          extra_headers={"CDEToken": self.cde_token()})

    # -- verify ------------------------------------------------------------
    def verify(self, spec: dict) -> tuple[list[str], bool]:
        """Read every recorded id back and confirm it is the object we think.

        This is the guard `destroy` depends on. Ids are recovered by searching a
        title, so a title collision, a rename, or a mis-parsed job response
        could bind a ref to someone else's object — and teardown deletes by
        recorded id without re-checking. Cheap to run, catastrophic to skip.

        Also reports spec'd policies with no record at all: those may exist
        un-recorded in the instance, which teardown will silently leave behind.
        """
        log: list[str] = []
        ok = True

        by_id = {str(p.get("id")): p for p in self._list_policies()}
        recorded_refs = set()

        for rec in self.state.teardown_order(KIND_ORDER):
            if rec["kind"] != "policy":
                continue
            recorded_refs.add(rec["ref"])
            rid, want = str(rec["id"]), (rec.get("name") or "")
            actual = by_id.get(rid)
            if actual is None:
                log.append(f"  ! policy {want!r} recorded as id={rid}, but no "
                           f"policy with that id exists. Stale state — teardown "
                           f"would delete nothing, or worse, a recycled id.")
                ok = False
                continue
            got = (actual.get("title") or "").strip()
            if got.strip().lower() != want.strip().lower():
                log.append(f"  ! MISMATCH id={rid}: recorded as {want!r} but the "
                           f"instance calls it {got!r}. DO NOT run destroy — it "
                           f"would delete the wrong object.")
                ok = False
            else:
                log.append(f"  = policy id={rid} {got!r} verified")

        # Standards live on the CDE service, so they need their own read-back.
        # Leaving them unverified would mean half the state file is trusted
        # rather than checked — and standards are deleted by recorded id too.
        std_recs = [r for r in self.state.teardown_order(KIND_ORDER)
                    if r["kind"] == "standard"]
        if std_recs:
            try:
                token = self.cde_token()
            except (AlationError, RuntimeError) as err:
                log.append(f"  ? {len(std_recs)} standard(s) recorded but the CDE "
                           f"service is unreachable, so they are UNVERIFIED: "
                           f"{str(err)[:120]}")
                ok = False
                token = None
            if token:
                for rec in std_recs:
                    rid, want = rec["id"], (rec.get("name") or "")
                    try:
                        got = self.c.get(f"{STANDARDS}{rid}/",
                                         extra_headers={"CDEToken": token})
                    except (AlationError, RuntimeError) as err:
                        log.append(f"  ! standard {want!r} recorded as id={rid} "
                                   f"but reading it back failed: {str(err)[:120]}")
                        ok = False
                        continue
                    actual = (got or {}).get("name") or ""
                    status = (got or {}).get("status")
                    if actual.strip().lower() != want.strip().lower():
                        log.append(f"  ! MISMATCH standard id={rid}: recorded as "
                                   f"{want!r} but instance calls it {actual!r}. "
                                   f"DO NOT run destroy.")
                        ok = False
                    else:
                        note = ""
                        if str(status).upper() != "PUBLISHED":
                            note = (f"  <- status {status}; CDM only applies "
                                    f"PUBLISHED versions, so this is not yet "
                                    f"attachable to CDEs")
                        log.append(f"  = standard id={rid} {actual!r} verified"
                                   f"{note}")

        for p in spec.get("policies") or []:
            if p["ref"] in recorded_refs:
                continue
            name = self.prefixed(p["title"])
            found = self.find_policy(name)
            if found:
                log.append(f"  ! policy {name!r} EXISTS in the instance "
                           f"(id={found.get('id')}) but is not recorded. Teardown "
                           f"will leave it behind; delete it in the UI, or re-run "
                           f"apply after removing it.")
                ok = False
            else:
                log.append(f"  - policy {name!r} not created yet")
        return log, ok

    # -- publish -----------------------------------------------------------
    def publish(self, new_status: str = "PUBLISHED", comment: str = "",
                dry_run: bool = True) -> tuple[list[str], bool]:
        """Transition recorded standards out of DRAFT.

        Schema verified from the CDE OpenAPI spec (`StandardStatusChangeRequest`):
        `POST /cde-service/integration/standard/{id}/status/` with
        `{new_status, comment}`. The settable values are DRAFT,
        PENDING_APPROVAL and PUBLISHED — note IN_REVIEW appears in PolicyStatus
        but is NOT settable here, so it is reached by the workflow, not by us.

        Whether DRAFT -> PUBLISHED is permitted in one hop depends on the
        instance's approval rules and whether the caller is a Global Standards
        Approver. A 403 here is a role problem, not a payload problem, and the
        honest fallback is PENDING_APPROVAL — which is arguably the truthful
        demo anyway, since no bank auto-publishes a governance standard.
        """
        allowed = {"DRAFT", "PENDING_APPROVAL", "PUBLISHED"}
        new_status = (new_status or "").upper()
        if new_status not in allowed:
            return ([f"  ! {new_status!r} is not settable. Choose one of "
                     f"{sorted(allowed)} — IN_REVIEW is reached via the approval "
                     f"workflow, not by this call."], False)

        log: list[str] = []
        ok = True
        recs = [r for r in self.state.teardown_order(KIND_ORDER)
                if r["kind"] == "standard"]
        if not recs:
            return (["  nothing recorded — no standards to publish"], True)

        try:
            token = self.cde_token()
        except (AlationError, RuntimeError) as err:
            return ([f"  ! CDE service unavailable: {str(err)[:200]}"], False)

        for rec in recs:
            rid, name = rec["id"], rec.get("name") or ""
            try:
                current = (self.c.get(f"{STANDARDS}{rid}/",
                                      extra_headers={"CDEToken": token})
                           or {}).get("status")
            except (AlationError, RuntimeError) as err:
                log.append(f"  ! standard id={rid} unreadable: {str(err)[:120]}")
                ok = False
                continue

            hops = status_path(str(current), new_status)
            if hops is None:
                log.append(f"  ! standard id={rid} {name!r}: no legal path from "
                           f"{current} to {new_status}")
                ok = False
                continue
            if not hops:
                log.append(f"  = standard id={rid} {name!r} already {new_status}")
                continue
            if dry_run:
                log.append(f"  ~ standard id={rid} {name!r}: "
                           f"{' -> '.join([str(current)] + hops)}")
                continue

            for hop in hops:
                try:
                    self.c.post(f"{STANDARDS}{rid}/status/",
                                json_body={"new_status": hop, "comment": comment},
                                extra_headers={"CDEToken": token})
                except (AlationError, RuntimeError) as err:
                    body = getattr(err, "body", None)
                    log.append(f"  ! standard id={rid} {name!r}: hop -> {hop} refused")
                    log.append(f"      {json.dumps(body, default=str) if body is not None else err}")
                    if getattr(err, "status", None) == 403:
                        log.append("      403 = role, not payload. Approving needs "
                                   "Global Standards Approver. The standard is left "
                                   "at its previous status, which is a legitimate "
                                   "end state — a bank approves standards, it does "
                                   "not auto-publish them.")
                    ok = False
                    break

                # Read back after EVERY hop: the approval workflow can divert a
                # transition (e.g. into IN_REVIEW), and continuing to the next
                # hop from an assumed state would compound the error.
                try:
                    now = (self.c.get(f"{STANDARDS}{rid}/",
                                      extra_headers={"CDEToken": token})
                           or {}).get("status")
                except (AlationError, RuntimeError):
                    now = "unreadable"
                if str(now).upper() != hop:
                    log.append(f"  ! standard id={rid} {name!r}: asked for {hop}, "
                               f"instance reports {now!r} — the approval workflow "
                               f"intervened. Stopping rather than guessing.")
                    ok = False
                    break
                log.append(f"  + standard id={rid} {name!r} -> {now}")
        return log, ok

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
