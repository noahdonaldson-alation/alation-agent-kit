#!/usr/bin/env python3
"""Render pipeline JSON as a readable markdown report.

    python3 scripts/render_report.py docs/runs/v0.6.0/run01.json -o register.md
    python3 scripts/render_report.py artifacts/pde-mapping-v040.json -o gaps.md

Dispatches on document shape, so it handles both contracts:
  * a requirements register (step 2) -> the audit view of what the regulation
    demands and why
  * a gap analysis (step 3) -> what this instance has against that register

The JSON is the source of truth; this is a view of it. Nothing here adds
information, and anything it cannot show is a gap in the JSON, not in the
renderer.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from alation_agent_kit.store import extract_json  # noqa: E402

CRIT = {3: "3 — figure invalid", 2: "2 — figure degraded", 1: "1 — supporting"}


def cite(c: dict) -> str:
    """Principle 4 (¶41, 43)"""
    paras = ", ".join(str(p) for p in c.get("paragraphs") or [])
    name = c.get("principle_name")
    head = f"Principle {c.get('principle')}" + (f" ({name})" if name else "")
    return f"{head} ¶{paras}" if paras else head


def quote_block(text: str | None) -> list[str]:
    return [f"> *{text.strip()}*", ""] if text else []


# --------------------------------------------------------------------------
# Step 2: requirements register
# --------------------------------------------------------------------------
def render_register(d: dict) -> str:
    reg = d.get("regulation", {})
    cdes = d.get("cde_candidates") or []
    out: list[str] = [
        f"# {reg.get('title', 'Regulation')} — data requirements",
        "",
        f"**Source:** {reg.get('source_url', '')}  ",
        f"**Published:** {reg.get('published', 'n/a')}  ",
        f"**Rendered:** {date.today().isoformat()}",
        "",
        "> Interpretation only. Nothing here has been checked against a catalog;",
        "> every claim carries the paragraph it rests on so it can be verified.",
        "",
    ]
    if reg.get("scope_note"):
        out += ["## Scope", "", reg["scope_note"], ""]

    if d.get("objectives"):
        out += ["## What the regulation is trying to achieve", ""]
        for o in d["objectives"]:
            paras = ", ".join(str(p) for p in o.get("paragraphs") or [])
            out.append(f"- {o['objective']} *(¶{paras})*")
        out.append("")

    out += ["## Critical data elements", "",
            "| Ref | Element | Criticality | Principles | DQ dimensions |",
            "|---|---|---|---|---|"]
    for c in cdes:
        prins = ", ".join(str(x.get("principle")) for x in c.get("driven_by") or [])
        dims = ", ".join(sorted({r.get("dimension", "")
                                 for r in c.get("dq_requirements") or []}))
        out.append(f"| {c.get('ref')} | {c.get('name')} | {c.get('criticality')} "
                   f"| {prins} | {dims} |")
    out.append("")

    for c in cdes:
        out += [f"### {c.get('ref')} — {c.get('name')}", ""]
        out += [f"**Definition.** {c.get('definition')}", ""]
        out += [f"**Why critical.** {c.get('why_critical')}", ""]
        if c.get("risk_types"):
            out += [f"**Risk types.** {', '.join(c['risk_types'])}", ""]
        out += [f"**Criticality {c.get('criticality')}.** "
                f"{c.get('criticality_rationale')}", ""]

        out += ["**Required by:**", ""]
        for x in c.get("driven_by") or []:
            out.append(f"- {cite(x)}")
            if x.get("quote"):
                out += ["", f"  > *{x['quote'].strip()}*", ""]
        out.append("")

        if c.get("search_terms"):
            out += [f"**Look for in a catalog:** "
                    f"{', '.join('`' + t + '`' for t in c['search_terms'])}", ""]

        reqs = c.get("dq_requirements") or []
        if reqs:
            out += ["**Data quality requirements**", "",
                    "| Dimension | Must be true | Measured by | Threshold | Authority |",
                    "|---|---|---|---|---|"]
            for r in reqs:
                auth = cite(r.get("citation", {})) if r.get("citation") else "—"
                out.append(f"| {r.get('dimension')} | {r.get('rule_intent')} "
                           f"| {r.get('measurement')} | {r.get('threshold')} | {auth} |")
            out.append("")
            for r in reqs:
                if r.get("threshold_basis"):
                    out.append(f"- *{r.get('dimension')} threshold:* "
                               f"{r['threshold_basis']}")
            out.append("")

    if d.get("cross_cutting_dq"):
        out += ["## Cross-cutting data quality requirements", "",
                "These span several elements and cannot be expressed by monitoring "
                "any one of them.", ""]
        for x in d["cross_cutting_dq"]:
            r = x.get("dq_requirement", {})
            out += [f"### {x.get('ref')} — {x.get('name')}", ""]
            if x.get("description"):
                out += [x["description"], ""]
            out += [f"**Spans:** {', '.join(x.get('spans') or [])}  ",
                    f"**Dimension:** {r.get('dimension')}  ",
                    f"**Must be true:** {r.get('rule_intent')}  ",
                    f"**Measured by:** {r.get('measurement')}  ",
                    f"**Threshold:** {r.get('threshold')} — {r.get('threshold_basis','')}  ",
                    f"**Authority:** {cite(r.get('citation', {}))}", ""]

    if d.get("out_of_scope"):
        out += ["## What a catalog cannot deliver", "",
                "Stating this plainly is what makes the rest trustworthy.", ""]
        for o in d["out_of_scope"]:
            prins = ", ".join(str(p) for p in o.get("principles") or [])
            head = o.get("topic") or f"Principles {prins}"
            out += [f"### {head} *(Principles {prins})*", "",
                    o.get("why_not_addressable", ""), "",
                    f"**What is needed instead:** {o.get('what_is_needed_instead','')}", ""]
            if o.get("also_drives_cde"):
                out += [f"*Note: these principles also drive "
                        f"{', '.join(o['also_drives_cde'])} — the data element is in "
                        f"scope even though the reporting obligation is not.*", ""]
    return "\n".join(out).rstrip() + "\n"


# --------------------------------------------------------------------------
# Step 3: gap analysis
# --------------------------------------------------------------------------
STATUS_LABEL = {
    "mapped": "Mapped",
    "partial": "Partial — unconfirmed",
    "not_found": "**Not found**",
    "already_exists": "Already exists",
}


def render_mapping(d: dict) -> str:
    src = d.get("source_register", {})
    inst = d.get("instance", {})
    cs = d.get("coverage_summary", {})
    maps = d.get("mappings") or []

    out: list[str] = [
        f"# {src.get('regulation_id', 'Regulation')} — data readiness gap analysis",
        "",
        f"**Rendered:** {date.today().isoformat()}  ",
        f"**Requirements assessed:** {src.get('cde_count', len(maps))}  ",
        f"**Critical data elements already defined:** {inst.get('existing_cde_count', 'n/a')}",
        "",
        "> Suggestion only. Nothing in this report has been created; every element "
        "named below was returned by a catalog search, and everything searched for "
        "and not found is recorded as such.",
        "",
        "## Coverage",
        "",
        "| Outcome | Count | Meaning |",
        "|---|---|---|",
        f"| Mapped | {cs.get('mapped', 0)} | a confirmed physical element exists |",
        f"| Partial | {cs.get('partial', 0)} | plausible, needs a data owner to confirm |",
        f"| Not found | {cs.get('not_found', 0)} | searched, nothing matched |",
        f"| Already governed | {cs.get('already_exists', 0)} | a CDE already covers it |",
        "",
    ]
    if cs.get("honest_assessment"):
        out += ["### Assessment", "", cs["honest_assessment"], ""]

    if inst.get("data_sources_seen"):
        out += ["### What was searched", ""]
        for s in inst["data_sources_seen"]:
            out.append(f"- {s}")
        out.append("")
    if inst.get("scope_caveat"):
        out += [f"*Scope caveat: {inst['scope_caveat']}*", ""]

    gaps = [m for m in maps if m.get("status") == "not_found"]
    if gaps:
        out += ["## Gaps — required elements not present", "",
                "These are the findings. Each was searched for with the terms listed "
                "and nothing in the catalog matched.", ""]
        for m in gaps:
            out += [f"### {m.get('cde_ref')} — {m.get('cde_name')}", "",
                    f"**Searched for:** "
                    f"{', '.join('`' + t + '`' for t in m.get('searched_for') or [])}", ""]
            for b in m.get("blockers") or []:
                out.append(f"- {b}")
            out.append("")

    out += ["## Element by element", "",
            "| Ref | Element | Outcome | Candidates | Monitors |",
            "|---|---|---|---|---|"]
    for m in maps:
        out.append(f"| {m.get('cde_ref')} | {m.get('cde_name')} "
                   f"| {STATUS_LABEL.get(m.get('status'), m.get('status'))} "
                   f"| {len(m.get('candidates') or [])} "
                   f"| {len(m.get('proposed_dq_monitors') or [])} |")
    out.append("")

    for m in maps:
        if m.get("status") == "not_found":
            continue  # already covered under Gaps
        out += [f"### {m.get('cde_ref')} — {m.get('cde_name')}", "",
                f"*{STATUS_LABEL.get(m.get('status'), '')}*", ""]

        ex = m.get("existing_cde")
        if ex:
            out += [f"**Existing CDE:** {ex.get('name')} "
                    f"({ex.get('linked_pde_count', 0)} linked elements)", "",
                    ex.get("assessment", ""), ""]

        cands = m.get("candidates") or []
        if cands:
            out += ["| Physical element | Type | Confidence | Why |",
                    "|---|---|---|---|"]
            for c in cands:
                dt = f" ({c['data_type']})" if c.get("data_type") else ""
                out.append(f"| `{c.get('fully_qualified_name')}`{dt} "
                           f"| {c.get('object_type')} | {c.get('confidence')} "
                           f"| {c.get('why_matched')} |")
            out.append("")
            for c in cands:
                if c.get("concerns"):
                    out.append(f"- *Concern on `{c.get('fully_qualified_name')}`:* "
                               f"{c['concerns']}")
            out.append("")

        mons = m.get("proposed_dq_monitors") or []
        if mons:
            out += ["**Proposed monitoring**", "",
                    "| Dimension | Target | Must be true | Threshold | Authority | Already monitored |",
                    "|---|---|---|---|---|---|"]
            for mo in mons:
                out.append(f"| {mo.get('dimension')} | `{mo.get('target')}` "
                           f"| {mo.get('rule_intent')} | {mo.get('threshold')} "
                           f"| {mo.get('authority')} "
                           f"| {mo.get('existing_monitor') or 'no'} |")
            out.append("")

        if m.get("blockers"):
            out += ["**Blockers**", ""]
            for b in m["blockers"]:
                out.append(f"- {b}")
            out.append("")

    if cs.get("recommended_next_actions"):
        out += ["## Recommended next actions", ""]
        for a in cs["recommended_next_actions"]:
            out.append(f"1. {a}")
        out.append("")

    out += ["---", "",
            "*Generated from the pipeline's JSON output. The JSON is the source of "
            "truth; this is a view of it.*"]
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Render pipeline JSON as markdown")
    ap.add_argument("file")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    doc = extract_json(Path(args.file).read_text(encoding="utf-8", errors="replace"))
    if not doc:
        print(f"No JSON object found in {args.file}", file=sys.stderr)
        return 1

    if "mappings" in doc:
        md, kind = render_mapping(doc), "gap analysis"
    elif "cde_candidates" in doc:
        md, kind = render_register(doc), "requirements register"
    else:
        print(f"Unrecognised document shape: keys {sorted(doc)[:6]}", file=sys.stderr)
        return 1

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"Rendered {kind}: {args.output} ({len(md):,} chars)")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
