# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable aggregation under stress.** Banks must produce accurate, complete, and timely risk data not only in normal conditions but during crises — the failure point that motivated the regulation. ¶35: *"risk data aggregation capabilities should meet all Principles below simultaneously"*; ¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*

- **A single, governed data architecture.** Risk data must flow from integrated, documented infrastructure rather than fragmented or manual processes. ¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*

- **Accuracy evidenced through reconciliation.** Risk figures must be reconcilable to accounting and source systems; an unverified figure does not satisfy the standard. ¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."*

- **Completeness across the full group.** Aggregation must capture all material exposures — on- and off-balance-sheet — across every legal entity, business line, asset type, industry, and region. ¶41: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*

- **Monitored data quality with escalation.** Banks must not merely aim for quality; they must measure it, monitor it, and have action plans ready. ¶40: *"Supervisors expect banks to measure and monitor the accuracy of data and to develop appropriate escalation channels and action plans to be in place to rectify poor data quality."* ¶43 extends this mandate explicitly to completeness.

- **Board-level governance and documented limitations.** The board must approve the framework, understand its gaps, and receive reports that reflect those gaps honestly. ¶30: *"A bank's senior management should be fully aware of and understand the limitations that prevent full risk data aggregation."*

**Who it applies to**

Globally systemically important banks (G-SIBs) from 2016, and other systemically important banks from 2016 onwards as determined by national supervisors. The principles apply at the consolidated banking group level, including subsidiaries and legal entities within the group. The text consistently addresses "the banking group" (¶33, ¶41) rather than individual legal entities in isolation.

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Unique Identifier**

- **Definition:** A single, persistent, system-independent code that identifies one legal counterparty across all risk systems, booking systems, and the general ledger. It is the key by which all exposures to one borrower, issuer, or trading counterparty can be summed.
- **Why critical:** Without a consistent counterparty key, exposures held in different systems — loans in the credit system, derivatives in the trading system, bonds in the custody system — cannot be matched and summed. The aggregate credit exposure to a single counterparty, which ¶46(a) and ¶46(b) name as among the most time-critical aggregations, is simply incalculable. This is the primary joining key that makes aggregation possible at all.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3.** Without this element, the aggregate figure "total exposure to counterparty X" cannot be computed at all, because no mechanism exists to recognise that records in different systems refer to the same counterparty.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures"*
- **Search terms:** counterparty ID, counterparty code, client ID, legal entity identifier, LEI, obligor ID, entity ID, party identifier, customer number, counterparty reference
- **Data quality requirements:**
  - *uniqueness* — Each counterparty maps to exactly one identifier; no two distinct counterparties share a code | Count of duplicate identifier values across the counterparty master; count of counterparty names resolving to more than one active identifier | Zero duplicates; any non-zero result is a structural defect, not a tolerance matter, because a duplicate key causes miscounting of exposures | **(¶33)**
  - *completeness* — Every exposure record carries a populated counterparty identifier | Count of exposure records with a null, blank, or placeholder counterparty identifier | Zero; a null key means the exposure cannot be attributed and the aggregate is understated by an unknown amount | **(¶43)**
  - *validity* — Every counterparty identifier on an exposure record resolves to an active entry in the counterparty master | Count of exposure records whose counterparty identifier does not match any record in the authoritative counterparty master | Zero; an unresolvable key is equivalent to a null for aggregation purposes | **(¶40)**
  - *consistency* — The same counterparty identifier is used for the same legal counterparty across all source systems contributing to risk aggregation | Count of counterparties that appear under different identifiers in two or more source systems, detected via name-and-LEI matching | Zero cross-system mismatches for any counterparty appearing in more than one system; materiality does not apply here because identifier inconsistency causes structural miscounting rather than measurement error | **(¶33)**

---

**CDE-02 — Booking Legal Entity Identifier**

- **Definition:** A persistent code identifying the specific legal entity within the banking group in whose books a transaction or position is recorded. Distinct from the counterparty identifier: this describes the bank's own entity, not its client.
- **Why critical:** Group-level consolidation requires that every exposure be attributed to a booking entity so that subsidiary-level and group-level aggregates can both be produced — and so that intra-group exposures can be identified and eliminated on consolidation. Without this, the bank cannot demonstrate it has captured the full group (¶33, ¶41), and the booking-entity slice required by Principle 4 is unavailable.
- **Risk types:** Cross-cutting (all risk types, all entities)
- **Criticality: 3.** Without this element, the aggregate figure "group-consolidated exposure" cannot be computed at all, because there is no mechanism to identify which records belong to which legal entity, and intra-group double-counting cannot be eliminated.
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures"* (implied: across all entities in the group)
- **Search terms:** legal entity ID, entity code, booking entity, subsidiary code, organisational unit identifier, reporting entity, legal entity hierarchy, LEI (own entity), consolidated entity
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a populated booking legal entity identifier | Count of exposure records with a null or missing legal entity identifier | Zero; a record with no legal entity cannot be placed within the group hierarchy and is either double-counted or omitted from consolidation | **(¶43)**
  - *validity* — Every legal entity identifier on an exposure record corresponds to an active, in-scope entity in the group legal entity hierarchy | Count of exposure records whose legal entity identifier does not match any entry in the approved group entity register | Zero; an invalid entity code cannot be placed in the consolidation tree | **(¶40)**
  - *consistency* — The same legal entity code is used for the same entity across all risk systems contributing to consolidated reporting | Count of legal entities identified by different codes in two or more source systems | Zero; mismatched entity codes cause the same exposure to be counted in different nodes of the consolidation tree | **(¶33)**

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary amount representing the bank's exposure before the application of mitigants such as collateral, netting, or credit risk mitigation. Denominated in transaction currency; requires a companion currency code (see CDE-04) for multi-currency aggregation.
- **Why critical:** This is the primary quantity being aggregated. Every risk figure — limit utilisation, concentration measure, capital calculation input — is derived from or compared against this amount. If it is wrong, every downstream aggregate is wrong. ¶46(a) names the aggregated credit exposure to a large corporate borrower as a critical risk measure; ¶57 requires exposure information for all significant risk areas.
- **Risk types:** Credit, counterparty credit, market, concentration, cross-cutting
- **Criticality: 3.** Without this element, no exposure aggregate can be computed at all, because there is no quantity to sum. This is the amount being aggregated.
- **Driven by:** Principle 3 (¶36) — *"A bank should aggregate risk data in a way that is accurate and reliable"*; Principle 5 (¶46(a)) — *"The aggregated credit exposure to a large corporate borrower"*; Principle 7 (¶52) — *"Risk management reports should be accurate and precise"*
- **Search terms:** exposure amount, gross exposure, notional amount, outstanding balance, drawn amount, mark-to-market value, current exposure, replacement cost, position size, nominal value
- **Data quality requirements:**
  - *accuracy* — Exposure amounts agree with the authoritative booking or accounting system for the same position as of the same date | Difference between exposure amount in the risk system and the corresponding amount in the system of record, expressed as a percentage of total portfolio exposure | Threshold set by materiality consistent with ¶56: *"if omission or misstatement could influence the risk decisions of users, this may be considered material"* — materiality level to be defined and approved by senior management | **(¶36(c), ¶56)**
  - *completeness* — All in-scope positions carry a non-null, non-zero exposure amount unless the position genuinely has zero exposure | Count of in-scope exposure records with a null or zero exposure amount where a non-zero amount is expected based on position type | Zero unexplained nulls; zero-value exceptions to be reviewed and documented | **(¶43)**
  - *validity* — Exposure amounts fall within plausible ranges for their asset class and are free from obvious data-entry errors | Count of exposure records whose amount exceeds predefined outlier thresholds for that asset class, or is negative where the product type prohibits negative exposure | All flagged exceptions reviewed and resolved within the reporting cycle | **(¶40)**

---

**CDE-04 — Transaction Currency Code**

- **Definition:** The ISO 4217 three-character code identifying the currency in which an exposure is denominated. Required for conversion to a common reporting currency when aggregating across multi-currency portfolios.
- **Why critical:** Multi-currency aggregation — for example, total credit exposure to a counterparty across loans in USD, EUR, and GBP — requires each exposure to carry its currency so that a consistent converted amount can be computed. A missing or invalid currency code makes the converted aggregate unreliable. ¶4 of Principle 4 requires aggregation by business line, legal entity, asset type, industry, and region; all of these span currencies in an international bank.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 2.** The exposure amount exists, but currency aggregation across the portfolio produces an incorrect or incomparable figure. The figure is produced but cannot be trusted when currencies are mixed.
- **Driven by:** Principle 4 (header) — *"capture and aggregate all material risk data across the banking group"*; Principle 3 (¶36) — *"aggregate risk data in a way that is accurate and reliable"*
- **Search terms:** currency code, ISO currency, denomination currency, transaction currency, currency of exposure, CCY, FX currency, reporting currency
- **Data quality requirements:**
  - *validity* — Every exposure record carries a currency code that is a valid ISO 4217 code | Count of exposure records with a currency code not present in the current ISO 4217 reference list | Zero; an invalid code cannot be converted to reporting currency | **(¶40)**
  - *completeness* — Every exposure record carries a populated currency code | Count of exposure records with a null or blank currency code | Zero; a null currency makes the amount unplaceable in a multi-currency aggregate | **(¶43)**

---

**CDE-05 — Risk Type Classification**

- **Definition:** A structured code or label that classifies each exposure or position according to the type of risk it represents: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk, or other categories defined in the bank's risk taxonomy. Corresponds to the "dictionary of concepts" required by ¶37.
- **Why critical:** Risk management reports must cover all significant risk areas (¶57). Aggregation by risk type is the primary partition: capital calculations, limit frameworks, and regulatory reports each apply to one risk type. If the classification is missing or inconsistent, exposures are misrouted into the wrong aggregate or omitted entirely. ¶37 explicitly requires this dictionary to exist and be applied consistently.
- **Risk types:** Cross-cutting (this element partitions all risk types)
- **Criticality: 2.** Aggregates by risk type are produced but are mis-populated: credit risk totals include items that should be in market risk, or operational risk exposures are omitted. The figure exists but cannot be trusted for any risk-specific calculation.
- **Driven by:** Principle 3 (¶37) — *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"*; Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas"*
- **Search terms:** risk type, risk category, risk class, risk classification, risk taxonomy, product type (where it drives risk classification), Basel risk type, risk flag
- **Data quality requirements:**
  - *validity* — Every exposure record carries a risk type code drawn from the approved risk taxonomy | Count of exposure records with a risk type code not present in the approved taxonomy reference list | Zero; an off-taxonomy code cannot be routed to the correct aggregate | **(¶40, ¶37)**
  - *completeness* — Every exposure record carries a populated risk type classification | Count of exposure records with a null or blank risk type code | Zero; an unclassified exposure is excluded from all risk-type aggregates and the totals are understated | **(¶43)**
  - *consistency* — The same product or instrument is classified to the same risk type across all source systems | Count of instruments that carry different risk type codes in two or more source systems for the same position date | Zero; inconsistent classification causes the same exposure to be counted in multiple or no risk-type aggregates | **(¶33, ¶37)**

---

**CDE-06 — Business Line**

- **Definition:** A structured code that assigns each exposure or position to a defined business line within the bank (e.g., retail banking, corporate banking, investment banking, trading). The granularity and naming must be consistent with the bank's approved business line hierarchy.
- **Why critical:** Principle 4 explicitly requires data to be available by business line; ¶50 gives a worked example of aggregating credit exposures across all business lines. Without a populated, consistent business line code, the bank cannot produce the business-line slice of any risk aggregate and cannot identify concentrations within a business line.
- **Risk types:** Cross-cutting (all risk types require business line disaggregation per Principle 4)
- **Criticality: 2.** The overall portfolio aggregate exists, but the business line slice of the aggregate is unavailable or unreliable. Senior management cannot see which business line drives a concentration.
- **Driven by:** Principle 4 (header) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures … across all business lines and geographic areas"*
- **Search terms:** business line, line of business, LOB, division, segment, business unit, reporting segment, business area, front office unit
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a populated business line code | Count of exposure records with a null or blank business line code | Zero; a null business line means the exposure cannot appear in any business-line-sliced aggregate | **(¶43)**
  - *validity* — Every business line code corresponds to an entry in the approved business line hierarchy | Count of exposure records with a business line code not present in the approved hierarchy | Zero; an invalid code cannot be placed in the hierarchy and the exposure falls out of business-line aggregates | **(¶40)**
  - *consistency* — The same business line code is applied to the same transaction across all systems that report it | Count of transactions where the business line code differs between the risk system and the finance or booking system | Zero; inconsistent codes cause the same exposure to be double-counted or omitted in business-line aggregates | **(¶33)**

---

**CDE-07 — Geography / Country of Risk**

- **Definition:** A structured code — ideally ISO 3166 country code or an internally approved geography hierarchy — that records the country or region to which the risk of an exposure is attributed. This is the country of risk, not necessarily the country of domicile of the counterparty or the booking location.
- **Why critical:** ¶50 names country credit exposure aggregated as of a specified date as a canonical example of the adaptability requirement. ¶46(c) requires trading concentrations by region. Without a consistent country of risk code, the bank cannot respond to supervisory stress scenarios (e.g., "what is our exposure to Country X?") or identify geographic concentrations.
- **Risk types:** Credit, market, concentration, cross-cutting
- **Criticality: 2.** A geographic aggregate is produced but mis-populated or incomplete. Concentrations in a stressed country may be understated because some exposures carry a different geography or none at all.
- **Driven by:** Principle 4 (header) — *"Data should be available by … region"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 8 (¶57) — *"country … for credit risk"*
- **Search terms:** country of risk, country code, geographic region, booking country, risk country, ISO country, jurisdiction, geographic flag, region code, country of issuer
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a populated geography or country of risk code | Count of exposure records with a null or blank country of risk code | Zero; a null means the exposure is excluded from every geographic aggregate, understating country concentrations | **(¶43)**
  - *validity* — Every country of risk code corresponds to an entry in the approved geographic reference list (e.g., ISO 3166) | Count of exposure records with an unrecognised country code | Zero; an unrecognised code cannot be mapped to a region and the exposure disappears from geographic aggregates | **(¶40)**

---

**CDE-08 — Industry / Sector Classification**

- **Definition:** A structured code classifying the counterparty or issuer by industry or economic sector, using a recognised taxonomy (e.g., GICS, NACE, SIC, or an internally approved equivalent). Applied at the counterparty level and inherited by all exposures to that counterparty.
- **Why critical:** ¶50 names industry credit exposures across all business lines and geographic areas as the second canonical example of the adaptability requirement. ¶57 names industry sector as a required component of credit risk reporting. Sector concentration analysis — a core supervisory concern — is impossible without this field. A bank that cannot aggregate credit exposure by industry sector cannot comply with Principle 6's adaptability test or Principle 8's comprehensiveness test.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Sector-sliced aggregates are produced but distorted: counterparties with missing or incorrect sector codes fall out of sector totals, understating concentrations in sectors under stress.
- **Driven by:** Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*
- **Search terms:** industry code, sector code, GICS sector, NACE code, SIC code, industry classification, counterparty sector, economic sector, industry group
- **Data quality requirements:**
  - *completeness* — Every counterparty record carries a populated industry or sector code; by inheritance, every exposure record is traceable to a sector | Count of counterparty records with a null or blank sector code; and count of exposure records linked to a counterparty with no sector code | Zero at the counterparty level; a counterparty without a sector causes all its exposures to be omitted from sector aggregates | **(¶43)**
  - *validity* — Every sector code corresponds to an entry in the approved sector taxonomy | Count of counterparty records with a sector code not present in the approved taxonomy | Zero; an unrecognised code cannot be mapped to a sector aggregate | **(¶40)**

---

**CDE-09 — Position / As-Of Date**

- **Definition:** The calendar date as of which an exposure, position, or balance is measured and reported. It is the temporal key that defines which snapshot of the portfolio a given record belongs to. Every aggregate is stated "as of" this date.
- **Why critical:** ¶50 gives the example of aggregating country and industry credit exposures "as of a specified date" — the as-of date is what makes the phrase meaningful. Without it, records from different days are mixed into the same aggregate, producing a figure that is neither accurate nor interpretable. Under stress, ¶46 requires rapid aggregation; without a reliable position date, there is no way to confirm that the rapid aggregate reflects the current position rather than yesterday's.
- **Risk types:** Cross-cutting (all risk types and all aggregations)
- **Criticality: 3.** Without this element, the aggregate figure for any risk measure cannot be stated as of any particular date; records from different days are combined and the figure is temporally undefined, which is equivalent to being invalid for any risk management or reporting purpose.
- **Driven by:** Principle 5 (¶44) — *"produce aggregate risk information on a timely basis to meet all risk management reporting requirements"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (¶52) — *"Risk management reports should be accurate and precise"*
- **Search terms:** position date, as-of date, value date, report date, snapshot date, trade date, settlement date, business date, effective date
- **Data quality requirements:**
  - *completeness* — Every exposure or position record carries a populated as-of date | Count of records with a null or blank position date | Zero; a record without a date cannot be assigned to a reporting period | **(¶43)**
  - *validity* — Every as-of date is a valid calendar date not in the future and consistent with the reporting period | Count of records with a position date that is not a valid calendar date, or that falls outside the expected reporting window | Zero; an invalid date makes the record unusable in any time-bounded aggregate | **(¶40)**
  - *timeliness* — Risk data for each position date is available in the risk aggregation environment within the timeframe required for the relevant risk type | Elapsed time between the close of business on the position date and the availability of complete, reconciled risk data for that date in the aggregation layer | Threshold set by risk type: market and trading data per ¶46(c) on a same-day or intraday basis; credit data per ¶46(a) within the frequency defined by senior management; liquidity data per ¶46(d) intraday or same-day in stress | **(¶44–47)**

---

**CDE-10 — General Ledger / System-of-Record Reference**

- **Definition:** The identifier that links a risk data record to its corresponding entry in the general ledger or in the authoritative booking system from which it originated. This is the reconciliation key that makes it possible to trace a risk record back to its accounting equivalent.
- **Why critical:** ¶36(c) states that risk data must be reconciled with the bank's sources, including accounting data. Without this key, the reconciliation required by ¶36(c) and ¶53(a) cannot be performed at all. An unreconciled risk figure is not a compliant risk figure, regardless of how it was computed; ¶56 establishes that accuracy requirements are analogous to accounting materiality, and that requires a mechanism to compare risk data against accounting data. This is the element that makes the evidence of accuracy possible.
- **Risk types:** Cross-cutting (applies to all risk types that have an accounting counterpart, which is the majority)
- **Criticality: 3.** Without this element, the reconciliation required by ¶36(c) cannot be performed at all, because there is no key by which a risk record can be matched to the system of record. An unverifiable figure is not a compliant figure under ¶36(c).
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** GL reference, general ledger ID, trade ID, deal ID, position ID, booking reference, system of record key, source transaction ID, accounting reference, deal reference number
- **Data quality requirements:**
  - *completeness* — Every risk record that has an accounting counterpart carries a populated GL or system-of-record reference | Count of risk records expected to have an accounting counterpart but carrying a null or blank GL reference | Zero; a null GL reference makes reconciliation impossible for that record | **(¶43, ¶36(c))**
  - *validity* — Every GL reference on a risk record resolves to an active entry in the general ledger or the nominated system of record | Count of risk records whose GL reference does not match any entry in the general ledger for the same position date | Zero; an unresolvable reference is equivalent to no reference for reconciliation purposes | **(¶40, ¶36(c))**
  - *consistency* — The exposure amount on the risk record agrees with the corresponding amount in the general ledger or system of record within the materiality threshold | Aggregate and record-level difference between risk exposure amounts and the matched GL amounts, as a proportion of total portfolio exposure | Threshold set by materiality per ¶56: *"if omission or misstatement could influence the risk decisions of users, this may be considered material"* — threshold to be defined by senior management and Finance, not by the catalog team | **(¶36(c), ¶56)**

---

**CDE-11 — Source System Identifier and Processing Method Flag**

- **Definition:** Two related attributes recorded together: (a) the identifier of the source system from which the risk record originated (e.g., the loans system, the derivatives platform, the treasury system); and (b) a flag indicating whether the record arrived via an automated feed or via a manual or end-user-computing (EUC) process.
- **Why critical:** ¶36(b) requires effective controls over manual and EUC-sourced data, and ¶39 requires documentation of all risk data aggregation processes, including manual workarounds. Without the source system identifier, data lineage cannot be established and it is impossible to know which system is authoritative for any given record (¶36(d) requires striving toward a single authoritative source per risk type). Without the manual/EUC flag, the controls prescribed by ¶36(b) cannot be applied selectively, and the documentation required by ¶39 cannot be maintained. The catalog's lineage capability is anchored to this element.
- **Risk types:** Cross-cutting (applies to all risk types; it is a provenance attribute, not a risk attribute)
- **Criticality: 2.** Aggregates are produced, but it is impossible to distinguish records whose accuracy is evidenced by automated controls from records that passed through manual processes with weaker controls. ¶36(b) and ¶39 require this distinction to be made and documented; without this element, that obligation cannot be discharged and the quality of any figure that relies on manual input cannot be assessed or escalated.
- **Driven by:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications … it should have effective mitigants in place … consistently applied across the bank's processes"*; Principle 3 (¶36(d)) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (¶39) — *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual"*
- **Search terms:** source system, source system name, system of origin, data source, feed name, originating system, manual flag, EUC flag, spreadsheet flag, manual override indicator, processing method, data entry method, automation flag
- **Data quality requirements:**
  - *completeness* — Every risk record carries a populated source system identifier and a populated processing method flag | Count of risk records with a null or blank source system identifier; count of risk records with a null or unrecognised processing method flag | Zero; a null source system identifier makes lineage impossible to establish; a null EUC flag means manual records cannot be identified and subjected to appropriate controls | **(¶43, ¶39)**
  - *validity* — Every source system identifier corresponds to an entry in the approved data source register maintained in the catalog | Count of risk records with a source system identifier not present in the approved data source register | Zero; an unrecognised source system identifier means the record's lineage is unknown and its controls cannot be verified | **(¶40, ¶36(d))**
  - *accuracy* — The proportion of risk records arriving via manual or EUC processes is monitored against agreed thresholds, and exceptions are escalated | Count and percentage of risk records carrying a manual or EUC processing flag, broken down by risk type and source system; trend over time | Threshold set by senior management based on the bank's stated direction of travel toward automation per ¶39: *"proposed actions to reduce the impact"* of manual workarounds — not zero by regulatory requirement, but movement toward automation must be evidenced | **(¶39, ¶36(b))**

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Risk-to-Finance Reconciliation**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-10 (GL / System-of-Record Reference), CDE-09 (Position / As-Of Date), CDE-02 (Booking Legal Entity Identifier)
- **Rule intent:** The aggregate of all exposure amounts in the risk aggregation layer, grouped by legal entity and position date, must be reconcilable to the corresponding balances in the general ledger. This is not the same as record-level matching (which CDE-10 addresses): it is the portfolio-level proof that no records have been added, dropped, or duplicated in the journey from source systems through risk aggregation to reporting. Neither CDE-03 nor CDE-10 alone can detect population-level omissions; only a cross-system count and sum reconciliation can do this.
- **Measurement:** For each legal entity and each position date: (a) count of records in the risk aggregation layer vs. count of records in the source system; (b) total exposure amount in the risk aggregation layer vs. total of corresponding amounts in the general ledger. Both differences are expressed as amounts and as percentages of the total.
- **Threshold:** Set by materiality consistent with ¶56. The threshold is not zero — legitimate timing differences and netting adjustments will always produce some difference — but any difference exceeding the materiality level defined by senior management and Finance must be investigated, explained, and escalated before the risk report is issued. Unexplained differences above materiality cause the report to fail the accuracy requirement.
- **Paragraph citations:** ¶36(c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; ¶53(a) — *"Defined requirements and processes to reconcile reports to risk data"*; ¶56 — *"Supervisors expect banks to consider accuracy requirements analogous to accounting materiality"*

---

**XDQ-02 — Cross-System Counterparty Identity Resolution**

- **CDEs spanned:** CDE-01 (Counterparty Unique Identifier), CDE-05 (Risk Type Classification), CDE-06 (Business Line), CDE-08 (Industry / Sector Classification)
- **Rule intent:** The same legal counterparty must be represented by the same identifier across all source systems that contribute to risk aggregation — loans, derivatives, bonds, repo, guarantees. This cannot be checked by monitoring CDE-01 in any single system; it requires a cross-system match. Where the same counterparty carries different internal codes in different systems, all codes must be linked to a single golden record in the counterparty master before aggregation. The failure mode this addresses — fragmented counterparty identity — is the single most common cause of understated large-exposure concentrations.
- **Measurement:** For each source system contributing to risk aggregation: count of counterparties in that system that cannot be matched by name, LEI, or other identifying attribute to the counterparty master; count of counterparties in the counterparty master that are matched to more than one internal code across contributing systems.
- **Threshold:** Zero unresolved cross-system counterparty mismatches for any counterparty whose total exposure across all systems exceeds the bank's defined materiality threshold for large exposures. The zero threshold is justified because even a single unmatched record for a large counterparty causes the aggregate exposure to be understated by that record's full amount, which is a structural failure rather than a measurement tolerance.
- **Paragraph citations:** ¶33 — *"use of single identifiers and/or unified naming conventions for data including … counterparties"*; ¶43 — *"Supervisors expect banks to produce aggregated risk data that is complete … with any exceptions identified and explained"*; ¶46(a) and (b) — naming large corporate and counterparty credit exposures as time-critical aggregations

---

**XDQ-03 — Data Timeliness by Risk Type**

- **CDEs spanned:** CDE-09 (Position / As-Of Date), CDE-03 (Gross Exposure Amount), CDE-01 (Counterparty Unique Identifier), CDE-11 (Source System Identifier and Processing Method Flag)
- **Rule intent:** ¶45 and ¶46 establish that different risk types require data at materially different speeds, with the fastest requirements applying to trading, counterparty credit, and liquidity data. This requirement cannot be expressed as a property of any single CDE; it applies to the pipeline as a whole — from position date on the source system to availability of complete, reconciled data in the risk aggregation layer. Monitoring individual elements for their own timeliness misses the aggregate pipeline latency, which is what ¶44 and ¶47 address.
- **Measurement:** For each risk type and each source system: elapsed time in hours between the close of business on the position date and the point at which complete data for that risk type and date is confirmed available and reconciled in the risk aggregation layer. Measured daily in normal conditions and at each intraday cycle in stress.
- **Threshold:** Differentiated by risk type per ¶46: (a) trading and market risk data — same-day or intraday availability as required by ¶46(c) and ¶71; (b) counterparty credit exposure — same-day in stress per ¶46(b) and ¶71; (c) liquidity indicators — intraday in stress per ¶46(d); (d) credit risk for retail/corporate — within the frequency cycle set by senior management per ¶47. Thresholds are not set by the catalog team; they are set by senior management and validated by supervisors per ¶47. The catalog monitors against those thresholds and flags breaches.
- **Paragraph citations:** ¶44 — *"produce aggregate risk information on a timely basis to meet all risk management reporting requirements"*; ¶45 — *"different types of data will be required at different speeds"*; ¶46 — listing critical risk types with specific timing expectations; ¶47 — supervisory review of frequency requirements

---

## 4. Out of Scope

The following matters are explicitly or practically beyond what a data catalog and CDE register can deliver. Where a principle also drives a CDE above, the split is explained.

---

**Principle 1 — Governance (¶27–31): Board and senior management accountability**

The governance obligations in Principle 1 — board approval of the risk data framework, deployment of adequate resources, awareness of limitations, strategic IT planning — are organisational and accountability requirements. A data catalog can document that a framework exists, record data ownership assignments, and surface known data limitations (e.g., systems excluded from aggregation, manual process flags). It cannot constitute the framework itself, cannot enforce board approval, and cannot substitute for the human governance structures ¶27–31 require. What is needed instead: a formal governance charter, documented board resolutions, a data stewardship programme with named owners recorded in or alongside the catalog, and an independent validation function.

¶30's instruction that senior management *"identify data critical to risk data aggregation"* is the basis for the CDE register in Section 2 above. That identification task is within scope; the governance accountability around it is not.

---

**Principle 2 — Data Architecture (¶32–35): IT infrastructure and business continuity**

¶33 drives CDE-01 (counterparty identifier) and CDE-02 (legal entity identifier) and is the principal justification for unified naming conventions cataloged as metadata. To that extent, Principle 2 is partially within scope.

What the catalog cannot deliver: the physical data architecture, integrated IT infrastructure, business continuity plans and business impact analyses (¶32), data lifecycle controls (¶34), and the actual technical integration of source systems. A catalog can describe the architecture and document lineage; it cannot build or test it. What is needed instead: enterprise data architecture design, IT project delivery, and BCP/DR testing programmes.

---

**Principle 6 — Adaptability (¶48–51): On-demand aggregation capability**

¶50 drives CDE-07 (geography) and CDE-08 (industry sector) as aggregation dimensions that must be available for ad hoc queries. To that extent, Principle 6 is partially within scope.

What the catalog cannot deliver: the technical capability to execute arbitrary ad hoc aggregations quickly during stress. Cataloging the dimensions ensures the data elements exist and are governed; it does not ensure that the underlying risk systems can slice and dice them in near-real time. What is needed instead: risk aggregation technology (e.g., in-memory databases, pre-computed cubes, flexible reporting engines) and stress-testing infrastructure.

---

**Principle 7 — Report Accuracy (¶52–56): Validation rules inventory and exception reporting**

¶53(b) requires an inventory of validation rules applied to quantitative information. A data catalog can hold this inventory and link validation rules to CDEs — and the DQ requirements in Section 2 are a direct input to that inventory. In that sense, Principle 7 is partially within scope.

What the catalog cannot deliver: the actual execution of reconciliation processes (¶53(a)), the real-time identification and reporting of data errors via exceptions reports (¶53(c)), or the setting of accuracy and precision requirements by senior management (¶55). A catalog documents what the rules are and tracks their results; it does not run them or escalate them autonomously. What is needed instead: operational data quality tooling, reconciliation workflows, and an escalation and issue-management process owned by risk and finance.

---

**Principle 8 — Comprehensiveness (¶57–60): Report content and forward-looking information**

¶57 names industry sector as a required report dimension, which drives CDE-08. ¶58 requires reports to identify emerging risk concentrations and provide forward-looking forecasts and stress tests. To that extent, Principle 8 is partially within scope (as a driver of aggregation dimensions).

What the catalog cannot deliver: the substantive content of risk reports, the scope decisions about which risk areas to cover, the depth and analytical quality of coverage, the provision of forward-looking scenarios and stress test results (¶60), or the assurance that reports contain risk-related measures such as regulatory and economic capital (¶59). These are risk management, modelling, and report authoring obligations. What is needed instead: a comprehensive risk reporting framework, stress testing programmes, capital calculation engines, and board-approved report templates.

---

**Principle 9 — Clarity and Usefulness (¶61–69): Report design and recipient feedback**

¶67 requires a bank to develop an inventory and classification of risk data items. A CDE register held in a data catalog is a direct implementation of this requirement — and is within scope.

Everything else in Principle 9 is beyond catalog scope: the balance of qualitative versus quantitative information in reports (¶62), differentiated reporting by recipient level (¶63), the board's role in determining its own requirements and alerting management when reports fail (¶64–65), senior management's reporting requirements (¶66), and the periodic confirmation with recipients that information remains relevant and appropriate (¶69). These are report design, communication, and board governance matters. What is needed instead: a formal report review and approval process, periodic recipient surveys, and governance minutes evidencing board engagement with report quality.

---

**Principle 10 — Frequency (¶70–71): Report production scheduling**

The frequency at which reports are produced — and the testing of the bank's ability to produce them within established timeframes under stress (¶70) — is an operational scheduling and infrastructure matter. A data catalog can record what the agreed frequency requirements are, as metadata against each report. It can also support timeliness monitoring at the data pipeline level (XDQ-03 addresses this). What it cannot do is schedule report production, test production under stress conditions, or enforce frequency requirements. What is needed instead: report scheduling infrastructure, operational runbooks, and regular fire-drill tests of stress reporting capability (¶70: *"A bank should routinely test its ability to produce accurate reports within established timeframes, particularly in stress/crisis situations"*).

---

**Principle 11 — Distribution (¶72–74): Report dissemination and confidentiality**

Distribution workflows, access controls on reports, confidentiality classifications, and the confirmation that relevant recipients receive timely reports (¶73) are all reporting infrastructure and access governance matters. A catalog can document the intended recipients of a report and its confidentiality classification as metadata, but it cannot manage the actual distribution, enforce access rights on report delivery channels, or periodically confirm receipt. What is needed instead: a report distribution platform with access controls, distribution lists maintained by report owners, and a periodic confirmation process owned by risk reporting governance.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Unique Identifier | 3 | 2 (¶33), 4 (¶41) | Uniqueness, Completeness, Validity, Consistency |
| CDE-02 | Booking Legal Entity Identifier | 3 | 2 (¶33), 4 (¶41) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3 (¶36), 5 (¶46), 7 (¶52) | Accuracy, Completeness, Validity |
| CDE-04 | Transaction Currency Code | 2 | 3 (¶36), 4 (header) | Validity, Completeness |
| CDE-05 | Risk Type Classification | 2 | 3 (¶37), 8 (¶57) | Validity, Completeness, Consistency |
| CDE-06 | Business Line | 2 | 4 (header), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-07 | Geography / Country of Risk | 2 | 4 (header), 6 (¶50), 8 (¶57) | Completeness, Validity |
| CDE-08 | Industry / Sector Classification | 2 | 6 (¶50), 8 (¶57) | Completeness, Validity |
| CDE-09 | Position / As-Of Date | 3 | 5 (¶44), 6 (¶50), 7 (¶52) | Completeness, Validity, Timeliness |
| CDE-10 | GL / System-of-Record Reference | 3 | 3 (¶36(c)), 7 (¶53(a)) | Completeness, Validity, Consistency |
| CDE-11 | Source System ID and Processing Method Flag | 2 | 3 (¶36(b), ¶36(d), ¶39) | Completeness, Validity, Accuracy |
| XDQ-01 | Risk-to-Finance Reconciliation | — | 3 (¶36(c)), 7 (¶53(a), ¶56) | Accuracy, Consistency |
| XDQ-02 | Cross-System Counterparty Identity Resolution | — | 2 (¶33), 4 (¶43), 5 (¶46) | Uniqueness, Completeness |
| XDQ-03 | Data Timeliness by Risk Type | — | 5 (¶44–47) | Timeliness |