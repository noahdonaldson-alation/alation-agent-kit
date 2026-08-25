# BCBS 239 — Data Catalog Governance Analysis

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a precondition for sound management.** The regulation requires banks to produce accurate, complete, and timely aggregated risk data so that boards and senior management can make effective decisions, particularly during stress and crisis (¶35: *"risk management reports reflect the risks in a reliable way … meeting data aggregation expectations is necessary to meet reporting expectations"*).

- **Governed data architecture with explicit metadata.** Banks must maintain integrated data taxonomies, single identifiers, and unified naming conventions across the group, with information on the characteristics of data — i.e., metadata (¶33: *"integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions"*).

- **Accuracy and reconcilability with a single authoritative source.** Risk data must be reconciled with accounting sources and, where possible, derived from a single authoritative source per risk type, with controls at least as robust as those applied to accounting data (¶36(a–d): *"Controls surrounding risk data should be as robust as those applicable to accounting data … reconciled with bank's sources, including accounting data … a single authoritative source for risk data per each type of risk"*).

- **Completeness across all material dimensions.** All material exposures — including off-balance-sheet items — must be capturable and sliceable by business line, legal entity, asset type, industry, region, and other relevant groupings (¶41–43: *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet … produce aggregated risk data that is complete"*; Principle 4 heading: *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*).

- **Documented lineage, with manual processes explicitly identified.** All aggregation processes — automated and manual — must be documented, including any end-user computing (EUC) or manual workarounds, with proposed remediation (¶39: *"document and explain all of their risk data aggregation processes whether automated or manual … appropriateness of any manual workarounds … proposed actions to reduce the impact"*).

- **A data dictionary as foundational infrastructure.** Concepts must be defined consistently across the organisation, supporting both aggregation integrity and the inventory/classification of risk data items referenced in reporting (¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"*; ¶67: *"develop an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"*).

**Who it applies to**

Principles 1–11 apply to Global Systemically Important Banks (G-SIBs) as the primary scope, with supervisors expected to apply the principles to a wider set of domestically significant banks over time (¶22, referenced in ¶35 and ¶51). The obligations flow to the entire banking group, including subsidiaries, across all jurisdictions where the group operates (¶30, ¶43).

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**
- **Definition:** The unique, system-persistent identifier assigned to each external counterparty (borrower, derivative counterparty, issuer, depositor) that resolves to a single entity across all source systems of the banking group. Distinct from internal customer identifiers that may differ by system or jurisdiction.
- **Why critical:** Without a single resolved counterparty identifier, exposures across trading book, banking book, and off-balance-sheet instruments cannot be summed to produce a group-level counterparty exposure. The aggregate figure is not degraded — it is structurally impossible to produce correctly. This is the foundational joining key for concentration risk and large-exposure reporting.
- **Risk types:** Credit / counterparty / concentration / cross-cutting
- **Criticality: 3** — Aggregation across systems is *impossible* without a resolvable single key. Any counterparty appearing under multiple local identifiers will be counted multiple times or not at all. The failure invalidates the aggregate, not merely degrades it.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶46(a)) — *"aggregated credit exposure to a large corporate borrower"* named as a critical timeliness case; Principle 5 (¶46(b)) — *"counterparty credit risk exposures, including, for example, derivatives"*
- **Search terms:** counterparty ID, legal entity identifier, LEI, counterparty master, party key, obligor ID, entity reference, golden record, customer master
- **Data quality requirements:**
  - *uniqueness* — Each counterparty entity maps to exactly one authoritative identifier across all source systems | count of counterparty entities with more than one active identifier in the group master | target: zero duplicates; tolerance: <0.01% of active counterparty population with unresolved duplicates
  - *accuracy* — The identifier resolves to the correct legal entity, including correct hierarchy linkage to ultimate parent | count of identifiers where group hierarchy parent is null or mismatched against external LEI registry | target: 100% of identifiers with non-null, validated parent linkage
  - *completeness* — Every exposure record carries a populated, non-null counterparty identifier | count of exposure records with null or unresolvable counterparty identifier | target: 0% null; escalation trigger: any null in credit or derivatives books
  - *timeliness* — New counterparties onboarded within the aggregation cycle are available before the aggregation run | lag in hours between counterparty creation in source system and availability in the group master | target: available within the agreed SLA for each reporting frequency tier

---

**CDE-02 — Legal Entity / Booking Entity Identifier**
- **Definition:** The unique identifier of the bank's own legal entity in which a transaction or position is booked. Represents the specific regulated subsidiary or branch, not a business line label. Supports group consolidation by identifying which entity holds the exposure.
- **Why critical:** Group-level aggregation requires summing or consolidating positions held across multiple booking entities. Without a governed legal entity identifier on every record, it is impossible to produce subsidiary-level reports, apply jurisdiction-specific regulatory constraints, or consolidate correctly at group level. ¶30 explicitly names subsidiaries not included as a coverage gap that senior management must understand.
- **Risk types:** Credit / market / liquidity / concentration / cross-cutting
- **Criticality: 3** — Group consolidation and subsidiary-level reporting are *impossible* if booking entity is absent or inconsistent. Exposures cannot be attributed to the correct regulated entity, invalidating both the group aggregate and any entity-level regulatory report.
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 heading — *"Data should be available by … legal entity"*; Principle 1 (¶30) — *"limitations … in terms of coverage … subsidiaries not included"*
- **Search terms:** legal entity identifier, booking entity, entity code, LEI, branch code, subsidiary code, registered entity, group entity hierarchy, consolidation entity
- **Data quality requirements:**
  - *completeness* — Every risk position and exposure record carries a non-null, resolvable legal entity identifier | count of records with null or unrecognised legal entity code | target: 0% null
  - *validity* — The legal entity code matches a current, active entry in the authoritative group entity hierarchy | count of records referencing decommissioned, merged, or unrecognised entity codes | target: 0% invalid references; hierarchy updated within one business day of any structural change
  - *consistency* — The same entity is named identically across risk systems, accounting systems, and the group entity master | count of entity names or codes that exist in risk systems but have no match in the group entity master | target: 0% unmatched entities in any production risk system

---

**CDE-03 — Gross Exposure Amount**
- **Definition:** The monetary amount representing the bank's gross risk exposure to a counterparty, instrument, or position before the application of netting, collateral, or credit risk mitigation. Denominated in a stated transaction currency, with a separate group-reporting currency equivalent. Covers on- and off-balance-sheet items.
- **Why critical:** This is the raw numeric input from which every aggregated risk measure — total credit exposure, concentration ratio, large exposure threshold, regulatory capital calculation — is derived. Without a governed, accurate exposure amount, no risk aggregate has a sound numeric foundation. ¶41 explicitly requires off-balance-sheet coverage, meaning the definition must include contingent and derivative exposures.
- **Risk types:** Credit / counterparty / concentration / market / cross-cutting
- **Criticality: 3** — The exposure amount *is* the risk figure. Its absence or systematic misstatement does not degrade an aggregate — it invalidates it. No downstream calculation (VaR, RWA, concentration limit utilisation) is valid without accurate gross exposure.
- **Driven by:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 7 (¶52) — *"accurate and precise to ensure … board and senior management can rely with confidence on the aggregated information"*
- **Search terms:** exposure amount, notional amount, outstanding balance, drawn amount, mark-to-market, fair value, current exposure, gross exposure, EAD, position value, contingent exposure
- **Data quality requirements:**
  - *accuracy* — The exposure amount on each risk record agrees to the corresponding amount in the general ledger or system of record within a defined tolerance | sum of absolute differences between risk system exposure and GL balance, by booking entity and product type | target: reconciliation variance <0.1% of total portfolio value; any individual item variance >threshold escalated same day
  - *completeness* — No material exposure category is systematically absent from the aggregated dataset | count and value of off-balance-sheet product types with zero exposure population relative to the prior period and accounting records | target: 0% unexplained zero-population product categories
  - *timeliness* — Exposure amounts reflect the agreed as-of date position within the defined cut-off window | count of exposure records whose value date lags the stated position date by more than the agreed threshold | target: 100% of records valued as of the correct date within the agreed cut-off

---

**CDE-04 — Risk Type Classification**
- **Definition:** The categorical label assigned to each exposure or position that identifies the primary risk type (credit risk, market risk, liquidity risk, operational risk, counterparty credit risk) and, where applicable, the sub-type (e.g., single-name credit, settlement risk, interest rate risk in the banking book). This is the taxonomy element that partitions the universe of risk data.
- **Why critical:** Aggregation, capital calculation, and reporting are all organised by risk type. An exposure misclassified as market risk rather than credit risk will appear in the wrong aggregate, distort capital allocation, and produce incorrect regulatory reports. ¶57 requires reports to cover "all significant risk areas" and "significant components of those risk areas," which presupposes that the classification itself is accurate and consistently applied.
- **Risk types:** Cross-cutting (governs the taxonomy for all risk types)
- **Criticality: 2** — Misclassification degrades aggregates and makes cross-risk comparison unreliable, but the aggregate for each risk type is still *produced*. The failure makes outputs untrustworthy and unsliceable by correct type without invalidating the arithmetic sum itself. Criticality 3 would apply only if the classification schema were entirely absent.
- **Driven by:** Principle 2 (¶33) — *"integrated data taxonomies and architecture across the banking group"*; Principle 3 (¶37) — *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"*; Principle 8 (¶57) — *"exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*
- **Search terms:** risk type, risk category, risk class, risk taxonomy, product type, exposure classification, risk sub-type, IRRBB, CCR, settlement risk label
- **Data quality requirements:**
  - *validity* — Every exposure record carries a risk type value drawn from the authoritative, board-approved risk taxonomy | count of records with null risk type or a value not present in the approved taxonomy reference list | target: 0% invalid or null values
  - *consistency* — The same instrument type is classified to the same risk type across all source systems that contribute to the aggregate | count of instrument types that carry different risk type labels in different contributing systems | target: 0% cross-system classification conflicts for the same instrument type
  - *accuracy* — Reclassifications between risk types are tracked, dated, and authorised | count of risk type changes on existing records without an associated authorisation record and effective date | target: 100% of reclassifications have an audit entry

---

**CDE-05 — Business Line**
- **Definition:** The organisational dimension that identifies the business unit or line of business (e.g., retail banking, corporate banking, trading, asset management, private banking) responsible for or owning the exposure. Defined at the level of granularity used in management reporting and risk appetite.
- **Why critical:** Principles 4 and 6 explicitly require data to be aggregatable and reportable by business line. An exposure record without a governed business line attribute cannot contribute to business-line-level risk reports, cannot be monitored against business-line risk limits, and cannot be used to identify concentrations within a line of business. ¶50 specifically describes the expectation that aggregation across all business lines is possible on demand.
- **Risk types:** Cross-cutting (aggregation dimension for all risk types)
- **Criticality: 2** — Business line is a required reporting slice. Its failure degrades report completeness and renders business-line limits unmonitorable, but the group-level aggregate (undifferentiated) remains producible. Criticality 3 applies only if business line is the *only* feasible path to aggregation — generally not the case at group level.
- **Driven by:** Principle 4 heading — *"Data should be available by business line"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures … across all business lines and geographic areas"*; Principle 8 (¶57) — reports must cover all significant risk areas by component
- **Search terms:** business line, business unit, LOB, division, profit centre, desk, segment, business segment code, organisational unit
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a non-null, valid business line code | count of exposure records with null or unrecognised business line | target: 0% null; <0.05% unrecognised codes before remediation
  - *validity* — Business line values match the current organisational hierarchy approved for risk reporting | count of records referencing retired, renamed, or unapproved business line codes | target: 0% invalid references; hierarchy updated within one business day of any restructuring
  - *consistency* — The business line attributed in risk systems matches the attribution in management accounting for the same positions | count of positions where business line differs between the risk system and the management accounting system | target: <0.1% unexplained discrepancies; all discrepancies investigated and resolved within the reporting cycle

---

**CDE-06 — Geography / Country of Risk**
- **Definition:** The country or geographic region to which the risk of an exposure is attributed for aggregation purposes. Distinct from the booking entity's domicile; this is the obligor's country of risk or the country where the collateral is located, as appropriate to the risk type. May be expressed as ISO country code with a defined hierarchy to region.
- **Why critical:** ¶50 explicitly uses country credit exposure as the paradigm example of an ad hoc aggregation request. Concentration risk by geography, regulatory reporting of cross-border exposures, and stress testing of country scenarios all depend on this element being accurately attributed and consistently defined. Its absence makes geographic concentration reports impossible to produce.
- **Risk types:** Credit / market / liquidity / concentration / cross-cutting
- **Criticality: 2** — Geographic aggregation is a required reporting slice. Failures degrade concentration and country risk reports without necessarily invalidating the total exposure figure. Where a geography-specific stress test is the *only* route to a required output, criticality rises to 3 for that specific use case.
- **Driven by:** Principle 4 heading — *"Data should be available by … region"*; Principle 5 (¶46(c)) — *"market concentrations by sector and region data"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures … based on a list of countries"*
- **Search terms:** country of risk, country code, obligor country, risk country, jurisdiction, geographic region, domicile, country of residence, ISO country, cross-border exposure
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a non-null country of risk attribution | count of exposure records with null or missing country code | target: 0% null for credit and counterparty exposures
  - *accuracy* — Country of risk attribution follows the bank's approved methodology (e.g., ultimate obligor country, not booking location) consistently across all source systems | count of records where country of risk equals booking entity domicile for non-domestic obligors, flagged for review | target: methodology applied consistently; cross-system variance <0.1% of portfolio by value
  - *validity* — Country codes reference the approved ISO 3166-1 alpha-2 standard or the bank's approved country hierarchy | count of records with non-standard, retired, or unrecognised country codes | target: 0% invalid codes

---

**CDE-07 — Industry / Sector Classification**
- **Definition:** The economic sector or industry to which a counterparty or obligor is attributed (e.g., using a standard taxonomy such as NACE, GICS, SIC, or the bank's own internal sector schema). Applied at the counterparty or facility level, depending on the bank's methodology.
- **Why critical:** ¶50 explicitly names industry credit exposure aggregation by sector across all business lines as a paradigm ad hoc aggregation case. ¶57 names industry sector as a required component of credit risk reporting. Sector concentration risk cannot be measured or reported without this element.
- **Risk types:** Credit / concentration
- **Criticality: 2** — Sector is a required reporting slice for credit concentration. Its failure prevents sector-level concentration reports from being produced correctly. The total credit aggregate remains valid; the sector breakdown does not. A missing sector creates an unallocated residual that supervisors will flag.
- **Driven by:** Principle 4 heading — *"Data should be available by … industry"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*
- **Search terms:** industry code, sector code, NACE, GICS, SIC, industry classification, sector classification, obligor sector, counterparty industry
- **Data quality requirements:**
  - *completeness* — Every credit counterparty record carries a non-null, validated industry/sector code | count of counterparty records and linked exposure records with null sector attribution | target: 0% null for credit counterparties
  - *validity* — Sector codes reference the bank's approved classification schema version current at the reporting date | count of records with codes from retired schema versions or not present in the current reference list | target: 0% invalid codes; reference list versioned and dated
  - *consistency* — Sector attribution is assigned at the counterparty level and propagates consistently to all facilities for that counterparty, unless a specific facility-level override is justified and documented | count of counterparties where two or more facilities carry different sector codes without an approved override | target: 0% unexplained cross-facility inconsistency per counterparty

---

**CDE-08 — Position / As-Of Date**
- **Definition:** The business date as of which a risk position, exposure, or valuation is stated. This is the temporal reference point for every aggregate: the date that identifies *when* the snapshot was taken, not when the record was processed or loaded.
- **Why critical:** Every aggregated risk figure is meaningless without an unambiguous as-of date. Mixing positions from different as-of dates produces a fictitious aggregate — neither the position at date T nor at date T-1. Reconciliation between risk and accounting is impossible if the two datasets use different cut-offs without explicit adjustment. ¶45 requires rapid production in stress — which requires clear, queryable position dates to select the correct snapshot.
- **Risk types:** Cross-cutting (temporal key for all risk types)
- **Criticality: 3** — Without a governed position date, it is *impossible* to confirm that aggregated figures represent a coherent point-in-time snapshot. Mixing stale and current positions without controlled date stamping invalidates the aggregate. This is not degradation — it is a structural invalidity.
- **Driven by:** Principle 5 heading — *"generate aggregate and up-to-date risk data in a timely manner"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (¶53(a)) — *"defined requirements and processes to reconcile reports to risk data"* (reconciliation presupposes an agreed reference date)
- **Search terms:** position date, as-of date, value date, reporting date, snapshot date, data extraction date, effective date, reference date, business date
- **Data quality requirements:**
  - *accuracy* — The position date on each record accurately reflects the business date of the position, not the processing or load date | count of records where position date equals system load timestamp but differs from the expected business date | target: 0% records with position date defaulting to load timestamp
  - *completeness* — Every exposure and position record carries a non-null position date | count of records with null or invalid (e.g., 1900-01-01, 9999-12-31) position date | target: 0% null or placeholder dates
  - *timeliness* — The most recent completed aggregation snapshot represents the agreed business date cut-off, within the SLA for each report frequency tier | elapsed time between market close / book close and availability of a fully populated position-date snapshot in the aggregation layer | target: within the agreed SLA per risk type; intraday capability demonstrable for trading book

---

**CDE-09 — General Ledger / System-of-Record Reconciliation Key**
- **Definition:** The identifier — typically an account number, transaction reference, or instrument identifier — that links a risk record to its corresponding entry in the general ledger (GL) or the authoritative accounting system of record. This is the reconciliation anchor required by ¶36(c).
- **Why critical:** ¶36(c) states that risk data must be reconciled with the bank's accounting sources to ensure accuracy. Without a field that explicitly links a risk record to the GL, reconciliation is at best a bulk-balance comparison that cannot identify which specific records are causing discrepancies. Without this key, it is impossible to evidence accuracy at the transaction level, which is what supervisors expect (¶36(a): controls as robust as accounting data). This CDE is the most frequently omitted in practice and among the most defensible under examination.
- **Risk types:** Cross-cutting (reconciliation mechanism for credit, market, and liquidity)
- **Criticality: 3** — Without this key, accuracy *cannot be evidenced* at the granular level required. ¶36(a) requires controls as robust as accounting; those controls require a join. Bulk-balance reconciliation alone does not satisfy the principle — supervisors expect transaction-level traceability. The absence of this key means accuracy is asserted rather than demonstrated.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 7 (¶53(a)) — *"defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** GL account, general ledger account number, accounting reference, transaction reference, instrument ID, ISIN, trade ID, deal reference, source transaction key, accounting entry ID, reconciliation key
- **Data quality requirements:**
  - *completeness* — Every material risk record carries a non-null GL or system-of-record reconciliation key | count of risk records with null reconciliation key, stratified by product type and materiality threshold | target: 0% null for on-balance-sheet positions; coverage target for OTC derivatives and off-balance-sheet items to be set per product type
  - *accuracy* — The reconciliation key on a risk record resolves to an existing, active entry in the GL or system of record | count of risk records whose reconciliation key returns no match in the GL within the same reference period | target: <0.1% unmatched keys by count; <0.05% by value; all unmatched items investigated within the same reporting cycle
  - *uniqueness* — Each GL entry is referenced by at most one risk record (or the many-to-one relationship is explicitly mapped and governed) | count of GL entries matched by more than one risk record without an approved mapping rule | target: 0% unexplained one-to-many relationships

---

**CDE-10 — Source System Identifier / Manual Override Flag**
- **Definition:** Two closely related attributes that together constitute the lineage/provenance record for a risk data item: (a) the identifier of the source system from which the data originated (e.g., the trading system, the loan origination system, the treasury system), and (b) a flag indicating whether the value was produced by an automated feed or introduced/modified through a manual process, end-user computing tool, or spreadsheet.
- **Why critical:** ¶36(b) requires specific mitigants for manual processes and EUC applications. ¶39 requires all aggregation processes — automated and manual — to be documented, with manual workarounds explicitly described and their criticality assessed. Without a source system identifier and manual flag on each record, it is impossible to: (i) identify which data in a report came from EUC inputs, (ii) assess the proportion of the portfolio subject to weaker controls, (iii) produce the documentation supervisors expect, or (iv) track improvement over time. This is the second most commonly omitted element in catalog implementations.
- **Risk types:** Cross-cutting (governance and control quality for all risk types)
- **Criticality: 2** — The absence of this element does not invalidate a single aggregate figure, but it makes it *impossible to demonstrate that the accuracy and integrity obligations of Principle 3 have been met* for any figure derived from manual processes. An aggregate produced partly from untracked manual inputs cannot be validated as reliable. Criticality 2 rather than 3 because the aggregate is arithmetically producible; but from a regulatory defensibility standpoint, the gap is severe.
- **Driven by:** Principle 3 (¶36(b)) — *"effective mitigants in place (eg end-user computing policies and procedures) and other effective controls"*; Principle 3 (¶36(d)) — *"a single authoritative source for risk data per each type of risk"*; Principle 3 (¶39) — *"document and explain all of their risk data aggregation processes whether automated or manual … description of their criticality to the accuracy of risk data aggregation and proposed actions to reduce the impact"*
- **Search terms:** source system, system of origin, feed source, data source ID, manual entry flag, EUC flag, spreadsheet flag, override flag, upload flag, data provenance, lineage tag, golden source indicator
- **Data quality requirements:**
  - *completeness* — Every risk record carries a non-null source system identifier | count of risk records with null or unrecognised source system identifier | target: 0% null; 0% unrecognised system codes
  - *validity* — Source system identifiers reference a current, registered entry in the bank's authorised system inventory (the data architecture catalog) | count of source system codes on risk records that have no match in the system inventory | target: 0% unregistered system codes
  - *accuracy* — The manual override flag correctly identifies records modified outside the automated feed | count of records where the load mechanism indicates a manual upload but the manual flag is set to false, or vice versa | target: 0% flag/mechanism mismatches; validated by reconciling feed logs against flag population
  - *timeliness* — Records flagged as manually entered are escalated for review within the same aggregation cycle in which they appear | count of manual-flagged records that entered an aggregation run without a documented review sign-off | target: 0% unsigned manual entries in production aggregation runs

---

**CDE-11 — Reporting Currency and FX Rate Applied**
- **Definition:** Two linked elements: (a) the transaction currency in which the original exposure is denominated, and (b) the exchange rate applied to convert that amount to the group reporting currency. Together they determine the group-currency equivalent exposure amount that feeds aggregated risk reports.
- **Why critical:** A bank operating across multiple jurisdictions aggregates exposures denominated in dozens of currencies. If the transaction currency is missing, the correct FX conversion cannot be applied. If the FX rate is not governed, different systems may apply different rates on the same date, producing inconsistent group-level aggregates that cannot be reconciled. Currency mismatch is a common and material source of aggregation error that directly distorts exposure totals. ¶43 requires completeness; ¶36(a) requires accounting-grade controls — both are compromised by ungoverned FX conversion.
- **Risk types:** Credit / market / liquidity / concentration / cross-cutting
- **Criticality: 2** — The group-currency aggregate is producible even with imperfect FX rates, but the result is systematically inaccurate. The failure degrades every cross-currency aggregate rather than making it impossible. Criticality 3 would apply if the bank had no conversion mechanism at all; that is rare in practice.
- **Driven by:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"* (FX conversion is an accounting-grade control); Principle 4 (¶42) — *"A banking organisation is not required to express all forms of risk in a common metric … each system should make clear the specific approach used to aggregate exposures"*; Principle 4 (¶43) — *"produce aggregated risk data that is complete"*
- **Search terms:** transaction currency, currency code, ISO 4217, FX rate, exchange rate, conversion rate, reporting currency, base currency, EUR equivalent, USD equivalent, spot rate, rate source
- **Data quality requirements:**
  - *accuracy* — The FX rate applied to each record matches the bank's official rate source for the position date | count of records where the applied rate deviates from the official rate source by more than a defined tolerance on the same date | target: 0% deviations outside tolerance; official rate source identified and governed in the data catalog
  - *completeness* — Every exposure record denominated in a non-reporting currency carries a non-null transaction currency code and a non-null FX rate | count of non-reporting-currency records with null currency code or null FX rate | target: 0% null for both fields
  - *consistency* — The same position carries the same FX rate across all systems that hold it simultaneously within an aggregation cycle | count of positions where two contributing systems apply different FX rates for the same position date | target: 0% cross-system rate discrepancies within the same aggregation cycle

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Risk-to-Finance Reconciliation Completeness**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-08 (Position / As-Of Date), CDE-09 (GL / System-of-Record Reconciliation Key), CDE-02 (Legal Entity Identifier)
- **Regulatory basis:** ¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; ¶36(a): *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; ¶53(a): *"defined requirements and processes to reconcile reports to risk data"*

This requirement cannot be expressed by monitoring any single CDE because it is relational: it tests whether the *joint* population of risk records, each carrying a reconciliation key, a position date, and an exposure amount, agrees to the corresponding accounting entries in the GL for the same legal entity and same date. No individual-element DQ rule detects a systematic misstatement that is internally consistent but diverges from the accounting record.

- *accuracy* — The sum of exposure amounts in the risk aggregation layer equals the corresponding GL balances for each product type and booking entity at each reporting date, within approved materiality thresholds | total absolute variance between risk system aggregate and GL balance, stratified by legal entity, product type, and currency, stated as both absolute amount and percentage of GL balance | suggested threshold: portfolio-level variance <0.1% of total on-balance-sheet exposure; no single legal entity variance >0.5%; all variances above a defined monetary threshold investigated and explained within the reporting cycle
- *completeness* — All product types held in the GL are represented in the risk aggregation dataset with no systematic category omission | count and notional value of GL product types with zero or implausibly low representation in the risk data layer relative to the prior period | target: 0% unexplained product-type omissions; any new product type appearing in the GL within 30 days triggers a classification review in the risk taxonomy

---

**XDQ-02 — Counterparty Entity Resolution Across Source Systems**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-07 (Industry / Sector Classification), CDE-06 (Geography / Country of Risk)
- **Regulatory basis:** ¶33: *"use of single identifiers and/or unified naming conventions … including … counterparties"*; ¶46(a): *"aggregated credit exposure to a large corporate borrower"* as a critical timeliness case; ¶50: aggregation of country and industry exposures *"across all business lines and geographic areas"*

Monitoring CDE-01 in isolation confirms that individual records carry a counterparty identifier. This cross-cutting requirement tests whether *the same counterparty appearing in multiple source systems* is resolved to a single group identifier before aggregation. If resolution fails, a counterparty with exposures in the loan system, the derivatives system, and the securities system will generate three separate entries in the aggregate, fragmenting concentration risk and making large-exposure reporting incorrect. No single-element rule detects this; it requires a cross-system matching check.

- *uniqueness* — Each distinct legal-entity counterparty has exactly one active group identifier, and all source systems reference that identifier for all positions with that counterparty | count of counterparty legal entities — verifiable against the external LEI registry — that map to more than one active group identifier, and count of source systems with unresolved local-to-group identifier mappings | target: 0% unresolved duplicates in the group master; 100% of source system counterparty populations mapped to the group master before each aggregation run
- *consistency* — Counterparty-level attributes (sector, country of risk, group hierarchy) are identical across all source systems for the same group identifier | count of counterparties where sector code, country of risk, or parent entity hierarchy differs between two or more contributing source systems for the same group counterparty identifier | target: <0.1% of active counterparty population with unresolved attribute conflicts; all conflicts flagged to the data owner for resolution within the reporting cycle
- *completeness* — The group counterparty master covers 100% of counterparties present in any source system contributing to risk aggregation | count of counterparty identifiers present in contributing source systems but absent from the group master | target: 0% unmapped counterparties in any production aggregation run

---

**XDQ-03 — Manual Process Coverage and Escalation Traceability**

- **CDEs spanned:** CDE-10 (Source System Identifier / Manual Override Flag), CDE-03 (Gross Exposure Amount), CDE-09 (GL / System-of-Record Reconciliation Key)
- **Regulatory basis:** ¶36(b): *"effective mitigants in place (eg end-user computing policies and procedures)"*; ¶39: *"document and explain all of their risk data aggregation processes whether automated or manual … description of their criticality to the accuracy of risk data aggregation and proposed actions to reduce the impact"*; ¶40: *"measure and monitor the accuracy of data and to develop appropriate escalation channels"*

No single CDE monitors whether manual inputs are escalated, reviewed, and tracked toward remediation. This cross-cutting requirement tests the *population* of manually-flagged records — their share of total exposure value, the review workflow attached to them, and the trend of manual input reduction over time. Supervisors expect a documented trajectory of automation improvement (¶39: "proposed actions to reduce the impact"); this can only be measured at the portfolio level, not at the level of any single record.

- *accuracy* — Manual and EUC-sourced records are reviewed and signed off before they contribute to any aggregation run | count of manual-flagged records that entered a completed aggregation run without a documented review sign-off in the workflow system | target: 0% unsigned manual entries in any production run; all manual inputs reviewed within the same business day as entry
- *completeness* — The share of total exposure value sourced from manual or EUC processes is measured and reported each aggregation cycle | percentage of total group exposure value (by risk type) attributable to manually-flagged source records | target metric: reported each period; reduction trajectory defined and approved by senior management per ¶39; escalation if manual share increases by more than a defined percentage point quarter-on-quarter without explanation
- *timeliness* — Errors identified in manual data are escalated and corrected within the same reporting cycle | elapsed time between identification of a manual data error and resolution in the aggregation dataset | target: all material manual errors resolved before final report sign-off; escalation to senior management if resolution cannot be achieved within cycle

---

## 4. Out of Scope

The following table is explicit about what the CDE register and DQ monitoring program described above *cannot* deliver, and what would be required instead. Where a principle also drives a CDE, the split is explained.

---

### Principle 1 — Governance (¶27–31)

**Partially addressable, partially out of scope.**

The catalog can *support* Principle 1 by hosting the data dictionary (¶37), recording data ownership assignments (¶34), and making the CDE register and DQ monitoring results visible to validation and audit teams (¶29(a)). These are necessary but not sufficient.

What the catalog cannot deliver:
- Board and senior management review and approval of the framework (¶28) — this is a governance process requiring documented board minutes, sign-off workflows, and committee structures, none of which live in a data catalog.
- Inclusion of BCBS 239 compliance in new-product and acquisition due diligence (¶29(b)) — this is a change management and M&A process.
- Senior management awareness of limitations and an IT strategy for remediation (¶30) — the catalog can surface limitations (e.g., manual flag rates from XDQ-03, entity coverage gaps from CDE-02), but it cannot compel strategic decisions or resource allocation.
- The independent validation program (¶29(a)) — the catalog provides evidence inputs to validation; the validation function itself is organisational and procedural.

---

### Principle 2 — Data Architecture and IT Infrastructure (¶32–35)

**Partially addressable, partially out of scope.**

The catalog directly addresses ¶33 (metadata, single identifiers, unified naming conventions) and ¶34 (data ownership roles). CDE-01, CDE-02, and CDE-10 are direct expressions of ¶33 requirements.

What the catalog cannot deliver:
- The underlying IT infrastructure (¶32, ¶35) — a data catalog documents what exists; it does not build integrated data stores, automated feeds, or disaster recovery systems. Business continuity planning (¶32) requires operational IT architecture, not metadata governance.
- Automated data aggregation pipelines — the catalog maps and monitors them; it does not replace them.

---

### Principle 7 — Accuracy (¶52–56) — *also drives CDEs*

**Partially addressable, partially out of scope.**

Principle 7 drives CDE-03, CDE-08, CDE-09, and XDQ-01 directly. The reconciliation and validation rules in the CDE register are the catalog's contribution to this principle.

What the catalog cannot deliver:
- The validation rule inventory required by ¶53(b) is partially addressable: the catalog can host a register of validation rules as metadata. However, executing those rules, generating exceptions reports (¶53(c)), and routing them through escalation channels (¶40) requires an operational DQ toolchain connected to live data, not metadata records alone.
- Accuracy and precision *requirements* (¶55) — setting these is a management decision, not a catalog function. The catalog records and makes visible the agreed thresholds; it does not determine them.
- Materiality assessment analogous to accounting materiality (¶56) — this is a judgement exercised by risk management and finance, informed by catalog outputs but not produced by them.

---

### Principle 8 — Comprehensiveness (¶57–60) — *also drives CDEs*

**Partially addressable, partially out of scope.**

Principle 8 drives CDE-07 (industry/sector) as a required reporting dimension (¶57) and implicitly supports CDE-04 (risk type taxonomy). These elements belong in the catalog.

What the catalog cannot deliver:
- The *content* of comprehensive risk reports: coverage of capital adequacy, regulatory capital, liquidity ratios, stress testing results, and forward-looking forecasts (¶59–60) — these are report-design and risk-modelling matters. The catalog ensures the underlying data elements exist and are governed; it has no role in report layout, narrative content, scenario selection, or forward-looking analysis.
- Confirmation that reports cover "all significant risk areas" (¶57) — this is an assertion made by the risk management function on the basis of their risk inventory, not something that follows automatically from CDE completeness.

---

### Principle 9 — Clarity and Usefulness (¶61–69)

**Substantially out of scope, with one narrow exception.**

¶67 requires a bank to develop an "inventory and classification of risk data items" — this is directly what a data catalog with a governed CDE register provides. That is the narrow contribution.

Everything else in Principle 9 is out of scope:
- Report clarity, balance of qualitative versus quantitative content, tailoring to recipient needs (¶61–68) — these are report design and communication decisions made by risk reporting teams.
- Periodic confirmation with recipients that reports are relevant (¶69) — this is a governance process involving structured feedback from board and senior management; no data catalog addresses it.

---

### Principle 10 — Frequency (¶70–71)

**Entirely out of scope.**

Principle 10 concerns how often reports are produced and the bank's ability to accelerate production in stress. The catalog has no role here. The catalog can record the agreed frequency SLAs as metadata on report objects and can surface timeliness DQ metrics (see CDE-08, timeliness dimension) that *inform* whether frequency requirements are being met. But:
- Setting frequency requirements is a governance decision by the board and senior management.
- Building systems capable of intraday production (¶71) is an infrastructure investment.
- Routinely testing the ability to produce reports within timeframes (¶70) is an operational testing process.

None of these are addressable by metadata management.

---

### Principle 11 — Distribution (¶72–74)

**Entirely out of scope.**

Principle 11 concerns report distribution — delivery to the right people, within the right timeframe, with appropriate confidentiality controls. The catalog governs data about data; it does not govern report delivery channels, access control lists on report distribution systems, or confirmation that recipients received reports. These are addressed by:
- Report scheduling and distribution tooling (e.g., report servers, secure file transfer).
- Identity and access management systems.
- Periodic operational checks confirming delivery (¶73).

A catalog may record data sensitivity classifications that inform access decisions, but that is a precursor to distribution governance, not the governance itself.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | P2 (¶33), P4, P5 (¶46a/b) | Uniqueness, Accuracy, Completeness, Timeliness |
| CDE-02 | Legal Entity / Booking Entity Identifier | 3 | P2 (¶33), P4, P1 (¶30) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | P3 (¶36a), P4 (¶41), P7 (¶52) | Accuracy, Completeness, Timeliness |
| CDE-04 | Risk Type Classification | 2 | P2 (¶33), P3 (¶37), P8 (¶57) | Validity, Consistency, Accuracy |
| CDE-05 | Business Line | 2 | P4, P6 (¶50), P8 (¶57) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | 2 | P4, P5 (¶46c), P6 (¶50) | Completeness, Accuracy, Validity |
| CDE-07 | Industry / Sector Classification | 2 | P4, P6 (¶50), P8 (¶57) | Completeness, Validity, Consistency |
| CDE-08 | Position / As-Of Date | 3 | P5, P6 (¶50), P7 (¶53a) | Accuracy, Completeness, Timeliness |
| CDE-09 | GL / System-of-Record Reconciliation Key | 3 | P3 (¶36a/c), P7 (¶53a) | Completeness, Accuracy, Uniqueness |
| CDE-10 | Source System Identifier / Manual Override Flag | 2 | P3 (¶36b/d, ¶39) | Completeness, Validity, Accuracy, Timeliness |
| CDE-11 | Reporting Currency and FX Rate Applied | 2 | P3 (¶36a), P4 (¶42/43) | Accuracy, Completeness, Consistency |
| XDQ-01 | Risk-to-Finance Reconciliation Completeness | — (cross-cutting) | P3 (¶36a/c), P7 (¶53a) | Accuracy, Completeness |
| XDQ-02 | Counterparty Entity Resolution Across Systems | — (cross-cutting) | P2 (¶33), P5 (¶46a), P6 (¶50) | Uniqueness, Consistency, Completeness |
| XDQ-03 | Manual Process Coverage and Escalation Traceability | — (cross-cutting) | P3 (¶36b, ¶39, ¶40) | Accuracy, Completeness, Timeliness |