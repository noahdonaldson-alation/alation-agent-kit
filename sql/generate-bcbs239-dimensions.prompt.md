# Prompt: generate the BCBS 239 risk-dimension SQL pack

Paste everything below the line into your SQL-generating LLM. It produces a
Snowflake pack that extends an existing demo warehouse with the risk dimensions
BCBS 239 requires — deliberately imperfect, so data quality monitors have
something real to find.

Keep the generated files under `sql/` in this repo. Do not commit credentials.

---

You are a senior data engineer building a **demonstration** banking data
warehouse in Snowflake. Your job is to extend an existing model so it can support
BCBS 239 risk data aggregation — and to leave it realistically imperfect.

## The existing model

Database `ALATION_EDW`, medallion architecture, schemas:

```
MCF_CORE_BRONZE / MCF_CORE_SILVER / MCF_CORE_GOLD
MCF_REGULATORY_BRONZE / MCF_REGULATORY_SILVER / MCF_REGULATORY_GOLD
```

Known objects (do not rename or drop these):

| Object | Schema | Notes |
|---|---|---|
| `DIM_PARTY` | MCF_CORE_GOLD | has `PARTY_SK` |
| `FACT_LOAN` | MCF_CORE_GOLD | loan positions |
| `FACT_TRANSACTION` | MCF_CORE_GOLD | transaction history |
| `FACT_ACCOUNT_BALANCE_SNAPSHOT` / `ACCT_BAL_SNAPSHOT` | MCF_CORE_GOLD | has `BALANCE_AMOUNT`, `AS_OF_DATE` |
| `VW_CORE_PARTY_POSITION_SUMMARY` | MCF_CORE_GOLD | position summary view |
| `CUST_MASTER_CLEAN` | MCF_CORE_SILVER | has `CUST_NBR` |
| `GL_MASTER_RAW` / `GL_MASTER_CLEAN` | MCF_REGULATORY_* | general ledger |
| `LOAN_MASTER_RAW` / `LOAN_MASTER_CLEAN` | MCF_REGULATORY_* | |
| `LOAN_REG_CATEGORY_RAW` / `LOAN_REG_CATEGORY_CLEAN` | MCF_REGULATORY_* | |

Match the existing conventions: `MCF_` schema prefix, `DIM_`/`FACT_`/`VW_`
object prefixes, `_SK` for surrogate keys, `_CD` for codes, `_RAW`/`_CLEAN` for
bronze/silver pairs, `SNOWFLAKE` uppercase identifiers.

## What is missing, and must be added

A gap analysis against BCBS 239 found the warehouse cannot slice exposure by the
dimensions the regulation requires. Add these, as conformed dimensions plus the
foreign keys on the fact tables that make aggregation possible:

1. **Booking legal entity** — the bank's *own* entity a position is booked in,
   with a parent hierarchy for group consolidation. Distinct from counterparty.
2. **Business line / segment** — aligned to an internal org hierarchy.
3. **Country of risk** — ISO 3166 alpha-2, distinct from country of domicile.
4. **Industry / sector** — a recognised scheme (NACE or SIC), on the counterparty.
5. **Risk type** — credit / market / liquidity / operational / counterparty,
   as a governed taxonomy, not free text.
6. **Currency** — ISO 4217 on every monetary amount, plus an FX rate table so
   amounts can be expressed in a reporting currency.

Use authentic banking column names, **not** obvious keyword matches. For example
`LEGAL_ENTITY_CD`, `BUSINESS_LINE_CD`, `COUNTRY_OF_RISK_CD`, `NACE_CD`,
`RISK_TYPE_CD`, `CCY_CD`, `EXPOSURE_AMT`, `NOTIONAL_AMT`. Realistic naming is the
point — a catalog search should have to work slightly for it.

Also add, because the regulation names them directly:

7. **A GL reconciliation key** on the fact tables that joins positions to
   `GL_MASTER_CLEAN`, so risk-to-finance reconciliation is possible at all.
8. **Source-system and manual-override provenance columns** —
   `SOURCE_SYSTEM_CD` and a boolean or flag distinguishing automated feeds from
   manual/end-user-computing input.

## Leave it deliberately imperfect — this is the important part

A warehouse where every check passes demonstrates nothing. Seed a **controlled,
documented** amount of dirt so quality monitors return findings a reviewer can
act on. Target roughly:

| Defect | Where | Rate |
|---|---|---|
| NULL business line | fact rows | ~3% |
| NULL / unknown country of risk | fact rows | ~2% |
| Missing industry code | counterparties | ~8% |
| Orphaned counterparty FK (no matching dimension row) | fact rows | ~0.5% |
| Duplicate counterparty (same entity, two surrogate keys) | dimension | ~12 rows |
| Same counterparty carrying different industry codes across systems | silver vs gold | ~15 rows |
| Risk type outside the approved taxonomy | fact rows | ~1% |
| Positions whose GL key has no ledger match | fact rows | ~1.5% |
| Stale `AS_OF_DATE` (older than the reporting cycle) | one legal entity | one entity's rows |
| Amounts with NULL currency | fact rows | ~0.8% |

Make the dirt **plausible and explainable** — it should look like a real
integration problem, not random corruption. Concentrate some of it in one source
system or one legal entity, because that is how real problems cluster and it
makes a much better story than uniform noise.

## Hard constraints

- **Snowflake SQL only.** No dbt, no external tooling.
- **Idempotent and re-runnable.** `CREATE OR REPLACE` / `MERGE`, safe to run
  twice. Never `DROP` an existing object listed above.
- **Do not use `RANDOM()` with a seed for anything that must be reproducible.**
  Snowflake explicitly does not guarantee reproducibility "whether or not you
  specify a seed." Use `SEQ4()` from `GENERATOR` plus deterministic hashing —
  e.g. `MOD(ABS(HASH(id_column)), 100) < 3` to hit a 3% rate the same way every
  run.
- **Generate fact volume with `GENERATOR`**, not literal INSERTs. Use literal
  `INSERT ... VALUES` only for dimension reference data, which should be
  reviewable in the diff.
- **Dates relative to `CURRENT_DATE`**, never hardcoded. Nothing kills a
  governance demo faster than data dated two years ago.
- **Respect the medallion layers.** Raw/bronze may be dirty; silver is cleansed;
  gold is conformed. Some of the seeded inconsistency should be *between* layers
  — that is what makes lineage and reconciliation worth showing.
- Volume: enough to be credible and fast. Low hundreds of thousands of fact rows
  at most.

## Deliverables

Numbered files, runnable in order:

```
sql/01_dimensions.sql        new DIM_ tables + reference data
sql/02_fact_columns.sql      add FKs and columns to existing facts (idempotent)
sql/03_fx_rates.sql          currency + FX rate table
sql/04_generate_data.sql     populate, including the seeded defects
sql/05_views.sql             update/replace affected views
sql/06_verify.sql            SELECTs that report the ACTUAL defect rate per
                             defect above, so expectation can be compared to
                             reality after loading
```

Plus **`sql/EXPECTED-DEFECTS.md`**: a table of every seeded defect, where it
lives, the intended rate, the BCBS 239 paragraph a monitor on it would cite
(¶33 identifiers, ¶36(c) reconciliation, ¶40 accuracy, ¶43 completeness,
¶44–47 timeliness), and one sentence on the business consequence.

That document is the answer key. Without it, nobody can tell a seeded defect
from a bug in the pack.

## What not to do

- **Do not make the data clean.** Perfect data means every monitor passes and
  the demo has nothing to show.
- **Do not fix everything.** Leave at least one dimension genuinely thin — for
  example, geography present on counterparties but absent on some fact tables —
  so a gap analysis still has a real finding to report.
- Do not add columns whose names simply echo the words a search would look for.
  Authentic naming is what makes discovery meaningful.
- Do not invent a new schema layout or rename existing objects.

Before returning, state in two or three sentences what a BCBS 239 gap analysis
should now find, and what should still be missing. That is how the result gets
checked.
