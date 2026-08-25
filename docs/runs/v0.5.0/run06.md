# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a structural property, not a best-effort outcome.** A bank must be able to produce accurate, complete and timely aggregated risk data under both normal and stress conditions — not just when systems are working well. The stress case is the design constraint. (¶35: *"risk data aggregation capabilities should meet all Principles below simultaneously"*; ¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*)

- **Data quality treated with the same rigour as financial accounting.** Controls around risk data must be as robust as those applied to accounting data, and risk data must be reconciled to accounting and source systems to evidence accuracy. (¶36(a): *"Controls surrounding risk data should be as robust as those applicable to accounting data."*; ¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate."*)

- **A single, authoritative, well-documented data architecture.** Banks must establish integrated data taxonomies, single identifiers, unified naming conventions, and a "dictionary" of consistently defined concepts — the direct mandate for a data catalog. (¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*; ¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation."*)

- **Measurable and monitored data quality, with escalation.** Banks must not merely aspire to quality — they must measure it, monitor it, and have escalation channels and action plans in place. (¶40: *"Supervisors expect banks to measure and monitor the accuracy of data and to develop appropriate escalation channels and action plans to be in place to rectify poor data quality."*; ¶43: *"Supervisors expect banks to produce aggregated risk data that is complete and to measure and monitor the completeness of their risk data."*)

- **Full dimensionality: aggregation must be sliceable.** Risk data must be available by business line, legal entity, asset type, industry, region, and other groupings. The ability to slice is not a reporting nicety — it is a compliance requirement. (¶41 / Principle 4 heading: *"Data should be available by business line, legal entity, asset type, industry, region and other groupings."*)

- **Governance accountability is traceable to the board.** Senior management must understand aggregation limitations; the board approves the framework. Ownership of data quality is a named responsibility shared between business and IT functions. (¶28: *"A bank's board and senior management should review and approve the bank's group risk data aggregation and risk reporting framework."*; ¶34: *"Roles and responsibilities should be established as they relate to the ownership and quality of risk data."*)

**Who it applies to**

Globally systemically important banks (G-SIBs) are the primary addressees, with national supervisors expected to apply the principles to domestically systemically important banks (D-SIBs) proportionately. The obligations run to the consolidated banking group — subsidiaries, legal entities and business lines are explicitly within scope (¶41, ¶33).

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** A unique, persistent identifier assigned to each counterparty (borrower, issuer, derivative counterparty, guarantor) that is consistent across all systems in the banking group — front office, risk, finance, and operations. Distinct from account or facility identifiers; it identifies the legal or natural person, not the relationship or instrument.
- **Why critical:** Without a single resolvable counterparty identifier, exposures held in different systems cannot be summed to produce a correct aggregated counterparty exposure. The aggregate figure is not merely imprecise — it cannot be computed at all, because the join between systems has no key. This is the most common failure mode BCBS 239 was written to address.
- **Risk types:** Credit / counterparty credit / concentration / cross-cutting
- **Criticality: 3.** Without this element, the aggregated credit exposure to a single counterparty across systems cannot be computed at all, because there is no consistent key on which to join exposure records from different source systems. A null or unresolvable counterparty identifier means the exposure is simply omitted from the aggregate — the figure is invalid, not merely degraded.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶46(a)) — *"The aggregated credit exposure to a large corporate borrower"* named as a critical risk.
- **Search terms:** counterparty ID, counterparty identifier, party ID, legal entity identifier, LEI, customer ID, obligor ID, counterparty reference, GCID (global counterparty ID), golden source party
- **Data quality requirements:**
  - *uniqueness* — Every counterparty record in the risk data store maps to exactly one counterparty identifier; no two distinct counterparties share an identifier | count of duplicate counterparty identifiers across systems | threshold: zero duplicates — a duplicate identifier merges separate counterparties' exposures, producing an aggregation error regardless of magnitude | **(¶33)**
  - *validity* — Every exposure record carries a counterparty identifier that resolves to a record in the authoritative counterparty master | count of exposure records with null or unresolvable counterparty identifier | threshold: zero — any unresolved identifier silently excludes an exposure from the aggregate | **(¶40, ¶43)**
  - *consistency* — The counterparty identifier used in the risk system matches the identifier used in the general ledger for the same counterparty | count of exposure records where the counterparty identifier in the risk system does not match the corresponding identifier in the GL | threshold: zero — a mismatch breaks reconciliation between risk and accounting data | **(¶36(c))**

---

**CDE-02 — Legal Entity Identifier (Bank's Own Booking Entity)**

- **Definition:** The identifier for each legal entity within the banking group that is the booking entity for a risk exposure — i.e., the subsidiary or branch in whose name the transaction is recorded. This is the bank's own legal entity, not the counterparty's.
- **Why critical:** Group-level risk aggregation requires summing exposures booked across multiple legal entities. Without a consistent legal entity identifier, exposures cannot be allocated to the correct subsidiary for solo-entity reporting, nor summed correctly for consolidated group reporting. It is also the key by which cross-jurisdictional data-sharing limitations are managed (¶30).
- **Risk types:** Cross-cutting / concentration / credit / market / liquidity
- **Criticality: 3.** Without this element, the consolidated group-level aggregate cannot be computed — exposures cannot be allocated to legal entities, so subsidiary reporting is impossible and consolidation has no structure. The aggregate figure for any legal entity is invalid.
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (heading) — *"capture and aggregate all material risk data across the banking group"*; ¶30 — *"coverage (eg risks not captured or subsidiaries not included)"* as an explicit limitation to be managed.
- **Search terms:** legal entity ID, entity code, booking entity, subsidiary code, branch code, LEI (bank own), organisational unit, consolidated entity, solo entity, group entity hierarchy
- **Data quality requirements:**
  - *uniqueness* — Each legal entity within the banking group has exactly one identifier; no entity is represented by more than one code | count of distinct identifiers mapping to the same legal entity in the entity hierarchy | threshold: zero — duplicate entity codes split an entity's exposure across records and corrupt both the entity-level and group-level aggregates | **(¶33)**
  - *completeness* — Every exposure record contains a populated and valid legal entity identifier | count of exposure records with null or unresolvable legal entity identifier | threshold: zero — an unattributed exposure cannot be included in any entity-level aggregate or excluded correctly from consolidation | **(¶43)**
  - *validity* — Every legal entity identifier in risk data resolves to an entry in the authoritative group entity hierarchy | count of legal entity identifiers in risk data not present in the group structure master | threshold: zero — a code that does not resolve to a known entity cannot be consolidated | **(¶40)**

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The pre-mitigation monetary value of an exposure — the amount at risk before the application of collateral, guarantees, netting, or credit risk mitigants. Expressed in transaction currency and, separately, in a common reporting currency after conversion. Covers on-balance-sheet and off-balance-sheet positions.
- **Why critical:** This is the quantity being aggregated. Every risk aggregate — counterparty exposure, sector concentration, portfolio total — is ultimately a sum of this element. If the value is wrong, the aggregate is wrong. The explicit inclusion of off-balance-sheet exposures in ¶41 means that omitting or mismeasuring contingent commitments also corrupts the aggregate.
- **Risk types:** Credit / counterparty credit / concentration / cross-cutting
- **Criticality: 3.** Without a populated and accurately valued exposure amount, the aggregate figure — the sum of credit exposures to a counterparty, sector, or region — cannot be computed at all. A null or misstated amount produces an aggregate that is wrong by the full value of the missing or incorrect position.
- **Driven by:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 5 (¶46(a)) — *"The aggregated credit exposure to a large corporate borrower"* as a critical risk requiring rapid aggregation.
- **Search terms:** exposure amount, gross exposure, notional amount, outstanding balance, drawn amount, off-balance-sheet exposure, committed amount, mark-to-market value, replacement cost, EAD (exposure at default), face value
- **Data quality requirements:**
  - *accuracy* — The gross exposure amount for each record agrees with the corresponding value in the authoritative source system (front-office system or general ledger) within materiality | sum of absolute differences between risk system exposure amounts and source system amounts, measured at position level | threshold: set by materiality per ¶56 — *"if omission or misstatement could influence the risk decisions of users, this may be considered material"*; the bank's risk framework owner defines the materiality threshold and documents the rationale | **(¶36(a), ¶56)**
  - *completeness* — Every known position in the source system has a corresponding exposure record in the risk aggregation system | count of source system positions with no matching record in the risk data store | threshold: zero material omissions — ¶41 requires all material exposures including off-balance-sheet; any missing material position corrupts the aggregate | **(¶43, ¶41)**
  - *validity* — Every exposure amount is a non-null, non-negative (or signed consistently with position type conventions) numeric value | count of exposure records with null, non-numeric, or sign-inconsistent amounts | threshold: zero — a null or invalid amount cannot be included in an aggregate | **(¶40)**

---

**CDE-04 — Risk Type Classification**

- **Definition:** The categorical label that assigns each exposure or position to a primary risk type — at minimum: credit risk, market risk, liquidity risk, operational risk. May include sub-classifications (e.g., counterparty credit risk as a sub-type of credit). This is the taxonomy element that governs which risk framework, limit structure, and capital treatment applies.
- **Why critical:** Risk aggregation is performed within risk types, not across them indiscriminately. A misclassified exposure is aggregated into the wrong risk bucket — it inflates one total and deflates another. It also determines which timeliness requirement applies (¶45–46 differentiate by risk type) and which report it appears in (¶57 requires reports covering all significant risk areas).
- **Risk types:** Cross-cutting
- **Criticality: 2.** The exposure amount is captured and the aggregate for each risk type is produced, but a misclassified exposure appears in the wrong aggregate — the credit risk total is understated and the market risk total is overstated, or vice versa. The aggregates are produced but cannot be trusted in part.
- **Driven by:** Principle 4 (heading and ¶41) — *"capture and aggregate all material risk data across the banking group"* with data available by groupings *"as relevant for the risk in question"*; Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*
- **Search terms:** risk type, risk category, risk class, risk taxonomy, risk classification, product risk type, asset class risk mapping, risk bucket
- **Data quality requirements:**
  - *validity* — Every exposure record carries a risk type classification drawn from the bank's approved risk taxonomy | count of exposure records with a null, blank, or non-standard risk type value | threshold: zero — an unclassified exposure cannot be routed to the correct aggregate or subject to the correct timeliness requirement | **(¶40)**
  - *consistency* — The risk type classification applied in the risk system matches the classification applied in capital and regulatory reporting systems for the same instrument | count of instruments where risk type differs between risk and regulatory reporting systems | threshold: zero — a mismatch means the same exposure is counted differently in different reports, which is a reporting accuracy failure | **(¶36(c), ¶53(a))**
  - *completeness* — All material exposure types recognised in the bank's risk framework are represented in the risk type taxonomy; no material risk category is absent | periodic review by risk owners of the taxonomy against the bank's approved risk appetite statement | threshold: no material risk type absent — set by risk framework owner with reference to the bank's risk profile; supervisory expectation is that all significant risk areas are covered | **(¶43, ¶57)**

---

**CDE-05 — Business Line**

- **Definition:** The label that identifies the internal business division or segment to which an exposure or position is attributed — for example, retail banking, corporate banking, trading, wealth management. Must be defined consistently across the banking group and mappable to the group organisational structure.
- **Why critical:** Principle 4 explicitly requires data to be available by business line. Without this element, the bank cannot produce business-line-level risk reports, cannot identify concentrations within a business line, and cannot respond to supervisory ad hoc queries requiring business-line breakdowns (¶50).
- **Risk types:** Cross-cutting / concentration
- **Criticality: 2.** Risk aggregates at the group level are produced, but the business-line slice is unavailable or unreliable. Reports cannot be decomposed to business line, which is a named requirement. Emerging concentrations within a business line cannot be identified.
- **Driven by:** Principle 4 (heading) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures … across all business lines and geographic areas."*
- **Search terms:** business line, business unit, division, segment, desk, product line, organisational unit, cost centre, profit centre, front office division
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a populated business line attribution | count of exposure records with null or missing business line | threshold: zero — an unattributed exposure cannot appear in any business-line aggregate and produces an understated subtotal | **(¶43)**
  - *validity* — Every business line value resolves to an entry in the bank's approved organisational hierarchy | count of exposure records with a business line code not present in the approved hierarchy | threshold: zero — an unresolvable code cannot be mapped to a correct subtotal | **(¶40)**
  - *consistency* — Business line attribution is applied using the same definitions across all source systems contributing to risk aggregation | count of instruments where business line attribution differs between source systems for the same instrument | threshold: zero material inconsistencies — different attributions for the same exposure produce double-counting or omission in cross-system aggregates | **(¶33)**

---

**CDE-06 — Geography / Country**

- **Definition:** The country or jurisdiction to which an exposure is attributed for risk reporting purposes — typically the country of the counterparty's domicile or the country of the underlying asset, depending on the risk type. Must be applied consistently across the group.
- **Why critical:** Principle 4 requires data available by region; ¶50 gives country credit exposure as the primary example of an ad hoc aggregation a bank must be able to produce quickly. Without a consistent country attribution, country concentration risk cannot be measured, and supervisory queries on geographic exposure cannot be answered.
- **Risk types:** Credit / concentration / cross-cutting
- **Criticality: 2.** Group-level aggregates are produced, but geographic slices are unavailable or inconsistent. The bank cannot respond to the ¶50 scenario (country credit exposure as of a specified date) or identify cross-border concentrations. The aggregate is produced but cannot be sliced as required.
- **Driven by:** Principle 4 (heading) — *"Data should be available by … region and other groupings"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
- **Search terms:** country code, country of risk, domicile country, booking country, country of incorporation, geographic region, jurisdiction, country attribution, ISO country code
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a country attribution | count of exposure records with null or missing country | threshold: zero — a missing country attribution excludes the exposure from any country-level aggregate | **(¶43)**
  - *validity* — Every country code resolves to a recognised sovereign jurisdiction in an approved reference list (e.g., ISO 3166) | count of country codes not present in the approved reference list | threshold: zero — unrecognised codes cannot be mapped to geographic aggregates | **(¶40)**
  - *consistency* — The country attribution methodology (country of risk vs. country of domicile vs. booking country) is applied consistently across all source systems and is documented | periodic review of attribution rules across systems; count of instruments where attribution methodology differs across systems | threshold: zero undocumented methodology differences — different methodologies produce incomparable geographic aggregates | **(¶33, ¶37)**

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The economic sector or industry to which a counterparty or exposure is attributed — for example, using a standard classification such as GICS, NACE, or SIC, or an internal equivalent. Applied at counterparty or instrument level and used to identify sector concentrations.
- **Why critical:** Principle 4 requires data by industry; ¶50 gives industry credit exposure as the explicit ad hoc aggregation example alongside country. Principle 8 (¶57) requires single-name, country, and industry sector as components of credit risk reports. Without consistent sector classification, concentration risk by sector cannot be measured.
- **Risk types:** Credit / concentration
- **Criticality: 2.** Group aggregates are produced, but sector slices are unavailable or inconsistent across systems. Sector concentration risk cannot be measured, and the ¶50 ad hoc scenario cannot be executed. The aggregate is produced but cannot be correctly partitioned by sector.

  *Note on Principle 8:* Principle 8 also drives this element (¶57 names industry sector as a required report dimension), but Principle 8's report-content obligations — what reports must contain, their depth and scope — are outside the scope of a data catalog. The CDE captures only the data element; whether a report actually presents it correctly is a reporting governance matter addressed in Section 4.

- **Driven by:** Principle 4 (heading) — *"Data should be available by … industry"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk."*
- **Search terms:** industry code, sector code, industry classification, GICS, NACE, SIC, counterparty sector, obligor industry, industry segment, economic sector
- **Data quality requirements:**
  - *completeness* — Every counterparty record and every material exposure record carries a populated industry/sector classification | count of counterparty or exposure records with null or missing sector code | threshold: zero for material exposures — ¶43 requires materially complete data; the risk framework owner defines materiality | **(¶43)**
  - *validity* — Every sector code resolves to an entry in the bank's approved sector taxonomy | count of sector codes not present in the approved taxonomy | threshold: zero — an unresolvable code cannot be included in any sector aggregate | **(¶40)**
  - *consistency* — The same sector classification standard is applied to the same counterparty across all systems | count of counterparties where sector classification differs between risk and CRM systems | threshold: zero — inconsistent classification produces a counterparty whose exposure is split across different sector aggregates | **(¶33)**

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The date as of which an exposure or position is measured and reported — the snapshot date that anchors the risk figure in time. Every aggregate is stated as of a specific date; this element is what makes that statement meaningful and comparable across systems.
- **Why critical:** Every aggregated risk figure is a point-in-time measure. Without a consistent and correctly populated as-of date, aggregates from different systems may be combining positions measured at different times, producing a hybrid figure that corresponds to no actual risk state. The ¶50 scenario explicitly requires aggregation *"as of a specified date"* — the date is the query parameter.
- **Risk types:** Cross-cutting
- **Criticality: 3.** Without a correctly and consistently populated position date, the aggregated figure cannot be computed for a specified date: records from different source systems with different as-of dates cannot be combined into a single coherent point-in-time aggregate. The figure does not correspond to any actual risk state and is therefore invalid.
- **Driven by:** Principle 5 (¶44–47) — timeliness requirements presuppose that each record is stamped with its reference date; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date."*
- **Search terms:** position date, as-of date, valuation date, reference date, reporting date, snapshot date, risk date, trade date vs. settlement date, effective date
- **Data quality requirements:**
  - *completeness* — Every exposure and position record carries a populated as-of date | count of records with null or missing as-of date | threshold: zero — a record without a date cannot be assigned to any reporting period | **(¶43)**
  - *consistency* — For any given aggregation run, all source systems contributing to the aggregate use the same as-of date, or differences are explicitly documented and reconciled | count of aggregation runs where source systems contributed records with different as-of dates without documented reconciliation | threshold: zero undocumented date mismatches — silent date differences produce an aggregate that mixes positions from different time points | **(¶36(c))**
  - *timeliness* — For each risk type, exposure records are available in the risk aggregation system by the deadline defined for that risk type (faster for market and liquidity risk; longer permissible for retail credit) | age of position records in the risk system relative to the defined cut-off for each risk type; count of records received after the required cut-off | threshold: set by the bank's risk framework for each risk type, reflecting ¶45–46's differentiation by risk type and stress versus normal conditions | **(¶44–47)**

---

**CDE-09 — General Ledger / System-of-Record Reconciliation Key**

- **Definition:** The identifier that links a risk data record to the corresponding record in the general ledger or in the authoritative source system of record (e.g., a trade ID, a loan account number, or a GL reference that is shared between the risk system and the accounting system). This is not a risk calculation element — it is the audit trail that allows a risk figure to be traced back to its financial accounting basis.
- **Why critical:** ¶36(c) directly mandates reconciliation of risk data to accounting data. Without a common key, reconciliation is impossible — the bank cannot evidence that its risk figures are accurate, because there is no mechanism to check them against the system of record. An unverifiable risk figure is not a compliant one, regardless of whether it happens to be correct. This is the structural enabler of Principle 3's accuracy requirement.
- **Risk types:** Cross-cutting
- **Criticality: 3.** Without this element, the aggregate risk figure cannot be reconciled to the system of record at all, because there is no key on which to join the risk record to the GL or source system record. ¶36(c) treats reconciliation as a requirement, not an option — a figure that cannot be reconciled cannot be evidenced as accurate, which is an equivalent compliance failure to the figure being wrong.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** trade ID, loan ID, account number, GL reference, transaction reference, instrument ID, deal ID, source system reference, reconciliation key, system of record ID, booking reference, CUSIP/ISIN (for securities positions)
- **Data quality requirements:**
  - *completeness* — Every risk data record carries a populated reconciliation key | count of risk records with null or missing reconciliation key | threshold: zero — a record without a reconciliation key cannot be verified against the GL and is therefore unauditable | **(¶36(c))**
  - *validity* — Every reconciliation key in the risk system resolves to a record in the GL or source system of record | count of risk records whose reconciliation key does not match any record in the GL or source system | threshold: zero — an unresolved key means the position cannot be reconciled; materiality does not apply here because the failure is not about the size of the difference but the absence of an audit trail | **(¶36(c), ¶40)**
  - *accuracy* — For reconciled records, the exposure amount in the risk system agrees with the corresponding balance in the GL within materiality | sum of absolute differences between matched risk records and GL records; count of records outside the materiality threshold | threshold: set by materiality per ¶56; the finance and risk framework owners define and document the materiality threshold jointly | **(¶36(c), ¶56)**

---

**CDE-10 — Source System Identifier / Manual Override Flag**

- **Definition:** A label or set of labels that identifies (a) the system from which a risk data record originated, and (b) whether the record was produced by an automated process or introduced or modified manually — including end-user computing (EUC) inputs such as spreadsheets. This is a provenance element, not a risk measure.
- **Why critical:** ¶36(b) and ¶39 require documentation and explanation of manual processes and EUC inputs. Without this element, the bank cannot identify which risk data has been touched by manual intervention, cannot apply the additional controls required for EUC-originated data, and cannot evidence to supervisors the degree of automation in its risk data aggregation. It is also required for lineage: tracing a risk figure to its source system is a prerequisite for any meaningful reconciliation or audit.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Risk aggregates are produced, but the bank cannot distinguish automated from manually entered or overridden data, cannot apply differential controls to EUC-sourced records, and cannot evidence compliance with ¶36(b) and ¶39. Supervisory review of the automation profile of risk data is blocked. The aggregate is produced but its provenance cannot be demonstrated.
- **Driven by:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications … it should have effective mitigants in place"*; Principle 3 (¶36(d)) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (¶39) — *"banks to document and explain all of their risk data aggregation processes whether automated or manual."*
- **Search terms:** source system, data source, originating system, system of origin, manual override, EUC flag, end-user computing flag, manual input indicator, spreadsheet flag, data lineage, data provenance, golden source flag, authoritative source indicator
- **Data quality requirements:**
  - *completeness* — Every risk data record carries a populated source system identifier | count of risk records with null or missing source system identifier | threshold: zero — a record without a source identifier cannot be traced to its origin or subjected to source-appropriate controls | **(¶39)**
  - *validity* — Every source system identifier resolves to an entry in the bank's approved inventory of risk data sources | count of records with source identifiers not present in the approved source inventory | threshold: zero — an unrecognised source cannot be assessed for its control framework | **(¶40)**
  - *accuracy* — The manual/EUC flag correctly identifies all records that originated from or were modified by a manual or EUC process | periodic reconciliation of manual override flags against the EUC inventory and change logs; count of records modified outside automated systems without a corresponding manual flag | threshold: zero unflagged manual interventions — an undetected manual input bypasses the controls required by ¶36(b) and cannot be explained per ¶39 | **(¶36(b), ¶39)**

---

**CDE-11 — Net Exposure / Credit Risk Mitigant Amount**

- **Definition:** The value of collateral, guarantees, netting agreements, or other credit risk mitigants that reduce the gross exposure to a net figure. Captured as either the mitigant value (to be subtracted from gross) or the resulting net exposure amount. Covers both financial collateral and credit derivatives used as protection.
- **Why critical:** Risk reports present both gross and net exposures. Limit monitoring and capital calculation are conducted on net exposures. An incorrect or missing mitigant amount means the net exposure figure is wrong — the bank may appear to be within limits when it is not. Principle 8 (¶58) requires reports to include limits context, which presupposes accurate net figures.
- **Risk types:** Credit / counterparty credit / concentration
- **Criticality: 2.** The gross exposure aggregate is computed correctly (CDE-03), but net exposure figures used for limit monitoring and capital adequacy reporting are wrong if mitigant values are incorrect or missing. The aggregate is produced but the net risk figure cannot be trusted, and limit breach detection is unreliable.
- **Driven by:** Principle 3 (¶36(a)) — accuracy controls apply to all risk data; Principle 8 (¶58) — *"Reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance."*
- **Search terms:** collateral value, eligible collateral, netting amount, net exposure, credit risk mitigation, CRM, guarantee value, credit derivative protection, haircut, LGD input, collateral haircut, pledged assets
- **Data quality requirements:**
  - *accuracy* — Collateral and mitigant values reflect current market values or book values per the bank's valuation policy, and agree with the collateral management system within materiality | sum of differences between risk system mitigant values and collateral management system values; count of records outside materiality | threshold: set by materiality per ¶56; the risk and treasury framework owners define the materiality threshold | **(¶36(a), ¶56)**
  - *completeness* — All recognised netting agreements and collateral arrangements are captured in the risk data; no material credit risk mitigant is absent | count of counterparties with known netting agreements in the legal documentation system that have no corresponding netting flag in the risk data | threshold: zero material omissions — a missing netting agreement inflates net exposure and may cause a spurious limit breach | **(¶43)**
  - *timeliness* — Collateral values are updated at the frequency required by the risk type and the bank's margin/collateral framework (intraday for derivatives, daily for secured lending) | age of collateral value records relative to the required update frequency; count of records not updated within the required window | threshold: set by the bank's collateral management policy; market risk collateral should be updated at the speed required by ¶45–46 for counterparty credit risk | **(¶44–47)**

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Risk-to-Finance Reconciliation: Counterparty Exposure Totals vs. General Ledger**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key)
- **Rule intent:** The total of all gross exposure amounts in the risk aggregation system, grouped by counterparty and legal entity, must be reconcilable to the corresponding balances in the general ledger. This is not a check on any individual element — it is a check that the risk data population as a whole is consistent with the accounting record. A bank that cannot demonstrate this reconciliation cannot evidence the accuracy of its aggregated risk figures, regardless of the quality of individual records.
- **Measurement:** For each reporting period, compute the difference between (a) the sum of gross exposure amounts in the risk system by booking entity and risk type, and (b) the corresponding account balances in the general ledger after mapping risk categories to GL accounts. Report the number and value of line items where the difference exceeds the materiality threshold, and the proportion of total exposure that is unreconciled.
- **Threshold:** Set by materiality per ¶56 — the bank's finance and risk owners jointly define the threshold below which a difference is not considered to influence risk decisions. The rationale must be documented. Zero tolerance applies to the existence of records with no GL match at all (i.e., CDE-09 is null or unresolved), because those records cannot be reconciled by any amount of tolerance.
- **Paragraph authorisation:** ¶36(c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; ¶53(a) — *"Defined requirements and processes to reconcile reports to risk data."*

---

**XDQ-02 — Cross-System Counterparty Resolution: Single Counterparty View Across Sources**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-04 (Risk Type Classification), CDE-05 (Business Line), CDE-06 (Geography), CDE-07 (Industry/Sector)
- **Rule intent:** A single counterparty may appear under different identifiers, names, or reference codes in different source systems (front office, credit risk, market risk, GL). The requirement is that all representations of the same counterparty across all systems resolve to a single authoritative counterparty identifier before aggregation. Without this, the aggregated exposure to a single counterparty is split across multiple records, none of which alone represents the true total — a failure BCBS 239 was specifically written to prevent.
- **Measurement:** Count of counterparties where the same legal entity (identified by LEI or other external identifier) appears under two or more distinct internal identifiers across contributing source systems. Count of exposure records linked to a counterparty identifier that has no mapping to the bank's golden-source counterparty master. Report the total exposure value associated with unresolved or duplicated counterparty identifiers.
- **Threshold:** Zero — any unresolved duplicate means the aggregated exposure to that counterparty is wrong. There is no materiality tolerance for identifier integrity: a ¥1 exposure to an unresolved counterparty is a structural failure, not a rounding difference, because the mechanism that produces wrong aggregates is present regardless of the amount.
- **Paragraph authorisation:** ¶33 — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; ¶36(d) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; ¶40 — mandate to measure and monitor accuracy.

---

**XDQ-03 — EUC / Manual Input Population Integrity**

- **CDEs spanned:** CDE-10 (Source System Identifier / Manual Override Flag), CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key)
- **Rule intent:** The bank must be able to identify, at any point in time, the total value of risk positions that derive from manual or EUC inputs, and confirm that all such positions have been subject to the compensating controls required by ¶36(b). This is a population-level check: it establishes what proportion of the risk data is automated versus manual, and ensures that no manual input has entered the risk aggregation system without being flagged. It cannot be assessed by looking at any single record.
- **Measurement:** Compute the proportion of total exposure value in the risk system attributable to records flagged as manually entered or EUC-sourced. Compare against the bank's stated target for automation. For the manual/EUC population, count the records where the required compensating controls (dual approval, independent validation, reconciliation to source) are documented as having been applied. Count of records where the source system identifier indicates automated origin but the record has been modified outside the automated pipeline without a manual override flag.
- **Threshold:** No numeric threshold for the proportion of manual data — ¶36(b) does not mandate a specific automation level, only that effective mitigants are in place where manual processes are used. The threshold for *unflagged* manual modifications is zero — any undetected manual intervention bypasses controls. The bank's senior management establishes the target automation rate and documents it per ¶39's documentation requirement.
- **Paragraph authorisation:** ¶36(b) — *"Where a bank relies on manual processes and desktop applications … it should have effective mitigants in place"*; ¶39 — *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*; ¶40 — mandate to measure and monitor.

---

## 4. Out of Scope

The following principles impose obligations that a data catalog and data quality monitoring program cannot satisfy, regardless of how thoroughly the catalog is built. Stating this plainly is what makes the rest of this analysis trustworthy — a catalog that claimed to address these would be overstating its own capabilities.

---

**Principle 1 — Governance (¶27–31): Board and senior management accountability**

The catalog can document data ownership, stewardship assignments, and governance policies (¶34 specifically mandates ownership roles). What it cannot do is constitute the governance framework itself, ensure that the board has reviewed and approved the risk data aggregation framework (¶28), or ensure that senior management understands aggregation limitations (¶30). These are organisational governance obligations — they require board minutes, terms of reference, attestation processes, and management information reporting. A catalog entry naming a data owner is supporting evidence of governance; it is not governance.

---

**Principle 2 — Data Architecture (¶32–35): IT infrastructure and business continuity**

CDE-01 and CDE-02 are directly driven by ¶33's requirement for single identifiers and integrated taxonomies. The catalog supports these elements. What the catalog cannot address is the underlying IT infrastructure design (¶32, ¶35) — whether systems are integrated, whether a single authoritative source exists per risk type (¶36(d)), and whether risk data aggregation capabilities survive a stress event or business continuity scenario (¶32). These require IT architecture decisions, system integration work, and BCP testing. The catalog documents the result; it does not build the infrastructure.

---

**Principle 6 — Adaptability (¶48–51): Flexible aggregation on demand**

The catalog can ensure that the dimensions required for ad hoc aggregation (business line, geography, sector — CDEs 05, 06, 07) are present and populated. Whether the bank can actually execute the ¶50 scenario — aggregate country credit exposures as of a specified date, on demand, quickly — depends on the query capabilities of the risk aggregation system, not on the catalog. Metadata management does not substitute for technical aggregation capability. The catalog is a prerequisite; it is not sufficient.

---

**Principle 7 — Report Accuracy (¶52–56): Reconciliation and validation of reports**

CDE-09 and XDQ-01 directly address ¶36(c)'s data reconciliation requirement. What remains outside scope is ¶53's requirement for defined reconciliation processes between reports and risk data (¶53(a)), automated edit and reasonableness checks with an inventory of validation rules (¶53(b)), and exception reporting procedures for data errors (¶53(c)). These are report production process controls — they require workflow, exception management systems, and validation rule inventories in the reporting layer. The catalog can host a reference list of validation rules as metadata, but it cannot execute them against reports or manage exceptions.

---

**Principle 8 — Comprehensiveness (¶57–60): Report content and coverage**

CDE-04, CDE-05, CDE-06, and CDE-07 are driven partly by Principle 8 — specifically, ¶57 names industry sector as a required credit risk report dimension, which produces CDE-07. The split is this: the catalog governs whether the industry sector data element exists, is populated, and is consistent — the data prerequisite for a comprehensive report. Whether the report actually covers all material risk areas (¶57), includes limits context and emerging concentrations (¶58), provides forward-looking forecasts and stress test results (¶60), and is appropriately scaled to the bank's complexity (¶59) — none of this can be verified or enforced through metadata. These are report design and content obligations requiring human judgment about what constitutes comprehensive coverage for a given risk profile.

---

**Principle 9 — Clarity and Usefulness (¶61–69): Report comprehensibility and recipient appropriateness**

¶67 mandates an inventory and classification of risk data items with a reference to the concepts used in reports — this is the closest Principle 9 comes to a catalog requirement, and it supports the data dictionary obligation of ¶37. The rest of Principle 9 — ensuring reports are clear and concise (¶61), appropriately balanced between quantitative and qualitative content (¶62), tailored to the board versus senior management versus risk committees (¶63–66), and periodically confirmed as relevant with recipients (¶69) — is entirely a reporting design and communication governance matter. No data quality check can assess whether a risk report is useful to its recipient.

---

**Principle 10 — Frequency (¶70–71): Report production and distribution timing**

The timeliness requirements for underlying data (CDE-08, DQ dimension *timeliness*) are within scope and are addressed above. What is outside scope is the board and senior management's obligation to set report frequency requirements (¶70), routinely test the bank's ability to produce reports within those timeframes (¶70), and ensure intraday availability of critical reports during stress (¶71). These are reporting operations and governance obligations — they require scheduling systems, report distribution infrastructure, and tested production procedures.

---

**Principle 11 — Distribution (¶72–74): Report dissemination and confidentiality**

The catalog can document data classification levels (confidential, restricted, public) as metadata attributes, which supports the confidentiality requirement of ¶72. Whether reports are actually distributed to the right recipients in a timely way (¶72), and whether the bank periodically confirms that recipients receive timely reports (¶73), are access management, distribution workflow, and governance confirmation obligations. These require entitlement management systems, distribution logs, and periodic attestation processes — not metadata.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|-----|------|-------------|------------|---------------|
| CDE-01 | Counterparty Identifier | 3 | 2 (¶33), 4 (¶41, ¶46) | Uniqueness, Validity, Consistency |
| CDE-02 | Legal Entity Identifier (Own Entity) | 3 | 2 (¶33), 4 (heading, ¶41) | Uniqueness, Completeness, Validity |
| CDE-03 | Gross Exposure Amount | 3 | 3 (¶36(a)), 4 (¶41), 5 (¶46) | Accuracy, Completeness, Validity |
| CDE-04 | Risk Type Classification | 2 | 4 (heading, ¶41), 8 (¶57) | Validity, Consistency, Completeness |
| CDE-05 | Business Line | 2 | 4 (heading), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country | 2 | 4 (heading), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-07 | Industry / Sector Classification | 2 | 4 (heading), 6 (¶50), 8 (¶57) | Completeness, Validity, Consistency |
| CDE-08 | Position / As-Of Date | 3 | 5 (¶44–47), 6 (¶50) | Completeness, Consistency, Timeliness |
| CDE-09 | GL / System-of-Record Reconciliation Key | 3 | 3 (¶36(c)), 7 (¶53(a)) | Completeness, Validity, Accuracy |
| CDE-10 | Source System Identifier / Manual Override Flag | 2 | 3 (¶36(b), ¶36(d), ¶39) | Completeness, Validity, Accuracy |
| CDE-11 | Net Exposure / Credit Risk Mitigant Amount | 2 | 3 (¶36(a)), 8 (¶58) | Accuracy, Completeness, Timeliness |

**Cross-cutting requirements:**

| ID | Description | CDEs Spanned | Principles |
|----|-------------|--------------|------------|
| XDQ-01 | Risk-to-Finance reconciliation: exposure totals vs. GL | CDE-01, CDE-03, CDE-09 | ¶36(c), ¶53(a) |
| XDQ-02 | Cross-system counterparty resolution: single counterparty view | CDE-01, CDE-04, CDE-05, CDE-06, CDE-07 | ¶33, ¶36(d), ¶40 |
| XDQ-03 | EUC/manual input population integrity | CDE-10, CDE-03, CDE-09 | ¶36(b), ¶39, ¶40 |

**Criticality distribution:** 5 elements at criticality 3 (CDE-01, CDE-02, CDE-03, CDE-08, CDE-09); 6 elements at criticality 2 (CDE-04, CDE-05, CDE-06, CDE-07, CDE-10, CDE-11); 0 elements at criticality 1. No element has been assigned to criticality 1 because every element in this register either makes an aggregate invalid if absent (3) or prevents a required slice or control from functioning (2). If the register were extended to include purely descriptive attributes such as counterparty legal name or instrument description, those would be candidates for criticality 1 — but they do not meet the CDE inclusion criteria and are therefore absent rather than rated 1.