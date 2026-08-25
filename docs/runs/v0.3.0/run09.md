# BCBS 239 — Data Catalog Governance Interpretation

---

## 1. Objectives and scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a precondition for sound governance.** The regulation requires that a bank can produce accurate, complete and timely aggregated risk data to support board and senior management decision-making — not merely as an IT capability but as a governance obligation. (¶28: *"A bank's board and senior management should review and approve the bank's group risk data aggregation and risk reporting framework and ensure that adequate resources are deployed."*)

- **Single, authoritative, reconcilable data.** Risk data must be traceable to a single authoritative source per risk type, reconciled to accounting records, and produced on a largely automated basis to minimise error. (¶36(c)–(d): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate… A bank should strive towards a single authoritative source for risk data per each type of risk."*)

- **Full-population completeness across the group.** Aggregation must capture all material exposures — including off-balance-sheet — sliceable by business line, legal entity, asset type, industry, and region. (¶41: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*)

- **A common data dictionary and integrated taxonomy.** Concepts must be defined consistently across the organisation, with unified naming conventions and single identifiers for legal entities, counterparties and accounts. (¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*; ¶37: *"A bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation."*)

- **Documented lineage and controlled manual intervention.** All aggregation processes, automated or manual, must be documented; manual workarounds must be explained and their criticality to accuracy assessed. (¶39: *"Documentation should include an explanation of the appropriateness of any manual workarounds, a description of their criticality to the accuracy of risk data aggregation and proposed actions to reduce the impact."*)

- **Timeliness under stress.** Systems must be capable of producing aggregated risk data rapidly during stress and crisis, across all critical risk types. (¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*)

**Who it applies to**

Principles 1–11 apply directly to Global Systemically Important Banks (G-SIBs), with the Basel Committee expecting adoption by Domestic Systemically Important Banks (D-SIBs) and, over time, other large internationally active banks. The obligations fall on the bank as an institution — board, senior management, risk and IT functions jointly — not on any single team.

---

## 2. Critical Data Element candidates

---

**CDE-01 — Counterparty Identifier**
- **Definition:** The unique, enterprise-wide identifier assigned to each legal-entity counterparty — borrower, derivatives counterparty, issuer, or guarantor — that is recognised consistently across all risk systems, the general ledger, and collateral systems. This is the logical anchor for any per-counterparty or cross-counterparty exposure aggregate.
- **Why critical:** Without a resolved, unique counterparty key, exposures recorded in different systems (loan origination, trading, collateral, derivatives) cannot be summed to a single counterparty view. Concentration risk, large-exposure limits, and counterparty credit risk (CCR) calculations are all structurally dependent on this key.
- **Risk types:** Credit, counterparty credit, concentration, cross-cutting
- **Criticality: 3.** Without a resolved counterparty identifier, the aggregate credit or CCR exposure to a single counterparty cannot be computed at all, because records in disparate systems cannot be joined into one view.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 5 (¶46(a)–(b)) — *"The aggregated credit exposure to a large corporate borrower… Counterparty credit risk exposures."*
- **Search terms:** counterparty ID, party ID, client ID, obligor ID, counterparty master, GFID, LEI, BIC, counterparty reference, entity identifier
- **Data quality requirements:**
  - *Uniqueness* — Each counterparty must have exactly one active enterprise identifier; no two distinct legal entities share it. | Count of duplicate active counterparty identifiers in the counterparty master. | Zero duplicates.
  - *Completeness* — Every exposure record carries a populated, non-null counterparty identifier. | Count of exposure records with null or missing counterparty identifier as a proportion of total exposure records. | < 0.1 %.
  - *Consistency* — The counterparty identifier resolves to the same legal entity name and LEI across all source systems. | Count of counterparty IDs where name or LEI differs between systems. | Zero cross-system mismatches for in-scope records.
  - *Validity* — Counterparty identifiers in exposure records match an active record in the authoritative counterparty master. | Count of exposure records whose counterparty identifier has no match in the master. | Zero unmatched identifiers in risk-aggregation runs.

---

**CDE-02 — Bank Legal Entity Identifier**
- **Definition:** The identifier that designates which legal entity within the banking group is the booking entity for a given exposure or position. Used to allocate exposures to subsidiaries, branches, and the parent for group consolidation, solo reporting, and cross-border data-sharing analysis.
- **Why critical:** Group-level aggregation requires that every exposure is attributed to exactly one booking entity; subsidiary-level reporting requires the same. Without this field, consolidation and the identification of cross-entity concentrations cannot be performed.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 3.** Without the booking-entity identifier, group-consolidated exposure figures cannot be computed at all, because there is no basis on which to determine which records belong to each legal entity in the consolidation perimeter.
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures"* (implying group-wide coverage).
- **Search terms:** legal entity ID, booking entity, entity code, subsidiary code, branch code, organisation unit, LEI, consolidation entity, reporting entity
- **Data quality requirements:**
  - *Completeness* — Every exposure and position record carries a populated booking-entity identifier. | Count of records with null booking-entity identifier. | Zero.
  - *Validity* — The booking-entity identifier resolves to an active entity in the group's legal entity master. | Count of records whose booking-entity code is absent from the legal entity master. | Zero.
  - *Consistency* — The same entity carries the same identifier across all risk systems and the general ledger. | Count of entity-name or LEI mismatches between the risk data and GL entity tables for the same entity code. | Zero.

---

**CDE-03 — Gross Exposure Amount**
- **Definition:** The monetary value of a bank's exposure to a counterparty, instrument, or portfolio before the application of credit risk mitigants (collateral, guarantees, netting). Expressed in the transaction currency and, separately, in a reporting currency equivalent. The foundational quantity from which all risk aggregates — regulatory capital, concentration limits, large-exposure returns — are derived.
- **Why critical:** This is the quantity being aggregated. If it is wrong, every downstream aggregate is wrong. It must be available for off-balance-sheet as well as on-balance-sheet positions.
- **Risk types:** Credit, counterparty credit, market, concentration
- **Criticality: 3.** Without a correct gross exposure amount, the aggregate risk exposure figure cannot be computed at all, because it is the addend in every summation.
- **Driven by:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data."*; Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*; Principle 7 (¶52) — *"Risk management reports should be accurate and precise."*
- **Search terms:** exposure at default, EAD, notional amount, outstanding balance, drawn amount, gross exposure, face value, mark-to-market, replacement cost, current exposure
- **Data quality requirements:**
  - *Accuracy* — Exposure amounts must agree to the position of record (trade system or GL) within defined tolerance. | Sum of absolute differences between risk system exposure and trade-system/GL position for matched records, as a proportion of total exposure. | Within materiality threshold set per ¶56.
  - *Completeness* — Every in-scope exposure record carries a non-null, non-zero exposure amount unless the position is genuinely zero and that is evidenced. | Count of in-scope exposure records with null or blank exposure amount. | Zero.
  - *Timeliness* — Exposure amounts reflect the as-of date of the aggregate run within the latency tolerance set for that risk type. | Age (in business hours) of the most recently loaded exposure amount at aggregation run time, by risk type. | Within SLA per ¶44–45.

---

**CDE-04 — Risk Type Classification**
- **Definition:** The categorical label that assigns an exposure or position to a risk type — at minimum: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk. This is the primary partition used to route records to the correct aggregation engine, capital model, and report section.
- **Why critical:** Principle 8 requires reports to cover all significant risk areas by type. If an exposure is classified to the wrong risk type, it will appear in an incorrect aggregate and be absent from the correct one, distorting both. The classification also governs which capital treatment, limit framework, and stress scenario is applied.
- **Risk types:** Cross-cutting
- **Criticality: 2.** An aggregate for a given risk type can be computed, but it will include exposures that belong elsewhere and exclude those that have been misclassified — the aggregate is produced but cannot be trusted in part.
- **Driven by:** Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*; Principle 4 (¶42) — *"each system should make clear the specific approach used to aggregate exposures for any given risk measure."*
- **Search terms:** risk type, risk category, risk class, asset class, risk flag, product risk classification, risk dimension
- **Data quality requirements:**
  - *Validity* — Every exposure record carries a risk-type classification drawn from the approved controlled vocabulary. | Count of records with a risk-type value absent from the approved reference list. | Zero.
  - *Completeness* — Every in-scope exposure record has a populated risk-type classification. | Count of records with null or blank risk-type. | Zero.
  - *Consistency* — Records that appear in both a risk system and the GL carry the same risk-type classification. | Count of matched records where risk-type classification differs between systems. | Zero for material exposures.

---

**CDE-05 — Business Line**
- **Definition:** The internal business unit or segment — retail banking, corporate banking, trading, treasury, etc. — to which an exposure is attributed. One of the explicit aggregation dimensions named by the regulation; also used for P&L attribution and capital allocation.
- **Why critical:** Principle 4 requires risk data to be available by business line. Without a correct business-line assignment, slice-and-dice queries and business-line risk reports cannot be produced. Concentration risk across a business line is also undetectable.
- **Risk types:** Credit, market, liquidity, operational, cross-cutting
- **Criticality: 2.** Aggregate exposures can be computed at the group level, but the business-line slice cannot be produced or reconciled — Principle 4's completeness requirement for this dimension is unmet.
- **Driven by:** Principle 4 (¶41, header) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings."*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures… across all business lines and geographic areas."*
- **Search terms:** business line, business unit, segment, division, LOB, cost centre, profit centre, desk, trading desk
- **Data quality requirements:**
  - *Completeness* — Every exposure record carries a populated business-line code. | Count of records with null business-line. | Zero.
  - *Validity* — Business-line codes resolve to the current approved hierarchy. | Count of records with a business-line code absent from the approved organisational hierarchy. | Zero.
  - *Consistency* — Business-line assignment for a given booking agrees between the risk system and the GL. | Count of matched records with differing business-line codes. | < 0.5 % by count.

---

**CDE-06 — Geography / Country**
- **Definition:** The country or regulatory jurisdiction to which an exposure is attributed — typically counterparty country of domicile, country of risk, or booking location, with the specific definition documented in the data dictionary. One of the explicit slicing dimensions named in Principles 4 and 6.
- **Why critical:** Cross-border concentration risk and sovereign risk cannot be assessed without a reliable country attribution. Principle 6 explicitly cites the ability to aggregate country credit exposures on demand as a test case.
- **Risk types:** Credit, market, liquidity, concentration
- **Criticality: 2.** Group-level aggregates can be produced, but country-level slices are incorrect or incomplete — the Principle 4 and 6 requirements for geographic aggregation cannot be satisfied.
- **Driven by:** Principle 4 (¶41, header) — *"Data should be available by… region."*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
- **Search terms:** country code, country of risk, country of domicile, jurisdiction, geography, region, ISO country code, booking location country
- **Data quality requirements:**
  - *Validity* — Country codes conform to an approved standard (e.g. ISO 3166-1 alpha-2). | Count of records with country codes not in the approved reference list. | Zero.
  - *Completeness* — Every credit and market risk exposure record carries a country attribution. | Count of in-scope records with null or blank country code. | Zero.
  - *Accuracy* — Country of risk is reviewed and updated when a counterparty's domicile or economic risk changes. | Age (in days) since last review of country-of-risk assignments against known migration events. | Reviewed at least quarterly, or within 5 business days of a material sovereign event.

---

**CDE-07 — Industry / Sector Classification**
- **Definition:** The industry or economic sector to which a counterparty or obligor belongs, assigned using an approved classification scheme (NACE, GICS, SIC, or an internal equivalent). Used for sector concentration analysis, stress testing, and comprehensiveness of credit risk reports.
- **Why critical:** Principle 8 cites industry sector as a required component of credit risk reporting. Sector concentration cannot be identified or reported without a populated, consistent sector code.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Credit risk aggregates at the group level are unaffected, but the industry-sector slice required by Principle 8 cannot be produced reliably — the report dimension degrades.
- **Driven by:** Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas… (eg single name, country and industry sector for credit risk)."*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas."*

> **Note on Principle 8:** While Principle 8 also imposes report-content obligations (forward-looking forecasts, stress test results, capital adequacy) that a data catalog cannot satisfy, it explicitly names industry sector as a data dimension. That dimension is addressable as a CDE. The reporting obligations themselves remain out of scope — see Section 4.

- **Search terms:** industry code, sector code, NACE code, GICS sector, SIC code, industry classification, counterparty sector, economic sector
- **Data quality requirements:**
  - *Completeness* — Every corporate and institutional credit exposure carries a populated industry/sector code. | Count of corporate/institutional credit records with null sector code as a proportion of total. | < 1 % by exposure value.
  - *Validity* — Sector codes are drawn from the single approved classification scheme documented in the data dictionary. | Count of records with sector codes not in the approved scheme. | Zero.
  - *Consistency* — The sector assigned in the risk system matches the sector recorded in the counterparty master. | Count of matched records with differing sector codes. | Zero for material obligors.

---

**CDE-08 — As-of / Position Date**
- **Definition:** The business date as of which an exposure or position is stated. Every aggregated risk figure is a snapshot at a specific point in time; this date is the temporal key that makes snapshots comparable, enables trend analysis, and ties a risk report to a specific reporting period.
- **Why critical:** Without a reliable as-of date, it is impossible to determine whether records in an aggregate belong to the same snapshot, making comparisons across periods and stress-scenario runs invalid. Principle 5's timeliness requirement — including intraday production — depends on this field being correctly and consistently populated.
- **Risk types:** Cross-cutting
- **Criticality: 3.** Without a correctly populated as-of date, the aggregate figure for a given reporting period cannot be computed at all, because records from different dates cannot be distinguished from those belonging to the target snapshot — the aggregate is temporally undefined.
- **Driven by:** Principle 5 (¶44) — *"A bank's risk data aggregation capabilities should ensure that it is able to produce aggregate risk information on a timely basis."*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date."*
- **Search terms:** as-of date, position date, reporting date, value date, trade date, snapshot date, reference date, effective date
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null as-of date. | Count of records with null as-of date. | Zero.
  - *Validity* — As-of dates are valid calendar dates and fall within expected reporting cycles; no future dates appear in closed snapshots. | Count of records with as-of dates outside the expected reporting window for a given batch run. | Zero.
  - *Timeliness* — The maximum lag between the as-of date and the date the record is available in the aggregation layer must be within the SLA for the risk type. | Distribution of (load date minus as-of date) in business hours, by risk type. | Within thresholds set per ¶45–46 for normal and stress modes.

---

**CDE-09 — GL / Source System Reconciliation Key**
- **Definition:** The identifier — trade reference, deal number, account number, or transaction ID — that links a risk record to its corresponding entry in the general ledger or system of record. This is the field that makes a reconciliation between risk data and finance data mechanically possible. Without it, ¶36(c) cannot be operationalised.
- **Why critical:** The regulation explicitly requires that risk data be reconciled to accounting data to evidence accuracy. If records in the risk layer cannot be matched to a GL entry, completeness and accuracy cannot be formally evidenced — risk data could silently diverge from the books of record. This element is the most commonly absent in practice and one of the most directly cited in the text.
- **Risk types:** Cross-cutting (all risk types that have accounting representation)
- **Criticality: 2.** Risk aggregates can be produced, but their accuracy relative to the books of record cannot be formally evidenced or reconciled — the Principle 3(c) control is broken, and regulatory reliance on the figures is undermined.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** deal ID, trade reference, transaction ID, account number, GL account, journal reference, source system key, booking reference, contract ID
- **Data quality requirements:**
  - *Completeness* — Every risk record that has a corresponding accounting entry carries a populated reconciliation key. | Count of risk records with no reconciliation key populated, where a GL entry is expected. | Zero for on-balance-sheet positions; tracked with explanation for off-balance-sheet.
  - *Validity* — Reconciliation keys in the risk layer match at least one active entry in the GL or system of record. | Count of risk records whose reconciliation key has no match in the GL or system of record. | Zero for material exposures; any exceptions logged and aged.
  - *Uniqueness* — Where a one-to-one relationship is defined, no reconciliation key maps to more than one risk record or GL entry. | Count of duplicate reconciliation keys within a single snapshot. | Zero in defined one-to-one contexts.

---

**CDE-10 — Source System / Provenance Flag**
- **Definition:** The identifier or attribute that designates the originating system (or process type) for a risk record — e.g. trade capture system, loan origination system, treasury system, or EUC/spreadsheet. Where the source is a manual or end-user-computing (EUC) process, this flag distinguishes those records from fully automated feeds and triggers enhanced controls.
- **Why critical:** The regulation requires that manual workarounds be documented, their criticality to accuracy assessed, and plans made to reduce reliance on them. Without knowing which records came from which system — and whether that system is automated or manual — the bank cannot apply differential controls, cannot document EUC dependency, and cannot demonstrate progress toward automation. This is the field that makes ¶36(b) and ¶39 auditable.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Aggregates can be computed, but the bank cannot distinguish manually sourced figures from automated ones — the differential control regime required by ¶36(b) and ¶39 cannot be applied, and any manual error embedded in the aggregate is undetectable.
- **Driven by:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications… it should have effective mitigants in place."*; Principle 3 (¶39) — *"Documentation should include an explanation of the appropriateness of any manual workarounds, a description of their criticality to the accuracy of risk data aggregation."*
- **Search terms:** source system, system of origin, data source, feed ID, source flag, EUC flag, manual override flag, upstream system, data lineage, pipeline name
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a populated source system identifier or provenance flag. | Count of records with null or blank source system identifier. | Zero.
  - *Validity* — Source system values are drawn from the approved source system registry. | Count of records whose source system identifier is absent from the registry. | Zero.
  - *Accuracy* — Records flagged as EUC or manual must correspond to entries in the EUC inventory maintained under ¶36(b) policy. | Count of EUC-flagged records whose source system is not listed in the EUC control inventory. | Zero; any new EUC sources trigger an inventory update within one business cycle.

---

**CDE-11 — Collateral / Credit Risk Mitigant Value**
- **Definition:** The monetary value of eligible collateral or other credit risk mitigants (guarantees, credit derivatives) assigned to an exposure, used to compute net exposure for regulatory capital and large-exposure calculations. Expressed in the transaction or reporting currency.
- **Why critical:** Net exposure — the figure that appears in capital adequacy and concentration reports — is gross exposure minus eligible mitigants. If mitigant values are wrong or absent, net exposure and regulatory capital figures are wrong. Principle 8 requires reports to include capital-related measures; those measures depend on this field.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 2.** Gross exposure aggregates can be produced, but net exposure and capital-related report figures — explicitly required by ¶57–59 — cannot be correctly computed when mitigant values are absent or inaccurate. The capital adequacy slice of the report degrades.
- **Driven by:** Principle 8 (¶57–59) — *"Risk management reports should also cover risk-related measures (eg regulatory and economic capital)."*; Principle 4 (¶41) — implicitly, as collateral is part of the complete picture of a material risk exposure.
- **Search terms:** collateral value, eligible collateral, LGD mitigant, CRM value, guarantee amount, haircut, net exposure, collateral haircut, netting agreement, credit protection
- **Data quality requirements:**
  - *Accuracy* — Collateral values are revalued at the frequency required by the collateral agreement and internal policy. | Age (in business days) of collateral valuation at aggregation run time, by collateral type. | Within policy-defined revaluation frequency; exceptions flagged.
  - *Completeness* — Every exposure that is contractually secured carries a collateral record with a current value. | Count of secured exposure records with null or zero collateral value, where a collateral agreement is on file. | Zero.
  - *Validity* — Collateral type codes are drawn from the approved collateral taxonomy. | Count of records with collateral type codes absent from the approved list. | Zero.

---

## 3. Cross-cutting data quality requirements

---

**XDQ-01 — Group-wide Counterparty Exposure Reconciliation**
- **Spans:** CDE-01 (Counterparty Identifier), CDE-02 (Bank Legal Entity Identifier), CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key)
- **What it requires:** The total aggregated exposure to each counterparty, summed across all booking entities and risk systems using the enterprise counterparty identifier, must be reconciled to the corresponding balance in the general ledger (or the system of record where GL booking does not apply). Discrepancies must be identified, quantified, aged, and explained. This cannot be expressed as a single-element rule because it requires joining records across systems using CDE-01 and CDE-02, summing CDE-03, and matching to GL entries via CDE-09.
- **Driven by:** ¶36(a) — *"Controls surrounding risk data should be as robust as those applicable to accounting data."*; ¶36(c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate."*; ¶53(a) — *"Defined requirements and processes to reconcile reports to risk data."*
- **Dimension:** Accuracy; Completeness
- **Rule intent:** The sum of risk-system gross exposures per counterparty, aggregated across all legal entities, must agree to the corresponding GL balance within a defined materiality tolerance. Any unreconciled difference must be logged, explained, and resolved within the agreed SLA.
- **Measurement:** (a) Count and value of counterparty exposure aggregates where risk-system total and GL balance differ by more than the materiality threshold; (b) Age distribution (in business days) of open reconciliation breaks. 
- **Suggested threshold:** Zero breaks above materiality; all breaks below materiality documented; no break unresolved beyond 5 business days for material counterparties.

---

**XDQ-02 — Cross-system Counterparty Identity Resolution**
- **Spans:** CDE-01 (Counterparty Identifier), CDE-04 (Risk Type Classification), CDE-05 (Business Line), CDE-07 (Industry/Sector Classification)
- **What it requires:** A single real-world counterparty may be represented by different local identifiers in the loan origination system, the trading system, and the derivatives system. The enterprise counterparty master must contain a mapping that resolves all system-local representations to a single enterprise counterparty identifier. Without this, aggregating credit exposure across risk types (CDE-04) and business lines (CDE-05) for the same counterparty is structurally impossible. This is a data architecture obligation under ¶33 that no per-element DQ rule can enforce — it requires a managed golden-record or party-resolution process.
- **Driven by:** ¶33 — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts."*; ¶37 — *"data is defined consistently across an organisation."*
- **Dimension:** Uniqueness; Consistency
- **Rule intent:** For every counterparty that has exposures recorded under more than one system-local identifier, a mapping to a single enterprise identifier must exist in the counterparty master. No exposure record should be orphaned — i.e. carry a system-local identifier with no resolution path to an enterprise identifier.
- **Measurement:** (a) Count of distinct system-local counterparty identifiers with no mapping to an enterprise identifier, weighted by associated exposure value; (b) Count of enterprise counterparty records with duplicate or conflicting mappings from the same source system.
- **Suggested threshold:** Zero orphaned system-local identifiers for counterparties above the materiality threshold; any gap in the mapping triggers a remediation ticket within 2 business days of detection.

---

**XDQ-03 — EUC and Manual-Source Completeness and Control Coverage**
- **Spans:** CDE-10 (Source System / Provenance Flag), CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key)
- **What it requires:** All records flagged as originating from EUC or manual processes must be (a) listed in the EUC control inventory, (b) subject to a documented compensating control, and (c) traceable to a GL or system-of-record entry via CDE-09. This cross-cutting requirement exists because the regulation does not simply require that EUC records be identified — it requires that their risk to accuracy be assessed and mitigated (¶36(b), ¶39). That assessment requires combining provenance flags (CDE-10) with exposure values (CDE-03) and reconciliation coverage (CDE-09). No single-element monitor captures this.
- **Driven by:** ¶36(b) — *"Where a bank relies on manual processes and desktop applications… it should have effective mitigants in place."*; ¶39 — *"Documentation should include an explanation of the appropriateness of any manual workarounds, a description of their criticality to the accuracy of risk data aggregation."*
- **Dimension:** Accuracy; Completeness; Validity
- **Rule intent:** The proportion of total risk exposure attributable to EUC or manual sources must be measured and reported; every EUC source must have a compensating control on record; no EUC-sourced record above the materiality threshold may be unreconciled to a system-of-record entry.
- **Measurement:** (a) EUC/manual exposure as a percentage of total risk exposure, by risk type; (b) Count of EUC sources in the provenance registry with no documented compensating control; (c) Count of EUC-flagged records above materiality with no reconciliation key match.
- **Suggested threshold:** (a) Tracked and trended — no absolute cap, but increases must be explained; (b) Zero undocumented EUC sources; (c) Zero unreconciled material EUC records.

---

## 4. Out of scope

The following principles impose obligations that a data catalog, a CDE register, and data quality monitoring cannot satisfy. Stating this clearly is essential — a governance program that conflates data management with reporting and board governance will leave supervisory expectations unmet in ways that are not visible until an examination.

---

**Principle 1 — Governance (¶27–31): Board and senior management accountability**

The catalog can hold data ownership records, stewardship assignments, and governance documentation, which supports Principle 1's requirement for documented ownership (¶34). However, the core obligations of Principle 1 — that the board and senior management approve the aggregation and reporting framework (¶28), that senior management understands the limitations of data coverage (¶30), that independent validation is conducted (¶29(a)) — are institutional governance acts. They require board minutes, terms of reference, validation reports, and executive attestation. No catalog feature substitutes for these.

---

**Principle 2 — Data Architecture (¶32–35): IT infrastructure and business continuity**

The catalog directly supports ¶33 (integrated data taxonomy, metadata, single identifiers) and ¶37 (data dictionary), and those requirements are reflected in CDE-01 through CDE-10. However, ¶32 requires business continuity planning and business impact analysis for risk data systems — that is a resilience engineering obligation. ¶34 requires that ownership and quality controls operate across the full data lifecycle and technology infrastructure. The catalog can record ownership and steward assignments; it cannot enforce controls in source systems, ETL pipelines, or compute environments.

---

**Principle 6 — Adaptability (¶48–51): Ad hoc query and stress scenario capability**

Principle 6 requires that the bank's systems can generate arbitrary subsets and aggregates on demand and under stress. A data catalog enables users to discover what data exists and where, which is a precondition for adaptability. However, the actual ability to execute ad hoc aggregations rapidly is a function of data warehouse and analytical platform architecture, not catalog governance. The catalog cannot deliver ¶49(a)–(d) on its own.

---

**Principle 7 — Report Accuracy (¶52–56): Reconciliation processes and edit checks**

Principle 7 partially drives data requirements — the reconciliation key (CDE-09) and gross exposure amount (CDE-03) are both grounded here. But ¶53(b) requires an inventory of validation rules applied to quantitative report figures, and ¶53(c) requires integrated exception-reporting procedures. These are operational reporting-layer controls — validation rule engines, exception workflows, report sign-off processes — not catalog metadata. The CDE register addresses the data inputs; it does not address the report-production controls.

---

**Principle 8 — Comprehensiveness (¶57–60): Report content and forward-looking information**

Principle 8 drives two CDEs: industry/sector (CDE-07) and, indirectly, the requirement to cover all risk types (CDE-04). Those data dimensions are addressable. However, ¶57–60 also require that reports cover capital adequacy, liquidity ratios, stress test results, inter-risk concentrations, and forward-looking forecasts. These are report-content obligations — they govern what a risk report must contain and present to the board, not what data must be governed. A catalog that holds well-governed CDEs enables these reports to be produced accurately but does not ensure they are produced, reviewed, or actioned. The distinction matters: if a bank governs all twelve CDEs in this register but fails to include stress test projections in its board reports, it is still non-compliant with Principle 8.

---

**Principles 9, 10, and 11 — Clarity, Frequency and Distribution (¶61–74)**

These principles govern reporting practice entirely:

- **Principle 9** requires that reports be clear, concise, and tailored to recipients (¶61–69). It includes a useful requirement at ¶67 — an inventory and classification of risk data items — which supports the catalog's data dictionary function. But the obligations around qualitative/quantitative balance (¶62), recipient-specific tailoring (¶63), and periodic confirmation with recipients (¶69) are governance and communication processes.

- **Principle 10** requires that report frequency be set by the board, tested routinely, and increased in stress (¶70–71). This is a report scheduling and SLA obligation. The as-of date (CDE-08) and timeliness DQ rules inform whether data is available in time to meet frequency targets, but cannot themselves set or enforce frequency policy.

- **Principle 11** requires confidential distribution to appropriate recipients (¶72–73). This is an information security and access-control obligation. The catalog can record data classifications and sensitivity labels, which supports access governance, but the distribution controls — entitlement management, secure delivery channels, distribution list maintenance — operate outside the catalog.

---

## 5. Summary table

| CDE | Name | Criticality | Principles | DQ dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | P2 (¶33), P5 (¶46) | Uniqueness, Completeness, Consistency, Validity |
| CDE-02 | Bank Legal Entity Identifier | 3 | P2 (¶33), P4 (¶41) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | P3 (¶36a), P4 (¶41), P7 (¶52) | Accuracy, Completeness, Timeliness |
| CDE-04 | Risk Type Classification | 2 | P8 (¶57), P4 (¶42) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | 2 | P4 (¶41 header), P6 (¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country | 2 | P4 (¶41 header), P6 (¶50) | Validity, Completeness, Accuracy |
| CDE-07 | Industry / Sector Classification | 2 | P8 (¶57), P6 (¶50) | Completeness, Validity, Consistency |
| CDE-08 | As-of / Position Date | 3 | P5 (¶44), P6 (¶50) | Completeness, Validity, Timeliness |
| CDE-09 | GL / Source System Reconciliation Key | 2 | P3 (¶36c), P7 (¶53a) | Completeness, Validity, Uniqueness |
| CDE-10 | Source System / Provenance Flag | 2 | P3 (¶36b), P3 (¶39) | Completeness, Validity, Accuracy |
| CDE-11 | Collateral / Credit Risk Mitigant Value | 2 | P8 (¶57–59), P4 (¶41) | Accuracy, Completeness, Validity |

**Cross-cutting DQ requirements**

| ID | Description | Spans | Dimensions |
|---|---|---|---|
| XDQ-01 | Group-wide counterparty exposure reconciliation to GL | CDE-01, 02, 03, 09 | Accuracy, Completeness |
| XDQ-02 | Cross-system counterparty identity resolution | CDE-01, 04, 05, 07 | Uniqueness, Consistency |
| XDQ-03 | EUC and manual-source control coverage and reconciliation | CDE-03, 09, 10 | Accuracy, Completeness, Validity |