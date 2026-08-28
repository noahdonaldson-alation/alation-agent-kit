#!/usr/bin/env python3
"""Validate agent JSON output against a schema, and check the rules a schema can't.

    python3 scripts/validate_output.py docs/runs/v0.6.0/*.json
    python3 scripts/validate_output.py --schema schemas/cde_dq_requirements.schema.json FILES

Exits non-zero if any file fails, so it drops into CI. Schema errors and
structural errors are reported separately: a schema failure means the shape is
wrong, a structural failure means the shape is right but the content is
self-inconsistent.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import Counter
from pathlib import Path

DEFAULT_SCHEMA = "schemas/cde_dq_requirements.schema.json"
MAPPING_SCHEMA = "schemas/pde_mapping.schema.json"
OBLIGATION_SCHEMA = "schemas/obligation_register.schema.json"
POLICY_BODY_SCHEMA = "schemas/policy_body.schema.json"


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from alation_agent_kit.store import extract_json  # noqa: E402


def load_json(text: str):
    """Tolerate narration and fences around the object — agents that call tools
    routinely explain themselves before answering."""
    doc = extract_json(text)
    if doc is None:
        raise json.JSONDecodeError("no JSON object found in response", text[:200], 0)
    return doc


def structural_checks(doc: dict, source: str | None = None) -> list[str]:
    """Rules JSON Schema cannot express. Dispatches on document shape — the
    pipeline has three contracts and they have different invariants.

    Dispatching matters more than it looks: running the CDE register's checks
    against an obligation register reported "0 elements at criticality 3" on a
    perfectly valid document. A false failure is worse than no check, because it
    teaches you to ignore the check."""
    if "mappings" in doc:
        return mapping_checks(doc)
    if "obligations" in doc:
        return obligation_checks(doc, source)
    if "policies" in doc and all("body_paragraphs" in p for p in doc["policies"]):
        return policy_body_checks(doc, source)
    return register_checks(doc)


def policy_body_checks(doc: dict, source: str | None = None) -> list[str]:
    """policy_body_author drafts: prose plus citation POINTERS.

    Pass --source pointing at the obligation register to get the checks that
    matter; without it only the shape-independent ones run. Note what is NOT
    checked here: quotation traceability. The agent emits no quotation text, so
    there is nothing to trace — that property is held by construction in
    authoring.assemble_policy_spec, which is the point of the design.
    """
    problems: list[str] = []
    entries = doc.get("policies") or []
    refs = [e.get("ref") for e in entries]
    dupes = {r for r in refs if refs.count(r) > 1}
    if dupes:
        problems.append(f"duplicate refs: {sorted(dupes)}")

    for e in entries:
        ref = e.get("ref", "?")
        body = " ".join(e.get("body_paragraphs") or [])
        if " should " in body:
            problems.append(f"{ref}: body says 'should' — a policy is an "
                            "obligation even where the source recommends")
        if re.search(r"<[a-z/]|&[a-z]+;|\*\*", body):
            problems.append(f"{ref}: body contains markup or HTML entities; "
                            "the assembly step adds those")

    register = None
    if source:
        try:
            register = json.loads(source[source.find("{"):source.rfind("}") + 1])
        except (ValueError, json.JSONDecodeError):
            register = None
    if not register or not register.get("obligations"):
        return problems

    by_ref = {o.get("ref"): o for o in register["obligations"]}
    missing = [r for r in by_ref if r not in refs]
    extra = [r for r in refs if r not in by_ref]
    if missing:
        problems.append(f"no policy body for {sorted(missing)} — one policy per "
                        "obligation is structural, not a judgement")
    if extra:
        problems.append(f"policy body for {sorted(set(extra))}, absent from the register")

    for e in entries:
        o = by_ref.get(e.get("ref"))
        if not o:
            continue
        ref = e["ref"]
        for c in e.get("cite") or []:
            arr = (o.get("citations") if c.get("from") == "citations"
                   else o.get("measurable_expectations")) or []
            if not isinstance(c.get("index"), int) or c["index"] >= len(arr):
                problems.append(f"{ref}: cite {c} is out of range "
                                f"({len(arr)} available)")
        # The CDM-derivability proxy, and the number that actually matters: a
        # dimension the register measured but the prose never names cannot be
        # derived into a requirement, because CDM reads only the prose.
        body = " ".join(e.get("body_paragraphs") or []).lower()
        dims = {x.get("dimension") for x in o.get("measurable_expectations") or []}
        lost = sorted(d for d in dims if d and d not in body)
        if lost:
            problems.append(f"{ref}: dimension(s) {lost} measured in the register "
                            "but never named in the policy body")
    return problems


def _norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def iter_quotes(doc: dict):
    """Every (owner_ref, kind, citation) in an obligation register."""
    for o in doc.get("obligations") or []:
        ref = o.get("ref", "?")
        for c in o.get("citations") or []:
            yield ref, "citation", c
        for e in o.get("measurable_expectations") or []:
            if e.get("citation"):
                yield ref, f"{e.get('dimension')} expectation", e["citation"]
    for x in doc.get("cross_cutting") or []:
        if x.get("citation"):
            yield x.get("ref", "?"), "cross_cutting", x["citation"]


def quote_provenance(doc: dict, source_text: str) -> list[str]:
    """Check every quotation appears VERBATIM in the source the agent was given.

    This is the check the whole "cited to the regulation" claim rests on, and
    until now it existed nowhere — the citation audit in authoring.py compares a
    policy to its register, so a quotation invented at register time is inherited
    as ground truth by everything downstream.

    Reported as NOT TRACEABLE, never as "fabricated". A mismatch has several
    causes and only one of them is invention: the model may have joined two
    non-adjacent sentences, silently skipped a list item, or substituted
    quotation marks. Naming it "fabricated" claims to know which — and on the
    first run of this check, every single mismatch turned out to be tidying
    rather than invention.
    """
    problems: list[str] = []
    src = _norm_ws(source_text)

    paras: dict[int, str] = {}
    marks = list(re.finditer(r"(?m)^(\d{1,3})\.\s", source_text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(source_text)
        paras[int(m.group(1))] = _norm_ws(source_text[m.end():end])

    for ref, kind, c in iter_quotes(doc):
        q = _norm_ws(c.get("quote") or "")
        cited = c.get("paragraphs") or []
        if not q:
            problems.append(f"{ref} [{kind}]: empty quote")
            continue
        if q not in src:
            # Locate the longest span that DOES match, so the report says which
            # end drifted rather than only that something did.
            sm = difflib.SequenceMatcher(None, q, src, autojunk=False)
            m = sm.find_longest_match(0, len(q), 0, len(src))
            pct = 100 * m.size // max(1, len(q))
            broke = "start" if m.a > 0 else "end"
            problems.append(
                f"{ref} [{kind}]: quote NOT TRACEABLE to source "
                f"({pct}% contiguous, diverges at the {broke}): {q[:70]!r}"
            )
            continue
        where = [p for p, t in paras.items() if q in t]
        if where and cited and not set(where) & set(cited):
            problems.append(
                f"{ref} [{kind}]: quote is in paragraph {where} but cited as {cited}"
            )
    return problems


def obligation_checks(doc: dict, source: str | None = None) -> list[str]:
    """Step 1: the obligation register."""
    problems: list[str] = []
    obs = doc.get("obligations") or []
    refs = {o.get("ref") for o in obs}

    if len(refs) != len(obs):
        problems.append("duplicate obligation refs")

    # The ref encodes its own principle. A disagreement means one of the two was
    # generated and the other copied, and there is no way to tell which is right.
    for o in obs:
        ref, principle = o.get("ref", "?"), o.get("principle")
        if ref.startswith("OBL-P") and principle is not None:
            if int(ref[5:]) != principle:
                problems.append(f"{ref}: ref disagrees with principle {principle}")
        if not (o.get("governable_because") or "").strip():
            problems.append(f"{ref}: no governable_because — the procedure's "
                            "output is missing, so it cannot be shown to have run")
        for e in o.get("measurable_expectations") or []:
            if not (e.get("threshold_basis") or "").strip() and e.get("threshold"):
                problems.append(f"{ref}: a {e.get('dimension')} expectation "
                                "asserts a threshold with no threshold_basis")
        # data_concepts are extraction, not inference — a concept with no
        # as_stated is the CDE-identification step leaking one stage early.
        for dc in o.get("data_concepts") or []:
            if not (dc.get("as_stated") or "").strip():
                problems.append(f"{ref}: data_concept {dc.get('concept')!r} has no "
                                "as_stated, so it cannot be shown to be in the text")

    # Required coverage: principles 2-8 either produce an obligation or are
    # explicitly accounted for in out_of_scope.
    covered = {o.get("principle") for o in obs}
    excused = {p for e in doc.get("out_of_scope") or [] for p in e.get("principles") or []}
    for p in range(2, 9):
        if p not in covered and p not in excused:
            problems.append(f"principle {p} produces no obligation and is not "
                            "named in out_of_scope — a silent omission")

    for x in doc.get("cross_cutting") or []:
        for span in x.get("spans") or []:
            if span not in refs:
                problems.append(f"{x.get('ref')}: spans unknown {span}")

    # A principle both governable and partly out of scope must say so.
    by_ref = {o.get("ref"): o.get("principle") for o in obs}
    for e in doc.get("out_of_scope") or []:
        ps = e.get("principles") or []
        also = e.get("also_obligates") or []
        for p in ps:
            if p in covered and not also:
                problems.append(
                    f"principle {p} is out_of_scope but also produces an "
                    "obligation, without also_obligates set"
                )
        # also_obligates means "THIS principle is partly governable, and here is
        # its obligation". It does not mean "here is a related obligation
        # elsewhere". Run01 under v0.1.1 pointed a principle-9 entry at
        # OBL-P03, which reads as a cross-reference and quietly turns the field
        # into two fields with one name — at which point neither the reader nor
        # the policy author can tell which sense was meant.
        for ref in also:
            if ref not in by_ref:
                problems.append(f"out_of_scope P{ps}: also_obligates {ref}, "
                                "which is not an obligation in this register")
            elif by_ref[ref] not in ps:
                problems.append(
                    f"out_of_scope P{ps}: also_obligates {ref}, which is for "
                    f"principle {by_ref[ref]} — also_obligates names THIS "
                    "principle's own obligation; use related_obligations for "
                    "a different principle's"
                )
        for ref in e.get("related_obligations") or []:
            if ref not in by_ref:
                problems.append(f"out_of_scope P{ps}: related_obligations {ref}, "
                                "which is not an obligation in this register")
            elif by_ref[ref] in ps:
                problems.append(
                    f"out_of_scope P{ps}: related_obligations {ref} is this "
                    "principle's own obligation — that is also_obligates"
                )

    if source is not None:
        problems.extend(quote_provenance(doc, source))
    return problems


def mapping_checks(doc: dict) -> list[str]:
    """Step 3: the gap analysis. The invariant that matters most is that a
    search is recorded even when it found nothing — otherwise a missed match is
    indistinguishable from an absent element."""
    problems: list[str] = []
    maps = doc.get("mappings") or []
    declared = (doc.get("source_register") or {}).get("cde_count")

    if declared and declared != len(maps):
        problems.append(
            f"register declares {declared} CDEs but only {len(maps)} mappings "
            "— every register entry needs a mapping, including not_found ones"
        )

    refs = [m.get("cde_ref") for m in maps]
    if len(set(refs)) != len(refs):
        problems.append("duplicate cde_ref in mappings")

    for m in maps:
        ref = m.get("cde_ref", "?")
        status = m.get("status")
        cands = m.get("candidates") or []

        if not (m.get("searched_for") or []):
            problems.append(f"{ref}: searched_for is empty — no record that a search happened")
        if status in ("mapped", "partial") and not cands:
            problems.append(f"{ref}: status {status!r} but no candidates")
        if status == "not_found" and cands:
            problems.append(f"{ref}: status not_found but {len(cands)} candidate(s) listed")
        if status == "not_found" and not (m.get("blockers") or []):
            problems.append(f"{ref}: not_found without any blockers explaining why")
        if status == "already_exists" and not m.get("existing_cde"):
            problems.append(f"{ref}: status already_exists but existing_cde not set")

        # A monitor must target something that was actually found.
        found = {c.get("fully_qualified_name") for c in cands}
        for mon in m.get("proposed_dq_monitors") or []:
            if not cands:
                problems.append(f"{ref}: proposes a monitor with no candidate element")
                break
            if mon.get("target") and mon["target"] not in found:
                problems.append(
                    f"{ref}: monitor targets {mon['target']!r}, which is not among "
                    "this mapping's candidates"
                )
            if not (mon.get("authority") or "").strip():
                problems.append(f"{ref}: a {mon.get('dimension')} monitor has no authority")

        for c in cands:
            if c.get("confidence") == "high" and len((c.get("why_matched") or "")) < 40:
                problems.append(
                    f"{ref}: 'high' confidence on {c.get('fully_qualified_name')} with a "
                    "thin why_matched — high requires name plus type or description"
                )

    # Summary must agree with the mappings it summarises.
    summ = doc.get("coverage_summary") or {}
    actual = Counter(m.get("status") for m in maps)
    for key in ("mapped", "partial", "not_found", "already_exists"):
        if key in summ and summ[key] != actual.get(key, 0):
            problems.append(
                f"coverage_summary.{key}={summ[key]} but {actual.get(key, 0)} mappings "
                f"have that status"
            )
    return problems


def register_checks(doc: dict) -> list[str]:
    """Step 2: the requirements register."""
    problems: list[str] = []
    cdes = doc.get("cde_candidates") or []
    refs = {c.get("ref") for c in cdes}

    if len(refs) != len(cdes):
        problems.append("duplicate cde_candidates refs")

    threes = [c for c in cdes if c.get("criticality") == 3]
    if not 3 <= len(threes) <= 6:
        problems.append(
            f"{len(threes)} elements at criticality 3 (prompt targets 4-5)"
        )

    for c in cdes:
        ref = c.get("ref", "?")
        for d in c.get("driven_by") or []:
            if not 1 <= (d.get("principle") or 0) <= 11:
                problems.append(f"{ref}: cites principle {d.get('principle')} "
                                "(only bank-facing 1-11 are valid)")
        for r in c.get("dq_requirements") or []:
            if not r.get("citation"):
                problems.append(f"{ref}: a {r.get('dimension')} check has no citation")
            if not (r.get("threshold_basis") or "").strip():
                problems.append(f"{ref}: a {r.get('dimension')} check has no threshold_basis")
            # A measurement naming physical objects means step 3's job leaked in.
            # Must match real SQL, not the English word "from" — an earlier version
            # of this check flagged "originating from manual processes" six times.
            m = (r.get("measurement") or "")
            sqlish = (
                re.search(r"\bSELECT\b[\s\S]{0,80}\bFROM\b", m, re.I)     # SELECT ... FROM
                or re.search(r"\b(?:dbo|information_schema)\.\w+", m, re.I)
                or re.search(r"\b\w+\.\w+\.\w+\b", m)                     # db.schema.table
                or re.search(r"[`\[]\w+[`\]]", m)                          # quoted identifier
            )
            if sqlish:
                problems.append(f"{ref}: measurement looks like SQL or names objects: "
                                f"{m[:60]!r}")

    # Cross-cutting must span CDEs that exist
    for x in doc.get("cross_cutting_dq") or []:
        for span in x.get("spans") or []:
            if span not in refs:
                problems.append(f"{x.get('ref')}: spans unknown {span}")
        if not (x.get("dq_requirement") or {}).get("citation"):
            problems.append(f"{x.get('ref')}: no citation")

    # A principle in out_of_scope that also drives a CDE must say so
    for o in doc.get("out_of_scope") or []:
        for p in o.get("principles") or []:
            drives = [c.get("ref") for c in cdes
                      if any(d.get("principle") == p for d in c.get("driven_by") or [])]
            if drives and not o.get("also_drives_cde"):
                problems.append(
                    f"principle {p} is out_of_scope but drives {', '.join(drives)} "
                    "without also_drives_cde set"
                )
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate agent JSON output")
    ap.add_argument("files", nargs="+")
    ap.add_argument(
        "--schema", default=None,
        help=f"Schema to validate against. Default: auto-detect from the "
             f"document's own keys, falling back to {DEFAULT_SCHEMA}. Auto-detect "
             f"exists because defaulting to the interpreter's schema silently "
             f"reported every mapper run as invalid — a false failure is worse "
             f"than no check, because it teaches you to ignore the check.")
    ap.add_argument(
        "--source", default=None,
        help="The text the agent was given, e.g. "
             "artifacts/bcbs239/bank_principles.txt. Obligation registers only. "
             "When supplied, every quotation is checked to appear VERBATIM in "
             "it. Nothing else in the pipeline verifies this: authoring.py's "
             "audit compares a policy to its register, so a quotation that drifts "
             "at register time is inherited downstream as ground truth.")
    args = ap.parse_args()

    source_text = None
    if args.source:
        sp = Path(args.source)
        if not sp.is_file():
            print(f"ERROR: --source {args.source} not found")
            return 2
        source_text = sp.read_text(encoding="utf-8")

    import jsonschema

    # One validator per schema, built lazily: the two agents in this pipeline
    # emit different contracts, and a run of mixed files is normal.
    _cache: dict[str, "jsonschema.Draft202012Validator"] = {}

    def validator_for(doc: dict) -> tuple[str, "jsonschema.Draft202012Validator"]:
        if args.schema:
            path = args.schema
        elif isinstance(doc, dict) and "mappings" in doc:
            path = MAPPING_SCHEMA
        elif isinstance(doc, dict) and "obligations" in doc:
            path = OBLIGATION_SCHEMA
        elif (isinstance(doc, dict) and doc.get("policies")
              and all("body_paragraphs" in p for p in doc["policies"])):
            path = POLICY_BODY_SCHEMA
        else:
            path = DEFAULT_SCHEMA
        if path not in _cache:
            _cache[path] = jsonschema.Draft202012Validator(
                json.loads(Path(path).read_text()))
        return path, _cache[path]

    failures = 0
    for name in args.files:
        p = Path(name)
        if not p.is_file():
            continue
        try:
            doc = load_json(p.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError as e:
            print(f"  {p.name:16} NOT JSON — {e}")
            failures += 1
            continue

        schema_path, validator = validator_for(doc)
        errs = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
        struct = structural_checks(doc, source_text)

        # Describe whichever contract this document is, not whichever one the
        # register happens to use.
        if "mappings" in doc:
            counts = Counter(m.get("status") for m in doc["mappings"])
            summary = (f"{len(doc['mappings'])} mappings "
                       f"({counts.get('mapped', 0)} mapped, "
                       f"{counts.get('partial', 0)} partial, "
                       f"{counts.get('not_found', 0)} not found)")
        elif "obligations" in doc:
            quotes = list(iter_quotes(doc))
            traced = ""
            if source_text is not None:
                src = _norm_ws(source_text)
                hit = sum(1 for _, _, c in quotes
                          if _norm_ws(c.get("quote") or "") in src)
                traced = f", {hit}/{len(quotes)} quotes traceable"
            summary = (f"{len(doc.get('obligations') or [])} obligations "
                       f"(P{','.join(str(o.get('principle')) for o in doc['obligations'])}), "
                       f"{len(doc.get('cross_cutting') or [])} cross-cutting{traced}")
        elif doc.get("policies") and all("body_paragraphs" in p
                                         for p in doc["policies"]):
            bodies = doc["policies"]
            chars = sum(len(" ".join(p.get("body_paragraphs") or []))
                        for p in bodies)
            cites = sum(len(p.get("cite") or []) for p in bodies)
            summary = (f"{len(bodies)} policy bodies "
                       f"(P{','.join(p['ref'][5:].lstrip('0') for p in bodies)}), "
                       f"{cites} citation pointers, {chars:,} chars of prose")
        else:
            summary = (f"{len(doc.get('cde_candidates') or [])} CDEs, "
                       f"{len(doc.get('cross_cutting_dq') or [])} cross-cutting")

        if not errs and not struct:
            print(f"  {p.name:26} OK    {summary}")
            continue

        failures += 1
        print(f"  {p.name:26} FAIL  {summary}")
        for e in errs[:6]:
            loc = "/".join(str(x) for x in e.path) or "(root)"
            print(f"        schema[{Path(schema_path).name}]: {loc}: {e.message[:110]}")
        if len(errs) > 6:
            print(f"        schema: ... and {len(errs) - 6} more")
        for s in struct[:6]:
            print(f"        struct: {s}")
        if len(struct) > 6:
            print(f"        struct: ... and {len(struct) - 6} more")

    total = len([f for f in args.files if Path(f).is_file()])
    print(f"\n{total - failures}/{total} valid")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
