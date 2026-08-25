# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a precondition for sound governance.** The bank must be able to produce accurate, complete and timely aggregated risk data not only in normal conditions but under stress, so that the board and senior management can make consequential decisions with confidence. ¶35: *"banks should develop and maintain strong risk data aggregation capabilities to ensure that risk management reports reflect the risks in a reliable way."*

- **A single, reconciled, authoritative data foundation.** Risk data must be traceable to its source, reconciled against accounting records, and derived from a single authoritative source per risk type, minimising manual error and ambiguity. ¶36(c–d): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate… A bank should strive towards a single authoritative source for risk data per each type of risk."*

- **Group-wide coverage across all material dimensions.** Aggregation must reach every legal entity, business line, asset type, industry and region, including off-balance-sheet exposures, so that concentrations and emerging risks are visible. ¶41: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*

- **Documented, validated and governed processes.** Aggregation and reporting processes must be fully documented, subject to independent validation, and supported by a common data dictionary that enforces consistent definitions across the organisation. ¶29(a): *"Fully documented and subject to high standards of validation… independent and review the bank's compliance with the Principles."* ¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation."*

- **Controlled use of manual processes.** Where automation is incomplete, manual workarounds and end-user-computing inputs must be documented, their criticality assessed, and mitigants applied. ¶39: *"banks to document and explain all of their risk data aggregation processes whether automated or manual… a description of their criticality to the accuracy of risk data aggregation."*

- **Adaptability to ad hoc and stress scenarios.** The aggregation architecture must support on-demand slicing across arbitrary combinations of dimensions—country, industry, business line—as of any specified date, without bespoke re-engineering. ¶50: *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries, as well as industry credit exposures… across all business lines and geographic areas."*

**Who it applies to**

Principles 1–11 apply directly to **Global Systemically Important Banks (G-SIBs)** and, by supervisory expectation, to **Domestic Systemically Important Banks (D-SIBs)**. Supervisors may extend application to other institutions. The obligations fall on the banking group as a whole, including subsidiaries and booking entities, not only at the consolidated head-office level.

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** The unique, persistent identifier assigned to each legal-entity counterparty across all systems of the banking group — the key that resolves a counterparty to a single record regardless of which booking system, product line or geography generated the exposure.
- **Why critical:** Without a single resolved counterparty key, it is impossible to sum all exposures to one borrower across business lines or legal entities. Every credit concentration and large-exposure calculation collapses. ¶33 mandates *"single identifiers and/or unified naming conventions for data including… counterparties."*
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3** — *Without this element, the aggregate credit exposure to counterparty X cannot be computed at all, because records from different source systems cannot be joined to the same obligor.*
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; also Principle 4 (¶41) and Principle 5 (¶46a–b)
- **Search terms:** customer ID, counterparty ID, obligor ID, client ID, LEI (Legal Entity Identifier), BIC, global party ID, golden record ID, party master
- **Data quality requirements:**
  - *Uniqueness* — Each counterparty maps to exactly one canonical identifier; no two distinct legal entities share the same key | Count of duplicate canonical identifiers in the party master | 0 duplicates
  - *Completeness* — Every exposure record carries a non-null, resolvable counterparty identifier | Count of exposure records with null or unmatched counterparty identifier | <0.1% of population
  - *Consistency* — The same counterparty identifier resolves to the same legal-entity name and LEI across all source systems | Count of identifier-to-name mismatches across system pairs | 0 mismatches for material counterparties

---

**CDE-02 — Booking Legal Entity Identifier**

- **Definition:** The identifier of the bank's own legal entity in which a position or exposure is booked — the entity within the banking group that is the obligee or holder of record.
- **Why critical:** Group consolidation requires summing exposures across subsidiaries and eliminating intragroup positions. Without a reliable booking entity identifier, it is impossible to produce subsidiary-level regulatory reports or consolidate to group level. ¶33 requires single identifiers for *"legal entities"*; ¶41 requires coverage across the *"banking organisation."*
- **Risk types:** Cross-cutting (all risk types), concentration
- **Criticality: 3** — *Without this element, the aggregated group risk exposure cannot be computed or attributed to any subsidiary, because records cannot be partitioned by booking entity for consolidation or elimination of intragroup positions.*
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (¶41) — *"all material risk exposures… across the banking group"*
- **Search terms:** legal entity ID, entity code, booking entity, subsidiary code, LEI of bank entity, org unit code, company code, reporting entity
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null, valid booking entity identifier | Count of risk records with null or unresolvable booking entity code | 0 for material positions
  - *Validity* — Every booking entity code resolves to an entry in the authoritative legal entity hierarchy | Count of entity codes not present in the group entity register | 0
  - *Consistency* — The booking entity recorded on the risk record matches the entity recorded in the general ledger for the same transaction | Count of risk-to-GL mismatches on entity code per reconciliation run | 0 material mismatches

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary value of a risk position before the application of collateral, netting, or credit risk mitigation — expressed in the transaction currency. This is the raw exposure quantum from which all risk aggregates are built.
- **Why critical:** It is the quantity being aggregated. Every credit, market and counterparty risk measure — regulatory capital, large-exposure limits, concentration metrics — is computed from or compared against this amount. ¶52 requires reports to *"accurately and precisely convey aggregated risk data."*
- **Risk types:** Credit, counterparty credit, market, concentration
- **Criticality: 3** — *Without this element, no aggregated risk exposure figure can be computed at all, because there is no quantity to sum.*
- **Driven by:** Principle 3 (¶36a) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 7 (¶52); Principle 5 (¶46a) — *"aggregated credit exposure to a large corporate borrower"*
- **Search terms:** exposure at default (EAD), notional amount, outstanding balance, drawn amount, mark-to-market value, fair value, position size, nominal value, current exposure
- **Data quality requirements:**
  - *Accuracy* — The gross exposure amount on a risk record reconciles to the corresponding balance on the general ledger or system of record within defined tolerance | Sum of absolute differences between risk exposure and GL balance per product type | Within materiality threshold per ¶56
  - *Completeness* — No material exposure record carries a null or zero exposure amount where a non-zero position exists | Count of active positions with null or zero exposure amount | 0 for positions above materiality threshold
  - *Timeliness* — Exposure amounts reflect the position as of the declared as-of date within the agreed batch or intraday window | Count of exposure records whose value timestamp exceeds the agreed staleness threshold | 0 for critical risk categories per ¶45–46

---

**CDE-04 — Transaction Currency**

- **Definition:** The ISO 4217 currency code in which a position or exposure is denominated, required to convert amounts to a reporting or base currency for aggregation.
- **Why critical:** Multi-currency aggregation is impossible without a reliable currency code. An incorrect currency causes the FX conversion to apply the wrong rate, distorting every aggregate that spans currencies. Principle 4 requires aggregation *"across the banking group"* — which is inherently multi-currency. ¶42 acknowledges that not all risks need a common metric, but where conversion is applied, the input currency must be correct.
- **Risk types:** Market, credit, liquidity, cross-cutting
- **Criticality: 2** — The aggregate is produced but, where currency is wrong, the FX-converted amount is incorrect. The figure exists but is distorted; it does not become entirely uncomputable.
- **Driven by:** Principle 4 (¶41–42) — *"risk data aggregation capabilities should be the same regardless of the choice of risk aggregation systems implemented"*; Principle 3 (¶36c)
- **Search terms:** currency code, ISO currency, transaction currency, denomination currency, ccy, base currency flag
- **Data quality requirements:**
  - *Validity* — Every exposure record carries a currency code that is a valid, active ISO 4217 code | Count of records with invalid or deprecated currency codes | 0
  - *Completeness* — No material exposure record has a null currency code | Count of exposure records with null currency | 0 for positions above materiality threshold
  - *Consistency* — The currency code on the risk record matches the currency recorded on the originating trade or loan in the source system | Count of currency mismatches between risk system and source system per reconciliation | 0 material mismatches

---

**CDE-05 — Risk Type Classification**

- **Definition:** The taxonomy code that classifies an exposure or position by primary risk type — at minimum: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk. May carry sub-type codes (e.g. single-name credit vs. sector concentration).
- **Why critical:** Risk reports are organised and consumed by risk type. Without reliable classification, exposures cannot be routed to the correct risk framework, limit structure or capital calculation. Aggregating across misclassified exposures produces figures that mix incompatible risk measures. ¶57 requires reports to cover *"all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*
- **Risk types:** Cross-cutting
- **Criticality: 2** — An aggregate is produced, but it draws from the wrong population: credit exposures may be counted in market risk totals, or counterparty exposures excluded from credit concentration reports. The figure exists but is unreliable for the named risk type.
- **Driven by:** Principle 7 (¶53b) — *"Automated and manual edit and reasonableness checks, including an inventory of the validation rules that are applied to quantitative information"*; Principle 8 (¶57)
- **Search terms:** risk type code, risk category, risk class, risk taxonomy, product risk flag, risk bucket, asset class
- **Data quality requirements:**
  - *Validity* — Every risk record carries a risk type code drawn from the bank's approved taxonomy | Count of records with codes not in the authorised risk taxonomy | 0
  - *Completeness* — No material exposure record lacks a risk type classification | Count of exposure records with null risk type | 0 for positions above materiality threshold
  - *Consistency* — The risk type classification applied in the risk system is consistent with the classification applied in regulatory capital calculations for the same instrument | Count of classification mismatches between risk system and capital system per period | 0 material mismatches

---

**CDE-06 — Business Line**

- **Definition:** The organisational dimension that identifies which business unit or division originated or owns a risk position — e.g. retail banking, corporate banking, trading, treasury, private banking.
- **Why critical:** Principle 4 explicitly names *"business line"* as a required aggregation dimension. Supervisors expect the bank to be able to slice any risk aggregate by business line on demand (¶50). Without a reliable business line attribute, the bank cannot demonstrate coverage across the organisation or identify business-line-level concentrations.
- **Risk types:** Cross-cutting
- **Criticality: 2** — The total aggregate is computable, but the business-line sub-aggregate — which Principle 4 mandates — cannot be produced or verified. The slice is missing.
- **Driven by:** Principle 4 (¶41) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50)
- **Search terms:** business line, business unit, division code, LOB (line of business), segment, desk code, product line, front office unit
- **Data quality requirements:**
  - *Completeness* — Every material risk record carries a non-null business line code | Count of records with null business line above materiality threshold | <0.5% of population
  - *Validity* — Every business line code resolves to an entry in the bank's approved organisational hierarchy | Count of codes not in the authorised hierarchy | 0
  - *Consistency* — The business line assigned in the risk system matches the business line recorded in the general ledger for the same position | Count of mismatches per reconciliation cycle | 0 material mismatches

---

**CDE-07 — Geography / Country Code**

- **Definition:** The ISO 3166-1 alpha-2 (or equivalent standard) country code representing the booking location, counterparty domicile, or collateral jurisdiction — as relevant to the risk in question, with the specific geography concept documented per use case.
- **Why critical:** Principle 4 names *"region"* as a required aggregation dimension. ¶50 uses country credit exposure as the explicit example of an on-demand aggregation capability supervisors will test. Without a reliable geography code, the bank cannot produce country-level concentration reports, cross-border exposure summaries, or respond to supervisory ad hoc queries by country.
- **Risk types:** Credit, market, liquidity, concentration
- **Criticality: 2** — The total exposure aggregate is computable, but the country sub-aggregate — which Principle 4 mandates and ¶50 names explicitly — cannot be produced reliably. The slice degrades.
- **Driven by:** Principle 4 (¶41) — *"Data should be available by… region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*
- **Search terms:** country code, booking country, counterparty country, country of risk, domicile country, region code, jurisdiction, ISO country
- **Data quality requirements:**
  - *Completeness* — Every material risk record carries a non-null, valid geography code | Count of records with null geography above materiality threshold | <0.5% of population
  - *Validity* — Every geography code is a valid, active ISO 3166-1 code or an approved internal regional grouping | Count of invalid or deprecated codes | 0
  - *Consistency* — The geography code in the risk system is consistent with the counterparty domicile recorded in the party master for the same counterparty | Count of mismatches per reconciliation | 0 for material counterparties

---

**CDE-08 — Industry / Sector Classification**

- **Definition:** The sector or industry code assigned to a counterparty or exposure, drawn from a standard taxonomy (e.g. NACE, GICS, SIC, or an approved internal equivalent), identifying the economic sector of the obligor.
- **Why critical:** Principle 4 names *"industry"* as a required aggregation dimension. ¶57 lists *"industry sector for credit risk"* as a required component of comprehensive risk reports. ¶50 names industry credit exposure as the second explicit test of on-demand aggregation. Without reliable sector codes, sector concentration cannot be measured.
- **Risk types:** Credit, concentration
- **Criticality: 2** — The total credit aggregate is computable, but the sector-level concentration slice — which Principles 4 and 8 both require — is unreliable. The slice degrades.
- **Driven by:** Principle 4 (¶41) — *"Data should be available by… industry"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*; Principle 6 (¶50)
- **Search terms:** industry code, sector code, NACE code, GICS sector, SIC code, industry classification, counterparty sector, economic sector
- **Data quality requirements:**
  - *Completeness* — Every material counterparty record carries a non-null sector code | Count of counterparty records with null sector above materiality threshold | <1% of population
  - *Validity* — Every sector code is drawn from the approved taxonomy version in force at the reporting date | Count of codes not in the current approved taxonomy | 0
  - *Consistency* — The sector code assigned in the risk system matches the sector recorded in the credit origination system for the same counterparty | Count of mismatches per cycle | 0 for material counterparties

---

**CDE-09 — As-Of / Position Date**

- **Definition:** The business date as of which a risk position or exposure is stated — the temporal anchor that defines which snapshot an aggregate represents. Distinct from system load date or processing date.
- **Why critical:** Every risk aggregate is meaningless without a declared as-of date. Reconciliation between risk data and the general ledger, and all comparisons between reporting periods, require that both sides refer to the same business date. ¶50 explicitly frames the supervisory test as exposure *"as of a specified date."* An aggregate over a mixed population of dates is not an aggregate — it is noise.
- **Risk types:** Cross-cutting
- **Criticality: 3** — *Without this element, the aggregated risk exposure as of date D cannot be computed or reconciled at all, because records from different business dates cannot be distinguished, and the aggregate cannot be tied to the general ledger which is also date-keyed.*
- **Driven by:** Principle 5 (¶44–45) — *"produce aggregate risk information on a timely basis"*; Principle 3 (¶36c) — reconciliation with accounting data; Principle 6 (¶50) — *"country credit exposures as of a specified date"*
- **Search terms:** as-of date, position date, value date, reference date, business date, snapshot date, reporting date, trade date
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null as-of date | Count of records with null as-of date | 0
  - *Validity* — Every as-of date is a valid business date within the bank's approved trading calendar and is not a future date relative to the processing timestamp | Count of records with invalid or future as-of dates | 0
  - *Timeliness* — The gap between the as-of date and the date on which the record is available for aggregation meets the agreed SLA for the risk type | Count of records where (load date − as-of date) exceeds the SLA per risk tier | 0 breaches for critical risk categories per ¶46

---

**CDE-10 — GL / Source System Reconciliation Key**

- **Definition:** The identifier — typically a trade reference, journal entry reference, or account number — that links a risk record to its corresponding entry in the general ledger or authoritative source system. This is the key that makes reconciliation between risk data and accounting data mechanically possible.
- **Why critical:** ¶36(c) requires risk data to be reconciled with accounting data. Without a reconciliation key, the reconciliation is a statistical comparison at best; individual mismatches cannot be located and corrected. An aggregate that cannot be reconciled to the ledger cannot be evidenced as accurate — which ¶36(a) equates to the standard applicable to accounting data. An unreconcilable figure is, under this standard, a non-compliant figure.
- **Risk types:** Cross-cutting
- **Criticality: 3** — *Without this element, the accuracy of the aggregated exposure figure cannot be reconciled to the general ledger at all, because there is no key to join individual risk records to their accounting counterparts — and an unverifiable figure fails ¶36(a–c) regardless of whether its computed value happens to be correct.*
- **Driven by:** Principle 3 (¶36c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; ¶36(a); Principle 7 (¶53a) — *"processes to reconcile reports to risk data"*
- **Search terms:** trade reference, deal ID, GL journal reference, account number, transaction ID, source reference, ledger entry ID, booking reference, unique trade identifier (UTI)
- **Data quality requirements:**
  - *Completeness* — Every material risk record carries a non-null reconciliation key | Count of risk records above materiality threshold with null reconciliation key | 0
  - *Uniqueness* — The reconciliation key uniquely identifies a single GL or source-system record; no two risk records map to the same GL entry unless the relationship is explicitly documented as a known many-to-one | Count of unexpected duplicate reconciliation keys per batch | 0 for material positions
  - *Accuracy* — The exposure amount on the risk record ties to the balance on the matched GL entry within tolerance | Sum of unreconciled differences by product type per period | Within materiality threshold per ¶56

---

**CDE-11 — Source System / Provenance Flag**

- **Definition:** The identifier of the upstream system, feed or process that originated a risk record — and, critically, whether the record was produced by an automated feed or entered through a manual or end-user-computing (EUC) process (e.g. a spreadsheet, access database, or manual journal).
- **Why critical:** ¶36(b) requires effective mitigants for manual and EUC processes. ¶39 requires documentation explaining the appropriateness of manual workarounds and their *"criticality to the accuracy of risk data aggregation."* Without a provenance flag, it is impossible to identify which records are EUC-derived, to apply elevated scrutiny to them, or to demonstrate to supervisors that the risk of manual error has been assessed and mitigated. A register that is silent on provenance cannot evidence compliance with ¶36(b–d).
- **Risk types:** Cross-cutting
- **Criticality: 2** — The aggregate is computable, but the bank cannot segregate automated from manual inputs, cannot apply differential controls, and cannot demonstrate the accuracy standard required by ¶36(a). The evidential trail for accuracy degrades.
- **Driven by:** Principle 3 (¶36b) — *"Where a bank relies on manual processes and desktop applications… it should have effective mitigants in place"*; ¶36(d) — *"single authoritative source"*; ¶39 — *"document and explain all of their risk data aggregation processes whether automated or manual"*
- **Search terms:** source system code, feed name, source system ID, EUC flag, manual entry flag, data origin, ingestion method, upstream system, data provenance, input channel
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null source system code | Count of records with null source system identifier | 0
  - *Validity* — Every source system code resolves to a registered entry in the bank's data source inventory, including EUC classification | Count of codes not in the authorised source register | 0
  - *Accuracy* — The proportion of material exposure records sourced from manual or EUC processes is measured and reported; where the proportion exceeds agreed thresholds, escalation occurs | Percentage of exposure (by notional) sourced from EUC/manual feeds per risk type per period | Tracked against threshold set by risk data owner; escalation triggered on breach

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Counterparty Single-View Reconciliation Across Source Systems**

*Spans: CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-06 (Business Line), CDE-07 (Geography)*

- **What it is:** The requirement that every distinct physical counterparty resolves to exactly one canonical counterparty identifier across all booking systems, product platforms and legal entities within the banking group. This is not a property of any single element — it is an organisational-level reconciliation that requires comparing the counterparty population in each source system against the enterprise party master and resolving conflicts.
- **Why it is cross-cutting and cannot be expressed as a single-element DQ rule:** CDE-01 can be monitored for completeness and uniqueness within one system. But the failure mode BCBS 239 targets — the same counterparty appearing under different IDs in the loans system, the derivatives system and the securities system — is invisible when each system is monitored in isolation. The rule must span the join.
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including… counterparties"*; Principle 4 (¶41); Principle 5 (¶46a–b)
- **Rule intent:** Every counterparty that holds positions in more than one source system maps to a single canonical counterparty identifier; no material exposure is stranded under an unmapped or orphaned local identifier.
- **Dimension:** *Consistency*
- **Measurement:** Count of distinct local counterparty identifiers (per source system) that cannot be matched to a canonical party master record; and count of canonical party master records where the sum of exposures across source systems differs from the exposure computed by the risk aggregation layer by more than the materiality threshold
- **Suggested threshold:** 0 unmatched identifiers for counterparties above the large-exposure notification threshold; reconciliation difference within materiality tolerance for all others

---

**XDQ-02 — Risk-to-Finance Reconciliation (Risk Ledger vs. General Ledger)**

*Spans: CDE-03 (Gross Exposure Amount), CDE-09 (As-Of / Position Date), CDE-10 (GL / Source System Reconciliation Key), CDE-02 (Booking Legal Entity Identifier)*

- **What it is:** The periodic, structured reconciliation that compares the total risk exposure population in the risk aggregation layer against the corresponding balances in the general ledger, at the level of booking entity, as-of date and product type, using the reconciliation key (CDE-10) as the linking mechanism. This reconciliation is the primary evidential mechanism for ¶36(a) — that risk data is held to the same accuracy standard as accounting data.
- **Why it is cross-cutting and cannot be expressed as a single-element DQ rule:** Each individual CDE can be monitored for its own completeness or accuracy. But the reconciliation itself — the act of tying the risk population to the finance population and explaining every difference — requires all four CDEs to be simultaneously valid and consistently populated. A break in any one of them will cause the reconciliation to fail, but monitoring them individually will not tell you that the reconciliation as a whole is intact.
- **Driven by:** Principle 3 (¶36a) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; ¶36(c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 7 (¶53a) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Rule intent:** The total exposure balance in the risk aggregation layer, summed by booking entity and as-of date, ties to the corresponding GL balance within defined tolerance; every break item is identified, owned, and resolved within the agreed escalation timeframe.
- **Dimension:** *Accuracy*
- **Measurement:** (a) Sum of absolute differences between risk-layer exposure totals and GL balances by product type, booking entity and as-of date per reconciliation cycle; (b) Count of break items outstanding beyond the agreed resolution SLA; (c) Count of exposure records with a reconciliation key that returns no match in the GL
- **Suggested threshold:** Aggregate difference within accounting materiality threshold per ¶56; break items resolved within the agreed SLA (to be defined by risk and finance data owners); 0 unmatched reconciliation keys for positions above materiality

---

**XDQ-03 — Manual / EUC Input Rate Monitoring Across Risk Aggregation Chain**

*Spans: CDE-11 (Source System / Provenance Flag), CDE-03 (Gross Exposure Amount), CDE-09 (As-Of / Position Date)*

- **What it is:** The group-wide measurement of what proportion of total risk exposure (by notional amount, by risk type, and by as-of date) passes through a manual or EUC input rather than an automated feed — and whether that proportion is tracked, trended and escalated as required by ¶39.
- **Why it is cross-cutting and cannot be expressed as a single-element DQ rule:** CDE-11 can flag whether an individual record is EUC-sourced. But the compliance obligation in ¶36(b) and ¶39 is about the *aggregate materiality* of manual reliance across the bank's risk data population. Whether a given EUC proportion is acceptable depends on what fraction of total exposure it represents — which requires joining CDE-11 to CDE-03 and CDE-09 across the whole population.
- **Driven by:** Principle 3 (¶36b) — *"Where a bank relies on manual processes and desktop applications… it should have effective mitigants in place"*; ¶39 — *"a description of their criticality to the accuracy of risk data aggregation and proposed actions to reduce the impact"*; ¶40 — *"measure and monitor the accuracy of data"*
- **Rule intent:** The percentage of total risk exposure (by notional) that is sourced from manual or EUC inputs is measured per risk type per reporting period; where the percentage exceeds a board-approved threshold or trends upward over successive periods, an escalation is triggered and the bank is required to document mitigants.
- **Dimension:** *Accuracy* (with timeliness and completeness secondary)
- **Measurement:** (a) Percentage of gross exposure notional (CDE-03) attributed to EUC/manual source flags (CDE-11), segmented by risk type and as-of date (CDE-09); (b) Trend direction over the last N reporting periods; (c) Count of EUC-sourced records above materiality threshold that lack documented mitigants in the data source inventory
- **Suggested threshold:** EUC/manual percentage tracked against a threshold set by the Chief Data Officer or equivalent; alert triggered on upward trend for two or more consecutive periods; 0 material EUC-sourced records without documented mitigants

---

## 4. Out of Scope

The following requirements arise from Principles 1–11 but cannot be satisfied — even partially — by a data catalog's CDE register, data quality monitoring, or metadata management. Stating this boundary clearly is what makes the catalog-based work defensible, because it prevents the catalog from being overstated as a compliance solution.

---

### Governance structure and board accountability (Principle 1, ¶27–31)

The requirement that the *board reviews and approves* the risk data aggregation framework (¶28), that *senior management understands limitations* in coverage and automation (¶30), and that the board *determines its own risk reporting requirements* (¶31) are organisational and fiduciary obligations. A data catalog can document data ownership and stewardship roles, and it can surface known data quality gaps. It cannot constitute, enforce or evidence a board review and approval process. What is needed instead: a formal governance committee structure with documented board-level sign-off, minutes, and a periodic attestation process against the principles.

---

### Independent validation of aggregation processes (Principle 1, ¶29a)

The regulation requires *independent validation* of risk data aggregation and reporting processes by staff with IT, data and reporting expertise. A catalog can supply metadata and lineage documentation that an independent validator could use as evidence. It cannot perform the validation itself, nor does populating a catalog constitute completion of validation. What is needed instead: a second-line or internal audit programme with a defined scope, methodology, and output that references the catalog's documentation as one input.

---

### Business continuity planning for risk data (Principle 2, ¶32)

Incorporating risk data aggregation capabilities into *business continuity planning* and *business impact analysis* is an operational resilience obligation. A catalog that documents source systems contributes context, but the BCP itself — recovery time objectives, failover procedures, crisis escalation — lives outside any catalog. What is needed instead: a formal BCP/BIA programme that explicitly lists the risk data systems identified in the catalog as critical infrastructure.

---

### Report content, comprehensiveness, and forward-looking assessments (Principle 8, ¶57–60)

Principle 8 requires risk reports to cover all material risk areas with *forward-looking forecasts and stress tests* (¶60), to include *capital adequacy, regulatory capital, and funding positions* (¶59), and to identify *emerging risk concentrations* (¶58). **Note on the split:** Principle 8 also names industry sector as a required report dimension (¶57), which drives CDE-08 above — that data element obligation is addressable by the catalog. However, the obligation that reports *contain* those forward-looking assessments, that they are *comprehensive in scope*, and that they *propose recommendations for action* (¶58) is a reporting governance and content matter. No CDE register or DQ monitor governs whether a stress test scenario is appropriately designed, whether capital projections are included, or whether the report's conclusions are actionable. What is needed instead: report design governance, report content standards, and a report inventory with defined scope and recipient requirements.

---

### Clarity, usefulness and recipient feedback (Principle 9, ¶61–69)

The requirement that reports be *clear and concise*, that they *balance quantitative data with qualitative interpretation* (¶62), that *reporting policies recognise the differing information needs* of the board versus senior management (¶63), and that the bank *periodically confirms with recipients* that information is relevant and appropriate (¶69) are communication design and stakeholder engagement obligations. A catalog can document report definitions and lineage, and ¶67's requirement for *"an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"* is catalog-addressable. However, the clarity of a report's narrative, the appropriateness of its structure for a given audience, and the process of soliciting recipient feedback cannot be assessed or enforced through metadata. What is needed instead: report governance procedures, recipient feedback mechanisms, and report quality review frameworks.

---

### Frequency setting and crisis escalation (Principle 10, ¶70–71)

The board and senior management must *set frequency requirements* for each report in both normal and stress conditions, and the bank must *routinely test its ability to produce accurate reports within established timeframes* (¶70). A catalog can record the declared frequency of a report as a metadata attribute. It cannot set that frequency as a governance decision, enforce it, or test the bank's operational ability to produce the report under stress. What is needed instead: a report frequency policy, SLA documentation per report type, and periodic drill/testing of crisis production capability.

---

### Distribution controls and confidentiality (Principle 11, ¶72–73)

The requirement for *rapid collection and dissemination of reports* balanced against *confidentiality* (¶72), and for periodic confirmation that recipients receive timely reports (¶73), is a report distribution and access control matter. A catalog can document data classifications and sensitivity levels for individual datasets, which supports access control decisions. However, the operational distribution mechanism — who receives which report, via which channel, within what timeframe — is governed by the reporting infrastructure and access management systems, not by the catalog. What is needed instead: a report distribution register, access management controls, and a periodic distribution audit.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | 2 (¶33), 4 (¶41), 5 (¶46a–b) | Uniqueness, Completeness, Consistency |
| CDE-02 | Booking Legal Entity Identifier | 3 | 2 (¶33), 4 (¶41) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3 (¶36a), 5 (¶46a), 7 (¶52) | Accuracy, Completeness, Timeliness |
| CDE-04 | Transaction Currency | 2 | 3 (¶36c), 4 (¶41–42) | Validity, Completeness, Consistency |
| CDE-05 | Risk Type Classification | 2 | 7 (¶53b), 8 (¶57) | Validity, Completeness, Consistency |
| CDE-06 | Business Line | 2 | 4 (¶41), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-07 | Geography / Country Code | 2 | 4 (¶41), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-08 | Industry / Sector Classification | 2 | 4 (¶41), 8 (¶57), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-09 | As-Of / Position Date | 3 | 5 (¶44–45), 3 (¶36c), 6 (¶50) | Completeness, Validity, Timeliness |
| CDE-10 | GL / Source System Reconciliation Key | 3 | 3 (¶36a–c), 7 (¶53a) | Completeness, Uniqueness, Accuracy |
| CDE-11 | Source System / Provenance Flag | 2 | 3 (¶36b–d), 3 (¶39) | Completeness, Validity, Accuracy |

**Criticality distribution:** 5 elements at level 3 (CDE-01, CDE-02, CDE-03, CDE-09, CDE-10); 6 elements at level 2 (CDE-04, CDE-05, CDE-06, CDE-07, CDE-08, CDE-11); 0 elements at level 1. No element was assessed as level 1 because every element in this register, if absent or wrong, degrades at least one mandatory aggregation slice or control — none is purely interpretive context. The level-1 category remains formally available but does not apply to this register as constructed.