# BCBS 239 gap analysis — first end-to-end pipeline result

**Instance:** `finance-industry.mtse.alationcloud.com` · **Date:** 2026-08-24
**Register:** `docs/runs/v0.6.0/run01.json` (prompt `bcbs239_cde_dq_interpreter` v0.6.0)
**Mapper:** `bcbs239_pde_mapper` v0.2.0 · **Output:** `artifacts/pde-mapping-postmde.json`

The whole chain ran: regulation text → 11 CDE requirements with paragraph
citations → catalog search → gap analysis against a real warehouse. This records
what it found, because the finding is more interesting than the plumbing.

---

## The headline

**The warehouse can report balances by customer and date. It cannot slice
exposure by business line, legal entity, country, or industry — which is exactly
what Principle 4 requires.**

Six of eleven required data elements are absent from the catalogued data, with
column-level metadata fully indexed. That is a material compliance gap, not a
catalogue gap.

| CDE | Status | Note |
|---|---|---|
| CDE-08 Position / As-of Date | **mapped** | 5 candidates, confirmed types |
| CDE-01 Counterparty Identifier | partial | `dim_party.PARTY_SK` is a plausible surrogate |
| CDE-03 Gross Exposure Amount | partial | `BALANCE_AMOUNT` serves as a proxy |
| CDE-09 GL / Reconciliation Key | partial | regulatory GL lines exist |
| CDE-10 Source System / Manual Override | partial | partial provenance |
| **CDE-02 Booking Legal Entity** | **not found** | no own-entity dimension |
| **CDE-04 Risk Type Classification** | **not found** | no risk taxonomy column |
| **CDE-05 Business Line** | **not found** | required by ¶41, ¶43 |
| **CDE-06 Geography / Country of Risk** | **not found** | required by ¶41, ¶50 |
| **CDE-07 Industry / Sector** | **not found** | named in ¶57 |
| **CDE-11 Transaction Currency** | **not found** | no currency dimension |

Each absence carries 2–3 blockers explaining what was searched and why nothing
matched, so the result is auditable rather than asserted.

## Why this is the right demo opening

A list of CDEs to create is a proposal. **This is a diagnosis**, and it has three
properties a proposal doesn't:

1. **It is about the customer's data, not ours.** Nothing here is generic.
2. **Every gap cites the paragraph that requires it.** "You cannot aggregate by
   business line" is an opinion; "¶41 requires aggregation across business lines
   and no business line dimension exists in the catalogued data" is a finding.
3. **It is falsifiable.** `searched_for` records 13–20 search terms per element.
   A customer's data lead can say "we do have that, it's called X" — and that
   correction is itself valuable, and fast.

## Before and after MDE — catalogue maturity is visible

The same register and agent were run twice, before and after re-running metadata
extraction with column-level crawling. Nothing else changed.

| | Before MDE | After MDE |
|---|---|---|
| Candidate object types | 14 **tables** | 18 **columns** |
| Confidence distribution | 13 medium, 1 low, **0 high** | 15 medium, **3 high** |
| Mapped | 0 | 1 |
| Partial | 5 | 4 |
| Not found | 6 | 6 |
| Blockers | 32 | 24 |

Two things worth drawing out:

**The pipeline's output tracks catalogue maturity rather than papering over it.**
Before the column crawl it could only reach table level and said so, refusing to
claim `high` confidence on anything. That is the behaviour you want from
something a bank will act on.

**The six not-found elements did not change.** Before the crawl, "not found"
was ambiguous — it could have meant the catalogue was thin. After, it is
unambiguous: the data does not carry those dimensions. **The same output means
something different once the catalogue is complete**, which is why the `instance`
block records scope and the `scope_caveat` matters.

## What is not yet true

- **Nothing has been created.** This is suggestion-only; no policy, CDE, or
  monitor exists as a result of this run.
- **Partial means unconfirmed.** `PARTY_SK` as a counterparty key and
  `BALANCE_AMOUNT` as an exposure measure are plausible and unverified. A data
  lead should confirm or correct them; that is a five-minute conversation, and
  the point of reporting confidence honestly.
- **One structural defect remained at v0.2.0** — a monitor targeted a view that
  was not recorded as a candidate. Fixed in v0.3.0; re-run to confirm.
- **The six gaps have not been triaged.** Some may be genuinely absent from the
  source systems; others may exist in tables not yet catalogued, or under names
  the search terms did not anticipate. Distinguishing those is the next
  conversation, not something the agent can settle.

## Reproducing this

```bash
# step 2: regulation -> requirements register (regulation-specific, reusable)
./run.sh run bcbs239_cde_dq_interpreter \
  --input-file artifacts/bcbs239/bank_principles.txt -o register.json
python3 scripts/validate_output.py register.json

# step 3: register -> gap analysis (customer-specific)
./run.sh run bcbs239_pde_mapper --input-file register.json -o mapping.json
python3 scripts/validate_output.py --schema schemas/pde_mapping.schema.json mapping.json
```

The register is the reusable artifact — BCBS 239 does not change per bank, so it
ships in the solution package reviewed once. Only step 3 runs per customer.
