# BCBS 239 â Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

### What the regulation is trying to achieve

- **Reliable risk aggregation as a structural capability, not a reporting exercise.** A bank must be able to aggregate all material risk data across the group â by legal entity, business line, asset type, industry, and region â and do so accurately, completely, and on demand, including under stress. This is a capability requirement, not merely a report-formatting requirement. (Â¶35: *"risk data aggregation capabilities should meet all Principles below simultaneously"*; Â¶41: *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*)

- **Data quality controls equivalent in rigour to accounting controls.** Risk data must be reconciled to source systems, including the general ledger where appropriate. The standard of control is explicitly compared to accounting: errors that would be material in a financial statement context are material here too. (Â¶36(a): *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Â¶56: *"Supervisors expect banks to consider accuracy requirements analogous to accounting materiality"*)

- **A single authoritative source per risk type, with documented lineage.** The bank must strive toward one authoritative source for each risk type, document all aggregation processes â automated and manual â and be able to explain any reliance on manual workarounds or end-user computing tools. (Â¶36(d): *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Â¶39: *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*)

- **Integrated data taxonomy and metadata, including unified identifiers.** The bank must establish integrated data taxonomies and architecture across the group, including metadata, and must use single identifiers and/or unified naming conventions for legal entities, counterparties, customers, and accounts. (Â¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*)

- **Adaptable, on-demand aggregation for ad hoc and stress scenarios.** Risk data infrastructure must support flexible, rapid re-aggregation across any requested dimension or scenario â country exposures as of a specified date, industry concentrations across all business lines â without bespoke manual extraction each time. (Â¶50: *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries, as well as industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*)

- **Board and senior management accountability for limitations.** Senior management must be aware of gaps in coverage, technical constraints, and legal impediments to data sharing, and must actively manage plans to remediate them. The board is responsible for understanding the limitations of the reports it receives. (Â¶30: *"Senior management should be fully aware of and understand the limitations that prevent full risk data aggregation, in terms of coverage â¦ technical terms â¦ or in legal terms"*)

### Who it applies to

BCBS 239 applies to **Global Systemically Important Banks (G-SIBs)** as a mandatory requirement (implementation required by January 2016 per the original timeline). National supervisors are encouraged to apply equivalent standards to other systemically important domestic institutions. The principles govern the **banking group as a whole**, including subsidiaries and cross-border entities â not merely the parent entity's data systems.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Identifier**

- **Definition:** The unique, persistent identifier assigned to a legal-entity counterparty â borrower, issuer, derivatives counterparty, or guarantor â that is consistent across all systems where that counterparty has an exposure. It is the key by which all exposures to a single counterparty are recognised as belonging to the same obligor, regardless of booking system, product type, or geographic booking location.
- **Why critical:** Without a common counterparty identifier, it is structurally impossible to aggregate total exposure to a single name. The concentration risk to a large corporate borrower â one of the named critical risks â cannot be computed. It is also the join key between credit risk systems, derivatives systems, and any collateral or netting set records.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3.** *Without this element, the aggregate single-name credit exposure figure cannot be computed at all, because there is no common key by which records across systems can be recognised as belonging to the same obligor.* Principle 5 names aggregated credit exposure to a large corporate borrower as a critical risk that must be producible rapidly (Â¶46(a)); Principle 4 requires aggregation across legal entities and business lines; neither is possible without a resolved, single identifier.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; reinforced by Principle 4 (Â¶41) and Principle 5 (Â¶46(a)â(b))
- **Search terms:** counterparty ID, obligor ID, party identifier, client ID, entity ID, LEI (Legal Entity Identifier), global counterparty code, GCID, BIC, customer master key
- **Data quality requirements:**
  - *Uniqueness* â Each counterparty maps to exactly one identifier across systems; no two distinct legal entities share an identifier | Count of identifier values that resolve to more than one distinct legal entity in the group's master reference data | Target: zero duplicate mappings
  - *Completeness* â Every exposure record carries a populated, non-null counterparty identifier | Count and percentage of exposure records with null or blank counterparty identifier field | Target: 0% null; materiality threshold aligned to concentration reporting threshold
  - *Consistency* â The same counterparty identifier appears in the credit risk system, the derivatives system, and the collateral system for the same obligor | Count of counterparty identifiers present in one system but absent or differently coded in another | Target: zero unresolved cross-system mismatches for material exposures
  - *Validity* â The identifier resolves to an active record in the counterparty master; no orphaned identifiers in exposure data | Count of exposure records whose counterparty identifier does not match any current record in the master reference file | Target: 0% orphaned identifiers at position-date close

---

**CDE-02 â Legal Entity Identifier (Own Entity / Booking Entity)**

- **Definition:** The identifier for the bank's own legal entity â subsidiary, branch, or group parent â in which a given exposure or position is booked. This is distinct from the counterparty's identifier; it is the bank's own side of the transaction, used to allocate exposures to the correct legal entity for solo and consolidated reporting.
- **Why critical:** Group consolidation requires summing exposures across all booking entities while eliminating intra-group positions. Solo reporting requires partitioning by booking entity. Neither is possible if the booking entity is misidentified or absent. It is also required to apply the correct regulatory capital and reporting rules for each jurisdiction.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting (all risk types aggregate across legal entities)
- **Criticality: 3.** *Without this element, the group-consolidated risk exposure figure cannot be computed at all, because there is no basis on which to include each exposure exactly once in the consolidation perimeter or to eliminate intra-group double-counting.* Principle 4 requires aggregation across legal entities explicitly (Â¶41; Â¶43).
- **Driven by:** Principle 2 (Â¶33) â *"integrated data taxonomies and architecture across the banking group â¦ including legal entities"*; Principle 4 (Â¶41) â *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"* across the group
- **Search terms:** legal entity identifier, LEI, booking entity, entity code, subsidiary code, branch code, solo entity, consolidation entity, RCON entity, MFI code
- **Data quality requirements:**
  - *Completeness* â Every exposure and position record carries a populated booking-entity identifier | Count and percentage of records with null booking entity | Target: 0% null
  - *Validity* â The booking entity identifier resolves to a legal entity within the current consolidation perimeter | Count of records bearing entity codes not in the active legal entity hierarchy | Target: zero for material exposures; any exceptions must be explained (Â¶43)
  - *Consistency* â The booking entity recorded in the risk system matches the entity recorded in the general ledger for the same transaction | Count of records where risk-system entity code differs from GL entity code for the same transaction reference | Target: 0% mismatch at reconciliation run

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary amount representing the bank's pre-mitigation risk exposure on a given instrument or position, expressed in the currency of the instrument. For credit, this is typically drawn balance plus contingent exposure; for derivatives, mark-to-market replacement cost or notional as applicable; for market risk, market value of the position. "Pre-mitigation" means before application of collateral, guarantees, or netting.
- **Why critical:** It is the quantity being aggregated. Every risk figure â single-name concentration, country exposure, portfolio loss estimate, capital requirement â is constructed by summing, weighting, or transforming this amount. An error here propagates directly and arithmetically into every downstream aggregate.
- **Risk types:** Credit, market, counterparty credit, concentration, liquidity
- **Criticality: 3.** *Without this element, the aggregate exposure figure cannot be computed at all, because it is the fundamental addend in every risk summation â there is no exposure aggregate without an exposure amount.* Principle 3 (Â¶36), Principle 4 (Â¶41), and Principle 7 (Â¶52) all presuppose that the underlying amounts being aggregated are accurate and complete.
- **Driven by:** Principle 3 (Â¶36(a)â(c)) â *"A bank should aggregate risk data in a way that is accurate and reliable â¦ Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 5 (Â¶46(a)) â *"aggregated credit exposure to a large corporate borrower"* as a named critical risk
- **Search terms:** exposure amount, drawn balance, outstanding balance, notional amount, market value, replacement cost, EAD (exposure at default), current exposure, gross notional, position value, book value
- **Data quality requirements:**
  - *Accuracy* â The exposure amount in the risk system agrees with the corresponding balance in the source transaction or accounting system within defined tolerance | Sum of absolute differences between risk-system exposure amounts and source-system balances for a matched population, expressed as a percentage of total portfolio exposure | Target: within accounting materiality threshold per Â¶56; zero unexplained variances above threshold
  - *Completeness* â No material exposure is absent from the aggregation | Count of transactions in the source system with no corresponding record in the risk aggregation dataset, by asset class and booking entity | Target: 0% omission for positions above materiality threshold; all off-balance-sheet exposures included per Â¶41
  - *Timeliness* â Exposure amounts reflect the position as of the stated position date; no stale valuations | Age of most recent valuation relative to position date, by instrument type | Target: within frequency SLA per risk type; intraday capability for trading exposures per Â¶71

---

**CDE-04 â Position / As-Of Date**

- **Definition:** The calendar date as of which an exposure amount, position, or aggregated risk figure is stated. It is the temporal key that defines the point in time to which every record in an aggregate belongs. Also referred to as the trade date, value date, or risk date depending on context â the relevant variant is whichever date governs inclusion in the regulatory or management report.
- **Why critical:** An aggregate is a sum *as of a specific date*. If records from different dates are mixed in a single aggregate without detection, or if a record is excluded because its date field is null or malformed, the aggregate is arithmetically wrong for the stated reporting date. Principle 6 explicitly requires the ability to produce aggregates *as of a specified date* on demand.
- **Risk types:** Cross-cutting â applies to all risk types
- **Criticality: 3.** *Without this element, the aggregate risk figure for a given reporting date cannot be computed at all, because there is no basis on which to select the correct population of records â the date filter that defines the snapshot cannot be applied.* Principle 6 (Â¶50) explicitly requires aggregation "as of a specified date."
- **Driven by:** Principle 5 (Â¶44) â *"risk data aggregation capabilities should ensure that it is able to produce aggregate risk information on a timely basis"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*
- **Search terms:** position date, as-of date, reporting date, value date, trade date, effective date, settlement date, risk date, snapshot date
- **Data quality requirements:**
  - *Completeness* â Every exposure and position record carries a populated, parseable as-of date | Count and percentage of records with null or unparseable date field | Target: 0% null or invalid
  - *Validity* â The as-of date is within the valid reporting calendar (not a future date, not more than one business day prior to the reporting run without documented explanation) | Count of records with as-of date outside the expected range for the reporting cycle | Target: zero unexplained out-of-range dates
  - *Timeliness* â Records for a given position date are available within the agreed SLA for that risk type | Elapsed time from position date close to availability of complete dataset in the aggregation layer, measured by risk type | Target: within SLA per Â¶45; stress reporting within shortened SLA per Â¶71

---

**CDE-05 â Risk Type Classification**

- **Definition:** The categorical label that assigns each exposure or position to a risk type â at minimum: credit risk, market risk, liquidity risk, counterparty credit risk, operational risk. May be hierarchical (e.g., credit risk â single-name credit â country credit â industry credit). This is the primary classification that determines which aggregation methodology, capital rule, and report destination applies to a record.
- **Why critical:** It drives which calculation is applied to the exposure amount and in which report the exposure appears. A position miscategorised between credit risk and market risk will appear in the wrong capital calculation, distort both risk figures, and potentially be invisible in one report entirely. Principle 8 requires reports to cover all significant risk areas; that partition is made on this element.
- **Risk types:** Cross-cutting â it *is* the risk type taxonomy
- **Criticality: 2.** The aggregate exposure figure is technically producible without this element (the amounts can still be summed), but the resulting aggregate cannot be partitioned by risk type. Supervisors and the board cannot assess risk by type; reconciliation to capital calculations is broken; and concentration reports cannot be produced by the required dimensions. The report is produced but cannot be trusted or used.
- **Driven by:** Principle 4 (Â¶41) â *"risk data aggregation capabilities should include all material risk exposures"*; Principle 7 (Â¶53(b)) â inventory of validation rules covering mathematical/logical relationships; Principle 8 (Â¶57) â *"exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*
- **Search terms:** risk type, risk category, risk class, risk taxonomy, product type, asset class, risk flag, exposure type, booking type
- **Data quality requirements:**
  - *Validity* â Every exposure record bears a risk type drawn from the agreed authoritative taxonomy; no free-text or legacy codes | Count of records with risk type values not in the approved taxonomy codelist | Target: 0% invalid codes; codelist maintained as reference data asset in catalog
  - *Completeness* â No record has a null or "unknown" risk type | Count and percentage of records with null or unclassified risk type | Target: 0%; any exception requires documented escalation per Â¶40
  - *Consistency* â The risk type assigned in the risk system is consistent with the product or instrument type in the source transaction system | Count of records where risk type classification conflicts with instrument-level product type mapping | Target: zero unexplained conflicts for material exposures

---

**CDE-06 â Business Line**

- **Definition:** The organisational unit or business division â retail banking, corporate banking, trading, private banking, treasury, etc. â to which an exposure or position is allocated for management reporting and risk aggregation. The granularity must be sufficient to support the bank's internal management structure and the aggregation dimensions supervisors require.
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. A risk report that cannot partition exposures by business line cannot satisfy the supervisory expectation that concentrations and emerging risks be identifiable at business-line level. It is also the dimension used for limit monitoring and P&L attribution.
- **Risk types:** Cross-cutting â all risk types aggregate across business lines
- **Criticality: 2.** Total exposure can be aggregated without this element, but the business-line slice required by Â¶41 and Â¶57 cannot be produced. The board and senior management cannot assess risk by line of business; the completeness principle is breached for this required dimension.
- **Driven by:** Principle 4 (Â¶41) â *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 8 (Â¶57) â reports should include exposure and position information for all significant components of risk areas
- **Search terms:** business line, business unit, division, segment, desk, LOB (line of business), profit centre, cost centre, front office code, organisational unit
- **Data quality requirements:**
  - *Completeness* â Every exposure record is assigned to a business line | Count and percentage of records with null or missing business line | Target: 0% null for material exposures
  - *Validity* â The business line code is drawn from the approved organisational hierarchy | Count of records with business line codes not present in the current org hierarchy reference data | Target: zero invalid codes; reference data version-controlled in catalog
  - *Consistency* â Business line assignment is consistent between the risk system and the management accounting / cost-centre system for the same position | Count of records with conflicting business line between risk and management accounting | Target: zero unexplained conflicts above materiality threshold

---

**CDE-07 â Geography / Country of Risk**

- **Definition:** The country or jurisdiction attributed to an exposure for risk aggregation purposes. This is the *country of risk* â typically the country of the counterparty's domicile or the country in which the underlying obligor's cash flows are generated â not necessarily the booking location or the currency country. Must support aggregation to regional groupings as well as country-level drill-down.
- **Why critical:** Principle 6 explicitly names country credit exposure aggregated as of a specified date as a paradigm case of required adaptable aggregation. Country concentration reporting, transfer risk monitoring, and sovereign exposure reporting all depend on this field. A bank that cannot produce a country credit exposure view on demand fails Principle 6 explicitly.
- **Risk types:** Credit, market, counterparty credit, concentration
- **Criticality: 2.** Total exposure is computable without this element, but the country and regional slices required by Principles 4, 6, and 8 cannot be produced. In a stress scenario requiring rapid aggregation of country exposures (e.g., a sovereign crisis), the bank cannot comply with Â¶50.
- **Driven by:** Principle 4 (Â¶41) â *"Data should be available by â¦ region"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*
- **Search terms:** country of risk, country code, domicile country, booking country, region, geographic area, ISO country code, country of incorporation, transfer risk country, obligor country
- **Data quality requirements:**
  - *Validity* â Country of risk is expressed as a valid ISO 3166-1 alpha-2 or alpha-3 code, or maps to one without ambiguity | Count of records with country codes not in the ISO 3166 reference list | Target: 0% invalid codes; ISO codelist maintained as reference data in catalog
  - *Completeness* â Every exposure record carries a populated country of risk | Count and percentage of records with null or "unknown" country of risk, by portfolio and materiality band | Target: 0% null for positions above materiality threshold
  - *Accuracy* â Country of risk reflects the economic risk jurisdiction, not merely the booking location, per the bank's documented country-of-risk assignment methodology | Count of records where country of risk equals booking country for counterparties known to be domiciled elsewhere | Target: zero for material cross-border exposures; exceptions require documented override

---

**CDE-08 â Industry / Sector Classification**

- **Definition:** The industry or economic sector to which a counterparty or obligor is classified â typically expressed using a standard taxonomy such as NACE, SIC, GICS, or an internal equivalent. Used to aggregate exposures by industry concentration and to identify emerging sector-specific risks.
- **Why critical:** Both Principle 4 and Principle 8 name industry sector explicitly as a required aggregation and reporting dimension. Principle 6's paradigm example of adaptable aggregation includes industry credit exposures across all business lines and geographies. Sector concentration is a named component of credit risk reporting.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Total credit exposure is computable without this element, but the industry-sector slice required by Principles 4, 6, and 8 cannot be produced. Concentration reporting by sector is broken; the bank cannot respond to a supervisory query for industry exposure on demand.
- **Driven by:** Principle 4 (Â¶41) â *"Data should be available by â¦ industry"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*
- **Search terms:** industry sector, SIC code, NACE code, GICS sector, sector classification, industry code, economic sector, counterparty sector, obligor industry
- **Data quality requirements:**
  - *Validity* â Industry classification is drawn from a single agreed taxonomy; no mixing of SIC, NACE, and GICS without a documented crosswalk | Count of records where the classification standard applied is inconsistent with the bank's approved taxonomy | Target: 0% cross-taxonomy contamination
  - *Completeness* â Every counterparty record and every exposure record carries a populated industry classification | Count and percentage of counterparty master records and exposure records with null or "unclassified" sector | Target: 0% null for material counterparties; residual "unclassified" bucket must be within materiality threshold per Â¶43
  - *Consistency* â The industry classification on the exposure record matches the classification on the counterparty master for the same obligor | Count of exposure records where industry code conflicts with the counterparty master's sector code | Target: zero conflicts; exposure inherits from counterparty master unless documented override

---

**CDE-09 â General Ledger / System-of-Record Reference Key**

- **Definition:** The identifier â transaction reference, GL account and cost-centre combination, or equivalent â that uniquely links a risk exposure record back to the corresponding entry in the bank's general ledger or authoritative source transaction system. This is the reconciliation anchor, not a duplicate of the exposure amount itself.
- **Why critical:** Principle 3 Â¶36(c) requires that risk data be reconciled with the bank's sources, including accounting data. Without a join key between the risk record and the GL record, reconciliation cannot be performed systematically â it can only be done at aggregate level, which cannot localise errors. Principle 7 Â¶53(a) requires defined processes to reconcile reports to risk data. Both requirements are structural: the key must exist before any reconciliation can occur.
- **Risk types:** Cross-cutting â reconciliation applies to all risk types
- **Criticality: 2.** The aggregate risk figure can be produced without this element, but it cannot be reconciled to the general ledger at transaction level. The accuracy and integrity of the figure cannot be evidenced, which means Principle 3 is substantively unmet even if the number looks right. Any audit or supervisory review of accuracy is reduced to aggregate comparison only.
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** GL reference, transaction ID, deal ID, trade reference, source system key, accounting reference, general ledger key, booking reference, contract ID, ISIN/CUSIP where applicable as instrument anchor
- **Data quality requirements:**
  - *Completeness* â Every risk exposure record carries a populated GL or source-system reference key | Count and percentage of exposure records with null or blank reconciliation key | Target: 0% null for on-balance-sheet positions; any exception documented with compensating control
  - *Validity* â The reconciliation key resolves to an active record in the general ledger or source transaction system | Count of risk records whose reference key has no matching entry in the GL | Target: zero unmatched keys for material exposures; unmatched keys escalated per Â¶40
  - *Uniqueness* â Each GL or source-system transaction maps to at most one risk exposure record (or to a defined, documented set where partial allocations are expected) | Count of GL reference keys that appear on more than the expected number of risk records | Target: zero unexpected duplicates; documented splits tracked as exceptions

---

**CDE-10 â Source System Identifier / Manual Override Flag**

- **Definition:** Two closely related but distinct attributes that together satisfy the lineage requirement: (a) the identifier of the source system from which a risk record originates (e.g., core banking system, derivatives platform, end-user computing spreadsheet), and (b) a flag or indicator recording whether the record â or any value within it â was manually entered, adjusted, or derived outside an automated feed. Together these constitute the provenance record for each exposure.
- **Why critical:** Â¶36(d) requires a single authoritative source per risk type; Â¶36(b) requires effective controls over end-user computing with consistently applied mitigants; Â¶39 requires documentation of all manual processes and their criticality to accuracy. A bank that cannot identify which records came from which system, and which were manually touched, cannot perform the documentation and control obligations the regulation names. It also cannot tell a supervisor where a data error originated.
- **Risk types:** Cross-cutting â applies to all risk types; particularly acute for market risk and operational risk where manual workarounds are most common
- **Criticality: 2.** Aggregated figures are technically producible without this element, but the bank cannot demonstrate that its single-authoritative-source discipline is maintained, cannot evidence that EUC controls are applied, and cannot trace errors to their origin. The figure may be right, but its provenance cannot be demonstrated â which is itself a Principle 3 breach.
- **Driven by:** Principle 3 (Â¶36(b)) â *"Where a bank relies on manual processes and desktop applications â¦ it should have effective mitigants in place â¦ consistently applied"*; Principle 3 (Â¶36(d)) â *"strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (Â¶39) â *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*
- **Search terms:** source system, system of origin, data source code, feed identifier, EUC flag, manual entry flag, manual override indicator, workaround flag, data lineage tag, upstream system name, transformation log flag
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a populated source system identifier | Count and percentage of records with null source system identifier | Target: 0% null; absence of source identifier is itself a lineage failure
  - *Validity* â The source system identifier refers to a registered, documented system in the bank's system inventory | Count of source system codes with no corresponding entry in the system inventory | Target: zero unregistered source codes; system inventory maintained as a catalog asset
  - *Accuracy* â The manual override flag is set if and only if a human intervention has occurred; neither false positives nor false negatives | Count of records flagged as manual that trace to fully automated feeds, and count of records arriving via known EUC paths that are not flagged | Target: zero systematic misfires; tested by periodic reconciliation of flag population against data lineage documentation per Â¶39
  - *Timeliness* â The source system and manual flag metadata is populated at the same time as the exposure record; not applied retrospectively | Count of records where source/flag metadata was applied more than one processing cycle after the exposure record was created | Target: zero retroactive metadata population for material records

---

**CDE-11 â Approved Risk Limit**

- **Definition:** The maximum exposure, VaR, concentration, or other risk metric that the board or senior management has formally approved for a given dimension â counterparty, country, business line, product type, or risk type. The limit is the authorised ceiling against which the exposure measure is compared to determine headroom, breach, or utilisation.
- **Why critical:** Principle 8 Â¶58 explicitly requires reports to *"provide information in the context of limits and risk appetite/tolerance."* A limit figure that is wrong, stale, or inconsistent with what the board has approved means that exposure-to-limit comparisons in every risk report are meaningless. The limit is not merely descriptive; it is the reference standard against which the risk measure is evaluated.
- **Risk types:** Credit, market, liquidity, concentration, counterparty credit
- **Criticality: 2.** The raw exposure aggregate can be computed without this element, but the report's representation of whether that exposure is within appetite is invalid. The board cannot assess limit utilisation; breach detection is disabled. The report is produced but cannot perform its governance function.
- **Driven by:** Principle 8 (Â¶58) â *"provide information in the context of limits and risk appetite/tolerance and propose recommendations for action where appropriate"*; Principle 5 (Â¶46(c)) â *"operating limits"* listed as critical risk data
- **Search terms:** risk limit, approved limit, exposure limit, concentration limit, VaR limit, position limit, counterparty limit, country limit, risk appetite threshold, limit table, board-approved limit
- **Data quality requirements:**
  - *Accuracy* â The limit value in the reporting system matches the most recently board- or committee-approved figure in the limit register | Count of limit records where the reported limit differs from the approved limit in the governance register | Target: zero unexplained discrepancies; limit changes reflected within one processing cycle of approval
  - *Timeliness* â Limit updates are applied to reporting systems within the agreed SLA after board or committee approval | Elapsed time between approval date and effective date in the reporting system | Target: within defined SLA; limit changes during stress must be flagged as per Â¶58
  - *Completeness* â Every exposure dimension required by risk policy carries an associated limit | Count of active exposure aggregation dimensions (counterparty, country, sector, desk) with no corresponding approved limit entry | Target: zero undefined limits for dimensions where policy requires one

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Counterparty Resolution and Deduplication Across Systems**

- **Spans:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-06 (Business Line), CDE-07 (Geography), CDE-08 (Industry / Sector)
- **What it is:** The requirement that a single real-world counterparty, wherever it appears across the bank's systems â credit origination, derivatives, securities, trade finance, collateral â is recognised as the same entity and carries the same identifier. This is a cross-system data integration requirement, not a field-level quality check. A bank can have zero null counterparty IDs in every individual system and still fail this requirement if "ACME Corp" in the credit system and "Acme Corporation" in the derivatives system are coded as two different counterparties.
- **Dimension:** Consistency (cross-system), Uniqueness (entity-level)
- **Rule intent:** Every distinct legal-entity counterparty is represented by exactly one identifier, and that identifier is used without exception in every system where that counterparty has an exposure. When a new counterparty identifier is introduced in any system, it must be matched against the master reference to confirm it does not duplicate an existing entity.
- **Measurement:** (a) Count of counterparty identifiers in each source system that cannot be matched to a record in the group counterparty master â the "unresolved population"; (b) Count of counterparty master records that are subsequently identified as referring to the same legal entity as another master record â the "duplicate population"; (c) Total exposure carried on unresolved or duplicate identifiers, expressed as a percentage of total group exposure. Both (a) and (b) must be tracked; (a) alone does not detect duplicates that have each been independently mastered.
- **Why it cannot be expressed per CDE:** Measuring completeness of the counterparty ID field in any single system (as in CDE-01) does not test whether the *same* identifier is used for the *same* counterparty across systems. The cross-system join must be evaluated as a separate process spanning the population of all source systems simultaneously.
- **Regulatory anchor:** Â¶33 â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Â¶36(d) â single authoritative source per risk type; Â¶46(a)â(b) â named critical risks dependent on single-name aggregation

---

**XDQ-02 â Risk-to-Finance Reconciliation Completeness**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-04 (Position / As-Of Date), CDE-09 (GL / System-of-Record Reference Key), CDE-10 (Source System Identifier / Manual Override Flag)
- **What it is:** The requirement that the aggregate exposure held in risk systems can be reconciled to the corresponding balances in the general ledger or authoritative accounting system, and that any differences are identified, explained, and escalated within a defined SLA. This is not a check on any single record's GL reference key (CDE-09), but a check on whether the *population* of risk records is complete and consistent with the accounting population â including the detection of records that exist in the GL but are absent from risk systems, and vice versa.
- **Dimension:** Accuracy (aggregate), Completeness (population), Consistency (cross-system)
- **Rule intent:** The total exposure in each material portfolio as measured in the risk aggregation system agrees with the corresponding balances in the general ledger within defined tolerance. Differences are categorised as: (a) timing differences with defined resolution dates; (b) scope differences (off-balance-sheet items legitimately absent from GL); (c) unexplained differences requiring escalation. The reconciliation must be run at a frequency consistent with the reporting SLA for each risk type, not just at month-end.
- **Measurement:** (a) Net difference between risk-system aggregate and GL aggregate, by portfolio segment and booking entity, as a percentage of total portfolio and in absolute currency terms; (b) Count and value of GL transactions with no matching risk record; (c) Count and value of risk records with no matching GL entry (excluding legitimately off-balance-sheet positions); (d) Age of oldest unresolved unexplained reconciling item, by materiality band.
- **Why it cannot be expressed per CDE:** CDE-09 tests whether each individual risk record carries a valid GL key. XDQ-02 tests whether the *set* of risk records, in aggregate, is complete relative to the set of GL records. A risk system could have 100% valid GL keys on every record it contains, but still be missing a material population of transactions entirely â an omission that only population-level reconciliation would detect. Â¶36(c) requires reconciliation with sources; Â¶43 requires measurement of completeness; both are population-level obligations.
- **Regulatory anchor:** Â¶36(a) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Â¶36(c) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Â¶53(a) â *"Defined requirements and processes to reconcile reports to risk data"*

---

**XDQ-03 â End-to-End Lineage Completeness for Aggregated Risk Figures**

- **Spans:** CDE-09 (GL Reference Key), CDE-10 (Source System Identifier / Manual Override Flag), and by extension CDE-03 (Gross Exposure Amount) and all aggregation-dimension CDEs (CDE-06, CDE-07, CDE-08)
- **What it is:** The requirement that for any aggregated risk figure appearing in a board or senior management report, the bank can trace the calculation path from that figure back to the individual source records, identify every transformation applied, and flag where manual intervention occurred. This is a lineage completeness check: not merely that source system and manual flags exist on individual records (addressed by CDE-10), but that the aggregation pathway itself â the sequence of systems, transformations, and manual adjustments between source data and reported figure â is documented and auditable end-to-end.
- **Dimension:** Accuracy (traceability), Completeness (lineage coverage), Consistency (transformation documentation)
- **Rule intent:** Every material aggregated figure in a risk report can be decomposed to its source records. The transformation logic at each step (netting, currency conversion, model application, manual adjustment) is documented. Where a manual adjustment has been applied at any stage in the aggregation chain, it is identified, the rationale is recorded, and it appears in the audit trail. No reported aggregate is a "black box."
- **Measurement:** (a) Percentage of material aggregated risk figures for which end-to-end lineage to source records is documented and traceable in the catalog or data lineage tool; (b) Count of aggregation steps â system-to-system handoffs â where the transformation logic is undocumented; (c) Count and value of manual adjustments in the aggregation chain with no recorded rationale or approver; (d) Count of aggregated figures where the reported value cannot be reproduced by re-running the documented logic against the source data.
- **Why it cannot be expressed per CDE:** CDE-10 addresses whether an individual record carries a source system tag and a manual flag. XDQ-03 addresses whether the *aggregation pathway* â potentially spanning five or six system handoffs between a trade booking system and a board report â is itself documented and auditable. A record can carry a perfect source system identifier and still be part of an aggregation chain where an intermediate transformation is undocumented. That gap is invisible at the record level.
- **Regulatory anchor:** Â¶36(b) â effective mitigants for manual processes *"consistently applied across the bank's processes"*; Â¶36(d) â *"strive towards a single authoritative source"* (violations appear in the lineage); Â¶39 â *"document and explain all of their risk data aggregation processes whether automated or manual â¦ including an explanation of the appropriateness of any manual workarounds"*

---

## 4. Out of Scope

The following principles â or material portions of them â impose obligations that a data catalog, a CDE register, and data quality monitoring cannot satisfy, regardless of how well those tools are implemented. Stating this plainly is necessary to prevent the catalog program from being oversold internally or to supervisors.

---

### Principle 1 â Governance (Â¶27â31)
**What cannot be delivered by a catalog:** The governance framework â board and senior management review and approval of the aggregation framework, service level agreements, data confidentiality and integrity policies, independent validation, business continuity planning for risk data, and the allocation of financial and human resources â is a *governance and organisational* requirement. A catalog can provide evidence inputs to governance (e.g., data ownership records, stewardship assignments, DQ monitoring dashboards), but it cannot constitute the governance framework itself. The independent validation required by Â¶29(a) must be performed by people with IT, data, and reporting expertise operating independently of the functions being validated â it cannot be automated or substituted by a monitoring tool. The board's awareness of limitations (Â¶30â31) requires human judgment and communication, not metadata.

**What the catalog does support:** Stewardship records (who owns each CDE), documentation of known data limitations and exceptions, and evidence of DQ rule execution â all of which feed the governance process as inputs. These are catalog contributions to Principle 1, not catalog delivery of Principle 1.

---

### Principle 2 â Data Architecture and IT Infrastructure (Â¶32â35)
**What cannot be delivered by a catalog:** The design and maintenance of the underlying IT architecture â integrated systems, automated data pipelines, business continuity capability for risk aggregation â is an *engineering and infrastructure* obligation. A catalog documents the architecture; it does not build or operate it. The requirement for a bank to be capable of producing aggregated risk data "during times of stress or crisis" (Principle 2 heading) depends on the resilience of production systems, not on catalog entries. Business impact analysis (Â¶32) is a governance and operational resilience process.

**What the catalog does support:** Principle 2 directly drives the CDE register (Â¶33 requires unified identifiers and metadata â the catalog *is* the metadata store for those identifiers), and data ownership assignment (Â¶34). These are substantive catalog deliverables, not mere documentation.

---

### Principle 7 â Accuracy of Risk Reports (Â¶52â56): *partial*
**What cannot be delivered by a catalog:** The requirements for automated and manual edit checks, reasonableness checks, and an inventory of validation rules applied to *reports* (Â¶53(b)) go beyond data catalog DQ monitoring. Validation of a final risk report â checking that a VaR figure is internally consistent with its component Greeks, or that a capital ratio has been calculated correctly â requires domain-specific model validation and report-level controls that operate downstream of data supply. The "integrated procedures for identifying, reporting and explaining data errors â¦ via exceptions reports" (Â¶53(c)) requires workflow and escalation tooling, not only monitoring.

**What the catalog does support:** CDE-level accuracy monitoring and the GL reconciliation requirement (CDE-09, XDQ-02) directly address the *data* accuracy obligations in Â¶36(c) and Â¶53(a). The DQ monitoring outputs documented here are necessary inputs to report accuracy, but they are not sufficient alone to demonstrate report-level accuracy compliance.

---

### Principle 8 â Comprehensiveness of Risk Reports (Â¶57â60): *partial*
**What cannot be delivered by a catalog:** The content obligations â that reports must cover all significant risk areas, include risk-related measures such as regulatory and economic capital, identify emerging concentrations, provide forward-looking forecasts and stress test results, and include the status of management actions â are *report design and risk management* requirements. No catalog governs what appears in a board risk report or whether it contains forward-looking scenario analysis. The requirement for reports to include "forecasts or scenarios for key market variables and the effects on the bank" (Â¶60) is a risk analytics and governance obligation entirely outside catalog scope.

**Note â apparent contradiction with CDE register:** Principle 8 also names business line, country, industry sector, and risk type as required report dimensions (Â¶57), which directly drive CDE-06, CDE-07, CDE-08, and CDE-05. This is not a contradiction: those data elements must exist and be governed in the catalog to *make possible* the report coverage Principle 8 requires. The catalog delivers the data substrate; it cannot deliver the report itself or guarantee that risk management chooses to produce the required report content. Both statements are true simultaneously: Principle 8 drives CDEs *and* its report-content obligations are out of catalog scope.

---

### Principle 9 â Clarity and Usefulness (Â¶61â69)
**What cannot be delivered by a catalog:** Clarity and usefulness are *communication design* properties of reports â the balance of quantitative versus qualitative information, interpretation, the tailoring of content to different audiences (board, senior management, risk committees), and the periodic confirmation that recipients find reports relevant and appropriate (Â¶69). These are governance and report design matters. A catalog cannot make a report clear, cannot ensure it contains meaningful analysis, and cannot confirm that the board is receiving the right qualitative interpretation alongside the data.

**Partial catalog contribution:** Â¶67 requires the bank to *"develop an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports."* This is, precisely, a data catalog function â a business glossary or concept inventory linked to CDEs. This specific sub-requirement is addressable by catalog tooling, but it is the sole catalog-relevant sub-requirement within Principle 9; the rest of the principle is out of scope.

---

### Principle 10 â Frequency (Â¶70â71)
**What cannot be delivered by a catalog:** The requirement to set, test, and meet frequency standards for risk report production â including the capability to produce reports within very short timeframes or intraday during stress (Â¶71) â is an *operational performance and scheduling* obligation. It depends on system throughput, data feed latency, and production scheduling, not on metadata governance. No catalog entry makes a risk system faster.

**Indirect catalog contribution:** Timeliness is listed as a DQ dimension for CDE-03 and CDE-04, and feed arrival time is a measurable attribute that could be monitored through catalog-integrated data observability tooling. This is a supporting contribution, not delivery of Principle 10 compliance.

---

### Principle 11 â Distribution (Â¶72â74)
**What cannot be delivered by a catalog:** The requirement that procedures are in place for rapid collection, analysis, and dissemination of risk reports to appropriate recipients, balanced against confidentiality requirements, is a *workflow, access control, and communications* obligation. Report distribution controls â who receives what, under what conditions, with what data classification handling â are managed through report distribution systems, entitlement frameworks, and information security policy, not through a data catalog.

**No catalog contribution:** Principle 11 does not drive any CDE and has no sub-requirement addressable through catalog metadata or DQ monitoring. It is entirely out of scope.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | P2 (Â¶33), P4 (Â¶41), P5 (Â¶46) | Uniqueness, Completeness, Consistency, Validity |
| CDE-02 | Legal Entity / Booking Entity | 3 | P2 (Â¶33), P4 (Â¶41) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | P3 (Â¶36), P4 (Â¶41), P5 (Â¶46), P7 (Â¶52) | Accuracy, Completeness, Timeliness |
| CDE-04 | Position / As-Of Date | 3 | P5 (Â¶44), P6 (Â¶50) | Completeness, Validity, Timeliness |
| CDE-05 | Risk Type Classification | 2 | P4 (Â¶41), P7 (Â¶53), P8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-06 | Business Line | 2 | P4 (Â¶41), P8 (Â¶57) | Completeness, Validity, Consistency |
| CDE-07 | Geography / Country of Risk | 2 | P4 (Â¶41), P6 (Â¶50), P8 (Â¶57) | Validity, Completeness, Accuracy |
| CDE-08 | Industry / Sector Classification | 2 | P4 (Â¶41), P6 (Â¶50), P8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-09 | GL / System-of-Record Reference Key | 2 | P3 (Â¶36(c)), P7 (Â¶53(a)) | Completeness, Validity, Uniqueness |
| CDE-10 | Source System ID / Manual Override Flag | 2 | P3 (Â¶36(b), Â¶36(d), Â¶39) | Completeness, Validity, Accuracy, Timeliness |
| CDE-11 | Approved Risk Limit | 2 | P5 (Â¶46(c)), P8 (Â¶58) | Accuracy, Timeliness, Completeness |
| XDQ-01 | Counterparty Resolution Across Systems | â | P2 (Â¶33), P3 (Â¶36(d)), P5 (Â¶46) | Consistency, Uniqueness |
| XDQ-02 | Risk-to-Finance Reconciliation Completeness | â | P3 (Â¶36(a)(c)), P7 (Â¶53(a)) | Accuracy, Completeness, Consistency |
| XDQ-03 | End-to-End Lineage Completeness | â | P3 (Â¶36(b)(d), Â¶39) | Accuracy, Completeness, Consistency |