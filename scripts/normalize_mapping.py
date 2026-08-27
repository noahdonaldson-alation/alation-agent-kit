#!/usr/bin/env python3
"""Recompute the derivable fields in a gap-analysis document.

    python3 scripts/normalize_mapping.py artifacts/mapping.json          # report
    python3 scripts/normalize_mapping.py artifacts/mapping.json --write   # fix

Rationale: `coverage_summary` counts are a function of `mappings`, and asking a
model to tally its own long output invites arithmetic errors — the first three
live runs all got them wrong by one or two. Judgement (why_matched, confidence,
blockers, assessments) stays with the model; counting belongs in code.

What it recomputes:
  * coverage_summary.mapped / partial / not_found / already_exists

What it only REPORTS, because these are judgement calls a script should not
silently overwrite:
  * a status that contradicts its candidate count
  * a monitor targeting an element absent from candidates
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from alation_agent_kit.store import extract_json  # noqa: E402

STATUSES = ("mapped", "partial", "not_found", "already_exists")


def main() -> int:
    ap = argparse.ArgumentParser(description="Recompute derivable mapping fields")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--write", action="store_true",
                    help="Write corrections back (default: report only)")
    args = ap.parse_args()

    exit_code = 0
    for name in args.files:
        p = Path(name)
        doc = extract_json(p.read_text(encoding="utf-8", errors="replace"))
        if not doc or "mappings" not in doc:
            print(f"  {p.name}: not a gap-analysis document")
            exit_code = 1
            continue

        maps = doc["mappings"]
        actual = Counter(m.get("status") for m in maps)
        summ = doc.setdefault("coverage_summary", {})

        fixed = []
        for s in STATUSES:
            want = actual.get(s, 0)
            if summ.get(s) != want:
                fixed.append(f"{s}: {summ.get(s)} -> {want}")
                summ[s] = want

        # Judgement issues: report, never rewrite.
        issues = []
        for m in maps:
            ref, status = m.get("cde_ref"), m.get("status")
            cands = m.get("candidates") or []
            names = {c.get("fully_qualified_name") for c in cands}
            if status == "not_found" and cands:
                issues.append(f"{ref}: not_found but {len(cands)} candidate(s) — "
                              f"should this be 'partial'?")
            if status in ("mapped", "partial") and not cands:
                issues.append(f"{ref}: {status} with no candidates")
            for mon in m.get("proposed_dq_monitors") or []:
                if mon.get("target") and mon["target"] not in names:
                    issues.append(f"{ref}: monitor targets an element not in candidates "
                                  f"({mon['target'].rsplit('.', 2)[-2:]}) — either add it "
                                  f"as a candidate or drop the monitor")

        total = sum(actual.values())
        declared = (doc.get("source_register") or {}).get("cde_count")
        print(f"  {p.name}: {total} mappings "
              f"({', '.join(f'{s}={actual.get(s,0)}' for s in STATUSES)})")
        if declared and declared != total:
            print(f"      ! register declared {declared} CDEs but {total} mappings present")
            exit_code = 1
        for f in fixed:
            print(f"      recomputed {f}")
        for i in issues:
            print(f"      ! {i}")
            exit_code = 1

        if args.write and fixed:
            p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")
            print(f"      wrote {p}")
        elif fixed and not args.write:
            print("      (run with --write to apply)")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
