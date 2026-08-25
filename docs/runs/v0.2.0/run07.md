# BCBS 239 â Data Catalog Governance Analysis

---

## 1. Objectives and scope

**What the regulation is trying to achieve**

- **Reliable aggregation of risk data across the group, including under stress.** Banks must capture *all* material risk exposures â including off-balance-sheet â and aggregate them by business line, legal entity, asset type, industry, and region (Â¶41â43). The failure point BCBS 239 targets is a bank that cannot produce a consolidated group-wide exposure figure quickly enough to act on it during a crisis.

- **A single authoritative source per risk type, with reconciliation to accounting data.** Â¶36(c)â(d) require that risk data be reconciled with source systems including the general ledger, and that banks strive toward one authoritative source per risk type. Fragmentation across siloed systems â each producing different numbers â is explicitly the problem being solved.

- **Documented, validated, largely automated data flows.** Â¶36â39 require that all aggregation processes, whether automated or manual, be documented; that manual workarounds be explained and their criticality assessed; and that accuracy be measured and monitored with escalation channels in place (Â¶40).

- **Integrated data taxonomy and architecture, including metadata.** Â¶33 requires banks to establish "integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts." This paragraph is the closest thing in the regulation to a direct mandate for a data catalog.

- **A data dictionary as a precondition for accurate aggregation.** Â¶37 states that "a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation." Without consistent definitions, the same field populated in two systems may mean different things, making aggregation unreliable even when both values are individually accurate.

- **Board and senior management accountability for known limitations.** Â¶30â31 require senior management to be "fully aware of and understand the limitations that prevent full risk data aggregation" â coverage gaps, technical constraints, legal impediments to cross-border data sharing â and to ensure the IT strategy addresses them. The catalog's role here is to make those limitations visible and documented, not to eliminate them.

**Who it applies to**

The principles are directed at **Global Systemically Important Banks (G-SIBs)**, with the expectation that national supervisors will apply them proportionately to Domestic Systemically Important Banks (D-SIBs). The obligations fall on the bank as a whole â board, senior management, risk, finance, and IT functions â across the entire **banking group**, meaning consolidated subsidiaries and legal entities, not just the parent.

---

## 2. Critical Data Element candidates

---

**CDE-01 â Counterparty Unique Identifier**

- **Definition:** A persistent, system-independent identifier that resolves to a single legal counterparty across all booking systems, risk engines, and data sources within the banking group. Where possible, this should align to an external standard (e.g., Legal Entity Identifier).
- **Why critical:** Without a single resolved identifier, exposure records from different systems cannot be summed to produce a group counterparty exposure. Two systems holding the same borrower under different local codes produce double-counts or omissions when aggregated. This is not a degradation of an aggregate â it is a failure of the aggregate to exist in a trustworthy form.
- **Risk types:** Credit, counterparty credit risk, concentration
- **Criticality: 3.** Aggregation of counterparty exposure across systems is *impossible* without a common identifier. Any aggregate produced without it is unverifiable and may be materially wrong.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶41) â *"risk data aggregation capabilities should include all material risk exposures"*; Principle 5 (Â¶46a) â *"the aggregated credit exposure to a large corporate borrower"* named as a critical risk requiring rapid aggregation.
- **Search terms:** counterparty ID, counterparty key, party identifier, LEI, obligor ID, customer master ID, entity reference, golden record counterparty
- **Data quality requirements:**
  - *Uniqueness* â Each counterparty is represented by exactly one active identifier in the counterparty master; no two records resolve to the same real-world entity under different IDs | Count of duplicate counterparty identifiers or records mapping to the same entity under distinct IDs | Target: zero duplicates in the authoritative master
  - *Completeness* â Every exposure record carries a populated, non-null counterparty identifier | Count of exposure records with null or blank counterparty identifier | Target: 0% null rate
  - *Validity* â Every counterparty identifier on an exposure record resolves to an active record in the counterparty master | Count of exposure records whose counterparty identifier has no matching record in the master | Target: 0% unmatched rate; any non-zero value requires immediate escalation
  - *Consistency* â The same counterparty is identified by the same identifier across credit, market, and liquidity risk systems | Count of counterparty identifiers that appear in one risk system but cannot be matched to the same entity in another | Measured per system pair at each aggregation run

---

**CDE-02 â Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier for the bank's own legal entity in which a position or exposure is booked â distinct from the counterparty identifier. Represents a node in the bank's own group structure (parent, subsidiary, branch).
- **Why critical:** Group consolidation requires summing exposures across booking entities. If a booking entity code is missing, mis-coded, or inconsistent across systems, exposures attributed to that entity cannot be included in or excluded from consolidated group aggregates. It is also required to produce subsidiary-level standalone reports and to respect legal impediments to cross-border data sharing (Â¶30).
- **Risk types:** Cross-cutting (all risk types require this for group consolidation)
- **Criticality: 3.** Group-level aggregation is impossible without knowing which legal entity owns each position. A missing or incorrect booking entity invalidates the exposure's assignment to the group structure, rendering it either omitted from or double-counted in consolidation.
- **Driven by:** Principle 2 (Â¶33) â *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (Â¶41â43) â completeness requires capturing exposures across the banking group; Principle 1 (Â¶30) â senior management must understand limitations including "subsidiaries not included."
- **Search terms:** legal entity code, booking entity, entity ID, subsidiary code, branch code, group entity hierarchy, consolidation unit, reporting entity
- **Data quality requirements:**
  - *Validity* â Every booking entity code on a position or exposure record must resolve to an active node in the official group legal entity hierarchy | Count of records with a booking entity code not present in the approved entity hierarchy | Target: 0%
  - *Completeness* â No position or exposure record may have a null or placeholder booking entity | Count of records with null, blank, or "unknown" booking entity | Target: 0%
  - *Consistency* â The same legal entity is represented by the same code across all risk, finance, and regulatory reporting systems | Cross-system comparison of entity code populations; count of entities present in one system but absent or differently coded in another | Measured at each consolidation cycle

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary measure of a bank's risk exposure to a counterparty or instrument before the application of credit risk mitigants such as collateral, netting agreements, or guarantees. Stated in the transaction currency of the position.
- **Why critical:** This is the primary input from which all credit risk aggregates â total group exposure, large exposure calculations, concentration measures â are constructed. It is also the figure reconciled against the general ledger to evidence accuracy (Â¶36c). No risk-weighted asset, concentration ratio, or limit utilisation figure can be produced without it.
- **Risk types:** Credit, counterparty credit risk, concentration
- **Criticality: 3.** If the gross exposure amount is missing, incorrect, or denominated in an unconverted currency, the aggregate risk figure is wrong. There is no fallback that preserves the validity of the aggregate.
- **Driven by:** Principle 3 (Â¶36a) â *"controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 3 (Â¶36c) â *"risk data should be reconciled with bank's sources, including accounting data"*; Principle 4 (Â¶41) â *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 7 (Â¶52) â reports must be "accurate and precise."
- **Search terms:** exposure amount, gross exposure, notional amount, outstanding balance, drawn balance, nominal exposure, face value, mark-to-market value, current exposure, potential future exposure
- **Data quality requirements:**
  - *Accuracy* â Exposure amounts must reconcile to the corresponding balances in the general ledger or system of record within an agreed tolerance | Sum of exposure amounts per booking entity and product type compared to general ledger balances; count and value of items outside tolerance | Target: reconciliation variance â¤ defined materiality threshold; all breaks investigated and resolved or explained
  - *Completeness* â Every exposure record carries a non-null, non-zero exposure amount (a zero amount is only valid if the position is genuinely flat and documented as such) | Count of exposure records with null or negative exposure amounts where the instrument type does not permit a negative balance | Target: 0% unexplained nulls
  - *Validity* â Exposure amounts fall within plausible bounds for the instrument type; amounts outside bounds are flagged for review | Count of records where exposure amount exceeds a defined instrument-type ceiling or is implausibly small | Threshold set per instrument type; all flagged items reviewed before inclusion in aggregation

---

**CDE-04 â Risk Type Classification**

- **Definition:** The classification that assigns an exposure or position to a defined risk category â at minimum: credit risk, market risk, liquidity risk, and operational risk. May include sub-classifications (e.g., counterparty credit risk, settlement risk).
- **Why critical:** Risk reports are structured by risk type. An exposure that is mis-classified or unclassified is aggregated into the wrong bucket, distorting both the category total and â by omission â at least one other category. Principle 8 (Â¶57) explicitly requires reports to cover "all significant risk areas," which presupposes that every exposure has been correctly assigned to one.
- **Risk types:** Cross-cutting (the classification itself spans all risk types)
- **Criticality: 2.** An unclassified or mis-classified exposure degrades the accuracy of the affected risk category's aggregate and may cause a concentration or limit breach to go undetected. The aggregate for other risk types is still produced, but the affected category is incomplete or inflated. Rated 2 rather than 3 because the overall group exposure total (before risk-type slicing) is not invalidated â only the slice is wrong.
- **Driven by:** Principle 4 (Â¶41â42) â aggregation must work regardless of the risk aggregation system chosen, and each system must make clear "the specific approach used to aggregate exposures for any given risk measure"; Principle 7 (Â¶52â53) â reports must be accurate and precise; Principle 8 (Â¶57) â *"reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*
- **Search terms:** risk type, risk category, risk class, risk classification, exposure classification, product risk type, risk bucket
- **Data quality requirements:**
  - *Validity* â Every exposure record carries a risk type code drawn from the approved risk taxonomy; codes outside the approved list are rejected | Count of records with risk type codes not present in the approved taxonomy | Target: 0%
  - *Completeness* â No exposure record has a null or "unclassified" risk type | Count of records with null or placeholder risk type code | Target: 0% in production; any exceptions require documented justification
  - *Consistency* â The same instrument or product type is classified to the same risk type across all booking systems | Cross-system comparison of risk type assignment for identical instrument types; count of instruments classified differently across systems | All discrepancies resolved before aggregation

---

**CDE-05 â Business Line**

- **Definition:** The internal organisational dimension that identifies which business unit or line of business originated or owns an exposure or position. Examples include retail banking, corporate banking, trading, transaction banking, wealth management.
- **Why critical:** Principle 4 explicitly requires risk data to be available "by business line." This is not an optional reporting slice â it is a named completeness requirement. Without it, the bank cannot produce business-line-level risk reports, cannot identify concentrations within a business segment, and cannot demonstrate that aggregation covers the entire group.
- **Risk types:** Cross-cutting
- **Criticality: 2.** The group-level aggregate can still be produced when a business line code is missing, but the mandatory business-line decomposition cannot be completed, and any concentration within that segment is invisible. Rated 2 because the top-level aggregate is not invalidated â the required slice is.
- **Driven by:** Principle 4 (Â¶41) â *"data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (Â¶50) â adaptability requires the ability to aggregate "across all business lines and geographic areas."
- **Search terms:** business line, line of business, business unit, LOB code, segment code, division, desk, product line, front office unit
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a populated business line code | Count of exposure records with null or blank business line | Target: â¤ 0.1% by count and value, with all exceptions documented
  - *Validity* â Business line codes resolve to an active entry in the approved organisational hierarchy | Count of records with business line codes not present in the approved hierarchy | Target: 0%
  - *Consistency* â Business line assignment is consistent across risk and finance systems for the same portfolio | Cross-system comparison of business line code distribution per booking entity | Discrepancy rate measured monthly; material discrepancies resolved before period-end aggregation

---

**CDE-06 â Country / Geographic Region**

- **Definition:** The country or geographic region associated with an exposure â which may be the country of the counterparty's domicile, the country of the collateral, or the country of the booking entity, depending on the risk measure. The specific definition must be documented and applied consistently.
- **Why critical:** Principle 4 names "region" as a mandatory aggregation dimension. Principle 6 (Â¶50) gives the explicit supervisory example of a bank being asked to "aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries." This is among the most frequently requested stress-scenario slices. Without a reliable country field, the bank cannot respond to a supervisor's ad-hoc request about a specific country's exposure â a direct failure of Principle 6.
- **Risk types:** Credit, counterparty credit risk, concentration, market
- **Criticality: 2.** Geographic aggregation fails or is incomplete when country is missing or inconsistently defined. The group aggregate is not invalidated, but the geographic slice â which the regulation explicitly requires â cannot be produced reliably. Rated 2.
- **Driven by:** Principle 4 (Â¶41) â data available by "region"; Principle 6 (Â¶50) â *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
- **Search terms:** country code, country of risk, country of domicile, geographic region, ISO country code, booking country, risk country, obligor country, collateral country
- **Data quality requirements:**
  - *Validity* â Country codes conform to an approved standard (e.g., ISO 3166-1 alpha-2 or alpha-3); non-conforming codes are flagged | Count of records with country codes not in the approved reference list | Target: 0%
  - *Completeness* â Every exposure record with a counterparty carries a populated country code | Count of exposure records with null or blank country code | Target: â¤ 0.1% by count and value; all exceptions documented
  - *Consistency* â The country of risk definition is applied identically across credit risk, market risk, and liquidity risk systems | Comparison of country code assignment for shared instruments across systems | All definitional inconsistencies documented in the data dictionary (Â¶37)

---

**CDE-07 â Industry / Sector Classification**

- **Definition:** The classification that assigns a counterparty or exposure to an economic industry sector, using a recognised taxonomy (e.g., GICS, NACE, SIC, or an internal equivalent mapped to one of these). Applied at the counterparty level and inherited by exposures.
- **Why critical:** Principle 4 names "industry" as a mandatory aggregation dimension alongside business line and region. Principle 8 (Â¶57) specifically names "industry sector for credit risk" as a required component of risk reports. Industry sector is also the primary lens through which sector concentration risk is monitored. Without it, the bank cannot identify an industry concentration before it becomes a crisis.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Industry-sector aggregation is required by name in the regulation. When sector classification is missing or inconsistent, the sector slice of the aggregate is incomplete or wrong, and concentration risk in that sector is undetectable. The group total is not invalidated. Rated 2.
- **Driven by:** Principle 4 (Â¶41) â data available by "industry"; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk."*
- **Search terms:** industry code, sector code, industry classification, GICS sector, NACE code, SIC code, counterparty industry, sector classification, obligor sector
- **Data quality requirements:**
  - *Validity* â Industry codes belong to the approved classification system; internal codes are mapped to the approved external taxonomy | Count of records with codes not present in the approved taxonomy | Target: 0%
  - *Completeness* â Every counterparty record carries a populated industry sector code, which propagates to associated exposures | Count of counterparty records with null sector code; count of exposure records whose counterparty has no sector classification | Target: â¤ 0.5% by count; all exceptions reviewed quarterly
  - *Consistency* â The same counterparty is assigned the same sector code in all systems that carry counterparty attributes | Cross-system comparison of sector code for shared counterparties | All discrepancies investigated before concentration reporting runs

---

**CDE-08 â Position / As-of Date**

- **Definition:** The date as of which an exposure, position, or risk measure is stated. This is the temporal reference that anchors every aggregate â not the trade date or settlement date, but the date the snapshot reflects.
- **Why critical:** Every aggregate risk figure is stated "as of" a specific date. Without a reliable as-of date, it is impossible to determine whether records from different systems refer to the same snapshot or to different points in time. Mixing records from different as-of dates in a single aggregate produces a figure that is neither accurate nor comparable over time. Principle 5 requires risk data to be "up-to-date" and aggregated on a timely basis; without a reliable position date this cannot be demonstrated.
- **Risk types:** Cross-cutting
- **Criticality: 3.** If position dates are missing, inconsistent, or incorrect across source systems, the aggregation run is mixing data from different points in time. The resulting aggregate is not degraded â it is wrong in a way that cannot be detected without this field. Rated 3.
- **Driven by:** Principle 5 (Â¶44â46) â *"produce aggregate risk information on a timely basis"* and the ability to produce aggregates rapidly under stress; Principle 6 (Â¶50) â ad-hoc requests explicitly specify "as of a specified date"; Principle 3 (Â¶36) â accuracy requires that all records in an aggregate refer to the same reference point.
- **Search terms:** as-of date, position date, valuation date, reporting date, snapshot date, trade date, reference date, data extraction date, close-of-business date
- **Data quality requirements:**
  - *Completeness* â Every exposure and position record carries a non-null as-of date | Count of records with null position date | Target: 0%; null position dates block inclusion in any aggregation run
  - *Validity* â As-of dates are not in the future, not prior to the instrument's inception date, and fall within the expected reporting cycle | Count of records with as-of dates outside valid bounds | Target: 0% out-of-bounds; automated rejection before aggregation
  - *Timeliness* â The lag between the as-of date and the availability of a complete aggregated dataset meets the bank's defined SLAs for normal and stress reporting | Measured as calendar hours/days between the as-of date and the timestamp of a complete, validated aggregated file | Tracked per reporting cycle; breaches escalated per Â¶40
  - *Consistency* â All records included in a single aggregation run share the same as-of date | Count of records in an aggregation batch with a position date that differs from the declared batch as-of date | Target: 0%

---

**CDE-09 â General Ledger Reconciliation Key**

- **Definition:** The identifier â typically an account code, transaction reference, or journal entry key â that links a risk record back to the corresponding entry in the general ledger or the system of record designated as the authoritative source for that balance.
- **Why critical:** Â¶36(c) explicitly requires that "risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate." Without a reconciliation key, this requirement cannot be operationalised: there is no mechanical link between the risk record and the accounting record that would allow an automated or manual break to be identified. Principle 7 (Â¶53a) requires "defined requirements and processes to reconcile reports to risk data." The reconciliation key is the data element that makes both requirements possible. Without it, accuracy cannot be evidenced â only asserted.
- **Risk types:** Cross-cutting (applies to all risk types that have an accounting counterpart â credit, market, liquidity)
- **Criticality: 3.** The absence of a reconciliation key does not merely degrade an aggregate â it makes the accuracy of the aggregate *unverifiable*. A bank cannot attest to Â¶36(c) without this link. Supervisors look for this specifically; its absence is among the most common and most serious findings in BCBS 239 reviews.
- **Driven by:** Principle 3 (Â¶36c) â *"risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (Â¶36d) â *"a bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 7 (Â¶53a) â *"defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** GL account code, general ledger reference, accounting transaction ID, source transaction reference, journal entry ID, subledger key, source system transaction number, finance reconciliation reference
- **Data quality requirements:**
  - *Completeness* â Every risk record that has a corresponding general ledger entry carries a populated reconciliation key | Count of risk records expected to have a GL counterpart but where the reconciliation key is null or blank | Target: 0%; any null reconciliation key on a balance-affecting record must be investigated before period-close
  - *Validity* â Every populated reconciliation key resolves to an active record in the general ledger or designated system of record | Count of risk records whose reconciliation key does not match any record in the GL | Target: 0% unmatched; unmatched items treated as reconciliation breaks and escalated
  - *Accuracy* â The sum of exposure amounts on risk records linked to a given GL account reconciles to the GL balance for that account within the defined tolerance | Reconciliation variance by account and legal entity; count and value of accounts outside tolerance | All breaks documented, root-caused, and resolved or formally accepted before report sign-off

---

**CDE-10 â Source System Identifier and Processing Method Flag**

- **Definition:** Two tightly related attributes: (a) the identifier of the source system from which a risk record originated; and (b) a flag indicating whether the record was produced by an automated feed, a manual data entry, or an end-user computing process (e.g., a spreadsheet or local database). These may be implemented as a single compound field or two adjacent attributes.
- **Why critical:** Â¶36(b) requires effective mitigants for manual processes and end-user computing. Â¶39 requires banks to "document and explain all of their risk data aggregation processes whether automated or manual" and to describe "the appropriateness of any manual workarounds." Neither obligation can be discharged if the record itself does not carry the information needed to identify where it came from and how it was produced. The source system identifier is also what enables data lineage to be traced from an aggregate back to its inputs â which is the foundation of the validation required by Â¶29(a). Â¶36(d) further requires banks to strive toward a single authoritative source per risk type; identifying the source system per record is necessary to assess whether that goal is being achieved.
- **Risk types:** Cross-cutting
- **Criticality: 2.** The presence of this field does not directly affect whether an aggregate is numerically right or wrong. It affects whether the accuracy of the aggregate can be validated, and whether manual-process risk is visible. If it is missing, automated monitoring for the disproportionate contribution of manual inputs to aggregates cannot be implemented, and lineage-based validation fails. Rated 2 rather than 3 because the aggregate number itself is not invalidated â the ability to verify and govern it is degraded.
- **Driven by:** Principle 3 (Â¶36b) â *"where a bank relies on manual processes and desktop applicationsâ¦ it should have effective mitigants in place"*; Principle 3 (Â¶36d) â *"strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (Â¶39) â *"document and explain all of their risk data aggregation processes whether automated or manual."*
- **Search terms:** source system, source system ID, feed name, data source, system of origin, upstream system, processing method, input type, automated flag, manual entry flag, EUC flag, spreadsheet flag, data lineage tag
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a populated source system identifier and processing method flag | Count of records with null or blank source system identifier or processing method flag | Target: 0%
  - *Validity* â Source system identifiers resolve to entries in the approved source system inventory maintained in the catalog | Count of records with source system identifiers not present in the approved inventory | Target: 0%; unknown source systems trigger immediate investigation
  - *Consistency* â The processing method flag accurately reflects the actual ingestion path; manual and EUC-sourced records are not miscategorised as automated | Proportion of records flagged as manual or EUC by source system compared to expected proportions per system; unexplained shifts flagged for review | Measured per aggregation cycle; significant increases in manual-flagged proportion trigger escalation per Â¶39â40
  - *Timeliness* â Source system metadata is updated in the catalog within the agreed SLA when a new source system is onboarded or decommissioned | Count of risk records whose source system identifier refers to a system not yet registered or already decommissioned in the catalog | Target: 0% at each aggregation run

---

**CDE-11 â Notional / Limit Amount for Risk Appetite Monitoring**

- **Definition:** The approved limit against which an exposure or position is measured, expressed in the same currency and at the same aggregation level as the corresponding exposure measure. Includes large exposure limits, single-counterparty concentration limits, and risk appetite thresholds set by the board.
- **Why critical:** Principle 8 (Â¶58) requires reports to "provide information in the context of limits and risk appetite/tolerance." This is not just a reporting presentation requirement â it means that the underlying data must carry the limit amount alongside the exposure, so that utilisation can be calculated and monitored. A report that shows exposure without limit context cannot fulfil Â¶58's requirement. Limit data also directly drives escalation: a breach cannot be identified unless the limit is a governed data element, comparable on a consistent basis to the exposure measure (CDE-03).
- **Risk types:** Credit, concentration, market, liquidity
- **Criticality: 2.** The aggregate exposure figure (CDE-03) is not wrong without the limit. But the report that contextualises it against risk appetite, which Â¶58 explicitly requires, cannot be produced. The missing context is a reporting completeness failure rather than an aggregation failure. Rated 2.
- **Driven by:** Principle 8 (Â¶58) â *"reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance"*; Principle 7 (Â¶52â53) â report accuracy requires reconciliation between exposure and approved limits.
- **Search terms:** credit limit, single-name limit, concentration limit, risk appetite threshold, counterparty limit, position limit, large exposure limit, approved limit, limit utilisation
- **Data quality requirements:**
  - *Completeness* â Every exposure subject to a board- or management-approved limit has a corresponding limit record with a populated limit amount | Count of counterparties or portfolios with exposure but no associated limit record where one is expected | Target: 0% for material exposures; gaps investigated before limit reporting
  - *Validity* â Limit amounts are within the range approved in the limit approval workflow; amounts outside the approved range are flagged | Count of limit records where the limit amount exceeds the authorised ceiling for that limit type | Target: 0%; flagged immediately
  - *Timeliness* â Limit records are updated within the agreed SLA following a board or management approval decision | Lag in calendar days between the effective date of a limit change and its reflection in the limit data store | Target: same-day or next-business-day update; breaches tracked per Â¶40

---

## 3. Cross-cutting data quality requirements

---

**XDQ-01 â Cross-system counterparty identity resolution**

- **Spans:** CDE-01 (Counterparty Unique Identifier), CDE-03 (Gross Exposure Amount), CDE-04 (Risk Type Classification), CDE-07 (Industry / Sector Classification)
- **What this is:** The most fundamental cross-cutting requirement in BCBS 239. It is not enough for each system to have a locally valid counterparty identifier. The counterparty master must serve as the golden record that resolves local identifiers from credit, market, liquidity, and finance systems to a single entity. When CDE-01 fails across systems, exposure amounts (CDE-03) cannot be summed by counterparty, risk type aggregation (CDE-04) may double-count, and sector classification (CDE-07) may be applied inconsistently. No single-element DQ rule catches this â it requires a cross-system reconciliation check that counts counterparty identifiers present in one system but unmatched in the master, and exposure value that is excluded from group aggregation because it carries only a local identifier.
- **Regulatory basis:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶41) â completeness across the banking group; Principle 5 (Â¶46a) â rapid aggregation of counterparty credit exposure named as a critical risk.
- **Dimension:** *Consistency* (across systems), *Completeness* (of mapping coverage)
- **Rule intent:** Every counterparty identifier in use across all risk and finance systems resolves to exactly one record in the group counterparty master, and the counterparty master covers 100% of active counterparties holding material exposures
- **Measurement:**
  - Count and exposure value of records in each risk system whose local counterparty identifier has no match in the group master
  - Count of counterparty identifiers that exist in two or more systems under different local codes but have not been linked in the master
  - Percentage of total group exposure (by value) attributable to counterparties that are fully resolved vs. locally identified only
- **Threshold:** Zero unmatched records for any counterparty with exposure above the materiality threshold; all others resolved within the agreed remediation SLA; total unresolved exposure value tracked and reported to senior management per Â¶30

---

**XDQ-02 â Risk-to-finance reconciliation completeness and break governance**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (General Ledger Reconciliation Key), CDE-02 (Legal Entity Identifier), CDE-08 (Position / As-of Date), CDE-10 (Source System Identifier and Processing Method Flag)
- **What this is:** Â¶36(c) requires risk data to be reconciled to accounting data. This cannot be expressed as a rule on any single element. It requires: (a) that every balance-affecting risk record carries a reconciliation key (CDE-09) linking it to the GL; (b) that exposure amounts (CDE-03) sum to the corresponding GL balances within tolerance; (c) that the comparison is made at a consistent legal entity (CDE-02) and as-of date (CDE-08); and (d) that breaks are identified, root-caused â which requires source system identification (CDE-10) â and escalated. The reconciliation process itself is the control; the data elements are its inputs. A catalog governs the inputs and can track break rates and resolution status. It cannot perform the reconciliation or own the resolution process.
- **Regulatory basis:** Principle 3 (Â¶36c) â *"risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (Â¶53a) â *"defined requirements and processes to reconcile reports to risk data"*; Principle 3 (Â¶40) â *"measure and monitor the accuracy of data and to develop appropriate escalation channels."*
- **Dimension:** *Accuracy* (reconciliation variance), *Completeness* (coverage of reconcilable items), *Consistency* (agreement between risk and finance at the same legal entity and date)
- **Rule intent:** The aggregate of risk exposure amounts, summed by legal entity and as-of date, agrees to the corresponding general ledger balances within a defined materiality tolerance; all breaks are identified, assigned a root cause, and resolved or formally accepted within the governance cycle
- **Measurement:**
  - Total reconciliation variance (value and percentage) between risk system exposure totals and GL balances, by legal entity, risk type, and as-of date
  - Count of risk records expected to be reconcilable (i.e., balance-affecting, with a GL counterpart) for which no reconciliation key is populated â measured using CDE-09
  - Count and value of reconciliation breaks unresolved beyond the defined SLA
  - Proportion of break value attributable to manual or EUC sources â measured using CDE-10 â to identify whether manual processing is a disproportionate driver of inaccuracy
- **Threshold:** Reconciliation variance â¤ defined materiality threshold (analogous to accounting materiality per Â¶56); zero unresolved breaks older than the defined escalation age; manual/EUC source proportion of total breaks tracked and trended

---

**XDQ-03 â Temporal consistency of aggregation batches**

- **Spans:** CDE-08 (Position / As-of Date), CDE-01 (Counterparty Unique Identifier), CDE-03 (Gross Exposure Amount), CDE-02 (Legal Entity Identifier)
- **What this is:** Each aggregation run must combine records that all refer to the same reference date. Stale data from a system that has not refreshed by the cut-off time, or a late-arriving feed with a different as-of date, silently distorts the aggregate. This cannot be detected by checking any single element's date in isolation â it requires comparing the as-of date distribution across all records in the batch. If a material proportion of records (or a material proportion of total exposure value) in a batch does not match the declared batch as-of date, the aggregate for that date is unreliable. Under stress, this is the failure mode that most often causes a bank to be unable to produce a same-day position. Principle 5 (Â¶45â46) makes rapid production of accurate aggregates under stress a named requirement; this cross-cutting check is what operationalises it.
- **Regulatory basis:** Principle 5 (Â¶44â46) â *"produce aggregate risk information on a timely basis"*; Principle 3 (Â¶36) â accuracy; Principle 6 (Â¶50) â ad-hoc aggregation "as of a specified date."
- **Dimension:** *Timeliness* (feed arrival relative to cut-off), *Consistency* (as-of date homogeneity within a batch)
- **Rule intent:** All records included in a declared aggregation batch share the same as-of date; feeds that have not delivered records stamped with the batch as-of date by the cut-off time are identified and their contribution to total exposure is quantified before the aggregate is released
- **Measurement:**
  - Count and exposure value of records in each aggregation batch whose as-of date differs from the declared batch date (measured using CDE-08 and CDE-03)
  - Count of source systems (measured using CDE-10) that have not delivered a complete file for the batch as-of date by the defined cut-off time
  - Exposure value attributable to late or stale feeds as a percentage of total batch exposure â to determine whether the aggregate can be released or must be withheld pending completion
- **Threshold:** Zero records with a mismatched as-of date in a released batch; any source system missing at the cut-off triggers an escalation decision per Â¶45; under stress reporting, stale-feed exposure above the materiality threshold blocks release

---

## 4. Out of scope

The following principles create obligations that a data catalog and CDE register, however well-governed, cannot satisfy. Stating this plainly is necessary: a bank that believes its catalog work discharges these obligations is misinformed, and a supervisor reviewing its BCBS 239 programme will find the gap.

---

**Principle 1 â Governance (Â¶27â31): Board and senior management accountability**

The governance obligations in Â¶27â31 â board approval of the risk data framework, senior management ownership of known limitations, inclusion of data considerations in acquisition due diligence, IT strategy for remediation â are organisational and decision-making requirements. A catalog can support them by making limitations visible (e.g., documenting known coverage gaps, tracking data quality scores) and by providing the data dictionary that Â¶37 requires. It cannot create the governance structures, approve the framework, or ensure senior management acts. Those require programme governance, committee mandates, and board-level accountability â which are beyond the catalog's scope. **What is needed instead:** a data governance operating model with named data owners (Â¶34), an executive data governance council, and a formal BCBS 239 compliance programme with board-level reporting.

---

**Principle 2 â Data architecture and IT infrastructure (Â¶32â35): System resilience and business continuity**

Â¶32 requires risk data capabilities to be included in business continuity planning. Â¶34 requires ownership and quality controls throughout the data lifecycle for both business and IT. A catalog can document data flows and identify upstream dependencies, supporting BCP planning. It cannot be the BCP, cannot provide system failover, and cannot enforce controls in source systems. **What is needed instead:** IT architecture governance, BCP testing programmes, and data quality controls implemented in source systems and ETL pipelines â not in the catalog's monitoring layer.

*Note: Â¶33 drives CDE-01 and CDE-02 above (the single-identifier requirement) and the catalog's taxonomy itself. That part is in scope. The infrastructure resilience obligation of Â¶32 is not.*

---

**Principle 6 â Adaptability (Â¶48â51): Ad-hoc query capability**

Â¶48â50 require that risk data can be re-sliced rapidly for ad-hoc scenarios, stress tests, and supervisory queries. A catalog governs whether the underlying data elements are defined, owned, and of sufficient quality to support that re-slicing. It does not provide the query or analytics capability itself. A bank with a perfect catalog but an inflexible risk data warehouse still fails Principle 6. **What is needed instead:** a flexible risk data warehouse or data lake with documented slicing dimensions, supported by the CDEs governed in this register.

*Note: Â¶50's explicit mention of country (CDE-06), industry (CDE-07), and business line (CDE-05) as required ad-hoc dimensions drives those CDEs above. The query capability to use them at speed is a system architecture matter, not a catalog matter.*

---

**Principle 7 â Accuracy in reports (Â¶52â56): Validation rule inventory and exception reporting**

Â¶53(b) requires "an inventory of the validation rules that are applied to quantitative information, including explanations of conventions used to describe mathematical or logical relationships." Â¶53(c) requires "integrated procedures for identifying, reporting and explaining data errors or weaknesses." The catalog can host and describe validation rules. It does not execute them on report outputs, own the exceptions process, or maintain the mathematical validation inventory that Â¶53(b) describes. **What is needed instead:** a report validation framework, typically owned by the risk reporting function, with a separate inventory of report-level validation rules distinct from data-level quality rules.

---

**Principle 8 â Comprehensiveness (Â¶57â60): Report content and forward-looking coverage**

Â¶57â60 govern what risk reports must contain: all significant risk areas, concentrations, limit context, forward-looking forecasts, and stress test results. A catalog governs whether the data underlying those report sections is well-defined and of sufficient quality. It does not govern report design, content completeness, or whether the board is receiving forward-looking information.

*Note: Â¶57's requirement to cover industry sector (CDE-07), and Â¶58's requirement to include limit context (CDE-11), drive data elements above. Those data governance obligations are in scope. The report content and design obligations are not. This dual applicability is intentional: a principle can simultaneously impose a data governance obligation (addressable in the catalog) and a reporting design obligation (not addressable there).*

**What is needed instead:** a risk report content standard, owned by the Chief Risk Officer and reviewed by the board, that specifies required sections, required metrics, and required narrative components for each report type.

---

**Principle 9 â Clarity and usefulness (Â¶61â69): Report tailoring, board dialogue, and periodic relevance confirmation**

Â¶62â69 govern the balance of quantitative vs. qualitative content, the board's dialogue with management about report adequacy, and the periodic confirmation that recipients find reports relevant (Â¶69). Â¶67 requires "an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports" â this is close to catalog scope and should inform the business glossary. But the dialogue, the tailoring, and the confirmation process are governance and communication obligations. **What is needed instead:** a risk reporting committee process, board feedback mechanism, and periodic recipient survey programme.

---

**Principle 10 â Frequency (Â¶70â71): Report production cadence and stress-scenario testing**

Â¶70 requires the bank to assess the purpose of each report and set timeliness requirements for normal and stress situations. Â¶71 expects intraday availability of critical positions under stress. The catalog can document the agreed timeliness SLAs for each data feed (CDE-08, CDE-10) and track whether feeds meet them. It cannot set the frequency requirements, own the stress-testing of report production, or ensure intraday system capability. **What is needed instead:** a report production SLA framework, owned by operations and technology, and a regular drill or simulation of stress-period report production.

---

**Principle 11 â Distribution (Â¶72â74): Report dissemination and confidentiality**

Â¶72â74 govern how reports are distributed, to whom, within what timeframe, and with what confidentiality controls. These are process, access management, and communications obligations entirely outside the catalog's scope. The catalog may inform access governance by classifying data sensitivity, but it does not own distribution processes or entitlements management for reports. **What is needed instead:** a report distribution framework, document management system with access controls, and an entitlements review process for risk reports.

---

## 5. Summary table

| CDE | Name | Criticality | Principles | DQ dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Unique Identifier | **3** | 2 (Â¶33), 4 (Â¶41), 5 (Â¶46a) | Uniqueness, Completeness, Validity, Consistency |
| CDE-02 | Legal Entity Identifier (Booking Entity) | **3** | 2 (Â¶33), 4 (Â¶41â43), 1 (Â¶30) | Validity, Completeness, Consistency |
| CDE-03 | Gross Exposure Amount | **3** | 3 (Â¶36a, Â¶36c), 4 (Â¶41), 7 (Â¶52) | Accuracy, Completeness, Validity |
| CDE-04 | Risk Type Classification | **2** | 4 (Â¶41â42), 7 (Â¶52), 8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | **2** | 4 (Â¶41), 6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-06 | Country / Geographic Region | **2** | 4 (Â¶41), 6 (Â¶50) | Validity, Completeness, Consistency |
| CDE-07 | Industry / Sector Classification | **2** | 4 (Â¶41), 6 (Â¶50), 8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-08 | Position / As-of Date | **3** | 5 (Â¶44â46), 6 (Â¶50), 3 (Â¶36) | Completeness, Validity, Timeliness, Consistency |
| CDE-09 | General Ledger Reconciliation Key | **3** | 3 (Â¶36c, Â¶36d), 7 (Â¶53a) | Completeness, Validity, Accuracy |
| CDE-10 | Source System Identifier and Processing Method Flag | **2** | 3 (Â¶36b, Â¶36d, Â¶39) | Completeness, Validity, Consistency, Timeliness |
| CDE-11 | Notional / Limit Amount | **2** | 8 (Â¶58), 7 (Â¶52â53) | Completeness, Validity, Timeliness |

**Cross-cutting requirements summary**

| ID | Name | Spans | DQ dimensions |
|---|---|---|---|
| XDQ-01 | Cross-system counterparty identity resolution | CDE-01, 03, 04, 07 | Consistency, Completeness |
| XDQ-02 | Risk-to-finance reconciliation completeness and break governance | CDE-03, 09, 02, 08, 10 | Accuracy, Completeness, Consistency |
| XDQ-03 | Temporal consistency of aggregation batches | CDE-08, 01, 03, 02 | Timeliness, Consistency |