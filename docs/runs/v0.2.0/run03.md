# BCBS 239 â Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a precondition for sound governance.** The regulation requires that a bank can produce accurate, complete, and timely aggregated risk data â not just for routine reporting but under stress and crisis conditions â so that boards and senior management can make sound decisions. Â¶35: *"risk management reports reflect the risks in a reliable way (ie meeting data aggregation expectations is necessary to meet reporting expectations)."*

- **Integrated data architecture with single identifiers.** Banks must build infrastructure that prevents fragmentation of risk data across systems. Â¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts."*

- **A single authoritative source per risk type, with reconciliation to accounting.** Risk data must be traceable back to verified sources and reconciled to the general ledger. Â¶36(c)â(d): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"* and *"a bank should strive towards a single authoritative source for risk data per each type of risk."*

- **Full coverage across all material dimensions.** Aggregation must span business lines, legal entities, geographies, asset types, and industry sectors â including off-balance-sheet exposures. Â¶41: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."* Â¶50 adds that country and industry credit exposures must be producible *"across all business lines and geographic areas."*

- **Documented lineage and control over manual processes.** Where automated pipelines are not used, manual and end-user-computing processes must be explicitly documented, their criticality assessed, and controls applied consistently. Â¶39: *"Documentation should include an explanation of the appropriateness of any manual workarounds, a description of their criticality to the accuracy of risk data aggregation and proposed actions to reduce the impact."*

- **A data dictionary as a governance foundation.** Consistent concept definitions across the organisation are a named precondition. Â¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation."*

**Who it applies to**

BCBS 239 applies to Global Systemically Important Banks (G-SIBs) as a mandatory standard, with national supervisors expected to apply it on a proportionate basis to other systemically important institutions. It binds banks at group level, meaning obligations extend to subsidiaries and legal entities within the banking group, not merely the parent entity.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Identifier**

- **Definition:** The single, system-independent key that uniquely and persistently identifies a counterparty â whether a corporate borrower, financial institution, or other obligor â across all booking systems, risk engines, and data stores within the banking group. This is the element that makes it possible to sum all exposures to one name.
- **Why critical:** Without a resolved, deduplicated counterparty key, it is impossible to aggregate credit exposure to a single name across business lines or legal entities. Any concentration figure, large-exposure report, or counterparty credit risk calculation depends on this joining key being populated, matched, and non-duplicated. Its failure does not merely degrade an aggregate â it invalidates the aggregate entirely, because partial summation of exposures to the same counterparty misrepresents both the total and the concentration.
- **Risk types:** Credit, counterparty credit risk, concentration
- **Criticality: 3.** Aggregation is impossible without a resolvable counterparty key. A partially matched identifier produces a figure that is arithmetically valid but analytically wrong â it may undercount a concentration that would breach a limit or trigger a regulatory notification. This is the definition of invalidation rather than degradation.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶41â43) â completeness across all material exposures; Principle 5 (Â¶46aâb) â *"aggregated credit exposure to a large corporate borrower"* and *"Counterparty credit risk exposures"* named as critical risk categories requiring rapid aggregation.
- **Search terms:** counterparty ID, party ID, obligor ID, client ID, customer identifier, legal entity identifier, LEI, global counterparty code, relationship ID, GFCID, golden record ID
- **Data quality requirements:**
  - *Uniqueness* â Each distinct legal-person counterparty resolves to exactly one identifier across all systems in scope | Count of counterparty identifier values that map to more than one master record, plus count of master records with more than one active identifier | Target: zero duplicates in the golden record; zero unresolved aliases in active exposure records
  - *Completeness* â Every exposure record carries a populated, non-null counterparty identifier | Count and percentage of exposure records with null, blank, or placeholder counterparty identifier | Target: 0% null rate; any exception requires documented escalation per Â¶40
  - *Validity* â Every counterparty identifier in an exposure record resolves to an active entry in the counterparty master | Count of exposure records whose counterparty identifier does not match any record in the authoritative counterparty reference | Target: 0% unresolved references; broken joins are escalated before any aggregation run
  - *Consistency* â The same counterparty identifier is used for the same legal person in every system that contributes to aggregated risk data (credit system, market risk engine, derivatives platform, GL) | Count of counterparty names or LEIs that are associated with more than one identifier across systems, detected by cross-system reconciliation | Reviewed at each reconciliation cycle; discrepancies logged and resolved within defined SLA

---

**CDE-02 â Legal Entity Identifier (Own Book)**

- **Definition:** The identifier that designates which legal entity within the banking group is the booking entity for a given risk position or exposure. Distinct from the counterparty identifier: this identifies the bank itself (or its subsidiary), not the external party. Sometimes called the booking entity code or solo entity identifier.
- **Why critical:** Group consolidation requires that every exposure can be assigned to the correct solo legal entity, both for group-level aggregation (to avoid double-counting intra-group) and for solo-entity regulatory reporting. Without it, it is impossible to produce subsidiary-level risk reports, to isolate intra-group exposures, or to demonstrate that risk data covers the full scope of the consolidated group. Â¶41 requires coverage of the full banking group; Â¶33 requires single identifiers for legal entities explicitly.
- **Risk types:** Cross-cutting (all risk types at solo and consolidated levels), concentration
- **Criticality: 3.** Without a reliable booking-entity code, it is impossible to produce a correct consolidated group aggregate (intra-group netting is impossible), and equally impossible to produce correct solo-entity reports. Both the consolidated and the subsidiary figures are invalidated, not merely degraded.
- **Driven by:** Principle 2 (Â¶33) â *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (Â¶41) â *"capture and aggregate all material risk data across the banking group"*; Principle 6 (Â¶50) â requires country credit exposures aggregated *"across all business lines and geographic areas"*, which presupposes entity-level attribution.
- **Search terms:** legal entity identifier, LEI, booking entity code, solo entity ID, subsidiary code, group entity code, entity hierarchy, organisational unit code, reporting unit ID
- **Data quality requirements:**
  - *Completeness* â Every risk exposure record carries a populated booking-entity identifier | Count and percentage of exposure records with null or missing legal entity identifier | Target: 0% null rate
  - *Validity* â Every booking-entity identifier in a risk record resolves to a node in the authoritative group legal entity hierarchy | Count of entity codes in risk records that do not exist in the legal entity reference | Target: 0% unresolved; unknown entity codes are quarantined before aggregation
  - *Consistency* â The same legal entity hierarchy structure is used in risk systems and in the general ledger | Comparison of entity code lists between the risk data layer and the finance/GL system; count of codes present in one but absent in the other | Reviewed at each reporting cycle; mismatches prevent consolidated aggregation and trigger immediate escalation

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary amount representing the bank's risk exposure to a counterparty or instrument before the application of mitigants (collateral, netting, guarantees, credit risk mitigation). Expressed in a defined currency. For credit risk this is typically the drawn amount plus undrawn committed amount; for market risk and derivatives it is the mark-to-market or replacement cost value; for liquidity this is the cash-flow or settlement amount. The precise definition varies by risk type, but the element class â a pre-mitigation monetary quantum â is common to all.
- **Why critical:** This is the foundational number from which every risk aggregate is constructed. Capital adequacy figures, large-exposure calculations, concentration metrics, and stress-test outputs all derive from aggregations of this element. If the gross exposure amount is wrong, every downstream aggregate is wrong. Â¶46aâd lists specific exposure types (credit to large corporates, counterparty credit risk including derivatives, trading exposures, liquidity cash flows) as critical risks requiring rapid aggregation â each is a variant of this element.
- **Risk types:** Credit, market, counterparty credit risk, liquidity, concentration
- **Criticality: 3.** A wrong or missing gross exposure amount directly corrupts the aggregate figure. There is no proxy that substitutes for it. The failure invalidates the aggregate.
- **Driven by:** Principle 3 (Â¶36a) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (Â¶41) â completeness of all material risk exposures; Principle 5 (Â¶46) â named critical risk categories are all monetary exposure measures; Principle 7 (Â¶52â53) â reports must *"accurately and precisely convey aggregated risk data."*
- **Search terms:** exposure at default, EAD, drawn amount, notional amount, mark-to-market value, replacement cost, current exposure, gross exposure, face value, outstanding balance, position size, settlement amount, cash flow
- **Data quality requirements:**
  - *Accuracy* â Gross exposure amounts in the risk system reconcile to the corresponding balances in the general ledger or system of record within defined tolerance | Sum of absolute differences between risk system exposure totals and GL balances by entity, risk type, and as-of date; count and value of reconciling items exceeding materiality threshold | Reconciliation performed at each reporting cycle; unreconciled items above materiality threshold escalated before reports are distributed, per Â¶36(c)
  - *Completeness* â No material exposure is absent from the aggregated dataset, including off-balance-sheet items | Count of off-balance-sheet facility types with no corresponding exposure records; coverage ratio of booked facilities to risk records by product type | Off-balance-sheet gap analysis reviewed monthly; any zero-coverage product type requires documented explanation, per Â¶41 and Â¶43
  - *Timeliness* â Exposure amounts reflect positions as of the stated position date and are available within the bank's defined aggregation window for both normal and stress reporting | Lag in hours/days between transaction booking and availability of the exposure record in the risk aggregation layer, measured by risk type | Lag thresholds defined per risk type; breach triggers escalation, per Â¶44â45
  - *Validity* â Exposure amounts are non-negative (or within defined signed-value conventions for derivatives), non-null, and within plausible ranges given instrument type and counterparty credit limit | Count of records with null, zero, or sign-convention-violating amounts by product type; count of amounts exceeding the counterparty's approved credit limit by a defined multiplier | Validated at ingestion; anomalies routed to exceptions report, per Â¶53(c)

---

**CDE-04 â Risk Type Classification**

- **Definition:** The controlled-vocabulary code that assigns each exposure or position to a primary risk type category: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk, or equivalent taxonomy used by the bank. This is the top-level partition of the risk taxonomy. It determines which aggregation methodology, capital model, and reporting framework applies to a given record.
- **Why critical:** Every risk report is organised by risk type. Misclassification routes an exposure into the wrong model, applies the wrong capital treatment, and produces aggregates that are wrong by construction. Â¶57 explicitly lists credit risk, market risk, liquidity risk, and operational risk as the required dimensions of a comprehensive risk report. The classification is not merely descriptive â it is the key that determines which calculation and which aggregate a record enters.
- **Risk types:** Cross-cutting
- **Criticality: 3.** Misclassification does not degrade the correct aggregate â it removes the record from it entirely and inserts it into the wrong one. Both the source and destination aggregates are invalidated. The failure is not partial; it is a complete mismatch of the record to its calculation.
- **Driven by:** Principle 4 (Â¶42) â *"each system should make clear the specific approach used to aggregate exposures for any given risk measure"*; Principle 7 (Â¶53b) â *"an inventory of the validation rules that are applied to quantitative information"* which presupposes that classification codes are governed; Principle 8 (Â¶57) â *"exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*
- **Search terms:** risk type code, risk category, risk classification, asset class code, risk taxonomy, product risk flag, risk bucket, Basel risk category
- **Data quality requirements:**
  - *Validity* â Every risk record carries a risk type code drawn from the bank's approved taxonomy; no free-text or non-standard values | Count of records whose risk type code does not match an entry in the approved risk taxonomy reference | Target: 0% invalid codes; violations quarantined before aggregation
  - *Completeness* â No risk record is missing a risk type classification | Count and percentage of risk records with null or blank risk type code | Target: 0% null rate
  - *Consistency* â The same risk type classification scheme is applied uniformly across all contributing systems and business lines | Comparison of risk type code lists across source systems; count of codes used in one system that are absent from or differently defined in another | Reviewed at each taxonomy update; inconsistencies resolved before cross-system aggregation

---

**CDE-05 â Business Line**

- **Definition:** The code that assigns a risk exposure or position to a defined business unit or division within the bank (e.g., corporate banking, retail banking, global markets, transaction banking, wealth management). The granularity is determined by the bank's own organisational taxonomy, but it must be sufficient to support slicing of aggregated risk data by business line as a reporting dimension.
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. A bank that cannot slice its risk data by business line cannot demonstrate completeness of coverage, cannot identify concentrations within a line of business, and cannot produce the sub-aggregate reports that senior management of individual divisions require. Â¶50 requires country and industry credit exposures to be producible *"across all business lines,"* making this a joining dimension for multi-axis aggregation.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 2.** The group aggregate can still be produced without business line attribution, but the required business-line slice cannot be produced at all, and cross-dimensional aggregations (e.g., credit exposure by business line and country) are impossible. The aggregate is not invalidated, but a required reporting dimension is unavailable â this is degradation rather than invalidation.
- **Driven by:** Principle 4 (Â¶41â43) â *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"* (from the Principle 4 title paragraph); Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas."*
- **Search terms:** business line code, business unit code, division code, segment code, line of business, LOB code, cost centre, profit centre, organisational unit
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a populated business line code | Count and percentage of records with null or missing business line code | Target: <0.1% null rate; any null record excluded from business-line slices and flagged in the exceptions report
  - *Validity* â Every business line code in a risk record resolves to the bank's current approved organisational taxonomy | Count of codes in risk records not present in the active business line reference | Target: 0% invalid codes; stale codes from reorganisations must be remapped
  - *Consistency* â The business line taxonomy used in risk systems matches the taxonomy used in management accounting and GL reporting | Count of business line codes present in risk aggregation but absent from the finance hierarchy, and vice versa | Reconciled at each reporting cycle to support cross-system dimensional analysis

---

**CDE-06 â Geography / Country of Risk**

- **Definition:** The code that identifies the country (or broader geographic region) to which a risk exposure is attributed for aggregation and reporting purposes. For credit risk this is typically the country of the obligor's domicile or the country of risk as defined by the bank's credit policy; for market risk it may be the market of the instrument. The specific attribution rule must be consistently defined and applied.
- **Why critical:** Geography is a named required aggregation dimension under Principle 4. Â¶50 provides the specific, concrete example that a bank must be able to produce *"country credit exposures as of a specified date based on a list of countries"* â this is not a general aspiration but an explicit capability test. Without a consistently coded country of risk, cross-border concentration measurement is impossible and the stress-test scenario in Â¶50 cannot be executed.
- **Risk types:** Credit, market, liquidity, concentration
- **Criticality: 2.** The total aggregate is producible. But the country-level slice â which is explicitly required and tested by supervisors (Â¶50) â cannot be produced or is unreliable. This is a required reporting dimension that degrades, not an element whose failure invalidates the total.
- **Driven by:** Principle 4 â *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"* (Principle 4 title paragraph); Principle 6 (Â¶50) â *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
- **Search terms:** country code, country of risk, country of domicile, obligor country, geographic region code, booking location, ISO country code, jurisdiction code
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a populated country of risk code | Count and percentage of records with null or missing country code | Target: <0.1% null rate; nulls excluded from geographic aggregations and flagged
  - *Validity* â Every country code is drawn from an approved reference (e.g., ISO 3166) or the bank's internal geographic taxonomy; no free-text entries | Count of country code values not present in the approved geographic reference | Target: 0% invalid values
  - *Consistency* â The country attribution rule (country of domicile, country of ultimate risk, country of booking) is applied uniformly across all source systems contributing to geographic aggregations | Comparison of country codes for matched counterparties across systems; count of records where the same counterparty is assigned different countries in different systems | Reviewed at each cycle; inconsistencies require resolution before country-level reports are distributed

---

**CDE-07 â Industry / Sector Classification**

- **Definition:** The code that assigns a counterparty or instrument to an industry or economic sector using a defined classification scheme (e.g., NACE, SIC, GICS, or an internal taxonomy). Used to slice credit risk, concentration risk, and market risk exposures by the counterparty's economic sector.
- **Why critical:** Principle 8 (Â¶57) names *"single name, country and industry sector for credit risk"* as required components of a comprehensive risk report. Principle 6 (Â¶50) names industry credit exposures as an explicit example of the ad hoc aggregation capability supervisors will test. Without a governed industry classification, sector-level concentration cannot be measured and the specific supervisory scenario in Â¶50 cannot be executed.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Total credit exposure is still calculable. The industry-sector slice â named explicitly in Â¶57 and Â¶50 â cannot be produced reliably. Required reporting dimension degrades; total aggregate is not invalidated.
- **Driven by:** Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"* named as required components.

  *Note on the Principle 8 split:* Principle 8 drives this CDE (because industry sector is a required data dimension that must exist in the data before any report can include it), but Principle 8's report-content obligations â the comprehensiveness, depth, and scope of what reports must say â are outside the scope of a data catalog. That split is explained in Section 4.

- **Search terms:** industry code, sector code, NACE code, SIC code, GICS sector, counterparty industry, borrower sector, economic sector, industry classification
- **Data quality requirements:**
  - *Completeness* â Every credit-risk counterparty record carries a populated industry classification code | Count and percentage of credit-risk exposure records with null or missing industry code | Target: <1% null rate for corporate counterparties; retail pools exempt where not applicable
  - *Validity* â Every industry code resolves to an entry in the bank's approved classification scheme | Count of codes in risk records not present in the reference taxonomy | Target: 0% invalid codes
  - *Consistency* â The industry classification scheme is applied uniformly across all business lines and geographies contributing to credit risk aggregations | Count of counterparties assigned different industry codes by different business lines or booking systems | Discrepancies resolved at the counterparty master level before sector aggregations are run

---

**CDE-08 â Position / As-Of Date**

- **Definition:** The date as of which a risk exposure, position, or aggregate is stated. Every risk record â individual transaction, aggregated position, or risk report figure â must carry an unambiguous as-of date so that aggregates can be constructed for a consistent point in time and so that intraday, daily, weekly, and monthly aggregates can be separated and compared.
- **Why critical:** An aggregate of risk data is only meaningful when all contributing records share the same as-of date. Mixing positions from different dates produces a figure that is arithmetically computable but analytically meaningless. Under Principle 5, the bank must produce aggregated data rapidly under stress â which requires that the as-of date is a well-governed filter, not an implicit assumption. Â¶50 makes this concrete: the bank must produce country credit exposures *"as of a specified date."* Without a governed position date on every record, that query cannot be answered.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3.** Without a governed as-of date, it is impossible to construct any time-consistent aggregate. Every aggregate is potentially wrong because records from different dates may be mixed. The failure invalidates rather than degrades because the resulting figure has no defined temporal meaning.
- **Driven by:** Principle 5 (Â¶44â46) â timeliness requires dated aggregates and the ability to produce rapid data at a specified point in time under stress; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (Â¶53) â reconciliation of reports to risk data requires that the data and reports share a common reference date.
- **Search terms:** position date, as-of date, trade date, value date, reporting date, snapshot date, effective date, reference date, data vintage
- **Data quality requirements:**
  - *Completeness* â Every risk exposure record carries a non-null as-of date | Count and percentage of records with null or missing position date | Target: 0% null rate; undated records cannot participate in any aggregate
  - *Validity* â As-of dates are within the expected range for the reporting cycle (not in the future, not older than defined historical cutoff) | Count of records with as-of dates outside the valid window for the current reporting cycle | Validated at ingestion; out-of-window dates quarantined and escalated
  - *Timeliness* â The gap between a transaction's economic date and its availability with a correct as-of date in the risk aggregation layer is within the bank's defined SLA per risk type | Distribution of booking-to-availability lag by risk type and source system | Breach of SLA by risk type escalated to data owner; critical risk types (per Â¶46) held to tighter thresholds

---

**CDE-09 â GL / System-of-Record Reconciliation Key**

- **Definition:** The identifier â typically a transaction reference number, account number, or instrument identifier â that ties a risk data record to its corresponding entry in the general ledger or the authoritative system of record (e.g., a loan management system, a trading system, or a payments platform). This is the element that makes it possible to perform the reconciliation required by Â¶36(c) and to evidence accuracy.

  This element is often not a single field but a compound key: for example, the combination of booking entity, account number, and instrument identifier that is needed to match a risk record to its GL counterpart. For catalog purposes, each component of that compound key is a CDE; here it is treated as a category.

- **Why critical:** Without a reconciliation key, it is impossible to verify that the gross exposure amount in the risk system matches the balance in the GL. The reconciliation mandated by Â¶36(c) â one of the most directly testable requirements in the entire standard â cannot be executed. It is also impossible to demonstrate the accuracy requirement of Principle 3 by any audit-ready method. Principle 7 (Â¶53a) requires *"defined requirements and processes to reconcile reports to risk data"* â this key is the mechanical prerequisite for that process.
- **Risk types:** Cross-cutting (accuracy and integrity across all risk types)
- **Criticality: 3.** Without a reconciliation key, the accuracy assertion in Principle 3 cannot be evidenced at all. The reconciliation process does not degrade â it does not exist. This is the clearest case of invalidation in the register.
- **Driven by:** Principle 3 (Â¶36c) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (Â¶36d) â *"a bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 7 (Â¶53a) â *"defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** transaction reference, deal ID, account number, instrument identifier, trade ID, loan reference, GL account code, position identifier, source transaction ID, system of record key, reconciliation identifier
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a populated reconciliation key linking it to a GL or system-of-record entry | Count and percentage of risk records with null or blank reconciliation key | Target: 0% null rate for all records whose exposure amount flows through the GL; exceptions require documented justification
  - *Validity* â Every reconciliation key in a risk record resolves to a matching entry in the GL or designated system of record | Count of risk records whose reconciliation key has no matching GL entry; count of GL entries that have no matching risk record (both directions of the gap) | Bi-directional reconciliation at each reporting cycle; unmatched items above materiality threshold prevent sign-off on the risk report
  - *Uniqueness* â Each GL entry maps to at most one risk record at a given as-of date (or the mapping logic is explicitly defined and documented for split or aggregated treatments) | Count of GL entries matched to more than one risk record without an approved mapping rule | Reviewed at each cycle; unexplained one-to-many matches escalated immediately
  - *Accuracy* â The exposure amount on the risk record matches the corresponding balance in the GL within defined tolerance | Sum and count of individual reconciling differences by risk type, entity, and as-of date; ageing of unresolved reconciling items | Tolerance thresholds aligned to accounting materiality per Â¶56; aged items escalated through defined channel per Â¶40

---

**CDE-10 â Source System / Lineage Flag**

- **Definition:** The metadata attribute â or set of attributes â that identifies (a) which source system originated a risk data record, and (b) whether the record entered the risk aggregation layer through an automated feed or through a manual process (including end-user computing tools such as spreadsheets or local databases). This is not the transaction data itself; it is the provenance metadata that must accompany every record.
- **Why critical:** Â¶36(b) requires effective controls for manual and EUC processes, explicitly distinguished from automated feeds. Â¶39 requires documentation of all risk data aggregation processes â automated or manual â including an explanation of manual workarounds and their criticality. Without a source system flag and an automation/manual indicator, it is impossible to identify which records are subject to the heightened controls required for manual input, impossible to assess the degree of reliance on manual processes that Â¶30 requires senior management to understand, and impossible to produce the documentation Â¶39 demands. In a catalog context, this is also the element that makes data lineage traceable.
- **Risk types:** Cross-cutting (governance and accuracy across all risk types)
- **Criticality: 2.** Individual risk aggregates can still be computed without provenance metadata. But the accuracy assurance required by Principle 3 is incomplete â manual-process records cannot be subjected to the appropriate heightened scrutiny â and the documentation obligation of Â¶39 cannot be met. The aggregate degrades in auditability and control assurance, even if the number itself is not wrong.
- **Driven by:** Principle 3 (Â¶36b) â *"it should have effective mitigants in place (eg end-user computing policies and procedures) and other effective controls that are consistently applied"*; Principle 3 (Â¶39) â *"document and explain all of their risk data aggregation processes whether automated or manual"*; Principle 1 (Â¶30) â senior management must understand *"degree of reliance on manual processes."*
- **Search terms:** source system name, source system code, feed type, automation flag, manual override indicator, EUC flag, data origin, originating system, pipeline identifier, process type, data provenance tag
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a populated source system identifier and a manual/automated flag | Count and percentage of records with null source system code or null process-type flag | Target: 0% null rate; unprovenance-tagged records cannot be classified for control purposes
  - *Validity* â Every source system code resolves to a registered system in the bank's authoritative application inventory (or data catalog system register) | Count of source system codes in risk records not present in the registered source system list | Target: 0% unregistered sources; unknown sources escalated to data governance team
  - *Accuracy* â Manual-flagged records are subjected to the documented additional controls (e.g., independent checker, version control) and the outcome of those controls is recorded | Count of manual-flagged records without a completed control attestation for the reporting cycle | Reviewed before each report distribution; un-attested manual records are exceptions per Â¶36(b) and Â¶53(c)

---

**CDE-11 â Reporting Currency / FX Rate**

- **Definition:** The currency in which an exposure amount is denominated, and the exchange rate applied to convert it to the bank's reporting currency for aggregation. These two elements are inseparable for aggregation purposes: the exposure currency identifies whether conversion is needed, and the FX rate determines the converted value. Without both, multi-currency aggregation produces incorrect totals.
- **Why critical:** A bank operating across multiple currencies cannot aggregate credit or market risk exposures into a single consolidated figure without currency conversion. A missing or stale FX rate is not a cosmetic error â it changes the reported aggregate. For stress testing and scenario analysis (Â¶48â50), the ability to apply scenario-specific FX rates is explicitly required by adaptability. Under Principle 5, rapidly produced stress aggregates must use rates consistent with the scenario's as-of date.
- **Risk types:** Credit, market, liquidity, concentration (wherever multi-currency aggregation is performed)
- **Criticality: 2.** Within a single currency, aggregation is unaffected. Across currencies, the consolidated aggregate is distorted but not absent â an approximate figure is produced. This is degradation rather than invalidation, because the calculation completes but with error.
- **Driven by:** Principle 4 (Â¶41â43) â completeness of aggregation across the banking group (which is inherently multi-currency for any international bank); Principle 5 (Â¶45â46) â rapid aggregation under stress requires timely and scenario-consistent rate application; Principle 6 (Â¶48â49) â adaptability to stress scenarios and changing conditions includes currency scenarios.
- **Search terms:** transaction currency, denomination currency, ISO currency code, FX rate, exchange rate, conversion rate, spot rate, reporting currency, base currency, rate as-of date
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a populated transaction currency code | Count and percentage of records with null or missing currency code | Target: 0% null rate
  - *Validity* â Every currency code is drawn from the ISO 4217 standard or the bank's approved currency reference | Count of currency codes not present in the approved reference | Target: 0% invalid codes
  - *Timeliness* â FX rates used for conversion are sourced as of the same as-of date as the exposure records they convert | Count of exposure records converted using an FX rate whose as-of date differs from the position date by more than the bank's defined tolerance | Stale-rate exceptions escalated before aggregated reports are finalised; stress runs use scenario-specified rates, not current rates
  - *Accuracy* â Converted exposure amounts reconcile to an independent FX rate source within defined basis-point tolerance | Count and value of conversion discrepancies exceeding tolerance when compared against a validated external rate source | Reviewed at each aggregation run

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Counterparty Deduplication and Single-View Resolution Across Systems**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-05 (Business Line), CDE-07 (Industry/Sector Classification)
- **The problem this addresses:** Multiple source systems â a corporate lending platform, a derivatives booking system, a trade finance system, a bond portfolio system â each maintain their own counterparty records. The same legal-person counterparty may appear under different names, different internal IDs, and different industry classifications in each. No individual CDE monitor on any one system detects this cross-system fragmentation. The total exposure to a single counterparty, aggregated across all of these systems, requires that their records have been resolved to one master identifier before the sum is taken. This is the cross-system problem that Â¶33 directly addresses and that concentration risk measurement (Â¶46aâb) depends on.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties"*; Principle 5 (Â¶46aâb) â *"aggregated credit exposure to a large corporate borrower"* and *"Counterparty credit risk exposures"* as critical risks.
- *Uniqueness* â Each distinct legal-person counterparty resolves to exactly one master record in the enterprise counterparty master; no active exposure record in any contributing system refers to a counterparty code that is not linked to that master | Count of counterparty codes in any source system that are either (a) absent from the counterparty master or (b) linked to more than one master record; count of exposure records orphaned from the master | Reviewed before every aggregation run; orphaned records excluded from concentration calculations and flagged in exceptions report; deduplication backlog tracked as a remediation metric
- *Consistency* â The industry classification and legal entity hierarchy attached to a counterparty in one system matches the values attached to the same counterparty master record in every other system | Count of counterparty master records where the industry code or legal entity structure assigned by one source system differs from that assigned by another | Discrepancies resolved at the master record level; downstream systems must consume the mastered attributes, not maintain their own

---

**XDQ-02 â Risk-to-Finance Reconciliation Completeness**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-09 (GL/System-of-Record Reconciliation Key), CDE-02 (Legal Entity Identifier), CDE-08 (Position/As-Of Date)
- **The problem this addresses:** Principle 3 requires that risk data be reconciled to accounting sources (Â¶36c). Principle 7 requires that reports be reconciled and validated (Â¶53a). These requirements are not met by monitoring any single CDE in isolation. A full risk-to-finance reconciliation requires that (a) every risk record has a valid GL reconciliation key (CDE-09), (b) the gross exposure amount on the risk record matches the GL balance within tolerance (CDE-03), (c) both are stated as of the same date (CDE-08), and (d) they are attributed to the same legal entity (CDE-02). The reconciliation gap â the population of exposures present in risk but absent from the GL, or present in the GL but absent from risk â is a cross-cutting metric that no individual CDE monitor can compute. This gap is the primary mechanism by which supervisors assess compliance with Principle 3 in practice.
- **Driven by:** Principle 3 (Â¶36c) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (Â¶53a) â *"defined requirements and processes to reconcile reports to risk data."*
- *Completeness* â The set of exposure records in the risk aggregation layer is complete relative to the GL: every GL balance that should generate a risk record does so, and no risk record is missing a GL counterpart | Count and value of GL balances with no matching risk record; count and value of risk records with no matching GL entry; expressed both as record counts and as monetary amounts by entity, risk type, and as-of date | Bi-directional gap reported at each reporting cycle; net and gross gaps tracked; monetary gap above materiality threshold (calibrated per Â¶56) prevents distribution of the affected risk report
- *Accuracy* â Where a risk record and its GL counterpart both exist, the amounts agree within defined tolerance | Sum of absolute differences between matched risk and GL amounts; count of matched pairs with differences exceeding the materiality threshold | Differences above threshold are individual reconciling items; aged items (unresolved beyond defined SLA) escalated through the channel defined per Â¶40; the aggregate reconciliation position is disclosed in the risk report where it is material
- *Timeliness* â The reconciliation is completed and the results are available before risk reports are distributed, for both normal and stress reporting cycles | Time between as-of date and completion of reconciliation sign-off, by risk type and entity; count of reports distributed before reconciliation is complete | Zero tolerance for distribution before reconciliation sign-off in normal cycles; defined emergency exception process for stress/crisis cycles with mandatory retrospective reconciliation

---

## 4. Out of Scope

The following regulation-mandated obligations cannot be addressed by a data catalog, a CDE register, or data quality monitoring rules. Stating this explicitly is not a limitation of the analysis â it is a prerequisite for a credible governance framework, because treating these as catalog problems would leave them unaddressed.

---

**Principle 8 â Comprehensiveness of Report Content**

Â¶57â60 require that risk management reports cover all material risk areas, include forward-looking stress test results, risk appetite context, and emerging concentration assessments, and are appropriately scoped for the size and complexity of the bank's operations.

A data catalog can ensure that the *data elements* required to build a comprehensive report exist, are governed, and are of sufficient quality. It cannot determine whether the *resulting report* covers the right risk areas, presents the right depth of analysis, or reaches the right conclusions. That is a risk management and board governance matter. The distinction is important: industry sector (CDE-07) is driven partly by Principle 8's requirement that credit risk reports include sector-level information. The CDE and its DQ requirements ensure the data exists. Whether the report that uses that data is genuinely comprehensive â forward-looking, appropriately scoped, correctly interpreted â is outside catalog scope and must be assessed through independent validation (Â¶29a) and board review (Â¶31, Â¶64â65).

---

**Principle 9 â Clarity and Usefulness of Reports**

Â¶61â69 require that reports are written clearly, balance quantitative data with qualitative interpretation, are tailored to the needs of the recipient, and are periodically confirmed as appropriate by recipients. Â¶67 â the requirement for an *"inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"* â is close to what a catalog's business glossary provides, and a catalog can support this. But the clarity of the narrative, the appropriateness of the quantitative-qualitative balance, and the periodic confirmation from board members that they find the reports useful are governance and communication obligations that no data governance tool addresses.

---

**Principle 10 â Frequency and Timeliness of Report Distribution**

Â¶70â71 require that the board and senior management set and periodically review frequency requirements for each report, that the bank routinely tests its ability to produce reports within those timeframes, and that in stress conditions critical reports are available within a very short period. CDE-08 (Position/As-Of Date) governs the temporal consistency of the *data* that flows into reports. CDE-10 (Source System/Lineage Flag) can identify bottlenecks in manual processing. But the *frequency setting* â which report is produced daily, weekly, or intraday, and whether that frequency is appropriate â is a board and senior management decision. The *routine testing* of report production under simulated stress is an operational resilience exercise. Neither is addressable through the catalog.

---

**Principle 11 â Distribution and Confidentiality of Reports**

Â¶72â74 require procedures for rapid collection, analysis, and timely dissemination to appropriate recipients while maintaining confidentiality. Access control, entitlements management, and distribution workflow are information security and report delivery infrastructure matters. A catalog can document which data assets are classified as confidential (supporting the policy established under Â¶27), but it cannot enforce the distribution procedures, validate that the right people received the right report, or manage the confidentiality of the report itself.

---

**Principle 1 â Governance Framework Establishment (the non-metadata obligations)**

Â¶27â31 require board and senior management ownership, independent validation of the entire risk data aggregation framework, business continuity integration, due diligence in acquisitions, and explicit board awareness of aggregation limitations. A data catalog supports these obligations by providing the metadata foundation, the data dictionary (Â¶37), the CDE register, and the data quality evidence. But the governance framework itself â board approval, resource allocation, independent validation function, change management process for acquisitions â must be established outside the catalog. The catalog is an instrument of that governance, not a substitute for it.

---

**Principle 3, Â¶38 â Human Judgement in Risk Aggregation**

Â¶38 acknowledges that where professional judgements are required, human intervention is appropriate, and that there should be an appropriate balance between automated and manual systems. This is a design principle for the risk aggregation process that a governance team and risk architects must apply. CDE-10 (Source System/Lineage Flag) ensures that manual interventions are *documented and visible*. It cannot determine whether the balance between automated and manual is appropriate for a given risk type â that requires expert judgement that is outside catalog capability.

---

**Principle 6, Â¶49(b) â Dashboard and Drill-Down Capability**

Â¶49(b) requires *"capabilities for data customisation to users' needs (eg dashboards, key takeaways, anomalies), to drill down as needed, and to produce quick summary reports."* The CDEs in this register â particularly the aggregation dimension elements (CDE-05, CDE-06, CDE-07) â ensure the data is available and correctly attributed so that a reporting or BI layer can provide these capabilities. But the dashboard design, the drill-down architecture, and the delivery mechanism are reporting infrastructure matters that are outside catalog scope.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | 2 (Â¶33), 4 (Â¶41â43), 5 (Â¶46aâb) | Uniqueness, Completeness, Validity, Consistency |
| CDE-02 | Legal Entity Identifier (Own Book) | 3 | 2 (Â¶33), 4 (Â¶41), 6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3 (Â¶36a), 4 (Â¶41), 5 (Â¶46), 7 (Â¶52â53) | Accuracy, Completeness, Timeliness, Validity |
| CDE-04 | Risk Type Classification | 3 | 4 (Â¶42), 7 (Â¶53b), 8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | 2 | 4 (title Â¶), 6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | 2 | 4 (title Â¶), 6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-07 | Industry / Sector Classification | 2 | 6 (Â¶50), 8 (Â¶57) | Completeness, Validity, Consistency |
| CDE-08 | Position / As-Of Date | 3 | 5 (Â¶44â46), 6 (Â¶50), 7 (Â¶53) | Completeness, Validity, Timeliness |
| CDE-09 | GL / System-of-Record Reconciliation Key | 3 | 3 (Â¶36câd), 7 (Â¶53a) | Completeness, Validity, Uniqueness, Accuracy |
| CDE-10 | Source System / Lineage Flag | 2 | 1 (Â¶30), 3 (Â¶36b, Â¶39) | Completeness, Validity, Accuracy |
| CDE-11 | Reporting Currency / FX Rate | 2 | 4 (Â¶41â43), 5 (Â¶45â46), 6 (Â¶48â49) | Completeness, Validity, Timeliness, Accuracy |

| XDQ | Name | CDEs Spanned | Principles | DQ Dimensions |
|---|---|---|---|---|
| XDQ-01 | Counterparty Deduplication and Single-View Resolution | CDE-01, CDE-03, CDE-05, CDE-07 | 2 (Â¶33), 5 (Â¶46aâb) | Uniqueness, Consistency |
| XDQ-02 | Risk-to-Finance Reconciliation Completeness | CDE-02, CDE-03, CDE-08, CDE-09 | 3 (Â¶36c), 7 (Â¶53a) | Completeness, Accuracy, Timeliness |