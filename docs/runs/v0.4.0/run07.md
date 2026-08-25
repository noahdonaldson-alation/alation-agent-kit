# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Board-level accountability for data quality as a risk discipline.** Senior management must identify data critical to risk aggregation and ensure IT strategy addresses gaps. A firm's inability to aggregate risk fully is a *governance* failure, not merely a technical one. (¶27–30: *"A bank's board and senior management should promote the identification, assessment and management of data quality risks as part of its overall risk management framework."*)

- **Integrated data architecture with single identifiers and documented metadata.** Banks must establish integrated data taxonomies across the group, including metadata characteristics and unified naming conventions for legal entities, counterparties, customers, and accounts. (¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*)

- **Accurate, reconciled, and largely automated risk data aggregation.** Risk data controls must match the robustness of accounting controls; data must be reconciled to source systems including accounting data; and a single authoritative source per risk type is the target state. Manual processes must be documented and justified. (¶36: *"Controls surrounding risk data should be as robust as those applicable to accounting data"* and *"Risk data should be reconciled with bank's sources, including accounting data where appropriate."*)

- **Complete coverage across the full group, all material exposures, all aggregation dimensions.** Aggregated data must be available by business line, legal entity, asset type, industry, region, and other groupings relevant to the risk in question, including off-balance-sheet exposures. Incompleteness must be measured, monitored, and explained. (¶41–43: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*)

- **Timeliness under both normal and stress conditions, with rapid production of critical risk data.** Risk systems must be capable of producing aggregated data rapidly during stress/crisis for credit, counterparty, trading, liquidity, and operational risks. Frequency is risk-type-dependent. (¶45–46: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*)

- **Adaptable aggregation that supports ad hoc queries, drill-down, and scenario analysis.** The aggregation capability must be flexible enough to respond to supervisory queries, changing business structure, and new regulatory requirements without rebuilding data pipelines from scratch. (¶48–50.)

**Who it applies to**

Principles 1–11 apply to Global Systemically Important Banks (G-SIBs) as the primary in-scope population, with national supervisors expected to apply them to domestic systemically important banks (D-SIBs) and other institutions over time. The obligations fall on the banking group as a whole — including subsidiaries — not merely the parent entity's risk function.

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** A persistent, system-independent identifier that uniquely and unambiguously identifies a single legal counterparty across all booking systems, risk engines, and the general ledger. This is the master key that links every exposure — loan, derivative, off-balance-sheet commitment — to the same counterparty record regardless of originating system.
- **Why critical:** Without a resolved, unique counterparty identifier, credit exposure cannot be aggregated across business lines or legal entities. Concentration risk to a single borrower cannot be computed. The aggregated credit exposure to a large corporate borrower, explicitly named as a critical risk in ¶46(a), is impossible to produce correctly without this key.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3** — *"Without this element, the aggregate figure 'total credit exposure to counterparty X' cannot be computed at all, because there is no basis on which to sum exposures booked in different systems or legal entities to the same obligor."* This is structurally load-bearing for every counterparty-level aggregate.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41) — completeness across all material exposures; Principle 5 (¶46a) — *"The aggregated credit exposure to a large corporate borrower."*
- **Search terms:** counterparty ID, obligor ID, client identifier, party ID, GFCID, LEI (Legal Entity Identifier), customer master key, counterparty master, entity reference
- **Data quality requirements:**
  - *Uniqueness* — Each distinct real-world counterparty maps to exactly one identifier across all source systems | Count of counterparty identifiers that resolve to more than one master record, or master records that map to more than one source-system identifier | Target: zero duplicates; no master record with ambiguous source mappings
  - *Completeness* — Every exposure record carries a non-null, populated counterparty identifier | Count of exposure records with null, blank, or placeholder counterparty identifier | Target: 0% null rate on in-scope exposure populations
  - *Validity* — Every counterparty identifier on an exposure record resolves to an active record in the counterparty master | Count of exposure records whose counterparty identifier does not match any record in the authoritative counterparty reference | Target: 0% unmatched rate
  - *Timeliness* — New counterparties are registered in the master before or at the point of first booking | Elapsed time between first booking event and counterparty master record creation | Target: same-day registration for new counterparties

---

**CDE-02 — Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier of the bank's own legal entity in which a position or exposure is booked. Distinct from the counterparty identifier: this identifies *which part of the banking group* owns the record, not the external party. Must map unambiguously to the group's legal entity hierarchy.
- **Why critical:** Group consolidation and subsidiary-level reporting both depend on the ability to attribute every exposure to a specific legal entity and then roll up correctly. Without it, the bank cannot produce group-level or entity-level aggregates and cannot demonstrate completeness of subsidiary coverage to supervisors.
- **Risk types:** Cross-cutting (credit, market, liquidity all require entity-level decomposition), concentration
- **Criticality: 3** — *"Without this element, the aggregate figure 'group total exposure' cannot be computed or evidenced, because there is no mechanism to identify which legal entities contribute to the consolidation perimeter or to exclude entities that are out of scope."* Required for every consolidation calculation.
- **Driven by:** Principle 2 (¶33) — *"unified naming conventions for data including legal entities"*; Principle 4 (¶41–43) — completeness across the banking group including off-balance-sheet; Principle 1 (¶30) — *"limitations that prevent full risk data aggregation, in terms of coverage (eg risks not captured or subsidiaries not included)."*
- **Search terms:** legal entity ID, booking entity, entity code, LE code, subsidiary identifier, consolidated entity, group entity, MFI code, RCON entity, LEI (when used for the bank's own entity)
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null booking entity identifier | Count of risk records with null booking entity | Target: 0% null rate
  - *Validity* — Every booking entity identifier on a risk record corresponds to an entity within the approved group consolidation perimeter | Count of records with booking entity codes not present in the legal entity master hierarchy | Target: 0% unmatched
  - *Consistency* — The legal entity hierarchy used in risk aggregation matches the hierarchy used in financial reporting consolidation | Number of legal entities present in one hierarchy but absent from the other | Target: zero discrepancies between risk and finance entity perimeters
  - *Accuracy* — Off-balance-sheet exposures are attributed to a legal entity | Proportion of off-balance-sheet exposure records with populated versus null booking entity | Target: 0% null rate on off-balance-sheet population specifically

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary value of a risk exposure before the application of any credit risk mitigant, netting, or collateral offset. Denominated in the transaction currency or a reporting currency equivalent. This is the primary quantity that risk aggregation sums across the portfolio.
- **Why critical:** Every aggregated risk figure — total credit exposure, concentration, limit utilization — is built by summing this amount. If the amount is wrong, all downstream aggregates are wrong. There is no indirect proxy: the exposure measure is the thing being aggregated.
- **Risk types:** Credit, counterparty, concentration, market (as notional or mark-to-market value)
- **Criticality: 3** — *"Without this element, the aggregate figure 'total credit exposure' cannot be computed at all, because there is no monetary quantity to sum across the portfolio."* The most fundamental quantity in any risk aggregate.
- **Driven by:** Principle 3 (¶36a) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (¶41) — all material risk exposures must be captured; Principle 7 (¶52) — *"Risk management reports should be accurate and precise."*; Principle 5 (¶46a, b) — aggregated credit and counterparty credit exposures named as critical risks.
- **Search terms:** exposure at default, EAD, notional amount, nominal amount, outstanding balance, drawn amount, mark-to-market value, current exposure, replacement cost, loan balance, commitment amount
- **Data quality requirements:**
  - *Accuracy* — Exposure amounts reconcile to the general ledger or system of record within defined tolerance | Sum of exposure amounts in risk systems versus corresponding balances in the general ledger, measured daily; variance expressed in absolute and percentage terms | Target: variance within defined materiality threshold (analogous to accounting materiality per ¶56)
  - *Completeness* — No material exposure is missing from the aggregated population | Count and value of exposures present in the general ledger but absent from the risk data store | Target: zero unexplained gaps above materiality threshold
  - *Validity* — Exposure amounts are non-negative where the business definition requires it; currency codes are valid ISO 4217 values | Count of records with negative gross exposure where not permitted; count with invalid or missing currency codes | Target: 0% invalid on both checks
  - *Timeliness* — Exposure amounts reflect the current position date, not stale data from prior close | Age of the most recent update to each exposure record relative to current position date | Target: all records updated within the defined production cycle for the relevant risk type

---

**CDE-04 — Risk Type Classification**

- **Definition:** The controlled vocabulary term that classifies an exposure or position by the primary risk type it contributes to: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk. Must map to a governed taxonomy used consistently across the group.
- **Why critical:** Risk type classification is the primary partitioning key for every risk report. Reports cover all significant risk areas (¶57). Without a consistent, governed classification, exposures cannot be correctly routed to the right risk aggregate, and cross-risk concentration analysis is impossible.
- **Risk types:** Cross-cutting — this element *defines* which risk type applies
- **Criticality: 2** — The aggregate figure for a given risk type (e.g., total credit risk exposure) can be produced but will include misclassified items from other risk types, distorting the result. The figure exists but cannot be trusted in part. The error is a slice failure, not a computational impossibility.
- **Driven by:** Principle 4 (¶41–42) — aggregation capabilities must cover all material risk exposures; Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*; Principle 2 (¶33) — *"integrated data taxonomies."*
- **Search terms:** risk type, risk category, risk classification, risk class code, risk taxonomy, risk pillar, Basel risk type
- **Data quality requirements:**
  - *Validity* — Every risk record carries a risk type value drawn from the approved controlled vocabulary | Count of records with risk type values not present in the approved taxonomy | Target: 0% invalid values
  - *Completeness* — Risk type is populated on every exposure and position record | Count of records with null or blank risk type | Target: 0% null rate
  - *Consistency* — The same risk type taxonomy is applied uniformly across all booking systems and legal entities | Number of distinct risk type code sets in use across source systems; count of mapping conflicts between source codes and the canonical taxonomy | Target: single canonical mapping with zero unmapped codes

---

**CDE-05 — Business Line**

- **Definition:** The business line or segment to which an exposure or position is attributed, using the bank's internal organisational taxonomy. Examples include retail banking, corporate banking, trading, treasury, private banking. Must be drawn from a governed, group-wide code set.
- **Why critical:** Principle 4 explicitly requires data to be available by business line. Business line is a mandatory aggregation dimension for concentration analysis and management reporting. Without it, the bank cannot decompose group-level risk by business segment.
- **Risk types:** Cross-cutting (required for credit, market, and liquidity aggregation by segment)
- **Criticality: 2** — Group-level exposure figures are computed, but the business line slice degrades: the bank cannot satisfy the regulatory requirement to report by business line, and emerging concentrations in one segment cannot be identified. The aggregate exists but cannot be decomposed as required.
- **Driven by:** Principle 4 (¶41) — *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures... across all business lines and geographic areas."*
- **Search terms:** business line, business segment, LOB (line of business), business unit, division code, organisational unit, desk, product line
- **Data quality requirements:**
  - *Completeness* — Every exposure record carries a populated business line code | Count of records with null or missing business line | Target: 0% null rate
  - *Validity* — Business line codes are drawn from the approved group-wide taxonomy | Count of records with business line values not in the canonical code set | Target: 0% invalid
  - *Consistency* — Business line attribution is consistent between risk systems and management reporting systems for the same exposure population | Proportion of exposures where business line differs between risk data and management reporting source | Target: zero unexplained discrepancies

---

**CDE-06 — Geography / Country of Risk**

- **Definition:** The country or region to which a credit exposure is attributed for risk aggregation purposes — typically the country of the counterparty's domicile, the country of the collateral, or the country of the underlying obligor depending on the risk type. Must be an ISO 3166 country code or mapped to one.
- **Why critical:** Principle 4 requires aggregation by region. Principle 6 (¶50) explicitly names country credit exposure aggregation as a specific example of required adaptability. Geographic concentration risk cannot be assessed without this dimension.
- **Risk types:** Credit, concentration, cross-cutting
- **Criticality: 2** — Aggregate exposure figures are produced but cannot be sliced by country or region, which is an explicit regulatory requirement. Country concentration reports are rendered incomplete or unreliable. A supervisor requiring a rapid country exposure report during stress cannot be served.
- **Driven by:** Principle 4 (¶41) — *"data should be available by... region"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*; Principle 8 (¶57) — country as a component of credit risk reporting.
- **Search terms:** country of risk, country code, domicile country, risk country, country exposure, booking country, obligor country, ISO country code, geographic region, regional classification
- **Data quality requirements:**
  - *Completeness* — Country of risk is populated on all credit and counterparty exposures | Count of in-scope exposure records with null or missing country code | Target: 0% null rate on credit and counterparty populations
  - *Validity* — Country codes conform to ISO 3166-1 alpha-2 or alpha-3 | Count of records with country codes not in the ISO 3166 reference list | Target: 0% invalid
  - *Accuracy* — Country of risk classification follows the bank's documented methodology (domicile, incorporation, ultimate parent, or risk transfer) consistently | Proportion of records where country attribution does not follow the documented methodology on sample review | Target: consistent application with documented exceptions

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The industry or sector code assigned to a counterparty or exposure, drawn from a standard classification scheme (e.g., NACE, NAICS, GICS, or an internal taxonomy mapped to one of these). Used to assess sector concentration in the credit portfolio.
- **Why critical:** Principle 4 names industry as a required aggregation dimension. Principle 8 (¶57) names industry sector as a specific component of credit risk reporting. Sector concentration — an explicit supervisory concern — cannot be measured without this classification.
- **Risk types:** Credit, concentration
- **Criticality: 2** — Exposure aggregates are computed, but industry-level concentration cannot be assessed or reported. The specific regulatory requirement to report by industry sector (¶57) cannot be met. The slice degrades entirely.
- **Driven by:** Principle 4 (¶41) — *"data should be available by... industry"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas."*
- **Search terms:** industry code, sector code, NACE code, NAICS code, GICS sector, industry classification, counterparty sector, borrower industry, economic sector
- **Data quality requirements:**
  - *Completeness* — Industry/sector code is populated on all counterparty and credit exposure records | Count of records with null or missing industry code | Target: 0% null rate on credit exposure population
  - *Validity* — Industry codes are drawn from the approved classification scheme and mapped to a standard | Count of records with codes not present in the approved scheme | Target: 0% invalid
  - *Consistency* — The same counterparty is assigned the same industry code across all systems where it appears | Count of counterparties with conflicting industry codes across source systems | Target: single authoritative industry code per counterparty in the master, zero conflicts

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The business date as of which a risk position or exposure is stated. This is the temporal key that defines the snapshot to which every aggregate belongs. Distinct from processing date, booking date, or load timestamp.
- **Why critical:** Every risk aggregate is a point-in-time statement. Without the as-of date, records from different snapshots cannot be prevented from mixing in the same aggregate, and the bank cannot produce position data "as of a specified date" as required by ¶50. Under stress, the ability to produce data as of a specific intraday or prior-close date is essential.
- **Risk types:** Cross-cutting — all risk types require a temporal key
- **Criticality: 3** — *"Without this element, the aggregate figure 'total exposure as of [date]' cannot be computed at all, because there is no mechanism to select the correct snapshot or to prevent records from different business dates from mixing in the same aggregate."* Temporal integrity is structurally required for every compliant aggregate.
- **Driven by:** Principle 5 (¶44–46) — timeliness requirements for up-to-date risk data; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 3 (¶36) — accuracy requires knowing what date the data represents; Principle 7 (¶52–53) — reports must be accurate and reconcilable.
- **Search terms:** position date, as-of date, business date, reference date, valuation date, snapshot date, risk date, reporting date, effective date
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null position date | Count of records with null or missing position date | Target: 0% null rate
  - *Validity* — Position dates are valid calendar dates, not future dates (unless forward positions are in scope by design), and not dates preceding the bank's data history | Count of records with position dates that are null, non-parseable, or outside the valid range | Target: 0% invalid
  - *Timeliness* — The most recent position date in the risk data store matches the expected production cycle close date | Lag between expected close date and the latest position date loaded, measured per risk type and source system | Target: lag within the production SLA defined for each risk type; zero unexplained gaps

---

**CDE-09 — Reconciliation Key (Risk-to-Ledger Linkage)**

- **Definition:** The identifier or set of identifiers that links a risk data record unambiguously to its corresponding record in the general ledger or authoritative system of record. This may be a trade identifier, loan account number, or a composite key, depending on asset class. It is the mechanism by which ¶36(c) reconciliation is operationalised.
- **Why critical:** Principle 3 (¶36c) directly requires reconciliation of risk data to accounting sources. Without a reconciliation key, the bank cannot demonstrate that its risk aggregates are complete and accurate with respect to the ledger. An unverifiable figure is not a compliant figure under this principle — the requirement is not merely to produce a number but to be able to evidence it against the system of record.
- **Risk types:** Cross-cutting — reconciliation applies to all risk types that have a corresponding accounting entry
- **Criticality: 3** — *"Without this element, the aggregate figure 'total credit exposure' cannot be reconciled to the general ledger at all, because there is no key by which risk records map to accounting records — making the figure unverifiable, which under ¶36(c) is an equivalent compliance failure to producing a wrong figure."* This is the element most often missing from CDE registers and the one supervisors pursue directly.
- **Driven by:** Principle 3 (¶36c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53a) — *"Defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** trade ID, deal ID, loan account number, facility ID, position ID, ledger reference, GL account key, instrument ID, ISIN (where applicable), booking reference, transaction reference, account number
- **Data quality requirements:**
  - *Completeness* — Every risk record that has a corresponding accounting entry carries a populated reconciliation key | Count of risk records in scope for reconciliation with null or blank reconciliation key | Target: 0% null rate on reconcilable populations
  - *Validity* — Every reconciliation key on a risk record resolves to a record in the general ledger or system of record | Count of risk records whose reconciliation key does not match any record in the ledger | Target: 0% unmatched; all exceptions logged and explained
  - *Uniqueness* — Each accounting record maps to at most one risk record (or the mapping logic is explicitly documented for one-to-many relationships) | Count of ledger records with duplicate or conflicting risk record mappings where not permitted by the mapping methodology | Target: zero unexplained duplicates
  - *Accuracy* — The exposure amount on the risk record agrees with the balance on the linked ledger record within defined tolerance | Sum of absolute variances between risk exposure amount and ledger balance for matched pairs; expressed as a percentage of total portfolio | Target: within materiality threshold, consistent with ¶56 analogy to accounting materiality

---

**CDE-10 — Source System / Provenance Flag**

- **Definition:** The identifier of the system or process that originated a risk data record, combined with a flag indicating whether the record was produced by an automated feed or by a manual / end-user computing (EUC) process. This is the metadata element that makes lineage visible and enables the controls required by ¶36(b) and ¶39.
- **Why critical:** Principle 3 (¶36b, d) requires effective controls over manual processes and EUC inputs, and requires a single authoritative source per risk type. ¶39 requires documentation of all aggregation processes whether automated or manual. Without a source system identifier and EUC flag, the bank cannot identify which records are at higher risk of error, cannot enforce the single-source principle, and cannot demonstrate to supervisors that manual workarounds are controlled and limited.
- **Risk types:** Cross-cutting — applies to all risk data regardless of type
- **Criticality: 2** — Aggregate figures are produced, but the bank cannot demonstrate that manual inputs are controlled or that a single authoritative source is operating as intended. The control evidencing required by ¶36(b) and ¶39 degrades entirely; supervisory validation of data quality becomes impossible.
- **Driven by:** Principle 3 (¶36b) — *"Where a bank relies on manual processes and desktop applications... it should have effective mitigants in place"*; Principle 3 (¶36d) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (¶39) — *"banks to document and explain all of their risk data aggregation processes whether automated or manual."*
- **Search terms:** source system, originating system, system of record, data source flag, EUC flag, manual override flag, feed name, extraction source, data lineage, process type, automated vs manual indicator
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a populated source system identifier | Count of records with null or missing source system identifier | Target: 0% null rate
  - *Validity* — Source system identifiers correspond to registered, approved systems in the data catalog's system inventory | Count of records with source system codes not in the approved system register | Target: 0% unregistered source systems
  - *Accuracy* — Records originating from manual or EUC processes are correctly flagged as such | Proportion of manual-process records carrying the EUC flag, verified against process documentation | Target: 100% of known EUC-sourced records flagged; zero misclassified as automated
  - *Timeliness* — Lineage metadata is captured at ingestion, not retrospectively applied | Proportion of records where source system and EUC flag are assigned at load time versus patched post-load | Target: 100% assigned at load time

---

**CDE-11 — Collateral / Credit Risk Mitigant Identifier**

- **Definition:** The identifier linking an exposure to any associated collateral, guarantee, netting agreement, or credit risk mitigant. Enables calculation of net exposure (gross exposure less recognised mitigants) for capital and concentration purposes.
- **Why critical:** Credit risk concentrations must be assessed on a net basis to reflect economic reality. Principle 8 (¶58) requires reports to include information in the context of limits and risk appetite. Off-balance-sheet exposures (¶41) frequently have associated credit enhancement. Without this link, net exposure figures — which drive capital adequacy calculations — cannot be correctly computed.
- **Risk types:** Credit, counterparty, concentration
- **Criticality: 2** — Gross exposure aggregates are computable from CDE-03 alone, but net exposure figures — which are what risk appetite limits and capital requirements reference — are distorted or uncomputable for collateralised positions. The figure produced is gross only, not the figure that appears in risk reports and board packs.
- **Driven by:** Principle 4 (¶41) — all material risk exposures including off-balance-sheet; Principle 8 (¶57–58) — *"provide information in the context of limits and risk appetite/tolerance"*; Principle 3 (¶36a) — risk data controls as robust as accounting data.
- **Search terms:** collateral ID, collateral reference, netting agreement ID, ISDA master agreement reference, guarantee reference, credit risk mitigant, CRM identifier, security interest, pledge reference, collateral pool ID
- **Data quality requirements:**
  - *Completeness* — All collateral agreements and netting arrangements that reduce regulatory capital requirements are recorded with a populated collateral identifier | Count of exposures flagged as collateralised with null collateral identifier | Target: 0% null rate on collateralised population
  - *Validity* — Collateral identifiers resolve to active records in the collateral management system | Count of exposure records with collateral identifiers that do not match the collateral master | Target: 0% unresolved
  - *Accuracy* — Collateral values used in net exposure calculations are current (marked to market at the required frequency) | Age of collateral valuation date relative to the position date on the linked exposure | Target: collateral values no older than defined staleness threshold for the collateral type (e.g., daily for liquid securities, monthly for real estate)

---

**CDE-12 — Limit / Risk Appetite Threshold**

- **Definition:** The approved limit value against which a risk measure is monitored — for example, a single-name credit limit, a country exposure limit, or a trading desk VaR limit. Together with the exposure measure, this enables limit utilisation calculation.
- **Why critical:** Principle 8 (¶58) explicitly requires reports to provide information in the context of limits and risk appetite/tolerance. Without the limit value as a governed data element, utilisation cannot be calculated, breaches cannot be detected systematically, and the board cannot monitor adherence to risk appetite — which is the central governance objective of Principle 1.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 2** — Exposure figures are computable, but utilisation rates and limit breach alerts cannot be produced. The board and senior management cannot monitor whether the bank is operating within its risk appetite, which is the primary purpose of risk reports per ¶64–65. The reporting output degrades from decision-useful to merely descriptive.
- **Driven by:** Principle 8 (¶57–58) — *"Reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance"*; Principle 1 (¶28) — board approval of the risk data aggregation framework including risk appetite; Principle 9 (¶64) — *"The board should ensure that it is asking for and receiving relevant information that will allow it to fulfil its governance mandate."*
- **Search terms:** credit limit, exposure limit, VaR limit, position limit, concentration limit, risk appetite limit, limit threshold, approved limit, board-approved limit, limit register, limit code
- **Data quality requirements:**
  - *Accuracy* — Limit values reflect the most recently board- or committee-approved level | Count of limits in the risk system where the value differs from the most recent approval document | Target: zero discrepancies between system limit and approved limit
  - *Completeness* — A limit record exists for every risk dimension and counterparty/portfolio combination for which the risk appetite framework mandates a limit | Count of counterparties or portfolios with active exposures but no corresponding limit record | Target: 0% missing limits on in-scope populations
  - *Timeliness* — Limit values are updated in risk systems within the defined change-management SLA following board or committee approval | Elapsed time between approval event and system update | Target: within the defined SLA, zero stale limits beyond the tolerance period
  - *Validity* — Limit values are positive, denominated in an approved currency, and of an order of magnitude consistent with the portfolio they govern | Count of limit records with zero, negative, or implausible values | Target: 0% invalid

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Risk-to-Finance Reconciliation Coverage**

*Spans: CDE-03 (Gross Exposure Amount), CDE-09 (Reconciliation Key), CDE-08 (Position / As-Of Date), CDE-02 (Legal Entity Identifier)*

- **Dimension:** Accuracy and completeness
- **Rule intent:** The total exposure value aggregated in the risk data store must agree with the corresponding balances in the general ledger within a defined materiality tolerance, for each legal entity and each position date. This cannot be expressed as a per-record check on any single CDE — it is a population-level reconciliation that requires CDE-09 to link records, CDE-03 to provide the amounts being compared, CDE-02 to scope the reconciliation to the correct legal entity, and CDE-08 to ensure both sides are on the same date. Failures manifest as unexplained breaks: records present in the ledger but absent from risk data (completeness failure), or amounts that agree on count but differ on value (accuracy failure).
- **Measurement:** Absolute and percentage variance between sum of gross exposure amounts in the risk data store and the corresponding general ledger balances, computed per legal entity per position date. Separately: count and aggregate value of ledger records with no matching risk record (reconciliation key is null or unmatched) and risk records with no matching ledger record.
- **Suggested threshold:** Monetary variance within defined materiality threshold per ¶56 (expressed as percentage of total portfolio and absolute value); zero unexplained missing records above individual materiality threshold; all breaks documented with a resolution plan.
- **Regulatory grounding:** ¶36(c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; ¶53(a) — *"Defined requirements and processes to reconcile reports to risk data."*

---

**XDQ-02 — Single Authoritative Counterparty Resolution Across Systems**

*Spans: CDE-01 (Counterparty Identifier), CDE-05 (Business Line), CDE-06 (Geography / Country of Risk), CDE-07 (Industry / Sector Classification)*

- **Dimension:** Uniqueness and consistency
- **Rule intent:** A single real-world counterparty must resolve to exactly one master identifier across all source systems, and the attributes associated with that counterparty (geography, industry, business line attribution) must be consistent across systems. This cannot be expressed per-record on a single CDE: it requires comparing records across multiple source systems and verifying that all carry the same master key and the same attribute values. The failure mode is silent — a counterparty appearing under two different IDs in two systems will cause exposure to be split across two buckets rather than aggregated, and no single-system data quality check will detect it.
- **Measurement:** Count of counterparties in the master register with more than one active identifier across source systems (golden record conflicts); count of counterparties where geography, industry, or business line attribution differs across systems after joining on the master identifier; proportion of cross-system exposure records that join successfully on the master counterparty identifier versus those that fail to join.
- **Suggested threshold:** Zero golden record conflicts in the counterparty master; zero unresolved attribute conflicts for counterparties with material exposure (defined by threshold); join success rate of 100% on in-scope exposure populations.
- **Regulatory grounding:** ¶33 — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; ¶36(d) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; ¶37 — *"data is defined consistently across an organisation."*

---

**XDQ-03 — Manual and EUC Process Population Monitoring**

*Spans: CDE-10 (Source System / Provenance Flag), CDE-03 (Gross Exposure Amount), CDE-09 (Reconciliation Key)*

- **Dimension:** Completeness, accuracy, timeliness
- **Rule intent:** The proportion of risk data — measured by record count and by aggregate exposure value — that originates from manual or EUC processes must be tracked over time and compared against the bank's documented target automation state. This is a cross-cutting requirement because no single CDE carries this information in isolation: it requires joining CDE-10 (which flags the process type) to CDE-03 (to measure the monetary weight of manual data) and CDE-09 (to assess whether manual records are reconcilable to the ledger at the same rate as automated records). Deterioration — an increasing proportion of manual input — is itself a governance signal that ¶39 requires to be documented and explained.
- **Measurement:** Percentage of risk records flagged as manual or EUC origin, by source system and risk type, measured as both record count and percentage of aggregate exposure value; trend over time; reconciliation success rate for manual-flagged records versus automated-feed records.
- **Suggested threshold:** Manual/EUC percentage tracked against documented baseline; any increase above threshold triggers documented escalation per ¶40; reconciliation success rate for manual records must meet the same standard as automated records.
- **Regulatory grounding:** ¶36(b) — *"Where a bank relies on manual processes and desktop applications... it should have effective mitigants in place"*; ¶39 — *"banks to document and explain all of their risk data aggregation processes whether automated or manual... description of their criticality to the accuracy of risk data aggregation and proposed actions to reduce the impact."*

---

## 4. Out of Scope

The following principles impose requirements that a data catalog and CDE/DQ monitoring framework cannot satisfy, or can only partially address. Where a principle also drives a CDE in Section 2, that intersection is explained.

---

**Principle 7 — Accuracy (¶52–56): partially in scope, partially out of scope**

*In scope:* The data accuracy requirements of Principle 7 — reconciliation of reports to risk data (¶53a), validation rules on quantitative information (¶53b), and exception identification (¶53c) — are addressed by CDE-03, CDE-09, and XDQ-01. The existence of a reconciliation key and the monitoring of exposure amount accuracy directly serve ¶53.

*Out of scope:* ¶53(b) requires an *inventory of validation rules* including mathematical and logical relationships verified through checks, and ¶53(c) requires *integrated exception reporting procedures*. These are report-production and risk-system controls, not data catalog metadata. An inventory of validation rules is a risk model and data quality rule library, not a CDE. Exception workflow and escalation channels (¶40, ¶53c) require operational process infrastructure — ticketing systems, escalation procedures, remediation ownership — that a catalog can reference but cannot operationalise.

---

**Principle 8 — Comprehensiveness (¶57–60): partially in scope, partially out of scope**

*In scope:* Principle 8 names specific aggregation dimensions — industry sector, country, single name — that directly drive CDE-07, CDE-06, and CDE-01. It also names limits and risk appetite context, driving CDE-12. These dimensions are in scope because the principle defines what dimensions must be present in the data, not just what must appear in a report.

*Out of scope:* ¶57's requirement that reports cover all significant risk areas, and ¶58–60's requirements for forward-looking forecasts, stress testing results, capital adequacy projections, and emerging risk concentration narratives are *report content and governance* obligations. A catalog can document that the underlying data elements exist, but it cannot enforce that a report *contains* the right analysis, covers the right scope of risk, or includes qualitative interpretation. Whether a board risk report adequately addresses emerging risks is a judgment by the board (¶31, ¶64–65), not a metadata assertion.

---

**Principle 9 — Clarity and Usefulness (¶61–69): out of scope**

Principle 9 addresses the quality of communication in risk reports: appropriate balance of quantitative and qualitative content (¶62), tailoring to the needs of specific recipients (¶63–66), and periodic confirmation with recipients that reports remain relevant (¶69). These are human-judgment and governance-process obligations. ¶67 — *"A bank should develop an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"* — is the one sub-element of Principle 9 that a data catalog directly addresses (this is, essentially, a description of a business glossary). However, whether the resulting reports are *clear and useful* to board members is outside what any technical tool can assess or enforce.

---

**Principle 10 — Frequency (¶70–71): out of scope**

Principle 10 requires the board and senior management to set report production frequency appropriate to each risk type, and to test the ability to produce accurate reports within those timeframes under stress. CDE-08 (Position / As-Of Date) and its timeliness monitoring address the currency of underlying data, but they do not address *report scheduling, SLA governance, or stress-scenario production testing*. The requirement to produce intraday data during stress (¶71) is a system capability and incident-management obligation, not a data element. Whether a bank can produce a complete credit report within four hours during a crisis is a technology and operations matter that a catalog cannot certify.

---

**Principle 11 — Distribution (¶72–74): out of scope**

Principle 11 requires procedures for rapid collection, analysis, and dissemination of risk reports to appropriate recipients while maintaining confidentiality. This is a report distribution, access-control, and information-security governance obligation. A data catalog can document data owners (¶34) and data confidentiality classifications (¶27), and those classifications are a prerequisite for implementing access controls — but whether the right people receive the right reports at the right time, and whether confidentiality is maintained in distribution channels, is an information security and operational process matter that the catalog cannot govern unilaterally.

---

**Principle 1 — Governance (¶27–31): mostly out of scope**

Principle 1 is the overarching governance principle. Its requirements for board approval of the framework (¶28), independent validation of risk data aggregation processes (¶29a), and board awareness of aggregation limitations (¶30–31) are institutional governance and audit obligations. A catalog supports Principle 1 by providing the documentation base — data ownership records per ¶34, metadata per ¶33, provenance flags per ¶39 — that governance and validation activities rely on. But the board approval act, the independent validation programme, and the escalation channels are not things a catalog produces. They use the catalog as evidence; they are not themselves catalog outputs.

---

**Principle 2 — Data Architecture (¶32–35): partially in scope**

¶33 is directly addressed by a data catalog (integrated taxonomies, metadata, single identifiers). ¶34's data ownership and quality responsibility framework is a governance design that the catalog documents but does not create. ¶32's business continuity planning for risk data aggregation is a DR/BCP obligation that is outside catalog scope entirely. ¶35's requirement for risk data aggregation capabilities that simultaneously meet all principles is a system design and testing obligation, not addressable by metadata alone.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | **3** | 2 (¶33), 4 (¶41), 5 (¶46a) | Uniqueness, Completeness, Validity, Timeliness |
| CDE-02 | Legal Entity Identifier (Booking Entity) | **3** | 2 (¶33), 4 (¶41–43), 1 (¶30) | Completeness, Validity, Consistency, Accuracy |
| CDE-03 | Gross Exposure Amount | **3** | 3 (¶36a), 4 (¶41), 7 (¶52), 5 (¶46a,b) | Accuracy, Completeness, Validity, Timeliness |
| CDE-04 | Risk Type Classification | **2** | 4 (¶41–42), 8 (¶57), 2 (¶33) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | **2** | 4 (¶41), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | **2** | 4 (¶41), 6 (¶50), 8 (¶57) | Completeness, Validity, Accuracy |
| CDE-07 | Industry / Sector Classification | **2** | 4 (¶41), 8 (¶57), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-08 | Position / As-Of Date | **3** | 5 (¶44–46), 6 (¶50), 3 (¶36), 7 (¶52–53) | Completeness, Validity, Timeliness |
| CDE-09 | Reconciliation Key (Risk-to-Ledger) | **3** | 3 (¶36c), 7 (¶53a) | Completeness, Validity, Uniqueness, Accuracy |
| CDE-10 | Source System / Provenance Flag | **2** | 3 (¶36b,d), 3 (¶39) | Completeness, Validity, Accuracy, Timeliness |
| CDE-11 | Collateral / Credit Risk Mitigant Identifier | **2** | 4 (¶41), 8 (¶57–58), 3 (¶36a) | Completeness, Validity, Accuracy |
| CDE-12 | Limit / Risk Appetite Threshold | **2** | 8 (¶57–58), 1 (¶28), 9 (¶64) | Accuracy, Completeness, Timeliness, Validity |

*Criticality 3 elements (5): CDE-01, CDE-02, CDE-03, CDE-08, CDE-09. All other elements are criticality 2. No element qualifies as criticality 1: every element in this register, if wrong or missing, degrades an aggregated risk figure or the ability to evidence it — none is purely contextual.*