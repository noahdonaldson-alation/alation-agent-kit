#!/usr/bin/env python3
"""Compare CDE sets across several runs of the interpreter to measure stability.

A single run cannot tell you whether a weakness is in the prompt or is sampling
noise. This parses the summary table out of N run files and reports which CDEs
are stable, which churn, and how much the criticality ratings move.

    python scripts/compare_runs.py docs/runs/*.md
    python scripts/compare_runs.py artifacts/runs/*.md --json out.json

Reads the `| CDE-01 | Name | 3 | 2, 4 | dims |` summary table, so it depends on
the prompt continuing to emit section 5. If a file yields 0 CDEs, that's the
first thing to check.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Concept buckets. Runs name the same element differently — "Reporting Date /
# Position Date" vs "Position / Valuation Date (As-of Date)" — so match on
# keywords rather than exact strings. Order matters: first match wins.
BUCKETS: list[tuple[str, tuple[str, ...]]] = [
    # Most specific first. "Transaction Currency" must not fall into the
    # transaction-identifier bucket, so currency is tested before it, and the
    # identifier bucket requires an id-ish word rather than bare "transaction".
    ("Currency / FX rate",           ("currency", "conversion rate", "exchange rate", "fx")),
    ("Counterparty identifier",      ("counterparty",)),
    ("Legal entity identifier",      ("legal entity", "booking entity")),
    ("Exposure amount",              ("exposure amount", "notional", "carrying value")),
    ("Position / reporting date",    ("date",)),
    ("Risk classification",          ("risk classification", "risk type")),
    ("Business line",                ("business line", "segment")),
    ("Geography / country",          ("geograph", "country", "jurisdiction")),
    ("Industry / sector",            ("industry", "sector")),
    ("Product / instrument type",    ("product", "instrument type")),
    ("Transaction / instrument id",  ("transaction id", "transaction reference",
                                      "transaction / instrument", "instrument identifier",
                                      "trade id", "deal id", "position id")),
    ("Collateral / netting",         ("collateral", "netting")),
    ("Calculated risk measure",      ("risk measure", "risk metric", "calculated")),
    ("Source system / lineage",      ("source system", "system of record", "lineage",
                                      "data source")),
    ("Risk limit / utilisation",     ("limit",)),
    ("Liquidity indicator",          ("liquidity", "cash flow", "settlement")),
]


def bucket_for(name: str) -> str:
    n = name.lower()
    for label, keys in BUCKETS:
        if any(k in n for k in keys):
            return label
    return f"OTHER: {name.strip()}"


ROW = re.compile(
    r"\|\s*(CDE-\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|"
)


def parse_run(path: Path) -> dict:
    """Parse one run file, defending against duplicated content.

    Output files can contain the answer more than once (a streaming-parser
    artifact) or echo the input. Deduplicate summary-table rows by CDE ref,
    keeping the first, and report how much duplication was found — a run that
    needed heavy deduplication should not be trusted for content analysis.
    """
    text = path.read_text(errors="replace")

    raw_rows = [
        (ref, name, crit, principles, dims)
        for ref, name, crit, principles, dims in ROW.findall(text)
        if not name.lower().startswith(("name", "---"))
    ]

    cdes: list[dict] = []
    seen_refs: set[str] = set()
    for ref, name, crit, principles, dims in raw_rows:
        if ref in seen_refs:
            continue  # duplicate copy of the table
        seen_refs.add(ref)
        cdes.append({
            "ref": ref,
            "name": name.strip(),
            "bucket": bucket_for(name),
            "criticality": int(crit),
            "principles": sorted({int(p) for p in re.findall(r"\d+", principles)}),
            "dq_dimensions": sorted(
                d.strip().lower() for d in dims.split(",") if d.strip()
            ),
        })

    # Duplication signals, so a contaminated file can't quietly skew the stats.
    copies = round(len(raw_rows) / len(cdes), 1) if cdes else 0
    echoes_input = bool(
        re.match(r"\s*BCBS 239 [—-] Principles for effective", text)
        or "Basel Committee on Banking Supervision, January 2013\nSource:" in text[:400]
    )

    return {
        "file": path.name,
        "cdes": cdes,
        "rows_found": len(raw_rows),
        "duplication_factor": copies,
        "echoes_input": echoes_input,
        "cross_cutting": sorted(set(re.findall(r"XDQ-\d+", text))),
        "has_out_of_scope": bool(re.search(r"out of scope", text, re.I)),
        "suspect": copies > 1.2 or echoes_input,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Measure CDE stability across runs")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", help="Also write the comparison as JSON")
    args = ap.parse_args()

    runs = [parse_run(Path(f)) for f in args.files]
    runs = [r for r in runs if r["cdes"]] or runs
    n = len(runs)
    if n < 2:
        print("Need at least 2 parseable runs to compare.")
        for r in runs:
            print(f"  {r['file']}: {len(r['cdes'])} CDEs")
        return 1

    print(f"Comparing {n} runs\n")
    for r in runs:
        crit = Counter(c["criticality"] for c in r["cdes"])
        flags = []
        if r["duplication_factor"] > 1.2:
            flags.append(f"{r['duplication_factor']}x DUPLICATED")
        if r["echoes_input"]:
            flags.append("ECHOES INPUT")
        print(f"  {r['file']:34} {len(r['cdes']):>2} CDEs   "
              f"crit3={crit[3]} crit2={crit[2]} crit1={crit[1]}   "
              f"{len(r['cross_cutting'])} cross-cutting   "
              f"out-of-scope={'yes' if r['has_out_of_scope'] else 'NO'}"
              + (f"   <-- {', '.join(flags)}" if flags else ""))

    suspect = [r for r in runs if r["suspect"]]
    if suspect:
        print(
            f"\n  !! {len(suspect)} of {n} files show duplicated or echoed content.\n"
            f"     Rows were deduplicated by CDE ref so the counts below are usable,\n"
            f"     but treat these files as unreliable for reading prose, and fix the\n"
            f"     capture before drawing conclusions about the prompt."
        )

    seen: dict[str, list[dict]] = defaultdict(list)
    for r in runs:
        for c in r["cdes"]:
            seen[c["bucket"]].append({"run": r["file"], **c})

    core = {b: v for b, v in seen.items() if len({x["run"] for x in v}) == n}
    partial = {b: v for b, v in seen.items() if len({x["run"] for x in v}) < n}

    print(f"\n{'='*74}\nSTABLE — present in all {n} runs ({len(core)})\n{'='*74}")
    for b in sorted(core):
        crits = [x["criticality"] for x in core[b]]
        drift = "" if len(set(crits)) == 1 else f"   <- criticality varies {crits}"
        print(f"  {b:32} crit={crits[0] if len(set(crits))==1 else '/'.join(map(str,crits))}{drift}")

    print(f"\n{'='*74}\nUNSTABLE — missing from at least one run ({len(partial)})\n{'='*74}")
    if not partial:
        print("  none — the set is fully reproducible")
    for b in sorted(partial, key=lambda k: -len({x['run'] for x in partial[k]})):
        runs_with = {x["run"] for x in partial[b]}
        crits = sorted({x["criticality"] for x in partial[b]})
        flag = "  ** was rated criticality 3 **" if 3 in crits else ""
        print(f"  {b:32} in {len(runs_with)}/{n} runs  crit={crits}{flag}")

    stability = len(core) / max(len(seen), 1)
    print(f"\n{'='*74}")
    print(f"Stability: {len(core)}/{len(seen)} concepts appear in every run  ({stability:.0%})")
    dropped3 = [b for b in partial if 3 in {x['criticality'] for x in partial[b]}]
    if dropped3:
        print(f"\nCriticality-3 elements that did NOT appear in every run: {len(dropped3)}")
        for b in dropped3:
            print(f"  - {b}")
        print("  A top-criticality element that comes and goes is the strongest")
        print("  argument for anchoring the set in the prompt.")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "runs": runs,
            "core": sorted(core),
            "unstable": {b: sorted({x["run"] for x in v}) for b, v in partial.items()},
            "stability": stability,
        }, indent=2))
        print(f"\nWrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
