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
JOB_ERRORS = "/api/job_error/"

# Verified from the Policy API spec (Create_Policy_Bulk_Response_Body), NOT
# guessed. Two independent fields, and the earlier code checked invented values
# ("successful", "partially_successful") that this API never returns — so
# `partial_success` was treated as still-running, the poll burned its full
# timeout, and the id-recovery search then ran against a job that had in fact
# finished. Cost: three policies that looked like search failures.
# NOTE `na` is deliberately NOT here. It means "not applicable yet" and appears
# while state is `queued`/`started` — treating it as terminal makes a running job
# look finished, which is the same class of error as the one above, inverted.
TERMINAL_STATUSES = {"succeeded", "failed", "partial_success", "skipped"}
TERMINAL_STATES = {"finished"}
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
    # PUBLISHED IS TERMINAL. This previously read {"DRAFT"}, which was assumed
    # and never tested, and teardown was built on it. Disproven by execution
    # 2026-08-28 on six standards:
    #   POST /standard/{id}/status/ {"new_status": "DRAFT"} -> 400 "Invalid
    #   target status for Standard status transition"
    #   DELETE /standard/{id}/       -> 403 "Only DRAFT and PENDING APPROVAL
    #   Standards can be deleted"
    # A published standard cannot be demoted and cannot be deleted. Editing one
    # creates a NEW DRAFT VERSION (POST /standard/{id}/new_version/) and the
    # published version stays; deleting that draft reverts to it. So publish is
    # a one-way door, and PENDING_APPROVAL is the last state from which a
    # standard is still removable.
    "PUBLISHED": set(),
}

# From the 403 body above, verbatim. Both states delete directly — there is no
# need to walk PENDING_APPROVAL back to DRAFT first.
DELETABLE_STANDARD_STATES = {"DRAFT", "PENDING_APPROVAL"}


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
        try:
            resp = self.c.request("POST", CDE_AUTH, None,
                                  extra_headers={"TOKEN": legacy})
        except AlationError as err:
            # 403 "Invalid Alation API token" means the cached access token was
            # revoked or expired. Access tokens last ~24h AND are revoked
            # whenever a new one is minted from the same refresh token, so a
            # cache hit is not proof of validity. Re-mint once before failing —
            # otherwise a routine `whoami` in another shell breaks the next
            # deploy for no visible reason.
            if getattr(err, "status", None) not in (401, 403):
                raise
            fresh = self.c.catalog_token(force_refresh=True)
            if not fresh or fresh == legacy:
                raise
            resp = self.c.request("POST", CDE_AUTH, None,
                                  extra_headers={"TOKEN": fresh})
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
    def state_conflicts(self, spec: dict) -> list[str]:
        """Records in the state file that do not belong to THIS spec.

        Two specs sharing a ref with different titles is not hypothetical: the
        hand-authored and generated BCBS 239 specs both used `POL-ACCURACY` and
        `POL-COMPLETE`, so `_ensure_*` found a recorded id, logged "already
        ours", and silently skipped creating the new object. `verify` caught it
        only afterwards, by which point three objects were missing and the run
        looked like a search failure. Checking BEFORE a write turns a silent skip
        into a refusal.
        """
        spec_refs = {p["ref"] for p in spec.get("policies") or []}
        spec_refs |= {s["ref"] for s in spec.get("standards") or []}
        titles = {p["ref"]: self.prefixed(p["title"])
                  for p in spec.get("policies") or []}

        problems: list[str] = []
        for rec in self.state.teardown_order(KIND_ORDER):
            ref, name = rec.get("ref"), (rec.get("name") or "")
            if ref not in spec_refs:
                problems.append(
                    f"{rec['kind']} {ref} (id={rec['id']}, {name!r}) is recorded "
                    f"but absent from this spec — left over from another one")
                continue
            expected = titles.get(ref)
            if expected and expected.strip().lower() != name.strip().lower():
                problems.append(
                    f"{rec['kind']} {ref} is recorded as {name!r} but this spec "
                    f"calls it {expected!r} — apply would skip creating it")
        return problems

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
        state = None
        if isinstance(resp, dict):
            task_id = (resp.get("task") or {}).get("id") or resp.get("job_id")
        if task_id:
            state = self._await_job(task_id, log)
            # Only a hard failure aborts. `partial_success` still gets the
            # recovery search, because the row may have committed — but if the
            # search then finds nothing, the message says "rejected", not
            # "search missed", which is the honest reading.
            if state == "failed":
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
            hint = ("The job reported partial_success, so Alation most likely "
                    "REJECTED this row rather than the search missing it — see "
                    "the job errors above."
                    if state in ("partial_success", "failed") else
                    "It may exist un-recorded — check the UI before re-running, "
                    "or destroy cannot remove it.")
            log.append(f"  ! policy {name}: no id could be recovered. {hint}")
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
            state = str(last.get("state") or "").lower()

            if state in TERMINAL_STATES or status in TERMINAL_STATUSES:
                if status not in ("succeeded",):
                    # A partial success means SOME rows committed. Which ones is
                    # not in this body, so fetch the per-row errors — otherwise
                    # "partial" is indistinguishable from "fine" and the missing
                    # object looks like a search failure instead of a rejection.
                    detail = last.get("result") or last.get("msg") or last
                    log.append(f"    (job {task_id} {status or state}: "
                               f"{json.dumps(detail, default=str)[:300]})")
                    for line in self._job_errors(task_id):
                        log.append(f"      {line}")
                return status or state
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

        # What the SPEC says each ref should be called. A record can agree with
        # the instance and still be wrong for this spec: if an earlier spec used
        # the same ref with a different title, the stale record satisfies
        # `_ensure_*` ("already ours") and the new object is never created —
        # silently, because state-vs-instance still matches.
        spec_titles = {p["ref"]: self.prefixed(p["title"])
                       for p in spec.get("policies") or []}
        spec_titles.update({
            s["ref"]: self.prefixed(next(
                (p["title"] for p in spec.get("policies") or []
                 if p["ref"] == s.get("from_policy")), s["ref"]))
            for s in spec.get("standards") or []})

        for rec in self.state.teardown_order(KIND_ORDER):
            if rec["kind"] != "policy":
                continue
            recorded_refs.add(rec["ref"])
            rid, want = str(rec["id"]), (rec.get("name") or "")
            expected = spec_titles.get(rec["ref"])
            if expected and expected.strip().lower() != want.strip().lower():
                log.append(f"  ! STALE RECORD {rec['ref']}: state says {want!r} "
                           f"but this spec calls it {expected!r}. The record is "
                           f"from an earlier spec, so `apply` skipped creating "
                           f"the current one. Run `policy destroy` first.")
                ok = False
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
                    if rec["ref"] not in {s["ref"] for s in spec.get("standards") or []}:
                        log.append(f"  ! ORPHAN RECORD {rec['ref']} (id={rid}, "
                                   f"{want!r}) — not in this spec at all. Left "
                                   f"over from an earlier one; `destroy` will "
                                   f"remove it.")
                        ok = False
                    exp = spec_titles.get(rec["ref"])
                    if exp and exp.strip().lower() != want.strip().lower():
                        log.append(f"  ! STALE RECORD {rec['ref']}: state says "
                                   f"{want!r} but this spec calls it {exp!r}")
                        ok = False
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

    def _job_errors(self, task_id: Any, limit: int = 5) -> list[str]:
        """Per-row errors for a bulk job. Best effort — never raises.

        The job status body says a job partially succeeded but not which rows
        failed or why. Without this, a rejected policy is indistinguishable from
        one the recovery search simply missed.
        """
        try:
            resp = self.c.get(f"{JOB_ERRORS}?job_id={task_id}")
        except (AlationError, RuntimeError) as err:
            return [f"! could not read job errors: {str(err)[:100]}"]
        rows = resp if isinstance(resp, list) else (
            resp.get("results") or resp.get("errors") or [] if isinstance(resp, dict) else [])
        if not rows:
            return ["(no per-row errors reported)"]
        out = [f"! {json.dumps(r, default=str)[:200]}" for r in rows[:limit]]
        if len(rows) > limit:
            out.append(f"! ... and {len(rows) - limit} more")
        return out

    # -- assess (drift) ----------------------------------------------------
    def assess(self, spec: dict, register: dict | None = None) -> tuple[list[str], dict]:
        """Does the instance's governance cover what this spec requires?

        Distinct from the PDE mapper's question. The mapper asks "does the
        catalog hold the DATA this regulation needs?" This asks "does the
        GOVERNANCE FRAMEWORK cover what the document says?" Same document,
        different target — and until now nothing answered the second one, so a
        re-run would have silently re-provisioned the same four policies.

        Reads only. Reports four states per policy:
          present  — in the spec and in the instance
          missing  — in the spec, absent from the instance -> needs creating
          untracked— in the instance but not recorded by this kit -> teardown
                     will not remove it
          orphaned — namespaced like ours, in the instance, absent from the spec
                     -> the spec shrank, or the document changed

        Plus, when a register is supplied, principles that drive CDEs but have
        no policy at all: uncovered regulatory surface.
        """
        log: list[str] = []
        summary = {"present": 0, "missing": 0, "untracked": 0, "orphaned": 0}

        instance = {(p.get("title") or "").strip().lower(): p
                    for p in self._list_policies()}
        spec_titles: set[str] = set()

        for pol in spec.get("policies") or []:
            name = self.prefixed(pol["title"])
            key = name.strip().lower()
            spec_titles.add(key)
            recorded = self.state.id_for("policy", pol["ref"])
            found = instance.get(key)

            if found and recorded:
                log.append(f"  present   {name} (id={found.get('id')})")
                summary["present"] += 1
            elif found:
                log.append(f"  untracked {name} (id={found.get('id')}) — exists but "
                           f"this kit did not record creating it, so `destroy` "
                           f"will leave it behind")
                summary["untracked"] += 1
            else:
                log.append(f"  MISSING   {name} — the spec requires it and the "
                           f"instance does not have it")
                summary["missing"] += 1

        # Orphans: only consider objects inside our namespace. Without a prefix
        # every unrelated policy in the catalog would look orphaned, which would
        # be a spectacularly unhelpful report in a real customer instance.
        if self.prefix:
            pref = self.prefix.strip().lower()
            for key, pol in instance.items():
                if key.startswith(pref) and key not in spec_titles:
                    log.append(f"  ORPHANED  {pol.get('title')} (id={pol.get('id')}) "
                               f"— namespaced like ours but not in the spec")
                    summary["orphaned"] += 1
        else:
            log.append("  (no --prefix, so orphan detection is skipped — every "
                       "unrelated policy in the catalog would match)")

        if register:
            from .authoring import register_facts
            driven = set(register_facts(register)["paragraphs_by_principle"])
            out_only: set[int] = set()
            for entry in register.get("out_of_scope") or []:
                if not entry.get("also_drives_cde"):
                    out_only.update(x for x in (entry.get("principles") or [])
                                    if isinstance(x, int))
            covered = {(p.get("derived_from") or {}).get("principle")
                       for p in spec.get("policies") or []}
            gap = sorted(driven - covered - out_only)
            summary["uncovered_principles"] = gap
            if gap:
                log.append(f"\n  UNCOVERED PRINCIPLES: {gap} drive CDEs in the "
                           f"register but no policy in this spec addresses them. "
                           f"Re-author the spec, or accept the gap explicitly.")
            else:
                log.append("\n  Every principle that drives a CDE has a policy.")
        return log, summary

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
                token = self.cde_token()
            except (AlationError, RuntimeError) as err:
                log.append(f"  ! standard {rec['name']}: CDE service unavailable, "
                           f"not deleted ({str(err)[:100]})")
                continue

            try:
                current = (self.c.get(f"{STANDARDS}{rec['id']}/",
                                      extra_headers={"CDEToken": token})
                           or {}).get("status")
            except (AlationError, RuntimeError):
                current = None
            cur = str(current or "").upper()

            # Ask the instance which transitions are legal rather than trusting
            # STATUS_EDGES. Guessing this table is what produced six failed
            # teardowns: it claimed PUBLISHED -> DRAFT and no such edge exists.
            # Best-effort — if the endpoint is absent the hard-coded table still
            # applies, but when it answers it is authoritative and its answer is
            # logged so the table can be corrected from evidence.
            allowed: set[str] | None = None
            try:
                nxt = self.c.get(f"{STANDARDS}{rec['id']}/next_status/",
                                 extra_headers={"CDEToken": token})
                if isinstance(nxt, list):
                    allowed = {str(s).upper() for s in nxt}
                elif isinstance(nxt, dict):
                    allowed = {str(s).upper()
                               for s in (nxt.get("next_status")
                                         or nxt.get("statuses") or [])}
                if allowed is not None:
                    log.append(f"    (standard id={rec['id']} is {cur}; instance "
                               f"reports next_status={sorted(allowed) or 'none'})")
            except (AlationError, RuntimeError):
                allowed = None

            if cur and cur not in DELETABLE_STANDARD_STATES:
                reachable = [s for s in (allowed if allowed is not None
                                         else STATUS_EDGES.get(cur, set()))
                             if s in DELETABLE_STANDARD_STATES]
                if not reachable:
                    # Not a failure to retry — a property of the object. Say so
                    # plainly, and KEEP the state record: an object that exists
                    # un-recorded is invisible to teardown forever.
                    log.append(
                        f"  # standard {rec['name']} (id={rec['id']}) is {cur} "
                        f"and is PERMANENT — a published standard cannot be "
                        f"demoted or deleted. Left in place, still recorded.")
                    continue
                hop = reachable[0]
                try:
                    self.c.post(f"{STANDARDS}{rec['id']}/status/",
                                json_body={"new_status": hop,
                                           "comment": "Teardown by agentkit"},
                                extra_headers={"CDEToken": token})
                    log.append(f"    (standard id={rec['id']} {cur} -> {hop} "
                               f"so it can be deleted)")
                    cur = hop
                except (AlationError, RuntimeError) as err:
                    log.append(f"  ! standard {rec['name']}: could not move "
                               f"{cur} -> {hop} for deletion: {str(err)[:120]}")
                    continue

            try:
                self.c.delete(f"{STANDARDS}{rec['id']}/",
                              extra_headers={"CDEToken": token})
            except (AlationError, RuntimeError) as err:
                log.append(f"  ! standard {rec['name']} (id={rec['id']}) NOT "
                           f"deleted: {str(err)[:160]}")
                continue

            # Read back, for the same reason as policies: a 2xx is not proof.
            try:
                self.c.get(f"{STANDARDS}{rec['id']}/",
                           extra_headers={"CDEToken": token})
            except (AlationError, RuntimeError):
                self.state.forget("standard", rec["ref"])
                log.append(f"  - deleted standard {rec['name']} (id={rec['id']})")
            else:
                log.append(f"  ! standard {rec['name']} (id={rec['id']}) STILL "
                           f"READABLE after delete. Keeping the state record so "
                           f"teardown can retry.")

        if policies:
            ids = [int(r["id"]) for r in policies if str(r["id"]).isdigit()]
            if dry_run:
                for r in policies:
                    log.append(f"  - would delete policy {r['name']} (id={r['id']})")
            elif ids:
                # DELETE is synchronous and takes {"ids": [...]} — one call.
                try:
                    resp = self.c.request("DELETE", POLICIES, json_body={"ids": ids})
                except (AlationError, RuntimeError) as err:
                    log.append(f"  ! deleting policies {ids}: {str(err)[:160]}")
                else:
                    # READ BACK. A 2xx is not proof of deletion: this endpoint
                    # answers 204 with an empty body, and the list endpoint has a
                    # `deleted` query parameter, which implies Alation may be
                    # SOFT-deleting. Forgetting a record for an object that still
                    # exists is the worst outcome — it becomes permanently
                    # invisible to teardown.
                    still: dict[str, dict] = {}
                    try:
                        after = {str(p.get("id")): p for p in self._list_policies()}
                        # Key by STRING throughout: `ids` holds ints while the
                        # records hold strings, and mixing them means the
                        # survivor check silently never matches.
                        still = {str(i): after[str(i)] for i in ids
                                 if str(i) in after}
                    except (AlationError, RuntimeError) as err:
                        log.append(f"  ? could not confirm deletion "
                                   f"({str(err)[:100]}); state left intact")
                        still = {str(i): {} for i in ids}

                    for r in policies:
                        if str(r["id"]) in still:
                            log.append(
                                f"  ! policy {r['name']} (id={r['id']}) STILL "
                                f"PRESENT after DELETE returned success. Alation "
                                f"may be soft-deleting, or the id was ignored. "
                                f"Keeping the state record so teardown can retry — "
                                f"delete it in the UI if it is really gone.")
                            continue
                        self.state.forget("policy", r["ref"])
                        log.append(f"  - deleted policy {r['name']} (id={r['id']})")
                    if still:
                        log.append(f"  ! {len(still)} of {len(ids)} policies survived "
                                   f"the delete. Response body was: "
                                   f"{json.dumps(resp, default=str)[:200]}")

        for rec in other:
            log.append(f"  ? {rec['kind']} {rec['name']}: no delete rule, left alone")

        log.append("")
        log.append("  Policy groups are never deleted: this kit cannot create them, "
                   "so it does not own them.")
        return log
