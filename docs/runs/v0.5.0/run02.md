# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and scope

**What the regulation is trying to achieve**

- **Reliable aggregation under stress.** Banks must be able to produce accurate, complete, and timely aggregate risk figures not only in normal conditions but during crises — including intraday when required. The driving concern is that during 2007–09 many banks could not tell their own boards what their exposures were. (¶35: *"risk management reports reflect the risks in a reliable way"*; ¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis."*)

- **A single, governed data architecture.** Banks must establish integrated data taxonomies, single identifiers, and unified naming conventions across the banking group so that the same counterparty, legal entity, or account is represented consistently everywhere. (¶33: *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts."*)

- **Demonstrated accuracy through reconciliation.** Risk data must be reconciled to accounting sources and a single authoritative source of record must be identifiable for each risk type. An aggregate that cannot be traced back and verified is non-compliant, not merely imperfect. (¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."*)

- **Completeness across all material dimensions.** Every material exposure — including off-balance-sheet — must be captured and must be sliceable by business line, legal entity, asset type, industry, region, and other relevant groupings. Gaps must be identified, explained, and assessed for impact. (¶41: *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*; ¶43: *"Supervisors expect banks' data to be materially complete, with any exceptions identified and explained."*)

- **Documented lineage and control over manual processes.** Every aggregation process — automated or manual — must be documented. Manual and end-user-computing inputs require specific mitigants and must be flagged explicitly. (¶36(b), ¶39: *"document and explain all of their risk data aggregation processes whether automated or manual … an explanation of the appropriateness of any manual workarounds."*)

- **Board and senior management accountability.** The board must understand the limitations of what it receives; senior management must know what gaps exist and ensure IT strategy addresses them. (¶30: *"Senior management should be fully aware of and understand the limitations that prevent full risk data aggregation."*; ¶31.)

**Who it applies to**

Principles 1–11 are addressed to banks designated as Global Systemically Important Banks (G-SIBs) and Domestic SIBs, with implementation expected by January 2016 for G-SIBs. The Basel Committee explicitly expects supervisors to apply equivalent expectations to other significant banks over time. The governance, data architecture, and data quality obligations fall on the banking group as a whole — including subsidiaries and any outsourced functions. (¶27–28, ¶34.)

---

## 2. Critical Data Element candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** The unique, persistent, group-wide identifier assigned to each legal-entity counterparty — borrower, issuer, derivative counterparty, or guarantor — that resolves to the same entity regardless of which booking system originated the exposure.
- **Why critical:** Without a single resolvable counterparty identifier, exposures recorded in different systems (loans, derivatives, bonds, off-balance-sheet facilities) cannot be summed to a counterparty-level aggregate. The resulting total is not wrong by a margin — it is structurally incalculable, because there is no basis on which to decide whether two records refer to the same counterparty. *"Without this element, the aggregate credit exposure to counterparty X cannot be computed at all, because there is no key on which to join exposure records across booking systems."*
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality:** **3** — the aggregate figure "total exposure to counterparty X" cannot be computed at all if this key is null, duplicated, or non-resolvable across systems. A figure cannot even be produced, let alone reconciled.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41) — all material exposures must be capturable; Principle 5 (¶46(b)) — counterparty credit risk exposures are named as a critical risk requiring rapid aggregation.
- **Search terms:** customer ID, counterparty ID, obligor ID, entity ID, legal entity identifier (LEI), client reference, BIC, GIIN, counterparty reference number, global party identifier
- **Data quality requirements:**
  - *uniqueness* — Every active counterparty is represented by exactly one authoritative identifier in the group master; no two records in the master refer to the same legal entity. | Count of duplicate identifier values across booking systems after mapping to the group master; count of counterparties with more than one active master record. | Threshold: zero duplicates — a single duplicated key produces an incorrect aggregate and there is no materiality basis for tolerating structural key duplication. | **(¶33)**
  - *accuracy* — Every exposure record carries an identifier that resolves to a current record in the counterparty master. | Count of exposure records whose counterparty identifier is null, retired, or absent from the master. | Threshold: zero unresolvable identifiers — any null or broken join directly excludes an exposure from the aggregate. | **(¶40)**
  - *consistency* — The same counterparty identifier is used consistently for the same legal entity in every booking and risk system. | Count of active counterparty identifiers in source systems that map to more than one master record, or that are present in one system but absent from the master. | Threshold: zero cross-system mismatches — inconsistency makes consolidation impossible regardless of the size of individual exposures. | **(¶33)**

---

**CDE-02 — Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier of the bank's own legal entity in which a transaction or position is booked — the specific subsidiary, branch, or group entity responsible for the exposure from the bank's own side.
- **Why critical:** Group consolidation and solo subsidiary reporting both require the ability to partition all exposures by booking entity and then sum across entities. Without a resolvable booking-entity identifier, neither the group aggregate nor any subsidiary sub-aggregate can be correctly produced. *"Without this element, the aggregated risk exposure for subsidiary Y cannot be computed at all, because there is no basis on which to separate that subsidiary's book from the rest of the group."*
- **Risk types:** Cross-cutting (all risk types), concentration
- **Criticality:** **3** — the aggregate "total exposure of legal entity Y" cannot be computed without it. This is a structural joining key for group consolidation.
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 — *"data should be available by … legal entity"*; Principle 8 (¶57) — reports must cover all significant risk areas across the organisation.
- **Search terms:** legal entity ID, entity code, subsidiary code, booking entity, branch code, MFI code, LEI (own entity), legal entity reference, fund entity code, group entity identifier
- **Data quality requirements:**
  - *uniqueness* — Each of the bank's own legal entities has exactly one active identifier in the group entity master; no two records refer to the same registered legal entity. | Count of group-entity master records sharing the same registration details or LEI. | Threshold: zero — same reasoning as CDE-01: structural key duplication makes consolidation impossible. | **(¶33)**
  - *completeness* — Every exposure record carries a non-null, resolvable booking-entity identifier. | Count of exposure records with null or unresolvable booking-entity identifier. | Threshold: zero — any record without a booking entity cannot be attributed to a subsidiary or excluded from it. | **(¶43)**
  - *validity* — Every booking-entity identifier on an exposure record matches a currently active entry in the group entity master (i.e., not a closed, merged, or hypothetical entity). | Count of exposure records referencing a booking entity not present in the current active entity master. | Threshold: zero — a reference to a non-existent or merged entity produces a silent omission from the group aggregate. | **(¶40)**

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary value of an exposure before the application of credit risk mitigants (collateral, guarantees, netting), expressed in the original transaction currency. This is the primary quantity from which risk figures — EAD, PD-weighted exposure, concentration measures, VaR inputs — are built.
- **Why critical:** This is the number being aggregated. Every aggregate risk figure is ultimately a function of exposure amounts. If amounts are wrong, every derived figure is wrong. *"Without this element, the aggregate credit exposure to counterparty X cannot be computed at all, because there is no quantity to sum."*
- **Risk types:** Credit, counterparty credit, market, concentration
- **Criticality:** **3** — the aggregate itself cannot be computed without a valid exposure amount. The criticality sentence is literal and direct.
- **Driven by:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (¶41) — all material exposures must be captured; Principle 7 (¶52) — *"Risk management reports should be accurate and precise."*
- **Search terms:** gross exposure, notional amount, drawn balance, outstanding balance, mark-to-market value, replacement cost, exposure at default (EAD), notional principal, face value, carrying amount, outstanding principal
- **Data quality requirements:**
  - *accuracy* — Every exposure amount is consistent with the originating system of record and can be reconciled to it within the materiality threshold set under ¶56. | Sum of absolute reconciling differences between risk system exposure totals and the corresponding general ledger or system-of-record balances; expressed as a percentage of total portfolio balance. | Threshold: set by the bank's materiality policy under ¶56 (*"analogous to accounting materiality"*) — not zero, because approximation is explicitly recognised, but the threshold must be documented and approved. The bank's Finance or Risk function owns the threshold. | **(¶36(c), ¶56)**
  - *completeness* — No material exposure is absent from the aggregated dataset; off-balance-sheet exposures are present as well as on-balance-sheet. | Count and aggregate value of exposure records present in the originating system but absent from the risk aggregation dataset; flagged separately for off-balance-sheet items. | Threshold: zero missing records — any absent record is an absent exposure that distorts the aggregate. Where approximation applies (e.g., undrawn commitments modelled rather than recorded individually), the methodology must be documented per ¶42. | **(¶43)**
  - *validity* — No exposure amount carries an implausible sign, currency, or magnitude that would indicate a data entry or transformation error. | Count of records with null, zero (for drawn facilities), negative, or statistically extreme amounts relative to instrument type and booking-entity portfolio norms; count of records where currency code is absent or invalid. | Threshold: zero records outside validity rules — these are control failures, not materiality questions, and must trigger exception reporting per ¶53(c). | **(¶40)**

---

**CDE-04 — Risk Type / Risk Classification**

- **Definition:** The attribute that categorises each exposure or position by the type of risk it primarily represents: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk, or a defined sub-category thereof (e.g., trading book vs. banking book; derivatives vs. loans).
- **Why critical:** Aggregation is always performed within a risk type or across risk types in defined ways. An exposure with no risk classification, or with the wrong one, either goes into the wrong aggregate or into none. Limits, capital requirements, and regulatory reports are all structured around risk types, so misclassification directly distorts any figure drawn from those reports.
- **Risk types:** Cross-cutting
- **Criticality:** **2** — an aggregate can be produced, but it will include exposures belonging to a different risk type and exclude others, making the figure untrustworthy for the specific slice. The figure is produced but cannot be trusted by category.
- **Driven by:** Principle 4 — completeness requires data available *"by … asset type"*; Principle 7 (¶53(b)) — *"Automated and manual edit and reasonableness checks, including an inventory of the validation rules"*; Principle 8 (¶57) — *"reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*
- **Search terms:** risk type, risk category, risk class, asset class, product type, book type (trading/banking), risk taxonomy code, risk factor type, position type, instrument category
- **Data quality requirements:**
  - *validity* — Every exposure record carries a risk type code that belongs to the bank's approved risk taxonomy, as defined in the business dictionary required by ¶37. | Count of exposure records with null risk type, or with a code not present in the approved taxonomy reference table. | Threshold: zero — a record with no valid risk type is unclassifiable and will be excluded from every type-specific aggregate, constituting a completeness failure. | **(¶40, ¶37)**
  - *consistency* — The risk type assigned to a record in the risk system matches the classification applied to the same record in the general ledger and in any downstream reporting system, per the reconciliation obligation. | Count of records where risk-type code differs between the risk system and the GL or downstream report for the same transaction identifier. | Threshold: zero — a mismatch means the same exposure contributes to different aggregates in different systems, making reconciliation impossible. | **(¶36(c))**

---

**CDE-05 — Business Line**

- **Definition:** The internal organisational division or line of business to which an exposure or position is attributed — for example, retail banking, corporate banking, trading, private banking, or transaction banking — using the bank's own approved taxonomy.
- **Why critical:** Principle 4 explicitly requires risk data to be available by business line. Without this dimension, the bank cannot produce business-line sub-aggregates or demonstrate completeness across lines. It is also the primary dimension for internal limit-monitoring and P&L attribution, so errors distort both the aggregate slice and the limit check.
- **Risk types:** Cross-cutting
- **Criticality:** **2** — the group-level aggregate can still be produced, but the business-line slice cannot be correctly produced or reconciled to the group total. The figure is produced at group level but cannot be sliced.
- **Driven by:** Principle 4 — *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures … across all business lines and geographic areas."*
- **Search terms:** business line, business unit, division code, segment code, desk code, LOB (line of business), cost centre, profit centre, front-office unit, product line
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a non-null business line code. | Count and aggregate value of exposure records with null or missing business line. | Threshold: zero null values — any null is an exposure that cannot be attributed to any business-line aggregate, producing an irreducible gap in the slice. | **(¶43)**
  - *validity* — Every business line code matches a current entry in the approved organisational taxonomy. | Count of exposure records referencing a business line code not present in the current approved hierarchy, including legacy codes for reorganised or closed units. | Threshold: zero — stale codes can silently inflate or deflate specific business-line totals without appearing as nulls. | **(¶40)**

---

**CDE-06 — Geography / Country of Risk**

- **Definition:** The country to which an exposure is attributed for risk purposes — typically the country of the counterparty's domicile, the country of collateral, or the country of the obligor's primary operations, following the bank's approved country-risk methodology.
- **Why critical:** Principle 4 requires data available by region; ¶50 gives a concrete supervisory example requiring rapid aggregation of country credit exposures as of a specified date across all business lines and geographies. Country coding is also the primary dimension for concentration risk and sovereign risk reporting. An incorrect or missing country code places an exposure in the wrong geographic aggregate or in none.
- **Risk types:** Credit, concentration, market
- **Criticality:** **2** — the total exposure figure can be produced, but the geographic slice and any concentration measure derived from it are incorrect. The figure is produced but cannot be correctly sliced by country or region.
- **Driven by:** Principle 4 — *"Data should be available by … region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
- **Search terms:** country of risk, country code, country of domicile, booking country, ISO country code, geographic region, country of incorporation, sovereign exposure code, region code, NUTS code
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a non-null, ISO-standard country of risk code. | Count and aggregate value of exposure records with null or non-ISO country code. | Threshold: zero — any missing country code is an exposure that cannot be included in any geographic aggregate or stress scenario aggregation. | **(¶43)**
  - *validity* — Country codes conform to ISO 3166-1 alpha-2 or alpha-3 and reference a current, active country in the approved reference table. | Count of exposure records with country codes not matching the current ISO standard, including deprecated or placeholder codes. | Threshold: zero — invalid codes are systematically excluded from geographic aggregates, creating silent omissions. | **(¶40)**
  - *consistency* — The country of risk assigned in the risk system matches the country attribution in any downstream country-risk or sovereign-risk report for the same transaction. | Count of records where country code differs between risk system and downstream reporting for the same transaction identifier. | Threshold: zero — any mismatch means a geographic aggregate and its corresponding report disagree, making reconciliation under ¶53(a) impossible. | **(¶36(c))**

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The industry or economic sector assigned to a counterparty or exposure, using an approved classification scheme (e.g., NACE, GICS, SIC, or the bank's internal taxonomy), indicating the counterparty's primary business activity.
- **Why critical:** Principle 4 requires data available by industry; ¶50 gives the specific supervisory example of aggregating industry credit exposures across all business lines and geographic areas; ¶57 names industry sector as a required component of credit risk reports. An incorrect or absent sector code produces an incorrect sector concentration figure.
- **Risk types:** Credit, concentration
- **Criticality:** **2** — total credit exposure can be computed, but sector-level aggregates and concentration figures are incorrect. The figure is produced but the sector slice is wrong.
- **Driven by:** Principle 4 — *"Data should be available by … industry"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk."*
- **Search terms:** industry code, sector code, NACE code, GICS code, SIC code, industry classification, counterparty sector, economic sector, business sector, industry group
- **Data quality requirements:**
  - *completeness* — Every counterparty in the master and every exposure record carries a non-null industry/sector code. | Count and value of exposure records or counterparty master entries with null sector code. | Threshold: zero — any absent code is an exposure that cannot appear in any sector aggregate or concentration monitor. | **(¶43)**
  - *validity* — Every sector code belongs to the approved classification scheme version currently in use. | Count of records referencing codes not present in the current approved sector taxonomy, including codes from superseded versions of NACE/GICS. | Threshold: zero — references to deprecated codes cannot be reliably mapped to current sectors and will be excluded from aggregation. | **(¶40)**

---

**CDE-08 — Position / As-of Date**

- **Definition:** The business date as of which an exposure, position, or balance is stated — the date on which the snapshot of the risk data was taken for aggregation purposes.
- **Why critical:** Every aggregate risk figure is inherently dated. If the as-of date is missing, wrong, or inconsistent across records within a single aggregation run, the resulting aggregate mixes exposures from different dates. It is formally undated, meaning it cannot be compared to a limit, reported to a supervisor, or used for trend analysis. *"Without a valid as-of date, the aggregate figure 'total credit exposure as of date D' cannot be computed at all, because there is no basis on which to confirm that all constituent records belong to the same snapshot."*
- **Risk types:** Cross-cutting
- **Criticality:** **3** — an aggregate that mixes dates is not an aggregate for any specific date; it is an undefined mixture. The figure cannot validly be produced for any stated period.
- **Driven by:** Principle 5 — timeliness requires aggregate risk data to be *"up-to-date"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (¶55) — senior management must establish accuracy requirements for *"critical position and exposure information."*
- **Search terms:** as-of date, position date, value date, reference date, snapshot date, reporting date, effective date, trade date vs. settlement date, business date, cut-off date
- **Data quality requirements:**
  - *accuracy* — The as-of date on every record in an aggregation run matches the declared reference date for that run, with no records carrying a prior or future business date except where explicitly modelled (e.g., forward commitments with a documented methodology). | Count of records within an aggregation run whose as-of date differs from the run's declared reference date. | Threshold: zero undocumented mismatches — any mixed-date record corrupts the dated aggregate. Documented forward/historical items must carry a flag and an explanation per ¶39. | **(¶40)**
  - *timeliness* — For each risk type, risk data reaches the aggregation layer within the maximum latency defined by the bank's frequency requirements and, during stress, within the accelerated timeframe required by ¶45–46. | Time elapsed between the close of business on the reference date and the availability of a complete, reconciled aggregate dataset for each risk type; measured per run. | Threshold: set by the bank's documented frequency requirements per risk type (¶47). For critical risks named in ¶46 (counterparty credit, trading, liquidity), the threshold must reflect near-real-time or intraday capability during stress. The Risk function owns the threshold by risk type. | **(¶44–47)**

---

**CDE-09 — GL / Source System Reconciliation Key**

- **Definition:** The identifier that links a specific risk record to its corresponding entry in the general ledger or the designated system of record for that risk type — the key that makes it possible to trace a risk figure back to the accounting or operational source and confirm they agree.
- **Why critical:** ¶36(c) requires explicit reconciliation of risk data to accounting sources. Without a reconciliation key, the reconciliation cannot be performed at the individual-record level — it can only be done as an aggregate-to-aggregate comparison, which cannot identify which records are causing a difference. ¶53(a) requires defined processes to reconcile reports to risk data. A risk figure that cannot be reconciled to the system of record is, under the standard, not an evidenced figure. *"Without this element, the reconciliation of risk record R to its GL entry cannot be performed at all, because there is no key on which to join the two systems."*
- **Risk types:** Cross-cutting (all risk types)
- **Criticality:** **3** — an unverifiable figure is not a compliant one under ¶36(c). The reconciliation process cannot be performed without this key, which means accuracy cannot be evidenced regardless of whether the underlying amounts happen to be correct.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** GL reference, journal entry ID, trade ID, deal reference, system of record ID, source transaction ID, accounting reference, SWIFT reference, trade reference number, booking reference, loan ID, facility ID
- **Data quality requirements:**
  - *completeness* — Every risk record carries a non-null reconciliation key that references an entry in the GL or designated system of record. | Count of risk records with null or blank reconciliation key; count of risk records whose key does not match any entry in the designated system of record. | Threshold: zero — any missing key is an exposure that cannot be reconciled to the accounting source, making ¶36(c) compliance impossible for that record. | **(¶36(c))**
  - *consistency* — The exposure amount on a risk record agrees with the amount on the corresponding GL entry within the materiality threshold, for all records where a matching key exists. | Sum of absolute differences between risk-system amounts and GL amounts for matched records; count of matched records exceeding the materiality threshold. | Threshold: set by the bank's materiality policy under ¶56 — documented, approved, and reviewed at least annually by Finance and Risk. Zero is not appropriate here because ¶56 explicitly contemplates materiality-based accuracy requirements; but every out-of-tolerance difference must be investigated and resolved per ¶53(c). | **(¶36(c), ¶56)**
  - *accuracy* — Reconciliation differences are identified, documented, and subject to escalation and resolution within defined timeframes. | Count of open reconciliation breaks aged beyond the defined resolution SLA; count of breaks not accompanied by a documented explanation. | Threshold: zero unresolved aged breaks and zero unexplained breaks — timeliness of resolution is itself a control requirement under ¶40's escalation channel mandate. | **(¶40)**

---

**CDE-10 — Source System / Data Provenance Flag**

- **Definition:** The attribute that identifies, for each risk record, which source system produced it and whether its value was generated by an automated process or entered or modified manually (including end-user computing tools such as spreadsheets, Access databases, or other desktop applications).
- **Why critical:** ¶36(b) requires effective mitigants for manual and EUC inputs; ¶39 requires documentation of all aggregation processes, with specific explanation of manual workarounds and their criticality. Without this flag, the bank cannot demonstrate that it has applied the controls required for EUC inputs, cannot assess the degree of manual risk in its aggregation chain, and cannot satisfy a supervisor that the accuracy of manual-origin figures has been adequately controlled. Without the source system identifier, data lineage cannot be traced and the single-authoritative-source requirement of ¶36(d) cannot be enforced or evidenced.
- **Risk types:** Cross-cutting
- **Criticality:** **2** — aggregate figures can be produced, but the bank cannot demonstrate which portions are subject to elevated manual risk, cannot show that EUC mitigants were applied, and cannot evidence the lineage required for ¶36(d). The aggregate is produced but cannot be trusted in part — specifically, the manual-origin component cannot be distinguished.
- **Driven by:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications … it should have effective mitigants in place"*; ¶36(d) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; ¶39 — *"document and explain all of their risk data aggregation processes whether automated or manual … a description of their criticality to the accuracy of risk data aggregation."*
- **Search terms:** source system, source system ID, system of origin, data source flag, EUC flag, manual override flag, feed identifier, data feed name, input channel, extraction source, automated vs. manual indicator, end-user computing indicator
- **Data quality requirements:**
  - *completeness* — Every risk record carries a non-null source system identifier and a non-null automated/manual flag. | Count of risk records with null source system ID; count of records with null or ambiguous manual/automated indicator. | Threshold: zero — any missing provenance flag means that record cannot be classified for EUC-control purposes, undermining the bank's ability to demonstrate ¶36(b) compliance. | **(¶36(b), ¶39)**
  - *validity* — Every source system identifier references a registered, documented system in the bank's inventory of data sources. Unregistered sources are treated as EUC by default and subject to EUC controls. | Count of distinct source system identifiers in risk records that are absent from the approved source system register. | Threshold: zero — an unregistered source cannot have documented controls, lineage, or a single-authoritative-source designation, making ¶36(d) compliance impossible for records originating there. | **(¶36(d), ¶40)**
  - *accuracy* — The manual/automated flag accurately reflects the actual processing path of each record; misclassification of a manually-entered record as automated is treated as a control failure. | Count of records flagged as automated that originated in a known EUC tool (identified by source system ID matching the EUC register); assessed during periodic reconciliation of the source system register against actual data feeds. | Threshold: zero misclassified EUC records — misclassifying a manual input as automated means the required EUC mitigants are not applied to that record, which is a direct breach of ¶36(b). | **(¶36(b), ¶40)**

---

**CDE-11 — Collateral / Credit Risk Mitigant Identifier**

- **Definition:** The identifier that links an exposure to any collateral, guarantee, netting agreement, or other credit risk mitigant recognised under the bank's risk framework — the key that enables the bank to compute net exposure after mitigation.
- **Why critical:** Net exposure (EAD after CRM) is the basis for regulatory capital, concentration limits, and large-exposure calculations. Without a correctly linked mitigant, the bank overstates net exposure (if it ignores valid collateral) or understates it (if it incorrectly doubles-counts mitigation). Principle 4 requires all material exposures to be captured; ¶41's reference to off-balance-sheet items implies that netting and guarantee structures — which are typically off-balance-sheet — must be included. The mitigant identifier is the joining key that makes this possible.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality:** **2** — gross exposure aggregates can be produced correctly, but net exposure figures and regulatory capital calculations are distorted. The figure is produced but cannot be trusted where CRM is material.
- **Driven by:** Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 3 (¶36(c)) — reconciliation to accounting sources, which include collateral records; Principle 8 (¶57) — reports must reflect *"risk-related measures (eg regulatory and economic capital)."*
- **Search terms:** collateral ID, collateral reference, netting agreement ID, ISDA agreement reference, CSA reference, guarantee ID, CRM identifier, collateral pool ID, pledge reference, security interest reference, margin agreement ID
- **Data quality requirements:**
  - *completeness* — Every exposure subject to a recognised credit risk mitigant carries a resolvable mitigant identifier; mitigants without a corresponding exposure are also flagged. | Count of exposures flagged as collateralised or guaranteed in the originating system that carry null or unresolvable mitigant identifiers in the risk aggregation layer; count of mitigant records with no associated exposure. | Threshold: zero orphaned identifiers — any broken link means the mitigant is either not applied (overstating net exposure) or applied without a corresponding asset (understating exposure), both of which distort risk figures. | **(¶43)**
  - *accuracy* — The value of each mitigant as recorded in the risk system is consistent with the value in the collateral management or accounting system, within the bank's materiality threshold. | Sum of absolute differences between risk-system mitigant values and collateral-system values for matched identifiers, expressed as a percentage of total collateral value. | Threshold: set by materiality policy under ¶56 — the same basis as gross exposure reconciliation, owned by Finance and Risk. | **(¶36(c), ¶56)**

---

## 3. Cross-cutting data quality requirements

---

**XDQ-01 — Risk-to-Finance Reconciliation: Aggregate Exposure Totals**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (GL / Source System Reconciliation Key), CDE-02 (Legal Entity Identifier), CDE-08 (Position / As-of Date)
- **Rule intent:** The total exposure recorded in the risk aggregation layer, when summed by legal entity and as-of date, must reconcile to the corresponding balances in the general ledger for each portfolio. The purpose is not merely to compare two numbers but to confirm that every risk record has an accounting counterpart and every accounting balance has a risk record — i.e., that nothing is in risk but not in finance, and nothing is in finance but not in risk.
- **Measurement:** (a) Aggregate gross exposure in risk system by legal entity × as-of date, vs. corresponding GL balance by legal entity × accounting date — difference expressed in absolute value and as a percentage of portfolio total. (b) Count of risk records with no matching GL entry via CDE-09. (c) Count of GL entries within scope that have no matching risk record. Both (b) and (c) are direction-of-miss indicators that a single net difference obscures.
- **Threshold:** The aggregate monetary difference is governed by the bank's materiality policy per ¶56, owned and documented by Finance and approved by senior management. The counts in (b) and (c) must be zero — an unmatched record is a structural gap, not a materiality question, and must trigger the exception-reporting process required by ¶53(c).
- **Why this cannot be expressed as a single-element check:** The reconciliation is inherently a join across CDE-03, CDE-09, CDE-02, and CDE-08. Monitoring any one of these in isolation tells you whether a field is populated; only the cross-system comparison tells you whether the figures agree.
- **(¶36(c), ¶53(a), ¶56)**

---

**XDQ-02 — Single Counterparty Resolution: Cross-System Identity Matching**

- **Spans:** CDE-01 (Counterparty Identifier), CDE-05 (Business Line), CDE-06 (Geography / Country of Risk), CDE-11 (Collateral / Credit Risk Mitigant Identifier)
- **Rule intent:** Every booking system that originates an exposure to the same legal-entity counterparty must reference that counterparty through a single, resolvable identifier that maps to the same master record. The purpose is to ensure that when counterparty-level aggregation is performed — summing loans from the corporate banking system, derivatives from the trading system, and bonds from the treasury system — all three are correctly attributed to the same counterparty. This is the operational realisation of the single-identifier requirement in ¶33.
- **Measurement:** (a) For each counterparty master record, count the number of distinct source-system identifiers that map to it (expected: one per system, all mapping to the same master). (b) Count of counterparties represented by more than one master record (fragmented identity). (c) Count of exposure records in each booking system whose counterparty identifier does not resolve to any master record (orphaned exposures). (d) For counterparties present in more than one booking system, compare the legal entity name, LEI, and domicile country recorded in each system — count of discrepancies. Discrepancies in (d) indicate that the same legal entity has been set up differently in different systems, which is a precursor to duplication failures.
- **Threshold:** All counts in (a)–(d) must be zero for structural mapping failures. Where approximate name-matching is used during a remediation exercise, the bank must document the matching methodology and have it reviewed independently per ¶29(a). The target is zero orphaned exposures and zero fragmented master records, because there is no materiality basis for tolerating a counterparty that cannot be aggregated.
- **Why this cannot be expressed as a single-element check:** CDE-01 monitors whether an identifier is present and resolves within one system. This cross-cutting check monitors whether the same identifier — or a consistently mapped identifier — is used for the same legal entity across all systems simultaneously. That property is only observable by comparing records across systems, not by inspecting any single system's records.
- **(¶33, ¶40, ¶43)**

---

## 4. Out of scope

The following principles, or significant portions of them, impose obligations that no CDE register or data quality monitoring programme can satisfy. They require management decisions, governance processes, and report-design work that lie outside what a catalog can address.

---

**Principle 1 — Governance (¶27–31):** The principle requires board and senior management to approve the risk data aggregation framework, deploy adequate resources, incorporate data quality risk into the risk management framework, and understand the limitations of what they receive. A catalog can document the framework, register data owners (¶34), and surface evidence of quality failures for escalation — but it cannot constitute the governance framework itself, make resource allocation decisions, or ensure that board members have read and understood the limitations. The management and board obligations are entirely out of catalog scope.

*Note:* ¶34's requirement to establish data ownership roles is partially addressable: a catalog can hold the register of data owners, stewards, and IT owners, and can make that ownership visible to auditors and supervisors. But the act of assigning those roles and holding people accountable for them is a governance action, not a catalog function.

**Principle 2 — Data Architecture (¶32–35):** The IT infrastructure and business continuity obligations (¶32, ¶35) — designing systems to function under stress, conducting business impact analysis, building automated aggregation pipelines — are technology and engineering requirements that a catalog documents but does not implement. ¶33 and ¶37 are the exceptions: the requirement for single identifiers, unified naming conventions, and a dictionary of concepts is directly addressable in a catalog through the CDE register, term definitions, and cross-system identifier mapping described in CDE-01, CDE-02, and CDE-04 above.

**Principle 6 — Adaptability (¶48–51):** The ability to re-aggregate data on demand, drill down by new dimensions, and respond to supervisory ad hoc queries is a capability of the risk data infrastructure. A catalog can document what dimensions are available for slicing (CDE-05, CDE-06, CDE-07) and flag when a requested dimension has no coverage — but the actual on-demand aggregation capability is an engineering and architecture matter outside catalog scope.

**Principle 7 — Accuracy of Reports (¶52–56):** The reconciliation-to-source requirement (¶53(a)) and the exception-reporting procedures (¶53(c)) are partly addressable: CDE-09 and XDQ-01 provide the data elements and cross-system checks needed to support reconciliation. However, the act of defining reasonableness checks, maintaining an inventory of validation rules with their mathematical relationships (¶53(b)), and operating the exception management process (¶53(c)) are procedural and system controls, not catalog metadata. The catalog can hold references to those rule inventories and link them to CDEs, but cannot run the report-layer validation itself.

**Principle 8 — Comprehensiveness (¶57–60):** This principle simultaneously drives two CDEs (CDE-07 — Industry Sector is named directly in ¶57; CDE-04 — Risk Type is implied by the requirement to cover all risk areas) and imposes report-content obligations that are entirely outside catalog scope. The requirement to include forward-looking forecasts, stress test results, capital adequacy projections, and inter-risk concentration assessments in reports (¶57–60) is a risk management reporting design obligation. A catalog can confirm that the underlying data elements are present and monitored — it cannot design or produce the reports, ensure they contain the right qualitative interpretations, or confirm they are comprehensive relative to the bank's risk profile. These are distinct: the presence of a CDE with clean quality scores does not guarantee that a report built from it satisfies ¶58's forward-looking requirement.

**Principle 9 — Clarity and Usefulness (¶61–69):** The obligations here — ensuring reports are clear, tailored to recipients, appropriately balanced between quantitative and qualitative content, and periodically validated as relevant by recipients (¶69) — are content and communication design obligations. ¶67's requirement to maintain an inventory and classification of risk data items with references to the concepts used in reports is partially addressable: the CDE register in a catalog is precisely this inventory. But the judgment about whether a report is clear, whether the balance of qualitative and quantitative content is appropriate for the board, and whether recipients are asked to confirm relevance (¶69) cannot be encoded as a data quality rule or a metadata attribute. These require governance process, not catalog function.

**Principle 10 — Frequency (¶70–71):** The obligation to set and periodically reassess report frequency requirements, test production capability within established timeframes (¶70), and ensure critical reports are available within very short periods during stress (¶71) is a governance and operational capability matter. The timeliness DQ check on CDE-08 monitors whether data arrives within the defined frequency window, but it does not itself set that window, test report production under stress, or make the organisational decision about what "timely" means for each risk type. Those are management decisions that precede and authorise the thresholds in the timeliness checks.

**Principle 11 — Distribution (¶72–74):** The requirements to disseminate reports to appropriate recipients promptly and to maintain confidentiality are access-control and process obligations. They concern who receives reports and how quickly — matters for entitlement management, document distribution systems, and information security governance. A catalog can document data sensitivity classifications (contributing to confidentiality design), but it cannot implement distribution controls, confirm that reports reached the right people, or verify that confidentiality was maintained in practice.

---

## 5. Summary table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | P2 (¶33), P4 (¶41), P5 (¶46) | Uniqueness, Accuracy, Consistency |
| CDE-02 | Legal Entity Identifier (Booking Entity) | 3 | P2 (¶33), P4, P8 (¶57) | Uniqueness, Completeness, Validity |
| CDE-03 | Gross Exposure Amount | 3 | P3 (¶36(a), ¶36(c)), P4 (¶41), P7 (¶52) | Accuracy, Completeness, Validity |
| CDE-04 | Risk Type / Risk Classification | 2 | P4, P7 (¶53(b)), P8 (¶57) | Validity, Consistency |
| CDE-05 | Business Line | 2 | P4, P6 (¶50) | Completeness, Validity |
| CDE-06 | Geography / Country of Risk | 2 | P4, P6 (¶50) | Completeness, Validity, Consistency |
| CDE-07 | Industry / Sector Classification | 2 | P4, P6 (¶50), P8 (¶57) | Completeness, Validity |
| CDE-08 | Position / As-of Date | 3 | P5 (¶44–47), P6 (¶50), P7 (¶55) | Accuracy, Timeliness |
| CDE-09 | GL / Source System Reconciliation Key | 3 | P3 (¶36(c)), P7 (¶53(a)) | Completeness, Consistency, Accuracy |
| CDE-10 | Source System / Data Provenance Flag | 2 | P3 (¶36(b), ¶36(d), ¶39) | Completeness, Validity, Accuracy |
| CDE-11 | Collateral / Credit Risk Mitigant Identifier | 2 | P4 (¶41), P3 (¶36(c)), P8 (¶57) | Completeness, Accuracy |
| XDQ-01 | Risk-to-Finance Reconciliation | Cross-cutting | P3 (¶36(c)), P7 (¶53(a), ¶56) | Accuracy, Consistency, Completeness |
| XDQ-02 | Single Counterparty Resolution | Cross-cutting | P2 (¶33), P3 (¶40), P4 (¶43) | Uniqueness, Accuracy, Consistency |