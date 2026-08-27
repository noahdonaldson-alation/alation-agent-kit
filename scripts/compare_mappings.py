#!/usr/bin/env python3
"""Compare gap-analysis runs of bcbs239_pde_mapper, and against a baseline.

    python3 scripts/compare_mappings.py artifacts/pde-mapping-postsql-*.json \
        --baseline artifacts/pde-mapping-v040.json

Why this exists separately from compare_runs.py: that script reads the
interpreter's markdown summary table. The mapper emits JSON with a `mappings`
array, so it needs its own reader.

What it answers, in order of importance:

  1. Did a not_found become mapped? That is the whole point of loading the SQL
     pack, and it is the only claim worth making about this comparison.
  2. Is the change stable across runs, or did one lucky run find a table? A
     single run cannot tell a fix from sampling noise -- the mapper searches,
     and searches vary.
  3. Did anything REGRESS -- something previously found now missing? A gap
     analysis that loses ground silently is worse than one that never improved.

Matching CDEs across runs is by name, normalised, because the mapper does not
emit stable cde_ids (every run so far has emitted null for cde_id) and run-to-run
naming drifts slightly. Anything unmatched is reported, never silently dropped --
that bug cost us two of nine runs once already.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from alation_agent_kit.store import extract_json  # noqa: E402

STATUS_ORDER = ["mapped", "partial", "not_found", "already_exists"]
# Ranked so "did this improve or regress" is a comparison, not a lookup table.
STATUS_RANK = {"not_found": 0, "partial": 1, "mapped": 2, "already_exists": 3}


def norm(name: str) -> str:
    """Loose key for matching the same concept across runs.

    Drops parentheticals and everything after a slash, so
    "Geography / Country of Risk" and "Geography (Country of Risk)" agree.
    """
    n = (name or "").lower()
    n = re.sub(r"\(.*?\)", " ", n)
    n = n.split("/")[0]
    n = re.sub(r"[^a-z0-9 ]", " ", n)
    return " ".join(n.split())


def load(path: Path) -> dict:
    """Read one run. Raises on anything unusable — never returns a partial doc.

    Note `extract_json` signals failure by RETURNING None, not by raising. An
    earlier version of this function passed that None straight through, so an
    unreadable file crashed several steps later instead of being reported as
    unparseable — defeating the point of collecting failures.
    """
    raw = path.read_text(encoding="utf-8")
    doc = None
    try:
        doc = extract_json(raw)
    except Exception:  # noqa: BLE001 - tolerant reader, fall through to regex
        doc = None
    if doc is None:
        m = re.search(r"\{.*\}", raw, re.S)
        if not m:
            raise ValueError("no JSON object found")
        doc = json.loads(m.group(0))
    if not isinstance(doc, dict):
        raise ValueError(f"expected a JSON object, got {type(doc).__name__}")
    if "mappings" not in doc:
        raise ValueError("no `mappings` key — is this mapper output?")
    return doc


def mappings_of(doc: dict) -> dict[str, dict]:
    out = {}
    for m in doc.get("mappings") or []:
        key = norm(m.get("cde_name") or m.get("name") or "")
        if key:
            out[key] = m
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--baseline", type=Path,
                    help="Prior run to measure movement against")
    ap.add_argument("--json", type=Path, help="Write the comparison as JSON")
    args = ap.parse_args()

    docs, failed = [], []
    for p in args.runs:
        try:
            docs.append((p, load(p)))
        except Exception as exc:  # noqa: BLE001
            failed.append((p, str(exc)[:120]))

    if failed:
        # Never hide an unparseable file: a quietly dropped run silently shrinks
        # the sample and flatters the result.
        print("UNPARSEABLE FILES (excluded from the comparison):")
        for p, why in failed:
            print(f"  ! {p}: {why}")
        print()
    if not docs:
        print("No parseable runs.")
        return 1

    base = None
    if args.baseline:
        try:
            base = mappings_of(load(args.baseline))
        except Exception as exc:  # noqa: BLE001
            print(f"! baseline unreadable ({exc}); comparing runs only\n")

    per_run = [(p, mappings_of(d)) for p, d in docs]
    all_keys = sorted({k for _, m in per_run for k in m})

    print(f"{len(per_run)} run(s) compared"
          + (f", baseline {args.baseline.name}" if base else "") + "\n")

    # -- coverage per run --------------------------------------------------
    print("Coverage per run (recomputed from mappings, not trusting the "
          "model's own tally):")
    for p, m in per_run:
        c = Counter((x.get("status") or "?") for x in m.values())
        print(f"  {p.name:44} " + "  ".join(
            f"{s}={c.get(s, 0)}" for s in STATUS_ORDER) + f"  n={len(m)}")
    if base:
        c = Counter((x.get("status") or "?") for x in base.values())
        print(f"  {'BASELINE ' + args.baseline.name:44} " + "  ".join(
            f"{s}={c.get(s, 0)}" for s in STATUS_ORDER) + f"  n={len(base)}")
    print()

    # -- per-CDE stability and movement ------------------------------------
    print("Per-CDE status across runs"
          + (" (baseline -> runs)" if base else "") + ":")
    improved, regressed, unstable = [], [], []
    rows = []
    for k in all_keys:
        statuses = [m.get(k, {}).get("status", "absent") for _, m in per_run]
        display = next((m[k].get("cde_name") for _, m in per_run if k in m), k)
        b = base.get(k, {}).get("status") if base else None

        uniq = set(statuses)
        flag = ""
        if len(uniq) > 1:
            flag = "  <- UNSTABLE across runs"
            unstable.append(display)
        elif b:
            only = statuses[0]
            if STATUS_RANK.get(only, -1) > STATUS_RANK.get(b, -1):
                flag = f"  <- IMPROVED from {b}"
                improved.append((display, b, only))
            elif STATUS_RANK.get(only, -1) < STATUS_RANK.get(b, -1):
                flag = f"  <- REGRESSED from {b}"
                regressed.append((display, b, only))

        cands = [len(m.get(k, {}).get("candidates") or []) for _, m in per_run]
        prefix = f"{b:>13} -> " if base else ""
        print(f"  {str(display)[:46]:46} {prefix}"
              f"{', '.join(statuses)}  cands={cands}{flag}")
        rows.append({"cde": display, "baseline": b, "runs": statuses,
                     "candidates": cands})

    # -- the headline ------------------------------------------------------
    print()
    if base:
        print(f"IMPROVED : {len(improved)}")
        for name, b, a in improved:
            print(f"  + {name}  ({b} -> {a})")
        print(f"REGRESSED: {len(regressed)}")
        for name, b, a in regressed:
            print(f"  - {name}  ({b} -> {a})")
        if not improved and not regressed:
            print("  (no movement against the baseline)")
    if unstable:
        print(f"\nUNSTABLE : {len(unstable)} CDE(s) disagree across runs — treat "
              f"their status as unproven, not as a result:")
        for name in unstable:
            print(f"  ? {name}")

    # Elements only the baseline knew about would otherwise vanish from view.
    if base:
        dropped = [k for k in base if k not in all_keys]
        if dropped:
            print(f"\nPRESENT IN BASELINE, ABSENT FROM EVERY RUN: {len(dropped)}")
            for k in dropped:
                print(f"  ! {base[k].get('cde_name') or k}")

    if args.json:
        args.json.write_text(json.dumps(
            {"runs": [str(p) for p, _ in per_run],
             "baseline": str(args.baseline) if base else None,
             "unparseable": [{"file": str(p), "error": e} for p, e in failed],
             "rows": rows,
             "improved": improved, "regressed": regressed,
             "unstable": unstable}, indent=2), encoding="utf-8")
        print(f"\nWrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
