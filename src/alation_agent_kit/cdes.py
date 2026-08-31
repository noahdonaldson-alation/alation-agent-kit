"""Critical Data Element provisioning against the CDE service.

Companion to policies.py, and deliberately narrower. The division of labour
across the chain, settled 2026-08-28:

    policies   the kit creates      (bulk endpoint, async, id by title search)
    standards  CDM creates          (UI only; no API generates one from a policy)
    CDEs       the kit creates      (this module)
    PDEs       CDM discovers        (DATA_MAPPING trigger; we never assert links)
    DQ         not built

Three properties of this API shape everything below.

**CDEs can only be created as DRAFT or CANDIDATE.** `CreateCDERequest.status`
accepts nothing else, so there is no way to script a certified CDE into someone's
instance even by accident. Unlike a published standard, a CDE is fully
reversible — `DELETE /cde/{id}/` works and `POST /cde/{id}/restore/` exists — so
teardown here behaves the way the settled decision assumes.

**Standards attach by UUID `key`, not by integer `id`.** `/standard/{id}/` takes
the int and `CreateCDERequest.fields[]` takes the UUID; both come back on a read.
Ids are per-instance and cannot be committed, so standards are resolved by NAME
at apply time, the same way policies.py resolves the policy group.

**PDEs are discovered, not asserted.** `pdes[]` exists on the create request and
we deliberately do not use it. DATA_MAPPING takes the register's `search_terms`
as `payload.keywords`, finds candidate columns itself, and marks them
`suggested` for a human to accept. That removes the fully-qualified-name to
attribute-id resolution step entirely, and it is the better demo: Alation's own
AI finding the columns rather than our script claiming to know them.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Any

from .client import AlationClient, AlationError
from .state import DeploymentState

CDES = "/cde-service/integration/cde/"
STANDARDS = "/cde-service/integration/standard/"
JOB = "/cde-service/integration/job/"

# CreateCDERequest.status: "Status in which CDE will be created: CANDIDATE or
# DRAFT, default is DRAFT". The full CDEStatus enum has six values, but the other
# four are reachable only through the workflow — POST /cde/{id}/status/ and
# POST /cde/{id}/recall/ — never at create time.
CREATABLE_STATUSES = {"DRAFT", "CANDIDATE"}

# Verified from the CDE API spec 2026-08-28. Not guessed: an invented action
# name would 422, but an action name that is merely WRONG (say CALCULATE_DQ_SCORE
# when DATA_MAPPING was meant) succeeds and silently does the wrong work.
ACTIONS = {"DATA_MAPPING", "CALCULATE_CURATION_SCORE", "CALCULATE_DQ_SCORE"}

JOB_TERMINAL = {"FINISHED", "ERROR", "CANCELED"}


@dataclass
class CDEAction:
    verb: str          # create | skip | prerequisite
    ref: str
    name: str
    detail: str = ""

    def __str__(self) -> str:
        mark = {"create": "+", "skip": "=", "prerequisite": "?"}.get(self.verb, " ")
        tail = f"  ({self.detail})" if self.detail else ""
        return f"  {mark} cde {self.ref:<8} {self.name}{tail}"


def risk_from_criticality(criticality: int | None) -> tuple[int | None, str | None]:
    """Register criticality 1-3 -> CDE risk level value and label.

    The register's scale was built with a deliberate procedure (default 2,
    promote to 3 only if an aggregate figure cannot be computed OR reconciled,
    demote to 1 if no figure is affected) and it converged to a stable rating per
    concept across 10 runs. It maps onto the Risk Assessment Framework's three
    levels directly, so do not re-derive it here — a second opinion on risk would
    just be an unstable one.
    """
    labels = {1: "Low", 2: "Medium", 3: "High"}
    if criticality not in labels:
        return None, None
    return criticality, labels[criticality]


# The CDE's own TRAILING noun implies its column suffix, and nothing else does.
# An earlier version generated all eleven suffixes against the head noun plus the
# bare head noun itself; on CDE-03 that took Physical Data Elements from 0 to 59,
# because bare "Exposure" matches every exposure-ish column across bronze,
# silver and gold. Precision matters more than recall here: a steward can find a
# missing column, but 59 suggestions is a rejection queue nobody works through.
_TAIL_SUFFIXES = {
    "identifier": ("_ID", "_KEY"), "id": ("_ID",), "key": ("_KEY", "_ID"),
    "amount": ("_AMT",), "amt": ("_AMT",), "balance": ("_AMT", "_BAL"),
    "date": ("_DT", "_DATE"), "timestamp": ("_TS",), "time": ("_TS",),
    "code": ("_CD",), "classification": ("_CD", "_TYPE"), "type": ("_TYPE", "_CD"),
    "flag": ("_FLG",), "indicator": ("_IND", "_FLG"), "name": ("_NM", "_NAME"),
    "number": ("_NBR",), "currency": ("_CCY",), "line": ("_CD", "_NM"),
    "reference": ("_REF",), "sector": ("_CD",), "country": ("_CD",),
}

# Words that carry no discriminating power in a column name. "Gross Exposure
# Amount" should yield EXPOSURE_AMT, not GROSS_*, and certainly not OF_*.
_STOPWORDS = {"the", "of", "a", "an", "and", "or", "own", "bank", "system",
              "record", "gross", "net", "total", "value", "data", "element"}

# Warehouse truncations. This is the half that made the difference on CDE-09:
# the column is GL_RECON_KEY, and no amount of decomposing "Reconciliation" gets
# you "RECON" without knowing that warehouses abbreviate. Noah's manual run
# succeeded because he typed "recon key" from experience.
#
# Deliberately short and deliberately incomplete. It covers the truncations that
# actually appear in this warehouse plus the obvious general ones; it is not an
# attempt at a banking ontology, and a term this table cannot produce is exactly
# what the register's own search_terms are for.
_ABBREV = {
    "reconciliation": "recon", "identifier": "id", "amount": "amt",
    "number": "nbr", "date": "dt", "timestamp": "ts", "code": "cd",
    "indicator": "ind", "transaction": "txn", "counterparty": "cpty",
    "reference": "ref", "description": "desc", "quantity": "qty",
    "currency": "ccy", "customer": "cust", "account": "acct",
    "general ledger": "gl", "legal entity": "le", "source system": "src",
}


def keyword_variants(name: str, extra: list[str] | None = None) -> list[str]:
    """Column-name-shaped search terms derived from a CDE's own name.

    WHY THIS EXISTS, measured 2026-08-28 on three live CDEs: DATA_MAPPING matches
    LEXICALLY against physical column names, not semantically.

      CDE-01 Counterparty Identifier   terms contained 'CPTY_ID' verbatim  -> 7 hits
      CDE-03 Gross Exposure Amount     target EXPOSURE_AMT, no term close  -> 0 hits
      CDE-09 ...Reconciliation Key     target GL_RECON_KEY, no term with
                                       'recon' at all                     -> 0 hits

    The register's `search_terms` are business vocabulary — "mark-to-market",
    "exposure at default", "fair value" — which is what the interpreter prompt
    asked for and which is useless to a lexical matcher. CDE-01 only worked by
    luck, because CPTY_ID is both a naming convention and the real column.

    Decomposing the CDE's own name is deterministic, so it is code's job. The
    register's terms are still passed through: they cost nothing and they carry
    domain knowledge this function cannot invent (LEI, BIC, GIIN).
    """
    words = [w for w in re.split(r"[^A-Za-z0-9]+", name or "") if w]
    keep = [w for w in words if w.lower() not in _STOPWORDS and len(w) > 2]

    out: list[str] = []

    def add(term: str) -> None:
        t = term.strip()
        if t and t.lower() not in {x.lower() for x in out}:
            out.append(t)

    # The full phrase and its trailing bigram: "Reconciliation Key",
    # "Exposure Amount" — the shape a human types and a column often spells.
    if keep:
        add(" ".join(keep))
    if len(keep) >= 2:
        add(" ".join(keep[-2:]))
        add("_".join(keep[-2:]).upper())
    # Head noun + ONLY the suffixes its own trailing noun implies. No bare head
    # noun: "Exposure" on its own is what produced 59 matches.
    head = keep[-2] if len(keep) >= 2 else (keep[-1] if keep else "")
    tail = keep[-1] if keep else ""
    suffixes = _TAIL_SUFFIXES.get(tail.lower(), ())
    for suf in suffixes:
        add(f"{head.upper()}{suf}")

    # Abbreviated forms, same discipline: the column is GL_RECON_KEY, not
    # GENERAL_LEDGER_RECONCILIATION_KEY, so abbreviate then apply the same
    # implied suffixes.
    short_head = _ABBREV.get(head.lower(), "")
    if short_head:
        add(f"{short_head} {tail}".strip())
        add(f"{short_head}_{tail}".upper())
        for suf in suffixes:
            add(f"{short_head.upper()}{suf}")

    # Multi-word abbreviations in the name ("general ledger" -> "gl") combined
    # with the abbreviated head, which is how GL_RECON_KEY is actually spelled.
    lowered = " ".join(w.lower() for w in words)
    for phrase, ab in _ABBREV.items():
        if " " not in phrase or phrase not in lowered:
            continue
        stem = short_head or head
        if stem:
            add(f"{ab}_{stem}_{tail}".upper())
            add(f"{ab}_{stem}".upper())
            add(f"{ab} {stem} {tail}")

    for e in extra or []:
        add(e)
    return out


def build_description(cde: dict) -> str:
    """Compose the CDE description from register fields.

    Section structure copied from a hand-built CDE that works well in the UI:
    Definition / Why It Matters / Governing Standards. That example also carried
    an "Important" section disambiguating the element from a similarly-named one
    — genuinely valuable, and deliberately NOT generated here, because the
    register holds nothing that supports it and inventing a disambiguation is
    worse than omitting one.

    HTML rather than plain text: the field is a rich-text editor, and paragraphs
    that arrive as one wall of text are what makes a CDE look unfinished.
    """
    parts: list[str] = []
    if cde.get("definition"):
        parts.append(f"<p><strong>Definition:</strong> {_esc(cde['definition'])}</p>")
    if cde.get("why_critical"):
        parts.append(f"<p><strong>Why It Matters:</strong> {_esc(cde['why_critical'])}</p>")

    # The paragraphs this element is driven by, so a reader can trace the CDE to
    # the regulation without leaving the page. This is the CDE-level equivalent
    # of the quotation blocks in a policy description.
    drivers = []
    for d in cde.get("driven_by") or []:
        paras = ", ".join(str(p) for p in (d.get("paragraphs") or []))
        name = d.get("principle_name") or ""
        drivers.append(f"Principle {d.get('principle')}"
                       + (f" &mdash; {_esc(name)}" if name else "")
                       + (f" (&para;{paras})" if paras else ""))
    if drivers:
        parts.append("<p><strong>Governing Standards:</strong> Derived from "
                     + "; ".join(drivers) + ".</p>")
    # `criticality_rationale` is deliberately NOT rendered. It is written for a
    # reviewer of the REGISTER, not for a steward reading a CDE — the interpreter
    # prompt asks for "the completed sentence from step 2 of the procedure", and
    # the first live CDE duly carried "...satisfying the step-2 sentence
    # directly" into a customer-visible description. It is also largely redundant
    # with why_critical. It still reaches Alation as `risk_rationale`, which is
    # the field that actually means "why this risk level".
    return "".join(parts)


def _esc(text: str) -> str:
    out = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for ch, ent in (("—", "&mdash;"), ("–", "&ndash;"), ("¶", "&para;"),
                    ("’", "&rsquo;"), ("“", "&ldquo;"), ("”", "&rdquo;")):
        out = out.replace(ch, ent)
    return "".join(c if ord(c) < 128 else f"&#{ord(c)};" for c in out)


class CDEProvisioner:
    def __init__(self, client: AlationClient, state: DeploymentState,
                 prefix: str = "", cde_token: str | None = None):
        self.c = client
        self.state = state
        self.prefix = prefix or ""
        self._cde_token = cde_token
        self._standards: list[dict] | None = None

    def prefixed(self, name: str) -> str:
        return f"{self.prefix}{name}" if self.prefix else name

    # -- auth ---------------------------------------------------------------
    def cde_token(self) -> str:
        """Reuses PolicyProvisioner's exchange rather than duplicating it.

        The two-step swap (legacy token -> CDEToken) is fiddly enough that a
        second implementation would drift from the first, and the first is the
        one that has been exercised against a live instance.
        """
        if self._cde_token:
            return self._cde_token
        from .policies import PolicyProvisioner
        self._cde_token = PolicyProvisioner(self.c, self.state).cde_token()
        return self._cde_token

    def _hdr(self) -> dict:
        return {"CDEToken": self.cde_token()}

    # -- reads --------------------------------------------------------------
    def list_standards(self) -> list[dict]:
        if self._standards is None:
            resp = self.c.get(f"{STANDARDS}?limit=100", extra_headers=self._hdr())
            self._standards = _rows(resp)
        return self._standards

    def resolve_standard(self, name: str) -> dict | None:
        """Name -> the full standard record, so callers can take `key` or `id`.

        Matched case-insensitively on the NAMESPACED name, because a standard
        inherits its source policy's title and our policies are prefixed.
        """
        want = self.prefixed(name).strip().lower()
        for s in self.list_standards():
            if (s.get("name") or "").strip().lower() == want:
                return s
        return None

    def list_cdes(self) -> list[dict]:
        resp = self.c.get(f"{CDES}?limit=100", extra_headers=self._hdr())
        return _rows(resp)

    def find_cde(self, name: str) -> dict | None:
        want = name.strip().lower()
        for c in self.list_cdes():
            if (c.get("name") or "").strip().lower() == want:
                return c
        return None

    # -- plan ---------------------------------------------------------------
    def plan(self, register: dict, attachment: dict | None = None) -> list[CDEAction]:
        """Reads only. Nothing is created."""
        actions: list[CDEAction] = []
        by_principle = ((attachment or {}).get("by_principle")) or {}

        wanted_standards: set[str] = set()
        for cde in register.get("cde_candidates") or []:
            for d in cde.get("driven_by") or []:
                for ref in by_principle.get(str(d.get("principle")), []):
                    wanted_standards.add(ref)

        for cde in register.get("cde_candidates") or []:
            ref = cde.get("ref", "?")
            name = self.prefixed(cde.get("name") or ref)
            if self.state.id_for("cde", ref):
                actions.append(CDEAction("skip", ref, name, "already created by this kit"))
            elif self.find_cde(name):
                actions.append(CDEAction("skip", ref, name, "exists on the instance, not ours"))
            else:
                actions.append(CDEAction("create", ref, name))
        return actions

    # -- apply --------------------------------------------------------------
    def apply(self, register: dict, standard_names: list[str],
              *, status: str = "DRAFT", steward_key: str | None = None,
              dry_run: bool = True) -> list[str]:
        """Create the register's CDEs as drafts, with standards attached.

        `standard_names` are UNPREFIXED policy titles; each is resolved to its
        UUID key here. A name that does not resolve ABORTS rather than creating
        CDEs without their standards: a CDE with no attestations looks created
        but governs nothing, and that is worse than a failed run because it is
        invisible.
        """
        log: list[str] = []
        if status.upper() not in CREATABLE_STATUSES:
            raise ValueError(
                f"status {status!r} cannot be set at create time — the API accepts "
                f"only {sorted(CREATABLE_STATUSES)}. Everything else is reached "
                f"through the workflow.")

        fields: list[dict] = []
        for nm in standard_names:
            std = self.resolve_standard(nm)
            if not std:
                raise RuntimeError(
                    f"standard {self.prefixed(nm)!r} not found on this instance. "
                    f"Standards are generated by CDM from a policy, in the UI — "
                    f"create it there first, then re-run.")
            st = str(std.get("status") or "").upper()
            if st != "PUBLISHED":
                raise RuntimeError(
                    f"standard {std.get('name')!r} is {st}, not PUBLISHED. CDM "
                    f"applies only published versions, and a draft standard is "
                    f"not offered when attaching to a CDE — so this would create "
                    f"CDEs with no attestations. Publish it first (note: "
                    f"publishing is irreversible).")
            fields.append({"key": std["key"]})
            log.append(f"  standard {std.get('name')} -> {std['key']} ({st})")

        for cde in register.get("cde_candidates") or []:
            ref = cde.get("ref", "?")
            name = self.prefixed(cde.get("name") or ref)
            if self.state.id_for("cde", ref) or self.find_cde(name):
                log.append(f"  = {name} already present, skipped")
                continue

            value, label = risk_from_criticality(cde.get("criticality"))
            body: dict[str, Any] = {
                "name": name,
                "description": build_description(cde),
                "status": status.upper(),
                # NOTE: no `pdes`. DATA_MAPPING discovers them — see the module
                # docstring. Asserting links here would bypass the discovery that
                # makes the demo worth watching.
            }
            if value is not None:
                body["risk_level_value"] = value
                body["risk_level_label"] = label
            if cde.get("criticality_rationale"):
                body["risk_rationale"] = cde["criticality_rationale"]
            if fields:
                body["fields"] = fields
            if steward_key:
                body["stewards"] = [{"source_key": steward_key}]

            if dry_run:
                log.append(f"  + would create {name} "
                           f"(risk {label or '-'}, {len(fields)} standard(s), "
                           f"{len(body['description'])} chars of description)")
                continue

            try:
                created = self.c.post(CDES, json_body=body, extra_headers=self._hdr())
            except (AlationError, RuntimeError) as err:
                log.append(f"  ! {name} NOT created: {str(err)[:200]}")
                continue

            cid, ckey = created.get("id"), created.get("key")
            # BOTH ids are recorded. /cde/{id}/ takes the int; the UUID is what
            # every nested structure references. Recording one and needing the
            # other is the mistake already made once with standards.
            self.state.record("cde", ref, str(cid), name,
                              key=ckey, status=created.get("status"),
                              criticality=cde.get("criticality"))
            log.append(f"  + created {name} (id={cid}, status={created.get('status')})")
        return log

    # -- discovery ----------------------------------------------------------
    def trigger(self, cde_id: str | int, action: str,
                keywords: list[str] | None = None,
                only_sources: list[str] | None = None) -> str | None:
        if action not in ACTIONS:
            raise ValueError(f"action {action!r} is not one of {sorted(ACTIONS)}")
        payload: dict[str, Any] = {}
        if keywords:
            payload["keywords"] = keywords
        if only_sources:
            payload["only_sources"] = only_sources
        body: dict[str, Any] = {"action": action}
        if payload:
            body["payload"] = payload
        resp = self.c.post(f"{CDES}{cde_id}/trigger_action/", json_body=body,
                           extra_headers=self._hdr())
        return (resp or {}).get("job_id")

    def await_job(self, job_id: str | int, attempts: int = 60,
                  delay: float = 5.0) -> dict:
        """Poll to a terminal state.

        Actions serialise per CDE — triggering a second one while the first runs
        returns 409 — so a caller looping over CDEs MUST wait here rather than
        firing them all and hoping.
        """
        last: dict = {}
        for _ in range(attempts):
            last = self.c.get(f"{JOB}{job_id}/", extra_headers=self._hdr()) or {}
            if str(last.get("status") or "").upper() in JOB_TERMINAL:
                return last
            time.sleep(delay)
        return last

    def discover_pdes(self, register: dict, only_sources: list[str],
                      dry_run: bool = True) -> list[str]:
        """DATA_MAPPING for every recorded CDE, using the register's search_terms.

        `search_terms` were written for our own PDE mapper — the interpreter
        prompt demands abbreviations, legacy names and physical column
        conventions — and turn out to be exactly what `payload.keywords` wants.
        """
        log: list[str] = []
        by_ref = {c.get("ref"): c for c in register.get("cde_candidates") or []}
        for rec in self.state.of_kind("cde"):
            ref = rec.get("ref")
            cand = by_ref.get(ref)
            # Not in the (possibly --only filtered) register: out of scope for
            # this run, not an error. Reporting it as "no search_terms" was a
            # misleading message for a condition that had not occurred.
            if cand is None:
                continue

            # Column-name variants derived from the CDE's own name, PLUS the
            # register's terms. Measured 2026-08-28: register terms alone got
            # CDE-01 seven hits (its list happened to contain the literal column
            # CPTY_ID) and CDE-03 and CDE-09 zero, because DATA_MAPPING matches
            # on column-name tokens and the register supplies business
            # vocabulary. See keyword_variants for the evidence.
            terms = keyword_variants(cand.get("name") or "",
                                     cand.get("search_terms") or [])
            if not terms:
                log.append(f"  ! {ref}: no usable search terms, skipped — an "
                           f"unscoped DATA_MAPPING would crawl the whole catalog")
                continue
            derived = [t for t in terms if t not in (cand.get("search_terms") or [])]
            if dry_run:
                log.append(f"  ~ would map {rec['name']} with {len(terms)} keyword(s) "
                           f"({len(derived)} derived from the name): "
                           f"{', '.join(terms[:5])}"
                           f"{'...' if len(terms) > 5 else ''}")
                continue
            try:
                job = self.trigger(rec["id"], "DATA_MAPPING",
                                   keywords=terms, only_sources=only_sources)
                log.append(f"  ~ {rec['name']}: DATA_MAPPING job {job} "
                           f"({len(terms)} keywords, {len(derived)} name-derived)")
                if job:
                    final = self.await_job(job)
                    log.append(f"      job {job} -> {final.get('status')}")
            except (AlationError, RuntimeError) as err:
                log.append(f"  ! {rec['name']}: {str(err)[:160]}")
        return log

    # -- destroy ------------------------------------------------------------
    def destroy(self, dry_run: bool = True,
                only: set[str] | None = None) -> list[str]:
        """Delete recorded CDEs by id.

        Genuinely reversible, unlike standards: DELETE works from any status and
        `POST /cde/{id}/restore/` exists, implying a soft delete. Still deletes
        only what this kit recorded creating, and still by recorded id.
        """
        log: list[str] = []
        records = [r for r in self.state.of_kind("cde")
                   if not only or r.get("ref") in only]
        if not records:
            return ["  nothing recorded — this kit has created no CDEs"
                    + (f" matching {sorted(only)}" if only else "")]
        for rec in records:
            if dry_run:
                log.append(f"  - would delete cde {rec['name']} (id={rec['id']})")
                continue
            try:
                self.c.delete(f"{CDES}{rec['id']}/", extra_headers=self._hdr())
            except (AlationError, RuntimeError) as err:
                log.append(f"  ! {rec['name']} (id={rec['id']}) NOT deleted: "
                           f"{str(err)[:160]}. Keeping the state record so teardown "
                           f"can retry — an un-recorded object is invisible forever.")
                continue
            self.state.forget("cde", rec["ref"])
            log.append(f"  - deleted cde {rec['name']} (id={rec['id']})")
        return log


def _rows(resp: Any) -> list[dict]:
    if isinstance(resp, list):
        return resp
    for key in ("items", "results", "data"):
        if isinstance(resp, dict) and isinstance(resp.get(key), list):
            return resp[key]
    return []
