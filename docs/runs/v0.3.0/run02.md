# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a precondition for sound risk management.** Banks must be able to aggregate all material risk exposures across the group — by business line, legal entity, asset type, industry, and region — on a timely basis under both normal and stress conditions. The failure mode being prevented is a crisis in which management cannot know the bank's actual risk position. (¶35: *"risk management reports reflect the risks in a reliable way"*; ¶45: *"banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis"*)

- **A single authoritative source per risk type, with documented lineage.** Banks must strive toward one authoritative source for each risk type and must document every aggregation process — automated or manual — including the appropriateness of manual workarounds. This directly targets fragmentation across spreadsheets, siloed systems, and undocumented end-user computing. (¶36(d): *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; ¶39: *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*)

- **A consistent data dictionary and integrated data architecture.** Banks must maintain a shared dictionary of concepts so that data is defined consistently across the organisation, and must establish integrated data taxonomies including metadata, single identifiers, and unified naming conventions for legal entities, counterparties, and accounts. (¶33: *"establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata)"*; ¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently"*)

- **Reconciliation between risk data and accounting/source systems.** Risk data must be reconciled with source systems — including the general ledger — to demonstrate accuracy. Reports must themselves be reconciled to the underlying risk data. Without an auditable reconciliation chain, neither accuracy nor completeness can be evidenced to supervisors. (¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; ¶53(a): *"Defined requirements and processes to reconcile reports to risk data"*)

- **Board and senior management accountability for limitations.** Senior management must be fully aware of limitations that prevent complete risk data aggregation — gaps in coverage, reliance on manual processes, legal impediments to cross-border data sharing — and must actively manage them. This creates a governance obligation that sits above any technical solution. (¶30: *"Senior management should be fully aware of and understand the limitations that prevent full risk data aggregation"*)

- **Measurable, monitored data quality with escalation.** Banks must measure and monitor data accuracy and completeness and must have escalation channels and action plans for poor data quality. Monitoring is not optional documentation — it is an expectation supervisors will test. (¶40: *"Supervisors expect banks to measure and monitor the accuracy of data and to develop appropriate escalation channels"*; ¶43: *"Supervisors expect banks to produce aggregated risk data that is complete and to measure and monitor the completeness"*)

**Who it applies to**

BCBS 239 is addressed to **Global Systemically Important Banks (G-SIBs)** as the primary target, with supervisory expectation that other significant banks will adopt the principles over time. It applies at **banking group level** — subsidiaries, legal entities, and business lines are all in scope, including off-balance-sheet exposures (¶41). The principles apply in both normal operating conditions and **stress and crisis situations**, with heightened timeliness requirements in the latter.

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Unique Identifier**

- **Definition:** The single, persistent, group-wide identifier assigned to a legal-entity counterparty (borrower, issuer, derivative counterparty, or guarantor) that remains stable across originating systems, business lines, and geographies. Distinct from any system-local account or facility identifier.
- **Why critical:** Without this key, exposures sitting in different booking systems, geographies, or product lines cannot be summed to a single counterparty. A large corporate exposure or a counterparty credit risk aggregate is structurally impossible to produce without it.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3.** Without this element, the aggregate figure *"total credit exposure to counterparty X"* cannot be computed at all, because records in different systems cannot be joined to the same obligor. This is not a matter of the figure being less precise — it cannot exist as a group-level number.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 5 (¶46a, 46b) — *"aggregated credit exposure to a large corporate borrower … counterparty credit risk exposures"*
- **Search terms:** counterparty ID, global counterparty identifier, GCI, legal entity identifier, LEI, obligor ID, client master ID, counterparty master
- **Data quality requirements:**
  - *Uniqueness* — Each distinct legal-entity counterparty resolves to exactly one identifier across all in-scope systems | Count of counterparty identifiers mapping to more than one master record, and count of distinct counterparties sharing an identifier | Zero duplicate mappings; zero shared IDs
  - *Completeness* — Every exposure record carries a non-null, populated counterparty identifier | Count of exposure records with null or unresolvable counterparty identifier, as a proportion of total exposure records | < 0.1% of records; 0% of records above a materiality threshold
  - *Consistency* — The same counterparty identifier resolves to the same master record in the credit system, the trading system, and the collateral system | Count of identifier values present in one system but absent from the counterparty master, or resolving to different entities across systems | Zero cross-system divergence for identifiers attached to material exposures
  - *Validity* — Where the bank uses the Legal Entity Identifier (LEI) standard, the LEI must be a registered, non-lapsed value | Count of LEI values that fail validation against the GLEIF registry | Zero lapsed or invalid LEIs on active counterparties

---

**CDE-02 — Booking Legal Entity Identifier**

- **Definition:** The identifier for the specific legal entity within the banking group in which an exposure, position, or transaction is booked. Used to attribute exposures to a regulated subsidiary for solo and sub-consolidated reporting.
- **Why critical:** Group consolidation and subsidiary-level risk reporting both require that every exposure can be attributed unambiguously to a booking entity. Without this, neither the group aggregate nor the solo-entity view is reliable, and the bank cannot demonstrate completeness across the group.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 3.** Without this element, the aggregate figure *"total risk exposure of legal entity Y"* cannot be computed at all, because there is no reliable basis on which to filter or partition records to a given subsidiary. The group cannot be disaggregated into its regulated parts.
- **Driven by:** Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures"* — coverage requires knowing which entity holds each exposure; Principle 2 (¶33) — *"unified naming conventions for data including legal entities"*
- **Search terms:** legal entity identifier, booking entity, booking entity code, entity ID, subsidiary code, legal entity master, entity hierarchy, org unit code
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a booking legal entity identifier | Count of risk records with null booking entity, as proportion of total | Zero nulls on records above materiality threshold
  - *Validity* — Every booking entity value corresponds to an active entity in the group legal entity hierarchy | Count of entity codes not present in the current authorised group structure | Zero orphaned codes
  - *Consistency* — The booking entity on a risk record matches the booking entity recorded in the general ledger for the same instrument | Count of instruments where risk system entity code differs from GL entity code | Zero mismatches on material positions

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary amount representing the bank's gross risk exposure on an instrument, facility, or position before the application of netting, collateral, or other mitigants. Expressed in the currency of the instrument.
- **Why critical:** This is the foundational number from which all risk aggregates are built. Every credit exposure sum, portfolio concentration figure, and regulatory capital input starts here. If this figure is wrong, every downstream aggregate is wrong.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3.** Without this element, the aggregate figure *"total credit exposure of the group"* cannot be computed at all, because there is no monetary amount to sum. This is the quantity being aggregated; without it no aggregate exists.
- **Driven by:** Principle 3 (¶36a) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (¶41) — *"include all material risk exposures, including those that are off-balance sheet"*; Principle 7 (¶52) — reports must *"accurately and precisely convey aggregated risk data"*
- **Search terms:** exposure amount, gross exposure, drawn amount, notional amount, outstanding balance, face value, EAD (exposure at default), book value
- **Data quality requirements:**
  - *Accuracy* — The gross exposure amount on a risk record agrees, within defined tolerance, to the corresponding balance in the general ledger or system of record | Sum of absolute differences between risk system exposure amounts and GL balances for matched instruments | Variance ≤ accounting materiality threshold; zero unexplained differences above that threshold
  - *Completeness* — Every in-scope instrument record carries a non-null, non-zero gross exposure amount (except instruments with genuinely zero balance) | Count of instrument records with null exposure amount; count with zero where non-zero is expected given instrument status | Zero nulls
  - *Timeliness* — Exposure amounts reflect the position as of the stated as-of date and are loaded within the bank's defined cut-off window | Count of instruments whose source-system timestamp post-dates the position date cut-off | Zero late-loaded instruments above materiality

---

**CDE-04 — Risk Type Classification**

- **Definition:** The controlled-vocabulary code that assigns an exposure or position to a defined risk category — at minimum: credit risk, market risk, liquidity risk, operational risk — according to the bank's authoritative risk taxonomy. May be hierarchical (risk type → sub-type).
- **Why critical:** Risk reports are organised by risk type (¶57). Without this classification, exposures cannot be partitioned into the categories that the board and senior management require, regulatory capital cannot be correctly attributed, and completeness across risk areas cannot be demonstrated.
- **Risk types:** Cross-cutting (it classifies all other risk types)
- **Criticality: 2.** The aggregate total exposure figure can be arithmetically produced without this field, but the *risk-type slice* — e.g., total credit risk exposure — degrades: the bank cannot correctly partition exposures and the board cannot assess risk by category.
- **Driven by:** Principle 4 (¶41, ¶42) — *"each system should make clear the specific approach used to aggregate exposures for any given risk measure"*; Principle 8 (¶57) — *"exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*
- **Search terms:** risk type, risk category, risk classification, risk taxonomy, risk class code, Basel risk category, risk sub-type
- **Data quality requirements:**
  - *Validity* — Every risk classification code belongs to the bank's authorised risk taxonomy | Count of records carrying risk type codes not present in the current authorised taxonomy | Zero invalid codes
  - *Completeness* — Every risk record carries a non-null risk type classification | Count of records with null risk type | Zero nulls
  - *Consistency* — The risk type assigned in the risk system is consistent with the product type and booking intention recorded in the origination system | Count of records where risk type and product type are inconsistent according to defined mapping rules | Zero mapping violations on material positions

---

**CDE-05 — Business Line**

- **Definition:** The code identifying the business division or segment — e.g., retail banking, wholesale banking, trading, private banking — responsible for originating or managing an exposure or position, using the bank's authorised business line hierarchy.
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. Without it, the bank cannot slice risk by business unit, cannot identify intra-group concentrations, and cannot respond to ad hoc supervisory queries disaggregated by line of business.
- **Risk types:** Cross-cutting (aggregation dimension across all risk types)
- **Criticality: 2.** The group total can be produced, but the *business-line slice* — e.g., credit exposure in the wholesale banking division — degrades and cannot be reliably produced, impairing both the board's oversight and the bank's ability to respond to supervisory queries.
- **Driven by:** Principle 4 (¶41) and the Principle 4 header — *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (¶50) — *"across all business lines and geographic areas"*
- **Search terms:** business line, business unit, division code, segment code, line of business, LOB code, product line, profit centre
- **Data quality requirements:**
  - *Completeness* — Every exposure record carries a non-null business line code | Count of exposure records with null business line | Zero nulls on material records
  - *Validity* — Every business line code corresponds to a current node in the authorised business line hierarchy | Count of business line codes not matching the authorised hierarchy | Zero invalid codes
  - *Consistency* — The business line code is consistent across the risk system, the management accounting system, and the general ledger for the same instrument | Count of instruments where business line diverges between systems | Zero divergences on material instruments

---

**CDE-06 — Geography / Country of Risk**

- **Definition:** The country or regulatory jurisdiction to which an exposure is attributed for risk aggregation purposes — typically the country of the counterparty's domicile or the country of the underlying collateral or obligor, according to the bank's defined country-of-risk convention.
- **Why critical:** Principle 4 names region as a required aggregation dimension. Principle 6 (¶50) explicitly gives country credit exposure as the paradigm example of an on-demand aggregate a bank must be able to produce rapidly. Without a reliable geography code, country-level concentration risk cannot be measured.
- **Risk types:** Credit, concentration, market, cross-cutting
- **Criticality: 2.** The group total is unaffected, but the *geographic slice* — e.g., total credit exposure to a named country — degrades. The bank cannot produce the specific example called out in ¶50, which supervisors will test directly.
- **Driven by:** Principle 4 header — *"Data should be available by … region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*; Principle 8 (¶57) — *"country … for credit risk"*
- **Search terms:** country of risk, country code, domicile country, jurisdiction, booking country, region code, geographic segment, ISO country code
- **Data quality requirements:**
  - *Completeness* — Every credit and counterparty exposure record carries a non-null country-of-risk code | Count of such records with null geography | Zero nulls on material exposures
  - *Validity* — Every country code is a valid entry in the bank's authorised country reference table (e.g., ISO 3166-1 alpha-2) | Count of codes not matching the authorised reference table | Zero invalid codes
  - *Accuracy* — The country of risk assigned reflects the bank's defined attribution convention (e.g., ultimate obligor domicile, not booking location) consistently across instruments | Sample-based review rate of records where attribution convention has been misapplied | Zero systematic misapplication

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The code that assigns a counterparty or issuer to an industry or economic sector using the bank's authorised sector taxonomy (e.g., NACE, GICS, SIC, or an internal equivalent).
- **Why critical:** Principles 4 and 8 both name industry sector as a required aggregation dimension. Industry concentration is a named component of comprehensive risk reporting (¶57: *"single name, country and industry sector for credit risk"*). Without it, sector concentration cannot be identified or reported.
- **Risk types:** Credit, concentration
- **Criticality: 2.** The group total is unaffected, but the *sector slice* — e.g., total credit exposure to the commercial real estate sector — degrades. Principle 8 is also partially a reporting principle (see Section 4), but the underlying data element is still required.
- **Driven by:** Principle 4 header — *"Data should be available by … industry"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types"*
- **Search terms:** industry code, sector code, NACE code, SIC code, GICS sector, industry classification, counterparty sector, borrower industry
- **Data quality requirements:**
  - *Completeness* — Every counterparty record and every credit exposure record carries a non-null industry/sector code | Count of counterparty and exposure records with null sector code | Zero nulls on material exposures
  - *Validity* — Every sector code is a valid entry in the bank's authorised sector taxonomy | Count of codes not present in the authorised taxonomy | Zero invalid codes
  - *Accuracy* — The sector assigned matches the primary business activity of the counterparty as recorded in the counterparty master | Rate of sector codes that diverge from the counterparty master's primary activity designation | < defined tolerance; zero systematic divergence

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The date as of which an exposure, position, or risk measure is stated. Every aggregate is meaningless without knowing the point in time it represents. Distinct from the transaction date, the settlement date, or the report production date.
- **Why critical:** All risk aggregates are snapshots. An aggregate summing exposures across different as-of dates does not represent the bank's risk position at any moment. Timeliness requirements (Principle 5) and the ability to produce aggregates as of a specified date on demand (¶50) both depend on this field being present, accurate, and consistent.
- **Risk types:** Cross-cutting (applies to all risk types)
- **Criticality: 3.** Without this element, the aggregate figure *"total credit exposure as of [date]"* cannot be computed at all, because records cannot be correctly filtered to a common reference date. Mixing exposures from different dates produces a figure that does not represent the bank's risk at any point in time — the aggregate is not merely less precise, it is invalid.
- **Driven by:** Principle 5 (¶44) — *"produce aggregate risk information on a timely basis"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (¶52) — reports must allow management to *"make critical decisions about risk"* with confidence
- **Search terms:** position date, as-of date, reference date, reporting date, value date, snapshot date, effective date
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null as-of date | Count of risk records with null position date | Zero nulls
  - *Accuracy* — The as-of date on each record correctly reflects the date the position was outstanding, not the load date or processing date | Count of records where as-of date equals system load timestamp rather than business date | Zero such misassignments
  - *Timeliness* — Records for a given position date are available in the aggregation layer within the bank's defined cut-off window | Count of position dates for which the full record set is not available within the SLA window | Zero SLA breaches for critical risk types; measured against the frequency requirements set under Principle 5

---

**CDE-09 — General Ledger Reconciliation Key**

- **Definition:** The identifier — or combination of identifiers (e.g., GL account code + cost centre + instrument reference) — that uniquely links a risk record to its corresponding entry in the general ledger or primary system of record. This is the join key for the reconciliation required under ¶36(c).
- **Why critical:** Accuracy and completeness under Principles 3 and 4 cannot be evidenced without a reconciliation between risk data and the GL. If a risk record cannot be traced to a GL entry, the bank cannot demonstrate that the exposure is being counted once (completeness) and at the correct amount (accuracy). Supervisors will look for this chain of evidence directly.
- **Risk types:** Cross-cutting (the control mechanism for accuracy and completeness across all risk types)
- **Criticality: 2.** The aggregate figure can be arithmetically produced from risk data alone, but the *reconciliation control* — the demonstration that risk data agrees with the GL — degrades entirely: the bank cannot evidence accuracy to supervisors, and unexplained differences between risk and finance cannot be identified or escalated as required by ¶40.
- **Driven by:** Principle 3 (¶36c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 7 (¶53a) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** GL account code, general ledger reference, ledger ID, cost centre, instrument reference, reconciliation key, finance system reference, account number
- **Data quality requirements:**
  - *Completeness* — Every in-scope risk record carries a non-null GL reconciliation key | Count of risk records with null GL reference | Zero nulls on records above materiality threshold
  - *Uniqueness* — Each GL reconciliation key maps to at most one risk record per position date (or the relationship is explicitly defined as one-to-many with a documented aggregation rule) | Count of GL references appearing on more than one risk record where a one-to-one relationship is expected | Zero unexpected duplicates
  - *Accuracy* — The exposure amount on the risk record agrees with the balance on the matched GL entry within defined tolerance | Sum of absolute variances between matched pairs; count of pairs with variance exceeding tolerance | Zero unexplained variances above materiality threshold

---

**CDE-10 — Source System Identifier / Manual Override Flag**

- **Definition:** Two related attributes: (1) the identifier of the authoritative source system from which a risk record was loaded or derived; (2) a flag or indicator marking whether the record — or any field on it — has been subject to manual intervention, end-user-computing input (e.g., spreadsheet), or override outside the automated pipeline.
- **Why critical:** ¶36(b) requires effective controls over manual processes; ¶36(d) requires a single authoritative source per risk type; ¶39 requires documentation of all manual workarounds. Without source system provenance and a manual override flag, the bank cannot demonstrate which records come from controlled automated pipelines versus uncontrolled EUC, cannot target validation effort, and cannot report on its degree of automation to governance bodies.
- **Risk types:** Cross-cutting (lineage and provenance spans all risk types)
- **Criticality: 2.** Aggregates can be produced, but the *provenance and control* dimension degrades: the bank cannot distinguish authoritative-source data from manually adjusted data, cannot evidence the controls required by ¶36(b), and cannot produce the documentation of manual workarounds required by ¶39. Governance bodies and supervisors have no way to assess reliability.
- **Driven by:** Principle 3 (¶36b) — *"effective mitigants in place (eg end-user computing policies and procedures)"*; Principle 3 (¶36d) — *"strive towards a single authoritative source for risk data"*; Principle 3 (¶39) — *"document and explain all of their risk data aggregation processes whether automated or manual"*
- **Search terms:** source system, system of origin, data source, feed identifier, EUC flag, manual override indicator, manual adjustment flag, data lineage, provenance, upstream system ID
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null source system identifier | Count of records with null source system identifier | Zero nulls
  - *Validity* — Every source system identifier corresponds to a registered, documented source system in the bank's data inventory | Count of source system codes not present in the authorised source system register | Zero unregistered source systems
  - *Accuracy* — The manual override flag correctly identifies all records that have been modified outside the automated pipeline | Rate of discrepancy identified through sampling between records flagged as automated and records showing evidence of manual modification (e.g., loaded via flat file, no system timestamp) | Zero undetected manual overrides on material records; periodic sample review rate defined by governance

---

**CDE-11 — Net Exposure / Post-Mitigation Exposure Amount**

- **Definition:** The monetary exposure amount remaining after recognised netting agreements, collateral, guarantees, and credit risk mitigants have been applied, expressed in a consistent currency for aggregation. Used as the input to regulatory and economic capital calculations and limit monitoring.
- **Why critical:** Risk limits, capital adequacy reporting, and concentration monitoring all operate on net rather than gross exposure. The board monitors adherence to risk appetite using net figures (¶58: *"provide information in the context of limits and risk appetite/tolerance"*). Without a reliable net exposure figure, limit utilisation cannot be correctly computed and capital adequacy reports are unreliable.
- **Risk types:** Credit, counterparty, concentration
- **Criticality: 2.** The gross exposure figure (CDE-03) still exists, but the *limit-utilisation and capital adequacy slice* degrades: the bank cannot correctly compute limit headroom, regulatory capital requirements, or net concentration figures. The aggregate is produced but cannot be trusted for its primary management use.
- **Driven by:** Principle 4 (¶41) — off-balance-sheet items and netting are in scope; Principle 8 (¶57) — *"risk-related measures (eg regulatory and economic capital)"*; Principle 8 (¶58) — *"provide information in the context of limits and risk appetite/tolerance"*
- **Search terms:** net exposure, post-mitigation exposure, EAD net of collateral, net credit exposure, net position, exposure after netting, RWA input, regulatory exposure
- **Data quality requirements:**
  - *Accuracy* — The net exposure amount correctly reflects the application of all recognised netting agreements and eligible collateral in accordance with the bank's credit risk policy | Count of instruments where net exposure equals gross exposure despite the existence of a registered netting agreement or collateral | Zero failures of this type on material positions
  - *Completeness* — Every credit and counterparty exposure record carries a net exposure amount (or an explicit indicator that no mitigants apply) | Count of records with null net exposure and no mitigant-absence indicator | Zero unexplained nulls on material positions
  - *Consistency* — The net exposure figure on the risk record is consistent with the collateral and netting data held in the collateral management system | Count of instruments where the implied mitigation (gross minus net) cannot be reconciled to collateral system records | Zero unreconciled differences above materiality

---

## 3. Cross-cutting Data Quality Requirements

---

**XDQ-01 — Group-wide Counterparty Consolidation: Single Obligor View**

- **Spans:** CDE-01 (Counterparty Unique Identifier), CDE-02 (Booking Legal Entity), CDE-03 (Gross Exposure Amount), CDE-11 (Net Exposure Amount)
- **What this monitors:** Whether the bank can correctly sum all exposures — across booking entities, products, geographies, and systems — to a single counterparty. This is not a property of any individual element. It is the integrative test: even if each CDE is correct in isolation, exposures remain fragmentary unless the join from CDE-03/CDE-11 through CDE-01 to a consolidated counterparty view functions correctly across all in-scope systems. This is the primary aggregation failure mode BCBS 239 was written to address.
- **Regulatory basis:** Principle 2 (¶33) — *"use of single identifiers … for … counterparties"*; Principle 4 (¶41) — *"include all material risk exposures"*; Principle 5 (¶46a, 46b) — aggregated credit exposure to a large corporate and counterparty credit risk are named critical risks requiring rapid production
- **Dimension:** Completeness, Consistency
- **Rule intent:** Every unit of gross and net exposure carried in any in-scope system for a given counterparty can be retrieved and summed to a single counterparty total using CDE-01 as the join key, with no double-counting and no omissions
- **Measurement:**
  1. For a sample of counterparties known to have exposures in multiple systems, compute the group-level total from the risk aggregation layer and compare to the independent sum from each source system. Count of counterparties where the two totals diverge by more than a defined tolerance.
  2. Count of exposure records in any source system that carry a counterparty identifier not resolvable in the group counterparty master — these are the orphaned exposures that would be excluded from the consolidated view.
  3. Count of counterparty identifiers in the aggregation layer that map to more than one master entity record (duplication test).
- **Suggested threshold:** Zero orphaned exposures above materiality threshold; zero duplicate master mappings; zero group-total divergences exceeding accounting materiality for any counterparty in the sample

---

**XDQ-02 — Risk-to-Finance Reconciliation Chain**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key), CDE-08 (Position / As-Of Date), CDE-02 (Booking Legal Entity)
- **What this monitors:** Whether the total of risk exposures, summed from the risk aggregation system as of a given position date and by booking entity, agrees with the corresponding balance in the general ledger — and whether every difference is identified, explained, and within a defined tolerance. This test cannot be performed on any single CDE; it requires the join between CDE-03 and the GL via CDE-09, scoped by CDE-02 and CDE-08. It is the primary control mechanism by which accuracy and completeness are demonstrated to supervisors and to internal audit.
- **Regulatory basis:** Principle 3 (¶36c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53a) — *"Defined requirements and processes to reconcile reports to risk data"*; Principle 3 (¶40) — *"measure and monitor the accuracy of data and … develop appropriate escalation channels and action plans to be in place to rectify poor data quality"*
- **Dimension:** Accuracy, Completeness
- **Rule intent:** For every booking entity (CDE-02) and every position date (CDE-08), the sum of gross exposure amounts (CDE-03) in the risk system, joined to the GL via CDE-09, equals the corresponding GL balance within defined tolerance; all variances are identified, categorised (timing, exclusion, methodology), and escalated if they exceed the materiality threshold
- **Measurement:**
  1. Aggregate gross exposure in the risk system by booking entity and position date; join to the GL via CDE-09; compute the net variance and the gross variance (sum of absolute differences) for each entity/date pair.
  2. Count of exposure records in the risk system with no matching GL entry (completeness gap: risk captures an exposure the GL does not).
  3. Count of GL entries with no matching risk record (completeness gap: GL captures an amount not in risk).
  4. Count of entity/date pairs for which the reconciliation has not been run within the SLA window.
- **Suggested threshold:** Net variance ≤ accounting materiality threshold for each entity/date pair; zero unmatched records above individual instrument materiality; zero entity/date pairs for which reconciliation has not been completed within the defined production window; all variances above threshold documented with a named owner and resolution date

---

## 4. Out of Scope

The following principles impose obligations that a data catalog and CDE register — however well designed — cannot satisfy. Being explicit about this is not a limitation of the analysis; it is the correct statement of what catalog-based data governance is and is not.

---

### Principles 8–11: Report content, clarity, frequency, and distribution

**What these principles require:**

- **Principle 8 (Comprehensiveness, ¶57–60):** Risk management reports must cover all material risk areas, include regulatory and economic capital, identify emerging concentrations, and contain forward-looking forecasts and stress test results. These are obligations about what a report says and whether it covers the right scope — not about whether the underlying data is governed.

- **Principle 9 (Clarity and usefulness, ¶61–69):** Reports must be clear, concise, and tailored to recipients. The board must confirm periodically that reports meet its needs. The balance of quantitative versus qualitative content must be appropriate to the level of the organisation. These are obligations about how information is communicated and whether governance bodies are engaged — not data quality obligations.

- **Principle 10 (Frequency, ¶70–71):** The board and senior management must set report frequency, and the bank must routinely test its ability to produce accurate reports within established timeframes, including intraday in a crisis. This is a reporting operations and governance obligation.

- **Principle 11 (Distribution, ¶72–73):** Reports must reach the right people, with confidentiality maintained, within defined timeframes. The bank must confirm periodically that relevant recipients receive reports on time. This is an information security, access control, and workflow obligation.

**Why a catalog cannot deliver this:**
A data catalog can describe data assets, monitor data quality against defined rules, and surface lineage. It cannot determine whether a report covers the right risk areas, whether the board finds the reports clear and useful, whether the frequency of production is appropriate to the nature of the risk, or whether reports reach the right people. These require report governance frameworks, board-level feedback mechanisms, escalation procedures, and workflow controls. A well-governed catalog is a necessary input to the data that feeds these reports — it cannot substitute for the governance of the reports themselves.

**The Principle 8 split — why it appears in both places:**
Principle 8 is the one principle that does both jobs simultaneously. Its report-content obligations (¶57–60: comprehensiveness of coverage, forward-looking content, stress testing) are out of scope for a catalog and belong to a report governance framework. However, Principle 8 also names specific data dimensions — industry sector (¶57), business line (¶50, applied via Principle 6), country (¶57–58) — that are required as data elements for the underlying aggregations. This is why industry/sector (CDE-07), business line (CDE-05), and geography (CDE-06) appear as CDEs above: the data element is within scope; the report-level obligation that names it is not. Treating this as a contradiction would be an error — the two halves of the principle operate at different levels.

---

### Principle 1 (Governance, ¶27–31): Board and senior management accountability

Principle 1 requires board approval of the risk data aggregation framework (¶28), senior management awareness of limitations (¶30), independent validation of aggregation and reporting processes (¶29), and board awareness of compliance with BCBS 239 (¶31). These are governance, oversight, and audit obligations. A data catalog can document the framework, hold metadata, and surface data quality issues — but the board's approval, the independent validation function, and senior management's acknowledgment of limitations are organisational and accountability matters that no technical tool can satisfy.

**What would be needed instead:** A documented governance framework with board sign-off; an independent validation function (separate from the data management team) conducting periodic compliance reviews against the Principles; a management information pack presented to senior management identifying known gaps, limitations, and remediation plans; and board minutes evidencing awareness and decision-making.

---

### Principle 2 (Data Architecture, ¶32–35): Infrastructure, business continuity, and role ownership

The architectural and ownership obligations in Principle 2 go beyond what a catalog governs. Specifically: business continuity planning and business impact analysis for risk data (¶32); the actual design and build of integrated data architecture (¶33 — the catalog describes architecture but does not constitute it); and the establishment of formal roles and responsibilities with adequate controls throughout the data lifecycle (¶34). A data catalog can register data owners and stewards and can document lineage, but it cannot create the underlying IT infrastructure, enforce access controls outside its own perimeter, or substitute for formal role accountability structures in the bank's operating model.

---

### Principle 3 (Accuracy, ¶36–40): Manual process controls, escalation procedures, and the "dictionary" obligation

Two elements of Principle 3 are beyond what a catalog provides:

1. **End-user computing controls (¶36b):** The requirement to have *"effective mitigants in place"* for manual processes — EUC policies, procedures, and controls — is an operational risk management and IT governance obligation. A catalog can flag records from EUC sources (CDE-10 addresses this at the data level), but it cannot enforce the policies or test the controls.

2. **Escalation channels and action plans (¶40):** The requirement to have escalation channels and action plans for poor data quality is an operational and governance process. A catalog can surface the monitoring signal (a DQ rule breach), but the escalation path, the ownership of remediation, and the action plan are defined and executed outside the catalog.

3. **The concept dictionary (¶37):** The requirement for *"a 'dictionary' of the concepts used, such that data is defined consistently"* is directionally supported by a business glossary in the catalog. However, the authoritative status of that dictionary — its governance, approval, and enforcement — requires an organisation-wide data governance process that the catalog tool facilitates but does not itself constitute.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Unique Identifier | **3** | P2 (¶33), P5 (¶46a–b) | Uniqueness, Completeness, Consistency, Validity |
| CDE-02 | Booking Legal Entity Identifier | **3** | P2 (¶33), P4 (¶41) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | **3** | P3 (¶36a), P4 (¶41), P7 (¶52) | Accuracy, Completeness, Timeliness |
| CDE-04 | Risk Type Classification | **2** | P4 (¶41–42), P8 (¶57) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | **2** | P4 header, P6 (¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | **2** | P4 header, P6 (¶50), P8 (¶57) | Completeness, Validity, Accuracy |
| CDE-07 | Industry / Sector Classification | **2** | P4 header, P8 (¶57), P6 (¶50) | Completeness, Validity, Accuracy |
| CDE-08 | Position / As-Of Date | **3** | P5 (¶44), P6 (¶50), P7 (¶52) | Completeness, Accuracy, Timeliness |
| CDE-09 | GL Reconciliation Key | **2** | P3 (¶36c), P7 (¶53a) | Completeness, Uniqueness, Accuracy |
| CDE-10 | Source System Identifier / Manual Override Flag | **2** | P3 (¶36b, ¶36d, ¶39) | Completeness, Validity, Accuracy |
| CDE-11 | Net Exposure / Post-Mitigation Exposure Amount | **2** | P4 (¶41), P8 (¶57–58) | Accuracy, Completeness, Consistency |

**Cross-cutting requirements:**

| ID | Description | Spans | DQ Dimensions |
|---|---|---|---|
| XDQ-01 | Group-wide counterparty consolidation: single obligor view | CDE-01, CDE-02, CDE-03, CDE-11 | Completeness, Consistency |
| XDQ-02 | Risk-to-finance reconciliation chain | CDE-03, CDE-09, CDE-08, CDE-02 | Accuracy, Completeness |

**Criticality distribution:** 4 elements at criticality 3 (CDE-01, CDE-02, CDE-03, CDE-08); 7 elements at criticality 2; 0 elements at criticality 1. No element in this register is merely supportive context — every one affects either the computability of an aggregate or the ability to slice, reconcile, or evidence it. If a criticality-1 element is identified in the bank's own implementation (e.g., a descriptive counterparty name field), it should be documented but clearly distinguished from the structural elements above.