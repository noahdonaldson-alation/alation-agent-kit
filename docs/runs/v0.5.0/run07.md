# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a precondition for risk management.** The regulation requires banks to produce accurate, complete and timely aggregated risk data not only under normal conditions but under stress and crisis — when the cost of failure is highest. The aspiration is that no risk position remains invisible because data cannot be joined across systems or entities (¶35: *"risk data aggregation capabilities should ensure that risk management reports reflect the risks in a reliable way"*).

- **A single, authoritative, well-defined data foundation.** Banks must strive toward one authoritative source per risk type (¶36(d)), supported by a dictionary of consistently defined concepts across the organisation (¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"*). Without this, aggregation is inherently unreliable.

- **Demonstrable accuracy through reconciliation.** Risk data must be reconciled to accounting and source systems so that accuracy is *evidenced*, not merely asserted (¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*). An unreconciled figure is not a compliant figure.

- **Integrated data architecture with explicit metadata.** Banks must establish integrated data taxonomies and architecture, including metadata about data characteristics and single identifiers or unified naming conventions across legal entities, counterparties, customers and accounts (¶33). This is the closest the regulation comes to mandating a data catalog.

- **Completeness across all material risk types and aggregation dimensions.** All material risk exposures — including off-balance sheet — must be captured, and risk data must be available by business line, legal entity, asset type, industry and region (¶41, ¶4 principle statement). Exceptions must be identified, explained and assessed for impact (¶43).

- **Board and senior management accountability for data quality governance.** Governance of data quality is not a technical function: it is owned at the board and senior management level, with explicit awareness of limitations in coverage, models and legal constraints (¶30–¶31). The data catalog supports this by making those limitations visible and documented.

**Who it applies to**

Principles 1–11 are addressed to **Global Systemically Important Banks (G-SIBs)** directly, with an expectation of adoption by supervisors for **Domestic Systemically Important Banks (D-SIBs)** and, over time, other banks with significant cross-border activity or complexity. The principles apply at the **banking group level**, meaning consolidated data across all subsidiaries and legal entities is within scope — not just the parent entity.

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** A unique, persistent identifier assigned to a counterparty (obligor, borrower, derivative counterparty, issuer) that resolves to a single entity record across all systems in which that counterparty appears. This is a business key, not a system-internal sequence number: it must be stable across source systems and reconcilable to a master counterparty record.
- **Why critical:** Without a common counterparty identifier, exposure records from different booking systems, business lines or geographies cannot be joined. Aggregated credit exposure to a single name — the most explicit example given in ¶46(a) — is arithmetically impossible without it. Every exposure figure attributed to a counterparty is unreliable if the linking key is absent, duplicated or inconsistent.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3.** *"Without this element, the aggregate credit exposure to a large corporate borrower [¶46(a)] cannot be computed at all, because exposure records from different booking systems and geographies cannot be joined to a single entity without a consistent identifying key."*
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; and Principle 5 (¶46(a)) — *"The aggregated credit exposure to a large corporate borrower"* as a named critical risk.
- **Search terms:** counterparty ID, obligor ID, client ID, customer master key, party identifier, legal entity identifier (LEI), counterparty master, global counterparty code
- **Data quality requirements:**
  - *uniqueness* — Each counterparty master record carries exactly one active identifier; no two distinct legal entities share an identifier | Count of duplicate counterparty identifiers in the master register | Threshold: zero duplicates — a duplicate identifier merges two distinct entities into one, making every aggregate that includes either entity wrong | **(¶33)**
  - *validity* — Every exposure record carries a counterparty identifier that resolves to an active record in the counterparty master | Count of exposure records with null, retired or unresolvable counterparty identifiers | Threshold: zero — any unresolvable identifier is an exposure that cannot be attributed or aggregated | **(¶40)**
  - *consistency* — The same counterparty carries the same identifier across all source systems contributing to risk aggregation | Count of counterparties present in more than one source system under differing identifiers, detected by name/LEI matching | Threshold: zero unresolved cross-system mismatches — a mismatch causes double-counting or omission in aggregation | **(¶33)**

---

**CDE-02 — Legal Entity Identifier (Booking Entity)**

- **Definition:** A unique identifier for the bank's own legal entity in which a transaction or position is booked. This is distinct from the counterparty identifier: it represents *the bank's side* of the transaction, used to assign exposures to a subsidiary, branch or consolidated group entity for reporting and consolidation purposes. An LEI (Legal Entity Identifier under ISO 17442) is the expected standard, but the element is the business concept, not the code scheme.
- **Why critical:** Group-level risk aggregation requires rolling up positions from subsidiaries to the consolidated parent. Without a reliable booking entity identifier, positions cannot be assigned to the correct node in the legal entity hierarchy, making both subsidiary-level and consolidated group reports unreliable. Off-balance sheet exposures, which ¶41 explicitly requires to be captured, are particularly vulnerable because they may sit in special-purpose entities with weak system coverage.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 3.** *"Without this element, the aggregate risk exposure at group consolidated level cannot be computed at all, because positions from different subsidiaries and branches cannot be correctly assigned to nodes in the legal entity hierarchy, making consolidation arithmetically impossible."*
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*
- **Search terms:** legal entity identifier, LEI, booking entity, booking legal entity, entity code, subsidiary code, entity hierarchy, consolidated entity, branch code, organisational unit
- **Data quality requirements:**
  - *uniqueness* — Each distinct legal entity in the banking group has exactly one active identifier in the entity master | Count of legal entities with more than one active identifier | Threshold: zero — a duplicate causes positions to be split across ghost entities, corrupting consolidation | **(¶33)**
  - *completeness* — Every exposure and position record carries a populated, valid booking entity identifier | Count of records with null or invalid booking entity identifier | Threshold: zero — a record without a booking entity cannot be assigned to any node in the group hierarchy; it is omitted from all consolidated aggregates | **(¶43)**
  - *validity* — Every booking entity identifier in exposure records resolves to an active node in the legal entity hierarchy | Count of exposure records referencing retired, pending or unrecognised entity codes | Threshold: zero — an unrecognised entity code means the exposure is invisible to consolidation | **(¶40)**

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary amount representing a bank's pre-mitigation exposure to a counterparty, instrument or position, expressed in the native transaction currency. This is the foundational quantity from which all derived risk measures — regulatory capital, concentration limits, stress test outputs — are computed. "Pre-mitigation" is deliberate: it is the amount before netting, collateral or guarantees are applied, which is the basis on which aggregation rules are most consistently applied.
- **Why critical:** Every risk aggregate is ultimately a summation of individual exposure amounts. If this amount is wrong, every figure built from it is wrong. Reconciliation to the general ledger under ¶36(c) is performed against this figure.
- **Risk types:** Credit, counterparty credit, concentration, cross-cutting
- **Criticality: 3.** *"Without this element, the aggregate gross credit exposure figure cannot be computed at all, because there is no monetary quantity to sum; and without it being reconciled to accounting data [¶36(c)], the figure cannot be evidenced as accurate even if computed."*
- **Driven by:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate."*
- **Search terms:** exposure amount, gross exposure, notional amount, outstanding balance, carrying value, principal amount, mark-to-market value, current exposure, drawn amount, commitment amount
- **Data quality requirements:**
  - *accuracy* — Exposure amounts, when aggregated by booking entity and product type, reconcile to corresponding general ledger balances within materiality tolerance | Sum of absolute reconciliation differences as a percentage of total portfolio balance | Threshold: set by the bank's materiality policy (¶56 authorises a materiality-based tolerance, not a fixed percentage; the threshold must be formally approved and documented by senior management) | **(¶36(c))**
  - *validity* — All exposure amounts are numeric, non-negative (for gross exposure before netting), and denominated in a recognised currency code | Count of records with null, non-numeric, negative or unrecognised-currency exposure amounts | Threshold: zero — a null or invalid amount cannot be included in any aggregate and distorts totals | **(¶40)**
  - *completeness* — All exposure records, including off-balance sheet items, carry a populated exposure amount | Count of exposure records with null or zero exposure amount where a non-zero amount is contractually expected | Threshold: zero — a missing amount for a live exposure means that exposure is absent from all aggregates | **(¶43)**

---

**CDE-04 — Risk Type Classification**

- **Definition:** The label assigned to each exposure or position that classifies it into the bank's primary risk taxonomy — at minimum: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk. This is the classification that determines which risk aggregation process, capital calculation and reporting template the record feeds into.
- **Why critical:** Risk reports are organised by risk type. An exposure misclassified as market risk instead of credit risk is excluded from credit risk aggregates and included incorrectly in market risk aggregates. The misclassification does not show as a missing record — it shows as a silent distortion in both figures.
- **Risk types:** Cross-cutting (the classification itself spans all risk types)
- **Criticality: 2.** The aggregate figures for each risk type are produced, but an exposure misclassified between risk types causes one aggregate to be overstated and another understated — the figures are produced but cannot be trusted as correctly partitioned. The error is a slicing failure, not a computational impossibility.
- **Driven by:** Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*; Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*
- **Search terms:** risk type, risk class, risk category, asset class, risk taxonomy, exposure class, product type mapping, risk classification code
- **Data quality requirements:**
  - *validity* — Every exposure record carries a risk type classification drawn from the bank's approved risk taxonomy | Count of records with null or out-of-taxonomy risk type codes | Threshold: zero — a null classification means the record cannot be routed to any risk aggregate | **(¶40)**
  - *completeness* — The approved risk taxonomy covers all product types and instrument classes the bank books | Count of product/instrument types not mapped to a risk type classification | Threshold: zero unmapped types — an unmapped product type is systematically excluded from risk reporting | **(¶43)**
  - *consistency* — The same instrument type carries the same risk classification across all booking systems | Count of instrument types classified differently across source systems for the same risk | Threshold: zero cross-system inconsistencies — inconsistency causes the same instrument to appear in different risk buckets depending on which system reported it | **(¶33)**

---

**CDE-05 — Business Line**

- **Definition:** The organisational dimension that assigns an exposure or position to a business segment of the bank — for example: retail banking, corporate banking, trading, private banking, transaction banking. The classification must be consistent with the bank's internal management reporting structure and stable enough to support time-series comparison.
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. Without it, the bank cannot produce the business-line breakdown that is a minimum requirement for completeness, and cannot identify concentrations within a line.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 2.** Aggregate totals are computed, but the business line slice required by ¶4 (principle statement) and ¶50 cannot be produced. The figure exists at portfolio level but cannot be disaggregated as required — a slice the regulation names directly is unavailable.
- **Driven by:** Principle 4 (principle statement) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date… across all business lines."*
- **Search terms:** business line, business segment, line of business, LOB, division, product line, front office segment, management reporting segment
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a business line assignment drawn from the approved taxonomy | Count of records with null or blank business line | Threshold: zero — a null business line means the record is invisible in all line-level aggregates | **(¶43)**
  - *validity* — All business line codes reference values in the approved, current business line taxonomy | Count of records with retired or unrecognised business line codes | Threshold: zero — a retired code may map to a dissolved segment and cannot be aggregated with current segments without distortion | **(¶40)**
  - *consistency* — Business line assignments are applied using the same taxonomy across all source systems | Count of records where the same transaction appears under different business line codes in different systems | Threshold: zero — inconsistent assignment leads to double-counting in some slices and gaps in others | **(¶33)**

---

**CDE-06 — Geography / Country of Risk**

- **Definition:** The country or region to which an exposure is assigned for risk aggregation purposes — specifically the country of the counterparty's primary domicile, the country of the underlying collateral, or the country of the issuer, depending on the risk type. This is "country of risk" in the standard sense: the jurisdiction whose economic or political conditions most directly affect the probability of loss.
- **Why critical:** Principle 4 names region as a required aggregation dimension. ¶50 gives country credit exposure aggregation as a named example of an on-demand capability supervisors will test. Concentration risk at country level — a primary supervisory concern — cannot be measured without it.
- **Risk types:** Credit, market, concentration, cross-cutting
- **Criticality: 2.** The portfolio aggregate is produced, but country-level concentration figures — which ¶50 names as an explicit supervisory test — cannot be produced. The slice the regulation calls out is unavailable, and the bank cannot respond to a country-risk scenario request.
- **Driven by:** Principle 4 (principle statement) — *"Data should be available by… region and other groupings"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
- **Search terms:** country of risk, country code, jurisdiction, region, geographic segment, domicile country, country of obligor, country of incorporation, ISO country code
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a country of risk assignment | Count of records with null or blank country code | Threshold: zero — a missing country code means the exposure is excluded from all geographic aggregates and concentration measures | **(¶43)**
  - *validity* — All country codes reference values in a recognised, maintained country code standard (e.g. ISO 3166) | Count of records with unrecognised or retired country codes | Threshold: zero — invalid codes cannot be mapped to a region and are excluded from geographic aggregates | **(¶40)**
  - *accuracy* — Country of risk assignments are reviewed periodically for alignment with current counterparty domicile and are updated following material geopolitical changes | Proportion of records where country of risk has not been reviewed within the bank's defined review cycle | Threshold: set by the bank's data maintenance policy; the regulation requires that aggregation remain current and reliable under changing external conditions (¶49(c)), so the review cycle must be documented and approved | **(¶49(c))**

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The classification of a counterparty's or issuer's primary economic activity according to a recognised taxonomy — for example GICS, NAICS, SIC, or the bank's own approved sector scheme. This is the industry or sector dimension used to measure sectoral concentration in credit risk portfolios.
- **Why critical:** ¶57 names industry sector as a required dimension within credit risk reports. ¶50 gives industry credit exposures as a named on-demand scenario. Sectoral concentration — which can be an early indicator of systemic stress — cannot be identified or reported without it.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Credit exposure aggregates are produced, but the sector-level concentration measure required by ¶57 and ¶50 cannot be produced. The industry slice named in the regulation is unavailable, degrading the comprehensiveness of credit risk reports.
- **Driven by:** Principle 8 (¶57) — *"single name, country and industry sector for credit risk"* as required components of risk management reports; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas."*
- **Search terms:** industry sector, industry code, sector classification, GICS sector, NAICS code, SIC code, counterparty industry, obligor sector, economic sector
- **Data quality requirements:**
  - *completeness* — Every credit exposure record carries an industry sector assignment | Count of credit exposure records with null or blank sector code | Threshold: zero — a missing sector code means the exposure is absent from sectoral concentration reports | **(¶43)**
  - *validity* — All sector codes reference values in the bank's approved, current sector taxonomy | Count of records with codes not present in the current approved taxonomy | Threshold: zero — an unrecognised code cannot be aggregated consistently with other records | **(¶40)**
  - *consistency* — The same counterparty carries the same sector classification in all systems that report to risk aggregation | Count of counterparties with differing sector codes across source systems | Threshold: zero — inconsistent classification causes the same counterparty's exposure to be split across sectors in the aggregate | **(¶33)**

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The date as of which an exposure, position or risk measure is stated. This is the temporal key of every risk record: it identifies the snapshot to which the record belongs and determines which records are included in a given daily, weekly or monthly aggregate.
- **Why critical:** Every risk aggregate is stated as of a specific date. Without a reliable as-of date, records from different snapshots cannot be distinguished; a "current" portfolio aggregate may silently include stale positions or exclude today's activity. Under stress conditions, where ¶45 requires rapid production of current data, a wrong or missing as-of date makes the timeliness of data unverifiable.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3.** *"Without this element, the aggregate risk figure for any given reporting date cannot be computed at all, because there is no basis on which to select which records belong to that snapshot; and the bank cannot evidence that its aggregated data is current, which ¶44–45 require as a condition of timeliness compliance."*
- **Driven by:** Principle 5 (¶44) — *"A bank's risk data aggregation capabilities should ensure that it is able to produce aggregate risk information on a timely basis"*; Principle 5 (¶45) — *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis."*
- **Search terms:** as-of date, position date, value date, reporting date, trade date, settlement date, snapshot date, reference date, effective date
- **Data quality requirements:**
  - *validity* — Every risk record carries a populated, parseable as-of date in the agreed format | Count of records with null, unparseable or future-dated as-of date (where future-dated is not permissible for the record type) | Threshold: zero — a null or invalid date means the record cannot be assigned to any reporting snapshot | **(¶40)**
  - *timeliness* — For each risk type, the as-of date of records feeding risk aggregation does not lag behind the expected close-of-business date by more than the tolerance set for that risk type | Count of records whose as-of date is more than the permitted lag behind the current reporting date, by risk type | Threshold: set per risk type based on the bank's frequency requirements per ¶45–46; for trading and counterparty credit risk, same-day data is expected; for retail credit, a longer tolerance may be approved — the tolerance must be documented and approved by senior management | **(¶44–47)**
  - *consistency* — The as-of date of risk records is consistent with the as-of date of the corresponding accounting records used in reconciliation | Count of risk-to-accounting record pairs where the as-of dates differ by more than the permitted tolerance | Threshold: same-date match required for reconciliation to be valid; differences must be documented as exceptions | **(¶36(c))**

---

**CDE-09 — Reconciliation Key (System of Record Reference)**

- **Definition:** The identifier — trade reference number, account number, contract ID, or equivalent — that uniquely identifies a risk record in the bank's authoritative system of record (typically the general ledger or the trade booking system) and allows the risk data record to be matched one-to-one with its counterpart in that system. This is the field that makes reconciliation mechanically possible.
- **Why critical:** ¶36(c) requires risk data to be reconciled to accounting and source data. Reconciliation is not an optional quality check — under BCBS 239 it is the mechanism by which accuracy is *evidenced*. Without a reconciliation key, the bank has no systematic way to demonstrate that its risk data correctly represents its positions. An unreconciled figure is not a compliant figure under this principle, regardless of how plausible it looks. This is the most frequently omitted element in CDE registers, which is exactly why supervisors look for it.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3.** *"Without this element, risk records cannot be matched to their counterparts in the general ledger or system of record, so ¶36(c) reconciliation cannot be performed; the bank therefore cannot evidence the accuracy of its aggregated risk data — an unverifiable figure is not a compliant one."*
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."*; Principle 3 (¶36(d)) — *"A bank should strive towards a single authoritative source for risk data per each type of risk."*
- **Search terms:** trade reference, trade ID, deal ID, account number, GL reference, contract ID, source system key, booking reference, primary key, system of record identifier, external reference
- **Data quality requirements:**
  - *uniqueness* — Each risk record carries exactly one reconciliation key, and that key is unique within the scope of the source system | Count of risk records sharing a reconciliation key within the same system scope | Threshold: zero — a non-unique key causes the reconciliation match to be ambiguous or to produce double-counting | **(¶33)**
  - *completeness* — Every material risk record carries a populated reconciliation key linking it to the system of record | Count of risk records with null or blank reconciliation key | Threshold: zero — a missing key means that record cannot be included in reconciliation and its accuracy cannot be evidenced | **(¶43)**
  - *validity* — Every reconciliation key in a risk record resolves to a live or archived record in the designated system of record | Count of risk records whose reconciliation key returns no match in the system of record | Threshold: zero — an unresolvable key means the risk record has no evidenced counterpart and its accuracy is unverifiable | **(¶40)**

---

**CDE-10 — Source System Identifier / Manual Override Flag**

- **Definition:** Two related attributes that together establish the *provenance* of a risk data record: (a) the identifier of the system from which the record originates (trade capture system, risk engine, spreadsheet, manual input), and (b) a flag indicating whether the record was produced by an automated process or involved manual intervention or end-user computing (EUC). These are metadata attributes of the record, not business data about the transaction itself.
- **Why critical:** ¶36(b) requires effective mitigants for manual processes and EUC, which presupposes that records originating from those processes can be identified. ¶39 requires all manual workarounds to be documented, including their criticality to accuracy. If provenance is not captured as a data attribute, the bank cannot measure its EUC dependency, cannot apply differential controls, and cannot report the limitation to senior management as ¶30 requires. A risk aggregate that contains an unknown proportion of manually produced, uncontrolled data has unquantifiable accuracy risk.
- **Risk types:** Cross-cutting (governance and accuracy across all risk types)
- **Criticality: 2.** Aggregate figures are produced, but the bank cannot demonstrate the control environment under which they were produced, cannot identify which components are EUC-dependent, and cannot support the documentation required by ¶39. The figure exists but its accuracy cannot be adequately evidenced — a provenance failure rather than a computational one.
- **Driven by:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications… it should have effective mitigants in place… and other effective controls that are consistently applied."*; Principle 3 (¶39) — *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual."*
- **Search terms:** source system, source system ID, data source, originating system, feed source, manual input flag, EUC flag, spreadsheet flag, override indicator, manual adjustment indicator, data lineage, input channel
- **Data quality requirements:**
  - *completeness* — Every risk record carries a populated source system identifier | Count of records with null or blank source system identifier | Threshold: zero — a null source system means provenance cannot be established for that record, making the ¶36(b) control requirement unenforceable | **(¶43)**
  - *validity* — All source system identifiers reference systems registered in the bank's authoritative system inventory | Count of records with source system identifiers not present in the registered system inventory | Threshold: zero — an unregistered system has no documented controls, no data owner per ¶34, and no mitigants per ¶36(b) | **(¶40)**
  - *accuracy* — The manual/EUC flag correctly identifies all records that originated from processes not fully automated | Proportion of records verified by periodic sampling where the flag value disagrees with the actual origin process | Threshold: set by the bank's EUC control policy; the regulation does not specify a numeric tolerance but requires that EUC dependency be identified and controlled (¶36(b)); a materially incorrect flag is a control failure | **(¶36(b))**

---

**CDE-11 — Net Exposure / Credit Equivalent Amount**

- **Definition:** The exposure amount after application of netting agreements, collateral and credit risk mitigants, representing the bank's economic risk to a counterparty following mitigation. For derivatives and SFTs, this is typically the net replacement cost or credit equivalent amount. This is the figure that feeds regulatory capital calculations and limit monitoring — it is distinct from gross exposure (CDE-03) and is itself a derived but critical output.
- **Why critical:** ¶58 requires risk reports to provide information "in the context of limits and risk appetite/tolerance." Limit utilisation is measured against net exposure, not gross. An error in collateral application or netting produces an incorrect net exposure, which causes limit breaches to be missed or false alarms to be generated — directly impairing the board's ability to monitor adherence to risk appetite.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 2.** The gross exposure aggregate (CDE-03) is not invalid, but the regulatory capital figure and limit utilisation measures are computed from net exposure. An error here causes risk appetite monitoring to produce incorrect signals — the figures are produced but the slice used for limit and capital purposes cannot be trusted.
- **Driven by:** Principle 8 (¶58) — *"Reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance."*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** net exposure, net credit exposure, post-netting exposure, credit equivalent amount, EAD (exposure at default), net replacement value, net current exposure, collateral-adjusted exposure, risk-weighted exposure
- **Data quality requirements:**
  - *accuracy* — Net exposure amounts reconcile to independently computed values (e.g. from the risk engine or netting system) for a defined sample of counterparties | Proportion of sampled counterparties where the net exposure differs from the independently computed value by more than materiality | Threshold: set by the bank's materiality policy per ¶56; senior management must approve the tolerance | **(¶36(c), ¶56)**
  - *completeness* — Every counterparty for whom a netting or collateral agreement is in force carries a populated net exposure figure | Count of counterparty-date combinations where a netting agreement is in force but net exposure is null | Threshold: zero — a null net exposure where a netting agreement exists means the capital and limit calculation for that counterparty is computed on a gross basis, overstating or understating the true position | **(¶43)**
  - *validity* — Net exposure is never greater than gross exposure (absent unusual CSA terms) and is non-negative for standard credit exposure | Count of records where net exposure exceeds gross exposure or is negative without a documented exception | Threshold: zero undocumented violations — a violation indicates a calculation error or data corruption in the netting engine | **(¶40)**

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Risk-to-Finance Reconciliation**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (Reconciliation Key), CDE-08 (Position / As-Of Date), CDE-02 (Legal Entity Identifier)
- **Rule intent:** The aggregate risk exposure figure, summed by legal entity and as-of date, must be reconcilable to the corresponding balances in the general ledger or accounting system. This reconciliation must be systematic — not performed only on request — and any difference above materiality must be logged as an exception, escalated, explained and resolved within a defined timeframe. The requirement is cross-cutting because it cannot be satisfied by monitoring any single CDE in isolation: it requires a join across risk records (using CDE-09), grouped by legal entity (CDE-02) and date (CDE-08), compared against an accounting system total. No individual element check produces this result.
- **Measurement:** For each combination of booking legal entity and reporting date, compute the sum of gross exposure amounts from the risk data store and compare it to the sum of corresponding balances from the general ledger; record the absolute difference and the difference as a proportion of the total.
- **Threshold and why:** Differences within the bank's approved materiality threshold (defined per ¶56 by reference to accounting materiality concepts, approved by senior management) are logged but do not require escalation; differences above materiality require documented investigation and resolution. The threshold is *not* zero — ¶56 explicitly anticipates a materiality-based tolerance — but it must be formally set, documented and consistently applied. A bank that cannot state its materiality threshold has not implemented this requirement.
- **Cited paragraphs:** ¶36(c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."*; ¶56 — *"Supervisors expect banks to consider accuracy requirements analogous to accounting materiality."*; ¶40 — for the monitoring and escalation obligation.

---

**XDQ-02 — Single Counterparty Resolution Across Systems**

- **Spans:** CDE-01 (Counterparty Identifier), CDE-04 (Risk Type Classification), CDE-03 (Gross Exposure Amount), CDE-11 (Net Exposure)
- **Rule intent:** A single counterparty — identified by legal name, LEI or other unique attributes — must resolve to one and only one counterparty master record across all source systems contributing to risk aggregation. Where a counterparty appears under different local identifiers in different systems (front office, back office, credit risk system, collateral management), those identifiers must be mapped to the single master identifier before aggregation. This is cross-cutting because the failure mode is a *join failure across systems*, not a quality problem within any single system: each system may have a perfectly valid local identifier, but without the cross-system mapping, aggregation produces a fragmented view of the same counterparty as if they were multiple distinct entities.
- **Measurement:** Count of unique counterparties (identified by LEI or confirmed legal name) that appear under two or more distinct identifiers across source systems contributing to risk aggregation, with no active cross-system mapping record linking them; also track the aggregate exposure associated with unmapped counterparties as a proportion of total portfolio exposure.
- **Threshold and why:** The count of unmapped cross-system counterparty appearances should be zero for counterparties that individually or collectively represent material exposure. For the remaining population, the bank's materiality policy determines the acceptable unmapped proportion. The threshold is not zero across all counterparties because ¶43 accepts that data may not be entirely complete provided exceptions are identified and their impact assessed — but for any counterparty above single-name concentration thresholds, the threshold is zero. This must be documented.
- **Cited paragraphs:** ¶33 — *"use of single identifiers and/or unified naming conventions for data including… counterparties"*; ¶46(a) — *"The aggregated credit exposure to a large corporate borrower"* as a named critical risk requiring rapid aggregation; ¶43 — for the completeness monitoring and materiality assessment obligation.

---

**XDQ-03 — EUC / Manual Input Inventory and Control Coverage**

- **Spans:** CDE-10 (Source System Identifier / Manual Override Flag), CDE-09 (Reconciliation Key), CDE-03 (Gross Exposure Amount)
- **Rule intent:** The bank must be able to identify, at any time, what proportion of its aggregated risk data originated from end-user computing tools (spreadsheets, local databases, manual adjustments) rather than controlled, validated systems. This is a cross-cutting requirement because it is a property of the *aggregation process as a whole*, not of any individual record: a portfolio aggregate that is 80% system-generated and 20% EUC-sourced carries materially different accuracy risk than one that is 99% system-generated, and this difference must be visible. No single-element check produces this view — it requires grouping records by CDE-10 (source system / EUC flag), confirming CDE-09 reconciliation keys are present for EUC-sourced records, and assessing the monetary weight of EUC-sourced exposure via CDE-03.
- **Measurement:** For each risk type and reporting date: (a) count and monetary sum of exposure records flagged as EUC or manual origin as a proportion of total records and total exposure; (b) count of EUC-sourced records that carry a reconciliation key (CDE-09) — those without one are both provenance-unknown and unreconcilable; (c) track whether all EUC processes are documented per ¶39.
- **Threshold and why:** The regulation does not set a numeric cap on EUC dependency, but ¶36(b) requires *effective mitigants* and ¶39 requires documentation of all manual processes. A bank must therefore set and publish its own maximum EUC tolerance (as a proportion of total exposure by risk type), approved by senior management. Breaching this tolerance is a governance event, not merely a data quality event. The threshold for undocumented EUC processes is zero — ¶39 admits no exceptions.
- **Cited paragraphs:** ¶36(b) — *"Where a bank relies on manual processes and desktop applications… it should have effective mitigants in place."*; ¶39 — *"banks to document and explain all of their risk data aggregation processes whether automated or manual."*; ¶30 — senior management must be aware of reliance on manual processes as a limitation.

---

## 4. Out of Scope

The following principles — or portions of principles — state requirements that a data catalog and CDE register cannot satisfy. This is not a deficiency in the catalog approach; these are governance, reporting and decision-making obligations that live in different parts of the bank's control framework.

---

**Principle 1 — Governance (¶27–31): partially in scope, partially out**

*What the catalog addresses:* The inventory of CDEs, data ownership assignments (¶34), and documented definitions (¶37) are the data artifact that governance acts upon. The catalog is the evidence that governance has been operationalised for data.

*What the catalog cannot address:* Board and senior management approval of the risk data aggregation framework (¶28), the requirement to deploy adequate resources (¶28), due diligence on acquisitions (¶29(b)), and the board's awareness of aggregation limitations (¶30–31) are organisational governance obligations. They require board minutes, committee charters, resource approval records and management information packs — none of which a data catalog produces or governs.

---

**Principle 2 — Data Architecture and IT Infrastructure (¶32–35): partially in scope**

*What the catalog addresses:* The metadata characteristics, single identifiers and unified naming conventions required by ¶33 are precisely what a data catalog is designed to hold and maintain. Business continuity planning (¶32) is indirectly supported by the catalog's record of data flows and system dependencies.

*What the catalog cannot address:* The design, build and resilience of the actual IT infrastructure — the databases, data pipelines, aggregation engines and their capacity to function under stress — are engineering and architecture decisions. A catalog documents what exists; it does not build or test it. Business impact analysis (¶32) and the IT strategy to remedy shortcomings (¶30) are planning and investment decisions.

---

**Principle 6 — Adaptability (¶48–51): partially in scope**

*What the catalog addresses:* The business line, geography and sector dimensions registered as CDEs (CDE-05, CDE-06, CDE-07) are the slices that adaptability depends on. If those dimensions are well-governed and consistently populated, ad hoc requests along those dimensions can be served.

*What the catalog cannot address:* Adaptability is fundamentally an architectural and systems capability — the ability of the aggregation system to recombine dimensions on demand, support stress scenario inputs (¶48, ¶50), and incorporate organisational changes (¶49(c)). These require flexible data architecture and query infrastructure. The catalog identifies the building blocks; it cannot guarantee the infrastructure can use them adaptably.

---

**Principle 7 — Accuracy in Reporting (¶52–56): partially in scope**

*What the catalog addresses:* The reconciliation key (CDE-09) and the cross-cutting reconciliation requirement (XDQ-01) are direct catalog and DQ monitoring responses to ¶36(c) and ¶53(a). The validation rules inventory described in ¶53(b) is also a catalog-adjacent artifact.

*What the catalog cannot address:* The edit and reasonableness checks on report outputs (¶53(b)), the exception reporting procedures (¶53(c)), and senior management's approval of accuracy and precision standards (¶55) are report production process controls. They govern the reporting pipeline and management review, not the underlying data. Setting materiality thresholds per ¶56 is a risk governance decision — the catalog holds the threshold values once set, but cannot set them.

---

**Principle 8 — Comprehensiveness (¶57–60): partially in scope**

*Why this principle appears in both places:* Principle 8 names industry sector (¶57) as a required report dimension. That naming is the direct authority for CDE-07 (Industry / Sector Classification). So Principle 8 drives a CDE and contributes to the DQ register. But the reporting obligations in Principle 8 itself remain outside catalog scope — this is not a contradiction; it reflects that the same principle has both a data dimension (addressed here) and a reporting dimension (addressed elsewhere).

*What the catalog cannot address:* Whether reports cover all material risk areas, include forward-looking forecasts and stress test results (¶60), address capital adequacy and regulatory capital (¶59), identify emerging concentrations (¶58), and are calibrated to the bank's size and complexity (principle statement) — these are report *content and scope* decisions. They require risk governance frameworks, stress testing infrastructure and board-level reporting design. No data catalog determines whether the right reports are produced for the right audience.

---

**Principle 9 — Clarity and Usefulness (¶61–69): out of scope**

*What the catalog can indirectly support:* The data item inventory and classification referenced in ¶67 (*"A bank should develop an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"*) is close to what a business glossary within a catalog provides.

*What the catalog cannot address:* The clarity, conciseness and usefulness of risk reports (¶61), the balance of qualitative versus quantitative content (¶62), the tailoring of reports to board versus senior management versus risk committees (¶63–66), and the periodic confirmation with recipients that reports remain relevant (¶69) are report design, communication and governance obligations. They depend on human judgment, recipient feedback and board engagement — none of which a data catalog governs.

---

**Principle 10 — Frequency (¶70–71): out of scope**

*Indirect connection:* Timeliness monitoring on CDE-08 (Position / As-Of Date) and the per-risk-type latency thresholds in the DQ register are the data-layer preconditions for frequency compliance. If source data arrives late, frequency requirements cannot be met.

*What the catalog cannot address:* Setting report production frequencies (¶70), testing the ability to produce reports within established timeframes under stress (¶70), and ensuring intraday availability of position data (¶71) are operational capabilities of the risk reporting infrastructure. They require scheduling systems, operational monitoring and escalation procedures — none of which a catalog provides.

---

**Principle 11 — Distribution (¶72–74): out of scope**

*What the catalog can support:* Data classification and sensitivity labelling in a catalog can support access control decisions, and the definition of data owners (¶34, Principle 2) is a prerequisite for distribution policy.

*What the catalog cannot address:* The procedures for rapid collection and dissemination of reports (¶72), the maintenance of confidentiality (¶72), and the periodic confirmation that recipients receive reports on time (¶73) are operational process and information security controls. They require report distribution systems, access management infrastructure and operational oversight. A catalog is not a report distribution system.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | P2 (¶33), P5 (¶46a) | Uniqueness, Validity, Consistency |
| CDE-02 | Legal Entity Identifier (Booking Entity) | 3 | P2 (¶33), P4 (¶41) | Uniqueness, Completeness, Validity |
| CDE-03 | Gross Exposure Amount | 3 | P3 (¶36a, ¶36c) | Accuracy, Validity, Completeness |
| CDE-04 | Risk Type Classification | 2 | P7 (¶53a), P8 (¶57) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | 2 | P4 (principle), P6 (¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | 2 | P4 (principle), P6 (¶50) | Completeness, Validity, Accuracy |
| CDE-07 | Industry / Sector Classification | 2 | P8 (¶57), P6 (¶50) | Completeness, Validity, Consistency |
| CDE-08 | Position / As-Of Date | 3 | P5 (¶44–45) | Validity, Timeliness, Consistency |
| CDE-09 | Reconciliation Key (System of Record Reference) | 3 | P3 (¶36c, ¶36d) | Uniqueness, Completeness, Validity |
| CDE-10 | Source System Identifier / Manual Override Flag | 2 | P3 (¶36b, ¶39) | Completeness, Validity, Accuracy |
| CDE-11 | Net Exposure / Credit Equivalent Amount | 2 | P8 (¶58), P7 (¶53a) | Accuracy, Completeness, Validity |

**Criticality distribution:** 5 elements at level 3 (CDE-01, CDE-02, CDE-03, CDE-08, CDE-09); 6 elements at level 2 (CDE-04, CDE-05, CDE-06, CDE-07, CDE-10, CDE-11); 0 elements at level 1 — no element in this register is merely interpretive context. Every element here, if wrong or missing, either invalidates an aggregate or prevents a required slice or control from functioning. If a level-1 element were warranted, it would be something like a counterparty credit rating or internal risk rating — useful for interpretation but not structurally load-bearing for the aggregate itself. None of those met the CDE definition as stated in the methodology.