# BCBS 239 â Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a board-level obligation.** The regulation requires that boards and senior management can obtain accurate, complete and timely aggregated risk data â not merely that data exists somewhere in the organisation. The governing obligation sits at the top: the board approves the framework and must understand its limitations (Â¶28, Â¶31 â *"A bank's board is responsible for determining its own risk reporting requirements and should be aware of limitations that prevent full risk data aggregation"*).

- **Data architecture as a prerequisite, not an afterthought.** A bank must design and maintain integrated data taxonomies, single identifiers, and unified naming conventions across the group â metadata and architecture are explicitly required, not implied (Â¶33 â *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions"*).

- **Accuracy through reconciliation and controlled automation.** Risk data must be reconcilable to source systems including accounting records, and automation must minimise manual error. A single authoritative source per risk type is the target state (Â¶36(c),(d) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; *"A bank should strive towards a single authoritative source for risk data per each type of risk"*).

- **Completeness across every material dimension.** Aggregation must cover all material exposures â including off-balance-sheet â and be sliceable by business line, legal entity, asset type, industry, region and other groupings material to the risk in question (Â¶41 â *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 4 header â *"Data should be available by business line, legal entity, asset type, industry, region"*).

- **Timeliness calibrated to risk volatility, including intraday under stress.** The regulation explicitly names liquidity, counterparty credit and trading exposures as risks that may need to be produced intraday during a crisis. Systems must be built to that standard in normal times (Â¶45 â *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks"*).

- **Documentation, provenance, and governance of manual processes.** All aggregation processes â automated and manual â must be documented. End-user computing (spreadsheets, desktop databases) requires specific mitigants and must be identified in the data lineage (Â¶36(b) â *"it should have effective mitigants in place (eg end-user computing policies and procedures)"*; Â¶39 â *"Documentation should include an explanation of the appropriateness of any manual workarounds, a description of their criticality to the accuracy of risk data aggregation"*).

**Who it applies to**

Principles 1â11 apply to **Global Systemically Important Banks (G-SIBs)** directly and as a supervisory expectation baseline. National supervisors may extend equivalent requirements to **Domestic Systemically Important Banks (D-SIBs)** and other significant institutions. The unit of compliance is the **banking group**: subsidiaries, off-balance-sheet vehicles and material entities within the consolidated perimeter are all in scope. The regulation does not exempt any legal entity, business line or geography within the group.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Identifier**

- **Definition:** A unique, persistent, group-wide identifier assigned to each legal-entity counterparty (borrower, derivative counterparty, guarantor, issuer) that resolves to the same record regardless of which booking system, product line or geography originated the exposure.
- **Why critical:** Without a single resolved counterparty key, exposures cannot be summed across systems to produce a group-level counterparty exposure. Every concentration calculation, large-exposure report, and counterparty credit risk aggregate depends on this join. Its failure does not degrade an aggregate â it makes the aggregate undefined.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3** â Aggregation is *impossible* without it. Duplicate or unmatched counterparty keys mean the summed exposure figure contains unknown double-counts or omissions; the figure is invalidated, not merely degraded.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 5 (Â¶46(a),(b)) â critical risks include aggregated credit exposure to large corporate borrowers and counterparty credit risk exposures.
- **Search terms:** counterparty ID, client ID, obligor ID, legal entity identifier, LEI, party ID, customer master, counterparty master, global party identifier
- **Data quality requirements:**
  - *Uniqueness* â Each counterparty is represented by exactly one active identifier in the group-level master; no two active records resolve to the same real-world entity | Count of duplicate or conflicting active counterparty records in the master reference table | Target: zero duplicates; any positive count is a blocking issue
  - *Completeness* â Every exposure record carries a populated counterparty identifier | Count and percentage of exposure records with null or missing counterparty ID | Target: 0% null; any gap means unknown exposure is excluded from aggregates
  - *Validity* â Every counterparty identifier on an exposure record resolves to an active record in the authoritative counterparty master | Count of exposure records referencing a counterparty ID not present in the master | Target: 0% unmatched
  - *Consistency* â The same counterparty carries the same identifier across all source systems contributing to risk aggregation | Count of cross-system identifier mismatches for the same legal entity (identified by LEI or equivalent) | Target: 0% mismatch

---

**CDE-02 â Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier of the bank's own legal entity in which a transaction is booked â the booking entity within the consolidated group. Distinct from the counterparty identifier; this represents the bank's own side of the transaction.
- **Why critical:** Group consolidation requires summing exposures across subsidiaries and then eliminating intra-group items. Without a reliable booking-entity identifier, the aggregation engine cannot determine which entity owns a given exposure, making consolidated group-level and entity-level reporting simultaneously impossible.
- **Risk types:** Cross-cutting (all risk types, all regulatory reporting)
- **Criticality: 3** â Without a resolved booking-entity key, the group aggregation cannot be constructed at all; intra-group eliminations cannot be performed; subsidiary-level reports are ambiguous. The aggregate is invalidated.
- **Driven by:** Principle 2 (Â¶33) â *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (Â¶41) â completeness across the banking group including off-balance-sheet; Principle 8 (Â¶57) â reports must cover all significant risk areas across the organisation.
- **Search terms:** legal entity ID, booking entity, entity code, subsidiary code, branch code, organisational unit, LE code, group entity hierarchy, consolidation entity
- **Data quality requirements:**
  - *Validity* â Every risk record carries a booking-entity identifier that maps to an active node in the group legal entity hierarchy | Count of risk records with a booking-entity code not present in the legal entity hierarchy | Target: 0%
  - *Completeness* â No risk record is missing a booking-entity identifier | Count and percentage of risk records with null booking-entity field | Target: 0%
  - *Consistency* â The booking-entity identifier on a risk record matches the entity assigned to the same transaction in the general ledger | Count of risk-to-GL record pairs where booking entity differs | Target: 0%; discrepancies require documented exception

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary value of the bank's credit or market exposure to a counterparty or position, denominated in the transaction currency, before the application of netting, collateral, or credit risk mitigation. This is the base monetary quantity from which all risk aggregation is built.
- **Why critical:** Every risk aggregate â counterparty exposure, large-exposure limit, portfolio concentration â is ultimately an arithmetic function of exposure amounts. An absent or mismeasured exposure amount does not degrade an aggregate; it silently distorts it. Reconciliation to accounting data (Â¶36(c)) is only possible if this amount matches the corresponding balance-sheet or off-balance-sheet notional in the general ledger.
- **Risk types:** Credit, counterparty credit, concentration, market
- **Criticality: 3** â The monetary amount is the thing being aggregated. Its failure does not reduce resolution; it produces a wrong number. No compensating CDE can substitute for it.
- **Driven by:** Principle 3 (Â¶36(a),(c)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 4 (Â¶41) â capture of all material risk exposures including off-balance sheet.
- **Search terms:** exposure amount, outstanding balance, notional amount, drawn amount, current exposure, mark-to-market value, replacement cost, gross receivable, carrying amount
- **Data quality requirements:**
  - *Accuracy* â Exposure amounts on risk records agree with the corresponding figures in the authoritative accounting or position system within defined materiality tolerances | Sum of absolute differences between risk-system exposure amounts and GL/position-system amounts by booking entity and position date | Threshold: materiality tolerance defined by senior management per Â¶55â56; any breach requires documented exception
  - *Completeness* â No exposure record carries a null or zero exposure amount without documented justification | Count and percentage of exposure records with null exposure amount | Target: 0%
  - *Validity* â Exposure amounts fall within plausible ranges for the instrument type and currency; negative values exist only where short positions are permitted | Count of exposure records with exposure amounts outside defined instrument-type bounds | Any outlier requires review before inclusion in aggregate

---

**CDE-04 â Risk Type Classification**

- **Definition:** The taxonomy code that assigns each exposure or position to a defined risk category â credit risk, market risk, liquidity risk, operational risk, counterparty credit risk â as used in the bank's internal risk framework and regulatory capital calculations.
- **Why critical:** Risk aggregation is organised by risk type. An exposure mis-classified between, say, counterparty credit risk and credit risk will appear in the wrong aggregate and be omitted from the correct one. Reports by risk type (Â¶57) are impossible to produce accurately if this classification is absent or unreliable. It also drives which capital and limit calculations apply.
- **Risk types:** Cross-cutting
- **Criticality: 3** â Mis-classification routes an exposure to the wrong aggregate and removes it from the correct one. Both the receiving aggregate and the originating aggregate are wrong simultaneously. The failure invalidates, not degrades.
- **Driven by:** Principle 7 (Â¶52â53) â reports must be accurate and precise; Principle 8 (Â¶57) â *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 4 (Principle header) â aggregation by risk type is a required dimension.
- **Search terms:** risk type, risk category, risk class, risk taxonomy, risk classification code, product risk type, Basel risk class
- **Data quality requirements:**
  - *Validity* â Every exposure record carries a risk type code drawn from the bank's approved risk taxonomy controlled vocabulary | Count of exposure records with risk type values not present in the approved taxonomy reference list | Target: 0%
  - *Completeness* â No exposure record is missing a risk type classification | Count and percentage of exposure records with null risk type | Target: 0%
  - *Consistency* â The risk type assigned in the risk system matches the risk type used to determine regulatory capital treatment for the same instrument | Count of instruments where risk-system classification and capital-calculation classification differ | Target: 0%; any difference requires documented business justification

---

**CDE-05 â Business Line**

- **Definition:** The code or identifier that assigns each exposure or position to an internal business unit or line of business (e.g., Corporate Banking, Investment Banking, Retail, Treasury, Private Banking) as defined in the bank's organisational taxonomy.
- **Why critical:** Principle 4 explicitly requires that risk data be available by business line. Without a reliable business line code, the aggregation cannot be sliced to produce business-line risk reports; concentration by business line cannot be computed; and stress scenarios that apply to specific business activities cannot be scoped. It is a required reporting dimension, not merely descriptive.
- **Risk types:** Cross-cutting
- **Criticality: 2** â A required reporting slice is absent or degraded. The group aggregate can still be computed, but business-line sub-aggregates are incomplete or unproduceable. Applying the rubric: the failure degrades rather than invalidates the top-level figure.
- **Driven by:** Principle 4 (principle header) â *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries, as well as industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*.
- **Search terms:** business line, line of business, business unit, division code, segment code, desk code, business segment, product line
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a business line code | Count and percentage of exposure records with null business line | Target: <1% with documented exceptions; 0% for material exposures
  - *Validity* â Business line codes reference the current approved organisational hierarchy | Count of records carrying a business line code no longer active in the hierarchy | Target: 0%; retired codes must be remapped on decommission

---

**CDE-06 â Geography / Country of Risk**

- **Definition:** The country code that represents the economic risk location of an exposure â typically the country of the counterparty's domicile or the location of collateral, as determined by the bank's country risk policy. Distinct from booking location.
- **Why critical:** Principle 4 requires aggregation by region; Principle 6 (Â¶50) specifically names country credit exposure as an example of data that must be producible on demand as of a specified date. Concentration by country is a core supervisory concern, particularly for sovereign and cross-border credit risk.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 2** â Geographic sub-aggregates are required slices. Without this element, country concentration reports are unproduceable and ad hoc supervisory requests (Â¶50) cannot be fulfilled, but the group-level total exposure figure is still valid. Degradation, not invalidation.
- **Driven by:** Principle 4 (principle header) â data available by region; Principle 6 (Â¶50) â *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*.
- **Search terms:** country of risk, country code, risk country, domicile country, counterparty country, obligor country, ISO country code, geographic region
- **Data quality requirements:**
  - *Completeness* â Every material exposure record carries a country-of-risk code | Count and percentage of material exposure records with null country code | Target: 0% for sovereign and large corporate; <1% overall with documented exceptions
  - *Validity* â Country codes conform to ISO 3166-1 alpha-2 or the bank's approved equivalent controlled list | Count of records with country codes outside the approved reference list | Target: 0%
  - *Consistency* â Country-of-risk assignment follows the bank's documented country risk policy; assignments are consistent for the same counterparty across business lines | Count of counterparties assigned different country-of-risk codes across systems for the same legal entity | Target: 0%; each mismatch requires review

---

**CDE-07 â Industry / Sector Classification**

- **Definition:** The code that classifies the counterparty's primary economic activity according to a standard or internal sector taxonomy (e.g., NACE, GICS, SIC, or internal equivalents) used for credit concentration and portfolio analysis.
- **Why critical:** Principle 4 requires aggregation by industry. Principle 8 (Â¶57) explicitly names *"single name, country and industry sector for credit risk"* as required report components. Sector concentration is one of the primary dimensions on which emerging risk is identified and reported to boards. Without it, concentration-by-sector aggregates cannot be produced.
- **Risk types:** Credit, concentration
- **Criticality: 2** â Industry sector sub-aggregates are a required reporting dimension. Their absence degrades concentration reports but does not invalidate the total exposure figure. The rubric places this at 2.
- **Driven by:** Principle 4 (principle header) â data available by industry; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*; Principle 6 (Â¶50) â industry credit exposures on demand across all business lines.
- **Search terms:** industry code, sector code, NACE code, GICS sector, SIC code, counterparty industry, borrower sector, industry classification
- **Data quality requirements:**
  - *Completeness* â Every corporate/institutional counterparty record carries an industry sector code | Count and percentage of corporate counterparty records with null sector code | Target: 0% for credit-risk-bearing counterparties
  - *Validity* â Sector codes are drawn from the bank's approved sector taxonomy reference list | Count of records with sector codes outside the approved list | Target: 0%
  - *Timeliness* â Sector classification is updated when a counterparty's primary business activity changes materially | Count of counterparty records whose sector code has not been reviewed within a defined review cycle (e.g., annual) | Target: 0% overdue

---

**CDE-08 â Position / As-Of Date**

- **Definition:** The calendar date as of which an exposure amount or position is stated â the snapshot date that defines what the record represents. Not the trade date, settlement date, or report-run date; specifically the economic reference date of the position.
- **Why critical:** Every risk aggregate is a function of both what is being measured and *when* it is measured. Mixing position records with different as-of dates into a single aggregate produces a figure that is neither accurate nor meaningful. Timeliness compliance (Principle 5) cannot be demonstrated unless this date is explicit and consistent. Reconciliation to accounting data requires matching on the same date. Without it, no aggregate can be stamped with a reliable reference point.
- **Risk types:** Cross-cutting
- **Criticality: 3** â An aggregate that mixes positions from different dates is not an aggregate of the risk as of any date. The figure is invalidated: it cannot be verified, reconciled, or used as the basis for a risk decision. The rubric's highest level applies.
- **Driven by:** Principle 3 (Â¶36(c)) â reconciliation to accounting data requires a shared reference date; Principle 5 (principle header and Â¶44â46) â *"generate aggregate and up-to-date risk data in a timely manner"*; Principle 6 (Â¶50) â on-demand aggregation must be producible *"as of a specified date"*.
- **Search terms:** position date, as-of date, reference date, valuation date, snapshot date, reporting date, effective date
- **Data quality requirements:**
  - *Completeness* â Every exposure and position record carries a populated as-of date | Count and percentage of records with null as-of date | Target: 0%
  - *Validity* â As-of dates fall within plausible business-day ranges; no future dates except in explicitly forward-looking datasets; no dates predating the instrument inception | Count of records with as-of dates outside valid range | Target: 0%
  - *Timeliness* â For critical risks (Â¶46), position records with the current business-day as-of date are available within the frequency window set by senior management | Time elapsed between position close and availability of aggregated data for critical risk categories | Threshold: defined per risk type per the bank's frequency standard; breach requires escalation per Â¶40

---

**CDE-09 â GL / Source System Reconciliation Key**

- **Definition:** The identifier â typically a trade reference, account number, or transaction ID â that links a risk data record to its corresponding record in the general ledger or the system-of-record from which it was sourced. This is the join key used to evidence that risk data and accounting data represent the same underlying transaction.
- **Why critical:** Â¶36(c) directly requires reconciliation between risk data and accounting data. Without a reliable reconciliation key, that reconciliation cannot be performed systematically: the bank cannot demonstrate that risk figures and financial figures are consistent, which is one of the foundational accuracy controls. A supervisor examining compliance with Principle 3 will look first for evidence that this reconciliation is operational â and its operation depends entirely on this key existing and matching.
- **Risk types:** Cross-cutting
- **Criticality: 3** â Without this key, the reconciliation mandated by Â¶36(c) cannot be performed. The accuracy of risk figures relative to accounting records is *undemonstrable*, not merely partially degraded. The figure may be correct, but correctness cannot be evidenced. For a regulation that treats accuracy controls as analogous to accounting controls (Â¶36(a)), undemonstrability is equivalent to failure.
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*.
- **Search terms:** trade ID, deal reference, account number, transaction reference, position ID, GL account key, source transaction identifier, booking reference, system of record ID
- **Data quality requirements:**
  - *Completeness* â Every risk data record carries a populated reconciliation key linking it to its GL or system-of-record counterpart | Count and percentage of risk records with null reconciliation key | Target: 0% for on-balance-sheet items; documented exceptions only for off-balance-sheet where no GL entry exists
  - *Validity* â Every reconciliation key on a risk record resolves to an active record in the corresponding GL or source system | Count of risk records whose reconciliation key does not match any record in the designated source system | Target: 0%; unmatched keys must be investigated before period-end
  - *Uniqueness* â Each GL transaction is represented at most once in the risk data store for a given position date (no double-counting) | Count of duplicate reconciliation key / position date combinations in the risk dataset | Target: 0%

---

**CDE-10 â Source System / Lineage Flag**

- **Definition:** The identifier of the system that originated the risk data record, combined with a flag indicating whether the record was produced through an automated feed or through manual intervention (including end-user computing tools such as spreadsheets or desktop databases).
- **Why critical:** Â¶36(b) requires specific mitigants for manual and EUC processes; Â¶39 requires that all aggregation processes â automated and manual â be documented, with explanations of manual workarounds and their criticality. Without this element, it is impossible to identify which records in an aggregate came through controlled automated pipelines and which entered through uncontrolled manual routes. Senior management cannot understand the limitations of aggregation (Â¶30) without it. Independent validation (Â¶29(a)) cannot assess coverage without it.
- **Risk types:** Cross-cutting (governance and accuracy)
- **Criticality: 2** â Its absence does not invalidate a specific risk figure, but it prevents the bank from demonstrating the reliability of *any* figure and from fulfilling the explicit documentation obligations of Â¶36(b) and Â¶39. Aggregates are still produced; their provenance is unauditable. This is a degradation of the governance framework rather than a figure-level invalidation â rubric level 2.
- **Driven by:** Principle 2 (Â¶33) â *"information on the characteristics of the data (metadata)"*; Principle 3 (Â¶36(b)) â *"effective mitigants in place (eg end-user computing policies and procedures)"*; Principle 3 (Â¶39) â *"document and explain all of their risk data aggregation processes whether automated or manual"*.
- **Search terms:** source system, feed name, data source, originating system, EUC flag, manual override flag, input method, data lineage, pipeline name, batch job name
- **Data quality requirements:**
  - *Completeness* â Every risk data record carries a populated source system identifier | Count and percentage of risk records with null source system field | Target: 0%
  - *Validity* â Source system identifiers reference the bank's approved system inventory; any unrecognised system code triggers an investigation | Count of records with source system codes not present in the approved system inventory | Target: 0%
  - *Completeness (EUC flag)* â Every record sourced from a manual process or EUC tool is flagged as such | Count of records from known EUC sources (identified by source system code) that do not carry the manual/EUC flag | Target: 0%; undetected EUC input represents a control failure

---

**CDE-11 â Facility / Limit Amount**

- **Definition:** The approved credit limit or trading limit associated with a counterparty, facility, or position â the authorised maximum exposure against which the current exposure is measured.
- **Why critical:** Principle 8 (Â¶58) explicitly requires risk reports to provide information *"in the context of limits and risk appetite/tolerance."* A limit amount is not merely descriptive: utilisation (exposure divided by limit) is the primary indicator of limit breach and emerging concentration. Without it, the report cannot fulfil its statutory content requirement. It also enables the monitoring of emerging trends (Â¶58) that is a board-level reporting obligation.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 2** â The risk figure (exposure) can be computed without the limit. However, the regulatory reporting requirement to contextualise exposure against limits (Â¶58) cannot be fulfilled, and limit-breach detection fails. The aggregate is produceable but the required contextualisation is absent â rubric level 2.
- **Driven by:** Principle 8 (Â¶58) â *"provide information in the context of limits and risk appetite/tolerance and propose recommendations for action where appropriate"*; Principle 5 (Â¶46(c)) â *"Trading exposures, positions, operating limits, and market concentrations"* are named as critical risk data items requiring timely availability.
- **Search terms:** credit limit, facility limit, approved limit, trading limit, counterparty limit, position limit, exposure limit, risk appetite limit, obligor limit
- **Data quality requirements:**
  - *Accuracy* â Limit amounts reflect board- or senior-management-approved values; changes to limits are reflected promptly and with audit trail | Time elapsed between a limit change approval and its update in the risk data store; count of limit records that differ from the approved limit register | Threshold: same-day update for material limit changes
  - *Completeness* â Every exposure record for a counterparty or facility with an approved limit carries the corresponding limit amount | Count and percentage of exposure records for limited facilities where limit amount is null | Target: 0%
  - *Timeliness* â Limit data is available alongside exposure data for the same position date | Count of position-date snapshots where exposure data is available but corresponding limit data is absent | Target: 0%

---

**CDE-12 â Currency Code**

- **Definition:** The ISO 4217 currency code of the transaction or exposure, required to convert all exposures to a common reporting currency (typically the group's functional currency) for aggregation.
- **Why critical:** Risk aggregation across instruments denominated in different currencies requires a currency code plus an exchange rate to produce a common-currency total. Without it, monetary aggregation across the group is impossible â an exposure in JPY cannot be added to one in USD unless the currency of each is known. This is a joining key for the currency conversion step; its absence makes the exposure amount uninterpretable in any cross-currency aggregate.
- **Risk types:** Credit, market, liquidity, cross-cutting
- **Criticality: 2** â For single-currency portfolios or reports, the aggregate is still produceable. For any group-wide or multi-currency aggregate, a missing currency code means the exposure cannot be converted and must either be excluded or assumed â both degrade the aggregate. Rubric level 2: the aggregate degrades rather than becomes impossible in all cases, but for a global banking group the practical effect is severe.
- **Driven by:** Principle 4 (Â¶41â43) â completeness across the banking group implicitly requires currency normalisation for any monetary aggregate; Principle 3 (Â¶36(c)) â reconciliation to accounting data requires currency-matched comparison.
- **Search terms:** currency code, transaction currency, deal currency, ISO currency, CCY, base currency, denomination
- **Data quality requirements:**
  - *Completeness* â Every monetary exposure record carries a currency code | Count and percentage of records with null currency code | Target: 0%
  - *Validity* â Currency codes conform to ISO 4217 or the bank's approved equivalents | Count of records with currency codes outside the approved reference list | Target: 0%
  - *Consistency* â The currency code on a risk record matches the currency code on the corresponding GL record for the same transaction | Count of risk-to-GL pairs where currency code differs | Target: 0%; any mismatch requires investigation before the figure enters an aggregate

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Group-Wide Counterparty Deduplication and Resolution**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-05 (Business Line), CDE-06 (Geography / Country of Risk), CDE-07 (Industry / Sector Classification)
- **What this is:** The requirement that a single real-world counterparty appears as one and only one record in the group-level counterparty master, regardless of how many source systems, booking entities, or business lines hold a relationship with that counterparty. This cannot be expressed as a rule on any single CDE: CDE-01 can be unique within one system while the same counterparty exists under a different identifier in a second system. Resolution requires cross-system matching, entity disambiguation, and master data management â none of which is a property of a single field.
- **Why it is cross-cutting:** The failure mode here is not a null field or an invalid code. It is that two correctly-formed, non-null identifiers in two systems refer to the same legal entity without the systems knowing it. The exposure amounts (CDE-03) for both identifiers are individually accurate; the risk classification (CDE-04) on each may be correct; but the group aggregate double-counts the counterparty, and the large-exposure report is wrong. No single-CDE monitor detects this. It requires a cross-system entity resolution process.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties"*; Principle 3 (Â¶36(d)) â single authoritative source per risk type; Principle 5 (Â¶46(a),(b)) â accurate counterparty credit exposure aggregation is named as a critical risk.
- **Dimension:** Uniqueness (cross-system)
- **Rule intent:** Each real-world legal entity counterparty maps to exactly one active identifier in the group counterparty master; no two active master records represent the same legal entity.
- **Measurement:** Count of counterparty master record pairs that share an LEI, registered name, or other external identifier and are not already linked as the same entity; count of group-level counterparty exposure aggregates that change materially when a deduplication reconciliation is run against the prior period.
- **Suggested threshold:** Zero unresolved duplicate pairs in the counterparty master; any newly detected pair must be resolved within a defined remediation window before the next reporting cycle.

---

**XDQ-02 â Risk-to-Finance Reconciliation Completeness**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-08 (Position / As-Of Date), CDE-09 (GL / Source System Reconciliation Key), CDE-10 (Source System / Lineage Flag), CDE-12 (Currency Code)
- **What this is:** The end-to-end reconciliation between the total exposure amounts that appear in risk aggregates and the balances or notionals recorded in the general ledger or financial accounting system, performed as of the same position date, in the same currency, using the reconciliation key to match individual records. This is a process requirement, not a field-level check. It cannot be satisfied by monitoring any single CDE because it requires the combination of: a matching key (CDE-09), a common date (CDE-08), a monetary amount to compare (CDE-03), a currency for normalisation (CDE-12), and source-system identification to scope the reconciliation (CDE-10).
- **Why it is cross-cutting:** Â¶36(c) mandates that risk data be reconciled to accounting sources. A CDE monitor on CDE-03 can confirm that no exposure amount is null; it cannot confirm that the sum of all exposure amounts agrees with the GL balance for the same portfolio. A CDE monitor on CDE-09 can confirm that every record has a reconciliation key; it cannot confirm that the key actually resolves to a matching GL record with the same amount. The reconciliation is only performed â and its output is only meaningful â when all five CDEs are present, populated, and consistent simultaneously.
- **Driven by:** Principle 3 (Â¶36(a),(c)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*.
- **Dimension:** Accuracy (cross-system)
- **Rule intent:** The sum of gross exposure amounts in the risk system for a given portfolio, legal entity, and position date agrees with the corresponding balance in the general ledger within a defined materiality tolerance; all differences are identified, explained, and either resolved or accepted with documented justification.
- **Measurement:** Absolute and percentage difference between risk-system aggregate exposure and GL balance by legal entity, risk type, and position date; count of unreconciled items (present in risk system but absent in GL, or vice versa) remaining open beyond the defined resolution window; count of position dates for which no reconciliation run was completed.
- **Suggested threshold:** Materiality tolerance defined by senior management per Â¶55â56; 100% of position dates must have a completed reconciliation; zero unreconciled items older than the defined resolution window.

---

## 4. Out of Scope

The following principles impose obligations that no combination of CDE definitions, data quality rules, and catalog metadata can satisfy. Stating this plainly is necessary: a data catalog is an information asset management tool. It governs *what data exists, what it means, how it was produced, and whether it meets quality standards*. It does not govern *what reports are produced, how they are structured, how frequently they are distributed, who receives them, or whether the board finds them useful*.

---

**Principle 1 (Â¶27â31) â Governance framework and board oversight**

*Partially addressed; partially out of scope.*

The data catalog supports Principle 1 insofar as it provides the documented data dictionary (Â¶37), CDE register, and quality monitoring that senior management needs to understand and report data limitations (Â¶30). Assigning data ownership in the catalog (Â¶34) directly supports the roles-and-responsibilities requirement.

What the catalog cannot deliver: the board's approval of the framework (Â¶28), the independent validation program (Â¶29(a)), the due diligence on acquisitions (Â¶29(b)), or the strategic IT planning process (Â¶30). These require governance structures, validation staff, and board-level decision processes. A catalog entry noting "independent validation: not yet conducted" documents the gap; it does not close it.

---

**Principle 7 (Â¶52â56) â Report accuracy: reconciliation and validation processes**

*Partially addressed; partially out of scope.*

CDE-09 (reconciliation key) and XDQ-02 (risk-to-finance reconciliation) directly support the accuracy requirements of Principle 7. Maintaining the inventory of validation rules (Â¶53(b)) is a natural catalog artifact.

What the catalog cannot deliver: the execution of reconciliation runs, the operation of edit and reasonableness checks, the production of exceptions reports (Â¶53(c)), or the establishment of accuracy standards by senior management (Â¶55). The catalog documents what the rules are and whether the data meets them in the abstract; it does not run the reconciliation process or escalate the results through management reporting channels.

---

**Principle 8 (Â¶57â60) â Comprehensiveness of risk report content**

*Partially addressed; partially out of scope.*

Principle 8 explicitly names industry sector (Â¶57) as a required report dimension, which is why CDE-07 is included in this register. Similarly, limits and risk appetite context (Â¶58) drive CDE-11. In those respects, Principle 8 generates CDEs.

What the catalog cannot deliver: ensuring that *reports themselves* cover all significant risk areas, that capital adequacy information is included (Â¶59), that forward-looking stress-test results appear (Â¶60), or that the board and senior management receive reports with the right balance of qualitative and quantitative content. These are report content and design obligations. No CDE register or DQ monitor can determine whether a report is comprehensive â only a human reader reviewing the report against a defined content standard can do that.

---

**Principle 9 (Â¶61â69) â Clarity and usefulness of risk reports**

*Entirely out of scope.*

Principle 9 concerns whether risk reports are clear, well-balanced, tailored to recipients, and contribute to sound decision-making. Â¶67 â *"A bank should develop an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"* â is the closest the principle comes to catalog-relevant content, and that obligation is addressed by the CDE register and data dictionary themselves.

Everything else in Principle 9 â the balance of qualitative versus quantitative content (Â¶62), the differing needs of the board versus risk committees (Â¶63), the board's obligation to challenge management when reports do not meet requirements (Â¶65), the periodic confirmation that recipients find reports relevant (Â¶69) â concerns report design, communication, and board governance. These are not data quality problems. A catalog cannot make a report clear, and a DQ score cannot confirm that the board found a report useful.

---

**Principle 10 (Â¶70â71) â Frequency of report production and distribution**

*Entirely out of scope.*

Principle 10 requires the board and senior management to set frequency requirements for each report, test the bank's ability to produce reports within those timeframes, and increase frequency during stress. CDE-08 (as-of date) and CDE-10 (source system) can provide evidence of data latency, and the timeliness DQ dimension on CDE-08 can flag that critical risk data is not available within the required window.

However: setting frequency requirements (Â¶70), conducting periodic tests of stress-scenario report production capability (Â¶70), and ensuring intraday report production for critical positions (Â¶71) are operational and governance activities. A catalog can surface how stale the data is; it cannot set production schedules, run tests, or guarantee that systems will perform under stress conditions.

---

**Principle 11 (Â¶72â74) â Distribution and confidentiality**

*Entirely out of scope.*

Principle 11 concerns the procedures for distributing reports to appropriate recipients, balancing timely dissemination against confidentiality obligations, and periodically confirming that relevant recipients receive reports (Â¶73). These are access management, information security, and distribution-workflow obligations. A data catalog supports data access governance and can document sensitivity classifications (relevant to Â¶27's reference to data confidentiality policy), but it does not control report distribution systems, enforce recipient lists, or confirm that a specific person received a specific report on a specific date.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | P2 (Â¶33), P5 (Â¶46) | Uniqueness, Completeness, Validity, Consistency |
| CDE-02 | Legal Entity Identifier (Booking Entity) | 3 | P2 (Â¶33), P4 (Â¶41), P8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | P3 (Â¶36(a),(c)), P4 (Â¶41) | Accuracy, Completeness, Validity |
| CDE-04 | Risk Type Classification | 3 | P7 (Â¶52â53), P8 (Â¶57), P4 header | Validity, Completeness, Consistency |
| CDE-05 | Business Line | 2 | P4 header, P6 (Â¶50) | Completeness, Validity |
| CDE-06 | Geography / Country of Risk | 2 | P4 header, P6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-07 | Industry / Sector Classification | 2 | P4 header, P8 (Â¶57), P6 (Â¶50) | Completeness, Validity, Timeliness |
| CDE-08 | Position / As-Of Date | 3 | P3 (Â¶36(c)), P5 header (Â¶44â46), P6 (Â¶50) | Completeness, Validity, Timeliness |
| CDE-09 | GL / Source System Reconciliation Key | 3 | P3 (Â¶36(c)), P7 (Â¶53(a)) | Completeness, Validity, Uniqueness |
| CDE-10 | Source System / Lineage Flag | 2 | P2 (Â¶33), P3 (Â¶36(b), Â¶39) | Completeness, Validity |
| CDE-11 | Facility / Limit Amount | 2 | P8 (Â¶58), P5 (Â¶46(c)) | Accuracy, Completeness, Timeliness |
| CDE-12 | Currency Code | 2 | P4 (Â¶41â43), P3 (Â¶36(c)) | Completeness, Validity, Consistency |

**Cross-cutting requirements**

| ID | Description | CDEs Spanned | Dimension |
|---|---|---|---|
| XDQ-01 | Group-wide counterparty deduplication and resolution | CDE-01, CDE-03, CDE-05, CDE-06, CDE-07 | Uniqueness (cross-system) |
| XDQ-02 | Risk-to-finance reconciliation completeness | CDE-03, CDE-08, CDE-09, CDE-10, CDE-12 | Accuracy (cross-system) |