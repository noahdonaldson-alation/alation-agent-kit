# BCBS 239 — Data Catalog Interpretation: CDEs, DQ Monitoring, and Scope Limits

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable aggregation across the group.** Banks must be able to aggregate all material risk exposures — across legal entities, business lines, geographies, and asset types — accurately and completely, so that risk figures are not distorted by gaps in coverage or broken joins between systems. (¶33, ¶41, ¶43: *"capture and aggregate all material risk data across the banking group … by business line, legal entity, asset type, industry, region."*)
- **Accuracy and reconcilability.** Risk data must be reconciled to accounting and authoritative source systems so that the figures presented to management and supervisors can be evidenced, not merely asserted. Manual processes and end-user computing must be identified and controlled. (¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."* ¶36(d): *"A bank should strive towards a single authoritative source for risk data per each type of risk."*)
- **Timeliness, including under stress.** Risk data aggregation must be fast enough to meet normal reporting cycles and must accelerate further during stress or crisis — with credit, market, and liquidity figures available rapidly, and some position data available intraday. (¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*)
- **Governed metadata and architecture.** Banks must maintain a dictionary of data concepts, single identifiers or unified naming conventions for counterparties, legal entities, customers and accounts, and clear documentation of all aggregation processes — automated or manual. (¶33: *"integrated data taxonomies and architecture … including information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."* ¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation."*)
- **Board and senior management accountability.** Senior management must understand the limitations that prevent full aggregation — coverage gaps, manual processes, legal impediments — and must embed data capability considerations into IT strategy, acquisitions, and new product initiatives. (¶30: *"Senior management should be fully aware of and understand the limitations that prevent full risk data aggregation."*)
- **Measurable, monitored data quality.** Banks must not merely aim for quality; they must measure and monitor it, with escalation channels and action plans for poor quality, and must assess the impact of any incompleteness on risk management effectiveness. (¶40: *"Supervisors expect banks to measure and monitor the accuracy of data and to develop appropriate escalation channels and action plans to be in place to rectify poor data quality."* ¶43: *"Supervisors expect banks to produce aggregated risk data that is complete and to measure and monitor the completeness of their risk data."*)

**Who it applies to**

Globally systemically important banks (G-SIBs) are the primary targets, with the Basel Committee's expectation that national supervisors would extend the principles to domestic systemically important banks (D-SIBs). The principles apply at the banking group level — consolidated across all legal entities, subsidiaries, and booking locations, regardless of jurisdiction.

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** The unique, persistent identifier assigned to each legal counterparty — a borrower, issuer, derivative counterparty, or depositor — that is used consistently across all systems in which exposures to that counterparty are recorded. This is the enterprise-wide key that makes it possible to sum all exposures to one counterparty regardless of which system, business line, or geography originated them.
- **Why critical:** Without a stable, single identifier for each counterparty, exposure records from different systems cannot be reliably joined. A credit exposure in the lending system and a mark-to-market exposure in the derivatives system would be attributed to the same entity only by accident. The aggregate credit exposure to that counterparty — the figure that triggers large-exposure limits and concentration reporting — would be understated or incomputable.
- **Risk types:** Credit, counterparty credit, concentration, cross-cutting
- **Criticality: 3.** Without a resolvable counterparty identifier, the aggregate credit exposure to a large corporate borrower cannot be computed at all, because exposure records from lending, trading, and off-balance-sheet systems cannot be reliably joined to a single obligor. An unresolvable key is not a precision problem — it is a structural failure that makes the figure unproducible.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 5 (¶46b) — *"Counterparty credit risk exposures, including, for example, derivatives"* named as a critical risk requiring rapid aggregation.
- **Search terms:** counterparty ID, counterparty code, obligor ID, client identifier, legal entity identifier (LEI), GFCID, golden source ID, entity key, customer master ID, party identifier
- **Data quality requirements:**
  - *uniqueness* — Each counterparty must resolve to exactly one identifier across the enterprise; no two distinct legal entities share the same identifier, and no single entity carries more than one active identifier | count of duplicate active identifiers per counterparty, and count of exposure records carrying identifiers that resolve to more than one master record | threshold: zero — a duplicate identifier is always a defect because it either splits a single obligor's exposures across two keys (understatement of concentration) or merges two obligors into one (overstatement); there is no materiality floor for an identifier whose sole function is to enable correct joins | **(¶33)**
  - *completeness* — Every exposure record carries a populated, non-null counterparty identifier | count and percentage of exposure records with a null or blank counterparty identifier field | threshold: zero — an exposure record with no counterparty key is invisible to counterparty-level aggregation; the omission cannot be tolerated at any volume because even a single large exposure record without a key could breach a concentration limit silently | **(¶43)**
  - *validity* — Every counterparty identifier present on an exposure record resolves to an active record in the authoritative counterparty master | count of exposure records carrying an identifier not found in the current counterparty master | threshold: zero — an unresolvable identifier is functionally equivalent to a null: the exposure cannot be attributed to any obligor and falls out of aggregation entirely | **(¶40)**
  - *consistency* — The same counterparty carries the same identifier across all source systems (lending, trading, collateral, derivatives) | count of counterparties appearing under different identifiers in two or more source systems, detected by matching on LEI, name-and-jurisdiction, or other stable attribute | threshold: zero — any cross-system mismatch means that joining on the identifier will fail to consolidate those exposures, producing a systematic undercount; this is the cross-system variant of the uniqueness check | **(¶33)**

---

**CDE-02 — Legal Entity Identifier (Own Booking Entity)**

- **Definition:** The identifier for the bank's own legal entity in which a transaction or position is booked — a subsidiary, branch, or holding company within the banking group. This is distinct from the counterparty identifier (CDE-01), which identifies the external obligor. This element answers "who within the group holds this exposure?"
- **Why critical:** Group-level consolidation — the summation of all risk exposures up to the consolidated banking group — requires that every exposure record be tagged with the booking entity so that intra-group trades can be identified and eliminated and subsidiary-level reports can be produced. Without this tag, the bank cannot disaggregate its aggregate risk position by legal entity, cannot produce subsidiary-level regulatory reports, and cannot identify intra-group concentrations.
- **Risk types:** Cross-cutting (applies to credit, market, liquidity — wherever group consolidation is required)
- **Criticality: 3.** Without the booking entity identifier, the aggregate group exposure cannot be correctly consolidated — intra-group positions cannot be eliminated, and subsidiary-level figures cannot be extracted. The consolidated risk figure is therefore either overstated (double-counting intra-group positions) or unproducible at the subsidiary level required by Principle 4.
- **Driven by:** Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures"* across the banking group; Principle 2 (¶33) — single identifiers required for *"legal entities"* specifically.
- **Search terms:** legal entity ID, booking entity, entity code, subsidiary code, branch identifier, organisational unit, LE code, group entity hierarchy, consolidated entity key, LEI (own entity)
- **Data quality requirements:**
  - *completeness* — Every exposure and position record carries a populated booking entity identifier | count and percentage of records with a null or missing entity code | threshold: zero — a record without a booking entity code falls outside both group consolidation and entity-level slicing; even a small number of unattributed large positions would corrupt the consolidated figure | **(¶43)**
  - *validity* — Every booking entity identifier present on a risk record maps to a current, active entity in the official group legal entity hierarchy | count of records carrying entity codes not present in the authorised group hierarchy | threshold: zero — an invalid entity code means the position cannot be attributed to any part of the group; it is excluded from consolidation, which is a completeness failure | **(¶40)**
  - *consistency* — The set of entity codes used in risk systems is the same as the set in the accounting / regulatory reporting systems | count of entity codes appearing in risk data that have no counterpart in finance reporting, and vice versa | threshold: zero — a mismatch means certain entities' exposures will be absent from one system's consolidated view, which directly undermines the reconciliation required by ¶36(c) | **(¶36(c))**

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary measure of the bank's risk exposure to a counterparty or position before the application of collateral, netting, or credit risk mitigants. For credit risk this is typically the drawn balance or notional; for derivatives it is the mark-to-market replacement cost or potential future exposure; for market risk it is the position value. This is the raw amount from which all risk figures are built.
- **Why critical:** Every aggregated risk figure — total credit exposure by counterparty, concentration by sector, market risk by business line — is arithmetically derived from summing exposure amounts. If the exposure amount is wrong or missing, every aggregate that includes it is wrong. No other CDE can compensate for a corrupt exposure amount.
- **Risk types:** Credit, counterparty credit, market, concentration, cross-cutting
- **Criticality: 3.** Without a populated and accurate gross exposure amount, the aggregate credit or market risk figure X cannot be computed at all, because the aggregate is defined as the sum of individual exposure amounts. A record with a null or erroneous amount contributes the wrong value — or zero — to every roll-up that includes it. This is the field being aggregated; every other CDE is a dimension or key.
- **Driven by:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 7 (¶52) — *"Risk management reports should be accurate and precise to ensure a bank's board and senior management can rely with confidence on the aggregated information."*
- **Search terms:** exposure amount, drawn balance, notional amount, current exposure, mark-to-market value, replacement cost, position value, EAD, exposure at default, gross credit exposure, face value
- **Data quality requirements:**
  - *accuracy* — Each exposure amount correctly reflects the current balance or valuation as recorded in the system of record for that instrument type | count of exposure records where the amount differs from the corresponding record in the source system or general ledger by more than the materiality threshold | threshold: set by materiality — per ¶56, a discrepancy is material if *"omission or misstatement could influence the risk decisions of users"*; the bank's risk finance reconciliation team defines the tolerance in monetary and percentage terms; there is no universal zero threshold because rounding and valuation timing differences are unavoidable | **(¶40, ¶56)**
  - *completeness* — Every exposure record carries a non-null exposure amount | count and percentage of exposure records with a null or zero amount where a non-zero balance is expected (identified by the presence of a live instrument record in the source system) | threshold: zero for nulls — a null exposure amount means the position contributes nothing to any aggregate and is silently excluded; zero-value positions that are genuinely zero are acceptable | **(¶43)**
  - *validity* — Exposure amounts are expressed in a defined currency and are non-negative for gross pre-netting measures (where the business definition requires a positive value) | count of records carrying negative gross exposure amounts or exposure amounts with no associated currency code | threshold: zero — a negative gross exposure or a currency-less amount is a data integrity failure that would corrupt any summation | **(¶40)**

---

**CDE-04 — Risk Type Classification**

- **Definition:** The categorical label that classifies each exposure or position by risk type — at minimum, credit risk, market risk, liquidity risk, counterparty credit risk, and operational risk. This classification determines which risk aggregation engine, limit framework, and report the record flows into.
- **Why critical:** Principle 7 requires that reports accurately convey aggregated risk data; Principle 8 requires that reports cover all significant risk areas. If an exposure is misclassified — a derivatives exposure labelled as a lending exposure, for example — it will be measured by the wrong methodology, appear in the wrong report, and absent from the correct one. The same exposure can also generate double-counting if it appears in two risk buckets. This is the primary taxonomy that routes exposures through the risk aggregation framework.
- **Risk types:** Cross-cutting (the classification itself applies across all risk types)
- **Criticality: 2.** A misclassification does not make the exposure disappear from all aggregations — it misdirects it. The aggregate for the incorrectly labelled risk type will be overstated, and the correct risk type understated. The aggregate figure is produced but wrong in a way that is invisible without the classification being correct. This is a 2 because the figure is produced, but cannot be trusted for any risk-type slice.
- **Driven by:** Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 4 (¶41) — completeness of aggregation across all material risk types; Principle 2 (¶33) — *"integrated data taxonomies."*
- **Search terms:** risk type, risk category, risk class, risk classification, risk taxonomy, risk bucket, product type, instrument class, asset class
- **Data quality requirements:**
  - *validity* — Every exposure record carries a risk type value drawn from the bank's approved risk taxonomy; no free-text or unlisted values appear | count of records carrying a risk type code not present in the approved taxonomy reference table | threshold: zero — an unrecognised risk type code means the exposure cannot be correctly routed to any risk report; it falls into an unmeasured residual category | **(¶40)**
  - *completeness* — Every exposure record carries a populated risk type classification | count and percentage of records with a null or blank risk type field | threshold: zero — an unclassified exposure is invisible to all risk-type-specific aggregations and limits; the omission cannot be tolerated at any volume | **(¶43)**
  - *consistency* — The risk type classification applied to a given instrument is consistent between the risk system and the finance system where the same instrument appears in both | count of instruments where the risk type in the risk system differs from the product/instrument class in the finance system | threshold: zero for structural mismatches (e.g., a derivative classified as a loan); the bank's data governance team reviews borderline cases | **(¶36(c))**

---

**CDE-05 — Business Line**

- **Definition:** The organisational dimension that identifies the business unit or division in which an exposure or position originates or is managed — for example, retail banking, corporate banking, investment banking, treasury, or trading. This is one of the explicit aggregation dimensions named in Principle 4.
- **Why critical:** Principle 4 explicitly requires that risk data be available by business line so that the bank can identify risk concentrations and emerging risks within each line of business. Without this tag, the bank cannot produce business-line-level risk reports, cannot identify which business unit is driving a concentration, and cannot respond to a supervisory request for exposures by business line.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 2.** The consolidated aggregate figure is still producible without the business line tag — all exposures are summed regardless. But the figure cannot be sliced by business line, which means the bank cannot identify concentrations within a line, cannot produce the business-line reports required by Principle 4, and cannot respond to a ¶50 ad hoc request for business-line-level data. The aggregate is present but ungroupable by a mandated dimension.
- **Driven by:** Principle 4 (¶41, header) — *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures … across all business lines and geographic areas."*
- **Search terms:** business line, business unit, line of business, division code, segment code, desk code, cost centre, organisational unit, front office unit
- **Data quality requirements:**
  - *completeness* — Every exposure and position record carries a populated business line code | count and percentage of records with null or missing business line | threshold: zero — a record without a business line tag cannot contribute to any business-line-level report or concentration analysis | **(¶43)**
  - *validity* — Every business line code resolves to an active entry in the bank's official organisational hierarchy | count of records carrying business line codes not present in the current hierarchy | threshold: zero — an obsolete or unrecognised business line code means the exposure cannot be attributed to any current business unit | **(¶40)**
  - *consistency* — Business line codes are assigned consistently for the same instrument type across booking systems | count of instruments appearing under different business line codes in two or more systems without a documented justification | threshold: zero for unexplained discrepancies; documented reclassifications are exempt | **(¶33)**

---

**CDE-06 — Geography / Country**

- **Definition:** The country or jurisdiction of the counterparty, the risk, or the booking location — the geographic dimension used to slice exposures for country risk, cross-border concentration, and regional reporting. This encompasses at minimum the country of counterparty domicile and, where relevant, the country of risk (which may differ for guaranteed or collateralised exposures).
- **Why critical:** Principle 4 names region as a mandatory aggregation dimension. Principle 6 (¶50) gives an explicit worked example: a bank must be able to aggregate country credit exposures as of a specified date. Without the geography field, neither supervisory ad hoc requests nor internal country-limit monitoring can be satisfied.
- **Risk types:** Credit, counterparty credit, concentration, market
- **Criticality: 2.** The total exposure figure is computable without the geography tag. But the figure cannot be sliced by country or region, which means country concentration reports cannot be produced, cross-border risk cannot be measured, and the ¶50 example query cannot be answered. The aggregate exists but the required geographic decomposition is absent.
- **Driven by:** Principle 4 (¶41, header) — *"Data should be available by … region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries … across all business lines and geographic areas"*; Principle 8 (¶57) — country as a component of credit risk reporting.
- **Search terms:** country code, country of risk, country of domicile, counterparty country, booking location country, region code, jurisdiction, ISO country code, geographic segment
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a populated country or region code | count and percentage of records with null or missing geography field | threshold: zero — a record with no geography cannot be included in any country or regional aggregate; missing geography is a direct barrier to the ¶50 capability | **(¶43)**
  - *validity* — Every country code value conforms to the agreed reference list (e.g., ISO 3166-1) or the bank's internal country taxonomy | count of records carrying country codes not present in the reference list | threshold: zero — non-standard codes cannot be consistently aggregated across systems; they fall into an unmeasured "other" bucket | **(¶40)**
  - *consistency* — The country assigned to a counterparty in the risk system matches the country assigned to the same counterparty in the finance and reference data system | count of counterparties where country of domicile differs between systems | threshold: zero for structural mismatches (different continents); materiality applied for disputed or dual-domicile cases under documented governance | **(¶33)**

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The economic sector or industry classification of the counterparty or underlying exposure — for example, using a standard taxonomy such as NACE, GICS, or SIC — that enables concentration analysis by type of economic activity.
- **Why critical:** Principle 4 names industry as a mandatory aggregation dimension. Principle 8 (¶57) names industry sector as a required component of credit risk reporting alongside single name and country. Principle 6 (¶50) requires the bank to be able to aggregate industry credit exposures as of a specified date across all business lines and geographies. Without a consistent industry classification, sector concentration cannot be measured, and the reporting capability mandated by ¶50 cannot be demonstrated.
- **Risk types:** Credit, concentration
- **Criticality: 2.** The total credit exposure figure is computable without industry. But the figure cannot be decomposed into sector concentrations, which means the bank cannot identify an emerging sectoral concentration (e.g., over-exposure to commercial real estate), cannot produce the sector component of credit risk reports required by ¶57, and cannot respond to the ¶50 ad hoc scenario. The aggregate is present but the mandated sectoral slicing is absent.
- **Driven by:** Principle 4 (¶41, header) — *"Data should be available by … industry"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (¶57) — *"country and industry sector for credit risk."*

  *Note on the split with Principle 8:* The industry sector field is a CDE because its presence or absence affects whether the ¶50 aggregation can be run at all. The report-level obligations in Principle 8 — what analysis is presented, how concentrations are interpreted, what recommendations accompany the data — remain outside catalog scope. Both apply; they address different layers.

- **Search terms:** industry code, sector code, industry classification, NACE code, GICS sector, SIC code, industry segment, counterparty sector, obligor industry
- **Data quality requirements:**
  - *completeness* — Every material credit exposure record carries a populated industry/sector code | count and percentage of credit exposure records with null or missing sector code | threshold: zero for wholesale/corporate exposures where the obligor is individually identifiable; for retail portfolios, coverage should be materially complete with exceptions documented per ¶43 | **(¶43)**
  - *validity* — Every sector code draws from the bank's approved industry taxonomy (or an agreed external standard) | count of records carrying sector codes not in the approved reference list | threshold: zero — an unrecognised sector code cannot be aggregated under any defined industry bucket | **(¶40)**
  - *consistency* — The sector classification assigned to a counterparty is the same across all systems in which that counterparty appears | count of counterparties where the industry code differs across the lending system, the trading system, and the counterparty master | threshold: zero — a counterparty cannot simultaneously belong to two different sectors; conflicting codes must be resolved in the counterparty master | **(¶33)**

---

**CDE-08 — Position / As-of Date**

- **Definition:** The date as of which an exposure, position, or risk figure is stated — the temporal anchor of every risk aggregate. This is the field that identifies whether a record belongs to end-of-day, month-end, quarter-end, or a specific intraday snapshot.
- **Why critical:** Every aggregated risk figure is a sum over a defined population of records as of a specific point in time. If position dates are missing, ambiguous, or inconsistent, records from different dates will be mixed into the same aggregate — producing a figure that is neither point-in-time nor period-average, but an arbitrary blend. The bank cannot then state "this is our credit exposure as of date X" with confidence, which undermines every reporting principle and the ¶50 requirement to produce figures "as of a specified date."
- **Risk types:** Cross-cutting (applies to all risk types)
- **Criticality: 3.** Without an accurate and consistent position date, the aggregate risk figure for a given reporting date cannot be produced correctly — records from the wrong snapshot are included or excluded, and the resulting figure cannot be stated as of any specific date. This is not a precision degradation; it is an inability to produce a temporally defined aggregate, which is the fundamental form of every risk report. An undated or wrongly dated aggregate is not a compliant risk figure.
- **Driven by:** Principle 5 (¶44) — *"produce aggregate risk information on a timely basis"*; Principle 5 (¶45) — *"producing aggregated risk data rapidly during times of stress/crisis"*, which presupposes that each snapshot is correctly date-stamped; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"* — the "as of a specified date" clause is only satisfiable if records carry an accurate position date.
- **Search terms:** position date, as-of date, reporting date, value date, trade date, effective date, snapshot date, reference date, run date, cut-off date
- **Data quality requirements:**
  - *completeness* — Every exposure and position record carries a non-null position date | count and percentage of records with a null or missing position date | threshold: zero — a record without a position date cannot be assigned to any reporting period and is excluded from all time-specific aggregations | **(¶43)**
  - *accuracy* — The position date on each record matches the actual cut-off date of the source system snapshot from which it was extracted | count of records where the position date is inconsistent with the known extraction timestamp of the source feed | threshold: zero for systematic offsets (e.g., all records in a batch dated one day early); individual discrepancies reviewed against materiality | **(¶40)**
  - *timeliness* — Risk data for a given position date is available in the aggregation layer within the timeframe required by the bank's frequency policy, and within the accelerated timescale required for stress/crisis reporting | elapsed time between position date cut-off and data availability in the risk aggregation layer, measured per risk type | threshold: set by the bank's frequency policy per ¶47; for critical risks (credit large exposures, counterparty, trading, liquidity), the stress/crisis threshold is materially shorter than the normal-cycle threshold | **(¶44–47)**

---

**CDE-09 — General Ledger / System-of-Record Reconciliation Key**

- **Definition:** The identifier — typically a transaction reference, account number, or instrument identifier — that links a risk data record back to the corresponding entry in the general ledger or the authoritative source system of record for that instrument. This is the key that makes reconciliation between risk data and accounting data possible.
- **Why critical:** Paragraph 36(c) directly mandates reconciliation of risk data to accounting data. Without a field that ties each risk record to its counterpart in the GL or source system, reconciliation is impossible in a systematic, auditable way. The bank can assert that its risk figures are accurate, but it cannot evidence that assertion. Under the regulation, an unverifiable figure is not a compliant one — accuracy must be demonstrated, not claimed.
- **Risk types:** Cross-cutting (the reconciliation obligation applies to all risk types)
- **Criticality: 3.** Without the GL reconciliation key, the aggregate risk figure cannot be reconciled to the system of record at all — reconciliation degrades to a manual, sample-based comparison with no systematic coverage. Per ¶36(c), reconciliation to accounting sources is a mandatory control; a figure that cannot be systematically reconciled is unverifiable, which under the regulation is equivalent to an unproducible figure. This is the element that converts an assertion of accuracy into an evidenced one.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (¶36(d)) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** GL account reference, journal entry ID, transaction reference number, instrument ID, account identifier, source transaction key, accounting entry reference, ledger reconciliation key, source system ID, deal reference
- **Data quality requirements:**
  - *completeness* — Every risk record carries a non-null reconciliation key that links it to the GL or source system | count and percentage of risk records with null or missing reconciliation key | threshold: zero — a risk record without a reconciliation key cannot be verified against the accounting record; its accuracy cannot be evidenced regardless of the figure it shows | **(¶36(c))**
  - *validity* — Every reconciliation key present on a risk record resolves to an active record in the GL or designated source system | count of risk records carrying a key that returns no match in the GL | threshold: zero — an unresolvable key is functionally equivalent to no key; the record exists in risk data but has no accountable counterpart | **(¶36(c), ¶40)**
  - *consistency* — The exposure amount on the risk record agrees with the corresponding balance in the GL or source system, within materiality | count and aggregate monetary value of reconciliation breaks where the risk-side amount differs from the GL-side amount by more than the materiality threshold | threshold: set by materiality per ¶56 — the bank's risk-finance reconciliation team defines the threshold; the basis is whether the discrepancy could influence a risk decision; zero is not appropriate here because timing differences and approved valuation adjustments create acceptable differences | **(¶36(c), ¶56)**

---

**CDE-10 — Source System / Provenance Flag**

- **Definition:** The metadata field or set of fields that identifies the originating system from which a risk record was sourced — and, critically, flags whether the record entered the risk data chain through an automated feed or through a manual process, end-user computing (EUC) tool, or spreadsheet. This is the lineage marker that makes the distinction between trusted automated data and manually handled data visible.
- **Why critical:** Paragraphs 36(b) and 39 directly address the risk posed by manual processes and end-user computing. A bank cannot manage this risk if it cannot see, at the data level, which records were produced by manual or EUC processes. Aggregates that mix automated and manual data without flagging the manual proportion cannot be assessed for the reliability that Principle 3 requires. The provenance flag also supports the documentation of all aggregation processes required by ¶39, and the lineage tracking that data governance (¶34) demands.
- **Risk types:** Cross-cutting (the provenance risk is not confined to one risk type)
- **Criticality: 2.** The aggregate figure is still producible whether or not provenance is flagged — the numbers will sum regardless. But the figure cannot be assessed for reliability: the bank cannot tell what proportion of the aggregate came from controlled automated sources versus manual processes, cannot apply the differentiated controls ¶36(b) requires, and cannot produce the documentation ¶39 mandates. The aggregate is present but the bank cannot evidence its quality or explain its provenance to a supervisor.
- **Driven by:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications … it should have effective mitigants in place … and other effective controls that are consistently applied"*; Principle 3 (¶36(d)) — single authoritative source; Principle 3 (¶39) — *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual."*
- **Search terms:** source system, source system name, feed type, data source, originating system, manual input flag, EUC flag, end-user computing flag, spreadsheet flag, data lineage, upstream system, automated vs manual indicator
- **Data quality requirements:**
  - *completeness* — Every risk record carries a populated source system identifier and a manual/automated process flag | count and percentage of records with null or missing source system identifier or process flag | threshold: zero — a record with no provenance information cannot be assessed for the controls applicable to it; it is ungovernable | **(¶39, ¶43)**
  - *validity* — Every source system identifier resolves to a system registered in the bank's approved data source inventory | count of records carrying source system codes not in the registered inventory | threshold: zero — an unregistered source means the data entered the risk aggregation layer through a channel not subject to the bank's governance framework; this is a control gap, not a data quality tolerance | **(¶40)**
  - *accuracy* — Records flagged as manually sourced carry the expected supplementary documentation (owner, justification, review date) per the bank's EUC policy | count of manually flagged records without complete EUC documentation | threshold: zero — the regulation explicitly requires documentation and mitigation for manual processes; an undocumented manual record has no evidenced controls | **(¶36(b), ¶39)**

---

**CDE-11 — Collateral / Credit Risk Mitigant Identifier**

- **Definition:** The identifier that links an exposure record to any associated collateral, guarantee, netting agreement, or other credit risk mitigant — enabling the calculation of net exposure after recognised mitigation. This is the element that enables the distinction between gross and net exposure in credit risk reporting.
- **Why critical:** Principle 4 requires capture of all material risk exposures, including off-balance-sheet items. Gross exposure alone overstates the economic risk where collateral or guarantees reduce it; net exposure alone understates the gross commitment. Both figures are required for complete risk reporting. Without the mitigant linkage, the bank cannot compute net exposure, cannot assess collateral coverage, and cannot produce the concentrations on a net basis that boards and supervisors require. The mitigant identifier is also a joining key — without it, the collateral management system cannot be linked to the credit risk system.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 2.** Gross exposure remains computable without the mitigant link. But net exposure — the figure used for limit monitoring, capital calculation, and concentration reporting on a net basis — cannot be derived. The gross figure is produced but the net figure, which materially affects credit risk decisions, cannot be computed. This is a degradation of a specific and important figure, not a total failure of aggregation.
- **Driven by:** Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 8 (¶58) — *"Reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance"* (limits are typically applied on a net basis).
- **Search terms:** collateral ID, collateral agreement reference, netting set ID, guarantee reference, credit mitigant identifier, security interest ID, ISDA agreement reference, collateral pool ID, lien reference, CRM identifier
- **Data quality requirements:**
  - *completeness* — Every exposure record subject to a collateral or netting agreement carries a populated mitigant identifier; exposures confirmed as uncollateralised carry a specific "no mitigant" indicator rather than a null | count of exposure records that are expected to carry mitigant linkage (based on product type) but have a null mitigant field; count of records with unexplained nulls | threshold: zero for nulls — a null is ambiguous between "no mitigant" and "mitigant not linked"; that ambiguity means net exposure cannot be computed reliably | **(¶43)**
  - *validity* — Every mitigant identifier on an exposure record resolves to an active record in the collateral management system | count of exposure records carrying a mitigant ID that returns no match in the collateral system | threshold: zero — an unresolvable mitigant ID means the exposure is treated as uncollateralised in any net exposure calculation, overstating the net figure | **(¶40)**
  - *accuracy* — The collateral value and eligibility status linked to an exposure record reflect the current valuation and legal enforceability assessment | count of exposure records linked to collateral records whose valuation date is older than the bank's refresh cycle, and count linked to collateral records whose eligibility status has changed but not been updated | threshold: set by materiality per ¶56 — stale collateral valuations are unavoidable for illiquid collateral; the bank defines a maximum age and flags exceptions for review | **(¶40, ¶56)**

---

**CDE-12 — Limit / Risk Appetite Threshold**

- **Definition:** The approved quantitative threshold — credit limit, market risk limit, concentration limit, or liquidity limit — against which an exposure or risk measure is compared in order to determine whether the bank is operating within its risk appetite. This is not itself an exposure measure but the reference value that gives exposure figures their decision-making context.
- **Why critical:** Principle 8 (¶58) requires that risk reports provide information "in the context of limits and risk appetite/tolerance." Without a linkable limit value, an exposure figure cannot be evaluated — the board and senior management cannot determine whether the bank is within appetite simply by looking at a gross number. The limit is the reference frame that converts a raw figure into a risk management signal. It also enables the automated edit and reasonableness checks required by ¶53(b).
- **Risk types:** Credit, market, liquidity, counterparty, concentration, cross-cutting
- **Criticality: 2.** The raw exposure aggregate is computable without the limit. But the figure cannot be contextualised against the bank's risk appetite, and the reasonableness checks required by ¶53(b) cannot be automated. The aggregate is produced but management cannot tell whether it represents a breach, an approach to a limit, or comfortable headroom. The reporting purpose of the figure is degraded.
- **Driven by:** Principle 8 (¶58) — *"Reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance and propose recommendations for action where appropriate"*; Principle 7 (¶53(b)) — *"Automated and manual edit and reasonableness checks, including an inventory of the validation rules."*
- **Search terms:** credit limit, risk limit, exposure limit, concentration limit, risk appetite threshold, approved limit, limit amount, limit utilisation, risk tolerance, counterparty limit, position limit, large exposure threshold
- **Data quality requirements:**
  - *accuracy* — The limit value attributed to a counterparty, portfolio, or risk dimension reflects the most recently approved board or senior management decision | count of limit records where the effective date is prior to the most recent approval record in the limit governance system | threshold: zero — an outdated limit means utilisation calculations compare current exposure to a superseded threshold; a limit breach may go undetected | **(¶40)**
  - *completeness* — Every material exposure dimension for which a limit has been set carries a linked limit value in the risk reporting system | count of counterparties, portfolios, or dimensions where exposure data exists but no corresponding approved limit is linked | threshold: zero for dimensions the board has explicitly mandated limits for; gaps require documented escalation | **(¶43, ¶58)**
  - *timeliness* — Limit updates approved by the board or senior management are reflected in the risk reporting system within the bank's governance-defined update cycle | elapsed time between limit approval date and effective date in the risk system | threshold: set by the bank's limit governance policy; limit updates for critical exposures should be effective within one business day; the basis is that a stale limit is operationally equivalent to no limit for the period it is wrong | **(¶44–47)**

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Group-Wide Counterparty Consolidation: Single Obligor Reconciliation**

- **Spans:** CDE-01 (Counterparty Identifier), CDE-02 (Legal Entity), CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key)
- **Rule intent:** The bank must be able to demonstrate, across all booking entities and source systems simultaneously, that every distinct real-world counterparty is represented by exactly one identifier in the enterprise — and that the sum of all exposure records carrying that identifier equals the total exposure to that counterparty that would be produced by a manual reconciliation of the underlying source systems. This cannot be verified by checking any single element in isolation: it requires matching CDE-01 across systems, summing CDE-03 per matched entity, and confirming that sum against the GL via CDE-09.
- **Why cross-cutting:** Any single-element check (e.g., "CDE-01 is non-null") passes even when the same counterparty exists under two different identifiers in two different systems. The consolidation failure is invisible at the element level and only detectable by a cross-system join on stable attributes (LEI, name-and-jurisdiction).
- **Measurement:** Identify counterparties that appear under more than one identifier across the enterprise by matching on legal entity identifier (LEI) or name-and-domicile combination; count the number of such split counterparties; compute the sum of exposures attributable to the secondary identifiers that would be excluded from a query against only the primary identifier. Report as both a count of affected counterparties and as a monetary amount of potentially mis-aggregated exposure.
- **Threshold and basis:** Zero for count of counterparties with unresolved duplicate identifiers — a split obligor always produces an incorrect concentration figure; there is no materiality floor for an identity error. The monetary exposure associated with the split is additionally reported against a materiality threshold set by the bank's large-exposure policy (typically a percentage of regulatory capital), per ¶56, to prioritise remediation.
- **Paragraph citations:** ¶33 — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties"*; ¶36(c) — reconciliation to source systems; ¶40 — measure and monitor accuracy; ¶43 — measure and monitor completeness.

---

**XDQ-02 — Risk-to-Finance Reconciliation: Aggregate Balance Confirmation**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key), CDE-08 (Position/As-of Date), CDE-02 (Legal Entity Identifier)
- **Rule intent:** The bank must be able to demonstrate, at each reporting date, that the total risk exposure aggregated from the risk data layer agrees with the total balance recorded in the general ledger for the same population of instruments, booking entities, and date — within the materiality threshold established under ¶56. This reconciliation cannot be executed by monitoring any single element: it requires joining the risk aggregate (built from CDE-03, filtered by CDE-08, grouped by CDE-02) to the GL total via CDE-09, and computing the break. The break must then be assessed against materiality and either explained or escalated.
- **Why cross-cutting:** The individual element-level checks (CDE-03 non-null, CDE-09 resolvable) confirm that each record is well-formed. They do not confirm that the sum of all risk records equals the sum in the GL. A systematic offset — for example, off-balance-sheet exposures included in risk but excluded from the GL query, or a currency conversion difference — would pass all element-level checks but fail the aggregate reconciliation. Only the cross-element check catches it.
- **Measurement:** For each risk type and legal entity combination, compute (a) the total exposure in the risk aggregation layer as of the reporting date, and (b) the total balance in the GL for the same scope and date. Report the absolute and percentage difference. Separately report the count and value of individual risk records that have no matching GL entry (via CDE-09), and the count and value of GL entries with no corresponding risk record.
- **Threshold and basis:** The aggregate break threshold is set by materiality per ¶56: the bank's risk-finance governance team defines the monetary and percentage tolerance, anchored to the principle that a discrepancy is material if it could influence a risk decision. Unmatched records (orphan risk records or orphan GL entries) are reported separately at a zero tolerance for records above a monetary de minimis; below de minimis, exceptions are documented.
- **Paragraph citations:** ¶36(c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; ¶53(a) — *"Defined requirements and processes to reconcile reports to risk data"*; ¶40 — measure and monitor accuracy; ¶56 — materiality analogy for accuracy requirements.

---

**XDQ-03 — Manual and EUC Exposure Concentration: Provenance-Weighted Reliability Assessment**

- **Spans:** CDE-10 (Source System / Provenance Flag), CDE-03 (Gross Exposure Amount), CDE-04 (Risk Type Classification), CDE-05 (Business Line)
- **Rule intent:** The bank must be able to determine, for any given risk aggregate (total credit exposure by business line, total trading exposure by risk type, etc.), what proportion of the monetary amount was sourced from manual or EUC processes rather than from controlled automated feeds. This cannot be done at the element level: it requires joining the provenance flag (CDE-10) to the exposure amount (CDE-03) and computing the manual share by risk type (CDE-04) and business line (CDE-05). The result is a "manual exposure ratio" for each reporting segment, which is the measurable indicator of the reliability risk that ¶36(b) and ¶39 require to be managed.
- **Why cross-cutting:** A check on CDE-10 alone tells you whether provenance is flagged — not whether the manual proportion of a given aggregate is acceptable. The risk the regulation is concerned with is that a material part of an aggregate could be wrong because it passed through an uncontrolled manual step. That risk is only quantifiable by weighting provenance against the exposure amount across the aggregation dimensions.
- **Measurement:** For each combination of risk type and business line, compute the sum of exposure amounts sourced from manual or EUC processes as a percentage of total exposure in that segment. Report as a heat map of manual exposure ratios by segment. Separately report the count of manual-flagged records without complete EUC documentation (owner, review date, justification).
- **Threshold and basis:** The manual exposure ratio threshold is set by the bank's risk data governance policy, not by the regulation — BCBS 239 requires management and mitigation, not elimination, of manual processes. The bank's senior management establishes a target maximum manual ratio per segment (e.g., no more than 5% of a given aggregate sourced from EUC without enhanced controls). Any segment exceeding the threshold triggers a review per ¶39's documentation requirement. Undocumented manual records are reported at zero tolerance: each one represents an unmitigated control gap.
- **Paragraph citations:** ¶36(b) — effective mitigants for manual processes and EUC; ¶39 — *"document and explain all of their risk data aggregation processes whether automated or manual"*; ¶40 — measure and monitor accuracy.

---

## 4. Out of Scope

The following obligations from Principles 1–11 are not addressable by a CDE register or data quality monitoring programme. Stating this plainly defines the boundary of what the catalog delivers and prevents compliance theatre — asserting coverage where none exists.

---

**Principle 1 — Governance (¶27–31): Board and senior management accountability**

The catalog can record data ownership (¶34), document CDE definitions (¶37), and evidence that monitoring is occurring. It cannot constitute, replace, or verify: the board's formal approval of the aggregation framework (¶28); the independent validation programme (¶29(a)); due diligence on acquisitions (¶29(b)); senior management's understanding of aggregation limitations (¶30); or the board's awareness of implementation status (¶31). These are organisational governance obligations. They require board minutes, internal audit engagement, validation reports, and committee structures — artefacts that exist outside any data catalog.

---

**Principle 2 — Data Architecture and IT Infrastructure (¶32–35): System design and business continuity**

CDE-01 and CDE-02 are directly driven by ¶33's requirement for single identifiers — that connection is made explicit above. What the catalog cannot deliver: the design and build of integrated IT infrastructure (¶32); business continuity planning for risk data processes (¶32); the assignment and enforcement of data ownership roles (¶34); or the adequacy of controls across the data lifecycle (¶34). A catalog can document roles and flag ownership gaps; it cannot enforce that those roles perform their control obligations.

---

**Principle 3 — Accuracy and Integrity (¶36–40): End-to-end automated controls**

The CDE register and DQ monitoring cover the data-level dimensions of ¶36(c) (reconciliation key), ¶36(d) (source system), and ¶40 (measurement and monitoring). What the catalog cannot deliver: the engineering of automated aggregation pipelines (¶36, ¶38); the remediation of manual processes (¶36(b)); the escalation channels and action plans for poor quality (¶40) — those require process ownership and operational response workflows, not metadata; and the independent validation of aggregation processes (¶29(a)). The catalog surfaces the problem; the organisation must act on it.

---

**Principle 5 — Timeliness (¶44–47): System latency and stress-mode capabilities**

CDE-08 (Position Date) carries a timeliness DQ check, measuring elapsed time between cut-off and availability. That check monitors whether data arrives on time; it does not build or operate the systems that determine how fast data can flow. The capability to produce intraday liquidity and trading position data during a crisis (¶46, ¶47) is a systems architecture and operational design problem. Documenting that a bank has failed the timeliness check is useful; fixing it requires infrastructure investment that the catalog cannot make.

---

**Principle 6 — Adaptability (¶48–51): Ad hoc query capability**

CDE-05, CDE-06, CDE-07, and CDE-08 are driven in part by the ¶50 example, which requires the ability to aggregate country and industry credit exposures as of a specified date across all business lines. Those elements support the query when it is run. What the catalog cannot provide: the flexible aggregation engine (¶49(a)), the drill-down capability (¶49(b)), the ability to incorporate new organisational structures or regulatory changes quickly (¶49(c, d)), or the actual execution of stress test scenarios (¶48). The catalog ensures the necessary data elements are governed; it does not perform the aggregation.

---

**Principle 7 — Accuracy of Reports (¶52–56): Report reconciliation processes**

CDE-09 and XDQ-02 address the data-level enablement of report-to-source reconciliation. What the catalog cannot deliver: the defined reconciliation processes themselves (¶53(a)); the inventory and operation of validation rules applied to reports (¶53(b)); the exception reporting and explanation workflows for data errors (¶53(c)); or senior management's establishment of accuracy and precision requirements (¶55). These are process and governance obligations. The catalog provides the keys and quality signals that make reconciliation possible; the reconciliation processes are owned and run by the risk-finance function.

---

**Principle 8 — Comprehensiveness (¶57–60): Report scope and forward-looking content**

CDE-04, CDE-07, and CDE-12 are driven by Principle 8 insofar as industry sector, risk type, and limits are required report dimensions or reference data for report content. This is stated explicitly in the entries for CDE-07 and CDE-12. What Principle 8 requires beyond these data elements cannot be addressed by catalog governance: the determination that all significant risk areas are covered in reports (¶57); the identification and reporting of emerging concentrations (¶58); risk appetite and limit monitoring as a reporting practice (¶58); forward-looking forecasts and stress test results in reports (¶60); and capital adequacy and regulatory capital reporting (¶59). These are report design, risk methodology, and board governance obligations.

---

**Principle 9 — Clarity and Usefulness (¶61–69): Report design, interpretation, and recipient feedback**

Nothing in Principle 9 is addressable by a CDE register. The obligation to produce meaningful, tailored reports (¶61–62); to match the level of qualitative versus quantitative content to the recipient (¶62–65); to confirm periodically with recipients that the information is relevant (¶69); and to develop an inventory of risk data items with conceptual references (¶67) — these are report authorship, stakeholder management, and governance process obligations. Paragraph 67's inventory of risk data items is conceptually adjacent to a data catalog, but the regulation frames it as a risk reporting tool for recipients, not a data quality governance tool. A catalog entry could inform such an inventory but cannot substitute for the report-level classification work.

---

**Principles 10 and 11 — Frequency and Distribution (¶70–74): Report scheduling and access control**

These principles concern how often reports are produced and to whom they are sent. No CDE or DQ monitoring rule addresses report scheduling, distribution lists, confidentiality controls, or the periodic confirmation that the right people are receiving reports on time (¶73). These are operational reporting infrastructure and access governance matters. CDE-08's timeliness check confirms that underlying data is available promptly — a necessary but not sufficient condition for meeting Principle 10.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | **3** | P2 (¶33), P4 (¶41), P5 (¶46b) | uniqueness, completeness, validity, consistency |
| CDE-02 | Legal Entity Identifier (Own Booking Entity) | **3** | P2 (¶33), P4 (¶41) | completeness, validity, consistency |
| CDE-03 | Gross Exposure Amount | **3** | P3 (¶36a), P4 (¶41), P7 (¶52) | accuracy, completeness, validity |
| CDE-04 | Risk Type Classification | **2** | P4 (¶41), P8 (¶57), P2 (¶33) | validity, completeness, consistency |
| CDE-05 | Business Line | **2** | P4 (¶41 header), P6 (¶50) | completeness, validity, consistency |
| CDE-06 | Geography / Country | **2** | P4 (¶41 header), P6 (¶50), P8 (¶57) | completeness, validity, consistency |
| CDE-07 | Industry / Sector Classification | **2** | P4 (¶41 header), P6 (¶50), P8 (¶57) | completeness, validity, consistency |
| CDE-08 | Position / As-of Date | **3** | P5 (¶44–47), P6 (¶50) | completeness, accuracy, timeliness |
| CDE-09 | GL / System-of-Record Reconciliation Key | **3** | P3 (¶36c, ¶36d), P7 (¶53a) | completeness, validity, consistency |
| CDE-10 | Source System / Provenance Flag | **2** | P3 (¶36b, ¶36d, ¶39) | completeness, validity, accuracy |
| CDE-11 | Collateral / Credit Risk Mitigant Identifier | **2** | P4 (¶41), P8 (¶58) | completeness, validity, accuracy |
| CDE-12 | Limit / Risk Appetite Threshold | **2** | P8 (¶58), P7 (¶53b) | accuracy, completeness, timeliness |
| **XDQ-01** | Group-Wide Counterparty Consolidation | — cross-cutting — | P2 (¶33), P3 (¶36c), P4 (¶40, ¶43) | uniqueness, completeness, accuracy |
| **XDQ-02** | Risk-to-Finance Aggregate Reconciliation | — cross-cutting — | P3 (¶36c), P7 (¶53a), P3 (¶40), P7 (¶56) | consistency, accuracy, completeness |
| **XDQ-03** | Manual/EUC Exposure Concentration Assessment | — cross-cutting — | P3 (¶36b, ¶39), P3 (¶40) | completeness, validity, accuracy |

*Criticality 3 count: CDE-01, CDE-02, CDE-03, CDE-08, CDE-09 — five elements. All five satisfy the step-2 sentence: the aggregate either cannot be computed or cannot be reconciled to the system of record without them. No element rated 1 appears in this register; nothing in the analysis reduces to supporting context whose absence leaves all aggregates intact.*