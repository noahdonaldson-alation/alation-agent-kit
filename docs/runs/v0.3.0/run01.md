# BCBS 239 — Data Catalog Governance Interpretation

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Board-level accountability for data quality as a risk management matter.** The framework must be approved and resourced by the board and senior management, who must understand coverage limitations and IT shortcomings. (¶27–28: *"A bank's board and senior management should promote the identification, assessment and management of data quality risks as part of its overall risk management framework."*)

- **Integrated data architecture with single identifiers and governed metadata.** Banks must establish *"integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts."* (¶33)

- **Accurate, reconciled, and predominantly automated risk data aggregation.** Risk data must be reconciled to accounting sources, sourced from a single authoritative system per risk type, and its aggregation processes fully documented including manual workarounds. (¶36(c), ¶36(d), ¶39)

- **Complete coverage across all material exposures and aggregation dimensions.** Risk data must be available by business line, legal entity, asset type, industry, and region so that concentrations and emerging risks can be identified. Off-balance-sheet exposures are explicitly in scope. (¶41: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*)

- **Timely production under both normal and stress conditions.** Systems must produce aggregated risk data rapidly in a crisis, particularly for credit, counterparty, trading, and liquidity risk. (¶45–46)

- **Accurate, comprehensive, and clear risk reports validated against underlying data.** Reports must be reconciled to source data, include all material risk areas with quantitative and qualitative balance, and be tailored to recipients including the board. (¶52–53, ¶57–58)

**Who it applies to**

Globally Systemically Important Banks (G-SIBs) were the primary addressees at issuance (January 2013), with national supervisors expected to extend application to Domestic Systemically Important Banks (D-SIBs). The principles apply at the **banking group** level, encompassing subsidiaries, legal entities, and off-balance-sheet structures. Outsourced processes are explicitly in scope (¶27).

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** The unique, enterprise-wide code that identifies a single legal counterparty (borrower, issuer, derivative counterparty, deposit taker) consistently across all booking systems, risk engines, and reporting platforms. This is the primary joining key from exposure to obligor.
- **Why critical:** Without a resolved, consistent counterparty identifier, exposures held in different systems cannot be summed to produce a single-name or group concentration figure. The regulation's requirement to produce aggregated credit exposure to a large corporate borrower (¶46(a)) and counterparty credit risk exposures including derivatives (¶46(b)) is structurally impossible without this key.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3** — *Without this element, the aggregate single-name credit exposure figure cannot be computed at all, because exposures in different systems refer to different entity representations and cannot be reliably summed or de-duplicated.* The regulation requires a single authoritative identifier for counterparties (¶33) precisely because aggregation fails without it.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 5 (¶46(a)) — *"The aggregated credit exposure to a large corporate borrower"*
- **Search terms:** counterparty ID, obligor ID, client ID, party identifier, legal entity identifier, LEI, GFCID, global counterparty code, customer master ID, BIC, entity reference
- **Data quality requirements:**
  - *Uniqueness* — Each real-world counterparty maps to exactly one enterprise identifier; no two identifiers refer to the same legal entity | Count of counterparty identifiers that resolve to duplicate legal entities via LEI or name-matching | Target: 0 confirmed duplicates in the counterparty master
  - *Completeness* — Every exposure record carries a non-null, populated counterparty identifier | Count (and percentage) of exposure records with null or unresolvable counterparty identifier | Target: <0.1% missing, zero tolerance for any record exceeding internal materiality threshold
  - *Validity* — Counterparty identifier resolves to an active record in the counterparty master at the time the exposure is booked | Count of exposure records whose counterparty identifier does not exist in the master reference table | Target: 0 unmatched identifiers in any overnight batch

---

**CDE-02 — Legal Entity / Booking Entity Identifier**

- **Definition:** The code that identifies the specific regulated legal entity within the banking group in which a position or exposure is booked. Used for subsidiary-level reporting, group consolidation, and jurisdictional regulatory submissions.
- **Why critical:** Group-level aggregation and subsidiary-level disaggregation both depend on this element. Without it, the bank cannot split or roll up exposures by legal entity, cannot produce subsidiary risk reports, and cannot demonstrate that off-balance-sheet entities are captured. (¶41: all material risk exposures including off-balance sheet.)
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 3** — *Without this element, the group-consolidated risk exposure figure cannot be computed at all, because there is no reliable basis on which to include or exclude individual legal entities from the consolidation perimeter.* The regulation requires unified naming conventions specifically for legal entities (¶33).
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*
- **Search terms:** legal entity ID, booking entity, entity code, subsidiary code, LEI (legal entity), consolidation entity, reporting unit, branch code, MFI code, ownership hierarchy ID
- **Data quality requirements:**
  - *Completeness* — Every exposure and position record is tagged with a non-null legal entity identifier | Count of records with null or blank legal entity code | Target: 0 missing
  - *Validity* — Legal entity identifier exists in the group entity hierarchy and is within the current consolidation perimeter | Count of records referencing decommissioned, merged, or unknown entity codes | Target: 0 invalid references
  - *Consistency* — The same booking entity is identified by the same code across all source systems feeding the risk aggregation layer | Count of entity code mismatches detected during cross-system reconciliation | Target: 0 discrepancies for material entities

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary value of an exposure before any credit risk mitigants (collateral, netting, guarantees) are applied. Expressed in the transaction currency, with a corresponding base-currency equivalent. Covers loans, bonds, derivatives (replacement cost or notional as applicable), and off-balance-sheet commitments.
- **Why critical:** This is the quantity being aggregated. Every risk figure — single-name concentration, sector total, group-level credit exposure — is ultimately a sum or transformation of individual exposure amounts. If the amount is wrong, every aggregate built from it is wrong.
- **Risk types:** Credit, counterparty, concentration
- **Criticality: 3** — *Without this element, the aggregate credit exposure figure cannot be computed at all, because there is no monetary quantity to sum across counterparties, lines of business, or geographies.* (¶46(a) explicitly names *"the aggregated credit exposure"* as the canonical use case for rapid stress reporting.)
- **Driven by:** Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 5 (¶46(a)) — *"The aggregated credit exposure to a large corporate borrower"*
- **Search terms:** gross exposure, EAD (exposure at default), notional amount, drawn amount, outstanding balance, current exposure, replacement cost, committed amount, facility utilisation, pre-mitigant exposure
- **Data quality requirements:**
  - *Accuracy* — Exposure amounts agree to the system of record (loan system, trading system, general ledger) within defined tolerance | Sum of absolute variance between risk system exposure amounts and GL/source system balances, by asset class | Target: aggregate variance ≤ materiality threshold set by Finance; zero unexplained differences above threshold
  - *Completeness* — No material exposure class is absent from the aggregated total; off-balance-sheet commitments are included | Comparison of exposure count and balance against product-type inventory; flag any product type with zero coverage | Target: all active product types represented; off-balance-sheet line items present
  - *Timeliness* — Exposure amounts reflect positions as of the stated as-of date, loaded within the production window | Age of most recent record per source system compared to the declared as-of date | Target: all source feeds loaded within agreed SLA (e.g., T+0 for trading, T+1 for banking book)

---

**CDE-04 — Position / As-Of Date**

- **Definition:** The business date as of which a risk position or exposure is stated. Every aggregate risk figure is implicitly or explicitly stated as of this date; it is the temporal key that makes point-in-time snapshots comparable and reconcilable.
- **Why critical:** Aggregation across systems is only valid when all records are stated as of the same date. Mixed dates produce figures that cannot be meaningfully summed, reconciled to the general ledger, or presented in a risk report. The requirement to produce aggregated data *"on a timely basis"* and *"rapidly during times of stress/crisis"* (¶44–45) implies that the as-of date is a controlled, verifiable attribute.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3** — *Without this element, the point-in-time aggregate risk figure cannot be computed at all, because records from different dates cannot be validly summed — the result would not correspond to any real state of the bank's exposure.* This is the minimal temporal anchor for every aggregate.
- **Driven by:** Principle 5 (¶44) — *"A bank's risk data aggregation capabilities should ensure that it is able to produce aggregate risk information on a timely basis"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*
- **Search terms:** as-of date, position date, valuation date, reference date, report date, snap date, cut-off date, business date, effective date, data as of
- **Data quality requirements:**
  - *Validity* — As-of date is a valid business calendar date; not null, not a future date, not a weekend or holiday where intraday snapshots are not expected | Count of records with null, future, or non-business-day as-of dates | Target: 0 invalid dates
  - *Consistency* — All records within a single aggregation run carry the same declared as-of date; cross-system feeds are aligned to the same business date | Count of distinct as-of dates found within a single aggregation batch across all source systems | Target: 1 distinct date per batch run (or documented exception for systems with known lag)
  - *Timeliness* — The as-of date is not stale relative to the production schedule; records load within the SLA window after close of business | Time elapsed between declared as-of date and availability of complete aggregated dataset | Target: within agreed SLA defined per risk type (e.g., T+0 intraday for market risk, T+1 for credit risk)

---

**CDE-05 — Risk Type Classification**

- **Definition:** The classification code that assigns an exposure or position to a primary risk type (credit risk, market risk, liquidity risk, operational risk, counterparty credit risk). This is the taxonomy element that partitions the risk universe for aggregation, capital calculation, and reporting.
- **Why critical:** Principle 8 (¶57) requires reports to cover all significant risk areas. Without a consistent risk type classification, the bank cannot partition its exposures to produce capital adequacy figures, regulatory returns by risk type, or concentration reports within a risk class. A misclassified exposure feeds the wrong aggregate and creates a false sense of completeness in the correct one.
- **Risk types:** Cross-cutting
- **Criticality: 2** — Aggregation by risk type is possible if the classification is missing for some records (they can be flagged as unclassified), but the slice by risk class is incomplete and cannot be trusted. The board cannot assess whether all material risk areas are covered (¶57) when classification is inconsistent. A wrong or missing risk type distorts the sub-total for that class but does not make the overall gross exposure sum invalid.
- **Driven by:** Principle 4 (header and ¶41) — *"capture and aggregate all material risk data across the banking group"*; Principle 8 (¶57) — *"exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*
- **Search terms:** risk type, risk class, risk category, Basel risk category, asset class, risk classification code, risk taxonomy code, exposure type
- **Data quality requirements:**
  - *Validity* — Risk type code belongs to the approved enterprise risk taxonomy; no free-text or local codes used | Count of records carrying risk type values not present in the authorised taxonomy reference table | Target: 0 unrecognised codes
  - *Completeness* — Every exposure and position record carries a non-null risk type classification | Count (and percentage) of records with null risk type | Target: 0 null classifications for any record above internal materiality threshold
  - *Consistency* — The same instrument or exposure is classified to the same risk type across all source systems contributing to the aggregated dataset | Count of instrument-level risk type mismatches detected between source systems feeding the risk layer | Target: 0 conflicts for any material instrument

---

**CDE-06 — Business Line**

- **Definition:** The organisational dimension code that assigns an exposure, position, or transaction to a business line (e.g., retail banking, wholesale/corporate banking, investment banking, private banking, treasury). Defined and maintained at group level, not by individual business units.
- **Why critical:** Principle 4 explicitly names business line as a required dimension for risk data availability. Without it, the bank cannot produce business-line-level risk reports, cannot identify concentrations within a line, and cannot support P&L and risk attribution to organisational units.
- **Risk types:** Credit, market, liquidity, operational, cross-cutting
- **Criticality: 2** — The overall gross exposure aggregate is not invalid, but the business-line sub-total cannot be produced or relied upon. The regulator explicitly requires data *"available by business line"* (Principle 4 header); a missing business line code degrades this required slice. ¶50 also names business lines as an axis for ad hoc stress queries.
- **Driven by:** Principle 4 (header) — *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date … across all business lines and geographic areas"*
- **Search terms:** business line, business unit, segment, division, line of business, LOB code, product line, client segment, organisational unit
- **Data quality requirements:**
  - *Completeness* — Every exposure and position record carries a non-null business line code | Count (and percentage) of records missing a business line classification | Target: <0.5% missing; 0 for records above materiality threshold
  - *Validity* — Business line code maps to the current enterprise business line taxonomy; no retired or locally-invented codes | Count of records with business line codes not in the approved reference table | Target: 0 unrecognised codes
  - *Consistency* — Business line assignment for the same booking entity is identical across risk system and management reporting system | Count of records where business line differs between the risk data layer and the management reporting layer for the same instrument | Target: 0 conflicts for material portfolios

---

**CDE-07 — Geography / Country of Risk**

- **Definition:** The country or geographic region to which an exposure is assigned for risk concentration and reporting purposes. This may be country of incorporation of the counterparty, country of collateral, or country of risk as defined by the bank's transfer risk methodology — whichever is the governing definition for the risk in question.
- **Why critical:** Principle 4 names region as a required aggregation dimension. Principle 6 (¶50) specifically illustrates the requirement with country credit exposure: *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."* Without a consistent country-of-risk assignment, geographic concentration reports are incomplete or misleading.
- **Risk types:** Credit, market, concentration
- **Criticality: 2** — The total exposure figure is not invalid, but the geographic sub-total cannot be sliced and the country concentration report required by ¶50 cannot be produced. Cross-border and transfer risk monitoring, which is a supervisory expectation, breaks down entirely.
- **Driven by:** Principle 4 (header) — *"Data should be available by … region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*
- **Search terms:** country of risk, country code, geography, region, jurisdiction, counterparty country, collateral country, ISO country code, transfer risk country, booking country
- **Data quality requirements:**
  - *Completeness* — Every exposure record carries a non-null country-of-risk code | Count (and percentage) of exposure records with null or blank country code | Target: 0 null for cross-border and wholesale exposures; <0.1% overall
  - *Validity* — Country code is a valid ISO 3166-1 alpha-2 or alpha-3 code, or maps to an approved internal geographic hierarchy | Count of records with country codes not present in the approved geographic reference table | Target: 0 invalid codes
  - *Consistency* — The same counterparty is assigned the same country of risk across all source systems | Count of counterparty-level country-of-risk mismatches across source systems for the same counterparty identifier | Target: 0 conflicts for material counterparties

---

**CDE-08 — Industry / Sector Classification**

- **Definition:** The economic sector or industry code assigned to a counterparty or exposure (e.g., NACE, GICS, SIC, or an internal taxonomy). Captures the type of economic activity the counterparty conducts, used for sector concentration analysis and stress testing.
- **Why critical:** Principle 4 explicitly names industry as a required aggregation dimension. Principle 8 (¶57) requires reports to cover *"single name, country and industry sector for credit risk."* Principle 6 (¶50) illustrates ad hoc aggregation by industry type. Without sector classification, concentration in any single industry — a key early-warning indicator — cannot be computed.
- **Risk types:** Credit, concentration
- **Criticality: 2** — Total exposure is unaffected, but the industry concentration sub-total is unavailable or unreliable. The regulator names industry sector explicitly three times across Principles 4, 6 and 8; failure here is a directly evidenced gap, not an inference.
- **Driven by:** Principle 4 (header) — *"Data should be available by … industry"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types"*
- **Search terms:** industry code, sector code, NACE code, GICS, SIC, industry classification, economic sector, sector taxonomy, counterparty sector
- **Data quality requirements:**
  - *Completeness* — Every wholesale/corporate counterparty record carries a non-null industry classification | Count (and percentage) of counterparty master records with null or placeholder sector code for non-retail counterparties | Target: <1% missing; 0 for material counterparties above defined credit exposure threshold
  - *Validity* — Industry code belongs to the adopted classification standard (NACE, GICS, or internal equivalent) and is not an obsolete version | Count of records referencing deprecated or unrecognised sector codes | Target: 0 invalid codes
  - *Consistency* — Sector assignment for the same counterparty is identical across counterparty master, credit risk system, and risk reporting layer | Count of counterparty-level sector code discrepancies across systems | Target: 0 conflicts for any counterparty with aggregate exposure above materiality threshold

---

**CDE-09 — General Ledger / Source System Reconciliation Key**

- **Definition:** The identifier — typically a trade ID, loan account number, or GL account code — that links a risk record to its corresponding entry in the general ledger or the system of record (loan origination system, trading system). This is the key that makes reconciliation between risk data and accounting data possible.
- **Why critical:** ¶36(c) states directly that *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."* Without a resolvable reconciliation key, this requirement cannot be met operationally: there is no basis on which to compare risk figures to the GL or identify discrepancies. Principle 7 (¶53(a)) requires *"defined requirements and processes to reconcile reports to risk data"* — reconciliation processes require this key to function.
- **Risk types:** Cross-cutting (accuracy and integrity for all risk types)
- **Criticality: 2** — The risk aggregate is still produced, but its accuracy cannot be evidenced or demonstrated to a supervisor. Without the reconciliation key, it is impossible to identify whether risk data has drifted from accounting data — the aggregate may be wrong and the bank has no mechanism to detect it. The figure is produced but cannot be trusted.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** trade ID, loan account number, GL account code, source system reference, deal reference, booking reference, contract ID, position ID, reconciliation key, primary key from source
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null reference to its originating transaction in the source system or GL | Count (and percentage) of risk records with null or blank reconciliation key | Target: 0 missing for any record above materiality threshold
  - *Uniqueness* — Each reconciliation key maps to exactly one risk record in the risk data layer per as-of date; no duplicated booking references | Count of duplicate reconciliation key instances within a single as-of date snapshot | Target: 0 duplicates
  - *Accuracy* — Reconciliation key resolves to an active, matched record in the source system; the associated exposure amount agrees to the source system amount within tolerance | Count of unmatched reconciliation keys; sum of unexplained variance between risk layer amounts and source system amounts | Target: 0 unmatched keys; aggregate variance ≤ materiality threshold

---

**CDE-10 — Source System Identifier / Data Provenance Flag**

- **Definition:** The attribute that identifies which source system supplied each risk record, and — separately — whether the record was produced by an automated process or by manual intervention (including end-user computing tools such as spreadsheets or local databases). Two related sub-elements: (a) source system code, and (b) manual/EUC flag.
- **Why critical:** ¶36(d) requires a single authoritative source per risk type, and ¶39 requires documentation of all processes *"whether automated or manual."* ¶36(b) requires *"effective mitigants in place (eg end-user computing policies)"* for manual processes. Without a provenance attribute, the bank cannot identify which records came from controlled automated systems and which came from spreadsheets, cannot apply differentiated controls, and cannot produce the documentation required by ¶39. Any aggregate that silently mixes authoritative and EUC-sourced data cannot be validated.
- **Risk types:** Cross-cutting (governance and accuracy for all risk types)
- **Criticality: 2** — The aggregate is produced, but the bank cannot demonstrate to a supervisor that it is sourced from authoritative systems or that manual inputs are controlled. The ability to segment by source is required for the differentiated EUC controls in ¶36(b) and the documentation of manual workarounds in ¶39. Without this attribute, the governance and audit trail that underpin accuracy claims are absent.
- **Driven by:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications … it should have effective mitigants in place"*; Principle 3 (¶36(d)) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (¶39) — *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*
- **Search terms:** source system, source system code, data source, system of origin, feed name, data provider, manual override flag, EUC flag, end-user computing indicator, manual input flag, spreadsheet flag, automated vs manual, data lineage source
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null source system identifier | Count (and percentage) of risk records with null or blank source system code | Target: 0 missing
  - *Validity* — Source system code belongs to the approved inventory of authorised data sources registered in the data architecture | Count of records referencing source system codes not present in the authorised source system registry | Target: 0 unregistered source systems
  - *Accuracy* — Manual/EUC flag correctly identifies records that originated outside automated production systems; EUC-sourced records are consistently flagged | Proportion of records carrying an EUC flag compared to the expected volume based on known EUC feeds; spot-check comparison of flagged records against the EUC register | Target: 0 unflagged records from known EUC sources

---

**CDE-11 — Net / Collateralised Exposure Amount (Post-Mitigant)**

- **Definition:** The residual exposure after the application of eligible credit risk mitigants — netting agreements, financial collateral, guarantees, and credit derivatives. The delta between gross exposure (CDE-03) and this figure represents the credit risk transfer. Used in regulatory capital calculations and net concentration analysis.
- **Why critical:** ¶41 explicitly scopes risk data aggregation to *"all material risk exposures, including those that are off-balance sheet."* Limits monitoring (¶58) and risk appetite reporting require the *net* figure against which limits are set. For counterparty credit risk with netting agreements (¶46(b)), the gross figure overstates actual exposure; the net figure is what regulatory capital and internal limits reference. If collateral or netting data is absent, net exposure cannot be computed and capital figures are distorted.
- **Risk types:** Credit, counterparty
- **Criticality: 2** — The gross exposure aggregate (CDE-03) remains valid, but net exposure — the basis for regulatory capital and limits — cannot be computed or reconciled. Concentration figures based on gross amounts will overstate risk; those based on incorrectly applied mitigants will understate it. The figure is produced but cannot be trusted for capital or limits purposes.
- **Driven by:** Principle 4 (¶41) — *"all material risk exposures, including those that are off-balance sheet"*; Principle 8 (¶58) — *"provide information in the context of limits and risk appetite/tolerance"*; Principle 5 (¶46(b)) — *"Counterparty credit risk exposures, including, for example, derivatives"*
- **Search terms:** net exposure, post-CRM exposure, collateral value, eligible collateral, netting set, net replacement cost, LGD input, RWA driver, credit risk mitigation, haircut, collateral haircut, net credit exposure, stress-tested collateral value
- **Data quality requirements:**
  - *Accuracy* — Collateral valuations used in net exposure calculation are current and sourced from the approved valuation system; netting agreements are reflected correctly | Variance between collateral values in the risk system and the collateral management system; count of counterparties where netting is applied in one system but not the other | Target: zero unexplained collateral valuation differences above materiality; 0 netting inconsistencies for ISDA-governed counterparties
  - *Completeness* — All recognised netting sets and collateral agreements are captured; no eligible mitigant is omitted from the calculation | Proportion of counterparties with master netting agreements where netting benefit is reflected in the risk data | Target: 100% of counterparties with legally confirmed netting agreements reflect that benefit
  - *Timeliness* — Collateral values are refreshed at a frequency consistent with market volatility; margin calls are reflected within the production window | Age of most recent collateral valuation per netting set compared to as-of date | Target: collateral values no older than T-1 for liquid collateral; intraday for derivatives margin under stress

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Cross-System Counterparty Resolution**

- **Spans:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-05 (Risk Type Classification), CDE-08 (Industry/Sector Classification), CDE-11 (Net/Collateralised Exposure Amount)
- **What it is:** The process of confirming that a single real-world counterparty, represented under different identifiers, names, or codes in different source systems, resolves to one and only one enterprise counterparty identifier before aggregation occurs. This is not a property of any single element — it is the cross-system matching discipline that makes CDE-01 meaningful.
- **Why it is cross-cutting:** Even if each source system individually populates a counterparty ID, those IDs may refer to different master records for the same entity. The aggregate single-name exposure (¶46(a)) is invalid if the same obligor appears under three different identifiers in three systems and none is linked. No per-element DQ check can detect this; it requires a cross-system matching process.
- **Regulatory basis:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 5 (¶46(a)) — *"The aggregated credit exposure to a large corporate borrower"*
- **Data quality requirement:**
  - *Uniqueness* — After cross-system matching, each real-world counterparty is represented by exactly one enterprise counterparty identifier across all source systems | Count of counterparties with more than one enterprise identifier in the counterparty master following entity-resolution processing; count of open entity-resolution alerts | Target: 0 confirmed duplicates; all open alerts resolved within SLA
  - *Consistency* — The counterparty identifier assigned to an exposure in the risk data layer matches the identifier in the counterparty master and in the GL for the same obligor | Count of exposure records where the counterparty identifier in the risk system does not match the identifier used in the GL for the same underlying obligation | Target: 0 mismatches above materiality threshold

---

**XDQ-02 — Risk-to-Finance Reconciliation**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-04 (Position / As-Of Date), CDE-09 (GL / Source System Reconciliation Key), CDE-10 (Source System Identifier / Provenance Flag)
- **What it is:** The periodic, systematic comparison of aggregate risk positions to the corresponding balances in the general ledger or the systems of record, to confirm that the risk data layer is complete and accurate. This is the operational realisation of ¶36(c) and ¶53(a). It cannot be expressed as a rule on any single element because it requires joining two populations — risk records and GL entries — and comparing their totals.
- **Why it is cross-cutting:** Reconciliation requires the as-of date (CDE-04) to be aligned across both systems, the reconciliation key (CDE-09) to join the populations, the gross amount (CDE-03) to be the compared quantity, and the source system flag (CDE-10) to exclude EUC-sourced records from automated reconciliation where appropriate. The reconciliation breaks if any one of these elements is missing or inconsistent. No single-element monitor detects the reconciliation gap.
- **Regulatory basis:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Data quality requirement:**
  - *Accuracy* — The sum of gross exposure amounts in the risk data layer agrees to the corresponding balance in the GL or system of record, by asset class and legal entity, as of each reporting date | Sum of absolute and net variance between risk-layer totals and GL totals, by asset class and legal entity; count of line items with unexplained variance exceeding materiality threshold | Target: aggregate net variance ≤ materiality threshold (expressed as a percentage of total portfolio); zero unexplained variances above the threshold outstanding beyond the escalation window (e.g., 24 hours for month-end)
  - *Completeness* — All instrument types and booking entities present in the GL are represented in the risk data layer; no population is silently excluded | Count of GL balance sheet lines with no corresponding risk record; count of legal entities present in the GL consolidation but absent from the risk aggregation | Target: 0 missing instrument types above materiality; 0 missing legal entities in the consolidation perimeter

---

**XDQ-03 — Aggregation Dimension Completeness Across the Hierarchy**

- **Spans:** CDE-02 (Legal Entity), CDE-06 (Business Line), CDE-07 (Geography / Country of Risk), CDE-08 (Industry / Sector Classification)
- **What it is:** The confirmation that every exposure record can be simultaneously sliced by all four required aggregation dimensions — legal entity, business line, geography, and sector — without loss of records. Principle 4 requires risk data to be *"available by business line, legal entity, asset type, industry, region"*. Adaptability (Principle 6, ¶50) requires combinations of these dimensions to respond to ad hoc stress queries. If any dimension is unpopulated on a material share of records, the bank cannot produce the cross-dimensional cuts a supervisor or board might request.
- **Why it is cross-cutting:** Each dimension is governed as a separate CDE, but the requirement is not that each is individually populated — it is that all four are simultaneously populated on the same record, enabling joint slicing. A record with a valid legal entity code but a null sector code is invisible to a sector-by-entity concentration query. This joint completeness requirement cannot be expressed as a rule on any single element.
- **Regulatory basis:** Principle 4 (header) — *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*
- **Data quality requirement:**
  - *Completeness* — Every exposure record above the materiality threshold carries non-null values for all four aggregation dimensions simultaneously | Count (and percentage) of exposure records where one or more of the four dimension codes (legal entity, business line, country, sector) is null | Target: 0 records above materiality threshold missing any single dimension; <0.5% overall with all gaps identified and explained
  - *Consistency* — The combination of dimension codes on a record is internally coherent (e.g., the legal entity's domicile country is consistent with the booking geography; the business line is consistent with the product type) | Count of records where dimension code combinations violate defined coherence rules | Target: 0 coherence violations for material records

---

## 4. Out of Scope

The following requirements arise from Principles 1–11 but **cannot be met by a data catalog or data quality monitoring programme**. For each, the reason is specific to the nature of the requirement, not a general disclaimer.

---

**Principle 1 — Governance framework, board accountability, and independent validation (¶27–31)**

A catalog can hold documentation of data ownership, stewardship assignments, and SLA metadata, but it cannot create or enforce the governance *framework* itself. The requirements in ¶27–31 that are out of scope include:

- The board's formal approval of the risk data aggregation framework (¶28). This is a board resolution and committee minutes matter, not a metadata record.
- Independent validation of compliance with the Principles (¶29(a)). This requires a qualified internal audit or second-line review function with IT and data expertise, conducting a structured assessment against all Principles. A catalog does not conduct assessments.
- Due diligence of acquired entities' data capabilities (¶29(b)). This is a transactional process requiring human assessment, not a catalog query.
- Senior management awareness of limitations (¶30–31). Awareness is a governance state that no catalog entry can guarantee. The catalog can *surface* known limitations (e.g., manual process flags from CDE-10), but surfacing a limitation does not constitute management awareness of it.

*What is needed instead:* A data governance operating model with defined RACI, a board-level data governance policy, and a periodic independent validation programme with documented findings and remediation tracking.

---

**Principle 2 — IT infrastructure resilience and business continuity (¶32)**

¶32 requires risk data aggregation capabilities to be *"given direct consideration as part of a bank's business continuity planning processes and be subject to a business impact analysis."* A catalog can document system dependencies and data flow architecture (which informs a BIA) but cannot itself conduct a business impact analysis, establish recovery time objectives, or test resilience under stress.

*What is needed instead:* A formal BCP/DR programme with documented RTO/RPO for risk data systems, tested through simulation exercises. The catalog's lineage metadata (CDE-10, XDQ-02) is an input to that programme, not a substitute for it.

---

**Principle 3 — Dictionary of concepts (¶37)**

¶37 states that *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation."* This is precisely what a data catalog's business glossary is designed to support, and the CDEs above are direct outputs of that requirement. **However**, the mere existence of definitions in a catalog does not satisfy ¶37 — the requirement is that definitions are *used consistently across the organisation*, which depends on adoption, training, and enforcement by data owners. A catalog contains the dictionary; it does not guarantee its use.

*What is needed instead:* Active glossary governance — steward assignments, definition approval workflows, periodic review cycles, and evidence that source system owners have aligned their local definitions to the enterprise glossary. The catalog is necessary but not sufficient.

---

**Principle 7 — Report reconciliation processes and exception management (¶53)**

¶53(a) requires *"defined requirements and processes to reconcile reports to risk data"* and ¶53(c) requires *"integrated procedures for identifying, reporting and explaining data errors … via exceptions reports."* The CDE register and XDQ-02 above address the *data quality* aspects of reconciliation. However, the *process* requirements — who runs the reconciliation, what the escalation path is, how exceptions are documented and cleared, and how the reconciliation result is attested in the report itself — are operational process design matters.

A catalog can flag reconciliation failures (via XDQ-02 monitoring), but it cannot run the reconciliation, assign and track exceptions, or produce the attestation that a report has been reconciled. These require workflow tooling, an exceptions management process, and documented sign-off procedures.

*What is needed instead:* A reconciliation framework with defined process owners, an exceptions log with SLA-driven resolution, and report-level attestation of reconciliation status prior to distribution.

---

**Principle 8 — Report comprehensiveness: content, capital measures, stress test results, forward-looking forecasts (¶57–60)**

Principle 8 drives two CDEs above: CDE-05 (Risk Type Classification) and CDE-08 (Industry/Sector Classification) are directly derived from ¶57's requirement to report by risk area and sector. **These elements are within scope and appear in the CDE register.**

However, the broader content obligations of ¶57–60 are not addressable by a catalog:

- Whether reports *include* regulatory and economic capital, stress testing results, and liquidity figures (¶57, ¶59) is a report design matter — it depends on what the report author chooses to include, not on whether the underlying data elements are governed.
- The requirement for forward-looking assessments, forecasts, and scenario results (¶60) involves model outputs and qualitative judgements that are produced by risk systems and analysts, not by metadata management.
- Whether report depth and scope are *"consistent with the size and complexity of the bank's operations"* (¶8 header) is a governance and editorial judgement.

*What is needed instead:* A report design standard, a report inventory with coverage mapping against required risk areas, and a board-level review of whether received reports meet comprehensiveness requirements (¶64–65).

---

**Principle 9 — Report clarity, usefulness, and recipient feedback (¶61–69)**

¶67 requires *"an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports."* This maps directly to a data catalog's business glossary and report lineage, and is implicitly supported by the CDE register and the glossary work driven by ¶37.

However, the remaining substance of Principle 9 is not addressable:

- Whether reports communicate in a *clear and concise manner* (¶9 header) is a presentational and editorial standard, not a data governance one.
- The balance of quantitative versus qualitative content varying by recipient level (¶62) is a report design policy.
- Periodic confirmation with recipients that information is relevant and appropriate (¶69) is a governance feedback loop — a management practice, not a monitoring rule.
- Board responsibility for determining its own reporting requirements (¶64) is a governance process.

*What is needed instead:* Report design standards, recipient feedback mechanisms (e.g., annual report review by the board risk committee), and documented report change management processes.

---

**Principle 10 — Report frequency and stress/crisis escalation (¶70–71)**

A catalog has no mechanism to set, enforce, or test report production frequencies. ¶70 requires the bank to *"assess periodically the purpose of each report and set requirements for how quickly the reports need to be produced"* and to *"routinely test its ability to produce accurate reports within established timeframes."*

CDE-04 (Position / As-Of Date) and its timeliness DQ rules confirm that *data* arrives within SLA, but this is a necessary condition, not a sufficient one. Whether the *report* is produced and distributed on time under normal and stress conditions is a production operations and testing matter.

*What is needed instead:* A report production schedule with documented frequency requirements per risk type, periodic drill exercises simulating stress conditions, and production monitoring that triggers escalation when report generation is delayed.

---

**Principle 11 — Report distribution and confidentiality (¶72–73)**

Distribution of reports to the right recipients while maintaining confidentiality is an access control, identity management, and document distribution matter. A catalog can document who is the intended audience for a dataset (and a well-governed catalog will do so), but it does not control report distribution systems, email, or portal access permissions.

*What is needed instead:* Report distribution lists managed in a controlled distribution system, access control policies for risk reports, and periodic confirmation that distribution lists remain current (¶73).

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | **3** | 2 (¶33), 5 (¶46a) | Uniqueness, Completeness, Validity |
| CDE-02 | Legal Entity / Booking Entity Identifier | **3** | 2 (¶33), 4 (¶41) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | **3** | 4 (¶41), 5 (¶46a) | Accuracy, Completeness, Timeliness |
| CDE-04 | Position / As-Of Date | **3** | 5 (¶44), 6 (¶50) | Validity, Consistency, Timeliness |
| CDE-05 | Risk Type Classification | **2** | 4 (header), 8 (¶57) | Validity, Completeness, Consistency |
| CDE-06 | Business Line | **2** | 4 (header), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-07 | Geography / Country of Risk | **2** | 4 (header), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-08 | Industry / Sector Classification | **2** | 4 (header), 8 (¶57), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-09 | GL / Source System Reconciliation Key | **2** | 3 (¶36c), 7 (¶53a) | Completeness, Uniqueness, Accuracy |
| CDE-10 | Source System Identifier / Data Provenance Flag | **2** | 3 (¶36b, ¶36d, ¶39) | Completeness, Validity, Accuracy |
| CDE-11 | Net / Collateralised Exposure Amount | **2** | 4 (¶41), 8 (¶58), 5 (¶46b) | Accuracy, Completeness, Timeliness |

**Cross-cutting DQ requirements:**

| XDQ | Name | Spans | Dimensions |
|---|---|---|---|
| XDQ-01 | Cross-System Counterparty Resolution | CDE-01, 03, 05, 08, 11 | Uniqueness, Consistency |
| XDQ-02 | Risk-to-Finance Reconciliation | CDE-03, 04, 09, 10 | Accuracy, Completeness |
| XDQ-03 | Aggregation Dimension Completeness Across the Hierarchy | CDE-02, 06, 07, 08 | Completeness, Consistency |