# BCBS 239 gap analysis after the dimension SQL pack

**Date:** 2026-08-27
**Register:** `docs/runs/v0.6.0/run01.json` (interpreter v0.6.0) — same input as the
baseline, so the comparison is matched.
**Agent/prompt:** `bcbs239_pde_mapper` v0.4.0, **unchanged**. Only the warehouse
changed, so movement is attributable to the SQL pack and not to a prompt edit.
**Runs:** 3 (`artifacts/pde-mapping-postsql-0{1,2,3}.json`), compared with
`scripts/compare_mappings.py` against `artifacts/pde-mapping-v040.json`.

## Headline

| | baseline v0.4.0 | post-SQL-pack (all 3 runs) |
|---|---|---|
| mapped | 1 | **11** |
| partial | 4 | 0 |
| not_found | 6 | 0 |
| improved | — | 10 of 11 |
| regressed | — | **0** |
| unstable across runs | — | **0** |

The six absent dimensions — business line, legal entity, geography, industry,
risk type, currency — all resolved to real column-level objects, and the four
`partial`s were completed. Every CDE landed on the same status in all three runs.

## What was actually checked, not just asserted

The result is "everything passed", which is the point at which a reviewer should
get suspicious rather than pleased. Prior versions of this prompt refused to
claim matches; a version that claims all of them could have got *correct* or got
*looser*. Checks run against all three runs:

| Check | Result |
|---|---|
| Schema valid (`pde_mapping.schema.json`) | 3/3 valid |
| `coverage_summary` agrees with `mappings` (`normalize_mapping.py`) | 3/3 agree, no recount needed |
| Candidate FQNs are column-level, not table-level | 3/3: **every** FQN is `db.schema.table.column` (4 dots) |
| `searched_for` populated even on found entries | 3/3: 0 empty of 11 |
| Monitor targets match a declared candidate verbatim (v0.2.0 rule) | 3/3: 0 violations |
| Monitor targets free of placeholders/brackets (v0.3.0 rule) | 3/3: 0 violations |

`mapped` therefore means what it is supposed to mean here: a confirmed column,
not a table that plausibly contains one. That was the blocker in every earlier
run, and MDE indexing columns is what removed it.

Secondary movement, consistent with gaps genuinely closing:

- **DQ monitors 8 → 19–23**, spread across completeness (11), validity (6),
  accuracy, uniqueness, consistency, timeliness. Monitors were previously
  blocked by unconfirmed targets; there are now real columns to attach to.
- **Blockers 33 → 12–20.** Not zero, and should not be — the remainder are
  genuine caveats, not search failures.

## Two things not to oversell

**1. Confidence ratings inflated, and that is watch item 2 from the changelog.**

| | baseline | run 01 | run 02 | run 03 |
|---|---|---|---|---|
| high | 3 | 35 | 41 | 32 |
| medium | 13 | 3 | 0 | 4 |
| low | 2 | 0 | 0 | 0 |

Some rise is legitimate: `high` requires name plus type or description, and
column metadata now exists to satisfy it — the validator's "high with a thin
`why_matched`" check found no violations. But **zero `low` across ~108
candidates** means the low end of the scale is no longer discriminating. Either
the warehouse really is unambiguous (it was purpose-built, so plausible) or the
definition has stopped biting. Unresolved; do not present the confidence
distribution as evidence of quality.

**2. Status is stable, but the evidence behind it is not.**

Across the three runs there are 52 distinct candidate FQNs, only **25 present in
all three — 48% agreement**. Fourteen were named by exactly one run. The status
per CDE never wavered, but *which* column supports it does.

The likely cause is benign: the warehouse now has bronze/silver/gold copies of
the same concept (`exposure_raw` / `exposure_clean` / `fact_risk_exposure`), so
several genuinely valid candidates exist and the agent picks different layers on
different runs. But for a customer-facing deliverable, naming different tables
each run undercuts trust. Worth a v0.5.0 rule — prefer the gold/curated layer
and name upstream copies as lineage rather than as alternative candidates.

## Tooling fixed while verifying this

- `scripts/compare_mappings.py` is new: the existing `compare_runs.py` parses
  the interpreter's markdown summary table and cannot read mapper JSON. It
  reports improvement, regression, cross-run instability, and baseline-only
  elements, and never silently drops an unparseable file.
- `scripts/validate_output.py` defaulted to the **interpreter's** schema, so it
  reported every mapper run — including the baseline — as invalid. It now
  auto-detects the contract from the document's keys and prints which schema it
  used. A false failure is worse than no check: it teaches you to ignore the
  check.

## Standing caveat

Three runs is enough to separate a real change from sampling noise on status,
and it did. It is not enough to characterise the confidence-rating or
candidate-selection variance above; those numbers are directional.
