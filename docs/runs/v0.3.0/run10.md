# BCBS 239 â Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a structural capability, not an ad hoc exercise.** The regulation requires that a bank can aggregate all material risk exposures across the group â by business line, legal entity, asset type, industry, and region â quickly, accurately, and completely, under both normal and stress conditions. *Â¶35: "banks should develop and maintain strong risk data aggregation capabilities to ensure that risk management reports reflect the risks in a reliable way."*

- **Data quality held to the same standard as accounting data.** Risk data controls must be as robust as those governing the general ledger, with reconciliation back to authoritative sources. *Â¶36(a)â(c): "Controls surrounding risk data should be as robust as those applicable to accounting dataâ¦ Risk data should be reconciled with bank's sources, including accounting data where appropriate."*

- **A single authoritative source per risk type, with documented lineage.** Manual processes and end-user computing must be identified, mitigated, and documented. The bank must strive toward one golden source per risk type. *Â¶36(d): "A bank should strive towards a single authoritative source for risk data per each type of risk."* And *Â¶39: "banks [should] document and explain all of their risk data aggregation processes whether automated or manual."*

- **Integrated data architecture with consistent definitions and identifiers.** The bank must establish integrated taxonomies, metadata, unified naming conventions, and single identifiers for legal entities, counterparties, customers, and accounts across the group. *Â¶33: "A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*

- **Completeness across the full perimeter, including off-balance-sheet.** No material exposure may be excluded from aggregation, and any gaps must be identified, explained, and reported to senior management and the board. *Â¶41: "A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*

- **Timely, adaptable supply of aggregated data for reporting and stress scenarios.** The architecture must support rapid production of aggregated risk data under stress, ad hoc supervisory queries, and scenario analysis, not only scheduled reporting. *Â¶48: "A bank's risk data aggregation capabilities should be flexible and adaptable to meet ad hoc data requests, as needed, and to assess emerging risks."*

**Who it applies to**

Principles 1â11 are addressed directly to **Global Systemically Important Banks (G-SIBs)** as of the January 2013 publication, with supervisors expected to apply equivalent standards to **Domestic Systemically Important Banks (D-SIBs)** and other significant institutions. The regulation governs the consolidated **banking group**, explicitly including subsidiaries, legal entities across jurisdictions, and off-balance-sheet exposures. Senior management, the board, business owners, IT functions, and risk managers all carry named responsibilities.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Unique Identifier**
- **Definition:** A persistent, system-independent identifier assigned to each legal counterparty (borrower, trading counterparty, guarantor) that resolves to the same entity record across all source systems in the banking group. Distinct from internal customer or account numbers, which may be system-local.
- **Why critical:** Without a single, resolvable counterparty identifier, exposures held in different systems â lending, derivatives, securities, trade finance â cannot be summed to produce a total group exposure to that counterparty. Every credit concentration report, large-exposure limit check, and counterparty credit risk aggregate depends on this join.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3.** Without this element, the aggregate total exposure to a single counterparty cannot be computed at all, because records in separate systems cannot be matched and summed â they remain isolated figures, not an aggregate.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶41) â completeness across all material exposures; Principle 5 (Â¶46(a),(b)) â *"aggregated credit exposure to a large corporate borrower"* and *"counterparty credit risk exposures"* named as critical risks.
- **Search terms:** counterparty ID, global counterparty identifier, GCID, legal entity identifier, LEI, party ID, obligor ID, client identifier, entity key, golden record
- **Data quality requirements:**
  - *Uniqueness* â Each real-world counterparty is represented by exactly one active identifier across all source systems | Count of counterparty identifiers that resolve to more than one master record in the group entity registry | Target: 0 duplicates for rated or reportable counterparties
  - *Completeness* â Every exposure record carries a populated, non-null counterparty identifier | Count of exposure records with null or unresolvable counterparty identifier, expressed as a percentage of total exposure records | Target: <0.1% by count, 0% by notional value above materiality threshold
  - *Validity* â Every counterparty identifier on an exposure record matches a live record in the authoritative counterparty master | Count of exposure records whose counterparty identifier returns no match in the master registry | Target: 0 unmatched records above materiality threshold
  - *Consistency* â The counterparty identifier used in risk systems matches the identifier used in the general ledger for the same counterparty | Count of counterparty records where the risk-system identifier and the GL identifier do not cross-reference to the same master entity | Target: 0 unlinked records for counterparties with exposures above reporting threshold

---

**CDE-02 â Legal Entity Identifier (Booking Entity)**
- **Definition:** The identifier of the bank's own legal entity in which a transaction is booked â not the counterparty's entity, but the bank's own subsidiary, branch, or holding company. Must correspond to the official legal entity structure of the banking group.
- **Why critical:** Group consolidation requires that every exposure be assigned to a booking entity so that subsidiary-level and group-level risk reports can be produced. Without this, exposures cannot be attributed to the correct perimeter for consolidated reporting or intragroup netting.
- **Risk types:** Credit, market, liquidity, cross-cutting
- **Criticality: 3.** Without this element, the consolidated group exposure figure cannot be computed at all, because the algorithm that rolls up subsidiary positions to group level has no way to assign or de-duplicate positions across legal entities.
- **Driven by:** Principle 2 (Â¶33) â *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (Â¶41â43) â aggregation across the banking group; Principle 1 (Â¶30) â senior management must understand *"coverage (egâ¦ subsidiaries not included)"*.
- **Search terms:** legal entity ID, booking entity, entity code, subsidiary code, LEI (own entity), legal entity hierarchy, group entity, consolidation entity, organisation unit
- **Data quality requirements:**
  - *Completeness* â Every risk exposure record carries a non-null booking entity identifier | Count of exposure records with null or invalid booking entity | Target: 0%
  - *Validity* â Every booking entity identifier maps to a live node in the official group legal entity hierarchy | Count of booking entity codes on exposure records that are absent from or retired in the legal entity master | Target: 0
  - *Consistency* â The booking entity on a risk exposure record matches the booking entity recorded on the corresponding general ledger entry for the same transaction | Count of transactions where risk-system booking entity differs from GL booking entity | Target: 0 above materiality threshold

---

**CDE-03 â Gross Exposure Amount**
- **Definition:** The pre-mitigation monetary value of a risk position, expressed in the transaction currency â the raw amount before netting, collateral, guarantees, or credit risk mitigation. For loans: outstanding principal. For derivatives: replacement cost or notional as applicable to the risk measure. For off-balance-sheet: the full drawn or contingent amount.
- **Why critical:** This is the primary quantity being aggregated. Every risk figure â total credit exposure, large-exposure limit utilisation, VaR input, liquidity gap â is built by summing, weighting, or transforming gross exposure amounts. It is the substance of what the regulation requires to be aggregated.
- **Risk types:** Credit, market, liquidity, counterparty, concentration
- **Criticality: 3.** Without this element, the aggregate exposure figure cannot be computed at all, because there is no monetary quantity to sum â the aggregation has no operand.
- **Driven by:** Principle 3 (Â¶36(a),(c)) â accuracy and reconciliation to accounting sources; Principle 4 (Â¶41) â *"capture and aggregate all material risk data"*, including off-balance sheet; Principle 5 (Â¶46(a)â(d)) â specific exposure types named as critical risks.
- **Search terms:** exposure amount, outstanding balance, notional amount, drawn amount, gross exposure, principal balance, mark-to-market, replacement cost, contingent amount, off-balance-sheet amount
- **Data quality requirements:**
  - *Accuracy* â The exposure amount on a risk record agrees with the corresponding balance on the general ledger or system of record within defined tolerance | Sum of absolute differences between risk exposure amounts and GL balances for matched transactions, as a percentage of total portfolio notional | Target: <0.5% of portfolio notional; any individual item above materiality threshold: 0 unexplained variances
  - *Completeness* â Every open position has a populated, non-zero exposure amount | Count of active exposure records with null or zero amount where a non-zero balance exists in the source system | Target: 0
  - *Timeliness* â Exposure amounts reflect the position as of the stated as-of date, not a prior day's snapshot carried forward | Count of exposure records whose amount timestamp lags the position date by more than the defined refresh tolerance | Target: 0 for critical risk types under stress reporting cadence
  - *Validity* â Exposure amounts are expressed in a recognised currency and are within plausible bounds for the instrument type | Count of records with non-standard currency codes or amounts outside instrument-type tolerance ranges | Target: 0 above materiality threshold

---

**CDE-04 â Position / As-Of Date**
- **Definition:** The date as of which a risk position or exposure amount is stated. Every aggregated risk figure must be stated as of a defined point in time; this element is the temporal anchor for the aggregate.
- **Why critical:** A risk aggregate is meaningless without a defined reference date. Mixing positions from different as-of dates in a single aggregate produces a figure that corresponds to no real snapshot of risk. Under stress reporting requirements, the as-of date also determines whether the bank can demonstrate it is meeting intraday or same-day reporting obligations.
- **Risk types:** Cross-cutting
- **Criticality: 3.** Without this element, the aggregate figure cannot be computed at all, because there is no defined point in time to which the aggregate corresponds â positions from different dates are not addable into a single coherent risk measure.
- **Driven by:** Principle 5 (Â¶44â46) â timeliness and ability to produce *"aggregate risk information on a timely basis"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (Â¶52) â accuracy of reports depends on temporal consistency.
- **Search terms:** as-of date, position date, value date, report date, snapshot date, effective date, reference date, trade date, settlement date
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null as-of date | Count of exposure records with null position date | Target: 0%
  - *Validity* â The as-of date is a valid calendar date, not a future date, and falls within the current or immediately prior reporting period | Count of records with as-of dates that are in the future or outside the current reporting window | Target: 0
  - *Timeliness* â Exposure records for a given as-of date are available in the aggregation layer within the defined SLA for that risk type | Elapsed time between position close-of-business and availability of complete data in the risk aggregation layer, measured per risk type | Target: within board- and management-approved SLA per Â¶44; reduced SLA under stress conditions per Â¶45
  - *Consistency* â All records contributing to a single aggregated risk report share the same as-of date, or any cross-date mixing is explicitly flagged and documented | Count of risk reports where contributing records span more than one as-of date without documented justification | Target: 0 undocumented cross-date aggregations

---

**CDE-05 â Risk Type Classification**
- **Definition:** The categorical label that assigns a risk record to a recognised risk type: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk, or concentration risk. May be a single field or a hierarchy (risk type / sub-type). Must be applied consistently across all source systems.
- **Why critical:** Risk type classification is the primary axis on which aggregated risk data is partitioned for reporting. It determines which records feed which risk report, which limit applies, and which capital charge is computed. A misclassified record inflates one risk category and deflates another; the aggregate for each type is wrong simultaneously.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Aggregation by risk type is technically possible with a misclassified record â the system will still sum â but the resulting figures for each risk category are wrong and cannot be reconciled to regulatory capital requirements. The aggregate is produced but cannot be trusted.
- **Driven by:** Principle 4 (Â¶41) â *"capture and aggregate all material risk data across the banking group"*; Principle 7 (Â¶57) â *"exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 2 (Â¶33) â *"integrated data taxonomies."*
- **Search terms:** risk type, risk category, risk class, risk classification, Basel risk type, risk taxonomy, risk flag, product risk type
- **Data quality requirements:**
  - *Validity* â Every exposure record carries a risk type classification drawn from the bank's approved taxonomy | Count of records with null, blank, or non-standard risk type codes | Target: 0%
  - *Consistency* â The risk type assigned in the risk system matches the classification applied in regulatory capital calculations for the same transaction | Count of transactions where risk-system risk type differs from the risk type used in the capital calculation engine | Target: 0 above materiality threshold
  - *Completeness* â The approved risk taxonomy covers all product types in the bank's portfolio; no product type maps to an unclassified or catch-all code | Count of active product types with no assigned risk type in the taxonomy | Target: 0

---

**CDE-06 â Business Line**
- **Definition:** The internal organisational unit or business segment to which a risk exposure is attributed for management and regulatory reporting purposes (e.g., Corporate Banking, Trading, Retail Mortgages, Transaction Banking). Must correspond to the bank's official management reporting hierarchy.
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. Without it, the bank cannot produce a business-line-level risk report, cannot identify concentrations within a line, and cannot demonstrate that risk data aggregation covers the full group perimeter broken down as supervisors require.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 2.** The group-level aggregate can still be computed without business line, but business-line slices â which the regulation explicitly mandates â cannot be produced. The figure is produced at group level but is not disaggregable as required.
- **Driven by:** Principle 4 (Â¶41) â data *"available by business lineâ¦ that permit identifying and reporting risk exposures, concentrations and emerging risks"*; Principle 6 (Â¶50) â *"across all business lines and geographic areas."*
- **Search terms:** business line, business unit, business segment, line of business, LOB, division, desk, product group, management reporting unit
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null business line code | Count and notional value of exposure records with null or missing business line | Target: 0% by notional value
  - *Validity* â Every business line code maps to an active node in the official management reporting hierarchy | Count of records with codes absent from or retired in the business line master | Target: 0
  - *Consistency* â Business line attribution in the risk system matches the attribution in management accounting for the same portfolio | Count of portfolios or desks where risk-system business line code differs from the management accounts code | Target: 0 unexplained differences

---

**CDE-07 â Geographic Region / Country**
- **Definition:** The country or geographic region to which a risk exposure is attributed â typically the country of the counterparty's domicile or the country of risk for sovereign and cross-border exposures. Must be expressed using a consistent standard (e.g., ISO 3166 country codes).
- **Why critical:** Principle 4 names region as a required aggregation dimension; Principle 6 explicitly requires the bank to be able to aggregate country credit exposures on demand. Country concentration risk is a named supervisory concern. Without a consistent geographic attribute, country-level aggregation produces incomplete or double-counted results.
- **Risk types:** Credit, concentration, market, liquidity
- **Criticality: 2.** The overall exposure aggregate is unaffected, but geographic slices â explicitly required by Â¶50 â cannot be produced reliably. The figure is produced in aggregate but cannot be cut by geography as mandated.
- **Driven by:** Principle 4 (Â¶41) â data available *"byâ¦ region"*; Principle 6 (Â¶50) â *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
- **Search terms:** country code, country of risk, counterparty country, domicile country, geographic region, region code, booking country, country of incorporation, ISO country
- **Data quality requirements:**
  - *Completeness* â Every credit exposure record carries a non-null country of risk attribute | Count and notional of exposure records with null or missing country code | Target: 0% by notional for rated or reportable exposures
  - *Validity* â Every country code conforms to ISO 3166-1 alpha-2 or the bank's approved country taxonomy | Count of records with non-standard or unrecognised country codes | Target: 0
  - *Consistency* â The country of risk used in the risk system matches the country classification applied in regulatory large-exposure reporting for the same counterparty | Count of counterparties where country code differs between systems | Target: 0 above materiality threshold

---

**CDE-08 â Industry / Sector Classification**
- **Definition:** The economic sector or industry to which a counterparty belongs, applied consistently to all credit and concentration risk exposures (e.g., NACE, GICS, or the bank's internal sector taxonomy). Must be assigned at the counterparty level, not the transaction level, and must be the same across all systems.
- **Why critical:** Principle 4 names industry as a required aggregation dimension; Principle 8 names industry sector as required content for credit risk reports; Principle 6 names industry-level aggregation as an explicit stress scenario capability. Without a consistent sector classification, industry concentration cannot be measured.
- **Risk types:** Credit, concentration
- **Criticality: 2.** The total credit aggregate is unaffected, but industry-concentration figures â explicitly required by Â¶57 and Â¶50 â cannot be produced. The figure is produced but cannot be sliced by sector as mandated.
- **Driven by:** Principle 4 (Â¶41) â data available *"byâ¦ industry"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk."*
- **Search terms:** industry code, sector code, NACE code, GICS, SIC, industry classification, counterparty sector, obligor industry, economic sector
- **Data quality requirements:**
  - *Completeness* â Every counterparty with a credit exposure above the materiality threshold carries a non-null industry classification | Count and notional of counterparties with null sector code | Target: 0% by notional for rated or reportable counterparties
  - *Validity* â Every sector code belongs to the bank's approved industry taxonomy | Count of records with codes not present in the approved taxonomy | Target: 0
  - *Consistency* â The same sector code is applied to the same counterparty across all risk, finance, and limit-management systems | Count of counterparties where sector code differs between systems | Target: 0 above materiality threshold

---

**CDE-09 â GL / Source System Reconciliation Key**
- **Definition:** The identifier that links a risk exposure record to its corresponding entry in the general ledger or authoritative system of record â enabling line-by-line reconciliation between the risk data layer and the accounting or operational source. May be a transaction reference number, account number, or a composite key, provided it is unique per transaction and consistent across systems.
- **Why critical:** Principle 3 explicitly requires reconciliation of risk data to accounting sources. Without a reconciliation key, the bank cannot demonstrate that its risk aggregates are complete and accurate relative to the books of record. Supervisory review of accuracy and completeness depends entirely on the ability to trace risk records to their source. This is one of the two elements most commonly absent from internal CDE registers.
- **Risk types:** Cross-cutting
- **Criticality: 2.** The risk aggregate can be produced without this key, but its accuracy and completeness cannot be evidenced. The figure is produced but cannot be reconciled or audited, which means the accuracy principle (Â¶36(a)â(c)) cannot be demonstrated as satisfied.
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (Â¶53(a)) â *"defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** transaction reference, deal ID, trade ID, GL account number, source transaction ID, reconciliation key, reference number, booking reference, contract number, instrument ID
- **Data quality requirements:**
  - *Uniqueness* â Each risk exposure record carries a reconciliation key that maps to exactly one GL or source-system entry | Count of risk records sharing the same reconciliation key where the source system has only one corresponding entry | Target: 0 duplicates
  - *Completeness* â Every risk exposure record above the materiality threshold carries a populated reconciliation key | Count and notional of records with null or blank reconciliation key | Target: 0% by notional above materiality threshold
  - *Accuracy* â The exposure amount on the risk record agrees with the corresponding balance on the matched GL or source-system entry within tolerance | Sum of unexplained monetary variances on matched pairs, as a percentage of total portfolio notional | Target: <0.5% of portfolio notional; 0 individual unexplained variances above materiality threshold
  - *Validity* â Every reconciliation key on a risk record resolves to an active record in the designated source system | Count of risk records whose reconciliation key returns no match in the source system | Target: 0 above materiality threshold

---

**CDE-10 â Source System / Provenance Flag**
- **Definition:** The attribute that identifies the originating system or process that produced a risk data record â distinguishing, at minimum, between automated feeds from authoritative source systems and manual or end-user-computing (EUC) inputs such as spreadsheets or manual database entries. May include the name of the source system, the feed identifier, and a flag indicating manual override or EUC origin.
- **Why critical:** Principle 3 requires documentation and mitigation of manual processes; Principle 2 requires a single authoritative source per risk type; Principle 1 requires governance of data quality risks. Without provenance information, the bank cannot identify which records carry elevated data quality risk, cannot enforce its EUC policy, and cannot demonstrate to supervisors the degree of automation in its aggregation process. This is the second of the two elements most commonly absent from CDE registers.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Aggregates can be produced whether or not provenance is tracked, but the bank cannot identify which portion of the aggregate is sourced from manually adjusted or EUC-origin records. The figure is produced but cannot be assessed for the accuracy risk introduced by manual processes, which means Â¶36(b), Â¶39, and the governance requirements of Principle 1 cannot be demonstrated.
- **Driven by:** Principle 3 (Â¶36(b),(d)) â *"Where a bank relies on manual processes and desktop applicationsâ¦ it should have effective mitigants in place"* and *"strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (Â¶39) â *"document and explain all of their risk data aggregation processes whether automated or manual."*
- **Search terms:** source system name, source system code, feed ID, data origin, EUC flag, manual entry flag, override flag, data source, lineage source, system of origin, provenance
- **Data quality requirements:**
  - *Completeness* â Every risk exposure record carries a non-null source system identifier and a populated manual/EUC flag | Count of exposure records with null source system or null EUC flag | Target: 0%
  - *Validity* â Every source system code maps to a registered system in the bank's data architecture inventory | Count of records with source system codes absent from the authorised system register | Target: 0
  - *Accuracy* â The proportion of risk data sourced from EUC or manual processes is measured and reported to senior management, and does not exceed the bank's approved threshold without documented escalation | Percentage of total exposure notional sourced from EUC or manual-flagged records, trended over time | Target: consistent with board/management-approved EUC tolerance; any increase above threshold triggers escalation per Â¶40
  - *Timeliness* â Provenance metadata is captured at the point of ingestion, not appended retrospectively | Count of records where source system or EUC flag was populated after the position date | Target: 0

---

**CDE-11 â Collateral / Credit Risk Mitigation Identifier**
- **Definition:** The identifier that links a risk exposure to any associated collateral agreement, guarantee, netting agreement, or other credit risk mitigation (CRM) instrument. Enables net exposure to be derived from gross exposure for counterparty and credit risk reporting, and supports concentration analysis on collateral type and issuer.
- **Why critical:** Net exposure figures â required for large-exposure reporting, regulatory capital calculation, and counterparty credit risk aggregation â cannot be computed without linking gross exposures to their associated mitigants. Missing or broken links between exposures and collateral records inflate net exposure figures and can cause regulatory breaches to go undetected.
- **Risk types:** Credit, counterparty, concentration
- **Criticality: 2.** Gross exposure figures are computable without this link, but net-of-collateral exposure aggregates â required for regulatory reporting and limit monitoring â are either overstated (if collateral is ignored) or uncomputable (if the link is broken). The net aggregate is produced but is systematically wrong.
- **Driven by:** Principle 4 (Â¶41) â *"all material risk exposures, including those that are off-balance sheet"* â collateral and netting agreements are material to net exposure; Principle 5 (Â¶46(b)) â *"counterparty credit risk exposures, includingâ¦ derivatives"* â net exposure for derivatives depends on netting and collateral agreements; Principle 8 (Â¶57) â *"risk-related measures (eg regulatory and economic capital)"* â capital calculations require net exposures.
- **Search terms:** collateral ID, collateral agreement ID, ISDA master agreement ID, CSA ID, netting set ID, guarantee ID, credit support annex, collateral type, CRM identifier, pledge ID, charge ID
- **Data quality requirements:**
  - *Completeness* â Every derivative or secured exposure above the materiality threshold has a populated link to its governing netting or collateral agreement | Count and notional of derivative/secured exposures with null collateral or netting agreement link | Target: 0% by notional above materiality threshold
  - *Validity* â Every collateral identifier on an exposure record maps to an active, unexpired collateral agreement in the collateral management system | Count of exposures whose collateral identifier returns no match or returns an expired agreement | Target: 0 above materiality threshold
  - *Accuracy* â The collateral value attributed to an exposure reflects the current mark-to-market of the collateral, not a stale valuation | Count of collateral records whose valuation date is older than the defined refresh tolerance relative to the position date | Target: 0 for critical counterparty types under stress reporting cadence
  - *Consistency* â The netting eligibility flag on an exposure record is consistent with the legal enforceability status of the governing agreement as recorded in the legal/documentation system | Count of exposures flagged as nettable whose governing agreement is not confirmed legally enforceable | Target: 0

---

## 3. Cross-cutting Data Quality Requirements

These requirements span multiple CDEs and cannot be expressed as a rule on any single element. They represent the most architecturally important quality obligations in BCBS 239 and are among the most common gaps in CDE registers.

---

**XDQ-01 â Counterparty Identity Resolution Across Source Systems**
- **Spans:** CDE-01 (Counterparty Unique Identifier), CDE-03 (Gross Exposure Amount), CDE-09 (Reconciliation Key), CDE-11 (Collateral Identifier)
- **What it is:** The end-to-end process of resolving that the same real-world counterparty is represented by the same identifier across all source systems â lending, derivatives, trade finance, securities, collateral management â such that a single sum of gross exposure to that counterparty is computable and can be reconciled to accounting records. This is not merely populating CDE-01; it is the matching and deduplication logic that makes CDE-01 valid across systems.
- **Why it cannot attach to a single CDE:** CDE-01 governs the identifier itself. This requirement governs the cross-system matching process that makes the identifier meaningful. A bank can have a formally populated counterparty identifier on every record in every system and still have unresolved duplicates if the matching logic is absent or inconsistent.
- **Driven by:** Â¶33 â *"use of single identifiers and/or unified naming conventionsâ¦ for counterparties"*; Â¶36(c) â reconciliation to sources; Â¶37 â *"a 'dictionary' of the concepts used, such that data is defined consistently across an organisation."*
- **Dimension:** Consistency
- **Rule intent:** Every occurrence of a given real-world counterparty across all source systems resolves to the same master counterparty record; no two master records represent the same legal entity.
- **Measurement:** Count of counterparty master records that are suspected duplicates (matched by name, LEI, or registration number but carrying distinct identifiers); count of source-system counterparty references that cannot be matched to any master record; total exposure notional attributable to unresolved or duplicate counterparty records.
- **Threshold:** 0 confirmed duplicates for counterparties with exposures above the reporting threshold; 0 unresolved source-system references above materiality threshold; full resolution required before any large-exposure or counterparty credit risk report is certified.

---

**XDQ-02 â Risk-to-Finance Reconciliation Completeness**
- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (Reconciliation Key), CDE-02 (Legal Entity Identifier), CDE-04 (Position / As-Of Date)
- **What it is:** The demonstrated agreement between the total of risk exposure records and the corresponding balances in the general ledger (or authoritative accounting system), performed at the legal-entity level and as of a defined position date. This is not a single-field check; it requires that CDE-03 values sum to a figure that can be traced to the GL via CDE-09, attributed to the correct entity via CDE-02, and stated as of the correct date via CDE-04. The four CDEs are jointly necessary; no single one is sufficient.
- **Why it cannot attach to a single CDE:** The reconciliation is a relationship between the risk data layer and the accounting layer, expressed across multiple elements simultaneously. CDE-09 provides the link; CDE-03 provides the amounts; CDE-02 and CDE-04 define the perimeter. A break in any of the four invalidates the reconciliation for the affected population.
- **Driven by:** Principle 3 (Â¶36(a),(c)) â *"Controls surrounding risk data should be as robust as those applicable to accounting dataâ¦ Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 7 (Â¶53(a)) â *"defined requirements and processes to reconcile reports to risk data."*
- **Dimension:** Accuracy, Completeness
- **Rule intent:** The aggregate of all risk exposure records for a given legal entity, risk type, and as-of date agrees with the corresponding aggregate in the general ledger within a defined monetary tolerance; any variance is identified, quantified, and explained before the risk report is certified.
- **Measurement:** (a) Sum of unexplained monetary variance between risk-layer aggregates and GL balances, expressed as a percentage of total portfolio notional, by legal entity and risk type; (b) count of risk exposure records with a populated reconciliation key (CDE-09) that cannot be matched to a GL entry; (c) count of GL entries within scope that have no corresponding risk exposure record.
- **Threshold:** Unexplained variance <0.5% of portfolio notional per legal entity per risk type per reporting period; 0 unmatched risk records or GL entries above materiality threshold; no risk report certified until reconciliation is completed and exceptions documented.

---

**XDQ-03 â EUC and Manual Process Population Monitoring**
- **Spans:** CDE-10 (Source System / Provenance Flag), CDE-03 (Gross Exposure Amount), CDE-09 (Reconciliation Key)
- **What it is:** Ongoing measurement of the proportion of the risk data population â by exposure notional, by risk type, and by legal entity â that originates from end-user computing tools or manual processes rather than authoritative automated feeds. This is the operational monitoring that gives CDE-10's provenance flag its governance meaning.
- **Why it cannot attach to a single CDE:** CDE-10 flags individual records. This requirement aggregates those flags across the portfolio to produce a bank-level view of EUC dependency, which is what senior management must understand under Â¶30 and Â¶39. A single-element DQ rule on CDE-10 tells you whether the flag is populated; this cross-cutting rule tells you what the populated flags mean collectively.
- **Driven by:** Principle 3 (Â¶36(b)) â *"Where a bank relies on manual processes and desktop applicationsâ¦ it should have effective mitigants in place"*; Principle 3 (Â¶39) â documentation of *"all of their risk data aggregation processes whether automated or manual"*; Principle 1 (Â¶30) â senior management must understand *"degree of reliance on manual processes."*
- **Dimension:** Accuracy, Completeness
- **Rule intent:** The bank can demonstrate at any point, by risk type and legal entity, what percentage of its aggregated risk data originates from EUC or manually adjusted sources; this percentage is within board/management-approved tolerances or escalation is active.
- **Measurement:** Percentage of total exposure notional (by risk type, legal entity, and as-of date) sourced from records carrying an EUC or manual flag in CDE-10; trend of this percentage over successive reporting periods; count of EUC-sourced records above the materiality threshold that lack documented compensating controls.
- **Threshold:** Within approved EUC tolerance per risk type (bank-specific); any increase above tolerance triggers documented escalation to senior management per Â¶40; 0 EUC-sourced records above materiality threshold without documented compensating controls.

---

## 4. Out of Scope

The following requirements are derived from Principles 1â11 but lie beyond what any CDE register or data quality monitoring framework can address. Stating this boundary explicitly is what makes the register above trustworthy.

---

**Principle 1 (Â¶27â31) â Board and senior management governance obligations**

The CDE register and DQ monitors give the board and senior management the information they need to discharge their governance obligations (awareness of aggregation limitations, approval of the framework, resource allocation). But the obligation itself â that the board reviews and approves the framework, that senior management identifies data-critical IT initiatives, that independent validation is conducted by staff with IT and data expertise â is a governance and organisational design matter. A catalog cannot install board ownership, commission independent validation, or ensure that IT strategy addresses aggregation shortfalls. These require policy documents, terms of reference, validation programmes, and board minutes.

*Note: Â¶30 does drive CDE-10 (provenance) and the EUC population monitoring in XDQ-03 above, because the limitation-awareness obligation presupposes that the bank can measure EUC dependency. Principle 1 therefore both drives a data element and contains obligations the element cannot itself satisfy.*

---

**Principle 2 (Â¶32â35) â Data architecture and IT infrastructure design**

The requirement to build an integrated data architecture â including business continuity planning, system integration, and role/responsibility structures â is an infrastructure and organisational design obligation. A data catalog documents the architecture and records ownership; it does not build the integrated taxonomy, implement the single counterparty identifier across systems, establish data ownership roles, or ensure business continuity coverage. CDE-01 and CDE-02 are driven by Â¶33's requirement for single identifiers, and CDE-10 by Â¶34's ownership and control obligations, but the infrastructure must exist before the catalog can govern it.

---

**Principle 7 (Â¶52â56) â Report reconciliation and validation processes**

Â¶53 requires defined reconciliation processes, automated and manual edit checks, and an inventory of validation rules. The CDE register and XDQ-02 address the data layer of reconciliation â the agreement between risk records and GL balances. But the report-layer obligations â the reconciliation between the aggregated figure in the risk report and the underlying data, the inventory of validation rules applied to published reports, the exception reporting and escalation process for report-level errors â are report production and governance obligations that require process design, report validation frameworks, and exception management workflows. A catalog cannot certify that a published risk report is reconciled to its underlying data; it can only certify that the underlying data is internally consistent.

*Note: Principle 7 also drives the reconciliation key (CDE-09) and XDQ-02. Its data-layer obligations are in scope; its report-production obligations are not.*

---

**Principle 8 (Â¶57â60) â Report comprehensiveness and content**

Â¶57 and Â¶59 specify what risk categories and measures must appear in risk management reports (capital adequacy, regulatory capital, stress testing results, inter- and intra-risk concentrations, etc.). These are report-content design obligations. The CDE register addresses the data elements that underpin the required dimensions (industry sector in CDE-08, business line in CDE-06, geographic region in CDE-07), but the obligation to produce reports that are comprehensive enough for effective governance â including forward-looking stress scenarios, capital ratio projections, and intra-risk concentration analysis â requires report design, scenario modelling, and capital planning processes. No data element or quality monitor produces a comprehensive risk report.

*Note: Â¶57 and Â¶50 do drive CDE-08 (industry classification), CDE-06 (business line), and CDE-07 (geographic region) as aggregation dimensions. Principle 8 therefore both drives data elements above and contains report-content obligations that remain out of scope. This dual appearance is intentional and is not a contradiction.*

---

**Principle 9 (Â¶61â69) â Clarity, usefulness, and recipient-tailoring of reports**

The obligation to tailor reports to recipients' needs, to balance quantitative data with qualitative interpretation, to confirm periodically with recipients that reports are appropriate, and to inventory risk data items in relation to report concepts (Â¶67) is a reporting and communication design obligation. Â¶67's inventory requirement is closely related to what a data catalog does, and the catalog's business glossary and data lineage capabilities are the most direct technical support for it. However, the confirmation process with report recipients, the qualitative interpretation layer, and the ongoing relevance assessment are human governance processes. A catalog cannot determine whether a board member found a report useful.

---

**Principle 10 (Â¶70â71) â Frequency of report production and distribution**

The obligation to set, periodically reassess, and routinely test frequency requirements for risk reports â including stress/crisis cadences â is a reporting governance and operational resilience matter. CDE-04 (position date) and its timeliness DQ rule support frequency compliance by ensuring data is available within SLA, but the SLA itself, the governance process for setting it, and the testing programme for stress-scenario production are outside the catalog's scope. These require documented frequency policies, SLA registers, and operational resilience testing programmes.

---

**Principle 11 (Â¶72â74) â Distribution and confidentiality**

The obligation to ensure that risk reports reach the right recipients rapidly while maintaining confidentiality is an access control, workflow, and information security obligation. A data catalog can record data sensitivity classifications and support access governance decisions, but it does not control report distribution systems, enforce need-to-know restrictions on report delivery, or test that the right people received the right reports. These require distribution workflow design, access control systems, and periodic recipient confirmation processes.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Unique Identifier | 3 | P2 (Â¶33), P4 (Â¶41), P5 (Â¶46a,b) | Uniqueness, Completeness, Validity, Consistency |
| CDE-02 | Legal Entity Identifier (Booking Entity) | 3 | P2 (Â¶33), P4 (Â¶41â43), P1 (Â¶30) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | P3 (Â¶36a,c), P4 (Â¶41), P5 (Â¶46aâd) | Accuracy, Completeness, Timeliness, Validity |
| CDE-04 | Position / As-Of Date | 3 | P5 (Â¶44â46), P6 (Â¶50), P7 (Â¶52) | Completeness, Validity, Timeliness, Consistency |
| CDE-05 | Risk Type Classification | 2 | P4 (Â¶41), P8 (Â¶57), P2 (Â¶33) | Validity, Consistency, Completeness |
| CDE-06 | Business Line | 2 | P4 (Â¶41), P6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-07 | Geographic Region / Country | 2 | P4 (Â¶41), P6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-08 | Industry / Sector Classification | 2 | P4 (Â¶41), P6 (Â¶50), P8 (Â¶57) | Completeness, Validity, Consistency |
| CDE-09 | GL / Source System Reconciliation Key | 2 | P3 (Â¶36c), P7 (Â¶53a) | Uniqueness, Completeness, Accuracy, Validity |
| CDE-10 | Source System / Provenance Flag | 2 | P3 (Â¶36b,d), P3 (Â¶39), P1 (Â¶30) | Completeness, Validity, Accuracy, Timeliness |
| CDE-11 | Collateral / CRM Identifier | 2 | P4 (Â¶41), P5 (Â¶46b), P8 (Â¶57) | Completeness, Validity, Accuracy, Consistency |

| XDQ | Name | Spans | DQ Dimension |
|---|---|---|---|
| XDQ-01 | Counterparty Identity Resolution Across Systems | CDE-01, CDE-03, CDE-09, CDE-11 | Consistency |
| XDQ-02 | Risk-to-Finance Reconciliation Completeness | CDE-02, CDE-03, CDE-04, CDE-09 | Accuracy, Completeness |
| XDQ-03 | EUC and Manual Process Population Monitoring | CDE-03, CDE-09, CDE-10 | Accuracy, Completeness |