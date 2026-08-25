# BCBS 239 — Data Catalog Governance Interpretation

---

## 1. Objectives and Scope

**What the regulation is trying to achieve:**

- **Accurate, complete, and timely risk aggregation across the entire banking group.** Banks must generate reliable risk data at the group level and by sub-dimension (business line, legal entity, geography, asset type, industry) under both normal and stress conditions. ¶43: *"Supervisors expect banks to produce aggregated risk data that is complete and to measure and monitor the completeness of their risk data."*

- **A single authoritative source per risk type, with reconciliation to accounting.** Risk data must be tied back to the general ledger so that accuracy can be evidenced, not merely asserted. ¶36(c)–(d): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate… A bank should strive towards a single authoritative source for risk data per each type of risk."*

- **Documented, validated, and largely automated data pipelines.** Manual processes and end-user computing must be identified, controlled, and minimised. ¶39: *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual."*

- **Integrated data taxonomy and common identifiers across the group.** Metadata, naming conventions, and unique identifiers for counterparties, legal entities, and accounts must be consistent enterprise-wide. ¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*

- **Adaptability to ad hoc and supervisory queries, including drill-down by scenario.** The underlying data must support slicing by country, industry, business line, and user-specified scenarios without bespoke rebuilds. ¶50: *"A bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries, as well as industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas."*

- **Board and senior management accountability for data quality and its limitations.** Governance requires that known gaps (coverage, model reliance, manual processes, legal impediments) are documented and escalated. ¶30: *"Senior management should be fully aware of and understand the limitations that prevent full risk data aggregation… in technical terms (eg model performance indicators or degree of reliance on manual processes)."*

**Who and what it applies to:**

Principles 1–11 apply to **Global Systemically Important Banks (G-SIBs)** as a binding requirement from January 2016, and to **Domestic Systemically Important Banks (D-SIBs)** by supervisory expectation. The unit of scope is the **consolidated banking group**, meaning subsidiaries, branches, and off-balance-sheet vehicles that carry material risk are included. The principles govern the data and processes that produce any **risk management report** used by board, senior management, or risk functions — not just regulatory returns.

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**
- **Definition:** A single, persistent, system-independent code that uniquely identifies a legal counterparty (borrower, issuer, derivative counterparty, depositor) across all systems within the banking group. Equivalent to a golden record key for counterparty identity.
- **Why critical:** Without a consistent counterparty key, exposures held in different booking systems, business lines, or legal entities cannot be summed. Aggregated credit exposure to a single large corporate — one of the named critical risks — is arithmetically impossible without it.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3.** *Without this element, the aggregate credit exposure to a single counterparty cannot be computed at all, because there is no joining key to sum positions held across systems, business lines, and legal entities into one total.*
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; also Principle 5 (¶46a–b) — aggregated credit exposure to a large corporate and counterparty credit risk are named critical risks.
- **Search terms:** counterparty ID, party ID, client ID, obligor ID, LEI (Legal Entity Identifier), BIC, CIF number, customer master key, golden source party
- **Data quality requirements:**
  - *Uniqueness* — Each real-world counterparty resolves to exactly one active identifier in the enterprise reference data system | Count of counterparty identifiers that map to more than one active master record; count of master records with no resolved identifier | Target: 0 duplicates; 0 unresolved
  - *Completeness* — Every exposure record carries a non-null, resolvable counterparty identifier | Count of exposure records where counterparty identifier is null or does not match the counterparty master | Target: 0 unmatched records for material exposures
  - *Consistency* — The same counterparty identifier is used in all risk systems (credit, market, liquidity) for the same legal entity | Count of counterparty identifiers that differ across systems for records that represent the same legal entity | Target: 0 cross-system mismatches for the same underlying party

---

**CDE-02 — Legal Entity Identifier (Booking Entity)**
- **Definition:** The code that identifies which legal entity within the banking group has booked a given exposure or position. Distinct from the counterparty identifier — this is the bank's own entity, not the client's.
- **Why critical:** Group consolidation and subsidiary-level reporting both require that every exposure record is attributed to a specific booking entity. Without this, neither group-wide aggregation nor legal-entity drill-down is possible.
- **Risk types:** Cross-cutting (credit, market, liquidity, concentration)
- **Criticality: 3.** *Without this element, the aggregate risk exposure of any individual legal entity within the group cannot be computed at all, because there is no way to assign records to a specific booking entity for consolidation or solo reporting.*
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (¶41) — *"all material risk exposures"* across the banking group; Principle 8 (¶57) — reports must cover all significant risk areas across the organisation.
- **Search terms:** legal entity code, LE code, entity ID, booking entity, subsidiary code, LEI (own entity), company code, organisational unit code
- **Data quality requirements:**
  - *Completeness* — Every exposure and position record carries a non-null, valid legal entity code | Count of records with null or invalid legal entity code | Target: 0 for all material risk asset classes
  - *Validity* — Every legal entity code in use corresponds to an active entry in the enterprise legal entity reference hierarchy | Count of legal entity codes in risk data not present in the current authoritative legal entity register | Target: 0 invalid codes
  - *Consistency* — The legal entity hierarchy used in risk systems matches the group consolidation hierarchy used in finance | Count of legal entity codes that appear in risk systems but are absent from or mapped differently in the finance consolidation structure | Target: 0 discrepancies

---

**CDE-03 — Gross Exposure Amount**
- **Definition:** The monetary amount representing the face value or mark-to-market value of a risk position before the application of credit risk mitigants, netting, or hedges. The primary quantity from which all risk aggregates are built.
- **Why critical:** This is the number being aggregated. Every risk figure — total credit exposure, concentration metrics, Value-at-Risk, liquidity outflows — is ultimately a function of individual exposure amounts. If the amount is wrong, every aggregate that includes the record is wrong.
- **Risk types:** Credit, market, liquidity, counterparty, concentration
- **Criticality: 3.** *Without this element, no aggregated risk exposure figure can be computed at all, because there is no monetary quantity to sum.*
- **Driven by:** Principle 3 (¶36a) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (¶41) — capture of all material risk exposures including off-balance-sheet; Principle 7 (¶52) — *"Risk management reports should be accurate and precise."*
- **Search terms:** notional amount, exposure at default (EAD), mark-to-market (MTM), fair value, outstanding balance, drawn amount, gross exposure, position size, face value, replacement cost
- **Data quality requirements:**
  - *Accuracy* — Exposure amounts in risk systems agree with corresponding balances in the general ledger or system of record within defined tolerance | Sum of absolute differences between risk system exposure amounts and GL balances for matched records, as a proportion of total portfolio; count of records outside tolerance | Target: reconciling items ≤ materiality threshold set by risk governance; 0 unexplained items above that threshold
  - *Completeness* — Off-balance-sheet exposures are present in the risk data, not only on-balance-sheet items | Count of off-balance-sheet commitments and contingent items in the GL that have no corresponding record in the risk data | Target: 0 missing material off-balance-sheet items (per ¶41)
  - *Timeliness* — Exposure amounts reflect positions as of the stated as-of date, not a prior date | Count of exposure records whose trade/value date is later than the stated position date | Target: 0 forward-dated records in any batch used for risk reporting

---

**CDE-04 — Risk Type Classification**
- **Definition:** The controlled vocabulary value that classifies each exposure or position into a risk category — at minimum: credit risk, market risk, liquidity risk, and operational risk. May extend to sub-types (e.g., counterparty credit risk, interest rate risk in the banking book).
- **Why critical:** This classification controls which calculation engine processes a record and which report section it populates. A misclassified record produces a wrong figure in one risk type and a gap in another simultaneously.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Classification determines which slice of an aggregate a record feeds. An incorrectly classified record does not prevent a total from being computed, but it corrupts the credit/market/liquidity split, making the per-risk-type figure unreliable. The aggregate is produced but cannot be trusted by risk type.
- **Driven by:** Principle 4 (¶41–42) — each system should make clear the specific approach used to aggregate exposures for any given risk measure; Principle 8 (¶57) — *"reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*
- **Search terms:** risk type code, risk category, risk class, asset class code, risk pillar, Basel risk category, risk classification
- **Data quality requirements:**
  - *Validity* — Every risk classification value belongs to the approved enterprise risk taxonomy | Count of exposure records carrying a risk type code not present in the approved taxonomy | Target: 0 invalid values
  - *Completeness* — Every exposure record carries a non-null risk classification | Count of records with null risk type code | Target: 0 unclassified records for material exposures
  - *Consistency* — The same instrument is classified to the same risk type across all systems that hold it | Count of instrument identifiers where risk type code differs across front-office, risk, and finance systems | Target: 0 cross-system classification conflicts for the same instrument

---

**CDE-05 — Business Line**
- **Definition:** The organisational dimension that assigns an exposure or position to a defined internal business line (e.g., Corporate Banking, Trading, Retail, Treasury). Part of the required aggregation hierarchy.
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. Supervisory scenario queries (¶50) require slicing by business line across geographies. Without a reliable business line attribute, the bank cannot demonstrate dimensional completeness.
- **Risk types:** Cross-cutting (credit, market, liquidity, concentration)
- **Criticality: 2.** Business line is a required slicing dimension. Its absence does not prevent a grand total from being computed, but the business-line breakdown — which Principle 4 requires — cannot be produced. The aggregate is produced; the required sub-aggregate is not.
- **Driven by:** Principle 4 (¶41) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — drill-down *"across all business lines and geographic areas."*
- **Search terms:** business line code, business unit, division code, LOB (line of business), desk code, product line, segment code
- **Data quality requirements:**
  - *Completeness* — Every exposure record carries a non-null business line code | Count of records with null or blank business line | Target: 0 for material risk populations
  - *Validity* — Business line codes match the current approved business line taxonomy | Count of records with a business line code not in the approved hierarchy | Target: 0 invalid codes
  - *Consistency* — Business line attribution is consistent between risk and finance systems for the same set of records | Count of records where business line code differs between the risk data mart and the finance general ledger sub-ledger | Target: 0 material discrepancies

---

**CDE-06 — Geography / Country of Risk**
- **Definition:** The country or geographic region to which a risk exposure is assigned for aggregation purposes — typically country of counterparty incorporation, country of collateral, or country of booking, applied consistently per risk type.
- **Why critical:** Principle 4 names region as a required aggregation dimension. The specific supervisory scenario in ¶50 — aggregating country credit exposures as of a specified date — is a direct test of whether this element is populated and reliable. Concentration reporting by geography depends entirely on it.
- **Risk types:** Credit, market, concentration, cross-cutting
- **Criticality: 2.** Geography is a required slicing dimension. Its absence does not invalidate the portfolio total, but the geographic breakdown required by Principles 4 and 6 cannot be produced, and the concentration identification required by Principle 8 (¶58) is impaired.
- **Driven by:** Principle 4 (¶41) — data available by *"region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
- **Search terms:** country code, country of risk, booking country, counterparty country, ISO country code, geographic region, domicile country, country of incorporation
- **Data quality requirements:**
  - *Completeness* — Every credit and market exposure record carries a non-null country of risk | Count of records with null or blank country code | Target: 0 for material asset classes
  - *Validity* — Country codes conform to an approved reference list (e.g., ISO 3166) | Count of records with country codes not in the approved reference set | Target: 0 invalid values
  - *Consistency* — Country of risk is assigned on a consistent basis (e.g., ultimate risk country vs. immediate counterparty country) within a given risk type, with the basis documented | Binary: is the assignment basis documented in the data catalog for each risk type? | Target: documented and applied consistently; 0 records that deviate from the stated basis

---

**CDE-07 — Industry / Sector Classification**
- **Definition:** The industry or economic sector code assigned to a counterparty or exposure (e.g., NACE, SIC, GICS, or internal sector code), used to aggregate credit and concentration exposures by sector.
- **Why critical:** Named directly as a required aggregation dimension in Principle 4 and as a required report content item in Principle 8. The ¶50 supervisory scenario explicitly requires producing *"industry credit exposures as of a specified date based on a list of industry types."* Sector concentration reporting is impossible without this element.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Industry sector is a required slicing dimension for concentration reporting. Its absence does not prevent a total exposure figure from being computed, but industry-sector concentration sub-aggregates — which both Principles 4 and 8 require — cannot be produced.
- **Driven by:** Principle 4 (¶41) — *"Data should be available by… industry"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*; Principle 6 (¶50) — industry credit exposures across all business lines.
- **Search terms:** industry code, sector code, NACE code, SIC code, GICS sector, industry classification, counterparty sector, economic sector
- **Data quality requirements:**
  - *Completeness* — Every corporate/wholesale counterparty record carries a non-null industry classification | Count of counterparty records with null industry code | Target: ≤ agreed threshold (e.g., 2%) for coverage, with exceptions logged
  - *Validity* — All industry codes belong to the approved classification scheme | Count of codes not present in the reference taxonomy | Target: 0 invalid values
  - *Accuracy* — Industry codes are reviewed periodically against counterparty public filings or reference data provider updates | Count of counterparty industry codes not reviewed within the defined review cycle | Target: 100% reviewed within cycle

---

**CDE-08 — Position / As-Of Date**
- **Definition:** The date as of which an exposure or position is stated — the temporal anchor for every aggregate. Distinct from trade date, settlement date, or report generation date.
- **Why critical:** Every risk aggregate is meaningful only when tied to a point in time. If the as-of date is missing or inconsistent across records in a batch, records from different dates are summed, producing a figure that is neither accurate nor interpretable. Stress and intraday reporting requirements (¶45, ¶71) make date precision especially material.
- **Risk types:** Cross-cutting
- **Criticality: 3.** *Without this element, the aggregate risk figure cannot be computed as of any defined date, because records from different time points would be mixed in the same sum, rendering the aggregate temporally undefined and therefore meaningless as a risk measurement.*
- **Driven by:** Principle 5 (¶44–45) — *"produce aggregate risk information on a timely basis"* and *"producing aggregated risk data rapidly during times of stress/crisis"*; Principle 6 (¶50) — supervisory queries are explicitly stated *"as of a specified date."*
- **Search terms:** as-of date, position date, reference date, valuation date, snapshot date, reporting date, batch date, business date
- **Data quality requirements:**
  - *Completeness* — Every exposure and position record carries a non-null as-of date | Count of records with null position date | Target: 0
  - *Validity* — As-of dates fall within the valid range for the reporting cycle (no future dates; no dates older than the lookback window for the relevant risk type) | Count of records with as-of dates outside the valid window | Target: 0 for any risk report batch
  - *Consistency* — All records within a single risk reporting batch share the same as-of date unless the batch explicitly covers a date range and this is declared | Count of distinct as-of dates within a batch that is supposed to represent a single point-in-time snapshot | Target: 1 distinct date per snapshot batch

---

**CDE-09 — General Ledger / Source System Reconciliation Key**
- **Definition:** The identifier — typically a transaction reference, account number, or trade ID — that uniquely links a risk record to its originating entry in the general ledger or the authoritative system of record. This is the key that makes ¶36(c) operationally testable.
- **Why critical:** Principle 3 requires that risk data be reconciled with accounting data. Without a reconciliation key, that requirement is stated as a policy aspiration but cannot be demonstrated to auditors or supervisors. It is the mechanism by which the accuracy assertion is evidenced, not merely claimed.
- **Risk types:** Cross-cutting (credit, market, liquidity)
- **Criticality: 2.** The absence of a reconciliation key does not make an individual aggregate figure arithmetically wrong, but it makes the accuracy of every aggregate unverifiable. The aggregate is produced; it cannot be reconciled to the general ledger, so the Principle 3 control fails entirely. This is the most commonly omitted CDE in practice.
- **Driven by:** Principle 3 (¶36c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53a) — *"Defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** trade ID, transaction reference, GL account reference, journal line reference, deal ID, position reference, source system key, origination system ID, booking reference, account number
- **Data quality requirements:**
  - *Completeness* — Every material risk record carries a non-null reconciliation key that points to an entry in the GL or system of record | Count of risk records with null or blank reconciliation key | Target: 0 for all asset classes in scope of GL reconciliation
  - *Accuracy* — For each risk record, the reconciliation key resolves to a matching GL entry, and the exposure amount on both sides agrees within tolerance | Count of risk records whose reconciliation key returns no matching GL entry; count of matched pairs where amounts differ beyond tolerance | Target: 0 unmatched keys for material populations; reconciling differences below materiality threshold and fully explained
  - *Uniqueness* — Each reconciliation key maps to exactly one risk record and one GL entry (no fan-out) | Count of reconciliation keys that appear on more than one risk record in the same snapshot | Target: 0 duplicate keys within a snapshot batch

---

**CDE-10 — Source System / Provenance Flag**
- **Definition:** An attribute on each risk record that identifies the originating system (e.g., front-office trading system, loan origination system, spreadsheet/EUC tool) and flags whether the record was produced by an automated feed or via a manual process or end-user computing application.
- **Why critical:** ¶36(b) and ¶39 require that manual processes and EUC inputs are identified, documented, and subject to mitigating controls. Without a provenance flag, there is no mechanism to identify which records carry elevated data quality risk from manual intervention, and no way to monitor whether manual reliance is increasing or decreasing over time.
- **Risk types:** Cross-cutting (operational, all risk types)
- **Criticality: 2.** Provenance does not affect whether an aggregate is arithmetically produced. Its absence means that manual/EUC-sourced records cannot be distinguished from automated-feed records, so the accuracy controls required by ¶36(b) and ¶39 cannot be applied differentially. The aggregate is produced; it cannot be trusted because the source quality tier is unknown.
- **Driven by:** Principle 3 (¶36b) — *"Where a bank relies on manual processes and desktop applications… it should have effective mitigants in place"*; Principle 3 (¶39) — *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual."*
- **Search terms:** source system code, originating system, data source flag, EUC flag, manual override indicator, feed type, automation flag, data origin, lineage source
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null source system identifier and a populated automation/manual flag | Count of records with null source system code or null manual/automated indicator | Target: 0
  - *Validity* — Source system codes resolve to entries in an approved source system register maintained in the data catalog | Count of source system codes not present in the approved register | Target: 0 unregistered sources
  - *Accuracy* — The proportion of risk records sourced from manual or EUC processes is monitored over time and compared against the baseline documented in the governance framework | Percentage of records per risk type flagged as manual/EUC origin; trend over rolling periods | Target: at or below the approved threshold per risk type; upward trends trigger escalation per ¶39

---

**CDE-11 — Net Exposure / Post-Mitigation Amount**
- **Definition:** The exposure amount remaining after recognised credit risk mitigants — collateral, guarantees, netting agreements — have been applied. The pre-mitigation amount (CDE-03) and post-mitigation amount together enable limit and concentration monitoring against net rather than gross risk.
- **Why critical:** Principle 8 (¶58) requires reports to provide information in the context of risk appetite and limits. Limit utilisation — a central board-level metric — is typically calculated on a net basis. If only the gross amount is governed, limit reporting is built on an unvalidated derived figure, and the board cannot reliably assess whether the bank is within appetite.
- **Risk types:** Credit, counterparty, concentration
- **Criticality: 2.** The gross aggregate (CDE-03) can be produced without this element. However, any risk report that presents net exposure or limit utilisation in the context of risk appetite — which Principle 8 requires — will be unreliable if this element is not governed. The figure is produced; it cannot be compared to limits or appetite.
- **Driven by:** Principle 8 (¶57–58) — *"Risk management reports should also cover risk-related measures"* and provide information *"in the context of limits and risk appetite/tolerance"*; Principle 5 (¶46c) — trading exposures and *"operating limits"* are named critical risk data.
- **Search terms:** net exposure, post-mitigation exposure, adjusted EAD, net credit exposure, collateral-adjusted exposure, netting benefit, net replacement cost, eligible collateral value
- **Data quality requirements:**
  - *Accuracy* — Net exposure is derived correctly from gross exposure and applied mitigant values, and the derivation is reproducible from the stored components | Count of records where gross minus recognised mitigants does not equal the stored net exposure amount | Target: 0 arithmetic inconsistencies
  - *Completeness* — Every record for which a recognised netting agreement or collateral arrangement exists carries a non-null net exposure value | Count of counterparty relationships with a documented netting or collateral agreement where net exposure is null | Target: 0 missing net exposures for recognised arrangements
  - *Validity* — Mitigant values used in deriving net exposure are sourced from the approved collateral/guarantee system and are dated as of the same position date as the exposure | Count of records where the mitigant value date differs from the position date (CDE-08) | Target: 0 date mismatches for regulatory and board reporting runs

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Counterparty Identity Resolution Across Systems**

*Spans: CDE-01 (Counterparty Identifier), CDE-04 (Risk Type Classification), CDE-05 (Business Line), CDE-06 (Geography), CDE-07 (Industry Sector)*

No single CDE monitor can detect the failure mode where two systems hold the same real-world counterparty under different identifiers — a scenario that causes double-counting or undercounting in every cross-system aggregate simultaneously. This is not a completeness problem in any one system; it is a cross-system consistency problem that can only be detected by comparing CDE-01 values across sources.

- **Dimension:** Consistency
- **Rule intent:** For any counterparty that is known to exist in more than one risk system, all systems must carry the same enterprise counterparty identifier. Where local system keys differ from the enterprise key, a mapping table must exist, be current, and be used in every aggregation pipeline.
- **Measurement:** Count of counterparty names or external identifiers (e.g., LEI, Bloomberg ID) that resolve to more than one distinct enterprise counterparty identifier across systems. Count of risk aggregation runs that consumed a local system key without passing through the enterprise mapping layer.
- **Suggested threshold:** 0 unresolved duplicate identities for counterparties above a materiality exposure threshold; mapping table coverage 100% for counterparties in the large-exposure monitoring population. Failures trigger a stop on the affected aggregation batch, not a warning.
- **Regulatory basis:** ¶33 — *"use of single identifiers and/or unified naming conventions for data including… counterparties"*; ¶36(c) — reconciliation to sources; ¶46(a–b) — aggregated credit exposure to large corporates and CCR named as critical risks.

---

**XDQ-02 — Risk-to-Finance Reconciliation Completeness**

*Spans: CDE-03 (Gross Exposure Amount), CDE-09 (Reconciliation Key), CDE-08 (Position / As-Of Date)*

Principle 3 requires reconciliation between risk data and accounting data. This cannot be monitored by checking any individual CDE in isolation: the reconciliation is a relationship between two populations — the risk data set and the GL — and the control is only meaningful when the two are compared in totality. A 100%-populated reconciliation key (CDE-09) on every risk record is a necessary but not sufficient condition; the reconciliation itself must be run, its results measured, and breaks investigated.

- **Dimension:** Accuracy, Completeness
- **Rule intent:** The total gross exposure in the risk data for each material asset class must be reconcilable to the corresponding balance in the general ledger as of the same position date. Every reconciling item above the materiality threshold must be assigned an owner, an explanation, and a resolution date.
- **Measurement:**
  - *Population completeness:* Count and value of GL balances for in-scope asset classes that have no corresponding risk record (omission).
  - *Amount accuracy:* Sum of absolute differences between matched risk and GL balances as a percentage of total GL balance for the asset class; count of matched pairs with difference exceeding the materiality threshold.
  - *Ageing:* Count of open reconciling items by age band (1–3 days, 4–7 days, >7 days); any item aged >7 days triggers escalation.
- **Suggested threshold:** Population completeness gap: 0 missing records above a minimum transaction size. Amount accuracy: reconciling differences ≤ 0.1% of total portfolio exposure (or board-approved materiality threshold). Aged breaks >3 business days: escalation to risk data governance committee.
- **Regulatory basis:** ¶36(a) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; ¶36(c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; ¶53(a) — *"Defined requirements and processes to reconcile reports to risk data."*

---

**XDQ-03 — Manual and EUC Dependency Tracking**

*Spans: CDE-10 (Source System / Provenance Flag), CDE-03 (Gross Exposure Amount), CDE-09 (Reconciliation Key)*

Identifying a single record as manually sourced (CDE-10) is necessary but not sufficient. The regulation requires that the bank understand the aggregate impact of manual processes on the reliability of its risk figures, document mitigants, and demonstrate that manual reliance is not growing. This requires a cross-cutting view that no individual element monitor can provide.

- **Dimension:** Accuracy, Completeness
- **Rule intent:** The proportion of total exposure value and record count that flows through manual or EUC processes must be measured and reported at the risk type and business line level. For any material risk type, if manual-sourced records account for more than an approved percentage of total exposure value, the mitigating controls must be documented in the data catalog against CDE-10, and an action plan to reduce the percentage must exist and be tracked.
- **Measurement:**
  - *Volume:* Percentage of exposure records per risk type flagged as manual/EUC origin (by count and by notional value).
  - *Coverage:* For all records flagged as manual/EUC, percentage that have a documented mitigant control recorded in the data catalog entry for CDE-10.
  - *Trend:* Month-on-month change in the percentage of manual/EUC records per risk type. An upward trend over two consecutive periods triggers an escalation flag.
- **Suggested threshold:** Manual/EUC exposure value ≤ the approved threshold per risk type (set by governance). Undocumented manual records: 0. Consecutive upward trends: automatic escalation to data steward and risk data governance committee.
- **Regulatory basis:** ¶36(b) — *"effective mitigants in place (eg end-user computing policies and procedures)"*; ¶39 — *"document and explain all of their risk data aggregation processes whether automated or manual… including an explanation of the appropriateness of any manual workarounds… and proposed actions to reduce the impact."*

---

## 4. Out of Scope

The following matters are directly required by Principles 1–11 but cannot be addressed by CDE registration, metadata management, or data quality monitoring. Stating these limits explicitly is part of responsible governance advice.

---

**Principle 1 — Board and senior management accountability for governance framework**

Paragraphs 27–31 require the board to approve the risk data aggregation framework, understand its limitations, ensure adequate resourcing, and include data quality in the overall risk management framework. A data catalog can provide evidence that governance artefacts exist (stewards assigned, policies linked), but it cannot *create* board accountability, *enforce* adequate resourcing, or *replace* the independent validation process described in ¶29(a). The governance framework must be designed, owned, and operated by risk management and internal audit. The catalog is a record-keeping tool for that framework, not a substitute for it.

**Principle 2 — IT architecture, business continuity planning, and data architecture design**

The data architecture and IT infrastructure requirements of ¶32–35 go well beyond what a catalog governs. Business continuity planning (¶32), the design of integrated data taxonomies (¶33), the assignment of data ownership roles (¶34), and the build-out of aggregation capabilities (¶35) all require IT investment decisions, infrastructure design, and organisational change. A catalog can document the taxonomy and record ownership assignments, but it cannot design or build the underlying architecture, remediate system fragmentation, or establish business continuity controls.

**Principle 5 — Timeliness of data production under stress**

The timeliness requirements of ¶44–47 concern how quickly risk systems can *produce* aggregated data — including intraday capability for critical risks. A data catalog can record timeliness SLAs as metadata against source systems (and CDE-08 monitoring can detect stale records), but meeting the production timeliness requirement depends on system performance, batch scheduling infrastructure, and data pipeline engineering. No catalog configuration accelerates a slow batch process or enables intraday aggregation where the architecture does not support it.

**Principle 6 — Adaptability and ad hoc query capability**

¶48–50 require that banks can execute novel aggregation queries — by any combination of country, industry, business line, and scenario — without bespoke development. This is a capability requirement on the underlying data architecture and query infrastructure, not on the catalog. The catalog can document which dimensions are available and support discoverability of datasets, but whether those datasets can actually be sliced dynamically depends on the technology stack holding the data.

**Principles 7 and 8 — Report content, validation rules, and accuracy of approximations (partial)**

Principle 7 (¶52–56) and Principle 8 (¶57–60) partly *drive CDEs* — Principle 7 drives the reconciliation key (CDE-09) and the net exposure amount (CDE-11); Principle 8 drives industry sector (CDE-07) and business line (CDE-05) as required report dimensions. These elements appear in the CDE register above, and the catalog can govern them.

However, the same principles also impose requirements that the catalog cannot meet:

- ¶53(b) requires an inventory of validation rules applied to quantitative information, including mathematical and logical relationships. The catalog can document that such an inventory exists and link to it, but the validation rules themselves must live in, and be enforced by, the risk reporting system or a dedicated data quality tool — not the catalog.
- ¶54–56 require that banks establish accuracy and precision requirements for approximations (models, stress tests, scenario analyses) analogous to accounting materiality. Calibrating model accuracy and setting materiality thresholds for approximations are model governance and actuarial/quant matters, outside catalog scope.
- ¶58–60 require forward-looking forecasts, stress test results, and inter/intra-risk concentration analysis in board reports. The content and analytical depth of risk reports are report design decisions, not data catalog governance decisions.

**Principle 9 — Report clarity, usefulness, and recipient-tailored communication**

¶61–69 address how reports are written, how information is balanced between quantitative and qualitative, and how boards confirm that reports meet their needs. Paragraph 67 — *"A bank should develop an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"* — is close to catalog scope and the data dictionary (¶37) directly supports it; the catalog can host the agreed definitions. But the communication design of reports, the board's confirmation of adequacy (¶69), and the governance of reporting policies (¶63) require human judgment and organisational process, not catalog tooling.

**Principles 10 and 11 — Frequency setting and distribution controls**

¶70–74 require the board and senior management to set frequency requirements for each report, routinely test whether reports can be produced within those timeframes, and maintain confidentiality controls on distribution. These are scheduling, testing, and access management matters. The catalog can record the agreed frequency as a metadata attribute on a report asset and document distribution lists, but it cannot enforce the board governance process of setting frequency, test system performance under stress, or implement the information barrier controls that protect confidential risk data.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | **3** | 2 (¶33), 5 (¶46a–b) | Uniqueness, Completeness, Consistency |
| CDE-02 | Legal Entity Identifier (Booking Entity) | **3** | 2 (¶33), 4 (¶41), 8 (¶57) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | **3** | 3 (¶36a), 4 (¶41), 7 (¶52) | Accuracy, Completeness, Timeliness |
| CDE-04 | Risk Type Classification | **2** | 4 (¶41–42), 8 (¶57) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | **2** | 4 (¶41), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | **2** | 4 (¶41), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-07 | Industry / Sector Classification | **2** | 4 (¶41), 8 (¶57), 6 (¶50) | Completeness, Validity, Accuracy |
| CDE-08 | Position / As-Of Date | **3** | 5 (¶44–45), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-09 | GL / Source System Reconciliation Key | **2** | 3 (¶36c), 7 (¶53a) | Completeness, Accuracy, Uniqueness |
| CDE-10 | Source System / Provenance Flag | **2** | 3 (¶36b, ¶39) | Completeness, Validity, Accuracy |
| CDE-11 | Net Exposure / Post-Mitigation Amount | **2** | 8 (¶57–58), 5 (¶46c) | Accuracy, Completeness, Validity |

*Criticality 3 count: 4 (CDE-01, CDE-02, CDE-03, CDE-08). All four satisfy the step-2 sentence: without each, a named aggregate cannot be computed at all. Remaining seven are rated 2: aggregates can be produced but cannot be sliced, reconciled, or trusted in the relevant dimension.*