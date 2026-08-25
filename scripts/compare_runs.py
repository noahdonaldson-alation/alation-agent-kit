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
    # The reconciliation key (prompt category 7) gets many names: "GL
    # Reconciliation Key", "GL / System-of-Record Reconciliation Key",
    # "Transaction / Instrument Identifier". Catch it first, before the lineage
    # bucket claims anything containing "system-of-record".
    ("Reconciliation key",           ("reconciliation key", "reconciliation")),
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
    ("Source system / lineage",      ("source system", "system of record",
                                      "system-of-record", "lineage", "data source",
                                      "provenance", "manual", "euc")),
    ("Risk limit / utilisation",     ("limit",)),
    ("Liquidity indicator",          ("liquidity", "cash flow", "settlement")),
    # Added after observing them as OTHER across 8 runs. Naming varies between
    # runs for the same concept ("MTM Value" vs "Mark-to-Market Value"), and
    # counting those as distinct concepts overstates instability.
    ("Market risk position / MTM",   ("mark-to-market", "mtm", "market risk position")),
    ("Maturity / tenor",             ("maturity", "tenor")),
    ("Off-balance-sheet indicator",  ("off-balance", "contingent exposure")),
    ("Data owner / steward",         ("steward", "data owner")),
    # Kept separate from the transaction identifier: a credit facility id and a
    # trade id are adjacent but not the same thing. Worth watching whether the
    # model treats them interchangeably.
    ("Instrument / facility id",     ("facility identifier", "facility id")),
]


def bucket_for(name: str) -> str:
    n = name.lower()
    for label, keys in BUCKETS:
        if any(k in n for k in keys):
            return label
    return f"OTHER: {name.strip()}"


# Tolerant of markdown emphasis and trailing commentary in the criticality cell:
# runs variously write `3`, `**3**`, and `3 — invalidates the figure`. Demanding a
# bare digit silently dropped two of nine runs.
ROW = re.compile(
    r"\|\s*(CDE-\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|"
)


def parse_criticality(cell: str) -> int | None:
    """First 1-3 digit in the cell, ignoring bold markers and prose."""
    for m in re.finditer(r"\d+", cell):
        v = int(m.group())
        if 1 <= v <= 3:
            return v
    return None


def parse_principles(cell: str) -> list[int]:
    """Principle numbers only.

    Cells look like `2, 4` but also `2 (¶33), 4 (¶41-43)` and `P2 (¶33)`.
    Strip parentheticals first, or paragraph numbers get read as principles.
    """
    stripped = re.sub(r"\([^)]*\)", "", cell)
    return sorted({
        int(m) for m in re.findall(r"\d+", stripped) if 1 <= int(m) <= 14
    })


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
            "criticality": parse_criticality(crit),
            "principles": parse_principles(principles),
            "dq_dimensions": sorted(
                d.strip().lower().strip("*") for d in dims.split(",") if d.strip()
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

    all_runs = [parse_run(Path(f)) for f in args.files]

    # NEVER silently drop a file. Unparseable output is a finding, not noise —
    # dropping it once hid two of nine runs and inflated the stability number.
    unparsed = [r for r in all_runs if not r["cdes"]]
    runs = [r for r in all_runs if r["cdes"]]
    if unparsed:
        print(f"!! {len(unparsed)} of {len(all_runs)} files yielded NO parseable "
              f"summary table and are excluded:")
        for r in unparsed:
            print(f"     {r['file']}  ({r['rows_found']} candidate rows)")
        print("   Check the summary-table format in those files before trusting "
              "the numbers below.\n")
    if not runs:
        print("No parseable runs.")
        return 1
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
