# BCBS 239 â Data Catalog Governance Interpretation

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a board-level obligation.** The board and senior management must be able to aggregate risk data accurately across the entire banking group â not just in normal conditions but under stress â and must understand the limitations of that aggregation (Â¶30: *"Senior management should be fully aware of and understand the limitations that prevent full risk data aggregation, in terms of coverageâ¦in technical termsâ¦or in legal terms"*).

- **A single, governed data architecture.** Banks must establish *"integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"* (Â¶33). This is the closest the regulation comes to explicitly mandating a data catalog.

- **Accuracy through reconciliation and automation.** Risk data must be reconciled with accounting sources and should flow from a single authoritative source per risk type, with manual processes documented, justified, and controlled (Â¶36(c), Â¶36(d), Â¶39).

- **Completeness across all material exposures and dimensions.** Aggregation must cover all material risk exposures â including off-balance sheet â and must be sliceable by business line, legal entity, asset type, industry, and region (Â¶41, Principle 4 header).

- **Timeliness that scales to stress conditions.** Systems must be capable of producing aggregates rapidly during crisis for critical risks including large credit exposures, counterparty credit risk, trading positions, liquidity indicators, and operational risk indicators (Â¶45, Â¶46).

- **Reports that are reconciled, validated, and traceable.** Risk management reports must be reconciled to underlying risk data; banks must maintain an inventory of validation rules applied to quantitative information and integrated procedures for surfacing data integrity exceptions (Â¶53(a), Â¶53(b), Â¶53(c)).

**Who it applies to**

Principles 1â11 apply directly to Global Systemically Important Banks (G-SIBs), with supervisors encouraged to apply them to other large internationally active banks. The obligations fall on the banking group as a whole â subsidiaries, legal entities, and branches are explicitly in scope for aggregation purposes.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Unique Identifier**

- **Definition:** A system-independent identifier that resolves a single legal counterparty â borrower, issuer, derivative counterparty, or guarantor â across all booking systems, risk engines, and the general ledger. The identifier must be consistent regardless of which business line or legal entity originated the exposure.
- **Why critical:** Without a stable, unique counterparty identifier, exposures cannot be summed to a single name. Large-exposure reporting, concentration risk, and counterparty credit risk aggregation all require this key. Errors here do not merely degrade accuracy â they make the aggregate figure structurally wrong.
- **Risk types:** Credit, counterparty credit risk, concentration
- **Criticality: 3.** *Without this element, the aggregate credit exposure to a single counterparty cannot be computed at all, because exposures held in different systems cannot be matched to the same legal entity â they are counted separately or not at all.* Â¶46(a) and Â¶46(b) name these aggregates explicitly as critical risks.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶41) â completeness across all material exposures; Principle 5 (Â¶46(b)) â counterparty credit risk as a critical risk.
- **Search terms:** counterparty ID, legal entity identifier, LEI, obligor ID, client ID, party key, golden record ID, counterparty master
- **Data quality requirements:**
  - *Uniqueness* â Each legal counterparty maps to exactly one identifier across all source systems; no two distinct legal entities share the same key | Count of counterparty identifiers that resolve to more than one distinct legal entity name in the master reference | Target: 0 duplicates in the golden source
  - *Accuracy* â The identifier matches the authoritative counterparty master (e.g., LEI registry or internal golden source) | Count of exposure records whose counterparty identifier does not resolve in the reference registry | Target: 0 unresolved identifiers in production risk data
  - *Completeness* â Every exposure record carries a non-null, populated counterparty identifier | Count of exposure records with null or missing counterparty identifier | Target: 0% null rate

---

**CDE-02 â Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier for the bank's own legal entity in which an exposure is booked â the subsidiary, branch, or parent â used to consolidate positions at group level and to produce subsidiary-level reports.
- **Why critical:** Group consolidation requires that every exposure is unambiguously attributed to one booking entity. If the booking entity is absent or inconsistent, the bank cannot aggregate up to group level or disaggregate to subsidiary level.
- **Risk types:** Cross-cutting (all risk types; applies to consolidation structure)
- **Criticality: 3.** *Without this element, the aggregate risk exposure at group level cannot be computed at all, because records from subsidiaries cannot be assigned to a node in the consolidation hierarchy â they either double-count or fall out of scope.* Â¶33 requires single identifiers for legal entities; Principle 4 requires aggregation by legal entity.
- **Driven by:** Principle 2 (Â¶33) â *"integrated data taxonomies and architecture across the banking groupâ¦including legal entities"*; Principle 4 (Principle header) â *"capture and aggregate all material risk data across the banking groupâ¦byâ¦legal entity"*.
- **Search terms:** legal entity ID, booking entity, entity code, subsidiary code, branch identifier, group entity hierarchy, legal entity master
- **Data quality requirements:**
  - *Validity* â Booking entity code must exist in the authoritative legal entity hierarchy and be a currently active entity | Count of exposure records with a booking entity code absent from, or flagged inactive in, the entity hierarchy | Target: 0%
  - *Completeness* â Every exposure record is attributed to a booking entity | Count of records with null booking entity | Target: 0%
  - *Consistency* â The booking entity code used in risk systems matches the code used in the general ledger for the same position | Count of positions where booking entity differs between risk system and GL | Target: 0

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary value of an exposure before the application of collateral, netting, or credit risk mitigants â expressed in the transaction currency. This is the primary quantity that risk aggregation sums, averages, or otherwise transforms.
- **Why critical:** This is the number being aggregated. All large-exposure calculations, concentration measures, and credit risk reports are arithmetic functions of this value. An incorrect or missing exposure amount directly invalidates the aggregate.
- **Risk types:** Credit, counterparty credit risk, concentration, market (for position values)
- **Criticality: 3.** *Without this element, the aggregate exposure figure cannot be computed at all, because there is no quantity to sum â the aggregation operation has no input.* This is the most fundamental load-bearing element in any risk aggregate.
- **Driven by:** Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (Â¶41) â *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 5 (Â¶46(a)) â aggregated credit exposure to a large corporate borrower named as a critical risk.
- **Search terms:** exposure at default, EAD, notional amount, outstanding balance, drawn amount, mark-to-market value, fair value, position size, face value, principal outstanding
- **Data quality requirements:**
  - *Accuracy* â Exposure amount reconciles to the general ledger or system of record for the same position | Sum of absolute difference between risk system exposure and GL balance, by asset class | Target: zero unreconciled variance above materiality threshold
  - *Completeness* â Every exposure record carries a non-null, non-zero (where a live position exists) exposure amount | Count of live positions with null or zero exposure amount | Target: 0%
  - *Timeliness* â Exposure amounts reflect the agreed as-of date with no stale values beyond the defined staleness threshold | Count of records whose value timestamp exceeds the defined staleness tolerance for the risk type | Target: 0 stale records at reporting cut

---

**CDE-04 â Position / As-Of Date**

- **Definition:** The business date as of which an exposure or position is stated â the temporal key that defines which snapshot of data constitutes the aggregate. Distinct from system processing timestamps.
- **Why critical:** All aggregates are period-specific. An aggregate that mixes exposures from different as-of dates is not a coherent risk figure. Â¶46 explicitly frames critical risks as point-in-time aggregates ("as of a specified date"). Timeliness obligations under Principle 5 are only measurable if positions carry this date.
- **Risk types:** Cross-cutting
- **Criticality: 3.** *Without this element, the aggregate cannot be computed at all, because there is no coherent snapshot â records from different business dates are indistinguishable, producing a figure that corresponds to no defined point in time.* Â¶50 illustrates ad hoc requests explicitly as "as of a specified date."
- **Driven by:** Principle 5 (Â¶44) â *"produce aggregate risk information on a timely basis"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (Â¶52) â reports must be accurate and precise for decision-making.
- **Search terms:** position date, as-of date, value date, trade date, reporting date, business date, snapshot date, effective date
- **Data quality requirements:**
  - *Validity* â As-of date must be a valid business date, not a future date and not more than one business day prior to the reporting date (for daily risk) | Count of records with an as-of date outside the valid reporting window | Target: 0%
  - *Completeness* â Every exposure record carries a non-null as-of date | Count of records with null as-of date | Target: 0%
  - *Timeliness* â For each risk type, the proportion of positions available as of the agreed cut-off time for that risk type | Count of positions not loaded by the production cut-off, by risk type | Target: measured against SLA thresholds set per risk type per Â¶45

---

**CDE-05 â Risk Type Classification**

- **Definition:** The categorisation of an exposure or position by primary risk type â at minimum: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk. This is the taxonomy that partitions the aggregate population for risk reporting.
- **Why critical:** Risk reports are organised by risk type (Â¶57). Aggregation across business lines, regions, and entities must be risk-type-specific. An exposure miscategorised between credit and market risk will appear in the wrong aggregate and be absent from the correct one.
- **Risk types:** Cross-cutting (classifies all risk types)
- **Criticality: 2.** The gross exposure amount (CDE-03) exists and the aggregate for the whole portfolio can still be summed, but the risk-type-specific aggregate â which is what every report presents â cannot be correctly partitioned. The figure is produced but cannot be trusted by risk type.
- **Driven by:** Principle 4 (Principle header) â *"aggregate all material risk data across the banking groupâ¦as relevant for the risk in question"*; Principle 8 (Â¶57) â *"reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*.
- **Search terms:** risk type, risk category, risk class, risk taxonomy, risk classification, product risk type, asset class
- **Data quality requirements:**
  - *Validity* â Risk type code must belong to the approved enterprise risk taxonomy; non-standard or free-text values are invalid | Count of records with a risk type value not in the approved code list | Target: 0%
  - *Completeness* â Every exposure record carries a risk type classification | Count of records with null risk type | Target: 0%
  - *Consistency* â Risk type classification must be consistent between the originating business system and the consolidated risk data store | Count of positions where risk type differs between source and risk aggregate | Target: 0

---

**CDE-06 â Business Line**

- **Definition:** The internal organisational unit or business segment â retail banking, corporate banking, trading, treasury, etc. â to which an exposure is attributed for management reporting and aggregation.
- **Why critical:** Principles 4 and 6 both explicitly name business line as a required aggregation dimension. Â¶50 illustrates the expectation that aggregates can be produced "across all business lines." Without a governed business line attribute, the bank cannot slice a risk figure by segment, which is a minimum supervisory expectation.
- **Risk types:** Cross-cutting
- **Criticality: 2.** The total portfolio aggregate can be computed, but it cannot be decomposed by business line â the slice required by Principles 4 and 6 is unavailable or unreliable.
- **Driven by:** Principle 4 (Principle header) â *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*.
- **Search terms:** business line, business unit, division, segment, desk, product line, front office unit, reporting segment
- **Data quality requirements:**
  - *Validity* â Business line code must belong to the approved organisational hierarchy | Count of records with business line codes not present in the current organisational master | Target: 0%
  - *Completeness* â Every exposure record carries a business line attribution | Count of records with null business line | Target: 0%
  - *Consistency* â Business line attribution is consistent between risk systems and finance/management reporting systems for the same positions | Count of positions with differing business line across systems | Target: 0

---

**CDE-07 â Geography / Country**

- **Definition:** The country or regional classification of an exposure â typically the country of the counterparty's domicile, country of risk, or booking location, depending on the risk measure. Must be governed with a clear definition of which geographic concept applies.
- **Why critical:** Geography is an explicit aggregation dimension in Principle 4 and is named as an on-demand aggregation scenario in Â¶50. Concentration risk reporting by country â a supervisory stress-testing scenario â depends entirely on this attribute being present and accurate.
- **Risk types:** Credit, market, concentration
- **Criticality: 2.** The total exposure can be computed, but the geographic slice â required for country concentration risk and named in Â¶46(c) for trading â cannot be produced correctly.
- **Driven by:** Principle 4 (Principle header) â *"Data should be available byâ¦region"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*; Principle 5 (Â¶46(c)) â *"market concentrations by sector and region data"* as a critical risk.
- **Search terms:** country of risk, country code, counterparty country, booking country, jurisdiction, region, geographic segment, ISO country code
- **Data quality requirements:**
  - *Validity* â Country codes must conform to ISO 3166-1 alpha-2 (or the bank's approved mapping to it); non-standard codes are invalid | Count of records with country codes absent from the approved reference list | Target: 0%
  - *Completeness* â Every credit and market exposure record carries a country of risk attribution | Count of such records with null country | Target: 0%
  - *Consistency* â Where country of risk and country of booking differ, both must be populated and the distinction documented per the bank's geography policy | Count of records where only one of two required geographic fields is populated | Target: 0

---

**CDE-08 â Industry / Sector Classification**

- **Definition:** The economic sector or industry classification of a counterparty or issuer â typically aligned to a standard taxonomy such as NACE, SIC, GICS, or an internal equivalent. Must be defined at the counterparty level and inherited by exposures.
- **Why critical:** Industry concentration risk is a core reporting dimension. Â¶57 requires reports to include "single name, country and industry sector for credit risk." Â¶50 names industry credit exposures as an explicit ad hoc aggregation scenario. This element drives the industry-level slice of every credit concentration report.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Aggregate exposure to a sector cannot be correctly computed. The total portfolio number is valid, but the sector slice â which is what drives concentration limits and supervisory stress scenarios â is unavailable.
- **Driven by:** Principle 8 (Â¶57) â *"all significant components of those risk areas (eg single name, country and industry sector for credit risk)"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines"*.

  *Note: Principle 8 is partly out of scope (see Section 4), but it directly names industry sector as a data element required to be present in risk data so that reports can include it. That data requirement is within the catalog's remit even though the reporting obligation itself is not.*

- **Search terms:** industry code, sector code, NACE code, SIC code, GICS, industry classification, counterparty sector, obligor industry
- **Data quality requirements:**
  - *Validity* â Industry code must belong to the approved classification scheme; free-text or unmapped codes are invalid | Count of counterparty records with industry codes absent from the reference taxonomy | Target: 0%
  - *Completeness* â Every corporate, financial institution, and sovereign counterparty carries an industry classification | Count of counterparty master records with null industry code, by counterparty segment | Target: 0% for material counterparties
  - *Consistency* â Industry classification is applied at the counterparty master level and inherited consistently by all exposure records for that counterparty | Count of exposure records whose industry code differs from the counterparty master record for the same counterparty | Target: 0

---

**CDE-09 â General Ledger Reconciliation Key**

- **Definition:** The identifier â account number, transaction reference, or GL posting key â that links a risk exposure record to its corresponding entry in the general ledger or the designated system of record for that exposure type. This is not the exposure amount itself; it is the tie-line that allows the amount to be verified.
- **Why critical:** Â¶36(c) states directly that *"risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."* Without a reconciliation key, this obligation is unverifiable â you cannot demonstrate accuracy without being able to join the risk record to the GL entry. This element is the mechanical enabler of Principle 3.
- **Risk types:** Cross-cutting (all risk types that have a GL representation)
- **Criticality: 2.** The aggregate figure may be computed, but its accuracy cannot be evidenced or the reconciliation control cannot be executed. The figure is produced but cannot be certified as reconciled â which is a direct and named regulatory requirement.
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*.
- **Search terms:** GL account reference, transaction ID, journal entry reference, accounting key, source transaction reference, booking reference, trade reference, reconciliation ID
- **Data quality requirements:**
  - *Completeness* â Every on-balance-sheet risk exposure record carries a non-null GL reconciliation key | Count of on-balance-sheet exposure records with null GL reference | Target: 0%
  - *Accuracy* â The GL reconciliation key resolves to an active, matching record in the general ledger for the same position | Count of risk records whose GL key does not match a current GL entry for the equivalent amount and counterparty | Target: 0 unresolved breaks above materiality
  - *Uniqueness* â Each GL reconciliation key maps to one and only one risk record (where one-to-one correspondence is the defined reconciliation basis) | Count of GL keys appearing on more than one risk record where one-to-one mapping is expected | Target: 0

---

**CDE-10 â Source System / Provenance Flag**

- **Definition:** The identifier of the originating system from which a risk record was sourced â for example, the trade capture system, the loan origination system, or a treasury system â together with a flag indicating whether the record was loaded automatically from that system or introduced via a manual process or end-user computing tool (spreadsheet, database outside the governed infrastructure).
- **Why critical:** Â¶36(d) requires banks to *"strive towards a single authoritative source for risk data per each type of risk."* Â¶39 requires documentation of all manual workarounds and their criticality. Without source system provenance, the bank cannot: (a) demonstrate that data came from the authoritative source; (b) identify the population of manually sourced records; (c) execute the governance controls that manual processes require. In a catalog, this is the element that makes lineage assertions verifiable rather than asserted.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Aggregates can be produced, but the bank cannot verify that the input population came from authoritative sources, cannot scope its manual-process controls, and cannot produce the documentation Â¶39 requires. The figure is produced but its provenance cannot be attested â which degrades the assurance that Principle 3 demands.
- **Driven by:** Principle 3 (Â¶36(d)) â *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (Â¶39) â *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*; Principle 1 (Â¶29(a)) â full documentation and independent validation of aggregation processes.
- **Search terms:** source system ID, feed name, data source code, EUC flag, manual override flag, system of record, data lineage tag, feed identifier, upload type
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a non-null source system identifier and a non-null automated/manual flag | Count of records with null source system ID or null process type flag | Target: 0%
  - *Validity* â Source system code must belong to the approved system registry; unregistered source codes indicate ungoverned data entry points | Count of records with source system codes absent from the system inventory | Target: 0%
  - *Accuracy* â For records flagged as automated, verify that the record was loaded within the expected automated feed window; outliers suggest manual substitution not flagged as such | Count of records flagged automated but loaded outside the automated feed window | Target: 0

---

**CDE-11 â Transaction / Instrument Currency**

- **Definition:** The ISO 4217 currency code in which the exposure or position is denominated, prior to any translation to the reporting currency.
- **Why critical:** Multi-currency portfolios require foreign-exchange translation before amounts can be aggregated in a common reporting currency (Â¶42 acknowledges different metrics but requires aggregation capabilities to be equivalent). A missing or incorrect currency code means the wrong exchange rate is applied â or no translation occurs â producing a materially incorrect aggregated exposure figure. Currency is structurally required for any bank with cross-border activity.
- **Risk types:** Credit, market, liquidity, counterparty credit risk
- **Criticality: 2.** The local-currency exposure amount exists (CDE-03), but the translated aggregate figure is wrong or cannot be produced. The aggregate is not invalid in the sense that it cannot be computed at all â it can be computed with an incorrect rate â but the resulting figure cannot be trusted. Translation accuracy depends entirely on currency being correct.
- **Driven by:** Principle 4 (Â¶42) â *"risk data aggregation capabilities should be the same regardless of the choice of risk aggregation systems"* and the requirement to aggregate across business lines and regions implicitly requires a common currency; Principle 3 (Â¶36(a)) â controls on risk data as robust as accounting data (accounting always governs transaction currency).
- **Search terms:** transaction currency, currency code, ISO currency, denomination, base currency, deal currency, FX currency
- **Data quality requirements:**
  - *Validity* â Currency code must be a valid, active ISO 4217 three-letter code | Count of records with currency codes not in the approved ISO 4217 reference list | Target: 0%
  - *Completeness* â Every monetary exposure record carries a non-null currency code | Count of records with null currency code | Target: 0%
  - *Consistency* â Currency code on the risk record matches the currency code on the originating trade or loan record in the source system | Count of records where risk system currency differs from source system currency for the same instrument | Target: 0

---

**CDE-12 â Limit / Risk Appetite Threshold Reference**

- **Definition:** The identifier linking an exposure or aggregated position to the applicable limit â large exposure limit, concentration limit, counterparty limit, or VaR limit â against which the exposure is measured for compliance and breach reporting.
- **Why critical:** Â¶58 requires reports to *"provide information in the context of limits and risk appetite/tolerance."* Without the link from an exposure to its applicable limit, the bank cannot produce utilisation figures, cannot identify breaches, and cannot report on adherence to risk appetite â all of which are named reporting obligations.
- **Risk types:** Credit, market, counterparty credit risk, concentration
- **Criticality: 2.** Gross exposure figures exist, but limit utilisation â the ratio that triggers management action and appears in board risk reports â cannot be computed or presented. Principle 8's report-content obligation cannot be met at the data level.
- **Driven by:** Principle 8 (Â¶58) â *"Reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance"*; Principle 5 (Â¶46(c)) â *"trading exposures, positions, operating limits"* as a critical risk category.

  *Note: Principle 8 is partly out of scope (see Section 4), but as with industry sector (CDE-08), the data element â the limit reference â is within the catalog's remit even where the reporting obligation is not.*

- **Search terms:** limit ID, limit reference, risk appetite threshold ID, limit framework code, concentration limit key, counterparty limit identifier, limit register reference
- **Data quality requirements:**
  - *Completeness* â Every material aggregated exposure is linked to at least one applicable limit identifier | Count of material aggregated positions with no limit reference | Target: 0%
  - *Validity* â Limit identifier must resolve to an active, board-approved limit in the limit management system | Count of limit references that do not match a current active record in the limit register | Target: 0%
  - *Timeliness* â Limit utilisation is recalculated within the frequency required for that risk type (intraday for trading, daily for large exposures) | Count of material limit positions whose utilisation calculation is older than the prescribed refresh frequency | Target: 0 breaches of the SLA

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Counterparty identity resolution across source systems**

- **Spans:** CDE-01 (Counterparty Unique Identifier), CDE-03 (Gross Exposure Amount), CDE-06 (Business Line), CDE-07 (Geography), CDE-08 (Industry / Sector)
- **What this is:** The requirement to verify that the same legal counterparty is represented by the same identifier across every system that contributes exposures to the group aggregate. This is not a property of any single element â it is a cross-system matching requirement. A counterparty that exists as three different identifiers in three booking systems will produce three separate aggregate lines rather than one, splitting the true exposure. No per-element check on CDE-01 alone can detect this fragmentation; it requires a cross-system reconciliation of the counterparty master.
- **Regulatory basis:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties"*; Principle 4 â completeness of aggregation across the banking group; Principle 5 (Â¶46(a)) â aggregated credit exposure to a large corporate borrower as a critical risk.
- **Dimension:** Uniqueness, Consistency
- **Rule intent:** Every distinct legal counterparty is represented by exactly one identifier value in every contributing system. Where system-native IDs differ, a cross-reference to the enterprise counterparty master exists and is maintained.
- **Measurement:** (a) Count of counterparty identifiers in each source system that cannot be matched to a record in the enterprise counterparty master; (b) Count of enterprise counterparty master records that match to more than one source-system identifier in the same contributing system; (c) Comparison of total aggregate exposure per counterparty computed from the enterprise master versus computed from each individual system, with unexplained variance flagged as a reconciliation break.
- **Suggested threshold:** Zero unmatched source identifiers for counterparties with exposure above the materiality threshold; zero unexplained aggregate variance above the bank's defined materiality level.

---

**XDQ-02 â Risk-to-finance reconciliation completeness**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key), CDE-10 (Source System / Provenance Flag), CDE-01 (Counterparty Unique Identifier), CDE-02 (Legal Entity Identifier)
- **What this is:** The requirement to verify that the population of risk records and the population of general ledger entries for on-balance-sheet items are mutually consistent â that no material position exists in the GL without a corresponding risk record, and no material risk record lacks a GL anchor. This is a population-level completeness check, not a field-level check on any individual CDE. A risk system may have all fields populated and still be missing positions relative to the GL; a GL may carry balances with no matching risk record. Only a joined population comparison can detect this.
- **Regulatory basis:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*; Principle 3 (Â¶40) â *"banks to measure and monitor the accuracy of data and to develop appropriate escalation channels."*
- **Dimension:** Completeness, Accuracy, Consistency
- **Rule intent:** The sum of on-balance-sheet exposures in the risk data store reconciles to the sum of corresponding balances in the general ledger, at the level of legal entity and risk type, within the defined materiality tolerance. Every break is identified, assigned a root cause (timing, classification difference, genuine error), and tracked to resolution.
- **Measurement:** (a) Sum of gross exposure in risk system versus sum of GL balance, by legal entity and risk type â absolute and percentage variance; (b) Count of GL positions with no matching risk record above the materiality threshold; (c) Count of risk records above the materiality threshold with no matching GL reconciliation key; (d) Age of unresolved reconciliation breaks in business days.
- **Suggested threshold:** Aggregate variance within the bank's defined accounting materiality threshold; zero unresolved breaks older than two business days for material positions; 100% of breaks above materiality assigned a root cause within one business day.

---

## 4. Out of Scope

The following obligations in Principles 1â11 cannot be addressed by a data catalog, CDE registers, or data quality monitoring. Stating this is not a limitation of the analysis â it is the honest boundary of what catalog governance can do.

---

**Principle 1 â Governance (Â¶27â31): Board and senior management accountability**

The catalog supports Principle 1 by holding documentation, ownership assignments, and validation records. It cannot enforce board approval of the risk data framework (Â¶28), ensure senior management understands aggregation limitations (Â¶30), or guarantee that independent validation is resourced with "specific IT, data and reporting expertise" (Â¶29(a)). These are organisational and governance obligations that require policy frameworks, committee structures, and audit programs â not data management tools.

---

**Principle 2 â Data architecture (Â¶32â35): Business continuity and IT resilience**

Principle 2 drives CDE design directly â Â¶33's requirement for single identifiers and unified naming conventions is the primary mandate for CDEs 01, 02, and the data architecture underlying the entire register. That data-element obligation is within scope. What the catalog cannot address is Â¶32's requirement that risk data aggregation be subject to a business impact analysis and integrated into business continuity planning. System resilience, recovery time objectives, and stress-scenario infrastructure capacity are IT and operational risk matters outside the catalog's remit.

---

**Principles 8â11 â Reporting practices (Â¶57â73): Report content, clarity, frequency, and distribution**

These principles describe what risk management reports must contain and how they must be delivered to the board and senior management. The catalog can ensure that the data inputs to those reports (the CDEs above) are accurate, complete, and traceable. It cannot govern:

- **Principle 8 (Â¶57â60):** Whether reports cover all material risk areas, include forward-looking forecasts, stress test results, or capital adequacy projections. These are report-design and governance obligations. *Exception noted:* Â¶57 names industry sector and Â¶58 names limit/risk appetite as required report content â those data elements (CDE-08 and CDE-12) are within scope. The reporting obligation â whether the content of the report itself is comprehensive â is not.
- **Principle 9 (Â¶61â69):** Whether reports present the right balance of qualitative and quantitative information, are tailored to recipients, or are periodically confirmed as relevant by the board (Â¶69). Â¶67's requirement for an "inventory and classification of risk data items" is partially addressable by the catalog's business glossary; the broader clarity and usefulness obligations are not.
- **Principle 10 (Â¶70â71):** Report production frequency and stress/crisis escalation of report cadence. The catalog does not control when reports are run, who receives them, or whether the bank can produce them within intraday timeframes. These are operational and system-capacity requirements.
- **Principle 11 (Â¶72â73):** Report distribution, access control, and confidentiality in dissemination. These are report-delivery and information-security obligations.

---

**Principle 3 â Manual process risk (Â¶38â39): Judgement and human intervention**

Â¶38 acknowledges that professional judgement requires human intervention and that this is appropriate. Â¶39 requires banks to document and justify all manual workarounds. CDE-10 (Source System / Provenance Flag) captures the population of manually sourced records and makes the documentation obligation executable. What the catalog cannot do is assess whether a specific manual judgement is appropriate, whether the workaround is correctly described, or whether the proposed remediation actions are credible. That is an audit and risk-management assessment function.

---

**Principle 5 â Timeliness in stress (Â¶45â46): System production capacity**

CDE-04 (Position / As-Of Date) enables measurement of whether data is timely. The catalog cannot guarantee that underlying systems produce data within required windows under stress, that infrastructure scales to intraday demands (Â¶71), or that the bank's technology architecture is capable of rapid aggregation. Timeliness monitoring in the catalog tells you when the SLA was breached; fixing that breach is a system architecture and operations matter.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Unique Identifier | 3 | 2 (Â¶33), 4 (Â¶41), 5 (Â¶46b) | Uniqueness, Accuracy, Completeness |
| CDE-02 | Legal Entity Identifier (Booking Entity) | 3 | 2 (Â¶33), 4 (header) | Validity, Completeness, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3 (Â¶36a), 4 (Â¶41), 5 (Â¶46a) | Accuracy, Completeness, Timeliness |
| CDE-04 | Position / As-Of Date | 3 | 5 (Â¶44â45), 6 (Â¶50), 7 (Â¶52) | Validity, Completeness, Timeliness |
| CDE-05 | Risk Type Classification | 2 | 4 (header), 8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-06 | Business Line | 2 | 4 (header), 6 (Â¶50) | Validity, Completeness, Consistency |
| CDE-07 | Geography / Country | 2 | 4 (header), 5 (Â¶46c), 6 (Â¶50) | Validity, Completeness, Consistency |
| CDE-08 | Industry / Sector Classification | 2 | 8 (Â¶57), 6 (Â¶50) | Validity, Completeness, Consistency |
| CDE-09 | GL Reconciliation Key | 2 | 3 (Â¶36c), 7 (Â¶53a) | Completeness, Accuracy, Uniqueness |
| CDE-10 | Source System / Provenance Flag | 2 | 3 (Â¶36d), 3 (Â¶39), 1 (Â¶29a) | Completeness, Validity, Accuracy |
| CDE-11 | Transaction / Instrument Currency | 2 | 4 (Â¶42), 3 (Â¶36a) | Validity, Completeness, Consistency |
| CDE-12 | Limit / Risk Appetite Threshold Reference | 2 | 8 (Â¶58), 5 (Â¶46c) | Completeness, Validity, Timeliness |