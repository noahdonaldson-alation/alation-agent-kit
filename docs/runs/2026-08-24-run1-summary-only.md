# BCBS 239 CDE/DQ interpretation — run 1 (summary table only)

**Partial record.** Run 1 predates the `-o` habit and was only ever pasted into a
chat window, so the full prose is lost. Its summary table is preserved here so
run 1 still counts in stability comparisons.

**Prompt:** `bcbs239_cde_dq_interpreter` sha `8673a293482e`
**Model:** Bedrock Claude Sonnet 4.6 (us-east-1)
**Cross-cutting:** XDQ-01, XDQ-02, XDQ-03, XDQ-04
**Out of scope:** Principles 8, 9, 10, 11, plus parts of 1 and 2

## 5. Summary table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | 2, 4, 5 | Uniqueness, validity, consistency, completeness |
| CDE-02 | Legal Entity Identifier (booking entity) | 3 | 2, 4 | Completeness, validity, consistency |
| CDE-03 | Exposure Amount (Gross Notional / Current Exposure) | 3 | 3, 7 | Accuracy, completeness, validity, timeliness |
| CDE-04 | Risk Classification / Risk Type Code | 3 | 2, 3, 7 | Validity, completeness, consistency |
| CDE-05 | Business Line / Segment Code | 2 | 4, 6 | Completeness, validity, consistency |
| CDE-06 | Geography / Jurisdiction Code | 2 | 4, 5, 6 | Completeness, validity, consistency |
| CDE-07 | Industry / Sector Code | 2 | 4, 6, 8 | Completeness, validity, consistency |
| CDE-08 | Transaction / Instrument Identifier | 3 | 2, 3 | Uniqueness, consistency, completeness |
| CDE-09 | Reporting Date / Position Date | 3 | 5, 6 | Accuracy, completeness, timeliness |
| CDE-10 | Collateral Value and Collateral Type | 2 | 3, 4 | Accuracy, completeness, validity |
| CDE-11 | Risk Measure / Calculated Risk Metric | 3 | 7 | Accuracy, validity, timeliness |
| CDE-12 | Data Source / System of Record Identifier | 2 | 3 | Completeness, validity, accuracy |
