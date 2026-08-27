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
import json
import re
import sys
from pathlib import Path

DEFAULT_SCHEMA = "schemas/cde_dq_requirements.schema.json"


def load_json(text: str):
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?|```$", "", s, flags=re.M).strip()
    return json.loads(s)


def structural_checks(doc: dict) -> list[str]:
    """Rules JSON Schema cannot express."""
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
    ap.add_argument("--schema", default=DEFAULT_SCHEMA)
    args = ap.parse_args()

    import jsonschema
    schema = json.loads(Path(args.schema).read_text())
    validator = jsonschema.Draft202012Validator(schema)

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

        errs = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
        struct = structural_checks(doc)
        n_cde = len(doc.get("cde_candidates") or [])
        n_xdq = len(doc.get("cross_cutting_dq") or [])

        if not errs and not struct:
            print(f"  {p.name:16} OK    {n_cde} CDEs, {n_xdq} cross-cutting")
            continue

        failures += 1
        print(f"  {p.name:16} FAIL  {n_cde} CDEs, {n_xdq} cross-cutting")
        for e in errs[:6]:
            loc = "/".join(str(x) for x in e.path) or "(root)"
            print(f"        schema: {loc}: {e.message[:110]}")
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
