# BCBS 239 â Data Catalog Governance Analysis

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation at group level.** Banks must capture and aggregate all material risk exposures across legal entities, business lines and geographies â not just in normal conditions but under stress â so that management and the board can make decisions on sound information. (Principle 4, Â¶41â43: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*)

- **Accuracy and integrity of risk data.** Risk data must be reconciled to authoritative sources including accounting data, with a single authoritative source per risk type and controls as robust as those applied to accounting figures. (Principle 3, Â¶36(c)â(d): *"Risk data should be reconciled with bank's sources, including accounting data where appropriateâ¦ A bank should strive towards a single authoritative source for risk data per each type of risk."*)

- **Timeliness proportionate to risk volatility.** Aggregate risk figures must be producible rapidly â including intraday for critical exposures â with speed requirements escalating during stress. (Principle 5, Â¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*)

- **Governed data architecture with documented metadata.** Banks must maintain integrated data taxonomies, unified naming conventions, and documented metadata across the group; roles and data ownership must be formally assigned. (Principle 2, Â¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*)

- **Documented, validated, and auditable processes.** All aggregation processes â automated and manual â must be documented, subject to independent validation, and manual workarounds must be explained and tracked for remediation. (Principle 3, Â¶39: *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manualâ¦ Documentation should include an explanation of the appropriateness of any manual workarounds."*)

- **Accurate risk reporting reconciled to data.** Risk reports must be reconciled back to the underlying data, with defined processes, edit checks, and exception reporting to identify and explain data errors before they reach decision-makers. (Principle 7, Â¶53(a): *"Defined requirements and processes to reconcile reports to risk data."*)

**Who it applies to**

BCBS 239 was initially directed at Global Systemically Important Banks (G-SIBs) with a compliance deadline of January 2016. The Basel Committee subsequently recommended that national supervisors extend these principles to Domestic Systemically Important Banks (D-SIBs) and, over time, to other supervised institutions of significant size or interconnectedness. In practice, many mid-tier internationally active banks treat these principles as binding expectations from their home supervisors.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Unique Identifier**

- **Definition:** A single, persistent, system-independent identifier assigned to each legal-entity counterparty (borrower, issuer, derivatives counterparty, guarantor) that resolves to the same counterparty record regardless of which booking system, business line, or geography originates the exposure. May be an internal golden-record ID or a recognised external standard such as the Legal Entity Identifier (LEI).
- **Why critical:** Without a single key that resolves across systems, exposures to the same counterparty cannot be summed. A bank cannot know its total credit exposure to a single name, making concentration measurement impossible and making the aggregate credit exposure figure structurally invalid.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality:** **3** â *"Without this element, the aggregate total credit exposure to counterparty X cannot be computed at all, because records in different booking systems cannot be matched to a single obligor."* The figure is not merely less accurate; it literally cannot be formed.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 5 (Â¶46(a)â(b)) â aggregated credit exposure to a large corporate borrower and counterparty credit risk exposures named as critical risks
- **Search terms:** counterparty ID, obligor ID, legal entity identifier, LEI, customer golden record, party key, entity reference, counterparty master
- **Data quality requirements:**
  - *Uniqueness* â Each active counterparty is represented by exactly one identifier in the enterprise reference data store | Count of duplicate identifier values mapped to more than one counterparty golden record | Target: 0 duplicates
  - *Completeness* â Every exposure record carries a non-null, populated counterparty identifier | Percentage of exposure records with null or blank counterparty identifier | Target: <0.1%
  - *Validity* â Every counterparty identifier on an exposure record resolves to an active record in the counterparty reference data store | Count of exposure records whose counterparty identifier has no matching entry in the reference table | Target: 0 unmatched
  - *Consistency* â The same counterparty carries the same identifier across all source booking systems | Count of counterparty names that map to more than one active identifier across systems | Target: 0

---

**CDE-02 â Legal Entity Identifier (Own Entity / Booking Entity)**

- **Definition:** The identifier of the bank's own legal entity in which a transaction is booked â i.e., the subsidiary, branch, or holding company that is the originating party to the exposure. Distinct from the counterparty identifier (CDE-01), which identifies the external obligor.
- **Why critical:** Group-level consolidation and subsidiary-level reporting both depend on knowing which legal entity holds each exposure. Without it, neither the group aggregate nor the legal-entity sub-aggregate can be correctly partitioned, making both figures invalid for the purposes of consolidated risk reporting.
- **Risk types:** Cross-cutting (credit, market, liquidity â any risk aggregated at group or subsidiary level)
- **Criticality:** **3** â *"Without this element, the aggregated risk exposure at group level cannot be computed at all, because individual exposure records cannot be assigned to â or excluded from â the relevant consolidation perimeter."*
- **Driven by:** Principle 4 (Â¶41) â *"A bank's risk data aggregation capabilities should include all material risk exposures"* across the banking group; Principle 2 (Â¶33) â *"integrated data taxonomies and architecture across the banking groupâ¦ including legal entities"*
- **Search terms:** booking entity, legal entity code, entity identifier, subsidiary code, branch identifier, consolidation entity, legal vehicle, booking location
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null booking entity identifier | Percentage of exposure records with null booking entity | Target: 0%
  - *Validity* â Every booking entity identifier resolves to an entity within the approved consolidation perimeter | Count of identifiers that do not match the active legal entity hierarchy | Target: 0
  - *Consistency* â The legal entity hierarchy used in risk systems matches the hierarchy used in the general ledger for consolidation | Count of legal entity nodes present in one hierarchy but absent in the other | Target: 0

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary amount representing the bank's gross risk exposure to a counterparty or instrument before the application of credit risk mitigants (collateral, netting, guarantees). Denominated in transaction currency, with a corresponding base-currency equivalent. Covers on- and off-balance-sheet positions.
- **Why critical:** This is the primary numerical quantity that risk aggregation sums. Without it, no aggregate risk figure â total credit exposure, concentration measure, capital requirement input â can be computed. Off-balance-sheet coverage is explicitly required (Â¶41).
- **Risk types:** Credit, counterparty, concentration
- **Criticality:** **3** â *"Without this element, the aggregate credit exposure figure cannot be computed at all, because there is no monetary quantity to sum."*
- **Driven by:** Principle 4 (Â¶41) â *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*
- **Search terms:** exposure at default, EAD, gross exposure, outstanding balance, notional amount, drawn amount, commitment amount, off-balance-sheet exposure, mark-to-market value
- **Data quality requirements:**
  - *Accuracy* â Exposure amounts reconcile to the general ledger or trade system of record within agreed materiality tolerance | Aggregate variance between risk system exposure total and ledger balance by asset class | Target: variance â¤ defined materiality threshold per asset class
  - *Completeness* â All on- and off-balance-sheet exposure records carry a non-null, non-zero gross amount | Percentage of exposure records with null or zero amount where a position is known to exist | Target: 0%
  - *Validity* â Exposure amounts are expressed in a valid ISO 4217 transaction currency and a populated base-currency equivalent exists | Count of records with invalid currency code or null base-currency equivalent | Target: 0
  - *Timeliness* â Exposure amounts reflect the current position as of the stated as-of date without stale carry-forwards | Count of exposure records whose last-updated timestamp precedes the as-of date by more than the agreed settlement lag | Target: 0 for critical risk types

---

**CDE-04 â Risk Classification / Risk Type Code**

- **Definition:** The categorical label that assigns each exposure or position to a primary risk type (credit risk, market risk, liquidity risk, operational risk, counterparty credit risk) and, where applicable, a sub-classification (e.g., drawn versus contingent for credit; trading versus banking book for market risk). This is the field that partitions the universe of exposures into the taxonomic buckets that risk aggregation operates on.
- **Why critical:** Aggregation by risk type is the foundational slice of every risk report. An exposure coded to the wrong risk type will appear in the wrong aggregate and be absent from the correct one; no validation or reconciliation step downstream can detect this without reference to the code itself.
- **Risk types:** Cross-cutting
- **Criticality:** **2** â The aggregate total for each risk type is produced, but it is produced incorrectly: exposures are in the wrong bucket. The figure exists but cannot be trusted for any specific risk type. This is degradation, not invalidity of the aggregation mechanism itself, so 2 applies.
- **Driven by:** Principle 8 (Â¶57) â *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 2 (Â¶33) â *"integrated data taxonomies and architecture"*; Principle 4 (Â¶41â42)
- **Search terms:** risk type, risk category, risk class, asset class, book type, trading/banking book flag, risk taxonomy code, risk bucket
- **Data quality requirements:**
  - *Validity* â Every exposure record carries a risk type code drawn from the approved enterprise risk taxonomy | Count of records with a risk type code not present in the approved taxonomy reference list | Target: 0
  - *Completeness* â No exposure record has a null risk type code | Percentage of exposure records with null risk type | Target: 0%
  - *Consistency* â Risk type classifications applied in risk systems match those used in regulatory capital calculation engines | Count of instruments classified differently between the risk system and the capital calculation system | Target: 0; all discrepancies explained

---

**CDE-05 â Business Line**

- **Definition:** The internal business line, division, or desk to which an exposure or position is attributed. This is the organisational dimension along which business-line sub-aggregates are produced (e.g., Corporate Banking, Trading, Retail, Private Banking).
- **Why critical:** Principle 4 explicitly names business line as a required dimension for risk data availability. Without it, the bank cannot produce sub-aggregates by business line and cannot identify concentrations within a line. It also supports limits monitoring, which Principle 8 (Â¶58) requires.
- **Risk types:** Cross-cutting
- **Criticality:** **2** â The group-level aggregate is valid, but the business-line sub-aggregate cannot be produced. Supervisors and senior management cannot assess concentrations or limits adherence by line.
- **Driven by:** Principle 4 (Â¶41) and its header statement â *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (Â¶50) â *"aggregate risk data quicklyâ¦ across all business lines and geographic areas"*
- **Search terms:** business line, business unit, division code, desk code, product line, segment, front-office unit, P&L centre
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null business line code | Percentage of records with null business line | Target: <0.5%
  - *Validity* â Business line codes resolve to nodes in the current approved organisational hierarchy | Count of records carrying a decommissioned or unrecognised business line code | Target: 0
  - *Consistency* â Business line attribution in risk systems matches attribution in management accounting | Count of instruments attributed to a different business line in risk versus management accounts | Investigated and explained

---

**CDE-06 â Country / Geography Code**

- **Definition:** The country (or broader geographic region) of risk associated with an exposure â typically the country of the obligor's domicile or the country of the underlying collateral or asset. Distinct from the booking location (which is captured by CDE-02). This is the geography dimension used for country concentration and cross-border risk reporting.
- **Why critical:** Principle 4 names region as a required aggregation dimension. Principle 6 (Â¶50) gives the specific supervisory example of aggregating country credit exposures on demand. Without it, country concentration cannot be measured and cross-border stress scenarios cannot be run.
- **Risk types:** Credit, market, concentration
- **Criticality:** **2** â The total aggregate is valid, but the country sub-aggregate and any country-based stress scenario cannot be produced. The figure that degrades is country credit concentration.
- **Driven by:** Principle 4 header â *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (Â¶50) â *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date"*
- **Search terms:** country of risk, country code, counterparty country, obligor domicile, ISO 3166 country code, geographic region, jurisdiction, country of incorporation
- **Data quality requirements:**
  - *Completeness* â Every credit exposure record carries a non-null country-of-risk code | Percentage of credit exposure records with null country code | Target: <0.5%
  - *Validity* â Country codes conform to ISO 3166-1 alpha-2 or the bank's approved geographic hierarchy | Count of non-conforming country codes | Target: 0
  - *Consistency* â Country-of-risk assignment uses a consistent methodology (e.g., ultimate risk basis) across all business lines and systems | Documentation of methodology; count of exceptions where methodology differs across systems | Qualitative review plus zero unexplained exceptions

---

**CDE-07 â Industry / Sector Code**

- **Definition:** The industry or economic sector classification of the counterparty or the underlying asset, using a standard scheme (e.g., NACE, GICS, SIC, or an internal equivalent). This is the sector dimension used to detect and report industry concentration risk.
- **Why critical:** Principle 4 names industry as an explicit aggregation dimension. Principle 8 (Â¶57) requires reports to include single-name, country, and industry sector for credit risk. Without it, sector concentration cannot be computed and the comprehensive credit risk report mandated by Principle 8 cannot be produced.
- **Risk types:** Credit, concentration
- **Criticality:** **2** â The aggregate total credit exposure is valid, but the sector sub-aggregate cannot be produced and sector concentrations cannot be identified, which is a specific reporting requirement under Principle 8. This is a reporting-completeness degradation.
- **Driven by:** Principle 4 header â *"Data should be available byâ¦ industryâ¦ and other groupings"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*
- **Search terms:** industry code, sector code, NACE code, GICS sector, SIC code, industry classification, obligor sector, borrower industry
- **Data quality requirements:**
  - *Completeness* â Every credit exposure record with a non-retail counterparty carries a non-null industry code | Percentage of wholesale credit records with null industry code | Target: <1%
  - *Validity* â Industry codes belong to the approved classification scheme and version | Count of codes not matching the active scheme | Target: 0
  - *Timeliness* â Industry codes are reviewed and updated when a counterparty undergoes a material change of business | Percentage of counterparty records not reviewed within the defined review cycle | Monitored against the defined cycle

---

**CDE-08 â As-Of / Position Date**

- **Definition:** The business date as of which an exposure or position is stated â the temporal anchor for every risk aggregate. This is the date that defines which records constitute a valid snapshot for a given reporting cycle, distinguishing today's position from yesterday's carry-forward.
- **Why critical:** Every risk aggregate is stated "as of" a date. Without this field, it is impossible to know which records belong to a reporting snapshot, meaning the aggregate cannot be constructed for any specific point in time. Any figure produced would be a meaningless blend of multiple dates.
- **Risk types:** Cross-cutting
- **Criticality:** **3** â *"Without this element, the aggregate risk exposure as of date T cannot be computed at all, because there is no basis on which to select the correct population of exposure records for that reporting period."*
- **Driven by:** Principle 5 (Â¶44â45) â timeliness of aggregate risk information; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (Â¶53(a)) â reconciliation of reports to risk data requires a shared temporal reference
- **Search terms:** as-of date, position date, value date, trade date, reporting date, snapshot date, effective date, reference date
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null as-of date | Percentage of records with null as-of date | Target: 0%
  - *Validity* â As-of dates are valid calendar dates and fall within the expected reporting calendar | Count of records with as-of dates outside the valid reporting calendar or in the future relative to the report run timestamp | Target: 0
  - *Timeliness* â The maximum lag between the as-of date and the availability of aggregated data for that date meets the bank's agreed production schedule | Measured as hours/days elapsed from close of business on the as-of date to data availability in the aggregation layer | Target: within agreed SLA per risk type (Principle 5)
  - *Consistency* â The same as-of date is used consistently across all source systems contributing to a given reporting snapshot | Count of source systems contributing records with a different as-of date to the declared reporting snapshot | Target: 0; discrepancies investigated

---

**CDE-09 â General Ledger / Source System Reconciliation Key**

- **Definition:** The identifier that links each risk record to its corresponding entry (or set of entries) in the general ledger or in the system of record for that transaction type (e.g., the loan origination system, the trade capture system). This key is the mechanism by which risk data accuracy is evidenced by reconciliation to the accounting record.
- **Why critical:** Â¶36(c) mandates reconciliation of risk data to accounting data. Without a linkage key, reconciliation is impossible at the individual-record level; it can only be performed at aggregate totals, which cannot isolate discrepancies. The accuracy assertion required by Principle 3 cannot be made without it.
- **Risk types:** Cross-cutting (accuracy and integrity across all risk types)
- **Criticality:** **2** â Aggregate risk figures are produced, but they cannot be reconciled to the general ledger or system of record. The accuracy and integrity assertion required by Principle 3 is unsupported. This is a controls degradation rather than an inability to compute the figure.
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** GL reference, ledger entry ID, trade reference number, deal ID, loan ID, account number, source system key, transaction reference, booking reference, primary key from source
- **Data quality requirements:**
  - *Completeness* â Every risk exposure record carries a non-null reconciliation key linking it to a general ledger entry or system-of-record transaction | Percentage of records with null reconciliation key | Target: <0.5% (with exceptions documented)
  - *Validity* â Every reconciliation key on a risk record resolves to an existing, active record in the designated general ledger or source system | Count of unmatched reconciliation keys | Target: 0 unexplained; all breaks logged as reconciliation exceptions
  - *Accuracy* â The sum of exposure amounts by reconciliation key agrees to the corresponding general ledger balance within defined materiality | Aggregate variance by portfolio between risk system and GL, reported as a reconciliation break | Target: within agreed materiality threshold; all breaks investigated and explained

---

**CDE-10 â Source System / Data Provenance Flag**

- **Definition:** The attribute(s) identifying the originating source system for each risk record, and a flag indicating whether the record was produced by an automated feed or by manual/end-user-computing (EUC) input (e.g., a spreadsheet, manual journal, or desktop database). This is the lineage marker required to implement the controls in Â¶36(b) and Â¶39.
- **Why critical:** The regulation treats manual and EUC-sourced data as a distinct control risk requiring documented mitigants. Without provenance metadata, a bank cannot demonstrate compliance with Â¶36(b) (EUC policies), cannot quantify reliance on manual processes, and cannot prioritise automation remediation. Reports that blend automated and manual data without identification are specifically flagged as a risk by Â¶39.
- **Risk types:** Cross-cutting (governance and operational integrity across all risk types)
- **Criticality:** **2** â Aggregate figures are produced, but the bank cannot demonstrate which portion rests on manual/EUC sources, cannot evidence compliance with Â¶36(b) controls, and cannot satisfy the documentation requirement of Â¶39. Independent validation and supervisor review will find a gap in evidencing accuracy.
- **Driven by:** Principle 3 (Â¶36(b)) â *"Where a bank relies on manual processes and desktop applicationsâ¦ it should have effective mitigants in placeâ¦ consistently applied"*; Principle 3 (Â¶39) â *"banks to document and explain all of their risk data aggregation processes whether automated or manualâ¦ Documentation should include an explanation of the appropriateness of any manual workarounds"*; Principle 3 (Â¶36(d)) â single authoritative source per risk type
- **Search terms:** source system, system of origin, source system code, data source flag, manual override flag, EUC flag, end-user computing indicator, spreadsheet indicator, data feed type, automated vs. manual indicator, provenance tag
- **Data quality requirements:**
  - *Completeness* â Every risk exposure record carries a non-null source system identifier and a populated automated/manual flag | Percentage of records with null source system or null manual/EUC flag | Target: 0%
  - *Validity* â Source system codes resolve to entries in the approved system inventory/data source register | Count of records carrying an unregistered source system code | Target: 0
  - *Accuracy* â The volume of EUC-sourced records is measured and tracked against the bank's target for reducing manual reliance, per the remediation plan required by Â¶39 | Percentage of total exposure records flagged as EUC or manual origin, trended over time | Monitored against approved remediation plan targets

---

**CDE-11 â Net Exposure / Post-Mitigation Exposure Amount**

- **Definition:** The monetary exposure remaining after the application of recognised credit risk mitigants: netting agreements, financial collateral, and guarantees. This is the figure that drives regulatory capital calculations and concentration limit consumption for credit and counterparty risk.
- **Why critical:** Capital adequacy and limit utilisation figures are built from net exposure, not gross. If net exposure is wrong, the capital ratio and limit headroom reported to the board are wrong. It is distinct from CDE-03 because the transformation from gross to net is where errors in collateral valuation and netting eligibility materialise.
- **Risk types:** Credit, counterparty, concentration
- **Criticality:** **2** â The gross aggregate (CDE-03) is valid, but the net exposure figure used in capital and limits reporting is incorrect. Specifically, the limit utilisation and capital ratio reported to the board under Principle 8 (Â¶58) are wrong. The figure is produced but cannot be trusted for regulatory capital or limits purposes.
- **Driven by:** Principle 8 (Â¶58) â *"provide information in the context of limits and risk appetite/tolerance"*; Principle 4 (Â¶41) â completeness including off-balance-sheet; Principle 7 (Â¶54) â accuracy of approximations including model-driven figures
- **Search terms:** net exposure, EAD post-mitigation, credit risk mitigant, collateral-adjusted exposure, post-netting exposure, net credit exposure, RWA driver, netting benefit, collateral haircut
- **Data quality requirements:**
  - *Accuracy* â Net exposure equals gross exposure minus recognised mitigants, where mitigant eligibility has been validated | Count of records where net exposure exceeds gross exposure without a documented explanation (e.g., over-collateralisation treated correctly) | Target: 0 unexplained exceptions
  - *Completeness* â Every record for which a netting agreement or collateral agreement exists carries a populated net exposure amount | Percentage of counterparties with a recognised netting agreement where net exposure is null | Target: 0%
  - *Validity* â Collateral values used in mitigation are sourced from the current valuation date consistent with CDE-08 | Count of records using collateral values with a valuation date older than the agreed staleness threshold | Target: 0

---

**CDE-12 â Liquidity Risk Indicator (Cash Flow / Contractual Maturity Date)**

- **Definition:** For each instrument, the contractual maturity date (for balance-sheet positions) or the next contractual cash flow date (for both on- and off-balance-sheet items). This feeds liquidity gap analysis and cash flow projections across the maturity ladder.
- **Why critical:** Principle 5 (Â¶46(d)) names liquidity risk indicators including cash flows and settlements as a critical risk type requiring rapid aggregation. Without maturity/cash flow dates, the maturity ladder cannot be constructed and the liquidity coverage ratio and net stable funding position cannot be computed for any given time bucket.
- **Risk types:** Liquidity
- **Criticality:** **2** â Liquidity aggregate totals can be computed at a point in time, but the time-bucket distribution â which is the essential output of liquidity risk management â cannot be correctly produced. The maturity ladder figures are invalid by time bucket but the total stock figure survives.
- **Driven by:** Principle 5 (Â¶46(d)) â *"Liquidity risk indicators such as cash flows/settlements and funding"*; Principle 4 (Â¶41) â completeness for all material risk exposures
- **Search terms:** maturity date, contractual maturity, next cash flow date, repricing date, scheduled settlement date, liquidity bucket, maturity bucket, contractual cash flow, funding maturity
- **Data quality requirements:**
  - *Completeness* â Every instrument record carries a non-null contractual maturity or next cash flow date | Percentage of instrument records with null maturity date | Target: 0% for dated instruments
  - *Validity* â Maturity dates are valid calendar dates after the as-of date (or equal to it for same-day maturities) and are consistent with the instrument's contractual terms | Count of records where maturity date precedes the as-of date without a matured/settled status flag | Target: 0
  - *Timeliness* â Maturity date updates (e.g., following a rollover or restructuring) are reflected in the risk system within the agreed lag | Count of instruments with a known restructuring event where the maturity date has not been updated within the agreed period | Target: 0

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Single-Counterparty Aggregation Integrity (Full-Population Reconciliation)**

- **Spans:** CDE-01 (Counterparty Unique Identifier), CDE-03 (Gross Exposure Amount), CDE-11 (Net Exposure), CDE-09 (GL Reconciliation Key)
- **What this is:** This requirement cannot be expressed as a rule on any single element. It is the end-to-end check that, for every counterparty, all exposure records across all booking systems, business lines, and geographies have been identified, linked via CDE-01, and summed to produce a complete single-counterparty aggregate â and that this aggregate reconciles to accounting records via CDE-09. It is the operational test of whether Principle 3 (accuracy) and Principle 4 (completeness) are simultaneously satisfied.
- **Dimension:** Completeness and accuracy (cross-cutting)
- **Rule intent:** For every active counterparty identifier, the sum of gross exposures across all source systems must equal the sum of exposures recorded in the general ledger or system of record for that counterparty, within agreed materiality. No counterparty with an exposure in any source system should be absent from the consolidated counterparty exposure view.
- **Measurement:**
  1. Count of source systems containing exposure records that do not contribute to the consolidated counterparty aggregation layer â identifies coverage gaps
  2. For each counterparty identifier, absolute and percentage variance between the risk-system aggregate and the GL-sourced aggregate â identifies accuracy breaks
  3. Count of counterparties present in source systems but absent from the consolidated view â identifies completeness failures
- **Regulatory basis:** Principle 3 (Â¶36(c)): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 4 (Â¶43): *"Supervisors expect banks to produce aggregated risk data that is complete and to measure and monitor the completeness of their risk data"*; Principle 5 (Â¶46(a)): aggregated credit exposure to a large corporate borrower named as a critical risk

---

**XDQ-02 â Manual / EUC Reliance and Lineage Transparency**

- **Spans:** CDE-10 (Source System / Provenance Flag), CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key), and by extension all other CDEs whose values may be sourced from manual processes
- **What this is:** No individual element rule can assess whether the bank's aggregate reliance on manual and end-user-computing sources is within acceptable risk tolerance, or whether the required mitigants are in place and documented for each manual feed. This cross-cutting requirement measures the proportion of the total exposure universe that rests on manual/EUC origins, trends it over time, and triggers review when it exceeds the approved threshold.
- **Dimension:** Accuracy, completeness (cross-cutting)
- **Rule intent:** The proportion of total exposure amount sourced from manual or EUC processes should be measured, disclosed in aggregate risk reports, and tracked against the bank's target for automation. Each manual source that exceeds a defined materiality threshold must have a documented mitigant, and the existence of that documentation must be verifiable.
- **Measurement:**
  1. Percentage of total gross exposure amount (CDE-03) attributable to records flagged as manual or EUC origin (CDE-10) â the "manual dependency ratio" by risk type and business line
  2. Count of manual/EUC sources above the materiality threshold that lack a current, approved mitigant document in the policy repository â the "undocumented manual exposure" count
  3. Trend of the manual dependency ratio over successive reporting periods â to evidence progress against Â¶39's requirement for proposed actions to reduce impact
- **Regulatory basis:** Principle 3 (Â¶36(b)): *"effective mitigants in placeâ¦ consistently applied across the bank's processes"*; Principle 3 (Â¶39): *"documentation should include an explanation of the appropriateness of any manual workarounds, a description of their criticalityâ¦ and proposed actions to reduce the impact"*; Principle 1 (Â¶30): senior management must understand *"limitationsâ¦ in technical terms (egâ¦ degree of reliance on manual processes)"*

---

**XDQ-03 â Aggregation Dimension Consistency Across Systems**

- **Spans:** CDE-05 (Business Line), CDE-06 (Country / Geography Code), CDE-07 (Industry / Sector Code), CDE-02 (Legal Entity), CDE-04 (Risk Classification)
- **What this is:** Even if each dimension element is individually valid within a single system, the bank will fail Principles 4 and 6 if the same exposure is attributed to different business lines, countries, or sectors across different source systems. This check cannot be performed on any single CDE â it requires comparing attributions across systems for the same instrument or counterparty.
- **Dimension:** Consistency (cross-cutting)
- **Rule intent:** For any instrument or exposure that appears in more than one source system (e.g., trade capture, risk engine, finance system), the values of each aggregation dimension â business line, country-of-risk, industry code, legal entity â must be identical or, where deliberate remapping exists, the remapping must be documented and approved. Inconsistent attribution causes exposures to be double-counted in one dimension and under-counted in another.
- **Measurement:**
  1. Count of instruments/exposures present in multiple source systems where the business line code differs between systems â "business line attribution conflicts"
  2. Count of instruments/exposures where the country-of-risk code differs between the booking system and the risk aggregation layer â "country attribution conflicts"
  3. Count of counterparties where the industry code differs between the counterparty reference system and the risk system â "sector attribution conflicts"
  4. All three measured by asset class and business line to enable root-cause triage
- **Regulatory basis:** Principle 2 (Â¶33): *"integrated data taxonomies and architectureâ¦ unified naming conventions"*; Principle 4 header: data available by business line, legal entity, industry, region simultaneously; Principle 6 (Â¶50): on-demand sub-aggregates by country and industry "across all business lines and geographic areas"

---

## 4. Out of Scope

What CDEs and data quality monitoring cannot deliver â and what is actually required instead.

---

### Principles 8â11: Reporting content, quality, frequency, and distribution

**Principle 8 â Comprehensiveness (Â¶57â60)**

This principle has two distinct faces.

*Face 1 â drives a CDE:* Â¶57 names industry sector and country as required report dimensions, and Â¶58 requires reports to show limit utilisation and risk appetite context. These requirements are the basis for CDE-07 (Industry/Sector Code) and CDE-11 (Net Exposure / Post-Mitigation Exposure Amount) in Section 2. To that extent, Principle 8 is addressed through the CDE register.

*Face 2 â beyond the catalog's reach:* The substance of Principle 8 â whether the reports actually cover all material risk areas, whether capital adequacy and stress testing results are included, whether forward-looking scenarios are presented, and whether the depth and scope are appropriate for the bank's risk profile â cannot be monitored by tracking data elements. Those are judgements about report design, content review, and board-level governance. What is required instead: a formal risk reporting inventory, reviewed and approved by senior management or the Risk Committee, documenting which reports address which risk areas, their recipients, and the sign-off process confirming material completeness. Independent validation teams (Â¶29(a)) are the mechanism for assessing whether coverage is genuinely comprehensive.

**Principle 9 â Clarity and usefulness (Â¶61â69)**

Â¶67 requires a bank to develop "an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports." A data catalog is precisely the tool for this, so Principle 9 supports the case for a catalog as an operational asset. However, the principle's core obligations â that reports balance quantitative and qualitative information appropriately (Â¶62), that recipients confirm reports are relevant (Â¶69), that the board receives the right level of aggregation (Â¶64â65) â are communication and governance matters. No data quality rule can assess whether a report is "clear and concise" or whether it "facilitates informed decision-making." What is required instead: structured recipient feedback processes, periodic report usefulness reviews, and documented sign-off from the board and Risk Committee that reporting meets their needs.

**Principle 10 â Frequency (Â¶70â71)**

The regulation requires that report production frequency be set by the board and senior management, that it escalate during stress, and that the bank routinely test its ability to produce reports within those timeframes. A data catalog can record agreed SLAs (consistent with Â¶27's reference to service level standards) and flag when data is available â but it cannot govern whether the board has set appropriate frequencies, whether escalation procedures are triggered correctly during stress, or whether the production test results are acted upon. What is required instead: a report production SLA register with documented board approval, a stress-reporting drill or simulation regime, and operational monitoring of production runtimes against approved SLAs. The timeliness DQ dimensions on CDE-08 and CDE-03 address data freshness at the element level only; they do not address end-to-end report delivery timing.

**Principle 11 â Distribution (Â¶72â74)**

Distribution requires that reports reach the right recipients rapidly while confidentiality is maintained. These are access control, entitlement management, and delivery infrastructure concerns. A data catalog can document data sensitivity classifications and intended audiences (supporting CDE-10's provenance metadata), but it cannot enforce distribution controls, verify that the right person received a report, or audit whether a report was accessed inappropriately. What is required instead: a formal entitlement framework with periodic recertification, a report distribution log, and access controls enforced at the report delivery layer.

---

### Principle 1 â Governance (Â¶27â31): The parts that remain out of scope

Principle 1 drives the requirement for a CDE register and DQ monitoring framework â the existence of this analysis is itself a response to Â¶30 ("identify data critical to risk data aggregation"). However, Principle 1's obligations go substantially beyond catalog governance:

- **Board and senior management approval** of the risk data aggregation framework (Â¶28) requires formal governance documentation, committee papers, and minuted approvals â not data element records.
- **Independent validation** of risk data aggregation processes (Â¶29(a)) requires a second-line or internal audit function with IT, data, and reporting expertise to assess the entire aggregation chain â not automated DQ monitoring.
- **Due diligence on acquisitions** for data aggregation impacts (Â¶29(b)) is a transaction governance matter.
- **Senior management awareness of limitations** (Â¶30) requires narrative disclosure and management reporting on known gaps â the DQ monitoring in this register generates the evidence for that disclosure, but the disclosure itself is a governance act outside the catalog's scope.

---

### Principle 2 â Data Architecture (Â¶32â35): Structural requirements the catalog records but cannot create

Principle 2 drives CDE-01 (single counterparty identifier) and CDE-10 (source system provenance), and it is the direct mandate for maintaining a data catalog with metadata and naming conventions (Â¶33). However, a catalog is a record of the architecture, not the architecture itself. The regulation requires the bank to *build* integrated data taxonomies, assign data ownership roles (Â¶34), and ensure business continuity planning covers data aggregation (Â¶32). A catalog populated with CDEs and DQ rules evidences progress but does not substitute for the technical architecture investment, the role assignments, or the BCP testing. What is required: a formal data architecture programme, a data ownership policy with named stewards, and BCP tests that include data aggregation scenarios.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Unique Identifier | 3 | 2 (Â¶33), 5 (Â¶46aâb) | Uniqueness, Completeness, Validity, Consistency |
| CDE-02 | Legal Entity / Booking Entity Identifier | 3 | 2 (Â¶33), 4 (Â¶41) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | 4 (Â¶41), 3 (Â¶36a) | Accuracy, Completeness, Validity, Timeliness |
| CDE-04 | Risk Classification / Risk Type Code | 2 | 8 (Â¶57), 2 (Â¶33), 4 (Â¶41â42) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | 2 | 4 (header), 6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-06 | Country / Geography Code | 2 | 4 (header), 6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-07 | Industry / Sector Code | 2 | 4 (header), 8 (Â¶57) | Completeness, Validity, Timeliness |
| CDE-08 | As-Of / Position Date | 3 | 5 (Â¶44â45), 6 (Â¶50), 7 (Â¶53a) | Completeness, Validity, Timeliness, Consistency |
| CDE-09 | GL / Source System Reconciliation Key | 2 | 3 (Â¶36c), 7 (Â¶53a) | Completeness, Validity, Accuracy |
| CDE-10 | Source System / Data Provenance Flag | 2 | 3 (Â¶36b, Â¶39) | Completeness, Validity, Accuracy |
| CDE-11 | Net Exposure / Post-Mitigation Amount | 2 | 8 (Â¶58), 4 (Â¶41), 7 (Â¶54) | Accuracy, Completeness, Validity |
| CDE-12 | Liquidity Cash Flow / Contractual Maturity Date | 2 | 5 (Â¶46d), 4 (Â¶41) | Completeness, Validity, Timeliness |

**Criticality 3 elements (4):** CDE-01, CDE-02, CDE-03, CDE-08 â the joining key, the consolidation key, the quantity being aggregated, and the temporal anchor. Remove any one and a correctly bounded aggregate figure cannot be produced.

**Criticality 2 elements (8):** All remaining CDEs. Each degrades a specific slice, reconciliation, or control â but the aggregation mechanism itself survives.

**Criticality 1 elements:** None identified. Every element in this register has a direct and concrete effect on either the correctness or the auditability of an aggregated risk figure. If an element fell to "improves interpretation only," it was excluded rather than retained at level 1.