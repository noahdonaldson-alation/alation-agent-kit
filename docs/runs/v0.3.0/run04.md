# BCBS 239 — Data Catalog Governance Analysis

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a precondition for governance.** The regulation requires that boards and senior management can rely on aggregated risk data to make critical decisions, particularly during stress and crisis. The entire framework rests on the premise that a figure that cannot be produced quickly and accurately is worse than useless — it gives false confidence. (¶35: *"risk management reports reflect the risks in a reliable way (ie meeting data aggregation expectations is necessary to meet reporting expectations)"*)

- **A single, authoritative, documented data architecture.** Banks must build integrated data taxonomies, unified naming conventions, and single identifiers for legal entities, counterparties and accounts — across the whole banking group, not just one system. (¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions"*)

- **Accuracy and integrity with minimised manual intervention.** Risk data must be reconciled against accounting sources, supported by a concept dictionary ensuring consistent definitions, and produced largely automatically — with every manual workaround documented and its materiality assessed. (¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; ¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"*)

- **Completeness across all material exposures and dimensions.** Aggregation must cover all material risks — including off-balance-sheet — and must be sliceable by business line, legal entity, asset type, industry, region and other groupings. Gaps must be identified, explained and shown not to be critical. (¶41: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; ¶43: *"any exceptions identified and explained"*)

- **Timeliness sufficient for stress conditions.** Systems must be capable of producing aggregated risk data rapidly during stress or crisis across all critical risk types, including intraday where required. (¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks"*)

- **Accountability and ownership embedded in governance.** Roles and responsibilities for data ownership and quality must be formally assigned to both business and IT functions, and senior management must understand the limitations that prevent full aggregation. (¶34, ¶30)

**Who and what it applies to**

BCBS 239 applies directly to **Global Systemically Important Banks (G-SIBs)** as identified by the FSB, with national supervisors expected to apply the principles more broadly to domestically significant institutions. The principles operate at the **banking group** level — they apply across legal entities, subsidiaries, business lines and geographies. The regulation is addressed to the **bank as an institution**, including its board, senior management, risk, finance and IT functions. Principles 12–14, which address supervisors, are excluded from this analysis per the task scope.

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** The unique, authoritative identifier that resolves a counterparty — borrower, issuer, derivatives counterpart, or other obligor — to a single entity record across all source systems, legal entities, and risk types within the banking group. This is the institution's internal master identifier, which may map to LEI or other external codes but is defined by the bank's own data architecture.
- **Why critical:** Without a consistent counterparty identifier, exposures recorded across trading systems, loan origination platforms, and collateral systems cannot be joined into an aggregate view. The identifier is the structural joining key that makes group-level credit and counterparty exposure aggregation possible at all. It is also required to identify concentrations and to respond to ad hoc supervisory queries about single-name exposures.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3.** Without this element, the aggregate credit and counterparty exposure to a single obligor across the banking group cannot be computed at all, because there is no key on which to join records from disparate systems. What is produced instead is a partial sum with unknown omissions — not an approximation of the true aggregate, but an unverifiable fragment.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 5 (¶46(b)) — *"Counterparty credit risk exposures, including, for example, derivatives"* named as critical risk requiring rapid aggregation
- **Search terms:** counterparty ID, client ID, obligor ID, legal entity identifier, LEI, customer master ID, party ID, counterparty master record, golden record counterparty
- **Data quality requirements:**
  - *uniqueness* — Each distinct counterparty must resolve to exactly one authoritative identifier across all source systems; no two active records in the counterparty master should represent the same real-world entity | count of duplicate counterparty records by identity-matching key (name, registration number, LEI) | target: 0 confirmed duplicates in the master; all candidate duplicates under active review
  - *completeness* — Every exposure record in every risk system must carry a populated, non-null counterparty identifier that resolves to a record in the counterparty master | count of exposure records with null or unresolvable counterparty identifier, as a percentage of total exposure records and as a percentage of total notional exposure value | target: 0% null; unresolved records reported to data owner within one business day
  - *consistency* — The counterparty identifier used in risk systems must match the identifier used in the general ledger and credit limit system for the same obligor | count of counterparty identifiers that appear in risk data but have no matching record in the authoritative counterparty master | target: 0% unmatched on any reporting date

---

**CDE-02 — Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier for the bank's own legal entity — the subsidiary or branch — in which a transaction or exposure is booked. This is the bank's own internal legal entity code, distinct from the counterparty's identifier. It may map to LEI or internal entity hierarchy codes, but its role here is to identify which part of the banking group owns the exposure.
- **Why critical:** Group consolidation and subsidiary reporting depend entirely on correctly attributing every exposure to a booking entity. An incorrectly coded booking entity either double-counts an exposure at group level or excludes it from the relevant subsidiary report. It is also the dimension through which legal and cross-jurisdictional aggregation constraints (¶30) apply.
- **Risk types:** Credit, market, liquidity, cross-cutting
- **Criticality: 3.** Without a valid booking entity identifier on every exposure record, the aggregate risk exposure of any subsidiary or legal entity within the banking group cannot be computed at all, because records cannot be correctly attributed for consolidation — they either cannot be assigned to an entity or must be arbitrarily assigned, producing a structurally incorrect aggregate.
- **Driven by:** Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures"* across the banking group; Principle 2 (¶33) — *"integrated data taxonomies and architecture across the banking group … single identifiers … for … legal entities"*
- **Search terms:** legal entity code, booking entity, entity ID, subsidiary code, branch code, organisational unit, LEI (own entity), legal entity hierarchy, group entity master
- **Data quality requirements:**
  - *validity* — Every booking entity code on an exposure record must correspond to a currently active entry in the authoritative legal entity master; codes for dissolved or merged entities must not appear on current-period records | count of exposure records carrying an entity code not present or marked inactive in the legal entity master | target: 0% invalid codes on current-period records
  - *completeness* — Every exposure record must carry a non-null booking entity identifier | count of exposure records with null booking entity code, as percentage of total records and total notional value | target: 0% null
  - *consistency* — The booking entity on a risk record must match the booking entity on the corresponding general ledger entry for the same transaction | count of risk-to-GL pairs where booking entity codes differ | target: 0% mismatch; exceptions escalated same day

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary amount representing a position's risk exposure before the application of any netting, collateral, or credit risk mitigation. This is the primary quantity that is summed, sliced, and compared against limits in all risk aggregation processes. Depending on risk type, this may be notional value, mark-to-market value, drawn balance, or outstanding principal.
- **Why critical:** This is the number being aggregated. Every aggregate risk figure — total credit exposure to a counterparty, total market risk by asset class, total liquidity outflows — is a function of this element. Errors here directly corrupt the aggregate rather than merely affecting its classification.
- **Risk types:** Credit, market, liquidity, counterparty, concentration, cross-cutting
- **Criticality: 3.** Without a valid gross exposure amount, the aggregate risk exposure figure cannot be computed at all, because there is no monetary quantity to sum. A null or zero value is not an approximation — it produces a structurally false aggregate regardless of how well all other dimensions are populated.
- **Driven by:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*; Principle 5 (¶46(a)) — *"The aggregated credit exposure to a large corporate borrower"* named as a critical risk requiring rapid aggregation
- **Search terms:** notional amount, exposure at default, drawn balance, mark-to-market value, outstanding principal, gross exposure, position size, current exposure, EAD, MtM
- **Data quality requirements:**
  - *accuracy* — The gross exposure amount on a risk record must agree to the corresponding amount in the system of record (loan system, trading system, or GL) within defined tolerances | sum of absolute differences between risk-system exposure amounts and system-of-record amounts, by exposure type and reporting date | target: total unexplained variance < materiality threshold (defined by risk and finance jointly); zero unexplained items above individual materiality threshold
  - *completeness* — No exposure record may carry a null or zero gross exposure amount unless the zero is economically valid (e.g. expired option with zero residual value, with that status coded explicitly) | count of exposure records with null or blank exposure amount; count with zero amount where instrument type does not permit zero | target: 0% null; zero-value exceptions require documented justification
  - *timeliness* — Gross exposure amounts must reflect positions as of the stated position date by the time the risk report is produced; stale values from a prior position date constitute a material accuracy failure | count of exposure records where the source-system timestamp lags the stated position date by more than the permitted tolerance for each risk type | target: defined per risk type; intraday for trading book; end-of-day for banking book

---

**CDE-04 — Risk Type Classification**

- **Definition:** The controlled vocabulary attribute that assigns each exposure or position to a primary risk category — at minimum: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk. May be hierarchical, with sub-types such as single-name credit versus country credit versus sector credit.
- **Why critical:** This classification determines which aggregation logic, limit framework, and risk report the exposure feeds. An exposure mis-classified as market risk when it is credit risk will appear in the wrong aggregate, corrupt both the credit aggregate and the market aggregate, and will not trigger credit concentration checks. It is the routing mechanism for all downstream risk calculations.
- **Risk types:** Cross-cutting (applies to all risk types by definition)
- **Criticality: 2.** If this element is wrong or missing, aggregated totals by risk type are produced but cannot be trusted — exposures are mis-routed into incorrect totals, making the credit aggregate, market aggregate, and liquidity aggregate simultaneously unreliable. The bank can still produce numbers; it cannot know whether those numbers are correct. This is a 2 rather than a 3 because the individual exposure amount is still valid; the failure is in classification and routing, not in the existence of the figure.
- **Driven by:** Principle 4 (¶42) — *"each system should make clear the specific approach used to aggregate exposures for any given risk measure, in order to allow the board and senior management to assess the results properly"*; Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*
- **Search terms:** risk type, risk category, risk class, risk taxonomy, product type, asset class, exposure type, risk flag, primary risk indicator
- **Data quality requirements:**
  - *validity* — Every exposure record must carry a risk type code from the approved controlled vocabulary; free-text or deprecated codes must not be present | count of exposure records with a risk type code not present in the current approved taxonomy | target: 0% invalid codes; taxonomy changes require formal change-control event before they appear in data
  - *completeness* — Every exposure record must carry a non-null risk type classification | count of exposure records with null risk type | target: 0% null
  - *consistency* — The risk type classification must be consistent with the instrument type; a plain vanilla loan must not be classified as market risk | count of instrument-type/risk-type combinations that violate defined compatibility rules | target: 0% invalid combinations; exceptions require documented override with approver

---

**CDE-05 — Business Line**

- **Definition:** The internal organisational dimension that assigns an exposure or position to a business segment — for example, retail banking, corporate banking, investment banking, treasury, or private wealth. The granularity and naming must be consistent across all systems that contribute to group-level risk aggregation.
- **Why critical:** BCBS 239 explicitly requires risk data to be available by business line as a mandatory aggregation dimension. Without a consistent business line attribute, the bank cannot slice its aggregate risk exposure by business segment, cannot identify concentrations within a line, and cannot respond to an ad hoc supervisory query asking for credit exposures within a specific business.
- **Risk types:** Credit, market, liquidity, cross-cutting
- **Criticality: 2.** The aggregate exposure figure is produced; without a valid business line attribute, it cannot be sliced by business segment, making business-line risk reports unreliable and concentration analysis by line impossible.
- **Driven by:** Principle 4 (¶41, heading) — data should be *"available by business line, legal entity, asset type, industry, region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures … as well as industry credit exposures … across all business lines and geographic areas"*
- **Search terms:** business line, business segment, division, desk, product line, segment code, profit centre, cost centre (where used as business line proxy), LOB (line of business)
- **Data quality requirements:**
  - *validity* — Business line codes must be drawn from the current approved segment hierarchy; retired or renamed segment codes must not appear on current-period records | count of exposure records carrying a business line code not in the current approved hierarchy | target: 0% invalid; hierarchy changes require advance notification to upstream systems
  - *completeness* — Every exposure record must carry a non-null business line code | count of exposure records with null business line, as percentage of records and notional value | target: 0% null
  - *consistency* — Business line assignment must be consistent across risk and finance systems for the same transaction; a loan booked by corporate banking in the GL must be assigned to corporate banking in the risk system | count of records where business line differs between risk system and GL for the same transaction identifier | target: 0% inconsistency; exceptions reported to data owner

---

**CDE-06 — Geography / Jurisdiction**

- **Definition:** The country or jurisdiction attribute that identifies where an exposure is located, booked, or where the counterparty is domiciled — depending on the risk type and the aggregation purpose. For credit risk this is typically the country of risk of the obligor; for market risk it may be the country of the exchange or clearing house; for liquidity risk it is the jurisdiction of the funding obligation.
- **Why critical:** Geography is an explicitly required aggregation dimension in Principle 4, and a named example in Principle 6's ad hoc query scenario. Country credit concentration is a directly named critical risk in ¶46. Without a consistent geography code, the bank cannot aggregate exposures by country, cannot identify geographic concentrations, and cannot respond to the specific supervisory example of country credit exposure aggregation.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 2.** The aggregate exposure figure is produced; without geography, it cannot be sliced by country or jurisdiction, making country concentration reports unreliable and cross-border regulatory reporting impossible.
- **Driven by:** Principle 4 (heading) — data should be available by *"region"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*; Principle 5 (¶46(c)) — *"market concentrations by sector and region data"* named as critical
- **Search terms:** country of risk, country code, jurisdiction, region, domicile, country of booking, geographic segment, ISO country code, country of counterparty, cross-border flag
- **Data quality requirements:**
  - *validity* — Geography codes must use the approved standard (ISO 3166-1 alpha-2 or the bank's approved mapping thereof); non-standard or deprecated codes must not appear | count of exposure records with geography codes not in the approved reference list | target: 0% invalid codes
  - *completeness* — Every exposure record must carry a non-null geography code appropriate to the risk type's definition of geography | count of null geography codes by risk type | target: 0% null
  - *accuracy* — The country of risk assigned to a counterparty must match the authoritative country of risk held in the counterparty master for the same counterparty identifier | count of records where geography code disagrees with the counterparty master for the same counterparty ID | target: 0% disagreement; all discrepancies investigated within one business day

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The economic sector or industry classification applied to the counterparty or the exposure — for example NACE, GICS, SIC, or the bank's internal sector taxonomy. This is applied primarily to credit exposures to identify sector concentrations, but also to trading and market risk positions where sector concentration is monitored.
- **Why critical:** Industry sector is an explicitly required aggregation dimension in the Principle 4 header, a named example in Principle 6's ad hoc query, and named in Principle 5 as a time-critical data element for trading exposures. It is also required by Principle 8 as a component of credit risk reporting. Without it, the bank cannot identify sector concentrations or produce the industry credit exposure slices demanded by ¶50.
- **Risk types:** Credit, market, concentration
- **Criticality: 2.** Exposure aggregates are produced; without industry sector, they cannot be sliced by sector, making sector concentration reports unreliable. This element also drives a mandatory reporting dimension (Principle 8, ¶57), placing it squarely in scope.
- **Driven by:** Principle 4 (heading) — data available by *"industry"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"* named as significant report components
- **Search terms:** industry code, sector code, NACE code, SIC code, GICS sector, industry classification, sector taxonomy, counterparty sector, borrower industry
- **Data quality requirements:**
  - *validity* — Industry codes must be drawn from the single approved classification standard; multiple competing taxonomies must be resolved to one canonical code per exposure at the point of aggregation | count of exposure records using deprecated or non-standard sector codes | target: 0% invalid; cross-taxonomy mapping rules maintained and version-controlled in the catalog
  - *completeness* — Every counterparty with credit exposure must carry an industry sector code; the bank should define and document acceptable null rates for counterparty types where classification is genuinely not applicable | count of credit exposure records with null sector code, by counterparty type | target: defined acceptable null rate per counterparty type, documented and approved; unclassified records above threshold escalated
  - *consistency* — The sector code on a credit exposure record must match the sector code held in the counterparty master for the same counterparty | count of records where exposure-level sector code differs from counterparty master sector code | target: 0% mismatch; resolution via counterparty master as the authoritative source

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The business date as of which an exposure or position is stated — the "snapshot date" or "reporting date" for the record. This is the temporal key that identifies which version of a position is the current one for a given aggregation run, distinguishes today's exposure from yesterday's, and anchors stress-scenario outputs to a specific point in time.
- **Why critical:** Every aggregate risk figure is stated as of a specific date. Without a correct position date, records from different time-points can be mixed in a single aggregate, producing a figure that is internally inconsistent. It is also required by ¶50's explicit formulation of ad hoc aggregation: *"as of a specified date"*. Timeliness monitoring (Principle 5) is also impossible without knowing the as-of date of each record.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3.** Without a valid position date on every record, the aggregate risk figure for a defined reporting date cannot be computed at all, because records from different business dates cannot be distinguished — the aggregate is either incoherent (mixing dates) or incomplete (records are excluded because they cannot be verified as belonging to the correct date).
- **Driven by:** Principle 5 (¶45) — *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis"* (implying the data is anchored to a known point in time); Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (¶53(a)) — reconciliation processes depend on comparing records at the same date
- **Search terms:** position date, as-of date, value date, report date, business date, trade date, snapshot date, effective date, reference date
- **Data quality requirements:**
  - *accuracy* — The position date on a risk record must match the business date for which the record was generated; dates must not be defaulted, forward-dated, or back-dated without an explicit override and documented reason | count of records where position date differs from the processing run date by more than the permitted settlement lag for that product type | target: 0% unexplained date mismatches
  - *timeliness* — Risk records for a given position date must be available by the time the risk report production run begins for that date | count of positions whose source-system position date is later than the target extraction time for the reporting run | target: 0% late records for standard runs; defined fast-close tolerance for stress/crisis runs (per Principle 5 requirements)
  - *validity* — Position dates must be valid business dates (not weekends or bank holidays in the relevant jurisdiction) unless the product type explicitly supports non-business-date settlement | count of records with a position date that is a non-business day without a valid product-type justification | target: 0% unjustified non-business-date records

---

**CDE-09 — Reconciliation Key (Transaction / GL Reference)**

- **Definition:** The identifier that links a risk data record to its corresponding entry in the general ledger or the authoritative system of record. This may be a transaction reference number, a deal ID, a loan account number, or an instrument ID — whichever identifier is used by both the risk data infrastructure and the finance/accounting infrastructure to refer to the same underlying transaction.
- **Why critical:** Principle 3 directly requires risk data to be reconciled with accounting data. This reconciliation is only mechanically possible if there is a key that links the risk record to the GL record for the same transaction. Without this key, reconciliation can only be performed at an aggregate level by comparing totals — a form of reconciliation that cannot identify which specific records are wrong. ¶36(c) makes this requirement explicit, and ¶53(a) requires defined processes to reconcile reports to risk data.
- **Risk types:** Cross-cutting (all risk types; the reconciliation obligation applies to the complete risk data set)
- **Criticality: 2.** Risk figures are produced; without a reconciliation key, the accuracy and integrity of those figures cannot be evidenced at a transaction level — the bank can show that aggregates approximately match but cannot demonstrate record-level correctness. This is the element whose absence makes Principle 3 compliance unverifiable. It is a 2 rather than a 3 because the aggregate figure can be produced; what fails is the control that validates it.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** transaction ID, deal ID, loan reference, GL reference, account number, instrument ID, trade reference, booking reference, source transaction key, primary key
- **Data quality requirements:**
  - *completeness* — Every risk record that corresponds to a balance-sheet item must carry a non-null reconciliation key that links it to the GL or system of record | count of risk records for on-balance-sheet positions with null or blank reconciliation key | target: 0% null; off-balance-sheet items require documented reason for absence of GL reference
  - *uniqueness* — A reconciliation key must uniquely identify a single transaction; duplicate keys on different risk records for the same period indicate a double-count | count of reconciliation keys that appear more than once on risk records for the same position date, where the instrument type does not permit multiple risk records per GL entry | target: 0% confirmed duplicates; all flagged cases investigated before report sign-off
  - *consistency* — The gross exposure amount on the risk record must reconcile to the balance or notional on the corresponding GL or system-of-record entry within defined tolerance | sum of absolute differences between risk-system amounts and GL amounts, matched by reconciliation key, as a percentage of total portfolio value | target: < materiality threshold (defined jointly by risk and finance); zero unexplained items above individual materiality threshold

---

**CDE-10 — Source System / Provenance Flag**

- **Definition:** The attribute that identifies which source system generated the risk record, and whether the record was produced through an automated pipeline or via a manual process (including end-user computing tools such as spreadsheets or desktop databases). This is not merely an audit trail field — it is a risk data quality control attribute with direct implications for the reliability of the record it accompanies.
- **Why critical:** Principle 3 requires documentation of all risk data aggregation processes, explicit identification of manual workarounds, and assessment of their materiality. Principle 3 also requires a single authoritative source per risk type (¶36(d)). Without a provenance flag, the bank cannot identify which records are manual-process-generated (and therefore subject to higher error risk), cannot measure its dependence on EUC tools, cannot prioritise automation investments, and cannot demonstrate to supervisors that it has control over its data lineage. ¶39 names this documentation obligation directly.
- **Risk types:** Cross-cutting (governance and data quality control across all risk types)
- **Criticality: 2.** Risk figures are produced; without source system and provenance information, the bank cannot stratify its data quality monitoring by source, cannot identify which portion of an aggregate derives from manual processes, and cannot demonstrate the control environment required by ¶36(b) and ¶39. The aggregate exists; its reliability cannot be assessed by source.
- **Driven by:** Principle 3 (¶36(d)) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (¶39) — *"banks to document and explain all of their risk data aggregation processes whether automated or manual … a description of their criticality to the accuracy of risk data aggregation"*; Principle 1 (¶29(a)) — independent validation must *"encompass all components of the bank's risk data aggregation and reporting processes"*
- **Search terms:** source system, system of origin, data source ID, feed name, manual entry flag, EUC flag, end-user computing indicator, pipeline ID, upstream system, data lineage tag, manual override flag
- **Data quality requirements:**
  - *completeness* — Every risk record must carry a non-null source system identifier and a manual/automated indicator | count of risk records with null source system code or null manual/automated flag | target: 0% null
  - *validity* — Source system codes must correspond to registered, currently active systems in the data catalog's system inventory; unregistered source codes indicate an unknown data feed | count of risk records carrying a source system code with no matching registration in the catalog | target: 0% unregistered sources; any new source system must be registered and validated before its records are included in risk aggregation
  - *accuracy* — The proportion of exposure records (by count and by notional value) that derive from manual or EUC processes must be measured and monitored against defined thresholds; increases above threshold are a data quality escalation event | percentage of total exposure notional value and record count where provenance flag = manual or EUC, measured per risk type and per reporting cycle | target: thresholds defined by risk management and approved by senior management; breach triggers documented escalation per ¶40

---

**CDE-11 — Collateral / Credit Risk Mitigation Reference**

- **Definition:** The identifier and amount of eligible collateral or credit risk mitigation (CRM) applied to a credit exposure, sufficient to link the exposure record to the collateral record in the collateral management system. Includes the collateral agreement reference (e.g. ISDA CSA, security interest, guarantee) and the current collateral value assigned.
- **Why critical:** Net credit exposure — the figure after netting and collateral — is a standard output of credit risk aggregation and appears in virtually all credit risk reports. If collateral is not linked to exposures via a stable identifier, net exposure cannot be computed correctly. The regulation requires aggregation of all material risk, and for secured exposures the uncollateralised portion is the material risk figure. This element also matters for liquidity risk (collateral encumbrance, available liquidity buffer) per ¶46(d).
- **Risk types:** Credit, counterparty, liquidity
- **Criticality: 2.** Gross exposure figures are produced correctly without this element; it is net exposure (post-collateral) that becomes unreliable. A supervisor reviewing net credit exposure totals would correctly identify the absence of CRM linkage as a completeness failure, but the underlying gross aggregate is not invalidated.
- **Driven by:** Principle 4 (¶41) — *"all material risk exposures, including those that are off-balance sheet"* (collateral arrangements are frequently off-balance-sheet); Principle 5 (¶46(d)) — *"Liquidity risk indicators such as cash flows/settlements and funding"* (collateral encumbrance affects available liquidity)
- **Search terms:** collateral ID, CRM reference, collateral agreement ID, CSA reference, netting set ID, collateral value, eligible collateral, collateral haircut, guarantee reference, security interest ID, encumbrance flag
- **Data quality requirements:**
  - *completeness* — Every secured credit exposure must carry a reference to the applicable collateral agreement; unsecured exposures must be explicitly flagged as uncollateralised rather than left blank | count of credit exposure records where collateral flag is null (neither collateralised nor explicitly uncollateralised) | target: 0% ambiguous; all exposures explicitly attributed
  - *accuracy* — The collateral value assigned to an exposure must reflect the current market value of the collateral after approved haircuts, as of the same position date as the exposure | count of exposure-collateral pairs where the collateral valuation date differs from the exposure position date by more than the approved tolerance | target: defined per collateral type (daily for liquid securities; defined lag for illiquid collateral)
  - *consistency* — The collateral value recorded on the risk record must agree with the value held in the authoritative collateral management system for the same agreement reference | count of exposure records where the risk-system collateral value disagrees with the collateral management system by more than a defined tolerance | target: 0% unexplained differences above tolerance

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Risk-to-Finance Reconciliation**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-09 (Reconciliation Key), CDE-02 (Legal Entity Identifier), CDE-08 (Position / As-Of Date)
- **What this requires:** The total risk exposure aggregated across the risk data infrastructure must reconcile to the corresponding balances in the general ledger, at the level of legal entity and position date. This reconciliation cannot be performed by monitoring any single element — it requires CDE-03 (the amount being compared), CDE-09 (the key that links risk and GL records), CDE-02 (the dimension of consolidation), and CDE-08 (the date the comparison is made as of). A bank that monitors each of these individually but never performs the cross-system reconciliation cannot demonstrate accuracy under Principle 3, because ¶36(c) requires reconciliation as an end-to-end control, not as a property of individual fields.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*
- *consistency* — The aggregate risk exposure by legal entity and position date must equal the corresponding balance in the GL within defined tolerance, with all differences identified, attributed to one of a defined set of permitted reconciling items, and cleared within defined deadlines | total unexplained variance between risk aggregates and GL balances by legal entity and position date, expressed as an amount and as a percentage of total exposure; count of reconciling items outstanding beyond their permitted age | target: zero unexplained items above individual materiality threshold; all reconciling items cleared or escalated within one business day of report production

---

**XDQ-02 — Counterparty Resolution Across Systems (Single Counterparty View)**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-04 (Risk Type Classification), CDE-05 (Business Line), CDE-06 (Geography / Jurisdiction), CDE-07 (Industry / Sector Classification)
- **What this requires:** The same real-world counterparty must be represented by the same counterparty identifier in every source system — trading systems, loan origination, derivatives platforms, collateral systems, and the credit limit system. Where different systems use different local identifiers, a cross-reference mapping must exist and be maintained. This is not a property of any single record; it is a property of the relationship between records across systems. A bank that monitors completeness of CDE-01 in each system individually without validating cross-system resolution will count the same counterparty multiple times when aggregating total group exposure — the exact failure Principle 2 and Principle 4 are designed to prevent. The slicing dimensions (CDE-04 through CDE-07) compound the failure: if the counterparty cannot be resolved, none of the dimension-based aggregation (by sector, by geography, by business line) across that counterparty's full exposure profile is reliable.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41) — all material exposures must be captured across the banking group; Principle 5 (¶46(a)(b)) — large-corporate and counterparty credit risk aggregation named as critical and time-sensitive
- *consistency* — Every counterparty that appears in more than one source system must have a cross-reference mapping to the single authoritative counterparty identifier in the counterparty master; unmapped local identifiers represent potential double-counts or omissions in group aggregation | count of active local counterparty identifiers in each source system with no mapping to an authoritative master record; count of counterparty identifiers that map to more than one master record | target: 0% unmapped identifiers; 0% one-to-many mappings; all new counterparties mapped within one business day of onboarding
- *completeness* — The total group exposure to any single counterparty, computed by joining all source systems on the authoritative counterparty identifier, must be verifiably complete — that is, the set of systems contributing to the join must be the full set of systems in which that counterparty has an active position | count of counterparties where at least one source system with a known active position did not contribute a record to the last group exposure aggregation run | target: 0% missing source systems; confirmed completeness documented in the aggregation run log

---

## 4. Out of Scope

The following principles — or specific obligations within them — address outcomes that no data element register, data quality monitoring programme, or metadata catalog can deliver, regardless of how completely those tools are implemented.

---

**Principles 8–11: Report content, clarity, frequency, and distribution**

These four principles are fundamentally concerned with what risk reports contain, how they are structured, how often they are produced, and who receives them.

**Principle 8 (Comprehensiveness, ¶57–60)** requires that risk reports cover all significant risk areas, include forward-looking forecasts and stress test results, and address inter- and intra-risk concentrations. The obligation to actually include this content — and to determine whether the depth and scope is appropriate for the bank's complexity — is a reporting design and governance decision that cannot be discharged by cataloguing data elements. *However*, Principle 8 also names industry sector (¶57) as a required report dimension, which directly drives CDE-07 above. The CDE captures the data element; the reporting obligation — that the element appears in a comprehensive report covering all significant risk areas, with appropriate forward-looking analysis — is a separate requirement that the catalog cannot satisfy. Both are true simultaneously.

**Principle 9 (Clarity and usefulness, ¶61–69)** requires that reports communicate clearly, balance quantitative data with qualitative interpretation, and be tailored to the needs of different recipients including the board, senior management, and risk committees. It also requires banks to periodically confirm with recipients that reporting is relevant and appropriate (¶69). These are report design, editorial judgment, and board engagement obligations. A data catalog can ensure the underlying data is well-defined (¶67: *"A bank should develop an inventory and classification of risk data items"* — this is the closest Principle 9 comes to a catalog-addressable requirement, and it is addressed by the CDE register itself), but it cannot ensure that a report is clear, well-balanced, or that recipients confirm it meets their needs.

**Principle 10 (Frequency, ¶70–71)** requires the board and senior management to set report frequency, to test the bank's ability to produce accurate reports within established timeframes, and to increase frequency during stress. These are operational and governance commitments — they require production infrastructure, escalation procedures, and board-level decisions about reporting cadence. Timeliness of underlying data (CDE-08) is a necessary but not sufficient condition; the actual frequency at which reports are produced and distributed is outside the scope of the catalog.

**Principle 11 (Distribution, ¶72–74)** requires that procedures exist for rapid collection and dissemination of reports to appropriate recipients, balanced against confidentiality requirements. This is a report distribution and access control obligation, addressed by report delivery infrastructure and information security governance — not by data element management or quality monitoring.

---

**Principle 1 (Governance, ¶27–31) — Board and senior management obligations**

Principle 1 requires the board to review and approve the risk data aggregation framework, to understand the limitations that prevent full aggregation, and to be aware of ongoing compliance. These are governance and accountability obligations that belong to the bank's three-lines-of-defence framework, validation programme, and board reporting cycle. A data catalog supports these obligations by making limitations visible (incomplete lineage, unresolved counterparty mappings, high manual processing rates) but cannot itself constitute the oversight framework, approve the policies, or ensure that the board is asking the right questions. ¶30's requirement that senior management identify data critical to aggregation is partially addressed by the CDE register; the strategic IT planning and resource allocation it requires are not.

---

**Principle 3 (Accuracy, ¶38) — Professional judgment in manual processes**

¶38 acknowledges that *"where professional judgements are required, human intervention may be appropriate"* and requires an appropriate balance between automated and manual systems. The judgment itself — whether a manual override is appropriate, and what value to assign — cannot be governed by a data element or monitored by a DQ rule. What the catalog *can* do is flag the record as manual-process-generated (CDE-10) and measure the proportion of the portfolio subject to manual judgment, supporting the oversight obligation without substituting for it.

---

**Principle 6 (Adaptability, ¶48–51) — Flexible aggregation infrastructure**

Principle 6 requires that the bank's data aggregation capabilities are flexible enough to respond to ad hoc requests, emerging risks, and scenario analyses in near real time. This is an infrastructure and architecture capability requirement — the ability to slice data along new dimensions not previously requested, to run new scenarios, and to incorporate changing business structures. The catalog supports adaptability by ensuring that data is well-described, lineage is known, and dimensions are consistently coded, but it cannot itself be the flexible aggregation infrastructure. The distinction is important: a bank cannot claim Principle 6 compliance by maintaining a good data catalog if its aggregation systems require months of IT work to produce a new slice.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | 2 (¶33), 5 (¶46b) | Uniqueness, Completeness, Consistency |
| CDE-02 | Legal Entity Identifier (Booking Entity) | 3 | 2 (¶33), 4 (¶41) | Validity, Completeness, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3 (¶36a, ¶36c), 7 (¶53a), 5 (¶46a) | Accuracy, Completeness, Timeliness |
| CDE-04 | Risk Type Classification | 2 | 4 (¶42), 8 (¶57) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | 2 | 4 (heading), 6 (¶50) | Validity, Completeness, Consistency |
| CDE-06 | Geography / Jurisdiction | 2 | 4 (heading), 6 (¶50), 5 (¶46c) | Validity, Completeness, Accuracy |
| CDE-07 | Industry / Sector Classification | 2 | 4 (heading), 6 (¶50), 8 (¶57) | Validity, Completeness, Consistency |
| CDE-08 | Position / As-Of Date | 3 | 5 (¶45), 6 (¶50), 7 (¶53a) | Accuracy, Timeliness, Validity |
| CDE-09 | Reconciliation Key (Transaction / GL Reference) | 2 | 3 (¶36c), 7 (¶53a) | Completeness, Uniqueness, Consistency |
| CDE-10 | Source System / Provenance Flag | 2 | 3 (¶36d, ¶39), 1 (¶29a) | Completeness, Validity, Accuracy |
| CDE-11 | Collateral / Credit Risk Mitigation Reference | 2 | 4 (¶41), 5 (¶46d) | Completeness, Accuracy, Consistency |

**Criticality 3 elements: CDE-01, CDE-02, CDE-03, CDE-08 (four elements).** Each satisfies the step-2 test: the aggregate figure cannot be computed at all without them, not merely less accurately. All remaining elements are Criticality 2: the aggregate is produced but cannot be sliced, reconciled, or its reliability demonstrated without them. No element has been rated Criticality 1, because no element in this register fails to affect at least one aggregate risk figure; if any purely descriptive element had been included, it would receive a 1. The register has been kept to 11 elements rather than extended to a thinner 15 to preserve the depth of justification.