# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Accurate, complete, timely risk aggregation.** Banks must produce reliable aggregated risk data across the full banking group — legal entities, business lines, asset types, industries, and geographies — in normal conditions and under stress. The data must be accurate enough that omissions or misstatements do not influence risk decisions (¶43: *"Supervisors expect banks to produce aggregated risk data that is complete and to measure and monitor the completeness of their risk data"*; ¶56: *"if omission or misstatement could influence the risk decisions of users, this may be considered material"*).

- **Integrated data architecture with single identifiers.** A bank must maintain unified taxonomies, metadata, and naming conventions — including single identifiers for legal entities, counterparties, customers, and accounts — so that exposures can be joined and aggregated without ambiguity (¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions"*).

- **Reconciliation to accounting and source systems.** Risk data must be reconcilable to accounting data and to authoritative source systems so that accuracy can be evidenced, not merely asserted (¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*).

- **Transparency over manual processes and data provenance.** Every aggregation process — automated or manual — must be documented. Manual workarounds must be explained, assessed for their criticality, and supported by controls. The source of every risk record must be traceable (¶39: *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual"*; ¶36(d): *"A bank should strive towards a single authoritative source for risk data per each type of risk"*).

- **Monitored data quality with escalation.** Banks must actively measure and monitor data accuracy, completeness, and timeliness, and must have escalation channels and remediation plans for defects — not merely passive controls (¶40: *"Supervisors expect banks to measure and monitor the accuracy of data and to develop appropriate escalation channels and action plans to be in place to rectify poor data quality"*).

- **Board and senior management accountability.** The governance framework — including data quality standards, IT strategy, and awareness of aggregation limitations — must be approved and owned at board and senior management level, not delegated entirely to IT (¶28: *"A bank's board and senior management should review and approve the bank's group risk data aggregation and risk reporting framework"*; ¶30).

**Who it applies to**

BCBS 239 applies, as of January 2013, to **Global Systemically Important Banks (G-SIBs)** and is expected to be extended to **Domestic Systemically Important Banks (D-SIBs)** by national supervisors. The principles apply at the **consolidated banking group** level, encompassing all material subsidiaries, legal entities, and business lines — including off-balance-sheet exposures (¶41).

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** A unique, persistent identifier assigned to each counterparty (borrower, issuer, derivative counterparty, depositor) that is consistent across all systems in which exposures to that counterparty are recorded. It is the key that allows all exposures to the same legal or natural person to be summed.
- **Why critical:** Without a single, resolvable counterparty identifier, exposures booked in different systems — the loan origination system, the derivatives platform, the securities ledger — cannot be reliably joined. The aggregate credit exposure to any counterparty cannot be computed. This is precisely the scenario ¶33 and ¶46(a)–(b) target: aggregating exposures to a large corporate borrower or counterparty credit risk including derivatives. A null or unresolvable identifier means the aggregation silently drops or double-counts exposures.
- **Risk types:** Credit, counterparty, concentration
- **Criticality:** **3.** Without this element, the aggregate exposure to counterparty X cannot be computed at all, because exposures in system A cannot be matched to exposures in system B — there is no common key to join on.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41) — off-balance-sheet exposures must be included; Principle 5 (¶46(a)–(b)) — aggregated credit and counterparty exposures are named as critical risks.
- **Search terms:** counterparty ID, counterparty identifier, client ID, obligor ID, entity ID, LEI (Legal Entity Identifier), GFCID, golden source party ID, party master key
- **Data quality requirements:**
  - *uniqueness* — Each counterparty identifier maps to exactly one counterparty; no two distinct counterparties share the same identifier across any system in scope | Count of identifier values that resolve to more than one distinct counterparty in the party master; count of duplicate identifiers across source systems | Target: zero duplicates — a shared key means two counterparties' exposures will be merged in any aggregate, making the figure structurally invalid | **(¶33)**
  - *validity* — Every exposure record carries a counterparty identifier that resolves to an active record in the counterparty master | Count of exposure records whose counterparty identifier is null, blank, or absent from the party master | Target: zero — an unresolvable identifier is not a missing field, it is a missing join; the record drops out of every aggregate silently | **(¶33, ¶40)**
  - *consistency* — The same counterparty carries the same identifier in all source systems contributing to the risk aggregate | Count of counterparties with more than one active identifier across contributing systems | Target: zero — cross-system inconsistency means the same counterparty appears as multiple entities in any aggregate | **(¶33)**

---

**CDE-02 — Legal Entity Identifier (Own Entity)**

- **Definition:** A unique, persistent identifier for each legal entity within the banking group at which a position or exposure is booked. This is the bank's own entity code, not the counterparty's. It is the key that attributes a position to a specific subsidiary, branch, or booking entity for group consolidation and solo-entity reporting.
- **Why critical:** Group-level aggregation requires summing exposures across all legal entities. Subsidiary-level reporting requires partitioning them. Neither is possible if the booking entity cannot be identified unambiguously. Acquisitions and divestitures (¶29(b)) introduce new entities that must be folded into the structure. Without this key, the group aggregate is either incomplete (entities omitted) or incorrect (positions attributed to the wrong entity).
- **Risk types:** Cross-cutting (all risk types, all Principles requiring group-level aggregation)
- **Criticality:** **3.** Without this element, the aggregate risk exposure at group level cannot be computed at all, because positions in subsidiary systems cannot be attributed to a legal entity and therefore cannot be correctly consolidated — entities are either omitted or merged incorrectly.
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (¶41) — the banking group scope; Principle 4 header — *"capture and aggregate all material risk data across the banking group"*
- **Search terms:** legal entity ID, entity code, booking entity, subsidiary code, LEI (own entity), organisational unit ID, branch code, consolidated entity identifier, MFI code
- **Data quality requirements:**
  - *validity* — Every position or exposure record carries a legal entity identifier that resolves to an active, in-scope entity in the group entity register | Count of position records with a null, blank, or unregistered entity code | Target: zero — an unresolvable entity code means the position is excluded from group aggregation with no alert | **(¶33, ¶40)**
  - *completeness* — All legal entities within the consolidation perimeter are represented in the entity master and receive positions | Count of in-scope legal entities absent from the entity master; count of entities for which no positions were received in the reporting period | Target: zero absent entities — an omitted entity silently understates group exposure | **(¶43)**
  - *consistency* — The same entity carries the same code in all systems contributing to the consolidated aggregate | Count of entities with more than one active code across contributing systems | Target: zero — inconsistency produces double-counting or omission in consolidation | **(¶33)**

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary amount representing the gross risk exposure on a position before application of collateral, netting, or credit risk mitigants. Denominated in a stated currency. This is the primary quantity that risk aggregates — totals, concentrations, and limit utilisation figures — are built from.
- **Why critical:** Every risk aggregate — total credit exposure, counterparty exposure, trading position — is a function of this amount. If it is wrong, every downstream aggregate is wrong. ¶56 explicitly frames accuracy requirements in terms of whether omission or misstatement would influence risk decisions; the gross exposure amount is the single quantity where misstatement most directly distorts a risk figure.
- **Risk types:** Credit, counterparty, market, concentration
- **Criticality:** **3.** Without this element, the aggregate exposure figure X cannot be computed at all, because there is no monetary quantity to sum — the aggregate has no input.
- **Driven by:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 7 (¶52) — *"Risk management reports should be accurate and precise"*; Principle 5 (¶46(a)) — *"The aggregated credit exposure to a large corporate borrower"* as a named critical risk
- **Search terms:** exposure amount, gross exposure, notional amount, face value, outstanding balance, drawn amount, mark-to-market value, current exposure, EAD (exposure at default), notional principal
- **Data quality requirements:**
  - *accuracy* — The exposure amount on each record agrees with the value held in the system of record (origination system, trading system, or accounting ledger) as of the same position date | Sum of absolute differences between risk system exposure amounts and corresponding system-of-record values, expressed as a percentage of total portfolio | Threshold set by materiality as defined under ¶56: the bank's risk committee determines the threshold below which misstatement would not influence a risk decision; the threshold is not zero because ¶56 explicitly applies accounting-materiality analogies | **(¶56, ¶36(c))**
  - *validity* — Every exposure record carries a non-null, non-negative gross exposure amount (or a documented zero for an instrument with known zero balance) | Count of records with null or negative amounts, excluding documented zero-balance instruments | Target: zero undocumented nulls or negatives — these represent structural data failures, not rounding | **(¶40)**
  - *completeness* — Off-balance-sheet exposures are captured in addition to on-balance-sheet exposures | Count of off-balance-sheet facility types (commitments, guarantees, derivatives) present in the origination system but absent from the risk aggregate | Target: zero absent facility types — ¶41 explicitly requires off-balance-sheet coverage | **(¶43, ¶41)**

---

**CDE-04 — Risk Type Classification**

- **Definition:** A controlled-vocabulary code that classifies each exposure or position by the primary risk type it represents — credit risk, market risk, liquidity risk, operational risk, counterparty credit risk — using the bank's defined taxonomy. This is the field that routes an exposure to the correct risk calculation, risk report section, and limit framework.
- **Why critical:** Principle 7 (¶53(b)) requires an inventory of validation rules applied to quantitative information. Principle 8 (¶57) requires reports to cover all significant risk areas. Neither is achievable if the classification that assigns an exposure to a risk area is absent or incorrect. A misclassified exposure appears in the wrong risk report and is absent from the correct one — it is not merely imprecisely reported, it is invisible to the appropriate risk manager.
- **Risk types:** Cross-cutting (classifies all risk types)
- **Criticality:** **2.** The total exposure figure is produced, but it cannot be correctly partitioned by risk type — credit risk is overstated or understated relative to market risk, and the report covering each risk type is incomplete or inflated.
- **Driven by:** Principle 7 (¶53(b)) — *"Automated and manual edit and reasonableness checks, including an inventory of the validation rules that are applied to quantitative information"*; Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas"*; Principle 2 (¶33) — *"integrated data taxonomies"*
- **Search terms:** risk type, risk category, risk classification, asset class, risk flag, risk bucket, risk type code, Basel risk category
- **Data quality requirements:**
  - *validity* — Every exposure record carries a risk type code drawn from the approved, governed taxonomy | Count of records with null, blank, or non-standard risk type codes | Target: zero — a null or free-text entry bypasses all downstream routing and validation rules | **(¶40, ¶33)**
  - *consistency* — The same instrument type is classified to the same risk type code across all source systems contributing to the aggregate | Count of instrument types that carry different risk type codes in different contributing systems | Target: zero — cross-system inconsistency creates double-counting in one risk report and a gap in another | **(¶36(c))**
  - *completeness* — All named risk types (credit, market, liquidity, operational, counterparty) are represented in the taxonomy and populated in the risk data | Count of regulatory-required risk types absent from the taxonomy or absent from any exposure records | Target: zero — an absent risk type means an entire category is invisible in risk reports, directly contradicting ¶57 | **(¶43)**

---

**CDE-05 — Business Line**

- **Definition:** A controlled-vocabulary code identifying the business line (e.g., retail banking, corporate banking, trading, wealth management, treasury) responsible for or generating an exposure. It is one of the explicit aggregation dimensions named in Principle 4.
- **Why critical:** Principle 4's header explicitly names business line as a required slice. Principle 6 (¶50) gives a concrete example — country credit exposures *"across all business lines and geographic areas"* — making this a directly named requirement for ad hoc aggregation. Without this dimension, the bank cannot satisfy a supervisory query that requests exposure by business line, and cannot identify business-line concentrations.
- **Risk types:** Credit, market, concentration, cross-cutting
- **Criticality:** **2.** Aggregate exposure figures can be produced, but they cannot be sliced by business line — concentration analysis by business line is unavailable, and ad hoc supervisory queries requiring this dimension cannot be answered.
- **Driven by:** Principle 4 header — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*
- **Search terms:** business line, business unit, line of business, LOB, product line, division code, segment code, desk code
- **Data quality requirements:**
  - *validity* — Every exposure record carries a business line code drawn from the approved taxonomy | Count of records with null, blank, or non-taxonomy business line codes | Target: zero — an unmapped record cannot be assigned to any business line slice, making the aggregate for that slice incomplete | **(¶40)**
  - *completeness* — All active business lines are represented in the taxonomy and receive allocations | Count of business lines active in the bank's organisational structure but absent from the taxonomy or receiving zero allocations in the reporting period | Target: zero absent business lines — an omitted business line means its exposures are unattributed | **(¶43)**

---

**CDE-06 — Geography / Country**

- **Definition:** A controlled-vocabulary code identifying the country or geographic region of risk for each exposure — typically the country of the borrower or counterparty's domicile, the country of the issuer, or the country of the collateral, depending on the risk type. It is one of the explicit aggregation dimensions named in Principle 4 and is specifically named in the Principle 6 example.
- **Why critical:** Country/geographic concentration is a core supervisory concern (¶50 names country credit exposures as a specific example of required ad hoc aggregation capability). Without a populated, consistent geography code, the bank cannot aggregate exposures to a country or region on demand — precisely the capability stress scenarios require.
- **Risk types:** Credit, market, concentration, cross-cutting
- **Criticality:** **2.** Aggregate exposures can be produced, but they cannot be sliced by geography — the bank cannot answer a supervisory query for country-level exposures or identify geographic concentrations.
- **Driven by:** Principle 4 header — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*
- **Search terms:** country code, country of risk, geography code, region code, jurisdiction, booking location, country of domicile, ISO country code, geographic segment
- **Data quality requirements:**
  - *validity* — Every exposure record carries a geography code from the approved, standardised list (e.g., ISO 3166) | Count of records with null, blank, or non-standard geography codes | Target: zero — an invalid code means the exposure falls outside every geographic slice | **(¶40)**
  - *consistency* — The same counterparty or issuer is assigned the same country code across all contributing systems | Count of counterparties or issuers assigned different country codes in different systems | Target: zero — inconsistency means geographic concentration is understated in one system and overstated in another | **(¶36(c))**

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** A controlled-vocabulary code classifying the counterparty or issuer by economic sector or industry (e.g., using NACE, SIC, GICS, or the bank's internal sector taxonomy). It is the third of the three aggregation dimensions Principle 4 names alongside business line and geography.
- **Why critical:** ¶50 directly names industry credit exposures as an example of required ad hoc aggregation. ¶57 names industry sector as a required component within credit risk reporting (*"single name, country and industry sector for credit risk"*). Principle 8 drives this as a CDE while its report-content obligations remain outside catalog scope (see Section 4). Without an industry code, concentration by sector cannot be measured and supervisory ad hoc queries on sector exposure cannot be answered.
- **Risk types:** Credit, concentration
- **Criticality:** **2.** Aggregate credit exposure is produced, but it cannot be sliced by industry — sector concentration cannot be identified and supervisory queries requiring industry-level aggregation cannot be answered.
- **Driven by:** Principle 4 header — *"Data should be available by … industry … and other groupings"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*
- **Search terms:** industry code, sector code, industry classification, NACE code, SIC code, GICS sector, obligor industry, counterparty sector, sector classification
- **Data quality requirements:**
  - *validity* — Every credit exposure record carries an industry code from the approved taxonomy | Count of credit exposure records with null, blank, or non-taxonomy industry codes | Target: zero — unclassified records fall outside all industry slices, making every sector aggregate potentially incomplete | **(¶40)**
  - *completeness* — The industry taxonomy covers all sectors in which the bank has material exposure | Count of counterparty industry types active in the portfolio but absent from the taxonomy | Target: zero absent sectors — an omitted sector means all its exposures are unclassified | **(¶43)**

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The business date as of which an exposure or position is stated. It is the temporal key that anchors every risk aggregate: a total credit exposure figure, a market position, or a liquidity measure is only meaningful when it is known as of a specific date.
- **Why critical:** Every aggregation function — sum, average, peak — operates over records sharing the same as-of date. Records with the wrong date are either double-counted (if included in the wrong day's aggregate) or omitted (if excluded from the correct day's aggregate). Principle 5 (¶44–¶47) requires timeliness, which cannot be assessed unless the date the data represents is explicit and correct. A stress-scenario query for exposures *"as of a specified date"* (¶50) is unanswerable if the date field is missing or inconsistent.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality:** **3.** Without a correct as-of date, the aggregate figure X cannot be computed for the correct reporting period at all, because there is no reliable basis for selecting which records belong to the aggregate being reported — the temporal boundary of the aggregate is undefined.
- **Driven by:** Principle 5 (¶44) — *"A bank's risk data aggregation capabilities should ensure that it is able to produce aggregate risk information on a timely basis"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (¶52) — reports must be accurate and precise
- **Search terms:** position date, as-of date, trade date, value date, reporting date, snapshot date, extraction date, effective date, reference date
- **Data quality requirements:**
  - *validity* — Every position record carries a non-null as-of date that falls within the valid reporting calendar | Count of records with null, future, or implausible as-of dates (e.g., dates before the bank's founding or more than one business day in the future) | Target: zero — a null or invalid date means the record cannot be assigned to any reporting period | **(¶40)**
  - *timeliness* — Risk data for each risk type is available within the bank-defined frequency requirement for that risk type, including the compressed timelines applicable during stress | Elapsed time between the close of the business day and availability of a complete, reconciled position dataset; measured per risk type; compared against the bank-defined SLA | Threshold: the bank-defined SLA per risk type per ¶45 and ¶47 — critical risks (large borrower credit, counterparty, trading, liquidity) have more demanding timelines than retail; the SLA is set by the risk committee and reviewed by supervisors | **(¶44–¶47)**
  - *consistency* — The as-of date on a risk record matches the as-of date on the corresponding accounting record for the same position | Count of position records where the risk-system as-of date differs from the accounting-system as-of date for the same trade or facility | Target: zero — a date mismatch means the reconciliation in ¶36(c) is performed across different points in time, making it meaningless | **(¶36(c))**

---

**CDE-09 — General Ledger / Source System Reconciliation Key**

- **Definition:** The identifier (or composite key) that links a risk record to its corresponding record in the general ledger or system of record — for example, a trade ID, facility ID, or account number that appears in both the risk system and the accounting or origination system. This is the field that makes ¶36(c) reconciliation mechanically possible.
- **Why critical:** ¶36(c) requires that risk data be reconciled with accounting data. Reconciliation is not a narrative statement — it is a record-level comparison that requires a shared key. Without this key, there is no mechanical way to match a risk record to its accounting counterpart and confirm that the exposure amount, classification, and date agree. An unverifiable risk figure is not a compliant one under BCBS 239, because ¶36(c) makes reconcilability a condition of accuracy. This is the element most commonly absent from risk data registers and most immediately cited in supervisory findings.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality:** **3.** Without this element, the aggregate risk figure X cannot be reconciled to the system of record at all, because there is no key by which to join risk records to accounting records — the accuracy required by ¶36(c) cannot be evidenced, and an unverifiable figure is not a compliant one.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** trade ID, facility ID, account number, deal ID, position ID, GL account reference, booking reference, source system key, origination system ID, accounting reference
- **Data quality requirements:**
  - *validity* — Every risk record carries a non-null reconciliation key that resolves to an active record in the corresponding source or accounting system | Count of risk records with null, blank, or unresolvable reconciliation keys | Target: zero — an unresolvable key means the record cannot be reconciled; its accuracy cannot be evidenced | **(¶36(c), ¶40)**
  - *uniqueness* — Each reconciliation key uniquely identifies one position or exposure in both the risk system and the source system (or a deliberate one-to-many relationship is documented) | Count of risk records sharing a reconciliation key where a one-to-one relationship is expected; count of source-system records with no matching risk record | Target: zero unexplained duplicates and zero unexplained orphans — duplicates create double-counting; orphans mean source positions are absent from the risk aggregate | **(¶33, ¶36(c))**
  - *completeness* — Every position in the source system that is within scope has a corresponding record in the risk system | Count of source-system positions with no matching risk record (population completeness); expressed as a count and as a percentage of total source-system exposure | Threshold: materiality as defined per ¶56 — the bank's risk committee defines the monetary threshold below which an omission does not influence a risk decision; zero is the aspirational target but the regulation permits a documented materiality tolerance | **(¶43, ¶56)**

---

**CDE-10 — Source System / Provenance Flag**

- **Definition:** A code or attribute on each risk record identifying the system from which it originated — for example, a named trading system, loan origination system, treasury system, or a flag indicating manual/spreadsheet input or end-user computing (EUC) origin. This is the field that makes ¶36(d) and ¶39 operational: it tells a data quality monitor where the data came from and whether enhanced scrutiny is warranted.
- **Why critical:** ¶39 requires documentation of all aggregation processes, including the *"criticality"* of manual workarounds. ¶36(b) requires effective mitigants for manual and EUC inputs. Neither can be operationalised if the system monitoring the data does not know which records are manual. A catalog that cannot flag EUC-sourced records cannot route them to enhanced validation, cannot report on the proportion of the risk aggregate derived from manual processes, and cannot demonstrate that the mitigants ¶36(b) requires are actually applied.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality:** **2.** The aggregate figure is produced, but the bank cannot demonstrate that the controls required for manual and EUC-sourced data (¶36(b)) have been applied, and cannot report on the proportion of the aggregate that is manually sourced — the provenance chain required by ¶39 is broken.
- **Driven by:** Principle 3 (¶36(b)) — *"effective mitigants in place (eg end-user computing policies and procedures)"*; Principle 3 (¶36(d)) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (¶39) — *"document and explain all of their risk data aggregation processes whether automated or manual"*
- **Search terms:** source system, data source, system of origin, EUC flag, manual input flag, feed code, data provider, upstream system, automated flag, spreadsheet flag, end-user computing
- **Data quality requirements:**
  - *validity* — Every risk record carries a non-null source system code drawn from the approved system inventory | Count of records with null, blank, or unregistered source system codes | Target: zero — a null source code means the record's provenance is unknown; no control can be applied and no manual-process documentation can reference it | **(¶39, ¶40)**
  - *completeness* — All source systems contributing to the risk aggregate are registered in the system inventory, including all EUC and manual feed types | Count of distinct source system codes appearing in risk records but absent from the system inventory | Target: zero — an unregistered source system means an entire feed is undocumented, directly contradicting ¶39 | **(¶43)**
  - *accuracy* — The proportion of the total risk aggregate derived from EUC or manual sources is measured and reported, enabling senior management awareness of reliance on manual processes per ¶30 | Percentage of gross exposure amount sourced from EUC or manual-flagged records; reported per reporting period | Threshold: no absolute threshold — this is a monitoring and disclosure requirement, not a correctness threshold; however, a trend toward increasing manual sourcing without documented mitigants triggers escalation per ¶40 | **(¶30, ¶40)**

---

**CDE-11 — Collateral / Credit Risk Mitigant Identifier**

- **Definition:** An identifier linking an exposure to any collateral, guarantee, netting agreement, or other credit risk mitigant that reduces the net exposure. Relevant where net exposure figures appear in risk reports alongside gross figures, and where limits are monitored on a net basis.
- **Why critical:** Principle 8 (¶58) requires reports to *"identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance."* Net exposure — gross minus mitigants — is the figure on which many credit limits are monitored. If the mitigant identifier is absent or broken, net exposure cannot be calculated and limit utilisation cannot be assessed. This does not invalidate the gross aggregate, but it makes the net aggregate — which drives limit monitoring and concentration reporting — incorrect.
- **Risk types:** Credit, counterparty
- **Criticality:** **2.** The gross aggregate is produced and is valid. The net aggregate, and all limit-utilisation figures derived from it, cannot be correctly computed — they are either overstated (collateral ignored) or understated (collateral double-applied).
- **Driven by:** Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas"* including risk-related measures; Principle 8 (¶58) — *"provide information in the context of limits and risk appetite/tolerance"*; Principle 4 (¶41) — complete capture of all material exposures including mitigants
- **Search terms:** collateral ID, collateral agreement, netting agreement, credit support annex, CSA, guarantee reference, CRM identifier, mitigant code, collateral pool ID, ISDA master agreement ID
- **Data quality requirements:**
  - *validity* — Every collateral or netting record carries a non-null identifier that resolves to an active agreement in the collateral management system | Count of collateral records with null or unresolvable identifiers | Target: zero — an unresolvable collateral record cannot be applied to an exposure; the net figure is overstated | **(¶40)**
  - *completeness* — All collateral agreements that are active as of the position date are captured in the risk data | Count of collateral agreements active in the collateral management system but absent from the risk aggregate | Threshold: materiality per ¶56 — the risk committee determines the monetary threshold below which an omitted agreement does not influence a net exposure decision | **(¶43, ¶56)**
  - *timeliness* — Collateral valuations are updated at the frequency required for the risk type they support (e.g., daily mark-to-market for derivative CSAs) | Elapsed time since the last collateral valuation update per agreement, compared against the bank-defined frequency for that collateral type | Threshold: the bank-defined SLA per collateral type per ¶45; derivative collateral is named in ¶46(b) as a critical risk | **(¶44–¶47)**

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Counterparty Exposure Reconciliation Across Systems**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-09 (GL / Source System Reconciliation Key)
- **Rule intent:** The total gross exposure to any individual counterparty, summed across all contributing systems using the counterparty identifier as the join key, must agree with the corresponding figure derived from the general ledger or accounting system within the materiality tolerance. This is the cross-system, cross-element check that operationalises ¶36(c): it is not enough that each individual record carries a valid counterparty identifier and a valid amount — the aggregate must reconcile to the accounting source.
- **Measurement:** For each counterparty in scope, compute the difference between (a) the total gross exposure in the risk aggregate and (b) the total exposure in the corresponding GL or accounting system. Express the difference as an absolute amount and as a percentage of the accounting-system total. Report the count of counterparties where the difference exceeds the materiality threshold.
- **Threshold and why:** Threshold set by materiality as defined under ¶56 — the risk committee defines the monetary amount or percentage below which a discrepancy would not influence a risk decision. Zero tolerance would be aspirational and the regulation does not require it; however, any counterparty where the discrepancy exceeds materiality must be escalated and remediated under ¶40. The threshold must be formally documented and approved.
- **Why this cannot be expressed at the level of a single CDE:** The reconciliation requires a join across two systems using the reconciliation key (CDE-09), a grouping on the counterparty identifier (CDE-01), and a comparison of summed amounts (CDE-03). No single-element monitor can perform this — it requires all three elements and two systems to be involved simultaneously.
- **Authorising paragraphs:** **(¶36(c))** — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; **(¶40)** — measure, monitor, escalate; **(¶56)** — materiality basis for the threshold

---

**XDQ-02 — Cross-System Counterparty Identity Resolution**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-02 (Own Legal Entity Identifier), CDE-09 (GL / Source System Reconciliation Key), CDE-10 (Source System / Provenance Flag)
- **Rule intent:** The same real-world counterparty must resolve to the same counterparty identifier in every contributing source system. Where a counterparty is booked in multiple systems (e.g., the same corporate borrower appears in both the corporate loan system and the derivatives platform), those records must carry a common, resolvable identifier. This check detects fragmentation in the counterparty master — the most common cause of concentration understatement. ¶33 requires single identifiers precisely to prevent this.
- **Measurement:** Using a defined matching algorithm (exact match on LEI, name-and-domicile fuzzy match, or a maintained golden-source mapping table): count of counterparties that appear in more than one source system (identified via CDE-10) with different counterparty identifiers and no documented mapping to a common golden-source record; count of cross-system exposure pairs that cannot be linked to a single counterparty record.
- **Threshold and why:** Target: zero unresolved cross-system counterparty fragments. This is not a materiality-calibrated threshold — a single fragmented identity can conceal a concentration that breaches a limit, regardless of its monetary size. ¶33 does not qualify the requirement with materiality. Any fragment without a documented, approved mapping is a defect.
- **Why this cannot be expressed at the level of a single CDE:** The check requires comparing identifiers for the same counterparty across multiple source systems, which requires knowing which systems contributed each record (CDE-10) and which entity the record belongs to (CDE-02). No single-element validation can detect a cross-system fragmentation; it requires a comparison across the combined output of all contributing feeds.
- **Authorising paragraphs:** **(¶33)** — *"use of single identifiers and/or unified naming conventions for data including … counterparties"*; **(¶40)** — measure, monitor, escalate

---

## 4. Out of Scope

This section is not an apology for the catalog's limitations. It is a precise statement of what Principles 1–11 require that no CDE register or data quality monitoring programme can deliver. A bank that mistakes catalog coverage for BCBS 239 compliance has a governance gap.

---

### Principle 1 — Governance framework and board ownership (¶27–¶31)

**What the catalog cannot deliver:** Principle 1 requires board and senior management approval of the risk data aggregation framework (¶28), awareness of aggregation limitations (¶30–¶31), service level agreements for outsourced and in-house processes (¶27), and independent validation of the bank's compliance (¶29(a)). These are governance and accountability obligations. A data catalog can make metadata visible and flag data quality defects; it cannot create a board-approved framework, it cannot commission or execute an independent validation, and it cannot evidence that senior management has reviewed the limitations it is required to understand. **What is needed instead:** Board resolution or equivalent formal approval of the framework; documented SLAs between data owners and risk consumers; an independent validation programme (typically Internal Audit or a specialist function) that tests the CDEs and DQ controls in the catalog against actual risk output.

---

### Principles 8–9 — Report comprehensiveness and clarity (¶57–¶69)

**What the catalog cannot deliver:** Principle 8 requires that reports cover all significant risk areas and components (¶57), identify emerging concentrations in the context of limits (¶58), and include forward-looking forecasts and stress tests (¶60). Principle 9 requires that reports communicate clearly to their recipients, be tailored to the board versus senior management, and be confirmed periodically as relevant (¶69). These are report-design, narrative-quality, and recipient-engagement obligations. A catalog can ensure the data elements needed to populate a report are defined and governed; it cannot write, review, or validate the report itself, cannot assess whether a board member finds it comprehensible, and cannot substitute for the periodic confirmation that ¶69 requires. **What is needed instead:** A formal risk reporting framework with defined report templates, owner responsibilities, and periodic recipient feedback processes; a report inventory linked (but not identical) to the CDE register.

**The split between what drives a CDE and what remains out of scope:** Principle 8 (¶57) names industry sector as a required reporting dimension. This drives CDE-07 (Industry / Sector Classification) because having the data element populated is a prerequisite for producing the report. However, whether the resulting report is comprehensive, clearly written, and appropriately tailored to its recipient is a Principle 8 obligation that the CDE register does not address. Both are genuine BCBS 239 requirements; they sit in different governance domains.

---

### Principle 10 — Report frequency and stress-scenario testing (¶70–¶71)

**What the catalog cannot deliver:** Principle 10 requires the bank to set and periodically review frequency requirements for each report (¶70), and to *routinely test* its ability to produce accurate reports within those timeframes under stress (¶70). CDE-08 (Position / As-Of Date) includes a timeliness check for data availability, and this partially supports frequency compliance. However, the obligation to test report production within stress timelines is a systems-and-process rehearsal, not a data quality monitor — it requires running the full aggregation pipeline under simulated stress conditions and confirming the output meets accuracy and completeness standards within the compressed timeline. A catalog cannot simulate or measure this. **What is needed instead:** Documented frequency requirements per report and risk type; periodic stress-run exercises with outcome documentation; a business continuity plan that explicitly includes risk data aggregation (¶32).

---

### Principle 11 — Report distribution and confidentiality (¶72–¶74)

**What the catalog cannot deliver:** Principle 11 requires procedures for rapid collection, analysis, and dissemination of risk reports to appropriate recipients (¶72), and periodic confirmation that recipients receive timely reports (¶73). These are workflow, access-control, and distribution obligations. A catalog can record data ownership and stewardship roles, but it cannot manage report distribution lists, enforce confidentiality controls over transmitted reports, or confirm that a given board member received a report on time. **What is needed instead:** A report distribution management framework with delivery confirmation; information security controls over report channels; access governance (which may be linked to but is not substituted by catalog ownership records).

---

### Principles 3 and 7 — Report-level reconciliation and exception management (¶53, ¶39)

**Partial coverage, partial gap:** Principle 3 (¶39) and Principle 7 (¶53(a)–(c)) require not only that reconciliation keys exist (addressed by CDE-09 and XDQ-01) but that the bank maintains a formal process for identifying, reporting, and explaining data errors via exceptions reports (¶53(c)), and that there is a documented inventory of validation rules applied to quantitative information (¶53(b)). A catalog can hold the CDE definitions and run the DQ checks; it cannot operate the exceptions management workflow (tracking who owns the exception, what the root cause was, whether it recurred, and what the escalation outcome was). **What is needed instead:** An integrated data exceptions management process — which may be triggered by catalog alerts but must include assignment, root cause analysis, remediation tracking, and sign-off by the relevant data owner and risk manager.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | **3** | P2 (¶33), P4 (¶41), P5 (¶46) | Uniqueness, Validity, Consistency |
| CDE-02 | Legal Entity Identifier (Own) | **3** | P2 (¶33), P4 header, P4 (¶41) | Validity, Completeness, Consistency |
| CDE-03 | Gross Exposure Amount | **3** | P3 (¶36(a)), P7 (¶52), P5 (¶46) | Accuracy, Validity, Completeness |
| CDE-04 | Risk Type Classification | **2** | P7 (¶53(b)), P8 (¶57), P2 (¶33) | Validity, Consistency, Completeness |
| CDE-05 | Business Line | **2** | P4 header, P6 (¶50) | Validity, Completeness |
| CDE-06 | Geography / Country | **2** | P4 header, P6 (¶50) | Validity, Consistency |
| CDE-07 | Industry / Sector Classification | **2** | P4 header, P6 (¶50), P8 (¶57) | Validity, Completeness |
| CDE-08 | Position / As-Of Date | **3** | P5 (¶44–¶47), P6 (¶50), P7 (¶52) | Validity, Timeliness, Consistency |
| CDE-09 | GL / Source System Reconciliation Key | **3** | P3 (¶36(c)), P7 (¶53(a)) | Validity, Uniqueness, Completeness |
| CDE-10 | Source System / Provenance Flag | **2** | P3 (¶36(b)), P3 (¶36(d)), P3 (¶39) | Validity, Completeness, Accuracy |
| CDE-11 | Collateral / Credit Risk Mitigant Identifier | **2** | P8 (¶57–¶58), P4 (¶41) | Validity, Completeness, Timeliness |

**Cross-cutting requirements**

| ID | Spans | Criticality driver | Authorising paragraphs |
|---|---|---|---|
| XDQ-01 | CDE-01, CDE-03, CDE-09 | Reconciliation of risk aggregate to GL — unresolved differences evidence an accuracy failure | ¶36(c), ¶40, ¶56 |
| XDQ-02 | CDE-01, CDE-02, CDE-09, CDE-10 | Cross-system identity resolution — fragmentation directly understates concentration | ¶33, ¶40 |

**Criticality distribution:** CDE-01, CDE-02, CDE-03, CDE-08, CDE-09 are rated **3** (five elements). All remaining CDEs are rated **2**. No element is rated **1** — no candidate in this register is purely interpretive context; each one, if absent or wrong, degrades an aggregate or breaks a control.