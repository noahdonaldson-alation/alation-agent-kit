# BCBS 239 â Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a precondition for sound governance.** Boards and senior management must be able to aggregate risk data across the entire banking group â by business line, legal entity, geography, and counterparty â in normal times *and* under stress. Without reliable underlying data, risk reports cannot be trusted and governance fails at the source. (Â¶35: *"risk management reports reflect the risks in a reliable way (ie meeting data aggregation expectations is necessary to meet reporting expectations)"*)

- **A single, authoritative, documented data architecture.** Banks must establish integrated data taxonomies, single identifiers, and unified naming conventions across the group, and must document every aggregation process â automated or manual. (Â¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions"*; Â¶39: *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*)

- **Completeness across all material exposures, including off-balance-sheet.** Risk data must cover all material exposures regardless of booking location, including items not on the balance sheet, and must be sliceable by business line, legal entity, asset type, industry, and region. (Â¶41: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*)

- **Accuracy evidenced by reconciliation, not asserted.** Risk data must be reconciled back to accounting sources. Controls around risk data must be as robust as those around accounting data. Manual processes and end-user computing must be documented and mitigated. (Â¶36(a): *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Â¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*)

- **Timeliness calibrated to risk type, with accelerated delivery in stress.** Systems must be capable of producing aggregated risk data rapidly during crisis for credit, market, liquidity, and counterparty credit risk. Intraday production may be required. (Â¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks"*)

- **A data dictionary as a formal precondition.** Before any aggregation can be valid, concepts must be defined consistently across the organisation. This is explicitly called a precondition, not a best practice. (Â¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"*)

**Who it applies to**

BCBS 239 applies to **Global Systemically Important Banks (G-SIBs)** from the date of initial publication, with national supervisors extending it to **Domestic Systemically Important Banks (D-SIBs)** on their own timelines. The obligations fall on the **banking group as a whole** â subsidiaries, branches, and off-balance-sheet vehicles are not exempt by virtue of being separately incorporated. Principles 1â11 are addressed directly to bank boards, senior management, risk functions, and IT functions.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Identifier**

- **Definition:** The unique, group-wide identifier that resolves a single legal counterparty â borrower, trading counterparty, or guarantor â across all source systems, booking entities, and risk types. It is the key that makes multi-system aggregation of exposure to one name possible.
- **Why critical:** Without a single resolved identifier, the bank cannot aggregate total credit or counterparty credit risk exposure to one name. Two systems holding the same counterparty under different local codes will produce double-counted or siloed figures. The regulation's explicit requirement for single identifiers is precisely because this failure mode is common.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3** â Without this element, the aggregate figure *total group exposure to counterparty X* cannot be computed at all, because records across systems cannot be joined to the same legal name; matching would be absent or random.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 5 (Â¶46(a),(b)) â aggregated credit and counterparty credit exposure named as critical risks
- **Search terms:** counterparty ID, obligor ID, entity ID, customer ID, GFCID, LEI, counterparty master, golden source counterparty
- **Data quality requirements:**
  - *Uniqueness* â Each distinct legal counterparty is represented by exactly one active identifier in the authoritative master; duplicate active records for the same legal entity are prohibited | Count of counterparty identifiers matched to more than one active master record; count of exposure records carrying an identifier not present in the master | Target: 0 duplicates; 0 unresolved identifiers on risk-reported positions
  - *Completeness* â Every exposure record carries a populated, non-null counterparty identifier | Count of exposure records where the counterparty identifier field is null or blank | Target: 0 null counterparty identifiers on in-scope positions
  - *Consistency* â The counterparty identifier on a risk record resolves to the same legal entity in all systems that hold the same position (risk system, collateral system, general ledger) | Count of positions where the counterparty identifier differs between the risk system and the general ledger for the same transaction | Target: 0 mismatches on reconciled positions

---

**CDE-02 â Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier of the bank's own legal entity in which a risk position is booked. This is distinct from the counterparty: it represents *the bank's own* subsidiary, branch, or holding company that holds the exposure. Required for group consolidation and for subsidiary-level reporting.
- **Why critical:** Group-wide risk aggregation requires summing across the bank's own legal entities. If a booking entity code is wrong, missing, or inconsistent, exposures are attributed to the wrong subsidiary, consolidation is incorrect, and intragroup eliminations cannot be performed.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3** â Without this element, the aggregate figure *group-consolidated exposure by legal entity* cannot be computed at all, because positions cannot be attributed to the correct node in the group structure; consolidation either double-counts or misses entities entirely.
- **Driven by:** Principle 2 (Â¶33) â *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (Â¶41) â *"include all material risk exposures"* across the banking group; Principle 4 (header) â *"Data should be available by business line, legal entity"*
- **Search terms:** legal entity code, booking entity, entity ID, legal entity identifier, group entity, subsidiary code, branch code, LEI (own entity)
- **Data quality requirements:**
  - *Validity* â Every booking entity code on a risk record must match an entry in the authorised group legal entity hierarchy | Count of risk records carrying a booking entity code absent from the current group legal entity register | Target: 0 invalid codes on in-scope positions
  - *Completeness* â No risk record is missing a booking entity code | Count of risk records where booking entity is null or blank | Target: 0 nulls
  - *Consistency* â The booking entity on a risk record matches the booking entity on the corresponding general ledger entry for the same transaction | Count of transactions where booking entity differs between risk and general ledger | Target: 0 mismatches on reconciled transactions

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary amount representing the bank's gross risk exposure for a position before the application of netting, collateral, guarantees, or other credit risk mitigants. Expressed in transaction currency, with a separate base-currency equivalent. This is the primary input to all exposure aggregation.
- **Why critical:** This is the quantity being aggregated. Every summed risk figure â total credit exposure, large-exposure limit utilisation, sector concentration â is an arithmetic function of this amount. If it is wrong, every downstream aggregate is wrong.
- **Risk types:** Credit, counterparty credit, concentration, market (notional for derivatives)
- **Criticality: 3** â Without this element, the aggregate figure *total group credit exposure* cannot be computed at all, because there is no amount to sum; or if the amount is systematically misstated, every aggregate figure built from it is arithmetically incorrect.
- **Driven by:** Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (Â¶41) â *"include all material risk exposures, including those that are off-balance sheet"*; Principle 5 (Â¶46(a)) â *"aggregated credit exposure to a large corporate borrower"* cited as a critical risk
- **Search terms:** exposure amount, outstanding balance, drawn amount, notional amount, gross exposure, EAD (exposure at default), current exposure, mark-to-market exposure
- **Data quality requirements:**
  - *Accuracy* â The gross exposure amount on a risk record agrees to the outstanding balance on the authoritative system of record (loan system, trading system, or general ledger) within defined materiality tolerance | Sum of absolute differences between risk-system exposure amount and system-of-record balance, by asset class | Target: aggregate variance below accounting materiality threshold; zero unexplained individual variances above a defined unit threshold
  - *Completeness* â No in-scope position has a null or zero gross exposure amount where a non-zero balance is known to exist | Count of positions flagged as active in the system of record where the risk record carries a null or zero exposure amount | Target: 0
  - *Timeliness* â The exposure amount reflects the position as of the stated position date, not a prior business day | Maximum age of source data feeding the exposure amount relative to the position date | Target: within the service level agreed per risk type (e.g., T+0 for trading book, T+1 for banking book)

---

**CDE-04 â Risk Type Classification**

- **Definition:** The categorical label that assigns an exposure or position to a defined risk type â at minimum: credit risk, market risk, liquidity risk, operational risk, and counterparty credit risk. May include sub-classifications (e.g., single-name credit, settlement risk). This is the primary taxonomy by which risk figures are partitioned in reports.
- **Why critical:** Risk reports are organised by risk type. If an exposure is misclassified â for example, a derivative counterparty credit risk exposure recorded as a plain credit risk â it will appear in the wrong report section, limits of the wrong type will be applied, and capital calculations will draw from the wrong pool of data.
- **Risk types:** Cross-cutting
- **Criticality: 2** â The aggregate exposure figure can be computed, but the slice *total credit risk exposure* versus *total counterparty credit risk exposure* is wrong, making those reported figures unreliable and limit comparisons invalid.
- **Driven by:** Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"* (reconciliation presupposes consistent classification); Principle 8 (Â¶57) â *"exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 4 (header) â *"permit identifying and reporting risk exposures, concentrations and emerging risks"*
- **Search terms:** risk type, risk category, risk class, asset class, risk bucket, risk taxonomy code
- **Data quality requirements:**
  - *Validity* â Every risk record carries a risk type code drawn from the authorised enterprise risk taxonomy | Count of risk records with a risk type code absent from the approved taxonomy | Target: 0 invalid codes
  - *Completeness* â No in-scope risk record is missing a risk type classification | Count of risk records with null risk type | Target: 0
  - *Consistency* â The risk type classification is applied using the same definition across all source systems feeding the consolidated risk data store | Count of positions where the risk type code differs between source system and consolidated risk store for the same position identifier | Target: 0 mismatches

---

**CDE-05 â Business Line**

- **Definition:** The internal organisational dimension â such as retail banking, corporate banking, trading, or private banking â to which a position is attributed for management reporting and risk aggregation. Must align with the bank's internal management structure and be consistent across systems.
- **Why critical:** Principle 4 explicitly requires risk data to be available by business line. Risk concentrations, limit breaches, and capital allocation are all assessed at the business line level. An exposure attributed to the wrong business line will distort business-line P&L, risk appetite tracking, and concentration reports for both lines involved.
- **Risk types:** Cross-cutting
- **Criticality: 2** â The total group exposure figure is unaffected, but the slice *exposure by business line* is wrong, making business-line risk reports unreliable and rendering business-line limit monitoring invalid.
- **Driven by:** Principle 4 (header) â *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures â¦ across all business lines and geographic areas"*
- **Search terms:** business line, business unit, division, segment, product line, desk, front office unit, cost centre (where used as business line proxy)
- **Data quality requirements:**
  - *Validity* â Every risk record carries a business line code present in the authorised management hierarchy | Count of risk records with an unrecognised business line code | Target: 0
  - *Completeness* â No in-scope risk record is missing a business line attribution | Count of risk records with null business line | Target: 0
  - *Consistency* â Business line attribution for the same position is identical across risk, finance, and management information systems | Count of positions where business line differs between risk and finance systems | Target: 0 mismatches on reconciled positions

---

**CDE-06 â Geography / Country of Risk**

- **Definition:** The country or geographic region to which an exposure is attributed for risk purposes â typically the country of the counterparty's domicile or the country of the underlying risk (for sovereign, transfer, and country credit risk). Distinct from the booking location.
- **Why critical:** Principle 4 requires risk data to be available by region. Country credit exposure aggregation is singled out by name in Â¶50 as a canonical example of an on-demand aggregation requirement. Cross-border concentration risk and sovereign risk monitoring are impossible without a consistent country-of-risk attribution.
- **Risk types:** Credit, concentration, counterparty credit
- **Criticality: 2** â The total exposure figure is unaffected, but the slice *country credit exposure* is wrong or impossible to produce, directly failing the Â¶50 example and making concentration monitoring by geography unreliable.
- **Driven by:** Principle 4 (header) â *"Data should be available by â¦ region"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries â¦ across all business lines and geographic areas"*
- **Search terms:** country of risk, country code, geography, jurisdiction, domicile country, risk country, ISO country code, transfer risk country
- **Data quality requirements:**
  - *Validity* â Every country-of-risk code is drawn from a controlled vocabulary (e.g., ISO 3166) mapped to the bank's internal geographic hierarchy | Count of risk records with a country code absent from the approved reference list | Target: 0
  - *Completeness* â No in-scope credit or counterparty credit risk record is missing a country-of-risk attribution | Count of in-scope records with null country of risk | Target: 0
  - *Consistency* â The country-of-risk attribution for the same counterparty is the same across all systems that hold an exposure to that counterparty | Count of counterparties where country-of-risk differs between risk system and counterparty master | Target: 0

---

**CDE-07 â Industry / Sector Classification**

- **Definition:** The industry or economic sector to which a counterparty or obligor is assigned â for example using a standard taxonomy such as NACE, GICS, or an internal equivalent. Used for sector concentration measurement and credit portfolio analysis.
- **Why critical:** Sector-level concentration is an explicit reporting requirement (Â¶57: *"single name, country and industry sector for credit risk"*). Principle 6 (Â¶50) names industry credit exposures by sector as a canonical on-demand aggregation case. Without consistent sector codes, the bank cannot demonstrate it has no hidden sector concentrations.
- **Risk types:** Credit, concentration
- **Criticality: 2** â Total exposure is unaffected, but the slice *exposure by industry sector* is wrong or unusable, directly failing the Â¶50 example and Â¶57 reporting requirement; sector concentration limits cannot be monitored.
- **Driven by:** Principle 4 (header) â *"Data should be available by â¦ industry"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*
- **Search terms:** industry code, sector code, industry classification, NACE code, GICS code, SIC code, economic sector, borrower industry
- **Data quality requirements:**
  - *Validity* â Every industry/sector code is drawn from the approved enterprise classification scheme; free-text entries are prohibited | Count of risk records with a sector code not present in the approved taxonomy | Target: 0
  - *Completeness* â Every credit and counterparty credit risk record carries an industry/sector code | Count of in-scope records with null sector | Target: 0
  - *Consistency* â The sector code assigned to a counterparty is the same across all exposure records for that counterparty within the same reporting period | Count of counterparties with more than one active sector code in the same period | Target: 0

---

**CDE-08 â Position / As-Of Date**

- **Definition:** The calendar date as of which a risk position or exposure amount is stated. Every aggregate risk figure is expressed as of a specific date; this element is what allows the bank to state *"as of [date], group exposure to X is Y"* and to produce consistent point-in-time snapshots.
- **Why critical:** Without a consistent, populated position date, it is impossible to know whether a set of records represent the same snapshot in time. Mixing positions from different dates in one aggregate produces a figure that is neither correct for any single date nor a valid approximation. Time-series analysis, stress test baselines, and regulatory submissions all require a clean position date.
- **Risk types:** Cross-cutting
- **Criticality: 3** â Without this element, the aggregate figure *group exposure as of [date]* cannot be computed at all, because the records being aggregated cannot be confirmed to represent the same point in time; a mixed-date aggregate is not a valid risk figure for any stated date.
- **Driven by:** Principle 5 (Â¶44) â *"produce aggregate risk information on a timely basis to meet all risk management reporting requirements"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"* (emphasis on date-specific aggregation); Principle 7 (Â¶52) â reports must be accurate and precise for decision-making
- **Search terms:** position date, as-of date, reference date, value date (where used as position date), report date, trade date vs settlement date distinction, snapshot date
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a non-null position date | Count of risk records with null position date | Target: 0
  - *Validity* â The position date on every record is a valid calendar date, not a default, placeholder, or future date beyond the reporting horizon | Count of records with position dates outside the valid reporting window (e.g., not between T-5 and T) | Target: 0
  - *Timeliness* â Risk records for a given position date are available in the aggregation layer within the agreed service window for that risk type | Elapsed time between position date close and record availability in the aggregation layer, measured per risk type | Target: within agreed SLA per Principle 5 requirements

---

**CDE-09 â General Ledger Reconciliation Key**

- **Definition:** The identifier â such as a trade reference number, journal entry reference, or account-level posting key â that ties a specific risk data record back to a specific entry in the general ledger or the authoritative system of record. This is the primary evidence that risk data and accounting data are in agreement.
- **Why critical:** Principle 3 explicitly requires reconciliation of risk data to accounting data. Without a joining key between a risk record and its GL counterpart, reconciliation cannot be performed: the bank can assert that totals agree but cannot identify which records are responsible for any gap. This is the operational mechanism for Â¶36(c), and its absence is the most common audit finding.
- **Risk types:** Cross-cutting (all risk types where balance-sheet or P&L impact exists)
- **Criticality: 2** â The risk aggregate can be computed, but it cannot be evidenced as accurate because the record-level link to the general ledger is absent; reconciliation degrades from a formal control to an assertion, directly failing Â¶36(c) and Â¶53(a).
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** trade reference number, deal ID, GL account reference, journal reference, posting reference, source transaction ID, reconciliation key, accounting reference, SWIFT reference (for settlements)
- **Data quality requirements:**
  - *Completeness* â Every risk record for a balance-sheet or P&L-impacting position carries a populated GL reconciliation key | Count of in-scope risk records with a null or blank reconciliation key | Target: 0 for balance-sheet positions; agreed tolerance for off-balance-sheet where GL posting structure differs
  - *Validity* â Every GL reconciliation key on a risk record resolves to an actual entry in the general ledger or system of record | Count of risk records whose reconciliation key has no match in the GL | Target: 0 unmatched keys; all exceptions logged and explained
  - *Accuracy* â The exposure amount on the risk record agrees to the balance on the matched GL entry within defined materiality tolerance | Sum of absolute differences between risk-record amount and matched GL balance, by asset class | Target: below the materiality threshold defined in Â¶56

---

**CDE-10 â Source System / Provenance Flag**

- **Definition:** The metadata attribute that identifies, for each risk data record, the source system from which the data originated, and whether the input was automated (straight-through processing) or manual (including end-user computing such as spreadsheets). This element is the mechanism by which Â¶36(b) and Â¶39 controls are operationalised.
- **Why critical:** The regulation requires banks to document all aggregation processes and to apply specific mitigants to manual and EUC inputs. If the provenance of a record is unknown, the bank cannot apply differentiated controls, cannot direct validation effort to high-risk inputs, and cannot demonstrate to a supervisor which portions of the risk aggregate are subject to which control regime. Supervisors explicitly expect this to be documented (Â¶39).
- **Risk types:** Cross-cutting
- **Criticality: 2** â The risk aggregate can be computed, but the bank cannot demonstrate that appropriate controls were applied to manual versus automated inputs; the accuracy assertion degrades and the Â¶29(a) independent validation cannot be scoped. Supervisory expectation in Â¶39 is directly unmet.
- **Driven by:** Principle 3 (Â¶36(b)) â *"Where a bank relies on manual processes and desktop applications â¦ it should have effective mitigants in place"*; Principle 3 (Â¶39) â *"banks to document and explain all of their risk data aggregation processes whether automated or manual â¦ include an explanation of the appropriateness of any manual workarounds"*; Principle 1 (Â¶29(a)) â independent validation must *"encompass all components of the bank's risk data aggregation and reporting processes"*
- **Search terms:** source system, feed name, data origin, manual override flag, EUC flag, end-user computing indicator, data lineage, automated vs manual indicator, upstream system name, data feed identifier
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a populated source system identifier and an automation/manual flag | Count of risk records with null source system or null manual/automated flag | Target: 0
  - *Validity* â The source system identifier on every record matches an entry in the authorised source system inventory | Count of records with unrecognised source system codes | Target: 0; unrecognised codes are treated as manual/EUC until resolved
  - *Accuracy* â Manual and EUC-flagged records are subject to documented additional validation checks; the proportion of manual inputs is measured and trended | Volume and percentage of risk records flagged as manual or EUC, by risk type and business line, per reporting period | Threshold: monitored against a defined acceptable maximum; increasing trend triggers escalation per Â¶40

---

**CDE-11 â Collateral / Credit Risk Mitigant Amount**

- **Definition:** The monetary value of collateral, guarantees, netting agreements, or other credit risk mitigants that reduce net exposure for a given position or counterparty. Required to compute net exposure for credit risk reporting and large-exposure limit monitoring.
- **Why critical:** Risk reports distinguish gross from net exposure (after mitigants). If collateral values are wrong or missing, net exposure figures are incorrect, and limits expressed on a net basis cannot be validly monitored. The regulation requires completeness including off-balance-sheet items (Â¶41), and off-balance-sheet credit enhancement is a primary form of collateral.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 2** â The gross exposure aggregate is unaffected (that is CDE-03), but the slice *net exposure after collateral* is wrong, making limit monitoring on a net basis and concentration measurement on a net basis unreliable.
- **Driven by:** Principle 4 (Â¶41) â *"include all material risk exposures, including those that are off-balance sheet"*; Principle 8 (Â¶58) â *"provide information in the context of limits and risk appetite/tolerance"* (net exposure is the relevant metric for limit comparison)
- **Search terms:** collateral value, collateral amount, eligible collateral, LGD mitigant, netting benefit, guarantee amount, credit risk mitigation, haircut-adjusted value, collateral haircut, recognised collateral
- **Data quality requirements:**
  - *Completeness* â Every credit exposure record that has an associated collateral agreement carries a populated collateral amount (which may be zero if the agreement has no current value) | Count of positions with an active collateral agreement in the collateral system that have no corresponding collateral record in the risk data store | Target: 0 unlinked collateral agreements on in-scope positions
  - *Accuracy* â The collateral value recorded in the risk data store agrees to the current value in the collateral management system within the agreed revaluation frequency | Sum of absolute differences between risk-data collateral value and collateral system value, by collateral type | Target: zero for daily-revalued collateral; within agreed tolerance for less frequently revalued instruments
  - *Timeliness* â Collateral values are refreshed at a frequency consistent with market volatility and the risk reporting cycle for the relevant exposure | Age of collateral valuation at the position date | Target: within the SLA defined for each collateral type; marked as stale and flagged if beyond the SLA

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Group-Wide Counterparty Consolidation (Single-Name Aggregation)**

- **Spans:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-06 (Geography / Country of Risk), CDE-07 (Industry / Sector Classification), CDE-11 (Collateral Amount)
- **What it is:** The requirement to resolve all records relating to the same legal counterparty â across booking systems, legal entities, risk types, and geographies â to a single aggregated exposure figure. This is not a property of any one data element; it is the correctness of the *join* between them, which depends on CDE-01 being a reliable key and all dimensional attributes being consistently attributed to the same counterparty.
- **Why it cannot be expressed as a single-element rule:** CDE-01 can be populated and unique in isolation, yet the join still fails if the same counterparty carries different sector codes in two systems (corrupting CDE-07), different country codes (corrupting CDE-06), or collateral that is booked against a parent entity rather than the subsidiary (corrupting CDE-11). The failure is relational, not elemental.
- **Driven by:** Principle 4 (Â¶41) â *"include all material risk exposures, including those that are off-balance sheet"*; Principle 5 (Â¶46(a)) â *"aggregated credit exposure to a large corporate borrower"* as a critical risk; Principle 6 (Â¶50) â on-demand aggregation across business lines and geographic areas

| Dimension | Rule intent | Measurement | Threshold |
|---|---|---|---|
| *Consistency* | The same counterparty carries identical country-of-risk and sector codes across all systems contributing to the consolidated risk store | Count of counterparties where country-of-risk or sector code differs between any two source systems for the same reporting period | Target: 0; all exceptions investigated before report production |
| *Completeness* | No sub-limit of a counterparty group (parent/subsidiary relationships) is absent from the consolidation perimeter | Count of counterparty legal entities in the group hierarchy that have active positions but no record in the consolidated risk data store | Target: 0 |
| *Accuracy* | The sum of individual-system exposures for a counterparty agrees to the consolidated single-name figure (after intragroup elimination) | Difference between sum of source-system exposures and consolidated figure, by counterparty, for the top-N exposures | Target: zero unexplained variance; all differences attributable to documented intragroup eliminations |

---

**XDQ-02 â Risk-to-Finance Reconciliation Control**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key), CDE-08 (Position/As-Of Date), CDE-02 (Legal Entity Identifier)
- **What it is:** The formal control that evidences agreement between the risk data aggregate and the accounting record â at the level of the banking group and at the subsidiary legal entity level. This is the operationalisation of Â¶36(c) and Â¶36(a). It requires CDE-09 to function as the join key, CDE-03 to be the amount being compared, CDE-08 to ensure both sides are as of the same date, and CDE-02 to ensure the comparison is within the correct legal entity.
- **Why it cannot be expressed as a single-element rule:** The reconciliation is a cross-system comparison. Even if CDE-03 is accurate within the risk system and CDE-09 is populated, the reconciliation can still fail because the GL is queried as of a different date (CDE-08 mismatch), or because positions are compared at a different legal entity level (CDE-02 mismatch). The integrity of the reconciliation depends on all four elements being correct and consistent simultaneously.
- **Driven by:** Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*

| Dimension | Rule intent | Measurement | Threshold |
|---|---|---|---|
| *Accuracy* | The aggregate gross exposure in the risk data store agrees to the aggregate outstanding balance in the general ledger, by legal entity and by risk type, as of the same position date | Sum of absolute differences between risk-aggregate and GL-aggregate, by legal entity and risk type, for each reporting cycle | Target: below the materiality threshold defined per Â¶56; all variances above threshold investigated and explained before report sign-off |
| *Completeness* | Every position recorded in the general ledger that falls within the risk reporting perimeter has a corresponding record in the risk data store | Count of GL entries within the risk perimeter that have no matching risk record (by reconciliation key, CDE-09) | Target: 0 unmatched GL entries; exceptions logged with root cause |
| *Timeliness* | The reconciliation is completed and exceptions are resolved before risk reports are distributed | Elapsed time between position-date close and completion of risk-to-finance reconciliation sign-off | Target: within the reporting production window defined for each report frequency; breach triggers escalation |

---

## 4. Out of Scope

The following principles address obligations that a data catalog, CDE register, and data quality monitoring framework cannot satisfy. They are either reporting-layer or governance-layer obligations that operate above the data tier, or they require human judgement, board-level decisions, and process controls that no metadata management system can substitute for.

---

**Principle 7 (Â¶53â56) â Report accuracy and reconciliation *processes***: The principle drives CDE-09 (Reconciliation Key) and XDQ-02 (Risk-to-Finance Reconciliation Control) above, so it is not entirely out of scope. However, the *process* requirements in Â¶53(b) and Â¶53(c) â maintaining an inventory of validation rules applied to reports, operating integrated exception-reporting procedures, establishing accuracy and precision standards for both regular and stress reporting â are workflow, model governance, and report production controls. A catalog can hold the inventory of validation rules as reference metadata, but it cannot execute them, route exceptions, or enforce that senior management has set the precision standards. These require a model risk management framework, a report production workflow, and a senior-management sign-off process.

**Principle 8 (Â¶57â60) â Report comprehensiveness**: This principle both drives CDEs and remains partially out of scope, which requires explicit explanation. It drives CDE-07 (Industry/Sector) because Â¶57 names industry sector as a required dimension â that is a data element a catalog can govern. However, Â¶57â60's core obligations â determining that reports cover *all* material risk areas, include forward-looking stress test results, present capital and liquidity ratio projections, and assess emerging concentrations â are report-content and risk-appetite decisions made by the board and senior management. A catalog cannot determine whether a report's scope is sufficient, whether stress scenarios are appropriate, or whether the board is receiving the right qualitative interpretation. These require risk governance frameworks, stress testing methodologies, and board engagement processes.

**Principle 9 (Â¶61â69) â Clarity and usefulness**: Almost entirely out of scope for a data catalog. The obligations here are report design, recipient engagement (Â¶69: *"confirm periodically with recipients that the information â¦ is relevant and appropriate"*), balancing quantitative and qualitative content (Â¶62), and ensuring reports support decision-making at the right level of the organisation. A catalog can host the data dictionary referenced in Â¶67 (*"inventory and classification of risk data items"*), which is a narrow contribution. It cannot make reports clear, ensure qualitative interpretation is sound, or verify that the board is asking the right questions.

**Principle 10 (Â¶70â71) â Frequency**: The obligation is for the board and senior management to set frequency requirements for each report, test that those requirements can be met in stress, and ensure intraday production is possible for critical positions. A catalog can document the agreed service levels as metadata on datasets, and CDE-08 (Position Date) supports timeliness monitoring. But setting frequency policy, stress-testing report production timelines, and ensuring intraday infrastructure capability are IT operations, business continuity, and governance decisions that no catalog or CDE register can address.

**Principle 11 (Â¶72â74) â Distribution**: The obligation is for procedures to ensure rapid dissemination to appropriate recipients while maintaining confidentiality. A catalog can document data classification and sensitivity labels (supporting the confidentiality aspect), but the distribution procedures themselves â who receives which report, through which channel, with what access controls â are information security, workflow, and governance controls outside the scope of a data governance catalog.

**Principle 1 (Â¶27â31) â Governance framework**: Principle 1 is the overarching governance obligation. It drives the need for the entire CDE register (Â¶30 requires senior management to *"identify data critical to risk data aggregation"*) and the need for a dictionary (Â¶37). However, the substantive obligations â board review and approval of the framework (Â¶28), independent validation of aggregation and reporting processes (Â¶29(a)), inclusion of data architecture in due diligence for acquisitions (Â¶29(b)), IT strategic planning (Â¶30) â are organisational governance and audit commitments. A data catalog supports the board's ability to evidence compliance, but it cannot constitute the governance framework itself, approve it, or perform the independent validation.

**Principle 2 (Â¶32â35) â IT infrastructure resilience**: Principle 2 drives CDE-01 (Counterparty Identifier) and CDE-02 (Legal Entity Identifier) through Â¶33's single-identifier requirement, and it motivates the entire catalog structure. However, Â¶32's business continuity and business impact analysis requirements, and Â¶34's data ownership and lifecycle control obligations, are IT operations and organisational accountability matters. A catalog can record data ownership assignments and document lineage, but it cannot ensure the IT infrastructure meets recovery time objectives or that business owners are actually exercising their control responsibilities.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | **3** | 2 (Â¶33), 5 (Â¶46a/b) | Uniqueness, Completeness, Consistency |
| CDE-02 | Legal Entity Identifier (Booking Entity) | **3** | 2 (Â¶33), 4 (Â¶41, header) | Validity, Completeness, Consistency |
| CDE-03 | Gross Exposure Amount | **3** | 3 (Â¶36a), 4 (Â¶41), 5 (Â¶46a) | Accuracy, Completeness, Timeliness |
| CDE-04 | Risk Type Classification | **2** | 7 (Â¶53a), 8 (Â¶57), 4 (header) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | **2** | 4 (header), 6 (Â¶50) | Validity, Completeness, Consistency |
| CDE-06 | Geography / Country of Risk | **2** | 4 (header), 6 (Â¶50) | Validity, Completeness, Consistency |
| CDE-07 | Industry / Sector Classification | **2** | 4 (header), 6 (Â¶50), 8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-08 | Position / As-Of Date | **3** | 5 (Â¶44), 6 (Â¶50), 7 (Â¶52) | Completeness, Validity, Timeliness |
| CDE-09 | GL Reconciliation Key | **2** | 3 (Â¶36c), 7 (Â¶53a) | Completeness, Validity, Accuracy |
| CDE-10 | Source System / Provenance Flag | **2** | 3 (Â¶36b, Â¶39), 1 (Â¶29a) | Completeness, Validity, Accuracy |
| CDE-11 | Collateral / Credit Risk Mitigant Amount | **2** | 4 (Â¶41), 8 (Â¶58) | Completeness, Accuracy, Timeliness |

**Criticality-3 count: 4 (CDE-01, CDE-02, CDE-03, CDE-08).** This is within the specified target of 4â5. Each satisfies the step-2 test: without it, a named aggregate figure â total group exposure to a counterparty, consolidated exposure by entity, total credit exposure, and any date-specific aggregate respectively â cannot be computed at all. All remaining elements are rated 2: the aggregate is computable but a required slice, reconciliation control, or provenance control degrades. No element has been rated 1 because no element in this register is purely contextual â each, if absent or wrong, degrades either an aggregate slice or a mandatory control. If the register were extended to include purely descriptive fields (e.g., counterparty long name, address), those would be 1s; none were included because they do not meet the CDE qualification tests.