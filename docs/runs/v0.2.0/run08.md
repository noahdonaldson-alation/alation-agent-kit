# BCBS 239 â Data Catalog Governance Interpretation

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **End the manual, fragmented risk data problem.** Banks must aggregate risk data on a "largely automated basis" and maintain "a single authoritative source for risk data per each type of risk" (Â¶36(d)). The driver is the 2008 crisis finding that senior management could not obtain a consolidated view of exposure in time to act.

- **Make risk data as trustworthy as accounting data.** "Controls surrounding risk data should be as robust as those applicable to accounting data" (Â¶36(a)). Risk figures must be reconcilable to the general ledger; unexplained gaps between the two are non-compliant.

- **Establish data architecture that survives stress.** A bank must "design, build and maintain data architecture and IT infrastructure which fully supports its risk data aggregation capabilitiesâ¦ not only in normal times but also during times of stress or crisis" (Principle 2 heading, Â¶32â35). Architecture is a precondition, not an afterthought.

- **Require a shared data dictionary.** "A bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation" (Â¶37). Inconsistent definitions across systems make group-level aggregation unreliable even where data is technically present.

- **Demand documented, auditable lineage.** Banks must "document and explain all of their risk data aggregation processes whether automated or manual" (Â¶39), including the appropriateness of manual workarounds. Supervisors will inspect this documentation.

- **Drive board-level accountability for data.** The board must "review and approve the bank's group risk data aggregation and risk reporting framework" (Â¶28) and must understand the limitations of the data it receives (Â¶31). Data governance is therefore a board matter, not solely an IT matter.

**Who it applies to**

BCBS 239 applies to **Global Systemically Important Banks (G-SIBs)** and, by supervisory expectation, to domestic systemically important banks (D-SIBs). It covers the **entire banking group** â all legal entities, subsidiaries, business lines, and geographies â and applies in both normal operations and stress/crisis conditions.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Identifier**
- **Definition:** A single, persistent, unique identifier assigned to each legal-entity counterparty, used to link every exposure record to that counterparty regardless of which source system originated the record.
- **Why critical:** Without a common counterparty key, exposures from trading, lending, and derivatives systems cannot be summed to produce a group-level counterparty exposure. The aggregate is impossible, not merely degraded.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3.** Its failure *invalidates* any aggregated single-name or counterparty credit exposure figure. No partial result is possible â you cannot aggregate what you cannot link. This is the clearest Level 3 case in the register.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶41) â *"risk data aggregation capabilities should include all material risk exposures"*; Principle 5 (Â¶46(b)) â *"counterparty credit risk exposures, including, for example, derivatives"*
- **Search terms:** counterparty ID, counterparty code, legal entity identifier, LEI, client ID, obligor ID, party ID, GCID (global counterparty ID)
- **Data quality requirements:**
  - *Uniqueness* â Each counterparty is represented by exactly one identifier across all source systems | Count of counterparty identifiers that resolve to more than one master record, or master records with more than one active identifier | Target: zero duplicates in the golden-source master
  - *Completeness* â Every exposure record carries a non-null, populated counterparty identifier | Count and percentage of exposure records with null or missing counterparty identifier | Target: 0% null; any exception logged with a remediation date
  - *Validity* â Every counterparty identifier on an exposure record resolves to an active record in the counterparty master | Count of exposure records whose counterparty identifier does not match any record in the authoritative counterparty register | Target: 0% unmatched
  - *Consistency* â The same counterparty identifier is used for the same legal entity across credit, market, and liquidity systems | Count of counterparty names or identifiers that appear in more than one system under different keys for the same real-world entity | Target: zero unresolved cross-system mismatches

---

**CDE-02 â Legal Entity Identifier (Own Entity)**
- **Definition:** The identifier for the bank's own booking or holding legal entity â the entity within the banking group in which an exposure, position, or liability is recorded for accounting and regulatory purposes.
- **Why critical:** Group consolidation and subsidiary-level regulatory reporting both require that every risk record is unambiguously attributed to a specific legal entity within the group structure. Without this, exposures cannot be rolled up to group level or broken out by subsidiary. Principle 4 explicitly requires aggregation "byâ¦ legal entity" (Principle 4 heading).
- **Risk types:** Cross-cutting (applies to credit, market, liquidity, and operational risk alike)
- **Criticality: 3.** Without a populated and valid own-entity identifier on every record, consolidation across the group is impossible. Records that cannot be attributed to an entity cannot be included in or excluded from a consolidation scope without arbitrary assumption, which invalidates the group aggregate.
- **Driven by:** Principle 2 (Â¶33) â *"integrated data taxonomies and architecture across the banking group, which includesâ¦ single identifiersâ¦ for data including legal entities"*; Principle 4 heading â *"capture and aggregate all material risk data across the banking groupâ¦ by business line, legal entity"*
- **Search terms:** legal entity ID, entity code, booking entity, subsidiary code, MFI code, LEI (own entity), consolidation entity, reporting entity
- **Data quality requirements:**
  - *Completeness* â Every risk and exposure record carries a non-null own-entity identifier | Count and percentage of records with null own-entity field | Target: 0% null
  - *Validity* â Every own-entity identifier resolves to an active entity in the group's legal entity hierarchy | Count of records referencing an entity code not present in the authoritative group structure register | Target: 0% invalid
  - *Consistency* â The same entity is represented by the same identifier across risk, finance, and regulatory reporting systems | Count of entity names that appear in multiple systems under different identifiers without a documented cross-reference | Target: zero unresolved mismatches

---

**CDE-03 â Gross Exposure Amount**
- **Definition:** The monetary value of a bank's gross (pre-mitigation) exposure to a counterparty, instrument, or position, expressed in a defined currency, as of a stated position date. This is the primary input to all credit and concentration risk aggregation.
- **Why critical:** This is the quantity that is summed, sliced, and reported. Every risk aggregate â single-name exposure, sector concentration, country exposure â is built from this field. If it is wrong, every downstream aggregate is wrong. It is also the primary field reconciled against the general ledger (Â¶36(c)).
- **Risk types:** Credit, counterparty, concentration
- **Criticality: 3.** An inaccurate or missing exposure amount does not degrade an aggregate â it corrupts it. Even a partially populated aggregate is misleading rather than merely incomplete, because the numerator is wrong without the missing exposures being flagged.
- **Driven by:** Principle 3 (Â¶36(c)) â *"risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 4 (Â¶41) â *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 5 (Â¶46(a)) â *"the aggregated credit exposure to a large corporate borrower"*
- **Search terms:** exposure at default, EAD, gross exposure, outstanding balance, notional amount, drawn balance, commitment amount, mark-to-market value, current exposure
- **Data quality requirements:**
  - *Accuracy* â Exposure amounts agree to the system of record (general ledger or position-keeping system) within agreed materiality tolerance | Sum of absolute differences between risk system exposure amounts and GL balances per counterparty, per position date | Target: variance within accounting materiality threshold; no unexplained variance above threshold
  - *Completeness* â All material exposure types, including off-balance-sheet items, are represented | Count of known off-balance-sheet product types absent from the risk data population versus the general ledger population | Target: zero product type gaps that exceed de minimis threshold
  - *Validity* â Exposure amounts are non-negative (or follow documented sign convention) and within plausible range for the product type | Count of records with negative gross exposure or amounts exceeding defined plausibility bounds without an override flag | Target: zero unexplained out-of-range values
  - *Timeliness* â Exposure amounts reflect the stated position date within the agreed settlement/booking lag | Count of records where the booking timestamp is more than the agreed lag after the position date | Target: within SLA for normal reporting; accelerated SLA for stress

---

**CDE-04 â Risk Type Classification**
- **Definition:** A controlled vocabulary term classifying each exposure or position by the primary type of risk it represents â credit risk, market risk, liquidity risk, operational risk, counterparty credit risk, or concentration risk.
- **Why critical:** Risk type is the primary partition used to route exposure records into the correct aggregation engine, capital model, and report section. Misclassification sends an exposure into the wrong calculation, producing a wrong figure in one report and a gap in another.
- **Risk types:** Cross-cutting
- **Criticality: 3.** Misclassification does not merely degrade a report; it simultaneously inflates one risk figure and deflates another. A credit exposure misclassified as operational risk is absent from credit concentration measures. The error is invisible unless risk-type totals are reconciled to a complete population.
- **Driven by:** Principle 7 (Â¶52) â *"risk management reports should be accurate and precise to ensure a bank's board and senior management can rely with confidence on the aggregated information"*; Principle 8 (Â¶57) â *"risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*
- **Search terms:** risk type, risk category, risk class, risk classification, product risk flag, risk bucket
- **Data quality requirements:**
  - *Validity* â Every exposure record carries a risk type value drawn from the authoritative controlled vocabulary | Count of records with a null, free-text, or non-enumerated risk type value | Target: 0% invalid or null
  - *Consistency* â The same instrument or product type is classified identically across source systems | Count of instrument types that receive different risk type codes in different systems without a documented override | Target: zero unexplained cross-system inconsistencies
  - *Completeness* â No risk type present in the general ledger population is absent from the risk data population | List of risk types appearing in GL product codes but absent from the risk classification register | Target: zero unrepresented risk types above de minimis

---

**CDE-05 â Business Line**
- **Definition:** A controlled vocabulary term identifying the organisational business unit or activity that originated or owns an exposure or position (e.g., retail banking, corporate banking, trading, treasury, wealth management).
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. The board and senior management must be able to see risk by business line; without a populated and valid business line attribute, that slice is impossible.
- **Risk types:** Cross-cutting
- **Criticality: 2.** If business line is null or miscoded on a subset of records, the business-line slice of any aggregate is incomplete or misleading, but the total aggregate (summed across all lines) may still be produced. The overall figure is not invalidated, but a required reporting dimension is not deliverable. This is a Level 2 degradation.
- **Driven by:** Principle 4 heading â *"data should be available by business line, legal entity, asset type, industry, region and other groupingsâ¦ that permit identifying and reporting risk exposures, concentrations and emerging risks"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*
- **Search terms:** business line, business unit, line of business, LOB code, division code, cost centre, desk code
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null business line code | Count and percentage of exposure records with null or missing business line | Target: 0% null; any exception documented
  - *Validity* â Business line codes are drawn from the authoritative organisational hierarchy | Count of records carrying a business line code not present in the current organisational hierarchy register | Target: 0% invalid
  - *Consistency* â Business line codes are applied consistently to the same product or desk across systems | Count of instruments or accounts that carry different business line codes in different systems without a documented reason | Target: zero unexplained cross-system differences

---

**CDE-06 â Geography / Country of Risk**
- **Definition:** The country or jurisdiction to which an exposure is attributed for risk purposes â typically the country of the counterparty's domicile, the country of the collateral, or the country of booking, depending on the risk type and the bank's documented methodology.
- **Why critical:** Country/geography is explicitly named as a required aggregation dimension in Principle 4. Supervisors specifically cite country credit exposure aggregation as a test case for adaptability (Â¶50). Geographic concentration risk cannot be measured without it.
- **Risk types:** Credit, concentration, cross-cutting
- **Criticality: 2.** A missing or miscoded geography prevents the geographic slice of a risk aggregate but does not prevent the total aggregate from being produced. Required reporting dimension degrades; overall figure does not invalidate. Level 2.
- **Driven by:** Principle 4 heading â *"data should be available byâ¦ region"*; Principle 6 (Â¶50) â *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*; Principle 5 (Â¶46(c)) â *"market concentrations by sector and region data"*
- **Search terms:** country code, country of risk, booking country, domicile country, region code, jurisdiction, ISO country code, geographic classification
- **Data quality requirements:**
  - *Validity* â Country codes conform to an authoritative standard (e.g., ISO 3166) | Count of records with country codes not present in the reference standard | Target: 0% non-standard codes
  - *Completeness* â Every exposure record carries a non-null country of risk | Count and percentage of records with null geography | Target: 0% null; exceptions documented with impact assessment
  - *Consistency* â The same counterparty is assigned the same country of risk across systems | Count of counterparties assigned different country codes in different systems without a documented methodology difference | Target: zero unexplained mismatches

---

**CDE-07 â Industry / Sector Classification**
- **Definition:** A controlled vocabulary term classifying each counterparty or issuer by economic sector or industry (e.g., using GICS, NACE, SIC, or an internal equivalent), used to measure sector concentration in credit and market risk.
- **Why critical:** Industry/sector is named explicitly in Principle 4, Principle 5 (Â¶46(c)), and Principle 8 (Â¶57) as a required reporting dimension and aggregation slice. Sector concentration risk cannot be identified or reported without it.
- **Risk types:** Credit, concentration, market
- **Criticality: 2.** Missing or invalid sector codes prevent the sector slice from being delivered but do not invalidate the total exposure aggregate. Required reporting dimension degrades; overall figure survives. Level 2.
- **Driven by:** Principle 4 heading â *"data should be available byâ¦ industry"*; Principle 5 (Â¶46(c)) â *"trading exposures, positions, operating limits, and market concentrations by sector and region data"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*
- **Search terms:** industry code, sector code, GICS sector, NACE code, SIC code, industry classification, sector classification, obligor sector
- **Data quality requirements:**
  - *Validity* â Sector codes are drawn from the authoritative classification scheme in use at the bank | Count of records with sector codes not in the controlled vocabulary | Target: 0% invalid
  - *Completeness* â Every counterparty record carries a non-null sector classification | Count and percentage of counterparty records with null sector | Target: 0% null
  - *Consistency* â The same counterparty receives the same sector classification in the counterparty master and in downstream risk systems | Count of counterparties with different sector codes across systems | Target: zero unexplained differences

---

**CDE-08 â Position / As-Of Date**
- **Definition:** The business date as of which a risk position, exposure, or balance is stated. This is the temporal key that anchors every aggregate to a point in time and enables point-in-time reconciliation.
- **Why critical:** Without a populated as-of date, it is impossible to determine whether records are current, stale, or belong to different reporting periods. Mixing positions from different dates in a single aggregate is a data integrity failure. Timeliness compliance (Principle 5) cannot be evidenced without it.
- **Risk types:** Cross-cutting
- **Criticality: 3.** A record without a valid position date cannot be correctly included in any time-anchored aggregate. Including it introduces an unknown error; excluding it understates the aggregate. Either way, the aggregate is invalidated rather than merely degraded. Level 3.
- **Driven by:** Principle 5 heading â *"a bank should be able to generate aggregate and up-to-date risk data in a timely manner"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (Â¶53(a)) â *"defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** position date, as-of date, snapshot date, value date, reference date, report date, trade date, balance date
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a non-null position date | Count and percentage of records with null position date | Target: 0% null
  - *Validity* â Position dates are valid calendar dates within a plausible range (not future-dated beyond booking lag, not older than data retention policy) | Count of records with position dates outside the valid range | Target: 0% invalid dates
  - *Timeliness* â The most recent position date in the risk system matches the current reporting period | Lag in days between the latest position date in the risk data store and the current business date | Target: within documented SLA; breach triggers escalation per Â¶40

---

**CDE-09 â GL / System-of-Record Reconciliation Key**
- **Definition:** The identifier â typically a trade reference number, account number, or journal entry key â that links a risk record to its corresponding entry in the general ledger or primary system of record, enabling the reconciliation required by Â¶36(c).
- **Why critical:** This is the mechanism by which accuracy and completeness are *evidenced* rather than asserted. Without a reconciliation key, a bank cannot demonstrate that its risk data agrees with its accounting data; it can only claim it does. Â¶36(c) makes this reconciliation an explicit requirement. Supervisors will look for evidence of reconciliation, not statements about it.
- **Risk types:** Cross-cutting
- **Criticality: 3.** Without the reconciliation key, the GL-to-risk reconciliation required by Â¶36(c) cannot be performed mechanically at the record level. The bank falls back on aggregate-level reconciliation at best, which cannot identify which specific records are missing or wrong. The accuracy and completeness assertions that underpin every risk report lack their evidential foundation. Level 3 â the control is impossible without it.
- **Driven by:** Principle 3 (Â¶36(c)) â *"risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (Â¶53(a)) â *"defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** trade ID, trade reference, account number, GL reference, journal entry ID, position ID, deal ID, booking reference, system key, source record ID
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a non-null GL or system-of-record reference key | Count and percentage of risk records with null reconciliation key | Target: 0% null; any null documented with an approved exception
  - *Validity* â Every GL reference key on a risk record resolves to an active record in the general ledger or system of record | Count of risk records whose reference key does not match any GL entry | Target: 0% unmatched; unmatched keys treated as reconciliation breaks
  - *Uniqueness* â Each GL reference key maps to at most one risk record (or the one-to-many mapping is documented and expected) | Count of GL reference keys appearing on more than one risk record where a one-to-one mapping is expected | Target: zero unexplained duplicates
  - *Accuracy* â Monetary amounts on the risk record agree to the corresponding GL entry within agreed tolerance | Sum of absolute differences between risk record amounts and GL amounts for matched keys | Target: within accounting materiality per Â¶56

---

**CDE-10 â Source System / Lineage Flag**
- **Definition:** The identifier of the system from which a risk record originated, combined with a flag indicating whether the record was produced by an automated process or involved manual intervention or end-user computing (EUC) input.
- **Why critical:** Â¶36(d) requires a single authoritative source per risk type; Â¶36(b) requires effective controls over manual and EUC processes; Â¶39 requires documentation of all processes, with manual workarounds explicitly called out. Without a source system tag and a manual/automated flag, a bank cannot identify which records are subject to heightened control, cannot demonstrate it has applied EUC policies consistently, and cannot produce the documentation supervisors will inspect.
- **Risk types:** Cross-cutting
- **Criticality: 2.** A missing source flag does not invalidate an individual exposure figure, but it makes it impossible to apply risk-tiered data quality controls, identify the population of EUC-sourced records, or produce the lineage documentation Â¶39 demands. The aggregate is produced, but the control framework around it is unauditable. Level 2.
- **Driven by:** Principle 3 (Â¶36(b)) â *"where a bank relies on manual processes and desktop applicationsâ¦ it should have effective mitigants in placeâ¦ consistently applied"*; Principle 3 (Â¶36(d)) â *"a bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (Â¶39) â *"document and explain all of their risk data aggregation processes whether automated or manual"*
- **Search terms:** source system, system of origin, feed name, data source, EUC flag, manual override flag, automated feed indicator, data provenance, lineage tag, upstream system
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a non-null source system identifier and a non-null manual/automated flag | Count and percentage of records missing either attribute | Target: 0% null on both fields
  - *Validity* â Source system identifiers are drawn from the bank's authoritative system register | Count of records referencing a source system not in the system register | Target: 0% unregistered sources
  - *Accuracy* â Records flagged as EUC or manual are the same population subject to enhanced controls in the EUC policy register | Count of records flagged as manual/EUC that have no corresponding entry in the EUC policy register, and vice versa | Target: zero gaps between flagged population and governed population

---

**CDE-11 â Limit / Risk Appetite Threshold**
- **Definition:** The approved maximum exposure or risk measure assigned to a counterparty, sector, country, or business line, against which the corresponding aggregated exposure is compared in risk reports.
- **Why critical:** Principle 8 (Â¶58) requires reports to "provide information in the context of limits and risk appetite/tolerance." Without the limit value as a governed data element, the utilisation ratio â exposure divided by limit â cannot be produced systematically, and breach identification is manual and unreliable.
- **Risk types:** Credit, market, liquidity, concentration
- **Criticality: 2.** An absent or stale limit does not prevent the exposure aggregate from being calculated, but it prevents the exposure from being contextualised against the bank's own risk appetite in the report. The aggregate is produced but the required contextual measure (utilisation, headroom) is missing or wrong. Level 2.
- **Driven by:** Principle 8 (Â¶58) â *"reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance and propose recommendations for action where appropriate"*; Principle 5 (Â¶46(c)) â *"trading exposures, positions, operating limits, and market concentrations"*
- **Search terms:** limit amount, exposure limit, credit limit, risk limit, approved limit, limit utilisation, risk appetite threshold, approved line
- **Data quality requirements:**
  - *Accuracy* â Limit values in the risk data system match the most recently board- or senior-management-approved limit | Count of limits in the risk system that differ from the value in the limit approval record | Target: zero unexplained differences; any difference resolved within documented SLA
  - *Timeliness* â Limit records are updated within the agreed lag after an approval decision | Count of limit records where the effective date of the system value is more than the agreed lag after the approval date | Target: within SLA; breach escalated
  - *Completeness* â Every counterparty, sector, or country dimension for which a limit has been approved carries a populated limit record | Count of approved limits not represented in the risk system | Target: 0% missing approved limits

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â GL-to-Risk Population Reconciliation**
- **Spans:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-08 (Position/As-Of Date), CDE-09 (GL Reconciliation Key)
- **What this is:** A control that confirms the *population* of records in the risk data store matches the population in the general ledger for the same position date, and that the monetary totals agree within materiality. This is distinct from validating any single element â it is the cross-system check that Â¶36(c) requires and that Â¶53(a) operationalises. No individual CDE monitor catches it, because each looks at one field on one record. The completeness failure this catches is a record that is *entirely absent* from the risk system â it has no null fields, because it does not exist.
- **Driven by:** Principle 3 (Â¶36(c)) â *"risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 7 (Â¶53(a)) â *"defined requirements and processes to reconcile reports to risk data"*
- **Requirements:**
  - *Completeness* â The count of records in the risk data population matches the count of corresponding records in the GL population for the same position date and scope | Count of GL records with no matching risk record (by reconciliation key), and count of risk records with no matching GL record, per position date | Target: zero unexplained breaks; all breaks documented with root cause and remediation date within agreed SLA
  - *Accuracy* â The sum of gross exposure amounts in the risk system equals the sum of corresponding GL balances within materiality tolerance | Absolute difference between risk-system total and GL total per risk type, per position date | Target: difference within accounting materiality per Â¶56; any breach triggers formal exception with escalation path per Â¶40

---

**XDQ-02 â Cross-System Counterparty Identity Resolution**
- **Spans:** CDE-01 (Counterparty Identifier), CDE-02 (Own Legal Entity), CDE-05 (Business Line), CDE-06 (Geography), CDE-07 (Industry/Sector)
- **What this is:** A control that confirms the same real-world counterparty is represented by the same identifier across all source systems (credit, trading, treasury, derivatives). This cannot be expressed as a monitor on a single element, because the problem â the same counterparty appearing under different IDs in different systems â only surfaces when records from different systems are compared. It is the most common failure mode in counterparty concentration risk, and it is what Â¶33's requirement for "single identifiers" is specifically designed to prevent. If this control is not operating, aggregated counterparty exposure is understated in proportion to how fragmented the identity is.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶41) â *"risk data aggregation capabilities should include all material risk exposures"*; Principle 5 (Â¶46(b)) â *"counterparty credit risk exposures, including, for example, derivatives"*
- **Requirements:**
  - *Uniqueness* â Each real-world counterparty legal entity appears under exactly one identifier in the enterprise counterparty master, with all source system local IDs mapped to that master record | Count of counterparty names or external identifiers (e.g., LEI, tax ID) that map to more than one master record, or master records with no source-system cross-reference | Target: zero unmapped or duplicated master records; any exception documented with a merge/suppress plan
  - *Consistency* â Dimension attributes of a counterparty â country of risk, sector, legal entity group â are identical across all source systems for the same master record | Count of counterparty master records where the same attribute (country, sector) carries different values in different source systems without a documented methodology explanation | Target: zero unexplained cross-system attribute conflicts; conflicts resolved through the data dictionary (Â¶37) within agreed SLA

---

**XDQ-03 â EUC and Manual Input Inventory Completeness**
- **Spans:** CDE-09 (GL Reconciliation Key), CDE-10 (Source System / Lineage Flag)
- **What this is:** A control that verifies the bank's inventory of end-user computing tools and manual processes contributing to risk data is complete â meaning every EUC tool and manual workaround that feeds a risk figure has been identified, registered, and is subject to the controls Â¶36(b) requires. This is not a property of any individual record; it is a property of the *set* of source systems producing records. A single-element monitor on the EUC flag (CDE-10) confirms that known EUC sources are flagged. This cross-cutting control asks the prior question: are all EUC sources known? The gap it catches is a spreadsheet that is feeding risk figures but has never been added to the register â a record with no source flag at all, or flagged as automated when it is not.
- **Driven by:** Principle 3 (Â¶36(b)) â *"where a bank relies on manual processes and desktop applicationsâ¦ it should have effective mitigants in placeâ¦ consistently applied across the bank's processes"*; Principle 3 (Â¶39) â *"banks [must] document and explain all of their risk data aggregation processes whether automated or manual"*
- **Requirements:**
  - *Completeness* â Every source contributing records to risk aggregation is listed in the source system register, and those identified as EUC or manual are listed in the EUC policy register | Count of distinct source system identifiers appearing in risk data that are absent from the system register; count of systems flagged as EUC in data but absent from the EUC policy register | Target: zero unregistered sources; any gap treated as a governance finding with a registration deadline
  - *Accuracy* â The volume of records originating from EUC and manual sources is tracked over time and compared against reduction targets where remediation is in progress | Trend in percentage of risk records flagged as EUC or manual, measured at each reporting period | Target: consistent with the bank's documented roadmap for reducing EUC reliance (Â¶39); any increase triggers review

---

## 4. Out of Scope

The following matters arise from Principles 1â11 but **cannot be addressed by a CDE register or data quality monitoring**. Stating this plainly is not an evasion â it identifies where the bank must invest governance effort *beyond* the catalog.

---

**Principle 1 â Governance framework and board accountability (Â¶27â31)**

The board approval of the risk data aggregation framework, the deployment of adequate resources, independent validation activities, and senior management awareness of aggregation limitations are organisational governance matters. A data catalog can provide the artifact that governance acts upon â the CDE register, the lineage documentation, the DQ monitoring results â but it cannot constitute the governance itself. The board's approval of the framework (Â¶28), the independence of the validation function (Â¶29(a)), and the senior management's strategic IT planning obligations (Â¶30) all require human decision-making, documented policies, and organisational authority that no catalog feature can substitute for.

---

**Principle 2 â IT architecture and business continuity (Â¶32â35)**

The requirement for integrated data architecture, business continuity planning, and role/responsibility assignment for data ownership (Â¶34) is an IT infrastructure and operating model matter. A catalog can document the architecture and publish ownership assignments, but it cannot build the integrated architecture, conduct the business impact analysis (Â¶32), or enforce the controls that owners are responsible for. The catalog is a record of the architecture, not the architecture itself.

---

**Principle 3 â Automation of aggregation (Â¶38â39)**

The requirement that aggregation be conducted on a "largely automated basis" (Principle 3 heading) and that manual workarounds be reduced over time (Â¶39) is a system engineering and process improvement obligation. A catalog can flag EUC sources (CDE-10, XDQ-03) and document them, but it cannot automate the processes, replace the spreadsheets, or enforce the remediation timeline. The documentation obligation in Â¶39 is partially addressable through catalog lineage; the remediation obligation is not.

---

**Principle 6 â Adaptability and stress scenario capability (Â¶48â50)**

The requirement that risk systems be capable of producing ad hoc aggregations and stress scenario subsets rapidly (Â¶48â50) is a technology capability requirement. A catalog can document which data elements exist and where they live, facilitating faster data discovery. It cannot guarantee that the underlying data systems can re-aggregate to arbitrary dimensions on demand or within the timescales that stress situations require. The capability gap is in the data platform, not the catalog.

---

**Principles 7â11 â Risk reporting obligations**

This is the most important out-of-scope category. Principles 7 through 11 are substantially about the *content, quality, frequency, and distribution of risk management reports* presented to the board and senior management. A data catalog addresses the upstream data; it does not govern the reports themselves.

**Principle 7 (Accuracy of reports, Â¶52â56)** partly drives data-layer requirements â and CDE-09 and XDQ-01 address the reconciliation and validation that underpin report accuracy. However, the requirements in Â¶53(b) (automated edit and reasonableness checks within the reporting process), Â¶53(c) (exception reporting procedures for data errors), and Â¶54â56 (accuracy standards for approximations and stress test results) are report-production and model-validation obligations that belong to the reporting infrastructure, not the catalog.

**Principle 8 (Comprehensiveness, Â¶57â60)** names industry sector as a reporting dimension â which drives CDE-07 â but the requirement that reports cover capital adequacy, regulatory capital, liquidity ratios, stress testing results, and forward-looking assessments (Â¶59â60) is a report-content obligation. The catalog governs the data elements; it does not govern what content the report includes or whether that content meets the board's information needs.

**Principle 9 (Clarity and usefulness, Â¶61â69)** is entirely outside catalog scope. The requirements that reports strike the right balance of quantitative and qualitative content (Â¶62), that the board confirms the relevance and appropriateness of what it receives (Â¶69), and that senior management tailors reports to recipients (Â¶63â66) are reporting design, governance, and communication obligations. Note: Â¶67 â "a bank should develop an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports" â is the one paragraph in Principle 9 that a data catalog directly supports. It describes, essentially, a business glossary and CDE register. But this does not make Principle 9 as a whole addressable through catalog governance.

**Principle 10 (Frequency, Â¶70â71)** requires the board and senior management to set reporting frequency requirements, test the bank's ability to produce accurate reports within those timeframes, and accelerate reporting in stress. This is a board governance and system capability obligation. Catalog-level timeliness monitoring on CDEs (CDE-08) supports it indirectly by flagging stale data, but the obligation to set the requirements, run the tests, and demonstrate stress-period compliance belongs to the reporting governance process.

**Principle 11 (Distribution, Â¶72â74)** concerns report dissemination procedures, confidentiality controls, and confirmation that recipients receive reports. These are information security, access control, and operational process matters entirely outside catalog scope.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | **3** | P2 (Â¶33), P4 (Â¶41), P5 (Â¶46b) | Uniqueness, Completeness, Validity, Consistency |
| CDE-02 | Legal Entity Identifier (Own Entity) | **3** | P2 (Â¶33), P4 (heading) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | **3** | P3 (Â¶36c), P4 (Â¶41), P5 (Â¶46a) | Accuracy, Completeness, Validity, Timeliness |
| CDE-04 | Risk Type Classification | **3** | P7 (Â¶52), P8 (Â¶57) | Validity, Consistency, Completeness |
| CDE-08 | Position / As-Of Date | **3** | P5 (heading), P6 (Â¶50), P7 (Â¶53a) | Completeness, Validity, Timeliness |
| CDE-09 | GL / System-of-Record Reconciliation Key | **3** | P3 (Â¶36c), P7 (Â¶53a) | Completeness, Validity, Uniqueness, Accuracy |
| CDE-05 | Business Line | **2** | P4 (heading), P6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | **2** | P4 (heading), P5 (Â¶46c), P6 (Â¶50) | Validity, Completeness, Consistency |
| CDE-07 | Industry / Sector Classification | **2** | P4 (heading), P5 (Â¶46c), P8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-10 | Source System / Lineage Flag | **2** | P3 (Â¶36b, Â¶36d, Â¶39) | Completeness, Validity, Accuracy |
| CDE-11 | Limit / Risk Appetite Threshold | **2** | P8 (Â¶58), P5 (Â¶46c) | Accuracy, Timeliness, Completeness |

| XDQ | Name | Spans | DQ Dimensions |
|---|---|---|---|
| XDQ-01 | GL-to-Risk Population Reconciliation | CDE-01, CDE-03, CDE-08, CDE-09 | Completeness, Accuracy |
| XDQ-02 | Cross-System Counterparty Identity Resolution | CDE-01, CDE-02, CDE-05, CDE-06, CDE-07 | Uniqueness, Consistency |
| XDQ-03 | EUC and Manual Input Inventory Completeness | CDE-09, CDE-10 | Completeness, Accuracy |