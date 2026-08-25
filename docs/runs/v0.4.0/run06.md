# BCBS 239 â Data Catalog Interpretation: CDEs, DQ Monitoring, and Scope Limits

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a board-level governance obligation.** Boards and senior management must approve the risk data aggregation framework, understand its limitations, and ensure adequate resources are deployed. The failure mode BCBS 239 addresses is boards making capital and risk decisions on figures they cannot trust and cannot interrogate. (Â¶28: *"A bank's board and senior management should review and approve the bank's group risk data aggregation and risk reporting framework and ensure that adequate resources are deployed."*)

- **A single authoritative data architecture.** Banks must establish integrated data taxonomies, metadata, single identifiers, and unified naming conventions across the group â covering legal entities, counterparties, customers, and accounts. Fragmented, system-specific identifiers are explicitly the problem to be solved. (Â¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*)

- **Accuracy and reconcilability as parallel requirements.** Risk data must be accurate, and that accuracy must be evidenced by reconciliation to authoritative sources, including accounting data. A figure that is plausible but unreconciled does not satisfy the standard â the ability to prove accuracy is part of the requirement, not a bonus. (Â¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."*)

- **Complete capture across the full group and all material exposures.** Aggregation must cover every business line, legal entity, asset type, industry, region, and off-balance-sheet item. Gaps must be identified, quantified, and explained â not silently omitted. (Â¶41: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*)

- **Timeliness under stress, not just in normal conditions.** The system must be capable of producing aggregated risk data rapidly during crisis â including intraday for certain positions. Timeliness requirements apply specifically to credit, counterparty, trading, liquidity, and operational risk. (Â¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*)

- **Reconciled, validated reporting with full lineage.** Risk reports must be reconciled to risk data, supported by an inventory of validation rules, and must be capable of explaining errors and data weaknesses through exception reporting. The provenance of data â including manual and end-user-computing inputs â must be documented. (Â¶39: *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual."*)

**Who it applies to**

BCBS 239 applies to **Global Systemically Important Banks (G-SIBs)** as a mandatory standard, with an original implementation deadline of January 2016. The Basel Committee extended the expectation to **domestic systemically important banks (D-SIBs)** at national supervisors' discretion, typically within three years of designation. In practice, supervisors across the EU (SSM), UK (PRA), US (Fed/OCC), and other major jurisdictions apply BCBS 239 expectations broadly to any bank whose failure would have systemic consequences. The principles govern the **banking group** as a whole â holding company, subsidiaries, and branches â not individual legal entities in isolation.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Identifier**

- **Definition:** A single, persistent, group-wide identifier assigned to each counterparty â legal entity, natural person, or other obligor â that allows all exposures to that counterparty to be aggregated across systems, business lines, and geographies. This is a resolving key, not a display name.
- **Why critical:** Without a common counterparty identifier, it is impossible to sum credit exposure, counterparty credit risk, or concentration risk across systems. Every aggregation in every risk dimension passes through this key. It is also the join that makes single-name concentration limits operational.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3.** Without this element, the aggregate figure *total group exposure to counterparty X* cannot be computed at all, because exposures held in different systems cannot be matched to the same obligor. The figure is structurally impossible, not merely degraded.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶46(a)â(b)) â aggregated credit exposure to a large borrower and counterparty credit risk are named as critical risks requiring rapid aggregation
- **Search terms:** Customer ID, counterparty ID, obligor ID, client identifier, entity ID, CIF (Customer Information File), LEI (Legal Entity Identifier), global party ID, golden record ID, party master
- **Data quality requirements:**
  - *Uniqueness* â Each counterparty has exactly one active group-wide identifier; no duplicates exist across systems | Count of counterparty identifiers that resolve to more than one master record | Target: 0 duplicates in the golden source
  - *Completeness* â Every exposure record carries a non-null counterparty identifier | Count of exposure records with a null or blank counterparty identifier field | Target: 0 nulls on any in-scope exposure record
  - *Validity* â Every counterparty identifier on an exposure record resolves to an active record in the counterparty master | Count of exposure records whose counterparty identifier does not match any active entry in the master register | Target: 0 unresolved references
  - *Consistency* â The same counterparty is represented by the same identifier across all source systems | Count of counterparties where the identifier differs between two or more source systems for the same underlying entity | Target: 0 cross-system mismatches

---

**CDE-02 â Legal Entity Identifier (Own Entity)**

- **Definition:** The identifier for each of the bank's own booking entities â subsidiary, branch, or holding company â within which a transaction or exposure is recorded. This is the bank's own entity hierarchy, not the counterparty's.
- **Why critical:** Group consolidation and subsidiary-level reporting both require that every exposure be attributed to an own legal entity. Without this, it is impossible to produce entity-level capital adequacy figures, to roll up from subsidiary to group, or to identify which entity bears the risk. Â¶33 names legal entities explicitly as requiring unified naming conventions.
- **Risk types:** Credit, market, liquidity, operational, cross-cutting
- **Criticality: 3.** Without this element, the aggregate figure *group consolidated exposure* cannot be computed or evidenced because individual entity contributions cannot be identified and summed; nor can subsidiary-level reports be reconciled to the group total.
- **Driven by:** Principle 2 (Â¶33) â *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (Â¶41) â *"A bank's risk data aggregation capabilities should include all material risk exposures"* across the banking group; Principle 1 (Â¶30) â senior management must understand limitations including subsidiaries not included
- **Search terms:** Legal entity ID, booking entity, entity code, subsidiary code, branch code, LEI (own entity), organisational unit ID, cost centre entity, reporting entity, consolidation entity, group entity hierarchy
- **Data quality requirements:**
  - *Completeness* â Every exposure or position record carries a non-null own legal entity identifier | Count of records with a null entity identifier | Target: 0 nulls
  - *Validity* â Every entity identifier on a record matches an active entry in the official group legal entity register | Count of records referencing an entity code not present in the master entity register | Target: 0 invalid references
  - *Consistency* â The entity hierarchy (parent-child relationships) is consistent across risk systems and the consolidation ledger | Count of entity-to-parent mappings that differ between the risk data store and the group structure register | Target: 0 discrepancies

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary amount representing a bank's exposure before the application of risk mitigants (collateral, guarantees, netting). Denominated in the transaction currency, with a base-currency equivalent required for aggregation. For derivatives, this includes positive mark-to-market and potential future exposure components as appropriate to the risk measure in use.
- **Why critical:** This is the primary quantity that risk aggregation acts upon. Every aggregate risk figure â total credit exposure, concentration, capital consumption â is computed from this amount. It is the number being summed.
- **Risk types:** Credit, counterparty, market, concentration
- **Criticality: 3.** Without this element, the aggregate figure *total credit exposure to sector X* cannot be computed at all; there is no quantity to sum. This is the scalar the entire aggregation pipeline operates on.
- **Driven by:** Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (Â¶41) â all material risk exposures must be captured; Principle 5 (Â¶46(a)) â *"The aggregated credit exposure to a large corporate borrower"* is named as a critical risk measure
- **Search terms:** Exposure at default (EAD), gross exposure, notional amount, outstanding balance, drawn amount, mark-to-market (MtM), replacement cost, current exposure, position amount, nominal value, outstanding principal
- **Data quality requirements:**
  - *Accuracy* â Exposure amounts reconcile to the general ledger or system of record within defined tolerance | Sum of exposure amounts per entity in the risk system compared to the corresponding balance in the accounting ledger; tolerance defined as a percentage of total portfolio | Suggested threshold: variance â¤ 0.1% of total portfolio value
  - *Completeness* â No material exposure category is excluded from the aggregate | Count of exposure records with a null or zero amount where the counterparty is active and the facility is drawn | Target: 0 nulls on drawn in-scope records
  - *Validity* â Amounts are expressed in a recognised currency and, where converted, the conversion rate is traceable to a dated reference rate | Count of records where the currency code is absent or does not match an ISO 4217 code | Target: 0 invalid currency codes
  - *Timeliness* â Exposure amounts reflect the position as of the stated as-of date, within the agreed settlement cycle | Age of the most recent update to each exposure record relative to the declared as-of date | Target: all records updated within the agreed processing window

---

**CDE-04 â Risk Type / Risk Classification**

- **Definition:** The categorical assignment of an exposure or position to a primary risk type â credit risk, market risk, liquidity risk, operational risk, counterparty credit risk â and, where applicable, to a sub-type (e.g. single-name credit, settlement risk, trading book market risk). This is the taxonomy that partitions the risk universe for aggregation and capital calculation purposes.
- **Why critical:** Risk reports are organised by risk type. If an exposure is misclassified, it appears in the wrong risk bucket and distorts both the aggregate for the correct bucket and the aggregate for the bucket it was wrongly assigned to. Capital requirements, limit monitoring, and stress test results all depend on this classification.
- **Risk types:** Cross-cutting (the classification itself spans all risk types)
- **Criticality: 2.** If this element is wrong, the aggregate figure *total credit risk exposure* is produced but includes misclassified items, making it incorrect for the misclassified portion â the figure is produced but cannot be trusted in the relevant slice.
- **Driven by:** Principle 7 (Â¶52) â *"Risk management reports should be accurate and precise to ensure a bank's board and senior management can rely with confidence on the aggregated information"*; Principle 8 (Â¶57) â *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 2 (Â¶33) â integrated data taxonomies across the banking group
- **Search terms:** Risk type code, risk category, risk class, risk taxonomy, asset class, risk flag, exposure type, portfolio classification, book type (banking book / trading book), risk bucket
- **Data quality requirements:**
  - *Validity* â Every exposure record carries a risk type code that is drawn from the approved enterprise risk taxonomy | Count of records where the risk type code is null or does not match an approved taxonomy value | Target: 0 invalid or null classifications
  - *Consistency* â The risk type assigned in the risk system matches the classification used in the capital calculation and in regulatory reporting | Count of records where the risk type code differs between the risk data store and the regulatory reporting extract | Target: 0 classification mismatches
  - *Accuracy* â Risk type assignments are reviewed and corrected when product or instrument characteristics change | Staleness of last-reviewed date on risk type assignment relative to the most recent product change event | Target: all reclassification reviews completed within the agreed review cycle

---

**CDE-05 â Business Line**

- **Definition:** The organisational classification that assigns an exposure or position to a defined business segment â for example, corporate banking, retail banking, trading, private banking, treasury. Must align to the group's official business line hierarchy used in management reporting and capital allocation.
- **Why critical:** Principle 4 explicitly requires that risk data be available by business line. Without a reliable business line attribute, the bank cannot produce business-line-level risk reports, cannot monitor limits at the business line level, and cannot decompose group-level concentrations. Principle 6 (Â¶50) requires the ability to aggregate across all business lines on demand.
- **Risk types:** Cross-cutting
- **Criticality: 2.** If this element is absent or inconsistent, the aggregate *credit risk exposure by business line* is produced but cannot be correctly partitioned; slices are invalid, not the total.
- **Driven by:** Principle 4 (Principle heading and Â¶41) â *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (Â¶50) â *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date â¦ across all business lines and geographic areas"*
- **Search terms:** Business line code, business unit code, segment code, division code, product line, desk code, profit centre, line of business (LOB), management reporting unit, business segment
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null business line code | Count of exposure records with a null or blank business line code | Target: 0 nulls
  - *Validity* â Every business line code resolves to an active entry in the official business line hierarchy | Count of records whose business line code is not present in the current approved hierarchy | Target: 0 invalid codes
  - *Consistency* â Business line assignments are consistent between the risk system and the management accounting system | Count of records where the business line code differs between the risk data store and the management accounts extract | Target: 0 cross-system discrepancies

---

**CDE-06 â Geography / Country of Risk**

- **Definition:** The country or geographic region to which an exposure is assigned for risk purposes â typically the country of the ultimate obligor's domicile, the country of the collateral, or the country of the booking entity, depending on the risk type. Must be distinguished from the country of booking where these differ.
- **Why critical:** Principle 4 requires data availability by region; Principle 6 (Â¶50) explicitly names the ability to aggregate country credit exposures on demand as a required capability. Country concentration risk, cross-border exposure limits, and sovereign risk reporting all depend on this element.
- **Risk types:** Credit, market, concentration, cross-cutting
- **Criticality: 2.** If this element is wrong or missing, aggregate *credit exposure by country* is produced but incorrectly partitioned; the total is not invalid but the geographic slice is.
- **Driven by:** Principle 4 (Principle heading) â *"Data should be available by â¦ region"*; Principle 6 (Â¶50) â *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*
- **Search terms:** Country of risk, country code, obligor domicile, country of incorporation, booking country, region code, geographic segment, cross-border flag, country classification, jurisdiction
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null country of risk code | Count of exposure records with a null or blank country code | Target: 0 nulls on in-scope records
  - *Validity* â Every country code conforms to ISO 3166-1 alpha-2 or the bank's approved equivalent | Count of records carrying a country code not present in the approved reference list | Target: 0 invalid codes
  - *Accuracy* â Country of risk assignment reflects the ultimate obligor domicile, not merely the booking location, where these differ | Count of records where country of risk equals country of booking for cross-border exposures (a proxy for potential miscoding) | Threshold set by risk management based on expected cross-border volume

---

**CDE-07 â Industry / Sector Classification**

- **Definition:** The economic sector or industry classification assigned to a counterparty or exposure â for example using a standard scheme such as NACE, GICS, SIC, or a bank-defined equivalent. Used to measure and report industry concentration risk.
- **Why critical:** Principle 4 names industry as a required aggregation dimension; Principle 6 (Â¶50) explicitly requires the ability to aggregate industry credit exposures across all business lines and geographic areas on demand; Principle 8 (Â¶57) names industry sector as a required component of credit risk reports. Sector concentrations are a primary supervisory concern in stressed environments.
- **Risk types:** Credit, concentration
- **Criticality: 2.** If this element is absent or miscoded, the aggregate *credit exposure by industry sector* is produced but incorrectly partitioned; slices are unreliable, not the total.
- **Driven by:** Principle 4 (Principle heading) â *"Data should be available by â¦ industry"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*
- **Search terms:** Industry code, sector code, NACE code, SIC code, GICS classification, industry sector, counterparty sector, economic sector, industry classification, sector taxonomy
- **Data quality requirements:**
  - *Completeness* â Every counterparty master record carries a non-null industry classification | Count of counterparty records with a null industry code | Target: 0 nulls for counterparties with active exposures
  - *Validity* â Every industry code is drawn from the approved classification scheme | Count of records carrying a code outside the approved scheme | Target: 0 invalid codes
  - *Consistency* â Industry classification at the exposure level matches the classification on the counterparty master | Count of exposures where the industry code on the record differs from the code on the counterparty master | Target: 0 discrepancies

---

**CDE-08 â Position / As-Of Date**

- **Definition:** The calendar date as of which an exposure, position, or balance is measured and stated. This is the temporal key for every risk aggregate â the date to which the aggregate refers. Distinct from the transaction date, the settlement date, and the report production date.
- **Why critical:** Every aggregate risk figure is defined as of a specific date. If the as-of date is wrong, absent, or inconsistent across records being summed, the aggregate mixes positions from different dates â it does not represent any coherent point in time. This is the temporal anchor that makes time-series comparison and regulatory point-in-time reporting meaningful. Principle 5 makes timeliness of data a direct regulatory requirement.
- **Risk types:** Cross-cutting
- **Criticality: 3.** Without a consistent and accurate as-of date on every record, the aggregate figure *group credit exposure as of [date]* cannot be computed in any coherent sense, because records from different dates are being combined as though they represent the same moment.
- **Driven by:** Principle 5 (Â¶44) â *"A bank's risk data aggregation capabilities should ensure that it is able to produce aggregate risk information on a timely basis"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (Â¶52â53) â reports must be accurate, reconciled, and validated
- **Search terms:** As-of date, position date, valuation date, reference date, report date, snapshot date, effective date, business date, cut-off date, price date
- **Data quality requirements:**
  - *Completeness* â Every exposure and position record carries a non-null as-of date | Count of records with a null as-of date | Target: 0 nulls
  - *Validity* â The as-of date is a valid calendar date within the expected operating range (not a future date beyond the next business day, not prior to the system go-live date) | Count of records where the as-of date is outside the expected valid range | Target: 0 invalid dates
  - *Timeliness* â Records for a given as-of date are available within the agreed processing window following that date | Elapsed time between the as-of date and the timestamp of record availability in the aggregation layer | Target: within the agreed SLA for each risk type (as defined per Principle 5 requirements)
  - *Consistency* â All records contributing to a given aggregate share the same as-of date; no mixing of dates within a single aggregation run | Count of aggregation batches where records with differing as-of dates are combined in a single aggregate | Target: 0 mixed-date aggregations

---

**CDE-09 â General Ledger / System-of-Record Reference Key**

- **Definition:** The identifier â trade reference number, facility reference, account number, or equivalent â that uniquely identifies the same exposure or position in both the risk data system and the general ledger or authoritative system of record. This is the key that makes reconciliation between risk data and accounting data mechanically possible.
- **Why critical:** Â¶36(c) requires risk data to be reconciled to accounting data. Â¶53(a) requires defined processes to reconcile reports to risk data. Without a common reference key that appears in both the risk system and the ledger, reconciliation can only be performed at aggregate level (which masks offsetting errors) or not at all. An unreconciled figure cannot be evidenced as accurate, which under the regulation is an equivalent failure to an inaccurate figure.
- **Risk types:** Cross-cutting (reconciliation spans all risk types)
- **Criticality: 3.** Without this element, the aggregate figure *total credit exposure per the risk system* cannot be reconciled to the general ledger at all â not because the figure is wrong, but because there is no mechanical basis on which to verify it. An unverifiable figure is not a compliant one under Â¶36(c).
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** Trade ID, facility ID, account number, deal reference, booking reference, GL account code, ledger reference, position ID, instrument ID, transaction reference, system reference number, source system key
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a non-null system-of-record reference key | Count of risk records with a null or blank reconciliation key | Target: 0 nulls
  - *Uniqueness* â Each reference key identifies exactly one record in the source system of record | Count of reference keys that return more than one record in the system of record | Target: 0 ambiguous keys
  - *Validity* â Every reference key resolves to an active record in the general ledger or authoritative source system | Count of risk records whose reference key does not match any record in the source system | Target: 0 unresolved keys
  - *Consistency* â The exposure amount on the risk record agrees with the balance on the corresponding ledger entry within defined tolerance | Count of matched pairs where the variance exceeds the defined materiality threshold | Threshold aligned to the accounting materiality standard applied in Â¶56

---

**CDE-10 â Source System Identifier / Data Provenance Flag**

- **Definition:** The attribute that identifies, for each risk data record, the originating source system and whether the data entered the aggregation pipeline via an automated feed, a manual upload, or an end-user computing (EUC) process (e.g. spreadsheet). Where a manual adjustment or override has been applied, the nature and authorisation of that adjustment should be captured.
- **Why critical:** Â¶39 requires documentation of all risk data aggregation processes, automated or manual, with explanations of manual workarounds. Â¶36(b) requires effective mitigants for manual processes and EUC tools. Without knowing the provenance of a data record, it is impossible to assess its reliability, apply appropriate controls, or explain to a supervisor why a figure is correct. A risk report that cannot answer "where did this number come from" does not meet Â¶39.
- **Risk types:** Cross-cutting
- **Criticality: 2.** If this element is absent, the aggregate is produced but cannot be validated â the bank cannot demonstrate whether the figure came from an authoritative automated source or from an uncontrolled spreadsheet. The provenance failure degrades the evidential basis, not the arithmetic.
- **Driven by:** Principle 3 (Â¶36(b)) â *"effective mitigants in place (eg end-user computing policies and procedures) and other effective controls that are consistently applied"*; Principle 3 (Â¶39) â *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual"*
- **Search terms:** Source system code, source system name, feed type, data origin flag, manual override indicator, EUC flag, spreadsheet flag, automated feed indicator, data provider, feed ID, extraction method, manual adjustment flag, override reason code
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a non-null source system identifier | Count of records with a null or blank source system code | Target: 0 nulls
  - *Validity* â Every source system code resolves to a registered entry in the data source inventory | Count of records whose source system code is not present in the approved source inventory | Target: 0 unregistered sources
  - *Accuracy* â Records flagged as manual or EUC-sourced are accompanied by a documented justification and an approval record | Count of manual/EUC-flagged records without a linked justification or approval | Target: 0 undocumented manual inputs entering production aggregation
  - *Timeliness* â The source system flag is assigned at the point of ingestion, not retrospectively | Count of records where the source system code was assigned after the as-of date plus the agreed processing window | Target: 0 retrospective assignments in production

---

**CDE-11 â Net Exposure / Collateral and Credit Risk Mitigant Amount**

- **Definition:** The monetary value of eligible collateral, guarantees, or other credit risk mitigants recognised against an exposure, along with the resulting net (post-mitigation) exposure amount. Covers both financial collateral and guarantees that reduce effective credit exposure for regulatory and internal capital purposes.
- **Why critical:** Principle 8 (Â¶58) requires risk reports to *"provide information in the context of limits and risk appetite/tolerance"* â which for credit risk requires both gross and net exposure. The difference between gross and net exposure drives regulatory capital consumption and limit headroom. An aggregate computed on gross exposure will overstate capital requirements where mitigation is material; an aggregate on net exposure may understate concentration where mitigation is concentrated in a single counterparty. Both views are needed for complete reporting.
- **Risk types:** Credit, counterparty, concentration
- **Criticality: 2.** If collateral amounts are wrong, the aggregate *net credit exposure* is produced but overstates or understates the post-mitigation risk figure; the gross figure is unaffected. The slice â post-mitigation view â is unreliable, not absent.
- **Driven by:** Principle 4 (Â¶41) â all material risk exposures must be captured; Principle 8 (Â¶58) â *"Reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance"*
- **Search terms:** Collateral value, collateral amount, eligible collateral, haircut, net exposure, post-mitigation exposure, guarantee amount, credit risk mitigation (CRM), collateral ID, security value, pledged assets, netting set value
- **Data quality requirements:**
  - *Accuracy* â Collateral values reflect current market valuations within the required frequency for the asset class | Age of the most recent collateral valuation relative to the as-of date | Target: valuations not older than the agreed revaluation cycle (e.g. daily for financial collateral)
  - *Completeness* â Every exposure that has associated collateral carries a non-null collateral amount | Count of facilities recorded as collateralised in the credit system where the collateral amount is null | Target: 0 null amounts for collateralised exposures
  - *Validity* â Collateral types are coded to the approved eligibility list for the applicable capital framework | Count of collateral records coded to a type not on the approved eligibility list | Target: 0 invalid type codes

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Cross-System Counterparty Resolution**

*Spans: CDE-01 (Counterparty Identifier), CDE-05 (Business Line), CDE-06 (Geography), CDE-07 (Industry), CDE-03 (Gross Exposure Amount)*

- **Regulatory basis:** Â¶33 â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Â¶50 â the requirement to aggregate country and industry exposures *"across all business lines and geographic areas"* is only achievable if all business lines use the same counterparty identifier to refer to the same obligor.
- **The problem this addresses:** Each business line or source system may maintain its own local counterparty record. CDE-01 addresses uniqueness within a single system. XDQ-01 addresses whether a counterparty identifier from System A and a counterparty identifier from System B that refer to the same legal person are actually mapped to the same master record. This is a cross-system matching problem that no single CDE's own monitoring can detect.
- **Dimension:** Consistency (cross-system)
- **Rule intent:** Every active counterparty that appears in more than one source system is resolved to exactly one master counterparty record; no counterparty is represented by two distinct master IDs across the group
- **Measurement:** Count of counterparty master records that share the same name, LEI, tax identifier, or other matching attribute but carry different master IDs â indicating a split record that would cause the same counterparty's exposures to aggregate into separate buckets; supplemented by the count of cross-system exposure pairs (same underlying obligor in two systems) that cannot be joined on counterparty ID
- **Suggested threshold:** Zero unresolved splits for counterparties whose combined exposure across systems exceeds the bank's single-name concentration reporting threshold; a defined remediation SLA for lower-exposure splits

---

**XDQ-02 â Risk-to-Finance Reconciliation Coverage**

*Spans: CDE-03 (Gross Exposure Amount), CDE-09 (GL / System-of-Record Reference Key), CDE-02 (Legal Entity), CDE-08 (As-Of Date)*

- **Regulatory basis:** Â¶36(c) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Â¶53(a) â *"Defined requirements and processes to reconcile reports to risk data"*
- **The problem this addresses:** CDE-09 monitors whether individual records carry a valid reconciliation key. XDQ-02 monitors whether the reconciliation process actually covers the full population â that is, whether every exposure in the risk system has been matched and compared to a ledger entry, and what proportion remains unmatched. A high individual-record validity score on CDE-09 is meaningless if 15% of the portfolio is structurally excluded from reconciliation because no reconciliation process exists for that product type or entity.
- **Dimension:** Completeness (reconciliation coverage), Accuracy (reconciliation outcome)
- **Rule intent:** Every material exposure category, booking entity, and product type is included in the periodic risk-to-finance reconciliation process; no category is exempt by default; unexplained variances are escalated and resolved within the agreed cycle
- **Measurement:**
  - (a) *Coverage:* Percentage of total exposure amount (by entity, product type, and risk class) included in the reconciliation process, measured against the full in-scope population | Target: 100% of material categories in scope; any exclusion documented and approved
  - (b) *Variance:* Sum of absolute differences between risk system exposure amounts and general ledger balances, expressed as a percentage of total portfolio value, for matched records | Target: within the materiality threshold defined under Â¶56
  - (c) *Break resolution:* Count of open reconciliation breaks older than the agreed resolution SLA | Target: 0 breaks exceeding the SLA without an approved escalation and remediation plan

---

**XDQ-03 â End-to-End Data Lineage Completeness**

*Spans: CDE-10 (Source System / Provenance), CDE-09 (GL / System-of-Record Reference Key), CDE-03 (Gross Exposure Amount), CDE-08 (As-Of Date)*

- **Regulatory basis:** Â¶39 â *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual"*; Â¶29(a) â risk data aggregation processes should be *"fully documented and subject to high standards of validation"*
- **The problem this addresses:** CDE-10 monitors whether individual records carry a source system flag. XDQ-03 monitors whether the complete lineage chain â from originating system, through all transformation steps, to the final aggregated figure in the risk report â is documented and traceable. A single record's provenance flag is necessary but not sufficient; the requirement is that a supervisor or internal auditor can trace any aggregate figure back through every processing step to its source records. This cannot be expressed as a property of any single data element.
- **Dimension:** Completeness (lineage documentation), Accuracy (transformation fidelity)
- **Rule intent:** For every aggregated risk figure published in a risk report, a complete lineage path exists from report figure to source system records, with each transformation step documented; manual interventions at any step are individually identified, quantified, and explained
- **Measurement:**
  - (a) *Lineage coverage:* Percentage of risk report line items for which a documented end-to-end lineage path exists | Target: 100% of material report line items
  - (b) *Manual step identification:* Count of transformation steps in the aggregation pipeline that are not covered by a documented process description or control | Target: 0 undocumented steps in the production pipeline
  - (c) *Manual volume:* Percentage of total exposure amount flowing through at least one manual or EUC step in the pipeline | Monitored against a bank-defined acceptable threshold; trend monitored over time with a target of reduction

---

## 4. Out of Scope

The following principles impose obligations that a data catalog, a CDE register, and data quality monitoring collectively cannot satisfy. Stating this clearly is a precondition for a proportionate and credible implementation.

---

**Principle 7 (Accuracy) â partial**
Principle 7 drives CDE-09 (the reconciliation key) and contributes to several DQ rules. However, Â¶53(b) requires *"an inventory of the validation rules that are applied to quantitative information â¦ including explanations of the conventions used to describe any mathematical or logical relationships."* Maintaining this inventory, executing the validation rules in report production, and managing the exception workflow (Â¶53(c)) are obligations of the risk reporting system and its operating procedures â not of a data catalog. A catalog can document that validation rules exist and link to their definitions, but it cannot own or execute them.

---

**Principle 8 (Comprehensiveness)**
This principle both drives CDEs and remains partly out of scope â and it is important to be explicit about the split.

*What it drives:* Â¶57 names industry sector as a required report component, which is the basis for CDE-07. Â¶58 references limits and risk appetite context, which supports CDE-11 (collateral/net exposure). To that extent, Principle 8 is addressed above.

*What it does not drive in a catalog:* Â¶57â60 also require that reports cover *all* material risk areas, include forward-looking forecasts and stress test results, address capital adequacy and liquidity ratios, and provide the board with a forward-looking assessment of the risk profile. These are content requirements for risk management reports â what must be in them, how they must be organised, and what forward-looking analysis they must contain. A data catalog can confirm that the underlying data elements are present; it cannot determine whether the report's analytical content, scope coverage, or forward-looking narrative is adequate. That requires governance review of report content by risk management and the board.

---

**Principle 9 (Clarity and Usefulness)**
Â¶61â69 are entirely out of scope for data catalog and DQ monitoring purposes. The requirement is that reports are comprehensible and useful to their recipients â that the balance of quantitative and qualitative information is appropriate, that conclusions are drawn, that the board can use the information to exercise its governance mandate. Â¶67 requires *"an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"* â this is a business glossary requirement that a catalog can support, but the remainder of Principle 9 concerns human judgement about report design and governance dialogue between the board and senior management. No technical control addresses it.

---

**Principle 10 (Frequency)**
Â¶70â71 require the board and senior management to set report frequency, test report production capability under stress, and ensure that critical position and exposure reports are available within very short timeframes (intraday in some cases). These are operational readiness, business continuity, and governance obligations. A data catalog can document the agreed frequency standards as metadata against a dataset, but it cannot enforce SLAs, test production under stress, or demonstrate intraday capability. Those require technology architecture, operational testing programmes, and governance attestation processes.

---

**Principle 11 (Distribution)**
Â¶72â73 concern report dissemination procedures and access controls â ensuring the right people receive reports and that confidentiality is maintained. This is a process and access management obligation. A catalog can document who is designated as a report recipient, but the distribution mechanism, access controls, and periodic confirmation of appropriate receipt (Â¶73) are outside catalog scope.

---

**Principle 1 (Governance) â the framework itself**
Principle 1 is what the entire implementation is accountable to, but its core obligations are not satisfiable by data infrastructure. Â¶27â31 require the board to approve the framework, senior management to understand its limitations, independent validation to be conducted, and the implications of acquisitions and divestitures to be assessed at board level. A catalog supports these activities by making metadata, lineage, and quality evidence available for independent review. It does not itself constitute the governance framework, and populating a catalog does not discharge the board's approval obligation.

---

**Principle 2 (Data Architecture) â the infrastructure itself**
Principle 2 requires that data architecture and IT infrastructure *fully support* aggregation capabilities in normal and stressed conditions (Â¶32â35). The CDE register and DQ monitoring are outputs of good data architecture â they do not substitute for it. Business continuity planning (Â¶32), IT ownership and lifecycle controls (Â¶34), and the existence of integrated, resilient systems are engineering and organisational obligations that precede and exceed what any catalog can provide.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | 2 (Â¶33), 4, 5 (Â¶46) | Uniqueness, Completeness, Validity, Consistency |
| CDE-02 | Legal Entity Identifier (Own Entity) | 3 | 2 (Â¶33), 4 (Â¶41), 1 (Â¶30) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3 (Â¶36), 4 (Â¶41), 5 (Â¶46) | Accuracy, Completeness, Validity, Timeliness |
| CDE-04 | Risk Type / Risk Classification | 2 | 2 (Â¶33), 7 (Â¶52), 8 (Â¶57) | Validity, Consistency, Accuracy |
| CDE-05 | Business Line | 2 | 4 (heading), 6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | 2 | 4 (heading), 6 (Â¶50) | Completeness, Validity, Accuracy |
| CDE-07 | Industry / Sector Classification | 2 | 4 (heading), 6 (Â¶50), 8 (Â¶57) | Completeness, Validity, Consistency |
| CDE-08 | Position / As-Of Date | 3 | 5 (Â¶44), 6 (Â¶50), 7 (Â¶52) | Completeness, Validity, Timeliness, Consistency |
| CDE-09 | GL / System-of-Record Reference Key | 3 | 3 (Â¶36(c)), 7 (Â¶53(a)) | Completeness, Uniqueness, Validity, Consistency |
| CDE-10 | Source System / Data Provenance Flag | 2 | 3 (Â¶36(b), Â¶39), 1 (Â¶29) | Completeness, Validity, Accuracy, Timeliness |
| CDE-11 | Net Exposure / Collateral Amount | 2 | 4 (Â¶41), 8 (Â¶58) | Accuracy, Completeness, Validity |

*Criticality 3 elements: CDE-01, CDE-02, CDE-03, CDE-08, CDE-09 â five elements, consistent with the target range of 4â5.*