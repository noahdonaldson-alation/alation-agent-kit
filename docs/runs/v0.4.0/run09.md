# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a precondition for safe governance.** Banks must be able to generate accurate, complete and timely aggregated risk data not only in normal conditions but under stress — "banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks" (¶45). The underlying premise is that a board cannot govern what it cannot measure.

- **A single, trusted version of risk data with provenance.** "A bank should strive towards a single authoritative source for risk data per each type of risk" (¶36(d)), supported by reconciliation to accounting sources (¶36(c)) and full documentation of every manual step (¶39). Unverified risk figures are not compliant figures.

- **Integrated data architecture with consistent identifiers and metadata.** "A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts" (¶33). A data catalog is the natural home for this.

- **Completeness across the full group, including off-balance-sheet.** "A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet" (¶41), and data must be available by "business line, legal entity, asset type, industry, region and other groupings" (Principle 4 header). Gaps are permissible only if they are identified, explained, and non-critical.

- **Board and senior management accountability for data quality as a risk in its own right.** "A bank's board and senior management should promote the identification, assessment and management of data quality risks as part of its overall risk management framework" (¶27). This makes data quality a governed discipline, not an IT housekeeping matter.

- **A data dictionary as a precondition for accuracy.** "A bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation" (¶37). A data catalog that hosts business definitions, ownership and lineage directly satisfies this requirement.

**Who it applies to**

Principles 1–11 apply to **Global Systemically Important Banks (G-SIBs)** from the publication date, with the Basel Committee explicitly extending expectations to **Domestic Systemically Important Banks (D-SIBs)** and encouraging national supervisors to apply equivalent standards more broadly. The unit of analysis is the **banking group** in its entirety — subsidiaries, branches and off-balance-sheet vehicles are in scope. Outsourced processes remain the bank's responsibility (¶27).

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Unique Identifier**

- **Definition:** A single, persistent, system-independent identifier assigned to each legal counterparty (borrower, derivative counterparty, issuer) that resolves to one and only one entity across all booking systems, risk engines and the general ledger. At group level this is typically mapped to a Legal Entity Identifier (LEI) or an internal golden-record ID.
- **Why critical:** Without a stable, cross-system counterparty key, exposures sitting in different booking systems cannot be summed to produce a single-name or concentration exposure. The aggregate figure — total credit exposure to counterparty X — literally cannot be computed because records in different systems refer to the same entity under different local IDs.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3.** *"Without this element, the aggregate figure 'total credit exposure to counterparty X' cannot be computed at all, because there is no basis on which to join exposure records from different systems to a common entity."* ¶46(a) and ¶46(b) name large-corporate and counterparty exposures as critical risks that must be aggregatable rapidly; ¶33 requires "single identifiers and/or unified naming conventions for data including … counterparties."
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41) — all material exposures; Principle 5 (¶46(a),(b)) — rapid aggregation under stress.
- **Search terms:** counterparty ID, party ID, obligor ID, legal entity identifier, LEI, golden source party, counterparty master, client ID, entity key
- **Data quality requirements:**
  - *Uniqueness* — Each counterparty is represented by exactly one active identifier in the enterprise party master | Count of duplicate counterparty IDs across source systems after cross-reference resolution | Target: 0 unresolved duplicates
  - *Accuracy* — Each counterparty identifier in an exposure record resolves to a valid, active record in the party master | Count of exposure records whose counterparty ID is absent from or inactive in the party master | Target: < 0.1% of exposure records
  - *Completeness* — Every exposure record carries a populated counterparty identifier | Count of exposure records with null or blank counterparty ID | Target: 0

---

**CDE-02 — Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier for the bank's own legal entity in which a transaction or exposure is booked. Used to attribute each exposure to a specific subsidiary, branch or parent entity within the banking group for consolidation and subsidiary-level reporting.
- **Why critical:** Without the booking entity identifier, the bank cannot disaggregate group-level risk by subsidiary or re-aggregate from legal entity level upward. Subsidiary-level and consolidated reporting both fail; so does any regulator query about a specific entity within the group.
- **Risk types:** Cross-cutting (all risk types at group consolidation level)
- **Criticality: 3.** *"Without this element, the aggregate figure 'group consolidated exposure' cannot be computed, because exposures cannot be assigned to the legal entities whose positions must be summed, and subsidiary-level reporting cannot be produced at all."* ¶33 requires single identifiers for legal entities; ¶41 requires group-wide completeness; ¶50 requires the ability to slice "across all business lines and geographic areas."
- **Driven by:** Principle 2 (¶33) — *"integrated data taxonomies and architecture across the banking group … single identifiers … for data including legal entities"*; Principle 4 (¶41) — group-wide completeness.
- **Search terms:** booking entity, legal entity ID, entity code, subsidiary code, branch code, LE code, reporting entity, LEID, legal entity master
- **Data quality requirements:**
  - *Validity* — Each booking entity code corresponds to a current, licensed entity in the group's legal entity register | Count of exposure records carrying a legal entity code not present in the group entity master | Target: 0
  - *Completeness* — Every exposure record carries a populated booking entity identifier | Count of records with null booking entity | Target: 0
  - *Consistency* — The same entity carries the same code across all source systems | Count of entity codes in source systems that map to more than one entry in the entity master | Target: 0

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary value of a risk exposure before the application of netting, collateral or credit risk mitigation. Expressed in the transaction currency and in a common reporting currency. Covers on- and off-balance-sheet positions. This is the primary numeric input to all risk aggregation.
- **Why critical:** This is the quantity being aggregated. Every downstream risk figure — total credit exposure, concentration measure, VaR input, capital calculation — is a function of this field. An incorrect or missing exposure amount makes every aggregate built from it wrong.
- **Risk types:** Credit, market, counterparty credit, concentration
- **Criticality: 3.** *"Without this element, the aggregate figure 'total gross credit exposure to sector Y' cannot be computed at all, because there is no monetary quantity to sum."* ¶41 requires all material exposures to be captured; ¶46(a),(b) identify credit and counterparty exposures as critical for rapid aggregation.
- **Driven by:** Principle 3 (¶36(a)) — *"controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (¶41) — all material risk exposures including off-balance-sheet; Principle 7 (¶52) — reports must be accurate and precise.
- **Search terms:** exposure amount, notional amount, gross exposure, outstanding balance, drawn amount, face value, nominal value, mark-to-market value, fair value, current exposure
- **Data quality requirements:**
  - *Accuracy* — Aggregated gross exposure per legal entity reconciles to the corresponding balance sheet or position system figure within agreed materiality thresholds | Sum of reconciling differences between risk system exposure totals and general ledger / position system totals, by legal entity and risk type | Target: difference < materiality threshold defined by the bank
  - *Completeness* — Every exposure record carries a non-null, non-zero exposure amount or an explicit zero with justification | Count of exposure records with null or unexplained zero exposure amount | Target: 0
  - *Validity* — Exposure amounts are denominated in a recognised currency and are arithmetically consistent with component fields (e.g. quantity × price) where applicable | Count of records where derived exposure differs from stored exposure beyond tolerance | Target: 0

---

**CDE-04 — Position / As-Of Date**

- **Definition:** The business date as of which an exposure, position or risk measure is stated. Every aggregated risk figure is implicitly a statement as of a specific date; this field is that date made explicit.
- **Why critical:** Without a reliable as-of date, aggregates drawn from records with different valuation dates cannot be reconciled, trend analysis is impossible, and the regulator's requirement to produce data "as of a specified date" (¶50) cannot be met. The figure exists but cannot be placed in time, rendering it uninterpretable and unverifiable.
- **Risk types:** Cross-cutting
- **Criticality: 3.** *"Without this element, the aggregate figure 'total exposure as of date D' cannot be reconciled to the system of record, because there is no basis on which to confirm that all constituent records share the same valuation date — the figure could mix stale and current positions without detection."* ¶50 explicitly requires the ability to "aggregate risk data quickly … as of a specified date"; ¶36(c) requires reconciliation to source data.
- **Driven by:** Principle 5 (¶44,¶45) — timeliness and stress-period rapid aggregation; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (¶53(a)) — reconciliation of reports to risk data.
- **Search terms:** as-of date, position date, valuation date, report date, snapshot date, business date, reference date, trade date, settlement date
- **Data quality requirements:**
  - *Completeness* — Every exposure and position record carries a populated as-of date | Count of records with null as-of date | Target: 0
  - *Validity* — As-of dates fall within the permissible range for the reporting cycle and are not future-dated beyond expected settlement | Count of records with as-of date outside the valid reporting window | Target: 0
  - *Consistency* — All records contributing to a given aggregate share the same stated as-of date, or differences are explicitly documented and explained | Count of aggregated batches containing records from more than one as-of date without documented exception | Target: 0

---

**CDE-05 — Risk Type Classification**

- **Definition:** A controlled-vocabulary code that classifies each exposure or position by primary risk type: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk, or other categories defined in the bank's risk taxonomy. This is the first-level partition of the risk data universe.
- **Why critical:** Risk reports are organised by risk type. An exposure assigned to the wrong category is excluded from one risk aggregate and incorrectly included in another. Capital and limit calculations that are risk-type-specific produce wrong results. The distortion is not in a single figure but potentially in multiple risk reports simultaneously.
- **Risk types:** Cross-cutting
- **Criticality: 2.** The aggregate figure is produced, but it is mis-partitioned: credit risk totals overstate or understate while another risk type's totals move inversely. The figure is populated but cannot be trusted as a correct slice. ¶57 requires reports covering all significant risk areas; ¶37 requires a consistent dictionary of concepts.
- **Driven by:** Principle 3 (¶37) — *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"*; Principle 8 (¶57) — *"exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*.
- **Search terms:** risk type, risk category, risk class, risk classification code, risk taxonomy, risk type code, exposure type
- **Data quality requirements:**
  - *Validity* — Every exposure record carries a risk type code drawn from the bank's approved risk taxonomy vocabulary | Count of records with a risk type code not present in the approved taxonomy reference table | Target: 0
  - *Completeness* — No exposure record carries a null risk type code | Count of records with null risk type | Target: 0
  - *Consistency* — The same instrument type is classified under the same risk type code across all source systems | Count of instrument type / risk type code combinations that differ across source systems for the same instrument class | Target: 0

---

**CDE-06 — Business Line**

- **Definition:** A controlled-vocabulary code identifying the business unit, division or line of business responsible for or originating the exposure. Examples: retail banking, corporate banking, trading, asset management, treasury.
- **Why critical:** Principle 4 explicitly requires the ability to aggregate "by business line." Without this dimension, the bank cannot produce business-line-level risk reports, cannot detect business-line concentrations, and cannot meet regulatory queries that slice exposure by originating division.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 2.** Aggregates are produced at the total group level but cannot be correctly sliced by business line. The total is not wrong; the business-line subtotal either does not exist or is incorrect. Principle 4 header and ¶50 require this slice explicitly; ¶57 implies it through "all significant components."
- **Driven by:** Principle 4 (header paragraph) — *"data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — *"across all business lines and geographic areas"*.
- **Search terms:** business line, business unit, line of business, division code, segment code, product line, originating unit, desk code, LOB
- **Data quality requirements:**
  - *Validity* — Business line codes are drawn from a controlled, approved hierarchy | Count of records with a business line code not present in the approved hierarchy | Target: 0
  - *Completeness* — Every exposure record carries a populated business line code | Count of records with null business line | Target: < 0.5% of records with approved exception documentation
  - *Consistency* — Business line hierarchies are applied uniformly across source systems feeding the same risk reports | Count of business line code mismatches for the same transaction observed in two or more source systems | Target: 0

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** A code classifying the counterparty or issuer by economic sector or industry, using a recognised taxonomy (e.g. NACE, GICS, SIC, or an internal equivalent). Used for concentration analysis and sectoral credit risk aggregation.
- **Why critical:** Principle 4 requires aggregation by industry. ¶50 explicitly requires the ability to produce "industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas." Without this, sectoral concentration risk — one of the named stress-scenario aggregations — cannot be produced.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Industry-level aggregates cannot be produced or are incorrectly partitioned. Total exposure is unaffected; the sectoral slice is missing or distorted, which is the specific output Principle 6 requires the bank to be capable of generating on demand. ¶57 names "industry sector for credit risk" as a required component of risk reports.
- **Driven by:** Principle 4 (header) — *"data should be available by … industry"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*.
- **Search terms:** industry code, sector code, NACE code, GICS sector, SIC code, industry classification, counterparty sector, obligor industry, borrower sector
- **Data quality requirements:**
  - *Validity* — Industry codes are drawn from a designated reference taxonomy | Count of records with a code not present in the reference taxonomy | Target: 0
  - *Completeness* — All material counterparties carry an industry classification | Count of counterparties above a materiality threshold with null or unclassified industry code | Target: 0
  - *Accuracy* — Industry classification reflects the counterparty's primary economic activity as verified against an authoritative external source | Periodic sample-based verification rate against external reference (e.g. LEI database, credit bureau) | Target: > 95% agreement on sample

---

**CDE-08 — Geography / Country of Risk**

- **Definition:** A code identifying the primary country or geographic region of risk for the exposure — typically the country of the counterparty's domicile, the country of collateral, or the country of the obligor's primary operations, depending on the risk type. Expressed as an ISO 3166-1 alpha-2 or alpha-3 code or mapped to an internal regional hierarchy.
- **Why critical:** Principle 4 requires aggregation by region. ¶50 names "country credit exposures as of a specified date based on a list of countries" as a paradigm case of an ad-hoc query the bank must be able to answer rapidly. Without this field, geographic concentration risk cannot be measured.
- **Risk types:** Credit, market, concentration, cross-cutting
- **Criticality: 2.** Country/regional aggregates cannot be produced or are incorrectly partitioned. The field's failure degrades an entire class of required outputs (country concentration reports) but does not prevent the total exposure aggregate from being produced. ¶50 and Principle 4 name this slice explicitly.
- **Driven by:** Principle 4 (header) — *"data should be available by … region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*; Principle 5 (¶46(c)) — *"market concentrations by sector and region"*.
- **Search terms:** country of risk, country code, geography code, region code, ISO country code, domicile country, booking country, risk country, geographic region
- **Data quality requirements:**
  - *Validity* — Country codes conform to ISO 3166-1 or the bank's approved geographic hierarchy | Count of records with a country code not in the approved reference list | Target: 0
  - *Completeness* — Every material exposure carries a populated country of risk | Count of exposure records above materiality threshold with null country code | Target: 0
  - *Accuracy* — Country of risk is assigned to reflect economic risk location, not merely booking location | Count of records where country of risk equals booking country for instruments known to require a distinct risk country (e.g. cross-border loans) | Reviewed periodically; exceptions documented

---

**CDE-09 — Source System / Reconciliation Key**

- **Definition:** The identifier that links each risk data record to its originating system of record and to the corresponding record in the general ledger or authoritative position system. Comprises two sub-elements that cannot usefully be separated: (a) the source system code (which system produced this record) and (b) the source system's own primary key for the record (trade ID, account number, or equivalent) that enables row-level reconciliation back to the system of record.
- **Why critical:** This is the element that makes accuracy and completeness *evidenceable* rather than merely asserted. Without it, the reconciliation required by ¶36(c) cannot be performed: the bank cannot prove that its aggregated risk data matches accounting data because there is no join key. An unverifiable aggregate is not a compliant aggregate under BCBS 239.
- **Risk types:** Cross-cutting
- **Criticality: 3.** *"Without this element, the aggregate figure for any risk type cannot be reconciled to the system of record at all, because there is no key on which to join risk records to their accounting or position-system counterparts — the figure cannot be evidenced as accurate, which under ¶36(c) is an equivalent failure to the figure being wrong."* ¶36(c) — *"risk data should be reconciled with bank's sources, including accounting data where appropriate"*; ¶39 — documentation of all processes required.
- **Driven by:** Principle 3 (¶36(c)) — *"risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (¶36(d)) — single authoritative source per risk type; Principle 7 (¶53(a)) — *"defined requirements and processes to reconcile reports to risk data"*.
- **Search terms:** source system ID, system of origin, source system code, trade ID, account ID, originating system key, GL reference, transaction reference, position ID, system reference number, upstream system
- **Data quality requirements:**
  - *Completeness* — Every risk record carries both a source system code and a source system primary key | Count of risk records with null source system code or null source system key | Target: 0
  - *Uniqueness* — The combination of source system code and source system key uniquely identifies one and only one risk record | Count of duplicate (source system, source key) pairs in the risk data store | Target: 0
  - *Accuracy* — Each risk record's key resolves to a matching record in the designated system of record | Count of risk records whose source key returns no match in the system of record during reconciliation | Target: 0; all exceptions investigated and documented

---

**CDE-10 — Data Provenance / Manual Override Flag**

- **Definition:** Metadata fields that identify (a) whether a data record was produced by an automated feed or by manual entry / end-user-computing (EUC), and (b) where applicable, which manual process or EUC tool produced it and when. This is a data-level attribute, not a system attribute — a single source system may feed both automated and manually-adjusted records.
- **Why critical:** ¶36(b) and ¶39 require banks to document and control manual processes and EUC use. ¶40 requires measurement and monitoring of data accuracy by process type. Without this flag, the bank cannot demonstrate that manual overrides are controlled, cannot measure the proportion of risk data subject to manual intervention, and cannot target remediation. An auditor or supervisor cannot distinguish clean automated data from manually-adjusted data — which is precisely the control gap the regulation is closing.
- **Risk types:** Cross-cutting
- **Criticality: 2.** No individual aggregate figure is made invalid by the absence of this flag in the way a missing counterparty key invalidates a join. However, the bank's ability to monitor and evidence accuracy per ¶36(b) and ¶39, and to measure EUC reliance as required by ¶30, is entirely lost. The control itself — not just the figure — degrades, and supervisors will treat an inability to distinguish automated from manual data as a material governance failure.
- **Driven by:** Principle 3 (¶36(b)) — *"where a bank relies on manual processes and desktop applications … it should have effective mitigants in place"*; Principle 3 (¶39) — *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*; Principle 1 (¶30) — senior management awareness of "degree of reliance on manual processes."
- **Search terms:** manual flag, manual override, EUC flag, end-user computing, data source type, automated indicator, manual adjustment, manual input flag, process type, adjustment flag, spreadsheet flag
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a populated provenance/source-type flag | Count of records with null provenance flag | Target: 0
  - *Validity* — Provenance flag values are drawn from the approved controlled vocabulary (e.g. AUTOMATED, MANUAL-EUC, MANUAL-OVERRIDE, INTERFACED) | Count of records with a flag value outside the approved vocabulary | Target: 0
  - *Accuracy* — Records flagged as AUTOMATED correspond to feeds with no manual touchpoints documented in the lineage; records flagged as MANUAL or EUC have an associated process identifier | Count of records where flag is AUTOMATED but lineage documentation shows a manual step, or vice versa | Target: 0; discrepancies trigger immediate review

---

**CDE-11 — Reporting Currency and FX Rate**

- **Definition:** Two related elements: (a) the ISO currency code of the transaction's denomination, and (b) the exchange rate applied to convert the transaction amount to the reporting/consolidation currency, including the rate source and rate date. These are inseparable in practice: the currency code without the rate, or the rate without the date and source, cannot support reconciliation.
- **Why critical:** A multinational bank aggregates exposures denominated in dozens of currencies. Without the transaction currency code, conversion is impossible. Without the rate source and rate date, the converted amount cannot be reconciled to the figure in the consolidated report — two groups using different rate sources on the same date will produce different aggregates with no way to detect or explain the difference. ¶36(c) requires reconciliation; ¶53(a) requires processes to reconcile reports to risk data.
- **Risk types:** Cross-cutting (affects all risk types in multi-currency groups)
- **Criticality: 2.** The unconverted figure exists; conversion is possible even with an imperfect rate. However, the reconciliation demanded by ¶36(c) degrades unless rate source and rate date are recorded: different systems using different rates produce irreconcilable group totals, and the gap cannot be explained without knowing which rate was used. The figure is produced but cannot be fully reconciled.
- **Driven by:** Principle 3 (¶36(a),(c)) — accuracy controls analogous to accounting, and reconciliation to source; Principle 4 (¶41) — all material risk exposures; Principle 7 (¶53(a)) — reconciliation of reports to risk data.
- **Search terms:** transaction currency, currency code, ISO currency, FX rate, exchange rate, conversion rate, rate source, rate date, reporting currency, base currency, FX conversion
- **Data quality requirements:**
  - *Validity* — Currency codes conform to ISO 4217 | Count of records with a currency code not in the ISO 4217 reference list | Target: 0
  - *Completeness* — Every monetary exposure record carries a transaction currency code, an FX rate, and a rate date | Count of records missing any of these three fields | Target: 0
  - *Accuracy* — FX rates applied to risk data match the bank's authoritative rate source for the same rate date, within agreed tolerance | Count of records where applied FX rate differs from the authoritative rate source by more than the agreed tolerance | Target: 0; all exceptions documented

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Cross-System Counterparty Resolution**

- **Spans:** CDE-01 (Counterparty Unique Identifier), CDE-03 (Gross Exposure Amount), CDE-07 (Industry / Sector), CDE-08 (Geography / Country of Risk)
- **Why cross-cutting:** Monitoring any single CDE in isolation cannot detect the problem this requirement addresses. A counterparty identifier may be valid within its own system and still refer to a different entity than the same name in another system. The failure is in the *relationship between systems*, not in any individual field. This is the most common structural data quality failure in large banks and the one BCBS 239 ¶33 targets most directly with its requirement for "single identifiers."
- **Dimension:** Consistency
- **Rule intent:** Every local counterparty identifier in every source system must map, without ambiguity, to exactly one record in the enterprise party master. Any exposure that cannot be resolved to the party master cannot be included in a compliant single-name or concentration aggregate.
- **Measurement:** Count of exposure records, per source system, whose local counterparty ID has no mapping to the enterprise party master; separately, count of party master entries with more than one active local ID in the same source system. Both counts are tracked by source system and by risk type, and trended weekly.
- **Suggested threshold:** Zero unresolved counterparty mappings for exposures above the bank's materiality threshold. Residual unmatched records below threshold documented with remediation timeline.
- **Regulation anchor:** ¶33 — *"single identifiers and/or unified naming conventions for data including legal entities, counterparties"*; ¶46(a),(b) — rapid aggregation of counterparty exposures under stress.

---

**XDQ-02 — Risk-to-Finance Reconciliation Completeness**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (Source System / Reconciliation Key), CDE-04 (Position / As-Of Date), CDE-11 (Reporting Currency and FX Rate)
- **Why cross-cutting:** Reconciliation is not a property of any single field. It is a relationship between the aggregated risk position and the corresponding accounting or position-system figure, established through the combination of the reconciliation key (CDE-09), the exposure amount (CDE-03), the as-of date (CDE-04), and the currency/rate (CDE-11). None of these elements alone constitutes reconciliation; all four must be present and consistent for a reconciliation to be performed and passed. This is the operationalisation of ¶36(c) and ¶53(a).
- **Dimension:** Accuracy (completeness of the reconciliation process itself)
- **Rule intent:** For every risk type and every legal entity, the sum of gross exposure amounts in the risk data store, translated to reporting currency at the authoritative rate for the as-of date, must reconcile to the corresponding position or balance in the general ledger or authoritative position system within agreed materiality thresholds. Every line item in the reconciliation must be traceable to a source system record via the reconciliation key.
- **Measurement:** (a) Count of risk-type / legal-entity combinations for which a reconciliation run was completed versus scheduled — reconciliation coverage rate. (b) Sum of absolute reconciling differences, by risk type and legal entity, expressed as a percentage of total exposure. (c) Count of exposure records that could not be included in a reconciliation run due to a missing or unmatched reconciliation key.
- **Suggested threshold:** (a) 100% reconciliation coverage — no risk-type / entity combination is exempt without documented approval. (b) Reconciling difference < materiality threshold as defined by the bank's accuracy policy per ¶56. (c) Zero records excluded from reconciliation due to missing key above the materiality threshold.
- **Regulation anchor:** ¶36(c) — *"risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; ¶53(a) — *"defined requirements and processes to reconcile reports to risk data"*.

---

**XDQ-03 — Manual Process Population and EUC Concentration Monitoring**

- **Spans:** CDE-10 (Data Provenance / Manual Override Flag), CDE-09 (Source System / Reconciliation Key), CDE-03 (Gross Exposure Amount)
- **Why cross-cutting:** The risk that manual and EUC processes introduce is not visible at the level of any individual data element. It is visible only when provenance flags are aggregated: what percentage of the total risk data population, and what percentage of total exposure by monetary value, passes through a manual step? A bank with 2% of records flagged as manual but those records representing 40% of exposure by value has a material control gap that no single-CDE monitor would surface. ¶39 requires documentation; ¶30 requires senior management awareness of the "degree of reliance on manual processes." Neither is satisfied by monitoring provenance flags record-by-record.
- **Dimension:** Completeness (of control coverage); Accuracy (of manual records relative to automated equivalents)
- **Rule intent:** The bank must be able to report, at any time, the fraction of its risk data population and total risk exposure that originates from manual or EUC processes, broken down by source system and risk type. Exceptions above the board-approved threshold must trigger escalation per ¶40.
- **Measurement:** (a) Percentage of exposure records carrying a MANUAL or EUC provenance flag, by source system and risk type. (b) Percentage of total gross exposure amount attributable to manually-flagged records, by risk type and legal entity. (c) Count of manual/EUC records without an associated process identifier or without a reconciliation key that can be traced to a system of record.
- **Suggested threshold:** Bank-defined maximum percentage for (a) and (b), approved by board/senior management. Breaches trigger escalation per ¶40; sustained high-EUC areas appear in remediation plans per ¶30.
- **Regulation anchor:** ¶36(b) — *"effective mitigants in place (eg end-user computing policies)"*; ¶39 — *"document and explain all of their risk data aggregation processes whether automated or manual"*; ¶30 — *"degree of reliance on manual processes"*.

---

## 4. Out of Scope

The following aspects of Principles 1–11 are not addressable by a CDE register or data quality monitoring, regardless of how well those tools are implemented.

---

**Principle 7 — Accuracy (reporting-layer obligations)**

Principle 7 drives CDE-09 (reconciliation key) and the cross-cutting reconciliation requirement XDQ-02 — these are genuine data-catalog deliverables. However, ¶53(b) requires "an inventory of the validation rules … including explanations of the conventions used to describe any mathematical or logical relationships that should be verified through these validations or checks," and ¶53(c) requires "integrated procedures for identifying, reporting and explaining data errors … via exceptions reports." These are *report production controls* — workflow, exception management, and escalation procedures that live in reporting tools, risk engines, or a dedicated data quality workflow system. A catalog can document which rules exist and link them to CDEs, but it cannot execute the exception workflow or manage the escalation chain. The distinction matters: the catalog is a register and a monitoring surface, not an operational control.

---

**Principle 8 — Comprehensiveness**

¶57 names industry sector as a required dimension of credit risk reports, which is why CDE-07 is in the register above. That is the data element Principle 8 drives. The remainder of Principle 8 — ensuring that reports cover "all material risk areas," include "risk-related measures (eg regulatory and economic capital)," and provide "forward-looking forecasts and stress tests" (¶57–¶60) — is a *report content* requirement. No CDE register can ensure that a report includes capital adequacy projections or stress test results. That requires report design, model governance, and senior management sign-off on report templates. The catalog's contribution is limited to ensuring the underlying data elements are defined, owned and monitored; it cannot govern what a report contains.

---

**Principle 9 — Clarity and usefulness**

This principle is entirely outside the scope of a data catalog. ¶61–¶69 govern whether risk reports are intelligible to their recipients, whether the balance of quantitative and qualitative content is appropriate, whether the board is asking the right questions, and whether recipients periodically confirm that reports remain relevant. ¶67 does require "an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports" — this is a business glossary obligation that a catalog can partially satisfy. However, the governance obligations around board engagement, tailoring of report content, and periodic relevance reviews are people-and-process matters that no data system addresses.

---

**Principle 10 — Frequency**

¶70–¶71 require the board and senior management to set report production frequencies, test the ability to produce accurate reports within those timeframes, and accelerate production in a crisis. This is a *scheduling and operational resilience* requirement. A catalog can record the expected refresh frequency of a data asset as metadata, and a DQ monitor can measure whether a dataset was refreshed on schedule (timeliness dimension). Those are useful. But the requirement to "routinely test" report production capability (¶70) and to produce intraday data under stress (¶71) is a business continuity and operational capability matter that belongs in recovery and resilience planning, not in catalog governance. The catalog documents the target; it does not test the bank's ability to hit it under pressure.

---

**Principle 11 — Distribution**

¶72–¶73 require that risk reports reach the right people rapidly while maintaining confidentiality, and that banks periodically confirm recipients are receiving timely reports. These are *access governance* and *distribution workflow* requirements. A catalog can record data classifications and data access policies, and it can inform role-based access design. However, ensuring that a report is delivered to the correct board member within the required window, or that confidentiality is maintained in report distribution, requires an entitlement management system, a reporting distribution platform, and operational procedures. The catalog contributes metadata; it does not control the distribution channel.

---

**Principle 1 — Governance (the residual obligations)**

Principle 1 drives CDE-10 (provenance / manual flag) insofar as it requires senior management awareness of manual process reliance (¶30). The catalog can surface this through XDQ-03. However, ¶27–¶31 also impose obligations on the bank's *board and senior management* — approving the framework (¶28), conducting independent validation (¶29(a)), assessing acquisitions (¶29(b)), and ensuring IT strategy remediates shortcomings (¶30). These are governance structure and programme management obligations. No data catalog satisfies them. The catalog can provide evidence (lineage, ownership records, DQ metrics) that supports the independent validation described in ¶29(a), but the validation itself — conducted by staff with IT, data and reporting expertise — must be performed by people, not by a platform.

---

**Principle 2 — Data architecture (the residual obligations)**

Principle 2 drives CDE-01 and CDE-02 insofar as it requires single identifiers for counterparties and legal entities (¶33). However, ¶32–¶35 also require risk data capabilities to be included in *business continuity planning*, and ¶34 requires roles and responsibilities to be established for data ownership across business and IT. A catalog can record ownership assignments; it cannot create or enforce the organisational accountability structure, and it does not substitute for business continuity planning or a business impact analysis.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Unique Identifier | 3 | 2 (¶33), 4 (¶41), 5 (¶46) | Uniqueness, Accuracy, Completeness |
| CDE-02 | Legal Entity Identifier (Booking Entity) | 3 | 2 (¶33), 4 (¶41), 6 (¶50) | Validity, Completeness, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3 (¶36(a)), 4 (¶41), 7 (¶52) | Accuracy, Completeness, Validity |
| CDE-04 | Position / As-Of Date | 3 | 5 (¶44,¶45), 6 (¶50), 7 (¶53(a)) | Completeness, Validity, Consistency |
| CDE-05 | Risk Type Classification | 2 | 3 (¶37), 8 (¶57) | Validity, Completeness, Consistency |
| CDE-06 | Business Line | 2 | 4 (header), 6 (¶50) | Validity, Completeness, Consistency |
| CDE-07 | Industry / Sector Classification | 2 | 4 (header), 6 (¶50), 8 (¶57) | Validity, Completeness, Accuracy |
| CDE-08 | Geography / Country of Risk | 2 | 4 (header), 5 (¶46(c)), 6 (¶50) | Validity, Completeness, Accuracy |
| CDE-09 | Source System / Reconciliation Key | 3 | 3 (¶36(c),(d)), 7 (¶53(a)) | Completeness, Uniqueness, Accuracy |
| CDE-10 | Data Provenance / Manual Override Flag | 2 | 1 (¶30), 3 (¶36(b),¶39) | Completeness, Validity, Accuracy |
| CDE-11 | Reporting Currency and FX Rate | 2 | 3 (¶36(a),(c)), 4 (¶41), 7 (¶53(a)) | Validity, Completeness, Accuracy |

*Criticality 3 elements (5): CDE-01, CDE-02, CDE-03, CDE-04, CDE-09. All others are Criticality 2. No element was assessed as Criticality 1: every element in the register affects either an aggregate figure or the evidential basis for proving that figure correct; purely descriptive or contextual fields were excluded at the selection stage.*