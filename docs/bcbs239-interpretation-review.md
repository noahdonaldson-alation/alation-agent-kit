# Review: BCBS 239 CDE/DQ interpretation, first run

**Date:** 2026-08-24 · **Agent:** `bcbs239_cde_dq_interpreter` (Bedrock Claude Sonnet 4.6)
**Prompt:** `prompts/bcbs239_cde_dq_interpreter.md` sha `8673a293482e`
**Input:** `artifacts/bcbs239/bank_principles.txt` — P1–P11, 25,955 chars

---

## Verdict

**Usable as a starting register.** 12 CDEs, 4 cross-cutting DQ requirements, and a
credible out-of-scope section. The material risk with this kind of output is
fabricated authority — confident-sounding citations that don't exist — and that
risk did not materialise.

## Citation verification

24 quoted phrases were checked programmatically against the extracted regulation
text, matching on whitespace-normalised substrings and confirming each quote sits
in the paragraph it was attributed to.

| Result | Count |
|---|---|
| Verified, correct paragraph | **24** |
| Attributed to the wrong paragraph | 0 |
| Not present in the document | 0 |

Spot-checked across ¶30, 32, 33, 35, 36, 37, 39, 40, 41, 43, 44, 46, 50, 53, 57,
67, 69, 71 — i.e. all four sections plus the out-of-scope reasoning.

**One caveat for audit use.** PDF extraction inlines footnote markers, so ¶33
reads *"integrated 16 data taxonomies"* in our text. The agent quoted it as
*"integrated data taxonomies"* — correct prose, but **not byte-identical to the
source**. For a compliance artifact where quotes must be literal, either clean
footnote markers during extraction or treat quotes as indicative and cite by
paragraph. Worth deciding before this output goes near an auditor.

## What it got right

- **Discipline on the inclusion tests.** The 12 candidates are joining keys,
  reconciliation keys, aggregation dimensions and calculated outputs — not a dump
  of every field a bank owns. CDE-08 (Transaction Identifier) justified as *the*
  reconciliation key to the GL is exactly the ¶36(c) argument.
- **Criticality is argued, not asserted.** "A wrong or inconsistent position date
  silently corrupts all aggregated figures" is a real consequence, not a
  restatement of importance.
- **DQ requirements are intent + measurement, no SQL**, and every dimension is
  one of Alation's native categories. These map onto monitor definitions with
  little translation.
- **The out-of-scope section is the strongest part.** Six subsections, each
  naming what would actually be required instead — report framework review,
  recipient feedback, operational testing, entitlement management. This is what
  makes the rest credible with a risk audience, and it's the section a generic
  prompt would have skipped.
- **Cross-cutting DQ was a good catch.** Risk-to-finance reconciliation and
  cross-system counterparty identity resolution genuinely span CDEs and would be
  lost if every requirement were forced to attach to a single element.

## Weaknesses worth a prompt revision

1. **P8 is cited as driving CDE-07 while also being declared out of scope.**
   Defensible — ¶57 names industry sector as a required report dimension, which
   does imply the data element — but the tension is unexplained and an auditor
   would ask. The prompt should require that any citation to a
   declared-out-of-scope principle be justified explicitly.

2. **Criticality ratings cluster.** Seven 3s and five 2s, no 1s. Either the scale
   isn't being used or nothing marginal was included. Worth asking for at least
   one honest 1, or removing the level entirely if 8–15 candidates are all
   critical by construction.

3. **Thresholds are mostly "0" or "0%".** Correct in spirit for identifier
   integrity, but "0 unexplained differences" on GL reconciliation isn't
   operable — real reconciliation runs to a materiality tolerance, which the
   output does gesture at via ¶56. The prompt could ask for tolerance-based
   thresholds where the regulation itself allows materiality.

4. **No ordering or dependency between CDEs.** CDE-01 and CDE-08 are
   prerequisites for XDQ-01 and XDQ-02, but nothing says which to establish
   first. A "sequence these for implementation" instruction would make this
   directly actionable.

5. **Search terms are good but untested.** `LEI`, `obligor ID`, `party ID`,
   `BIC`, `GIIN` are plausible; whether they match anything in a real catalog is
   step 3's problem. Fine — but they should be treated as hypotheses.

## Recommended next steps

**Do not change the prompt yet.** Run it two or three more times first. Output is
non-deterministic, and a single run can't distinguish a prompt weakness from
sampling variance. If the CDE set is stable across runs, the prompt is doing its
job; if it swings wildly, tighten it before anything else.

Then, in order:

1. **Capture runs to files** via the CLI so results are diffable:
   `./run.sh run bcbs239_cde_dq_interpreter --input-file artifacts/bcbs239/bank_principles.txt -o artifacts/run-$(date +%F-%H%M).md`
2. **Decide the quote-literalness question** above — it changes the extractor.
3. **Address weakness 1** (out-of-scope citation tension) — smallest edit, real
   credibility gain.
4. **Then step 3 of the pipeline:** feed the search terms to catalog search and
   see what actually exists. That's where this stops being an essay and starts
   being a gap analysis, and it's the first step needing tools
   (`search_catalog`) and therefore ACU budget.

---

## Run 2 comparison — the prompt is not yet stable

Second run, same prompt sha, same model, same input. **This is the important
finding: the CDE set drifts materially between runs.**

| | Run 1 | Run 2 |
|---|---|---|
| CDEs | 12 | 13 |
| Criticality 3 | 7 | 4 |
| Cross-cutting DQ | 4 | 4 |

**Stable core — 8 CDEs appeared in both:** Counterparty Identifier, Legal Entity
Identifier, Exposure Amount, Risk Classification, Business Line, Geography,
Industry/Sector, Position/Reporting Date. These are trustworthy.

**Present in run 1, gone in run 2:**

- **Transaction / Instrument Identifier** — run 1 rated this **criticality 3** and
  argued it was *the* reconciliation key for ¶36(c). A criticality-3 element
  vanishing between identical runs is disqualifying for a compliance artifact.
- **Risk Measure / Calculated Risk Metric** (criticality 3)
- **Data Source / System of Record Identifier** — the lineage element, which was
  the ¶36(d)/¶39 hook

**New in run 2:** Transaction Currency and Conversion Rate, Product/Instrument
Type Code, Risk Limit and Limit Utilisation, Netting Set/Collateral Agreement
Identifier, Liquidity Risk Indicator. All defensible; none more defensible than
what they displaced.

**Criticality ratings drift too.** Risk Classification was 3 in run 1, 2 in run 2.
So the scale isn't anchored to anything stable.

**The out-of-scope contradiction got worse.** Run 2 names Principle 7 as out of
scope while also citing P7 as the driver for CDE-05 and CDE-10. Run 1 had the
milder version of this with P8. The prompt needs to resolve whether a principle
can both drive a CDE and be out of scope — it can (a principle may require a
data element while its reporting obligations remain unaddressable), but that has
to be stated rather than left as an apparent contradiction.

### Confirmed over 8 runs

The two-run figure above was superseded by an 8-run baseline
(`python3 scripts/compare_runs.py docs/runs/*.md`).

| Measure | Result |
|---|---|
| Concepts appearing in **all 8** runs | **7 of 21 (33%)** |
| CDEs per run | 12–13 (the prompt asks for 8–15 — this part works) |
| Criticality-3 concepts that are **not** in every run | **7** |
| Runs omitting the cross-cutting DQ section entirely | **3 of 8** |

**Stable core (7):** counterparty identifier, legal entity identifier, exposure
amount, business line, geography, industry/sector, risk classification. Note
even risk classification's *criticality* swings between 2 and 3.

**Notable losses from the earlier stable set:** position/reporting date now
appears in only 6/8 runs (and 1 of 3 clean runs) despite being rated criticality
3 whenever present. Transaction/instrument identifier appears in **1 of 8**.

**Salvage was ruled out as a cause.** Comparing like-for-like at n=3, the
salvaged runs score 47% and the cleanly-captured runs 56% — the same range, and
the gap is noise at that sample size. Beware comparing sets of different sizes:
fewer runs mechanically inflates stability because there are fewer chances for a
concept to be absent. The 3-run figures are not comparable to the 8-run figure.

**Concept bucketing matters to this measurement.** Runs name the same element
differently ("MTM Value" vs "Mark-to-Market Value"), and counting those as
distinct concepts overstates instability. `compare_runs.py` buckets by keyword
and prints anything unmatched as `OTHER:` so naming drift stays visible rather
than silently distorting the number.

### What this means

Roughly 60% stability. The core is real; the tail is sampling noise. For a
demo that's survivable — for a compliance deliverable it is not, because the
output changes if you re-run it in front of the customer.

### Prompt revisions now justified

1. **Anchor the set.** Require coverage of named categories — entity
   identifiers, exposure measures, aggregation dimensions, temporal keys,
   lineage/source — so the tail can't churn freely. Ask for exactly 10–12.
2. **Give criticality a rubric.** e.g. 3 = aggregation is impossible without it;
   2 = a required reporting dimension degrades; 1 = supporting context. Ratings
   should follow from the rubric, not from vibes.
3. **Resolve the driver/out-of-scope tension explicitly.** A principle may
   appear in both lists, but each such case must say why.
4. **Require the reconciliation key and the lineage element**, or an explicit
   statement of why they were excluded. Both dropped out of run 2 despite being
   the strongest ¶36 arguments in run 1.

### Method note

Run 2's raw output was corrupted by a stream-parsing bug (28MB of duplicated
input echo) and had to be recovered by extracting the final complete copy. The
bug is fixed — the stream resends the whole answer on every event rather than
sending deltas, so the parser now collapses cumulative resends and filters
echoed input, with a size sanity check that fails loudly instead of writing a
huge file. Five assembly cases are covered by tests.

Run 2's recovered output is committed at
[`docs/runs/2026-08-24-1444-run2.md`](runs/2026-08-24-1444-run2.md) as the
evidence behind the drift finding. Run 1 was only ever pasted into a chat window
and was not captured to a file — which is itself the argument for always using
`-o`.

---

## Note on the plumbing

The kit did its job. The prompt lives in git with a content hash, the model is
pinned and resolved by UUID at deploy, and this review references a specific
prompt sha — so any future change in output is attributable. That was the point
of building it.
