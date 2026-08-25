# BCBS 239: Data Catalog Governance Requirements

---

## 1. Objectives and Scope

**What the regulation is trying to achieve:**

- **Reliable risk aggregation as a precondition for sound governance.** The regulation requires that boards and senior management can obtain accurate, complete and timely aggregate risk data â not just in normal conditions but during stress and crisis â to make effective risk decisions. The aggregation capability must exist before reporting can be trusted. (Â¶35: *"risk data aggregation capabilities should ensure that risk management reports reflect the risks in a reliable way (ie meeting data aggregation expectations is necessary to meet reporting expectations)"*)

- **A single authoritative data architecture, not a patchwork of systems.** Banks must establish integrated data taxonomies, single identifiers, and unified naming conventions across the group. The absence of a common identifier for a counterparty or legal entity is not an operational inconvenience â it is a structural compliance failure. (Â¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions"*)

- **Accuracy evidenced through reconciliation, not assumed.** Risk data must be reconciled with source systems and accounting data. The regulation treats unreconciled risk data with the same seriousness as unreconciled accounting data. (Â¶36(a),(c): *"Controls surrounding risk data should be as robust as those applicable to accounting data"* and *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*)

- **Complete coverage across all material dimensions.** Aggregation must be possible by business line, legal entity, asset type, industry, region, and other relevant groupings. Incompleteness must be measured, monitored, and explained â not simply tolerated. (Â¶43: *"Supervisors expect banks to produce aggregated risk data that is complete and to measure and monitor the completeness of their risk data"*)

- **Timeliness calibrated to risk type and crisis conditions.** Different risks require different speeds. Systems must be capable of rapid aggregation for critical risks â credit concentrations, counterparty exposures, trading positions, liquidity indicators â under stress. (Â¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks"*)

- **Documented lineage for all processes, automated or manual.** Every risk data aggregation process must be documented. Manual workarounds and end-user computing applications are permitted but must be identified, explained, and subject to controls. (Â¶39: *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*)

**Who it applies to:**

BCBS 239 Principles 1â11 apply to **Global Systemically Important Banks (G-SIBs)** with a mandatory compliance deadline (January 2016 in the original publication). National supervisors may extend the principles to **Domestic Systemically Important Banks (D-SIBs)**. The principles apply at the **consolidated banking group level**, covering all legal entities, subsidiaries, and material business lines within the group, including off-balance-sheet exposures (Â¶41).

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Unique Identifier**
- **Definition:** A single, persistent, system-independent identifier assigned to each counterparty (legal entity, corporate group, individual) that is used consistently across all systems in which that counterparty's exposures are recorded. This is the primary key for linking exposures to a counterparty across the banking group.
- **Why critical:** Without a common counterparty identifier, it is impossible to aggregate total exposure to a single counterparty across booking systems, asset classes, or legal entities. Any aggregate credit exposure figure is unverifiable and any concentration analysis is incomplete.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3** â Aggregation is impossible without it. The absence of a resolvable counterparty identifier does not degrade an aggregate figure: it invalidates it. No group-level counterparty exposure can be stated as reliable without this key.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶41) â *"risk data aggregation capabilities should include all material risk exposures"*; Principle 5 (Â¶46(a),(b)) â *"aggregated credit exposure to a large corporate borrower"* and *"counterparty credit risk exposures"* named as critical risks requiring rapid aggregation
- **Search terms:** counterparty ID, client ID, party ID, legal entity identifier, LEI, global party ID, customer master ID, obligor ID, counterparty reference data
- **Data quality requirements:**
  - *Uniqueness* â Each counterparty is assigned exactly one identifier in the authoritative counterparty master; no two records in that master share the same identifier | Count of duplicate identifier values in the counterparty master | 0 duplicates tolerated
  - *Completeness* â Every exposure record carries a non-null, resolvable counterparty identifier | Count of exposure records where counterparty identifier is null or does not resolve to a record in the counterparty master | Target: 0; breach triggers escalation
  - *Consistency* â The identifier used in risk systems matches the identifier used in the general ledger and in the counterparty master for the same counterparty | Count of counterparty identifiers present in risk exposure data that do not have a matched record in the counterparty master | Target: 0 unmatched

---

**CDE-02 â Legal Entity Identifier (Booking Entity)**
- **Definition:** The identifier of the bank's own legal entity in which an exposure is booked. This is distinct from the counterparty identifier: it identifies which part of the banking group owns the position, not who the position is with.
- **Why critical:** Group consolidation â summing exposures across all subsidiaries to produce a group-level aggregate â requires knowing which legal entity each exposure belongs to. Without this, the bank cannot perform intra-group eliminations, cannot produce subsidiary-level reports, and cannot demonstrate that all legal entities are included in the consolidated view.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 3** â Group consolidation is impossible without it. An aggregate that purports to cover the banking group but cannot enumerate and sum exposures by booking entity cannot be validated as complete. The failure invalidates the consolidated figure, not merely a dimension of it.
- **Driven by:** Principle 2 (Â¶33) â *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (header) â *"capture and aggregate all material risk data across the banking group"* and data should be available *"by business line, legal entity"*; Principle 1 (Â¶30) â *"limitations that prevent full risk data aggregation, in terms of coverage (eg risks not captured or subsidiaries not included)"*
- **Search terms:** legal entity identifier, LEI, booking entity, entity code, subsidiary code, legal entity master, group entity ID, organisational unit code, reporting entity
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null legal entity identifier | Count of exposure records with null or unrecognised booking entity code | Target: 0
  - *Validity* â Every legal entity identifier on an exposure record resolves to an active, in-scope entity in the group's legal entity master | Count of exposure records referencing entity codes not present in the active legal entity master | Target: 0
  - *Consistency* â The set of legal entities represented in risk data matches the set defined as in-scope in the governance framework | List of legal entities in risk data not in the approved scope list, and vice versa | Any discrepancy requires documented explanation

---

**CDE-03 â Gross Exposure Amount**
- **Definition:** The monetary amount representing an obligor's or position's exposure before the application of credit risk mitigants, netting, or collateral. Expressed in the transaction currency (see CDE-09). This is the base monetary input from which net exposure, risk-weighted assets, and concentration measures are derived.
- **Why critical:** This is the primary quantity that risk aggregation operates on. Every credit risk aggregate â single-name exposure, sector concentration, country exposure â is ultimately a sum or transformation of gross exposure amounts. Errors here propagate into every downstream risk figure.
- **Risk types:** Credit, counterparty, concentration
- **Criticality: 3** â An exposure figure that is wrong or missing does not degrade a risk aggregate: it distorts it. Given that this is the quantity being summed, its failure invalidates the resulting aggregate.
- **Driven by:** Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (Â¶41) â *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** exposure at default, EAD, gross exposure, committed exposure, notional amount, drawn amount, outstanding balance, credit exposure, face value, principal amount
- **Data quality requirements:**
  - *Accuracy* â The sum of gross exposure amounts for a given entity and date in the risk system agrees with the corresponding balance in the general ledger within a defined tolerance | Variance between risk system aggregate and GL balance by legal entity and asset class as of the same position date | Tolerance to be defined against accounting materiality per Â¶56; breaches escalated
  - *Completeness* â Off-balance-sheet exposures (contingent, undrawn, derivative) are present in the risk data alongside on-balance-sheet exposures | Count of facility types defined as material but absent from the risk exposure population for a given reporting date | Target: 0 defined types missing
  - *Validity* â Exposure amounts are non-negative and within a plausible range for the instrument type | Count of records where exposure amount is negative, zero for a live position, or outside instrument-type-specific bounds | Target: 0

---

**CDE-04 â Risk Type Classification**
- **Definition:** The categorical label that assigns an exposure or position to a primary risk type â credit risk, market risk, liquidity risk, operational risk, counterparty credit risk â according to the bank's approved risk taxonomy. This is not a description field: it is the primary partition key for risk aggregation.
- **Why critical:** Risk reports are organised by risk type. Aggregating across risk types without this classification produces meaningless totals. Misclassification moves exposure from one risk bucket to another, distorting capital calculations, limit consumption, and report completeness across all sections.
- **Risk types:** Cross-cutting (the classification itself spans all risk types)
- **Criticality: 3** â A report that purports to show total credit risk exposure cannot be validated if its input population is undefined. Misclassification invalidates the affected aggregate rather than merely degrading a dimension of it.
- **Driven by:** Principle 2 (Â¶33) â *"establish integrated data taxonomies and architecture across the banking group"*; Principle 3 (Â¶37) â *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"*; Principle 8 (Â¶57) â *"exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*
- **Search terms:** risk type, risk category, risk class, risk taxonomy code, primary risk type, risk classification, risk flag, product risk type
- **Data quality requirements:**
  - *Validity* â Every exposure record carries a risk type value that is a member of the approved, version-controlled risk taxonomy | Count of exposure records with risk type values not present in the current approved taxonomy | Target: 0
  - *Completeness* â No exposure record is unclassified | Count of exposure records with null or blank risk type | Target: 0
  - *Consistency* â The risk type assigned in the risk system is consistent with the product/instrument classification in the source booking system | Count of records where the risk type in the risk system contradicts the product-level risk mapping defined in the taxonomy | Target: 0 contradictions

---

**CDE-05 â Business Line**
- **Definition:** The identifier of the internal business line or business unit responsible for the exposure, defined according to the bank's approved organisational taxonomy. Examples include retail banking, corporate banking, investment banking, treasury, and private banking.
- **Why critical:** Principle 4 explicitly requires that risk data be aggregable by business line. Without a reliable business line attribute, the bank cannot produce the business-line-sliced views of risk exposure required for management reporting, nor demonstrate completeness across all business lines.
- **Risk types:** Credit, market, liquidity, cross-cutting
- **Criticality: 2** â The aggregate is still produced but one required reporting dimension is unsliceable or unreliable. A null or incorrect business line does not invalidate the total exposure figure; it prevents the bank from producing a valid business-line breakdown, which is a named regulatory requirement.
- **Driven by:** Principle 4 (header and Â¶43) â data should be available *"by business line"* and banks should *"measure and monitor the completeness of their risk data"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries, as well as industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*
- **Search terms:** business line, business unit, division, desk code, segment code, organisational unit, cost centre, front office unit, business segment
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null business line identifier | Count of exposure records with null or blank business line | Target: 0
  - *Validity* â Business line values are members of the current approved organisational taxonomy | Count of records referencing decommissioned, unrecognised, or unmapped business line codes | Target: 0
  - *Consistency* â The business line assigned in risk systems matches the assignment in the general ledger for the same position | Count of records where business line in risk data does not match the business line in the corresponding GL record | Breaches require documented explanation

---

**CDE-06 â Country / Geography**
- **Definition:** The country or geographic region associated with an exposure, defined consistently â either as the country of the counterparty's domicile, the country of the obligor's primary risk, or the country of the collateral, depending on the risk type. The bank must define and document which geographic concept is used for each risk type.
- **Why critical:** Principle 4 requires aggregation by region. Country-level credit exposure aggregation is explicitly cited in Â¶50 as an example of required ad hoc aggregation capability. Geographic concentration is a named output of risk reporting (Â¶57).
- **Risk types:** Credit, market, concentration
- **Criticality: 2** â Geographic aggregation degrades but overall exposure totals remain intact. Missing or incorrect geography prevents the bank from producing country-level concentration reports and responding to supervisory ad hoc requests of the type described in Â¶50.
- **Driven by:** Principle 4 (header) â *"data should be available by â¦ region"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"* as required components of risk reports
- **Search terms:** country code, country of risk, domicile country, obligor country, geographic region, ISO country code, country of incorporation, country of exposure, region code
- **Data quality requirements:**
  - *Completeness* â Every credit exposure record carries a non-null country of risk assignment | Count of credit exposure records with null or blank country code | Target: 0
  - *Validity* â Country values conform to the approved reference list (e.g., ISO 3166-1) | Count of records with country codes not in the approved reference list | Target: 0
  - *Consistency* â The country concept used (domicile vs. country of risk vs. collateral location) is applied uniformly within each risk type and documented in metadata | Presence of documented mapping rules per risk type; count of records where country assignment method deviates from the documented rule | Deviations require explanation

---

**CDE-07 â Industry / Sector Classification**
- **Definition:** The industry or economic sector to which a counterparty or exposure is assigned, based on a defined classification system such as NACE, SIC, NAICS, or an internal taxonomy. This is the industry dimension required for sector concentration analysis.
- **Why critical:** Sector concentration is a named risk output requirement. Industry-level aggregation of credit exposures is explicitly cited in Â¶50 as a required ad hoc capability. Missing or inconsistent sector data prevents the production of sector-level concentration reports.
- **Risk types:** Credit, concentration
- **Criticality: 2** â Industry-level slicing degrades but exposure totals are not invalidated. However, the bank cannot satisfy the specific ad hoc aggregation requirement described in Â¶50 without it.
- **Driven by:** Principle 4 (header) â *"data should be available by â¦ industry"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*

  *Note on Principle 8:* Principle 8 is primarily a reporting practice principle (see Section 4), but it independently names industry sector as a required data dimension. The CDE derives from that data requirement; the broader report content and comprehensiveness obligations of Principle 8 remain outside the scope of a CDE register.

- **Search terms:** industry code, sector code, NACE code, SIC code, NAICS code, industry classification, economic sector, business sector, counterparty industry
- **Data quality requirements:**
  - *Completeness* â Every corporate credit exposure record carries a non-null industry classification | Count of corporate credit exposure records with null or blank industry code | Target: 0 for material portfolios
  - *Validity* â Industry codes are members of the approved classification standard in use | Count of records with codes not present in the approved version of the classification standard | Target: 0
  - *Consistency* â Industry classification is applied at the counterparty level (not per-facility) and all facilities for a counterparty carry the same industry code unless a documented multi-industry assignment rule applies | Count of counterparties with facilities carrying differing industry codes without a documented exception | Target: 0 undocumented inconsistencies

---

**CDE-08 â Position / As-Of Date**
- **Definition:** The business date as of which an exposure or position is measured and stated. This is the temporal key that makes an aggregate meaningful: "total credit exposure to sector X" is only an interpretable figure if it is stated as of a specific date.
- **Why critical:** Every aggregate in BCBS 239 is implicitly or explicitly time-stamped. Without a reliable position date, it is impossible to verify that exposures in an aggregate are contemporaneous, to reconcile against the general ledger as of the same date, or to reconstruct a historical position for supervisory review. Timeliness monitoring â Principle 5 â is entirely predicated on measuring latency between the position date and the report generation date.
- **Risk types:** Cross-cutting
- **Criticality: 3** â Without a position date, a risk aggregate cannot be defined: it is not possible to state what the aggregate measures or to verify it against any other source. An undated aggregate is not degraded â it is uninterpretable.
- **Driven by:** Principle 5 (header) â *"generate aggregate and up-to-date risk data in a timely manner"*; Principle 5 (Â¶46) â critical risks listed require timely aggregation on a named-date basis; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (Â¶52) â reports must be *"accurate and precise"* so boards can rely on them
- **Search terms:** position date, as-of date, value date, reporting date, trade date, snapshot date, data as of, reference date, business date
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null position date | Count of records with null position date | Target: 0
  - *Timeliness* â The latency between position date and availability of the aggregated risk dataset does not exceed the bank's defined SLA for each risk type (e.g., T+1 for standard credit reporting, intraday for trading exposures under stress) | Measured elapsed time between position date and dataset availability by risk type and reporting frequency | Breach defined by SLA per risk type; stress-mode SLAs separately monitored per Â¶45
  - *Validity* â Position dates are valid business dates (not weekends, not future dates, not dates prior to the bank's defined history horizon) | Count of records with position dates that are non-business days, future dates, or outside the defined history window | Target: 0

---

**CDE-09 â Transaction Currency**
- **Definition:** The currency in which an exposure or position is denominated at the time of booking. Distinct from the reporting currency into which the exposure is translated for consolidated reporting.
- **Why critical:** Multi-currency aggregation requires currency as a joining dimension. Without it, FX conversion cannot be applied correctly, currency concentration cannot be measured, and the translation from transaction currency to reporting currency â which must be reconciled back to the GL â cannot be performed. Errors in currency produce systematic distortions in every monetary aggregate.
- **Risk types:** Market, credit, liquidity, cross-cutting
- **Criticality: 2** â The aggregate can be produced, but currency translation errors degrade its accuracy. Missing currency does not prevent an exposure from being counted but prevents it from being correctly valued in the consolidated reporting currency, producing a degraded â and potentially materially misstated â aggregate.
- **Driven by:** Principle 3 (Â¶36(a),(c)) â reconciliation with accounting data requires consistent currency handling; Principle 4 (Â¶41) â *"all material risk exposures"* requires capturing denominated amounts correctly; Principle 5 (Â¶46(c)) â *"Trading exposures, positions â¦ and market concentrations by sector and region"* implies multi-currency aggregation
- **Search terms:** currency code, transaction currency, deal currency, ISO currency code, base currency, denominated currency, notional currency, position currency
- **Data quality requirements:**
  - *Validity* â Currency codes are members of the ISO 4217 standard | Count of records with currency codes not in the ISO 4217 approved list | Target: 0
  - *Completeness* â Every monetary exposure record carries a non-null currency code | Count of monetary exposure records with null or blank currency code | Target: 0
  - *Consistency* â The currency on a risk record matches the currency recorded for the same transaction in the general ledger | Count of records where currency in risk system differs from currency in GL for the same transaction reference | Target: 0

---

**CDE-10 â General Ledger Reconciliation Key**
- **Definition:** The identifier â typically a trade reference number, deal ID, account number, or journal entry reference â that links a risk data record to its corresponding entry in the general ledger or primary system of record. This is not a risk-specific identifier: it is the bridge between the risk data layer and the accounting layer.
- **Why critical:** This is the element that makes reconciliation between risk and finance operationally possible. Principle 3 requires that risk data be reconciled with accounting data (Â¶36(c)) and that risk controls be as robust as accounting controls (Â¶36(a)). Without this key, reconciliation degenerates into approximate balance-matching at aggregate level, which cannot identify individual mispostings, double-counts, or missing records. Supervisors will look for evidence of reconciliation at record level, not just at total level.
- **Risk types:** Cross-cutting (applies to every risk type that has a corresponding accounting entry)
- **Criticality: 3** â Record-level reconciliation between risk and finance is impossible without this key. The regulation explicitly demands reconciliation (Â¶36(c)); balance-sheet-level totals matching is insufficient evidence of that requirement. The absence of this key means the accuracy requirement of Principle 3 cannot be evidenced â the figure may be right, but it cannot be proved to be right.
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** deal ID, trade reference, transaction ID, GL account reference, journal ID, source transaction ID, facility ID, trade ID, booking reference, account number, source system key
- **Data quality requirements:**
  - *Completeness* â Every risk record that has a corresponding accounting entry carries a non-null GL reconciliation key | Count of risk records expected to have a GL entry where the reconciliation key is null | Target: 0; exceptions require documented explanation per Â¶39
  - *Uniqueness* â The reconciliation key resolves to exactly one record in the general ledger or source system of record (no fan-out) | Count of reconciliation keys that match more than one GL record | Target: 0; any fan-out must be documented as an intentional one-to-many relationship
  - *Accuracy* â The monetary amount on the risk record matches the monetary amount on the corresponding GL record for the same key within defined tolerance | Sum of absolute variances between matched risk and GL records, expressed as a proportion of total portfolio value | Tolerance defined by accounting materiality threshold per Â¶56

---

**CDE-11 â Source System Identifier and Manual Override Flag**
- **Definition:** Two related but distinct attributes on every risk data record: (a) the identifier of the source system or feed from which the record originated, and (b) a flag indicating whether the record or any of its material fields were subject to manual entry, manual adjustment, or end-user computing (EUC) input (e.g., a spreadsheet or manual database). Together these constitute the provenance record for every data item in the risk aggregation chain.
- **Why critical:** The regulation requires that all risk data aggregation processes â automated and manual â be documented (Â¶39). Manual processes and EUC are permitted only with effective mitigants (Â¶36(b)). Without source system identification, it is impossible to trace a risk figure back to its origin, diagnose root causes of errors, assess systemic exposure to a single failing feed, or demonstrate to supervisors that manual processes are controlled. Without the manual flag, the bank cannot monitor the proportion of its risk data that is derived from manual processes â a key governance indicator.
- **Risk types:** Cross-cutting
- **Criticality: 2** â Aggregates are produced, but lineage cannot be traced and manual-process risk cannot be quantified. The failure degrades the bank's ability to evidence governance and diagnose accuracy failures rather than directly invalidating any single aggregate figure.
- **Driven by:** Principle 3 (Â¶36(b)) â *"where a bank relies on manual processes and desktop applications â¦ it should have effective mitigants in place"*; Principle 3 (Â¶36(d)) â *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (Â¶39) â *"banks to document and explain all of their risk data aggregation processes whether automated or manual â¦ including an explanation of the appropriateness of any manual workarounds"*; Principle 2 (Â¶33) â *"information on the characteristics of the data (metadata)"*
- **Search terms:** source system, feed name, data source code, originating system, system of record, manual entry flag, EUC flag, override indicator, manual adjustment flag, data lineage, feed identifier
- **Data quality requirements:**
  - *Completeness* â Every risk data record carries a non-null source system identifier | Count of records with null or blank source system identifier | Target: 0
  - *Completeness* â Every risk data record carries a populated manual/EUC flag (the flag must be present and set, not merely absent) | Count of records where the manual flag is null rather than explicitly set to true or false | Target: 0
  - *Validity* â Source system identifiers resolve to entries in an approved, maintained system inventory | Count of records referencing source system codes not present in the approved inventory | Target: 0; unrecognised source codes are treated as a lineage break
  - *Timeliness* â The proportion of risk records derived from manual or EUC sources is measured at each reporting cycle and trends are monitored | Percentage of records flagged as manual or EUC origin by risk type and business line, trended over reporting cycles | No fixed threshold; material increase from baseline triggers governance review per Â¶30

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Group-Level Counterparty Consolidation Integrity**

*Spans: CDE-01 (Counterparty Unique Identifier), CDE-02 (Legal Entity), CDE-03 (Gross Exposure Amount), CDE-08 (Position / As-Of Date)*

This requirement cannot be expressed by monitoring any single CDE. It tests whether the bank can reliably produce a consolidated view of total exposure to a single counterparty across all booking entities, asset classes, and source systems â which is the primary aggregation objective of BCBS 239. A counterparty identifier that is internally consistent within one system but not resolved across systems produces CDEs that individually pass their own quality checks while jointly failing the aggregation requirement.

- **Driven by:** Â¶33 (*"single identifiers and/or unified naming conventions for data including â¦ counterparties"*); Â¶46(a),(b) â aggregated credit exposure to a large borrower and counterparty CCR exposures are named critical risks requiring rapid aggregation
- **Dimension:** Consistency
- **Rule intent:** For any given counterparty identifier in the authoritative counterparty master, all exposure records linked to that counterparty across all source systems and booking entities â as of the same position date â can be retrieved, summed, and reconciled to a single consolidated figure without residual unmatched records
- **Measurement:** (a) Count of counterparty identifiers in the risk aggregation layer that do not resolve to a record in the authoritative master; (b) Count of source systems that hold exposure records for counterparties without a mapping to the canonical counterparty identifier; (c) For a defined sample of counterparties, variance between the consolidated exposure figure produced by the risk aggregation layer and the figure produced by independently summing exposures from each source system
- **Suggested threshold:** Zero unresolved identifiers and zero unmapped source systems; sample reconciliation variance within the bank's defined accounting materiality threshold per Â¶56

---

**XDQ-02 â Risk-to-Finance Reconciliation Completeness**

*Spans: CDE-03 (Gross Exposure Amount), CDE-08 (Position / As-Of Date), CDE-09 (Transaction Currency), CDE-10 (GL Reconciliation Key), CDE-11 (Source System Identifier and Manual Override Flag)*

This requirement tests the completeness and accuracy of the bridge between the risk data layer and the general ledger at the portfolio level â not merely at the record level. Principle 3 requires that risk data be reconciled with accounting data; Principle 7 requires that reports be reconciled and validated. A record-level reconciliation key (CDE-10) is necessary but not sufficient: the bank must also demonstrate that the population of risk records is complete relative to the GL population (no records are missing from either side), that currency translation has been applied consistently, and that the reconciliation was performed as of the same position date. None of these can be confirmed by monitoring any single CDE in isolation.

- **Driven by:** Â¶36(a) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Â¶36(c) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Â¶53(a) â *"Defined requirements and processes to reconcile reports to risk data"*
- **Dimension:** Accuracy, Completeness, Consistency
- **Rule intent:** The total gross exposure in the risk aggregation layer, after currency translation to reporting currency, agrees with the corresponding balance in the general ledger as of the same position date, within defined materiality tolerance; and the population of records in the risk layer is neither larger nor smaller than the in-scope population in the GL without a documented explanation
- **Measurement:** (a) Absolute and percentage variance between total risk-layer exposure and total GL balance by legal entity, risk type, and position date; (b) Count of GL records in scope that have no matching risk record (records in GL not in risk â potential omissions); (c) Count of risk records with no matching GL record (records in risk not in GL â potential phantoms or mis-feeds); (d) Count of manual-flagged records (CDE-11) contributing to the reconciling items, as an indicator of manual process risk
- **Suggested threshold:** Monetary variance within the bank's accounting materiality threshold per Â¶56; zero phantom or omission items without documented explanation; material increase in manual-sourced reconciling items triggers governance escalation

---

## 4. Out of Scope

The following requirements are clearly stated in Principles 1â11 but cannot be addressed by a CDE register, data quality monitoring, or metadata management in a data catalog. In each case, the reason is stated plainly.

---

### Principle 1 (Â¶27â31) â Governance framework, board accountability, and independent validation

**What it requires:** A governance framework with board-level approval, SLAs for data processes, data confidentiality and integrity policies, independent validation by IT/data-specialist staff, and explicit board awareness of aggregation limitations.

**Why a catalog cannot deliver it:** A data catalog can document ownership, stewards, and policies, but it cannot constitute a governance framework, conduct independent validation, or hold a board accountable. Governance framework implementation requires a formal programme â a Data Governance Committee or equivalent, board-approved data quality policies, and an internal audit or validation function with independent reporting lines. The catalog is an instrument within that framework, not a substitute for it.

**Partial overlap:** CDE-11 (Source System and Manual Override Flag) supports Â¶29(a) by documenting manual processes in metadata, and the data stewardship assignments supportable in a catalog are a precondition for Â¶34 (roles and responsibilities for data ownership). But these are inputs to governance, not governance itself.

---

### Principle 2 (Â¶32â35) â IT architecture, business continuity, and system integration

**What it requires:** An integrated data architecture and IT infrastructure that supports aggregation under stress, integrated across the banking group, subject to business continuity planning and business impact analysis.

**Why a catalog cannot deliver it:** Data architecture design, system integration, and BCP are engineering and enterprise architecture decisions. A catalog can surface the current state of data sources and lineage, which is valuable input to architecture design. It can document the intended architecture. But it cannot build the integrated infrastructure, enforce single-identifier use at the database level, or test BCP resilience.

**Partial overlap:** Â¶33 directly drives CDE-01 (Counterparty Unique Identifier), CDE-02 (Legal Entity Identifier), and CDE-11 (Source System). These CDEs are necessary conditions for integrated architecture, and governing them in a catalog supports compliance. The infrastructure itself remains out of scope.

---

### Principle 7 (Â¶52â56) â Report reconciliation processes and validation inventory

**What it requires:** Defined reconciliation processes between reports and underlying risk data; an inventory of validation rules applied to quantitative report figures; integrated exception reporting procedures.

**Why a catalog cannot deliver it:** The validation rule inventory (Â¶53(b)) and exception reporting procedures (Â¶53(c)) are operational reporting controls, not metadata records. They require implementation in the report production process â in ETL pipelines, in report generation tools, and in exception workflow systems. A catalog can reference these controls and link them to CDEs, but it cannot execute them or ensure they run correctly in the report production cycle.

**Partial overlap:** CDE-10 (GL Reconciliation Key) and XDQ-02 (Risk-to-Finance Reconciliation Completeness) directly support Â¶53(a). These are addressable through the catalog. The broader control framework around report validation and exception management is not.

---

### Principle 8 (Â¶57â60) â Report comprehensiveness, capital adequacy, forward-looking content

**What it requires:** Risk reports that cover all significant risk areas and components; inclusion of capital adequacy and regulatory capital measures; liquidity ratios; stress testing results; forward-looking forecasts and scenario content; intra- and inter-risk concentrations.

**Why a catalog cannot deliver it:** Report content, forward-looking analysis, scenario design, and capital model outputs are reporting and risk management decisions. No CDE register governs whether a report actually contains stress test results or forward-looking capital projections â that depends on the analytical capability and the reporting process.

**Partial overlap (explicitly stated):** Â¶57 names industry sector as a required report dimension. This drives CDE-07 (Industry / Sector Classification). The underlying data element is addressable in a catalog; whether it is actually presented in the required report, alongside the other required dimensions and content, is a reporting governance matter outside scope. This is not a contradiction: a well-governed data element is a necessary condition for a compliant report, but it is not a sufficient one.

---

### Principle 9 (Â¶61â69) â Report clarity, recipient tailoring, and qualitative interpretation

**What it requires:** Risk reports that balance quantitative data with qualitative analysis; reports tailored to the different needs of the board, senior management, and risk committees; periodic confirmation with recipients that reports are relevant; an inventory and classification of risk data items linked to reporting concepts.

**Why a catalog cannot deliver it:** Whether a risk report is clear, useful, appropriately balanced between quantitative and qualitative content, and tailored to its recipients is a judgment about the report itself â its design, its narrative, and its governance. A catalog cannot assess or enforce these properties. Â¶67 (*"A bank should develop an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"*) is the closest the regulation comes to describing a data catalog directly. That inventory is exactly what a CDE register in a catalog supports. But the clarity, usefulness, and tailoring requirements of the principle as a whole are beyond it.

**Partial overlap:** Â¶67 is directly satisfied by the CDE register in Section 2 and by the business glossary and metadata capabilities of a data catalog. That portion of Principle 9 is in scope. The remainder is not.

---

### Principles 10 and 11 (Â¶70â74) â Report frequency, distribution, and confidentiality

**What they require:** Board and senior management set report frequency calibrated to risk type, volatility, and stress conditions; banks test their ability to produce reports within SLAs; reports are distributed to appropriate recipients with confidentiality maintained; rapid collection and dissemination procedures.

**Why a catalog cannot deliver it:** Frequency governance is a board and senior management decision implemented through report scheduling, SLA agreements, and operational testing. Distribution controls and confidentiality management are implemented in the reporting infrastructure â access controls, distribution lists, secure transmission channels. A data catalog governs the data that feeds reports; it does not govern the report production schedule, the distribution list, or the access controls on report dissemination.

**Partial overlap:** CDE-08 (Position / As-Of Date) supports timeliness monitoring by enabling measurement of latency between position date and data availability. This is a necessary input to assessing whether Principle 10 SLAs are achievable. But the SLA-setting and testing obligations of Principle 10 remain outside scope.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Unique Identifier | 3 | 2, 4, 5 | Uniqueness, Completeness, Consistency |
| CDE-02 | Legal Entity Identifier (Booking Entity) | 3 | 1, 2, 4 | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3, 4, 7 | Accuracy, Completeness, Validity |
| CDE-04 | Risk Type Classification | 3 | 2, 3, 8 | Validity, Completeness, Consistency |
| CDE-05 | Business Line | 2 | 4, 6 | Completeness, Validity, Consistency |
| CDE-06 | Country / Geography | 2 | 4, 6, 8 | Completeness, Validity, Consistency |
| CDE-07 | Industry / Sector Classification | 2 | 4, 6, 8 | Completeness, Validity, Consistency |
| CDE-08 | Position / As-Of Date | 3 | 5, 6, 7 | Completeness, Timeliness, Validity |
| CDE-09 | Transaction Currency | 2 | 3, 4, 5 | Validity, Completeness, Consistency |
| CDE-10 | GL Reconciliation Key | 3 | 3, 7 | Completeness, Uniqueness, Accuracy |
| CDE-11 | Source System Identifier and Manual Override Flag | 2 | 2, 3 | Completeness, Validity, Timeliness |
| XDQ-01 | Group-Level Counterparty Consolidation Integrity | â | 2, 4, 5 | Consistency |
| XDQ-02 | Risk-to-Finance Reconciliation Completeness | â | 3, 7 | Accuracy, Completeness, Consistency |