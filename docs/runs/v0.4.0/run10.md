# BCBS 239 â Data Catalog Governance Interpretation

---

## 1. Objectives and Scope

**What the regulation is trying to achieve:**

- **Reliable risk aggregation as the foundation of risk management.** Banks must be able to produce accurate, complete, and timely aggregated risk data under both normal and stress conditions, not merely to report to supervisors but to support internal decision-making by the board and senior management. Â¶35: *"banks should develop and maintain strong risk data aggregation capabilities to ensure that risk management reports reflect the risks in a reliable way."*

- **A single, governed data architecture with common identifiers.** Risk data must flow from integrated systems using consistent taxonomies, metadata, and naming conventions rather than from siloed or ad-hoc sources. Â¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts."*

- **Completeness across all material exposures and all aggregation dimensions.** Every material risk exposure â including off-balance-sheet items â must be capturable and sliceable by business line, legal entity, asset type, industry, region, and other relevant groupings. Â¶41: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."* Â¶50 further requires that aggregation be performable across combinations of dimensions (e.g., country credit exposures as of a specified date across all business lines and geographic areas) on demand.

- **Reconcilability and evidenced accuracy.** Risk data must be reconciled to accounting and other authoritative sources so that accuracy is not asserted but proven. Â¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."* Â¶36(d) establishes the goal of a single authoritative source per risk type. An unreconciled figure, even if numerically plausible, is non-compliant.

- **Transparency of provenance, including manual and EUC processes.** All aggregation processes â automated or manual â must be documented. Manual workarounds must be explained and their criticality to accuracy assessed. Â¶39: *"Documentation should include an explanation of the appropriateness of any manual workarounds, a description of their criticality to the accuracy of risk data aggregation and proposed actions to reduce the impact."*

- **Adaptability to support on-demand slicing and stress scenarios.** The underlying data must support ad-hoc queries and scenario analyses without requiring architectural changes, meaning the dimensional attributes used to slice exposures must be present and consistent at the record level, not constructed at report time. Â¶48: *"A bank's risk data aggregation capabilities should be flexible and adaptable to meet ad hoc data requests, as needed, and to assess emerging risks."*

**Who it applies to:**

BCBS 239 was issued in January 2013 and addressed primarily to **Global Systemically Important Banks (G-SIBs)**, with a compliance deadline of January 2016. The Basel Committee subsequently extended expectations to **Domestic Systemically Important Banks (D-SIBs)** through national supervisory implementation, typically within three years of their designation. In practice, many large internationally active banks outside the G-SIB/D-SIB lists have adopted the principles either voluntarily or under national supervisory guidance. The principles apply to the **consolidated banking group** â all legal entities, subsidiaries, and branches â not merely the parent entity or regulated solo entities.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Identifier**

- **Definition:** A unique, persistent identifier assigned to each external counterparty (corporate borrower, financial institution, sovereign, or retail customer treated as a single obligor) that remains stable across systems, business lines, and legal entities within the banking group. It is the joining key by which all exposures to a single counterparty can be collected and summed.
- **Why critical:** Without a single resolvable counterparty identifier, it is impossible to aggregate total exposure to a single name â the most fundamental credit risk calculation. Duplicate or ambiguous identifiers cause the same counterparty to appear as multiple obligors, making concentration risk invisible. Â¶46(a) explicitly names *"the aggregated credit exposure to a large corporate borrower"* as a critical risk requiring rapid aggregation in stress.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3.** Without a resolvable counterparty identifier, the aggregate credit exposure to a single obligor cannot be computed at all, because there is no joining key to collect records from multiple source systems into a single obligor total. This is not degradation â the aggregate simply does not exist.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶41) â completeness of material exposures; Principle 5 (Â¶46(a)(b)) â rapid aggregation of credit and counterparty exposures under stress.
- **Search terms:** counterparty ID, obligor ID, client ID, legal entity identifier (LEI), customer master, party identifier, GFCID, GCIF, golden record, counterparty master
- **Data quality requirements:**
  - *Uniqueness* â Each distinct legal-entity counterparty maps to exactly one identifier in the counterparty master; no two records represent the same real-world entity under different IDs | Count of duplicate counterparty names or registration numbers mapped to more than one active identifier | Target: 0 duplicates confirmed by reconciliation against an authoritative external reference (e.g., LEI register, company registry)
  - *Completeness* â Every exposure record carries a non-null, resolvable counterparty identifier that matches a record in the counterparty master | Count and percentage of exposure records with null, blank, or unmatched counterparty identifier | Target: <0.1% unmatched at EOD; 0% for records entering regulatory capital calculations
  - *Consistency* â The same counterparty is represented by the same identifier across all source systems contributing to risk aggregation | Count of counterparties where different source systems carry different identifiers for the same legal entity, identified through matching on LEI, tax identifier, or registration number | Target: 0 cross-system mismatches in scope of regulatory reporting

---

**CDE-02 â Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier for the bank's own legal entity in which a transaction or exposure is booked. Distinct from the counterparty identifier (CDE-01), this identifies which part of the banking group holds the exposure â the booking entity for consolidation, solo reporting, and intragroup netting purposes.
- **Why critical:** Group-level risk aggregation requires rolling up exposures from individual booking entities. Regulatory reports are often required at both solo and consolidated levels. If booking entity is wrong or inconsistently coded, the same exposure may be double-counted in consolidation or dropped from a subsidiary report. Â¶33 requires a single identifier for legal entities; Â¶41 requires aggregation across the banking group.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 3.** Without a correct and consistent booking-entity identifier, consolidated group exposure figures cannot be computed â records cannot be attributed to entities, and intercompany eliminations cannot be executed. The aggregate is invalid, not merely degraded.
- **Driven by:** Principle 2 (Â¶33) â *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (Â¶41) â *"capture and aggregate all material risk data across the banking group"*
- **Search terms:** legal entity ID, booking entity, entity code, subsidiary code, LEI (own entity), branch code, reporting unit, consolidation entity, organizational unit
- **Data quality requirements:**
  - *Validity* â Every booking entity code on an exposure record must match an active, in-scope entry in the group entity hierarchy | Count of exposure records carrying entity codes not present in the current legal entity reference table | Target: 0 invalid codes in any risk aggregation feed
  - *Completeness* â No exposure record in any risk system carries a null or placeholder booking entity code | Count of records with null, "unknown," or "default" entity code | Target: 0% null for records used in regulatory reporting
  - *Consistency* â The entity code used in the risk system matches the entity code used in the general ledger for the same booking entity | Reconciliation count of exposures where risk-system entity code differs from GL entity code for the same transaction identifier | Target: 0 mismatches after daily reconciliation

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary amount representing the bank's gross risk exposure on a position or transaction before credit risk mitigation (collateral, guarantees, netting). This is the primary input to credit risk aggregation, limit monitoring, and capital calculation. Expressed in the transaction currency and, separately, in the reporting currency (see CDE-04 for currency conversion dependency).
- **Why critical:** This is the figure being aggregated. Every other CDE either identifies what it belongs to or classifies how it should be counted. If gross exposure is inaccurate or incomplete, every downstream aggregate â single-name concentration, business line total, country exposure â inherits the error. Â¶36(a): controls around risk data must be as robust as those applicable to accounting data.
- **Risk types:** Credit, counterparty credit, concentration, cross-cutting
- **Criticality: 3.** Without a gross exposure amount, there is no quantity to aggregate. The aggregate figure credit exposure to counterparty X is arithmetically undefined if the component exposure amounts are missing or unreliable. This is structural: no amount, no sum.
- **Driven by:** Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (Â¶41) â all material exposures must be captured; Principle 5 (Â¶46(a)) â rapid aggregation of credit exposures under stress
- **Search terms:** notional amount, outstanding balance, drawn exposure, commitment amount, mark-to-market value, replacement cost, EAD (exposure at default), carrying amount, book value, face value
- **Data quality requirements:**
  - *Accuracy* â The exposure amount on each risk record reconciles to the corresponding balance on the general ledger or system of record within an agreed tolerance | Sum of absolute differences between risk system exposure amounts and GL balances by transaction, expressed as a percentage of total portfolio | Target: â¤0.1% unexplained variance; any variance >agreed materiality threshold triggers exception report
  - *Completeness* â Every in-scope transaction carries a non-null, non-zero exposure amount unless contractually zero is correct and documented | Count of exposure records with null or zero amounts where product type and transaction status require a positive balance | Target: 0 unexplained null or zero amounts in regulatory scope
  - *Timeliness* â Exposure amounts reflect positions as of the declared position date (CDE-08); stale values from prior dates are identifiable | Count of records where the value-date of the exposure amount lags the declared position date by more than the agreed tolerance | Target: 0 records with unexplained value-date lag exceeding 1 business day for daily reporting

---

**CDE-04 â Transaction Currency / Reporting Currency**

- **Definition:** The currency in which the exposure amount (CDE-03) is denominated (transaction currency), and the standardised reporting currency into which it is converted for group-level aggregation. Includes the exchange rate applied and its effective date.
- **Why critical:** A banking group with exposures in multiple currencies cannot aggregate total exposure without currency conversion. An incorrect currency code, a stale exchange rate, or a missing conversion causes the reported exposure amount to be wrong in the reporting currency â silently, because the record still carries a number. Currency is a dimension of every monetary aggregate. Â¶42 notes that while a common metric is not mandatory, each system must make its aggregation approach clear; currency conversion is the most universal form of that problem.
- **Risk types:** Market (FX), credit, liquidity, cross-cutting
- **Criticality: 2.** A gross exposure aggregate can be computed with wrong currency codes â the arithmetic runs â but the result is wrong in a way that may not be immediately visible. The aggregate is produced but cannot be trusted in the reporting currency. This is degradation of accuracy, not structural impossibility, so it does not meet the step-2 test for a 3.
- **Driven by:** Principle 3 (Â¶36(a)) â accuracy parity with accounting data (accounting always specifies functional currency); Principle 4 (Â¶41â43) â completeness and comparability of aggregated risk data; Principle 6 (Â¶50) â on-demand aggregation of country credit exposures requires a consistent currency basis
- **Search terms:** currency code, ISO currency, transaction currency, functional currency, base currency, reporting currency, FX rate, exchange rate, rate effective date
- **Data quality requirements:**
  - *Validity* â Every currency code on a risk record must be a recognised ISO 4217 three-letter code | Count of records with currency codes not in the ISO 4217 reference list | Target: 0 invalid codes
  - *Accuracy* â Exchange rates applied to convert transaction-currency exposures to reporting currency must match the bank's official rate source for the relevant rate date | Count of records where the applied exchange rate deviates from the official rate by more than an agreed tolerance | Target: 0 unexplained deviations; all approved deviations documented with business rationale
  - *Timeliness* â Exchange rates used in daily risk aggregation reflect rates no older than the prior business day's official close | Count of records using exchange rates with an effective date more than 1 business day before the position date (CDE-08) | Target: 0% stale rates for end-of-day regulatory aggregations

---

**CDE-05 â Risk Type Classification**

- **Definition:** The categorical label assigned to each exposure or position identifying the primary risk type it contributes to (credit risk, market risk, liquidity risk, operational risk, counterparty credit risk). May include sub-type where material (e.g., specific wrong-way risk within counterparty credit). This is the primary partition of a bank's risk taxonomy.
- **Why critical:** Risk management reports are organised by risk type (Â¶57). Aggregation engines filter and route records by risk type. A record misclassified as market risk instead of credit risk disappears from the credit risk aggregate and inflates the market risk aggregate simultaneously â a double error that neither aggregate reveals on its own. Â¶37 requires a dictionary of concepts defined consistently across the organisation; risk type is the most fundamental entry in that dictionary.
- **Risk types:** Cross-cutting (classifies all other risk types)
- **Criticality: 2.** An aggregate can be computed with a wrong risk type â the arithmetic runs â but the credit risk total is wrong and the market risk total is wrong. The sliced aggregate cannot be trusted. This is the definition of a 2: produced but cannot be trusted in the relevant partition.
- **Driven by:** Principle 3 (Â¶37) â *"A bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"*; Principle 7 (Â¶57) â *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 8 (Â¶57) â reports must cover all significant risk areas
- **Search terms:** risk type, risk class, risk category, asset class, risk flag, product risk type, risk taxonomy code
- **Data quality requirements:**
  - *Validity* â Every exposure record carries a risk type code that exists in the bank's approved risk taxonomy | Count of records with risk type codes not present in the current approved taxonomy reference table | Target: 0 invalid codes
  - *Completeness* â No material exposure record carries a null or "unclassified" risk type code | Count and percentage of records with null or "other/unclassified" risk type | Target: <0.5% unclassified for records in scope; each exception documented and resolved within agreed SLA
  - *Consistency* â The risk type assigned in the risk system is consistent with the risk type implied by the product type and transaction characteristics | Count of records where the risk type code is inconsistent with the product-type-to-risk-type mapping rules | Target: 0 inconsistencies; mapping rules maintained in catalog as a reference dataset

---

**CDE-06 â Business Line**

- **Definition:** The internal organisational unit or business segment to which an exposure is attributed for management reporting purposes (e.g., retail banking, corporate banking, trading, treasury, private banking). Must align to the bank's official organisational taxonomy.
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. Principle 8 (Â¶57) requires reports that cover all significant risk areas, which presupposes that every record is attributed to a business line. A record with a null or incorrect business line is excluded from the relevant business line aggregate and may inflate or deflate limit utilisation for that line. Â¶50 requires aggregation of credit exposures *across all business lines* â this is only possible if every record carries a valid business line.
- **Risk types:** Credit, market, liquidity, operational, cross-cutting
- **Criticality: 2.** Aggregates can be computed without complete business line attribution, but the business-line slice of the aggregate is wrong â over- or understated for the affected line. Senior management cannot rely on business line risk reports. This is a slice integrity failure, not an inability to compute.
- **Driven by:** Principle 4 (Â¶41, header) â *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures â¦ across all business lines and geographic areas"*
- **Search terms:** business line, business segment, line of business, LOB code, business unit, division code, cost centre, desk, product line
- **Data quality requirements:**
  - *Completeness* â Every exposure record in scope of risk reporting carries a non-null business line code | Count and percentage of records with null or "default" business line code | Target: 0% null for records in regulatory scope
  - *Validity* â Business line codes reference active entries in the bank's official organisational hierarchy | Count of records referencing business line codes that are inactive, merged, or not in the current hierarchy | Target: 0 invalid codes
  - *Consistency* â The business line on the risk record matches the business line recorded on the corresponding GL entry for the same transaction | Count of transactions where risk system business line differs from GL cost centre/business segment mapping | Target: reconciliation difference <1% by count; all exceptions investigated

---

**CDE-07 â Geography / Country of Risk**

- **Definition:** The country to which an exposure is attributed for risk aggregation purposes. This may be country of counterparty domicile, country of risk (transfer risk basis), country of collateral, or country of booking â the specific basis must be documented and applied consistently. For credit risk, country of risk (the jurisdiction whose transfer risk the bank bears) is typically the primary attribute.
- **Why critical:** Principle 4 names region as a required aggregation dimension. Principle 6 (Â¶50) gives the on-demand aggregation of country credit exposures as the canonical example of adaptability. Principle 8 (Â¶57) names country as a component of credit risk reporting. A record with a wrong or null country code is excluded from the relevant country aggregate, making concentration risk in that country invisible. During stress events (e.g., sovereign crisis), the ability to pull all exposures to a country on demand is critical to crisis management.
- **Risk types:** Credit, concentration, market
- **Criticality: 2.** Country aggregates can be computed â but with wrong or missing country codes, the country-level exposure figure is understated and concentration risk is invisible for that jurisdiction. The aggregate is produced but cannot be trusted for the affected country slice.
- **Driven by:** Principle 4 (Â¶41, header) â *"Data should be available by â¦ region"*; Principle 6 (Â¶50) â *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*; Principle 8 (Â¶57) â country is a named component of credit risk reporting
- **Search terms:** country code, country of risk, country of domicile, country of booking, jurisdiction, ISO country code, transfer risk country, geographic region
- **Data quality requirements:**
  - *Validity* â Every geography/country code on a risk record must be a recognised ISO 3166-1 alpha-2 or alpha-3 code, or a bank-defined regional grouping that maps to ISO codes | Count of records with unrecognised country codes | Target: 0 invalid codes
  - *Completeness* â Every exposure record carries a non-null country of risk | Count and percentage of records with null country code | Target: <0.1% null for records in credit risk scope
  - *Consistency* â The country of risk basis (domicile, transfer risk, collateral location) is applied consistently within each risk type and is documented | Presence and completeness of the country-of-risk basis definition in the catalog for each risk type in scope | Target: 100% of risk types in scope have a documented and approved country-of-risk basis rule

---

**CDE-08 â Position Date / As-Of Date**

- **Definition:** The date as of which a risk position or exposure amount is stated. This is the temporal key that anchors every aggregate to a specific point in time. It is distinct from trade date, settlement date, or value date, though in some contexts those may coincide. For any aggregated risk figure, the as-of date is part of the figure's definition: "total credit exposure as of [date]" is meaningless without a reliable, consistent as-of date on every contributing record.
- **Why critical:** Principle 5 requires timely aggregation as of a specific date, and Principle 6 (Â¶50) requires on-demand aggregation *"as of a specified date."* If different records in the same aggregate carry different as-of dates â whether because of stale feeds, late bookings, or inconsistent cut-off conventions â the aggregate mixes positions from different points in time. The resulting figure does not represent any real moment and cannot be used for limit monitoring, capital calculation, or stress reporting. Principle 7 (Â¶52â53) requires reports to be accurate and reconcilable; a temporally inconsistent aggregate cannot be reconciled to accounting data as of the same date.
- **Risk types:** Credit, market, liquidity, counterparty credit, cross-cutting
- **Criticality: 3.** Without a consistent and reliable position date, the aggregate figure "total exposure as of date D" cannot be computed â records from different dates are mixed, and there is no way to produce a point-in-time figure that can be reconciled to accounting or reported to the board. The figure is invalid because it does not correspond to any defined moment. This meets the step-2 test: the aggregate X (exposure as of date D) cannot be computed because the constituent records are not all timestamped to date D.
- **Driven by:** Principle 5 (Â¶44â46) â *"produce aggregate risk information on a timely basis"* and *"capable of producing aggregated risk data rapidly during times of stress/crisis"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (Â¶52â53) â reconciliation of reports to risk data requires a common temporal reference
- **Search terms:** position date, as-of date, reporting date, value date, snapshot date, reference date, effective date, risk date, data as-of
- **Data quality requirements:**
  - *Validity* â Position dates must be valid calendar dates within an agreed operational range (e.g., not in the future, not more than N business days stale) | Count of records with null, non-date, or out-of-range position dates | Target: 0 invalid dates in any risk aggregation feed
  - *Consistency* â All records contributing to a single risk aggregate (e.g., end-of-day credit exposure) carry the same position date | Count of records in an aggregation batch where the position date differs from the declared batch as-of date | Target: 0 mismatched dates in any end-of-day regulatory batch; late-arriving records documented and their impact quantified
  - *Timeliness* â Risk system feeds are loaded by the cut-off time agreed for the declared position date; records are not silently backdated or forward-dated | Count of records where the feed load timestamp is more than agreed tolerance after the declared position date cut-off | Target: 0 unexplained overruns; all late loads logged with business justification

---

**CDE-09 â General Ledger / System-of-Record Reconciliation Key**

- **Definition:** The identifier â typically a transaction reference number, deal ID, or account number â that links a risk data record to its corresponding entry in the general ledger or designated system of record. This is not a new piece of data: it is the key that, when present and correct on both sides, makes reconciliation between risk and finance possible. Without it, Â¶36(c) compliance is structurally impossible.
- **Why critical:** Â¶36(c) requires that *"risk data should be reconciled with bank's sources, including accounting data where appropriate."* Â¶53(a) requires *"defined requirements and processes to reconcile reports to risk data."* Reconciliation is not a one-time exercise â it is a continuous control. The reconciliation key is what makes that control executable. If it is absent, corrupted, or inconsistently populated between risk and GL systems, reconciliation cannot be performed at record level â only at summary level, which is insufficient to isolate individual errors. An unreconcilable aggregate is, under the regulation's own logic, an unverifiable one. Supervisors will look for evidence of reconciliation as the primary proof of accuracy.
- **Risk types:** Credit, market, liquidity, cross-cutting (reconciliation spans all risk types)
- **Criticality: 3.** Without a resolvable GL/system-of-record reconciliation key, the accuracy of the exposure aggregate cannot be evidenced â Â¶36(c) compliance fails structurally. Under the regulation's logic, an unverifiable figure is not a compliant one. The step-2 sentence applies directly: "Without this element, the aggregate figure for credit exposure cannot be reconciled to the general ledger at all, because there is no joining key to match risk records to GL entries."
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (Â¶36(d)) â *"a single authoritative source for risk data per each type of risk"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** transaction ID, deal ID, trade ID, account number, GL reference, journal entry reference, source transaction key, booking reference, contract number, facility ID
- **Data quality requirements:**
  - *Completeness* â Every risk data record in scope of reconciliation carries a non-null GL/system-of-record reference key | Count and percentage of risk records with null or placeholder reconciliation keys | Target: 0% null for records within regulatory reporting scope
  - *Accuracy* â Each reconciliation key on a risk record resolves to an existing entry in the general ledger or designated system of record | Count of risk records whose reconciliation key has no matching entry in the GL after the daily reconciliation run | Target: 0 unmatched keys after reconciliation; all breaks logged and resolved within agreed SLA
  - *Uniqueness* â The reconciliation key uniquely identifies the same transaction on both the risk and GL sides; the same key does not map to multiple risk records unless the GL entry is intentionally split and that split is documented | Count of reconciliation keys appearing on more than one risk record where the GL entry is not split | Target: 0 unintended duplicates

---

**CDE-10 â Industry / Sector Classification**

- **Definition:** The industry or economic sector code assigned to a counterparty or exposure (e.g., NACE, GICS, SIC, or a bank's internal sector taxonomy). Identifies the economic activity of the borrower or issuer, used to identify sector concentrations in credit portfolios.
- **Why critical:** Principle 4 names industry as a required aggregation dimension alongside business line, legal entity, and region. Principle 8 (Â¶57) explicitly names industry sector as a component of credit risk reporting: *"single name, country and industry sector for credit risk."* Principle 6 (Â¶50) requires on-demand aggregation of *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas."* A record with a null or wrong sector code is excluded from the relevant sector aggregate, making sector concentration invisible.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Sector aggregates can be computed, but with missing or wrong sector codes the sector-level concentration figure is understated or misattributed. Senior management cannot rely on sector concentration reports for the affected classifications. This is a slice integrity failure â the aggregate is produced but cannot be trusted for the relevant sector.
- **Driven by:** Principle 4 (Â¶41, header) â *"Data should be available by â¦ industry"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*
- **Search terms:** industry code, sector code, NACE code, SIC code, GICS sector, industry classification, borrower industry, counterparty sector, economic sector
- **Data quality requirements:**
  - *Completeness* â Every credit exposure record carries a non-null industry/sector code | Count and percentage of credit exposure records with null or "unclassified" sector code | Target: <1% unclassified; all exceptions documented with resolution timeline
  - *Validity* â Industry codes reference entries in the bank's approved sector taxonomy or an approved external classification standard | Count of records with codes not in the approved taxonomy reference table | Target: 0 invalid codes
  - *Consistency* â The sector taxonomy used in the risk system is the same taxonomy used in the credit risk report and in limit monitoring; translations between taxonomies (e.g., internal to NACE) are documented and applied consistently | Presence of approved cross-walk mapping between taxonomies in the catalog; count of records where the mapped code differs from the directly assigned code | Target: one approved cross-walk per taxonomy pair; 0 unmapped codes

---

**CDE-11 â Source System / Data Provenance Flag**

- **Definition:** The identifier or attribute that records (a) which source system originated the risk data record, and (b) whether the record was produced by an automated feed or entered or modified manually (including end-user computing / spreadsheet-sourced data). These two attributes together constitute provenance for the purposes of Â¶36(b), Â¶36(d), and Â¶39.
- **Why critical:** Â¶39 requires documentation of all risk data aggregation processes, automated and manual, including the appropriateness of manual workarounds and their criticality to accuracy. Â¶36(b) requires effective mitigants for manual processes and EUC. Â¶36(d) requires a single authoritative source. Without a source system flag and a manual/automated flag on each record, it is impossible to (a) demonstrate which records came from controlled automated sources versus uncontrolled spreadsheets, (b) measure the proportion of the aggregate that depends on manual input, or (c) target remediation toward the highest-risk data paths. Supervisors examining compliance with Â¶39 will ask for evidence that the bank knows which parts of its risk data are manually sourced.
- **Risk types:** Cross-cutting (affects all risk types)
- **Criticality: 2.** Aggregate figures can be computed without provenance flags. But without them, the bank cannot demonstrate Â¶36(b) and Â¶39 compliance, cannot quantify manual process risk, and cannot perform lineage analysis to identify which aggregates are degraded by EUC input. This is a governance control failure, not an arithmetic one â the aggregate is produced but cannot be evidenced as controlled.
- **Driven by:** Principle 3 (Â¶36(b)) â *"Where a bank relies on manual processes and desktop applications â¦ it should have effective mitigants in place"*; Principle 3 (Â¶36(d)) â *"a single authoritative source for risk data per each type of risk"*; Principle 3 (Â¶39) â *"Documentation should include an explanation of the appropriateness of any manual workarounds, a description of their criticality to the accuracy of risk data aggregation"*
- **Search terms:** source system, originating system, data source, feed name, system of origin, manual override flag, EUC flag, end-user computing, spreadsheet flag, data entry source, automation flag, interface name
- **Data quality requirements:**
  - *Completeness* â Every risk data record carries a non-null source system identifier and a non-null manual/automated flag | Count and percentage of records with null source system ID or null manual/automated flag | Target: 0% null on any record entering a regulatory risk aggregate
  - *Validity* â Source system codes reference entries in the bank's approved system inventory; manual/automated flags use a defined enumerated set | Count of records with source system codes not in the approved inventory, or flag values outside the defined enumeration | Target: 0 invalid values
  - *Accuracy* â Records that passed through any manual intervention (override, adjustment, spreadsheet upload) are flagged as manual; records that did not are flagged as automated | Count of records where an audit trail confirms manual intervention but the flag is set to "automated" | Target: 0 misclassified flags; evidence of control tested quarterly through reconciliation of manual flags to intervention audit logs

---

**CDE-12 â Collateral / Credit Risk Mitigant Identifier**

- **Definition:** The identifier linking an exposure to any credit risk mitigant â collateral, guarantee, netting agreement, or credit derivative â that reduces the net exposure for capital and concentration purposes. Includes the mitigant type, the mitigant value, and the currency of the mitigant.
- **Why critical:** Net exposure after credit risk mitigation (CRM) is what drives regulatory capital requirements and what appears in risk reports on a post-mitigation basis. Â¶58 requires reports to *"identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance."* Concentration reports that show gross exposure without accessible mitigation data cannot be evaluated for capital adequacy. Â¶41 requires capture of all material risk exposures, including off-balance-sheet items; guarantees and collateral arrangements are central to assessing whether an off-balance-sheet exposure is truly material on a net basis. This element is included because the regulation directly supports it and because omitting it would leave a gap a supervisor reviewing concentration risk reports would immediately identify.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 2.** The gross exposure aggregate (CDE-03) can be computed without mitigation data. But net exposure â the figure used for capital purposes and limit monitoring â cannot be correctly stated. Reports show gross where net is required. The aggregate is produced at the gross level but cannot be trusted for capital and concentration purposes.
- **Driven by:** Principle 4 (Â¶41) â all material risk exposures including off-balance-sheet; Principle 7 (Â¶53â56) â accuracy of reports including capital-related measures; Principle 8 (Â¶57â59) â *"risk-related measures (eg regulatory and economic capital)"* and *"inter- and intra-risk concentrations"*
- **Search terms:** collateral ID, collateral type, collateral value, netting agreement ID, guarantee ID, credit risk mitigant, CRM type, eligible collateral, haircut, LGD input, security identifier, ISIN (of collateral)
- **Data quality requirements:**
  - *Completeness* â Every exposure record that has an associated credit risk mitigant carries a non-null mitigant identifier; exposures with no mitigant carry an explicit "none" indicator rather than a null | Count of exposure records where collateral or guarantee is known to exist in the collateral management system but no mitigant identifier appears on the risk record | Target: 0 unlinked mitigants for exposures above materiality threshold
  - *Accuracy* â Mitigant values on risk records match current values in the collateral management or guarantee system | Sum of absolute differences between mitigant values on risk records and collateral management system values, expressed as a percentage of total mitigant book | Target: â¤0.5% unexplained variance; all variances above materiality threshold investigated
  - *Validity* â Mitigant type codes reference entries in the bank's approved collateral/mitigant taxonomy; mitigant currencies are valid ISO 4217 codes | Count of records with invalid mitigant type codes or invalid currency codes | Target: 0 invalid codes

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Cross-System Counterparty Resolution (Single Obligor View)**

- **Spans:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-06 (Business Line), CDE-07 (Geography), CDE-10 (Industry/Sector), CDE-12 (Collateral/Mitigant Identifier)
- **What this is:** Individual CDE-level monitoring â checking that each field is non-null, valid, and internally consistent â does not verify that the same real-world counterparty is resolved to the same identifier across all source systems. A bank may have CDE-01 fully populated and valid within each system individually, while system A calls the same corporate group "Counterparty-001" and system B calls it "Counterparty-847." Every downstream aggregate that aggregates by counterparty â single-name concentration, country exposure, sector exposure â will then fragment the obligor's exposure across two identities. This failure is invisible to any single-element DQ monitor. It can only be detected by cross-system matching.
- **Regulatory grounding:** Â¶33 â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Â¶46(a) â rapid aggregation of credit exposure to a large corporate borrower requires a resolved single identity across all systems
- **Dimension:** Consistency (cross-system)
- **Rule intent:** The same real-world legal entity counterparty maps to the same counterparty identifier in every source system that contributes to risk aggregation; no counterparty appears under multiple identifiers in the consolidated risk view.
- **Measurement:** Count of counterparties where cross-system matching (on LEI, tax identifier, or registration number) identifies multiple active counterparty IDs in scope of the same risk aggregate; percentage of total consolidated exposure affected by such split identities; number of exposure records that would be reassigned under a resolved single-identity view versus the current view.
- **Suggested threshold:** 0 split identities for counterparties above the bank's single-name concentration materiality threshold; full resolution completed for the top-N obligors (where N is defined by senior management) within the agreed remediation timeline.

---

**XDQ-02 â Risk-to-Finance Reconciliation Completeness (Portfolio Level)**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (GL/System-of-Record Reconciliation Key), CDE-01 (Counterparty Identifier), CDE-02 (Legal Entity Identifier), CDE-08 (Position Date)
- **What this is:** Individual element monitoring on CDE-09 verifies that every risk record carries a reconciliation key and that the key resolves to a GL entry. That is necessary but not sufficient. The cross-cutting requirement is that the *total* of risk data aggregates â summed by legal entity, risk type, and position date â reconciles to the corresponding accounting balances in the general ledger, and that all breaks are identified, explained, and within agreed tolerance. This cannot be expressed as a property of any single data element. It requires comparing two populations (risk system totals and GL totals) after joining on CDE-09 and grouping on CDE-02, CDE-08, and CDE-05. Breaks arise from timing differences, scope differences, and measurement differences (e.g., amortised cost vs. fair value), all of which must be documented and approved. Without this reconciliation, Â¶36(c) and Â¶53(a) cannot be evidenced.
- **Regulatory grounding:** Â¶36(c) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Â¶53(a) â *"Defined requirements and processes to reconcile reports to risk data"*; Â¶36(a) â controls as robust as those applicable to accounting data
- **Dimension:** Accuracy (portfolio-level), Completeness (population-level)
- **Rule intent:** The sum of risk exposures in the risk system, grouped by legal entity and position date, reconciles to the corresponding carrying amounts in the general ledger within an approved tolerance; all differences are categorised (timing, scope, measurement basis) and individually approved; no unexplained residual exists above the materiality threshold.
- **Measurement:** (a) Total unexplained variance between risk system portfolio total and GL balance by legal entity and position date, expressed as an absolute amount and as a percentage of total portfolio; (b) Count and value of reconciliation breaks open beyond the agreed resolution SLA; (c) Percentage of total portfolio covered by record-level reconciliation (via CDE-09 key matches) versus only summary-level reconciliation â this ratio measures the quality of CDE-09 population.
- **Suggested threshold:** Unexplained variance â¤ the bank's approved accounting materiality threshold; 100% of breaks above materiality threshold investigated and resolved or approved within 2 business days; record-level reconciliation coverage â¥ 95% of portfolio value (residual 5% covered by documented summary reconciliation with approved exception).

---

**XDQ-03 â Temporal Consistency Across Aggregation Dimensions (Batch Integrity)**

- **Spans:** CDE-08 (Position Date), CDE-01 (Counterparty Identifier), CDE-02 (Legal Entity Identifier), CDE-06 (Business Line), CDE-07 (Geography), CDE-10 (Industry/Sector), CDE-03 (Gross Exposure Amount)
- **What this is:** Individual monitoring of CDE-08 verifies that each record carries a valid position date. The cross-cutting requirement is that *within any single aggregation run*, all records contributing to the same aggregate carry the same position date â that no mixing of T and T-1 (or earlier) positions occurs across source systems with different cut-off times. This is particularly acute when multiple source systems feed a consolidated aggregate: system A may close at 18:00 and feed T positions, while system B is delayed and feeds T-1 positions, and the combined aggregate silently mixes the two. This mixing cannot be detected by monitoring position date on individual records â it requires comparing the distribution of position dates across all records within a batch.
- **Regulatory grounding:** Principle 5 (Â¶44â46) â timely aggregation requires that the aggregate reflects a defined moment; Â¶50 â *"aggregate risk data quickly â¦ as of a specified date"* presupposes temporal consistency; Principle 7 (Â¶52â53) â reconciliation to accounting data requires a common as-of date
- **Dimension:** Consistency (temporal), Timeliness
- **Rule intent:** Within any aggregation batch declared as "as of date D," 100% of contributing records carry position date D; any records with a different position date are identified, flagged, and excluded from the batch with their impact quantified and reported.
- **Measurement:** For each aggregation batch, count and percentage of records with position date â  declared batch as-of date; total exposure value of temporally inconsistent records as a percentage of batch total; comparison of this percentage across source systems to identify which systems are consistently late.
- **Suggested threshold:** 0% of records in any regulatory aggregation batch carry a position date other than the declared as-of date, except where a documented late-feed policy applies and the impact is quantified; late-feed exceptions logged and reported to the data quality governance forum within the same business day.

---

## 4. Out of Scope

The following table identifies which principles (and which aspects of principles that also drove CDEs) are not addressable through a data catalog's CDE register or data quality monitoring.

---

### Principles 8â11 (reporting practices): report content, format, frequency, and distribution

**Principles 8 (Comprehensiveness), 9 (Clarity and Usefulness), 10 (Frequency), and 11 (Distribution)** are primarily obligations about how risk *reports* are designed, governed, and delivered to their recipients â not about the properties of underlying data elements. A CDE register and DQ monitoring framework cannot satisfy these requirements and should not claim to.

**Principle 8 â Comprehensiveness (Â¶57â60):**
Â¶57 requires that reports cover all significant risk areas and components, including capital adequacy and liquidity ratios. Â¶58 requires forward-looking forecasts and stress test results. Â¶59 specifies a list of report content including regulatory capital, liquidity ratio projections, and funding positions. Â¶60 requires forward-looking assessment, not just current and past data. These are obligations on the *content and analytical depth of reports* â specifically on the completeness of risk coverage, the inclusion of scenario analysis, and the forward-looking perspective â that no data catalog can enforce or monitor.

**However, Principle 8 also directly drives CDEs.** Â¶57 names industry sector and country as report dimensions; these drove CDE-10 and CDE-07. Â¶57 also names regulatory and economic capital measures, which require underlying data (exposure, risk weight, LGD). The split is: the *data elements* that feed the required report dimensions are in scope for the catalog; the *report itself* â its content completeness, its analytical narrative, its forward-looking adequacy â is not. The catalog governs the inputs; the reporting governance framework governs the output. Both are required for compliance; neither substitutes for the other.

**Principle 9 â Clarity and Usefulness (Â¶61â69):**
Â¶61â68 govern whether reports are clear, appropriately balanced between quantitative and qualitative content, tailored to their audience, and interpreted rather than merely presented. Â¶67 requires an inventory and classification of risk data items referenced in reports â this is close to what a catalog provides, but it is an obligation about the *report inventory*, not the data asset inventory. Â¶69 requires periodic confirmation with recipients that information is relevant and appropriate. These are governance and communication obligations that require human judgment: they cannot be automated, profiled, or scored by a monitoring tool.

**Principle 10 â Frequency (Â¶70â71):**
Â¶70â71 require that report frequency be set by recipients, reviewed periodically, and tested for feasibility under stress. Â¶71 requires that critical position and exposure reports be available within a very short period, potentially intraday, under stress. CDE-08 (Position Date) and XDQ-03 (batch temporal consistency) address the *data timeliness* precondition â records must be available and correctly timestamped. But the frequency obligations â deciding which reports are produced daily vs. weekly vs. intraday, testing that production timelines are met, and escalating when they are not â are operational and governance obligations. A catalog cannot set report frequency, test production run times, or confirm distribution to recipients.

**Principle 11 â Distribution (Â¶72â74):**
Â¶72â73 require procedures for rapid dissemination of reports to appropriate recipients while maintaining confidentiality, and periodic confirmation that the right people receive timely reports. These are report delivery and access-control obligations. Data confidentiality is referenced in Principle 1 (Â¶27) as well. A catalog can document which data assets are confidential and which steward owns access decisions â that is within scope. But the distribution procedures themselves, the confirmation that the right person received the right report at the right time, and the balance between rapid dissemination and confidentiality are operational and governance obligations outside the catalog's domain.

---

### Principle 1 â Governance (Â¶27â31): board accountability, independent validation, resource allocation

Principle 1 drives the *reason* a bank needs CDEs and DQ monitoring â it establishes that the board and senior management are accountable for the risk data aggregation framework, that independent validation must be conducted, and that resources must be allocated. These are institutional governance obligations.

A catalog supports Principle 1 compliance by providing evidence: stewardship assignments (Â¶34), documented metadata (Â¶33, Â¶37), and DQ monitoring results. But the following aspects of Principle 1 cannot be satisfied by catalog content:

- Â¶28: Board review and approval of the aggregation and reporting framework â this is a board resolution, not a data asset.
- Â¶29(a): Independent validation by staff with IT, data, and reporting expertise â this is an assurance activity; the catalog may be examined during validation, but cannot conduct it.
- Â¶29(b): Assessment of acquisitions' risk data capabilities during due diligence â this requires human judgment applied to a specific transaction.
- Â¶30: Senior management awareness of limitations (coverage gaps, model limitations, legal impediments to cross-jurisdictional data sharing) â awareness requires communication and governance processes, not metadata.
- Â¶31: Board awareness of implementation limitations â same point.

---

### Principle 2 â Data Architecture (Â¶32â35): infrastructure, business continuity, roles and responsibilities

Principle 2 drives several CDEs and the rationale for a unified taxonomy. But the following aspects are outside catalog scope:

- Â¶32: Business continuity planning and business impact analysis for risk data processes â these are operational resilience obligations requiring BCP documentation and testing.
- Â¶34: Roles and responsibilities for data ownership across business and IT â a catalog can *record* stewardship assignments, but it cannot *establish* them. Role definition requires organisational authority; the catalog is the registry, not the governance body.
- Â¶35: Ensuring risk data aggregation capabilities meet all principles simultaneously â this is an architectural quality assurance obligation requiring system testing, not metadata management.

---

### Principle 3 â Accuracy and Integrity (Â¶36â40): independent validation, escalation channels, remediation

Principle 3 drives several CDEs and two cross-cutting DQ requirements. But:

- Â¶38: The appropriate balance between automated and manual systems, including professional judgement â this is a process design obligation; the catalog can flag which processes are manual (CDE-11), but cannot prescribe the right balance.
- Â¶40: Escalation channels and action plans for poor data quality â the catalog can surface DQ scores and threshold breaches; it cannot operate the escalation process, assign remediation owners, or track resolution. Those require workflow and governance infrastructure (issue tracking, data quality councils) beyond the catalog itself.

---

### Principle 5 â Timeliness (Â¶44â47): stress-scenario production capabilities

Principle 5 drives CDE-08 (Position Date) and informs XDQ-03. But Â¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis"* â this is a systems engineering obligation. The catalog can record that a system is designated as a critical feed and document its SLA, but it cannot build or test the production capability itself. Stress-scenario production testing (Â¶47, Â¶70) requires operational exercises, not metadata.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | P2 (Â¶33), P4 (Â¶41), P5 (Â¶46) | Uniqueness, Completeness, Consistency |
| CDE-02 | Legal Entity Identifier (Booking Entity) | 3 | P2 (Â¶33), P4 (Â¶41) | Validity, Completeness, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | P3 (Â¶36a), P4 (Â¶41), P5 (Â¶46a) | Accuracy, Completeness, Timeliness |
| CDE-04 | Transaction / Reporting Currency | 2 | P3 (Â¶36a), P4 (Â¶41â43), P6 (Â¶50) | Validity, Accuracy, Timeliness |
| CDE-05 | Risk Type Classification | 2 | P3 (Â¶37), P7 (Â¶57), P8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-06 | Business Line | 2 | P4 (Â¶41), P6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-07 | Geography / Country of Risk | 2 | P4 (Â¶41), P6 (Â¶50), P8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-08 | Position Date / As-Of Date | 3 | P5 (Â¶44â46), P6 (Â¶50), P7 (Â¶52â53) | Validity, Consistency, Timeliness |
| CDE-09 | GL / System-of-Record Reconciliation Key | 3 | P3 (Â¶36c), P3 (Â¶36d), P7 (Â¶53a) | Completeness, Accuracy, Uniqueness |
| CDE-10 | Industry / Sector Classification | 2 | P4 (Â¶41), P6 (Â¶50), P8 (Â¶57) | Completeness, Validity, Consistency |
| CDE-11 | Source System / Data Provenance Flag | 2 | P3 (Â¶36b), P3 (Â¶36d), P3 (Â¶39) | Completeness, Validity, Accuracy |
| CDE-12 | Collateral / Credit Risk Mitigant Identifier | 2 | P4 (Â¶41), P7 (Â¶53â56), P8 (Â¶57â59) | Completeness, Accuracy, Validity |

**Cross-cutting DQ requirements:**

| ID | Name | Spans | Dimensions |
|---|---|---|---|
| XDQ-01 | Cross-System Counterparty Resolution | CDE-01, 03, 06, 07, 10, 12 | Consistency (cross-system) |
| XDQ-02 | Risk-to-Finance Reconciliation Completeness | CDE-03, 09, 01, 02, 08 | Accuracy, Completeness |
| XDQ-03 | Temporal Consistency Across Aggregation Dimensions | CDE-08, 01, 02, 06, 07, 10, 03 | Consistency (temporal), Timeliness |