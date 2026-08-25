# BCBS 239 â Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

### What the regulation is trying to achieve

- **Risk data must be accurate, complete, and timely across the entire banking group, including under stress.** A bank must be able to aggregate all material risk exposures â across legal entities, business lines, geographies, and asset types â rapidly enough to support decisions in a crisis. (Principle 3, Â¶36; Principle 4, Â¶41; Principle 5, Â¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*)

- **Data architecture must be designed for aggregation, not retrofitted.** The bank must establish *"integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts."* (Principle 2, Â¶33)

- **Risk data must be reconciled to authoritative sources, especially accounting.** Controls on risk data must be *"as robust as those applicable to accounting data"* and risk data must be *"reconciled with bank's sources, including accounting data where appropriate."* (Principle 3, Â¶36(a) and Â¶36(c))

- **The provenance and automation status of every data input must be documented and monitored.** Banks must *"document and explain all of their risk data aggregation processes whether automated or manual,"* and manual workarounds must be documented, assessed for criticality, and have remediation plans. (Principle 3, Â¶39)

- **Aggregation must be adaptable to ad hoc slicing across any dimension.** Supervisors explicitly expect banks to be able to *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries, as well as industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas."* (Principle 6, Â¶50)

- **Risk reports must be reconciled and validated, not just produced.** Reports must meet defined accuracy standards with *"defined requirements and processes to reconcile reports to risk data"* and an *"inventory of the validation rules that are applied to quantitative information."* (Principle 7, Â¶53(a) and Â¶53(b))

### Who it applies to

BCBS 239 was issued for **Global Systemically Important Banks (G-SIBs)** and is expected to be applied proportionately to **Domestic Systemically Important Banks (D-SIBs)** by national supervisors. The obligations fall on the **consolidated banking group**, meaning every subsidiary, booking entity, and jurisdiction the group operates in is in scope. The principles are board-level and enterprise-wide: they cannot be satisfied by any single system or business line in isolation.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Identifier**

- **Definition:** A unique, persistent identifier assigned to each legal-entity counterparty (borrower, derivative counterparty, guarantor, issuer) that resolves to the same record regardless of which booking system, product line, or geography originated the transaction. This is distinct from a customer number, which may be system-local.
- **Why critical:** Without a single resolved counterparty identifier, exposures from different systems cannot be summed to produce a group-level counterparty total. A bank cannot know its aggregate credit exposure to a large corporate borrower â the textbook stress scenario in Â¶46(a) â without this key.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3.** *Without this element, the aggregate credit exposure to counterparty X cannot be computed at all, because records from different booking systems refer to the same counterparty under different local identifiers and cannot be joined.*
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶41) â all material exposures must be captured; Principle 5 (Â¶46(a)) â *"The aggregated credit exposure to a large corporate borrower"* is named as a critical risk requiring rapid aggregation.
- **Search terms:** counterparty ID, counterparty key, legal entity identifier, LEI, obligor ID, counterparty master, party identifier, golden record counterparty
- **Data quality requirements:**
  - *Uniqueness* â Each real-world counterparty entity maps to exactly one active identifier in the counterparty master | Count of duplicate or conflicting counterparty records mapping to the same legal entity | Target: 0 duplicates in master; any match to an external LEI registry that contradicts the internal record is an exception
  - *Completeness* â Every exposure record carries a non-null, resolvable counterparty identifier | Count of exposure records with null or unmatched counterparty identifier as a proportion of total exposure population | Target: <0.1% by count; 0% by notional above materiality threshold
  - *Consistency* â The identifier used in the risk data store matches the identifier in the counterparty master (not a local alias) | Count of exposure records whose counterparty identifier resolves only within a single source system and not to the enterprise master | Target: 0 unresolved local aliases in aggregated positions

---

**CDE-02 â Legal Entity / Booking Entity Identifier**

- **Definition:** The identifier of the specific legal entity within the banking group that is the booking entity for a transaction â i.e., the regulated subsidiary or branch whose balance sheet carries the exposure. Distinct from a business line or cost centre.
- **Why critical:** Group consolidation and subsidiary-level reporting are only possible if every transaction is tagged to its booking entity. Without this, the bank cannot produce entity-level risk reports, cannot consolidate upward, and cannot demonstrate that all subsidiaries are captured as required by Principles 4 and 8.
- **Risk types:** Cross-cutting (all risk types at consolidated and entity level)
- **Criticality: 3.** *Without this element, the aggregate exposure for legal entity Y cannot be computed at all, because transactions from different entities cannot be separated or consolidated â group consolidation and the subsidiary roll-up are structurally impossible.*
- **Driven by:** Principle 2 (Â¶33) â *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (Â¶41) â *"capture and aggregate all material risk data across the banking group"*; Principle 1 (Â¶30) â senior management must understand *"coverage (eg risks not captured or subsidiaries not included)"* as a limitation.
- **Search terms:** legal entity identifier, booking entity, LEI, entity code, subsidiary code, branch code, booking location, reporting entity, consolidation entity
- **Data quality requirements:**
  - *Validity* â Every legal entity identifier in the risk data store must exist in the authoritative legal entity hierarchy | Count of exposure records carrying an entity code not present in the group legal entity hierarchy | Target: 0
  - *Completeness* â Every transaction record carries a non-null booking entity identifier | Count of records with null booking entity as a proportion of total | Target: 0% for any record included in a regulatory report
  - *Consistency* â The entity identifier is used uniformly across risk, finance, and treasury systems for the same booking entity | Count of entity codes in risk data that do not have a confirmed mapping to the finance general ledger entity hierarchy | Target: 0 unmapped entities in any consolidated report

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The pre-mitigation monetary amount of a risk position â the face value, notional, or drawn balance that represents what the bank is exposed to before application of collateral, netting, or guarantees. Expressed in transaction currency; a separate element (CDE-04) handles the reporting currency conversion.
- **Why critical:** This is the fundamental quantity that risk aggregation sums. Every credit exposure total, VaR calculation, and liquidity metric is built by aggregating this field across populations of records. If it is wrong, every aggregate built from it is wrong.
- **Risk types:** Credit, market, liquidity, counterparty credit, concentration
- **Criticality: 3.** *Without this element, no aggregate risk exposure figure X can be computed at all, because there is no monetary quantity to sum â the number being aggregated does not exist.*
- **Driven by:** Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (Â¶41) â *"capture and aggregate all material risk exposures, including those that are off-balance sheet"*; Principle 7 (Â¶53) â reports must be accurate and reconciled.
- **Search terms:** gross exposure, notional amount, outstanding balance, drawn balance, face value, position size, mark-to-market value, replacement cost, carrying amount
- **Data quality requirements:**
  - *Accuracy* â The gross exposure amount for a record agrees with the value held in the system of record (lending system, trading system, or GL) within defined tolerance | Count and aggregate value of records where the exposure amount diverges from the source system of record by more than the materiality threshold | Target: 0 records above materiality threshold with unexplained variance
  - *Completeness* â Off-balance-sheet exposures (commitments, guarantees, derivatives) are present in the risk data store, not only on-balance-sheet items | Proportion of off-balance-sheet notional in the risk data store versus the figure in the signed financial statements | Target: â¥99% coverage by notional
  - *Validity* â Exposure amounts are non-negative for positions that cannot have negative exposure (e.g., drawn loans) | Count of records with values failing business-rule sign checks | Target: 0

---

**CDE-04 â Reporting Currency / FX Rate**

- **Definition:** The currency of the transaction (transaction currency code) and the exchange rate applied to convert it to the group reporting currency for aggregation. Together these two attributes enable cross-currency summation of exposures.
- **Why critical:** Aggregation across business lines and geographies requires summing exposures denominated in multiple currencies into a single reporting currency. An incorrect or missing FX rate distorts every cross-currency aggregate. A missing currency code means the correct rate cannot be applied.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 2.** Exposure records exist and can be aggregated in local currency; the aggregate in reporting currency is distorted, not absent. This degrades accuracy of cross-currency slices rather than making them impossible.
- **Driven by:** Principle 4 (Â¶41âÂ¶42) â aggregation must span the banking group; the bank need not use a common metric but must be able to aggregate; Principle 3 (Â¶36) â accuracy requirement applies to the aggregated figure; Principle 6 (Â¶50) â country and industry credit exposures must be producible on demand, which requires consistent currency conversion.
- **Search terms:** transaction currency, currency code, ISO currency, FX rate, exchange rate, conversion rate, reporting currency, base currency, spot rate, rate date
- **Data quality requirements:**
  - *Validity* â Transaction currency codes conform to ISO 4217 | Count of records carrying currency codes not in the ISO 4217 reference list | Target: 0
  - *Timeliness* â FX rates applied in aggregation are sourced from the rate as of the position date, not a stale date | Count of aggregated positions where the rate date differs from the position date by more than the defined tolerance (e.g., 1 business day for standard reporting) | Target: 0 exceptions on report production date
  - *Consistency* â The same rate source is used across all systems contributing to a consolidated report | Count of positions where the FX rate applied differs from the enterprise-approved rate for the same currency pair and date | Target: 0

---

**CDE-05 â Risk Classification / Risk Type**

- **Definition:** The taxonomy code that classifies an exposure or position by risk type (credit risk, market risk, liquidity risk, operational risk, counterparty credit risk) and, where applicable, sub-type. This is the field that determines which risk bucket an exposure belongs to and therefore which aggregations it feeds.
- **Why critical:** Risk reports are structured by risk type. If an exposure is misclassified, it appears in the wrong report and is absent from the correct one. Principle 8 requires reports to cover *all* significant risk areas; a misclassification is an omission from one area and a double-count in another.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Aggregate figures for risk type X are produced but include or exclude positions they should not â the figure is wrong for a specific slice but the overall exposure total is not made impossible.
- **Driven by:** Principle 7 (Â¶57) â *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 2 (Â¶33) â *"integrated data taxonomies"*; Principle 9 (Â¶67) â *"A bank should develop an inventory and classification of risk data items."*
- **Search terms:** risk type, risk category, risk class, risk taxonomy, product type, risk classification, asset class, instrument type
- **Data quality requirements:**
  - *Validity* â Every risk record carries a risk classification code drawn from the approved enterprise taxonomy | Count of records with a null or unrecognised risk type code | Target: 0 in any report population
  - *Consistency* â The same instrument carries the same risk classification across all systems (e.g., a derivative does not appear as credit risk in one system and market risk in another) | Count of instrument records where risk type differs across contributing systems for the same position | Target: 0 unresolved conflicts
  - *Completeness* â Every material risk type identified in the bank's risk appetite statement has at least one record in the risk data store (absence itself is a data quality signal) | Documented coverage check: each risk type in the taxonomy maps to at least one active data source | Target: 100% coverage of approved taxonomy nodes

---

**CDE-06 â Business Line**

- **Definition:** The internal organisational dimension that identifies which business line or segment originated or owns an exposure â for example, retail banking, corporate banking, trading, treasury, private banking. This is an aggregation dimension, not a booking entity.
- **Why critical:** Principle 4 explicitly requires data to be *"available by business line"* for aggregation. Principle 8 requires reports to cover *all significant components* of risk areas. Without a consistent business line dimension, neither can be achieved â supervisory ad hoc queries by business line (Â¶50) cannot be answered.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Aggregate exposures can be totalled across the whole bank, but the business-line slice â which Principle 4 explicitly mandates â cannot be produced or cannot be trusted. Slicing degrades; total does not.
- **Driven by:** Principle 4 (Â¶41, heading) â *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines."*
- **Search terms:** business line, business unit, segment, product line, division, desk, front office unit, P&L centre
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null business line code | Count and proportion of records with null or unmapped business line | Target: <0.1% by count
  - *Validity* â Business line codes conform to the approved organisational taxonomy | Count of records carrying business line codes not present in the enterprise organisational hierarchy | Target: 0
  - *Consistency* â Business line attribution is consistent across risk and finance systems for the same portfolio | Count of positions where business line attribution differs between the risk data store and the management accounting system | Target: 0 unresolved differences above materiality threshold

---

**CDE-07 â Geography / Country**

- **Definition:** The country or jurisdiction code associated with an exposure â typically the country of the borrower's domicile or incorporation, the country of the collateral, or the country of the booking entity, depending on the risk measure. ISO 3166-1 alpha-2 or alpha-3 standard.
- **Why critical:** Principle 6, Â¶50 names *"country credit exposures as of a specified date based on a list of countries"* as a concrete example of what supervisors will test a bank's ability to produce. Geography is the explicit aggregation dimension for concentration risk and cross-border risk.
- **Risk types:** Credit, market, liquidity, concentration
- **Criticality: 2.** Country-level aggregates are the slice that degrades: total exposures are still computable, but the geographic slice â which is explicitly tested in Â¶50 â cannot be reliably produced.
- **Driven by:** Principle 4 (Â¶41 heading) â *"Data should be available by â¦ region and other groupings"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"* named as significant components.
- **Search terms:** country code, country of risk, domicile country, obligor country, country of incorporation, booking country, ISO country, geographic region, jurisdiction
- **Data quality requirements:**
  - *Validity* â Country codes conform to ISO 3166-1 | Count of records carrying country codes not in the ISO reference list | Target: 0
  - *Completeness* â Every credit exposure record carries a non-null country of risk | Count of credit exposure records with null or unknown country | Target: 0% above materiality threshold
  - *Consistency* â Country of risk is assigned using a documented and consistently applied methodology (e.g., ultimate parent domicile vs. immediate obligor domicile) and that methodology is applied uniformly | Count of records where different methodologies produce conflicting country assignments for the same obligor across systems | Target: 0 unresolved conflicts

---

**CDE-08 â Industry / Sector**

- **Definition:** The industry or sector classification of the counterparty or issuer â for example, a standard industrial classification code (SIC, NACE, GICS, or equivalent) assigned to the economic activity of the obligor.
- **Why critical:** Principle 8 names *"single name, country and industry sector for credit risk"* as required report components. Principle 6, Â¶50 requires the bank to produce industry credit exposures on demand. Sector concentration is a core dimension of credit risk reports reviewed by supervisors.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Industry-sector slices â required both by Principle 4 and by Principle 8 â cannot be reliably produced, but total exposure is unaffected. The sector report is the specific output that degrades.
- **Driven by:** Principle 4 (Â¶41 heading) â *"Data should be available by â¦ industry"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas."*
- **Search terms:** industry code, sector code, NACE, SIC, GICS, industry classification, obligor sector, counterparty industry, economic sector
- **Data quality requirements:**
  - *Completeness* â Every credit exposure record above materiality threshold carries a non-null industry/sector code | Count and proportion of credit exposure records with null sector | Target: 0% above materiality threshold
  - *Validity* â Sector codes belong to the approved classification scheme, with no free-text or local variants | Count of records using codes outside the approved reference list | Target: 0
  - *Accuracy* â Sector assignment reflects the primary economic activity of the obligor, verified against an external reference (e.g., LEI/GLEIF, commercial data provider) | Proportion of obligors in the top 10% of exposure concentration where sector assignment has been independently verified | Target: 100% of concentration-threshold obligors verified annually

---

**CDE-09 â Position / As-Of Date**

- **Definition:** The date as of which a risk position or exposure is stated â the snapshot date that defines the universe of records included in an aggregate. Sometimes called the value date, trade date, or reporting date depending on context; the key characteristic is that it is the date the position exists, not the date it was entered or processed.
- **Why critical:** Every aggregate risk figure is stated *as of* a specific date. Without a reliable position date on every record, it is impossible to construct a correct point-in-time snapshot: records from different dates are mixed into a single aggregate, producing a figure that is neither accurate nor reproducible. Principle 5's timeliness requirements and Principle 6's ad hoc capability (Â¶50: *"as of a specified date"*) are both structurally dependent on this element.
- **Risk types:** Cross-cutting
- **Criticality: 3.** *Without this element, the aggregate exposure figure X as of date D cannot be computed at all, because the record population for date D cannot be correctly identified â records from other dates are included or excluded arbitrarily, making the snapshot invalid.*
- **Driven by:** Principle 5 (Â¶44âÂ¶45) â timely aggregation requires knowing which records constitute a given day's position; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"* â the phrase "as of a specified date" appears twice in Â¶50 and is the operational test; Principle 7 (Â¶52âÂ¶53) â accuracy of reports depends on correct population definition.
- **Search terms:** position date, as-of date, value date, snapshot date, trade date, effective date, reference date, report date, business date
- **Data quality requirements:**
  - *Completeness* â Every position record carries a non-null position date | Count of records with null position date | Target: 0
  - *Validity* â Position dates are valid calendar dates and fall within the expected reporting window | Count of records with position dates outside the defined reporting period or that are not valid dates | Target: 0
  - *Timeliness* â Positions for date D are available in the risk data store within the defined SLA after close of business on date D | Proportion of records for date D loaded after the SLA cutoff | Target: per risk-type SLA defined under Principle 5; 0% late for critical risks under stress scenarios

---

**CDE-10 â General Ledger / System-of-Record Reconciliation Key**

- **Definition:** The identifier that links a risk data record to its corresponding record in the general ledger or primary system of record (e.g., the GL account number, the loan system deal identifier, or the trade reference number used by the booking system). This is the cross-walk between the risk data store and the authoritative source.
- **Why critical:** Principle 3, Â¶36(c) states risk data *"should be reconciled with bank's sources, including accounting data where appropriate."* Principle 7, Â¶53(a) requires *"defined requirements and processes to reconcile reports to risk data."* A risk figure that cannot be traced back to a GL or system-of-record entry cannot be verified as accurate or complete. An unreconciled figure is, for regulatory purposes, an unverified figure. The reconciliation key is the technical mechanism that makes reconciliation possible at all.
- **Risk types:** Cross-cutting (all risk types; this is a control element, not a risk-type-specific one)
- **Criticality: 3.** *Without this element, the aggregate risk figure X cannot be reconciled to the general ledger at all, because there is no link between risk records and GL entries â the accuracy and completeness of the figure required by Â¶36(c) cannot be evidenced, which under the regulation is equivalent to the figure being unverifiable.*
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** GL account number, deal reference, trade ID, loan ID, booking reference, source system key, primary key, system of record ID, accounting reference, transaction reference
- **Data quality requirements:**
  - *Completeness* â Every material risk record carries a non-null reconciliation key linking it to the GL or source system | Count and aggregate exposure value of risk records with null or missing reconciliation key | Target: 0 above materiality threshold
  - *Accuracy* â The reconciliation key in the risk data store resolves to exactly one record in the GL or system of record | Count of risk records whose reconciliation key returns no match or multiple matches in the source system | Target: 0 unresolved breaks above materiality threshold
  - *Consistency* â The exposure amount on the risk record agrees with the amount on the matched GL/source record within defined tolerance | Count and value of risk-to-GL breaks exceeding the materiality threshold | Target: 0 unexplained breaks; all breaks logged, assigned, and resolved within defined SLA

---

**CDE-11 â Source System / Provenance Flag**

- **Definition:** The identifier of the system that originated a risk data record â for example, the name and instance of the lending system, trading platform, or treasury system â together with a flag indicating whether the record was produced by an automated feed or entered manually (including end-user computing tools such as spreadsheets). These two attributes together constitute the provenance of the record.
- **Why critical:** Principle 3, Â¶36(b) requires *"effective mitigants in place (eg end-user computing policies)"* for manual processes, and Â¶39 requires banks to *"document and explain all of their risk data aggregation processes whether automated or manual."* Without a source system identifier and an automation flag, it is impossible to identify which records came from manual or EUC sources, to apply appropriate controls, or to report on the degree of reliance on manual processes to senior management (Â¶30).
- **Risk types:** Cross-cutting (governance and control element)
- **Criticality: 2.** Aggregate figures are produced, but the bank cannot demonstrate the control standard applied to each input, cannot identify manually sourced records for heightened scrutiny, and cannot evidence compliance with Â¶36(b) and Â¶39. The figure is produced but cannot be fully evidenced.
- **Driven by:** Principle 3 (Â¶36(b)) â *"Where a bank relies on manual processes and desktop applications â¦ it should have effective mitigants in place"*; Principle 3 (Â¶39) â *"document and explain all of their risk data aggregation processes whether automated or manual"*; Principle 1 (Â¶30) â senior management must understand limitations *"in technical terms (eg â¦ degree of reliance on manual processes)."*
- **Search terms:** source system, source application, system of origin, feed name, data source, automation flag, manual override flag, EUC flag, end-user computing, manual adjustment, spreadsheet input
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a non-null source system identifier | Count of records with null or generic/unknown source system | Target: 0 in any report population
  - *Validity* â Source system codes resolve to entries in the approved data source inventory | Count of records carrying source system codes not registered in the enterprise data source inventory | Target: 0
  - *Accuracy* â The manual/automated flag correctly reflects how the record was produced, verified by periodic reconciliation against IT system logs | Proportion of manual-flagged records confirmed as manually sourced by periodic IT audit; proportion of auto-flagged records that were in fact manually adjusted | Target: 100% of records above materiality correctly flagged; audit performed at least quarterly

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Enterprise Counterparty Resolution: Single View of Counterparty Across Systems**

- **Spans:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-05 (Risk Classification), CDE-08 (Industry/Sector)
- **Why cross-cutting:** This requirement cannot be expressed by monitoring any single CDE in isolation. The problem is that the *same real-world counterparty* may have different identifiers, different industry codes, and different names across the lending system, the trading system, and the treasury system. CDE-01 monitoring catches null or locally unresolved identifiers, but it does not catch the case where two systems each have a valid-looking local identifier that refers to the same legal entity under different codes. Only a cross-system matching and deduplication process can surface this. The aggregate credit exposure to a counterparty â the risk in Â¶46(a) â is understated or overstated unless this resolution is correct.
- **Regulatory basis:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties"*; Principle 5 (Â¶46(a)) â *"The aggregated credit exposure to a large corporate borrower"* as a critical stress risk.
- **Dimension:** Consistency, Uniqueness
- **Rule intent:** For any given real-world legal entity, there must be exactly one active master record in the enterprise counterparty master, and every contributing system must map its local identifier to that master record. The mapping must be current â it must be updated when counterparties merge, restructure, or change names.
- **Measurement:** (a) Count of counterparty master records that have no mapping from at least one contributing system that holds exposure against that counterparty; (b) Count of contributing-system local identifiers that match to zero or multiple master records; (c) For the top-N counterparties by gross exposure, proportion whose group-total exposure as computed from the risk data store agrees with the figure produced by a manual reconciliation exercise, within defined tolerance.
- **Suggested threshold:** 0 unmapped local identifiers above materiality threshold; 100% match on group-total exposure for top-50 counterparties by exposure in each quarterly validation.

---

**XDQ-02 â Risk-to-Finance Reconciliation: Completeness and Accuracy of the Risk Population Relative to the General Ledger**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-10 (GL/System-of-Record Reconciliation Key), CDE-02 (Legal Entity Identifier), CDE-09 (Position/As-Of Date)
- **Why cross-cutting:** Principle 3, Â¶36(c) requires risk data to be reconciled to accounting data. This cannot be done by monitoring any single data element: it requires comparing the population of records in the risk data store against the population in the general ledger, matching on multiple keys simultaneously (entity + instrument + date), and explaining every break. An unreconciled gap could mean (a) an exposure present in the GL is missing from the risk data store â a completeness failure â or (b) an exposure in the risk data store has no GL counterpart â a phantom. Either distorts the aggregate. No single-element DQ monitor detects this because it requires a join across systems.
- **Regulatory basis:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (Â¶36(a)) â controls must be *"as robust as those applicable to accounting data"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data."*
- **Dimension:** Completeness, Accuracy, Consistency
- **Rule intent:** For each legal entity and each reporting date, the sum of gross exposure amounts in the risk data store (for on-balance-sheet positions) must agree with the corresponding balance in the general ledger within the defined materiality threshold. Every break must be identified by booking entity, risk type, and business line, assigned an owner, and resolved within the defined SLA. Off-balance-sheet positions must be reconciled to the off-balance-sheet commitment register or equivalent source.
- **Measurement:** (a) Net aggregate break between risk data store total and GL total by legal entity and position date, expressed in reporting currency; (b) Count of risk records with no matching GL entry (orphan risk records) above materiality threshold; (c) Count of GL entries with no matching risk record (GL coverage gaps) above materiality threshold; (d) Proportion of breaks resolved within SLA.
- **Suggested threshold:** Net aggregate break â¤ defined materiality threshold (expressed as a percentage of total on-balance-sheet exposure, to be set by the bank's materiality policy); 0 unexplained breaks above materiality threshold outstanding beyond SLA; break register reviewed by risk and finance data owners at least monthly.

---

## 4. Out of Scope

The following principles establish obligations that CDEs and data quality monitoring cannot satisfy, however well the register is designed and maintained. Stating this explicitly is necessary to avoid overstating what a catalog delivers.

---

### Principles 8â11: Report content, clarity, frequency, and distribution

**Principle 8 â Comprehensiveness** requires that risk reports *"cover all material risk areas"* and include forward-looking assessments, stress test results, limit utilisation, and capital measures (Â¶57âÂ¶60). A data catalog can confirm that the data elements supporting these reports exist, are defined, and are of known quality. It cannot confirm that a report actually covers all material risk areas, that a limit framework is correctly reflected in a report, or that forward-looking scenarios have been incorporated. These are report-content and governance obligations exercised through report review, model validation, and board/senior management challenge â not through metadata management.

*Note on the split:* Principle 8 also names industry sector and country as required report dimensions (Â¶57), and this drives CDE-07 and CDE-08 above. The principle therefore appears in both this section and Section 2. The data element obligation (the dimension must exist and be governed) is within scope; the report-content obligation (the report must cover all material areas with appropriate depth) is not.

**Principle 9 â Clarity and usefulness** requires that reports be *"clear and concise,"* that they include the right balance of quantitative and qualitative information, and that recipients periodically confirm the information is relevant and appropriate (Â¶61âÂ¶69). A catalog can govern the data items that feed reports and can record what data is included in each report. It cannot assess whether the narrative is clear, whether the qualitative/quantitative balance is appropriate for a given recipient, or whether the board is asking the right questions. These are editorial, governance, and board-level obligations.

*Note:* Â¶67 requires banks to *"develop an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"* â this is the closest the regulation comes to mandating a data catalog explicitly, and it is fully within scope. The rest of Principle 9 is not.

**Principle 10 â Frequency** requires the board and senior management to set report frequency requirements and to test the bank's ability to produce accurate reports within those timeframes, including under stress (Â¶70âÂ¶71). CDE-09 (Position/As-Of Date) and CDE-11 (Source System) support the detection of timeliness failures in data feeds, and the DQ monitoring for those elements includes timeliness dimensions. However, the principle's core obligation â that a human governance body sets the frequency requirements, approves them, and periodically validates them through production tests â cannot be discharged by any monitoring rule. It requires documented SLAs approved by senior management, regular drill exercises, and evidence of board oversight.

**Principle 11 â Distribution** requires that risk reports be distributed to the right recipients with confidentiality maintained and that the bank confirms recipients receive timely reports (Â¶72âÂ¶74). This is an access control and distribution management obligation, not a data quality one. It is addressed through report distribution systems, entitlement management, and periodic confirmation processes â none of which are governed by a data catalog's CDE register.

---

### Principles 1 and 2 (partially): Governance framework, board oversight, and IT infrastructure

**Principle 1** (Â¶27âÂ¶31) establishes that the board and senior management are accountable for the risk data aggregation framework, must approve it, must understand its limitations, and must ensure adequate resources. A data catalog can provide evidence to support these obligations â documenting known gaps, lineage, and DQ metrics that senior management can review. It cannot discharge the governance obligation itself. Board approval, strategic IT planning (Â¶30), and the independent validation programme (Â¶29(a)) are institutional and process obligations.

**Principle 2** (Â¶32âÂ¶35) requires business continuity planning for risk data (Â¶32), single identifiers and integrated taxonomies (Â¶33 â within scope, drives CDEs), documented data ownership (Â¶34 â within scope, drives stewardship in the catalog), and strong aggregation capabilities (Â¶35). The capability obligations â that systems actually function under stress, that IT infrastructure is resilient, that data can be produced rapidly in a crisis â are engineering and operational obligations that no catalog governs. The catalog can document what systems exist and who owns what; it cannot substitute for a tested recovery capability.

---

### Principle 3 (partially): Automated vs. manual balance

**Principle 3, Â¶38âÂ¶39** requires an appropriate balance between automated and manual processes and documentation of all aggregation processes. CDE-11 (Source System / Provenance Flag) directly addresses the identification and flagging of manual inputs, and XDQ-02 addresses the reconciliation control. However, the remediation obligation in Â¶39 â *"proposed actions to reduce the impact"* of manual workarounds â is a programme management obligation, not a catalog function. The catalog can surface which sources are manual and how frequently they are used; the decision to remediate them, and the funding and prioritisation of that remediation, belongs to the IT strategy and governance process under Â¶30.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | 2 (Â¶33), 4 (Â¶41), 5 (Â¶46a) | Uniqueness, Completeness, Consistency |
| CDE-02 | Legal Entity / Booking Entity Identifier | 3 | 2 (Â¶33), 4 (Â¶41), 1 (Â¶30) | Validity, Completeness, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3 (Â¶36a, Â¶36c), 4 (Â¶41), 7 (Â¶53) | Accuracy, Completeness, Validity |
| CDE-04 | Reporting Currency / FX Rate | 2 | 4 (Â¶41âÂ¶42), 3 (Â¶36), 6 (Â¶50) | Validity, Timeliness, Consistency |
| CDE-05 | Risk Classification / Risk Type | 2 | 7 (Â¶57), 2 (Â¶33), 9 (Â¶67) | Validity, Consistency, Completeness |
| CDE-06 | Business Line | 2 | 4 (Â¶41 heading), 6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-07 | Geography / Country | 2 | 4 (Â¶41 heading), 6 (Â¶50), 8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-08 | Industry / Sector | 2 | 4 (Â¶41 heading), 8 (Â¶57), 6 (Â¶50) | Completeness, Validity, Accuracy |
| CDE-09 | Position / As-Of Date | 3 | 5 (Â¶44âÂ¶45), 6 (Â¶50), 7 (Â¶52âÂ¶53) | Completeness, Validity, Timeliness |
| CDE-10 | GL / System-of-Record Reconciliation Key | 3 | 3 (Â¶36a, Â¶36c), 7 (Â¶53a) | Completeness, Accuracy, Consistency |
| CDE-11 | Source System / Provenance Flag | 2 | 3 (Â¶36b, Â¶39), 1 (Â¶30) | Completeness, Validity, Accuracy |

**Cross-cutting requirements**

| ID | Name | Spans | Dimensions |
|---|---|---|---|
| XDQ-01 | Enterprise Counterparty Resolution | CDE-01, CDE-03, CDE-05, CDE-08 | Consistency, Uniqueness |
| XDQ-02 | Risk-to-Finance Reconciliation | CDE-03, CDE-10, CDE-02, CDE-09 | Completeness, Accuracy, Consistency |