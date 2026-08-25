# BCBS 239 — Data Catalog Governance Analysis

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **End the "data blind spot" that amplified the 2008 crisis.** Banks could not rapidly aggregate their own risk positions across legal entities and business lines. The regulation demands that this aggregation be possible in normal times and, critically, in stress or crisis (¶35: *"risk data aggregation capabilities should meet all Principles below simultaneously"*; ¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis"*).

- **Establish a single authoritative data layer for risk.** Multiple competing versions of the same exposure figure undermine confidence in reported numbers. The regulation demands convergence toward one source per risk type (¶36(d): *"A bank should strive towards a single authoritative source for risk data per each type of risk"*) and a shared data dictionary (¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"*).

- **Make aggregation traceable and reconcilable.** Risk data must be tied back to accounting sources. Manual and end-user-computing (EUC) interventions must be documented rather than hidden (¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; ¶39: documentation of *"all of their risk data aggregation processes whether automated or manual"*).

- **Require multidimensional slicing as a standing capability, not a one-off exercise.** Aggregation by business line, legal entity, asset type, industry, and region must be routine, not built ad hoc in response to each supervisory request (¶4 header and ¶50: *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date … as well as industry credit exposures … across all business lines and geographic areas"*).

- **Bind governance to data.** Board and senior management are personally accountable for understanding the limitations of what they receive (¶30, ¶31). Data ownership roles — business and IT — must be formally assigned (¶34: *"Roles and responsibilities should be established as they relate to the ownership and quality of risk data"*).

- **Treat accuracy and completeness as measurable obligations, not aspirations.** Banks must measure and monitor data accuracy and completeness, with escalation plans for failures (¶40: *"Supervisors expect banks to measure and monitor the accuracy of data and to develop appropriate escalation channels"*; ¶43: *"Supervisors expect banks to produce aggregated risk data that is complete and to measure and monitor the completeness"*).

**Who it applies to**

Globally systemically important banks (G-SIBs) are the primary addressees; the Basel Committee subsequently extended the expectation to domestic systemically important banks (D-SIBs). The principles apply at the **banking group** level — legal entities, subsidiaries, and branches — not just at the solo-entity level (¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group"*).

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** A unique, persistent, system-independent code that identifies a legal counterparty (borrower, trading counterparty, issuer) across all systems where the bank books or manages exposures to that counterparty. Distinct from internal customer numbers, which may differ by system.
- **Why critical:** Without a resolved counterparty identifier, exposures recorded in different booking systems, business lines, or geographies cannot be summed to a single obligor. A bank cannot know its aggregate credit exposure to a large corporate borrower (¶46(a)) or its counterparty credit risk exposure in derivatives (¶46(b)) unless all records for that counterparty carry the same key.
- **Risk types:** Credit, counterparty, concentration
- **Criticality: 3** — Aggregation across systems is **impossible** without a shared counterparty key. The failure does not degrade a figure; it produces a figure that is simply wrong by omission. This is the joining key specified in the rubric.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures"*; Principle 5 (¶46(a),(b))
- **Search terms:** counterparty ID, counterparty code, obligor ID, client ID, legal entity identifier (LEI), GIIN, entity key, party key, BIC-based identifier, golden record ID
- **Data quality requirements:**
  - *Uniqueness* — Each distinct legal counterparty resolves to exactly one identifier across all in-scope systems | Count of counterparties with more than one active identifier in the enterprise reference table | Target: 0 duplicates; alert threshold: any new duplicate
  - *Completeness* — Every exposure record carries a non-null, non-placeholder counterparty identifier | Count of exposure records with null, blank, or default-value counterparty identifier | Target: 0; tolerance: <0.01% of records by notional exposure
  - *Validity* — Every counterparty identifier on an exposure record resolves to an active entry in the enterprise counterparty master | Count of exposure records whose identifier returns no match in the master | Target: 0 unmatched
  - *Timeliness* — New counterparty master entries are available to downstream systems within the agreed service level before the next position capture | Age of counterparty master records at time of first downstream use | SLA: same-day creation for new trades

---

**CDE-02 — Legal Entity Identifier (Booking Entity)**

- **Definition:** A unique code that identifies the specific legal entity within the banking group in which an exposure or position is booked. Distinct from business line or cost centre; this is the regulated legal entity — subsidiary, branch, or parent — that holds the position on its balance sheet.
- **Why critical:** Group-level consolidation and subsidiary-level reporting both require that every position be unambiguously assigned to one legal entity. Without this, the bank cannot isolate a subsidiary's risk profile for regulatory reporting to a local supervisor, nor can it roll positions up to the group without double-counting or gaps.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3** — Group consolidation is **impossible** without it. Assigning an exposure to the wrong entity, or leaving it unassigned, invalidates the consolidated figure for at least one entity.
- **Driven by:** Principle 2 (¶33) — *"integrated data taxonomies and architecture across the banking group, which includes … use of single identifiers … for data including legal entities"*; Principle 4 (header) — *"capture and aggregate all material risk data across the banking group"*
- **Search terms:** legal entity code, booking entity, entity ID, subsidiary code, branch code, LEI (when used as booking-entity key), consolidation entity, reporting unit
- **Data quality requirements:**
  - *Completeness* — Every position and exposure record carries a non-null booking entity code | Count of records with null or missing entity code | Target: 0
  - *Validity* — Every booking entity code maps to an active entry in the group legal entity hierarchy | Count of codes that do not resolve in the hierarchy | Target: 0
  - *Consistency* — The booking entity code on a risk record matches the legal entity recorded on the corresponding accounting entry for the same transaction | Count of transaction identifiers where risk and accounting entity codes differ | Target: 0; alert on any mismatch
  - *Uniqueness* — Each legal entity has exactly one active code; no two codes refer to the same regulated entity | Count of entities with more than one active code | Target: 0

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The pre-mitigation monetary amount of an exposure or position, expressed in the transaction currency, representing the maximum potential loss the bank faces from a single instrument, transaction, or netting set before the application of collateral, guarantees, or credit risk mitigation.
- **Why critical:** This is the primary input to every risk aggregation calculation. Net exposure figures, risk-weighted assets, large exposure limits, and stress test outputs are all derived from or reconciled against gross exposure. Errors here propagate into every downstream risk metric.
- **Risk types:** Credit, counterparty, market, concentration
- **Criticality: 3** — A wrong gross exposure amount directly invalidates the aggregate it feeds. No amount of correct metadata recovers an incorrect monetary figure.
- **Driven by:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (¶41) — *"include all material risk exposures, including those that are off-balance sheet"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** exposure amount, outstanding balance, notional amount, mark-to-market, fair value, drawn balance, commitment amount, current exposure, potential future exposure
- **Data quality requirements:**
  - *Accuracy* — The sum of gross exposure amounts per legal entity and risk class reconciles to the corresponding accounting balance or system-of-record total within defined materiality tolerance | Signed difference between risk aggregation total and accounting/source-system total, per entity per risk class | Tolerance: ≤0.1% of total or a defined monetary threshold, whichever is lower
  - *Completeness* — No off-balance-sheet exposure category is absent from the population | Count of instrument types in scope that have zero exposure records in the aggregation run; comparison of instrument coverage against defined scope inventory | Target: 0 gaps
  - *Validity* — Exposure amount is a positive non-zero numeric value for all in-scope instrument types | Count of records with null, zero, or negative exposure where the instrument type requires a positive value | Target: 0
  - *Timeliness* — Exposure amounts reflect positions as of the stated as-of date; no stale valuations beyond the agreed tolerance | Count of records whose valuation date differs from the position date by more than the permitted lag | SLA: defined per risk type; zero tolerance for traded products

---

**CDE-04 — Risk Type Classification**

- **Definition:** A controlled vocabulary term that assigns each exposure or position to a primary risk category — typically credit risk, market risk, liquidity risk, operational risk, counterparty credit risk — in accordance with the bank's internal risk taxonomy. This is the top-level partitioning of the risk register.
- **Why critical:** Risk reports are structured around risk types (¶57 names credit, market, liquidity, and operational explicitly). Regulatory capital calculations are risk-type-specific. Without a reliable, consistently applied classification, positions may be counted under the wrong regime or omitted from a category entirely.
- **Risk types:** Cross-cutting
- **Criticality: 3** — A misclassified exposure is counted in the wrong aggregate and absent from the correct one. The error affects two figures simultaneously and is invisible unless the classification itself is auditable. This drives a risk calculation per the rubric.
- **Driven by:** Principle 8 (¶57) — *"exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 4 (header) — *"permit identifying and reporting risk exposures, concentrations and emerging risks"*; ¶37 — *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently"*
- **Search terms:** risk category, risk type, risk class, risk taxonomy code, Basel risk class, regulatory risk type, risk bucket
- **Data quality requirements:**
  - *Validity* — Every exposure record carries a risk type code drawn from the approved controlled list | Count of records with a risk type code not in the approved taxonomy | Target: 0; any out-of-vocabulary value triggers immediate investigation
  - *Completeness* — Every in-scope exposure record has a non-null risk type assignment | Count of records with null or missing risk type | Target: 0
  - *Consistency* — The risk type assigned to an instrument in the risk system matches the risk type recorded for that instrument in the accounting/capital system | Count of instrument identifiers where the two systems disagree | Target: 0 discrepancies; alert on any new mismatch
  - *Accuracy* — Classification rules are applied uniformly: instruments of the same type receive the same risk type code across all booking systems | Count of instruments of the same product type that carry different risk type codes in different systems | Target: 0

---

**CDE-05 — Business Line**

- **Definition:** A standardised code or label that assigns an exposure or position to a distinct business segment of the bank — for example, corporate banking, retail banking, trading, treasury, private banking — using a group-wide taxonomy that is stable across reporting periods.
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. Senior management reports are routinely structured by business line, and risk appetite is often set and monitored at this level. Without a consistent business line code, exposures cannot be correctly partitioned, and concentrations within a line may be invisible.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 2** — If business line is missing or inconsistent, the overall aggregate is still computable, but the business-line slice is incomplete or unreliable. This degrades a required reporting dimension rather than invalidating the total.
- **Driven by:** Principle 4 (header and ¶43) — *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date … across all business lines and geographic areas"*
- **Search terms:** business line code, business unit, division, segment code, LOB (line of business), profit centre, cost centre (where used as business line proxy)
- **Data quality requirements:**
  - *Completeness* — Every exposure and position record carries a non-null business line code | Count of records with null or missing business line | Target: <0.1% of records by count and notional
  - *Validity* — Every business line code is drawn from the approved group-level taxonomy | Count of codes not in the approved list | Target: 0
  - *Consistency* — The business line code is applied uniformly for the same product type and booking desk across systems | Count of positions where identical booking desks carry different business line codes in risk vs. finance systems | Alert threshold: any structural mismatch

---

**CDE-06 — Geography / Country of Risk**

- **Definition:** A standardised ISO country code or approved regional grouping that identifies the primary country of risk for an exposure — typically the country of the obligor's domicile, the country of collateral, or the country in which a position's primary risk driver resides — as defined in the bank's geographic risk policy.
- **Why critical:** Principle 4 requires aggregation by region; Principle 6 (¶50) explicitly cites country credit exposure as the canonical example of an ad hoc aggregation request a bank must be able to fulfil rapidly. During sovereign stress events, this element is the primary filter.
- **Risk types:** Credit, market, concentration
- **Criticality: 2** — The aggregate exposure to a country is uncomputable if country of risk is absent or inconsistently assigned, but other aggregates (total credit exposure, business line totals) are unaffected. A required reporting dimension is degraded.
- **Driven by:** Principle 4 (header) — *"Data should be available by … region and other groupings"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*
- **Search terms:** country of risk, obligor country, country code, ISO 3166 country, geographic region, sovereign exposure flag, country of domicile, booking country
- **Data quality requirements:**
  - *Completeness* — Every credit and market exposure record carries a non-null country of risk code | Count of records with null or missing country code as a proportion of total records by notional | Target: <0.1%
  - *Validity* — Every country code is a valid ISO 3166-1 alpha-2 or alpha-3 code, or an approved regional grouping code | Count of non-conforming codes | Target: 0
  - *Consistency* — The country of risk assigned in the risk system is consistent with the country recorded in the trade confirmation or accounting system for the same instrument | Proportion of sampled instruments where the two systems agree | Target: ≥99.9%

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** A standardised industrial classification code — drawn from an approved scheme such as NACE, SIC, GICS, or an internal equivalent — that assigns each credit obligor to an economic sector, used to identify sectoral concentrations in the lending and trading portfolios.
- **Why critical:** Principle 8 (¶57) names industry sector as a required component of credit risk reports. Principle 6 (¶50) cites industry credit exposures as the second canonical example of a rapid aggregation requirement. Sectoral concentration risk cannot be identified or reported without this element.
- **Risk types:** Credit, concentration
- **Criticality: 2** — Sectoral aggregations and concentration metrics are unproducible or unreliable without it, but total credit exposure figures remain valid. A required reporting slice is degraded.
- **Driven by:** Principle 4 (header) — *"Data should be available by … industry"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types"*
- **Search terms:** industry code, sector code, NACE code, SIC code, GICS sector, industry classification, obligor sector, counterparty sector
- **Data quality requirements:**
  - *Completeness* — Every credit exposure record for a non-sovereign obligor carries a non-null sector code | Count of non-sovereign credit records with null or missing sector code | Target: <0.5% by notional
  - *Validity* — Every sector code is drawn from the approved classification scheme version in effect for the reporting period | Count of codes not in the approved scheme | Target: 0
  - *Consistency* — The sector code assigned to a counterparty is the same across all exposure records for that counterparty within a reporting period | Count of counterparties with more than one active sector code in the same period | Target: 0 for large and mid-corporate; <1% for retail/SME

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The calendar date as of which an exposure, position, or balance is stated. This is the temporal anchor for every aggregate: it determines which records are included in a snapshot and allows comparison across time periods. Distinct from trade date, settlement date, or report run date.
- **Why critical:** Every risk aggregate is defined relative to a specific date. Mixing records with different as-of dates in a single aggregation run produces a figure that is neither current nor historical — it is meaningless. Principle 5 requires that aggregated data be up-to-date; Principle 6 requires production of data *"as of a specified date"* (¶50). Without a reliable, consistent as-of date on every record, timeliness cannot be demonstrated and completeness cannot be measured.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3** — If as-of date is missing, null, or inconsistently populated, the temporal integrity of the aggregate is void. A figure labelled as "30 June" that includes records from other dates is not a 30 June figure. This is a temporal joining key; its failure invalidates the aggregate.
- **Driven by:** Principle 5 (header and ¶44) — *"generate aggregate and up-to-date risk data in a timely manner"*; Principle 6 (¶50) — *"aggregate risk data … as of a specified date"*; Principle 7 (¶52) — *"accurate and precise to ensure … the aggregated information"*
- **Search terms:** position date, as-of date, valuation date, snapshot date, reference date, reporting date, effective date, trade date (distinguish carefully)
- **Data quality requirements:**
  - *Completeness* — Every position and exposure record carries a non-null as-of date | Count of records with null or missing as-of date | Target: 0
  - *Validity* — The as-of date is a valid calendar date that falls within the expected range for the reporting cycle | Count of records with as-of dates outside the expected window (e.g., future-dated or more than one business day stale for daily runs) | Target: 0 anomalies
  - *Timeliness* — All records in a given aggregation run carry the same as-of date, or the distribution of as-of dates across records is within the permitted tolerance for the risk type | Count of records in a run whose as-of date differs from the stated run date by more than the permitted lag | SLA: 0 records outside tolerance for trading book; defined tolerance for banking book
  - *Consistency* — The as-of date on a risk record matches the valuation date on the corresponding accounting entry | Count of transaction identifiers where the two dates differ | Target: 0 for same-day positions

---

**CDE-09 — General Ledger / Source System Reconciliation Key**

- **Definition:** The identifier — typically a transaction reference, deal number, or accounting entry reference — that links a risk data record to its corresponding entry in the general ledger or the system of record (trading system, loan origination system, etc.). This is the join key that makes ¶36(c) operationally testable.
- **Why critical:** Principle 3 (¶36(c)) requires that risk data be reconciled with accounting sources. Without a reconciliation key on every risk record, this reconciliation cannot be performed systematically. Any record that cannot be matched to a GL entry is either a phantom exposure (present in risk, absent in accounting) or a missing exposure (present in accounting, absent in risk). Both are material errors. This is the category-7 element in the rubric and among the most commonly omitted.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3** — Accuracy and integrity cannot be evidenced without this key. ¶36(c) is not merely aspirational; it is a reconciliation obligation. An unmatched risk record is an unexplained discrepancy that must be escalated per ¶40. The failure of this element does not degrade an aggregate — it removes the basis for claiming the aggregate is accurate.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** deal ID, trade reference, transaction ID, GL reference, accounting entry ID, loan number, position ID, booking reference, system transaction key, source system key
- **Data quality requirements:**
  - *Completeness* — Every risk data record carries a non-null reconciliation key linking it to the source system or general ledger | Count of risk records with null or missing reconciliation key | Target: 0; any null triggers an exception
  - *Validity* — Every reconciliation key on a risk record resolves to an active record in the source system or GL | Count of risk records whose reconciliation key returns no match | Target: 0; unmatched keys escalated same-day
  - *Uniqueness* — Each source-system transaction is represented exactly once in the risk aggregation dataset (no duplication, no omission) | Count of reconciliation keys that appear more than once in the risk dataset for the same as-of date; count of GL keys with no matching risk record | Target: 0 duplicates; 0 unmatched GL entries above materiality threshold
  - *Accuracy* — The exposure amount on the risk record agrees with the balance on the corresponding GL or source-system entry within the defined materiality tolerance | Sum of absolute differences between risk-record amounts and matched GL balances | Tolerance: per ¶56 analogy, omission or misstatement that could influence risk decisions

---

**CDE-10 — Source System Identifier and Manual Override Flag**

- **Definition:** Two related attributes on every risk data record: (a) a code identifying the system from which the record originates (trading system, loan system, treasury system, manual upload, EUC spreadsheet), and (b) a boolean or categorical flag indicating whether the record was subject to a manual adjustment, override, or end-user-computing process after extraction from the authoritative source.
- **Why critical:** ¶36(b) requires effective controls over manual processes and EUC; ¶39 requires documentation and explanation of all manual workarounds. Without these attributes, a bank cannot identify which records were manually touched, cannot measure the proportion of risk data flowing through EUC, and cannot demonstrate to supervisors that manual interventions are controlled and declining. This is the category-8 lineage/provenance element, explicitly named in the rubric as among the most often forgotten.
- **Risk types:** Cross-cutting (all risk types — this is a data provenance element)
- **Criticality: 2** — The aggregate figure is computable without this flag, but the bank cannot distinguish automated from manual inputs, cannot evidence the control standard required by ¶36(b), and cannot produce the documentation required by ¶39. The aggregate is produced but unauditable in part.
- **Driven by:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications … it should have effective mitigants"*; Principle 3 (¶39) — *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual"*; Principle 2 (¶34) — *"adequate controls throughout the lifecycle of the data"*
- **Search terms:** source system code, source system name, data origin, feed source, EUC flag, manual input flag, override flag, manual adjustment indicator, data lineage tag, system of origin
- **Data quality requirements:**
  - *Completeness* — Every risk data record carries a non-null source system code and a non-null manual override flag | Count of records with null source system code or null manual flag | Target: 0
  - *Validity* — Every source system code is drawn from the approved source system inventory registered in the data catalog | Count of records whose source system code does not appear in the inventory | Target: 0; unlisted source codes indicate an unregistered feed and trigger immediate governance review
  - *Accuracy* — The manual override flag correctly reflects whether the record was altered post-extraction | Proportion of flagged-manual records that can be confirmed by audit trail as having been manually altered; proportion of unflagged records where an audit trail shows manual alteration | Target: 100% flag accuracy for in-scope processes; monitored quarterly by internal audit
  - *Timeliness* — Source system lineage is attached to records at the time of ingestion, not retrospectively | Count of records where source system code was added after the initial load timestamp | Target: 0 retrospective assignments

---

**CDE-11 — Collateral Value and Type**

- **Definition:** The current monetary value of financial or physical collateral pledged against an exposure, together with a standardised code identifying the collateral type (cash, government securities, residential property, commercial property, equities, etc.). Value is stated in the collateral currency as of the last valuation date.
- **Why critical:** Net credit exposure — the figure that drives regulatory capital for secured lending and the Risk Weighted Asset calculation — cannot be computed without knowing how much collateral offsets gross exposure (¶41 includes off-balance-sheet items; netting and collateral are material to the completeness of risk measurement). Large exposure limits under CRR/Basel are stated on a net-of-eligible-collateral basis. Without collateral value and type, the bank reports gross exposure as if it were net, overstating or understating risk depending on context.
- **Risk types:** Credit, counterparty
- **Criticality: 2** — Net credit exposure figures are degraded or uncomputable for secured transactions, but unsecured exposure aggregates remain valid. A significant class of exposures is misrepresented rather than the entire aggregate being invalidated.
- **Driven by:** Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"* (collateral values feed accounting fair value adjustments); Principle 5 (¶46(a)) — *"aggregated credit exposure to a large corporate borrower"* (implicitly net of eligible mitigation)
- **Search terms:** collateral value, collateral amount, security value, haircut, eligible collateral flag, collateral type code, LTV (loan-to-value), margin balance, security type, pledge value
- **Data quality requirements:**
  - *Timeliness* — Collateral values are re-marked within the frequency required by the risk type (daily for traded collateral, monthly minimum for property) | Count of collateral records whose last valuation date exceeds the permitted stale-value threshold for their collateral type | Target: 0 breaches of type-specific SLA
  - *Validity* — Collateral type code is drawn from the approved collateral taxonomy aligned to the regulatory eligibility framework | Count of codes outside the approved list | Target: 0
  - *Accuracy* — For cash and liquid security collateral, value reconciles to the custodian or clearing house statement | Sum of absolute differences between internal collateral records and custodian/CCP statements | Tolerance: 0 for cash; defined threshold for securities
  - *Completeness* — Every secured exposure record links to at least one collateral record; the absence of a collateral link on a secured instrument is flagged as an exception | Count of instruments classified as secured with no associated collateral record | Target: 0

---

## 3. Cross-Cutting Data Quality Requirements

**XDQ-01 — Counterparty Resolution Across Systems**

- **Spans:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-05 (Business Line), CDE-06 (Geography), CDE-07 (Industry / Sector)
- **What this is:** The enterprise-wide process of resolving multiple system-local representations of the same legal counterparty into a single golden record. This cannot be expressed as a quality check on any single element because the problem is defined across systems. A counterparty identifier that passes all single-system validity checks may still produce a duplicated or split aggregate if the same counterparty is represented by different codes in different booking systems.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including … counterparties"*; Principle 3 (¶36(d)) — *"a single authoritative source for risk data per each type of risk"*; Principle 4 (¶41) — *"include all material risk exposures"* (a counterparty whose exposures are split across two IDs has half its exposures missing from each aggregate)
- **Dimension:** *Uniqueness* and *consistency* (cross-system)
- **Rule intent:** Every legal counterparty that exists in more than one booking or risk system resolves to a single master identifier, and all exposure records for that counterparty in all systems carry that master identifier (or a cross-reference to it)
- **Measurement:**
  - Count of counterparty names or LEIs that match to more than one active identifier in the enterprise master
  - Count of pairs of exposure records (from different source systems) that refer to the same legal entity by name or LEI but carry different counterparty identifiers with no cross-reference
  - Proportion of the bank's top-100 credit exposures (by gross notional) for which a complete cross-system reconciliation of all records to a single counterparty ID can be demonstrated
- **Suggested threshold:** 0 unresolved duplicates in the top-500 counterparties by gross exposure; full resolution across all G-SIB-reportable counterparties; residual unresolved count reported to data governance committee monthly
- **Why cross-cutting:** Counterparty resolution requires coordination across CDE-01 (the key), CDE-03 (the amounts being reconciled), and the dimension elements (CDE-05, CDE-06, CDE-07) that are only meaningful once the counterparty is correctly identified. No single-element monitor detects the cross-system fragmentation.

---

**XDQ-02 — Risk-to-Finance Reconciliation**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (GL / Source System Reconciliation Key), CDE-02 (Legal Entity Identifier), CDE-08 (Position / As-Of Date), CDE-10 (Source System Identifier and Manual Override Flag)
- **What this is:** The systematic comparison of aggregate risk positions, by legal entity and as-of date, against the corresponding balances in the general ledger or the system of record. This is the operational test of ¶36(c). It requires CDE-09 as the join key, CDE-03 as the amount being compared, CDE-02 to scope the comparison to the correct entity, CDE-08 to synchronise the comparison to the correct date, and CDE-10 to identify and separately account for manually adjusted records. No single-element monitor performs this; it is a cross-register comparison.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*; ¶40 — *"measure and monitor the accuracy of data and to develop appropriate escalation channels"*
- **Dimension:** *Accuracy* and *completeness* (cross-system)
- **Rule intent:** For each legal entity and each risk type, the sum of gross exposure amounts in the risk aggregation dataset equals the sum of corresponding balances in the general ledger (or system of record) within the defined materiality tolerance; and every GL balance in scope has a matching risk record
- **Measurement:**
  - Aggregate difference (risk total minus GL total) by legal entity, risk type, and as-of date, expressed both in absolute terms and as a percentage of the GL total
  - Count of GL entries in scope with no matching reconciliation key in the risk dataset (items in finance but not in risk)
  - Count of risk records with a reconciliation key that finds no match in the GL (items in risk but not in finance)
  - Proportion of manual-override-flagged records (CDE-10) as a share of total records in each reconciliation run, tracked over time
- **Suggested threshold:** Aggregate monetary difference ≤0.1% of total GL balance per entity per risk type; 0 unmatched items above the defined de-minimis amount; manual-override proportion reported with direction-of-trend commentary; escalation to Chief Risk Officer for any reconciliation break exceeding materiality
- **Why cross-cutting:** Reconciliation is definitionally a comparison between two datasets. It cannot be performed by monitoring any single CDE in isolation. The test requires the join (CDE-09), the amount (CDE-03), the entity scope (CDE-02), the temporal anchor (CDE-08), and the provenance audit (CDE-10) to operate together.

---

**XDQ-03 — Temporal Consistency of Aggregation Runs**

- **Spans:** CDE-08 (Position / As-Of Date), CDE-03 (Gross Exposure Amount), CDE-01 (Counterparty Identifier), CDE-09 (Reconciliation Key)
- **What this is:** The requirement that all records contributing to a single aggregation run refer to the same as-of date, and that the run captures the complete population as of that date — no records from a prior date substituted because the current-date record is unavailable, and no records silently excluded because they arrived after the cut-off. This is a completeness and timeliness obligation that cannot be monitored on any single element; it is a property of the run as a whole.
- **Driven by:** Principle 5 (¶44, ¶45) — *"produce aggregate risk information on a timely basis"* and the need to respond *"rapidly during times of stress/crisis"*; Principle 6 (¶50) — *"aggregate risk data … as of a specified date"*; Principle 4 (¶43) — *"produce aggregated risk data that is complete"*
- **Dimension:** *Timeliness* and *completeness* (run-level)
- **Rule intent:** Within each aggregation run, the distribution of as-of dates across all contributing records conforms to the stated run date; the count of records is consistent with the prior run (adjusted for known new bookings and maturities); and the run completes within the agreed production SLA
- **Measurement:**
  - Distribution of as-of dates across records in each run — number and notional weight of records whose as-of date differs from the stated run date
  - Run-over-run change in record count and aggregate notional, with unexplained variances above a defined threshold flagged
  - Time elapsed from risk data cut-off to availability of validated aggregate output, compared against the SLA for each risk type
  - Count of instrument types or booking systems with zero contribution to a run (potential missing feed)
- **Suggested threshold:** 0 records in a run with an as-of date more than the permitted lag from the run date (0 days for trading book daily runs; 1 business day tolerance for banking book); run-over-run notional change outside ±X% (calibrated to portfolio volatility) requires documented explanation before output is released; production SLA breach triggers escalation per the agreed plan
- **Why cross-cutting:** No single CDE can detect a silent substitution of yesterday's records for today's, or an entire booking system feed that failed to arrive. This is a run-level completeness check that spans the as-of date (CDE-08), the amounts (CDE-03), the counterparty population (CDE-01), and the reconciliation framework (CDE-09).

---

## 4. Out of Scope

The following principles address obligations that a data catalog — with any CDE register or data quality monitoring programme — cannot satisfy. Being explicit about this is as important as the analysis above: a governance programme that claims its catalog meets Principles 8–11 has made a claim that does not survive scrutiny.

---

### Principles 8–11: Report content, clarity, frequency, and distribution

**What these principles require:**

- **Principle 8 (Comprehensiveness, ¶57–60):** Risk management reports must cover all significant risk areas, identify emerging concentrations, include limits and risk appetite context, and provide forward-looking forecasts and stress test results. The *content* of reports, not merely the data feeding them, must be comprehensive.
- **Principle 9 (Clarity and usefulness, ¶61–69):** Reports must be tailored to their recipients, balance quantitative and qualitative information appropriately by organisational level, and be periodically validated with recipients for relevance. ¶67 requires an inventory and classification of risk data items — this is addressable (see note below) — but the broader content obligations are not.
- **Principle 10 (Frequency, ¶70–71):** The board and senior management must set and periodically reassess production frequencies; frequencies must be increased during stress. Banks must *routinely test* their ability to produce accurate reports within established timeframes.
- **Principle 11 (Distribution, ¶72–73):** Reports must reach the right people rapidly while maintaining confidentiality. Timely dissemination must be periodically confirmed.

**Why a catalog cannot address these:**

A data catalog governs data elements: their definitions, lineage, quality, and stewardship. It has no visibility into, or control over:
- Whether a report sent to the board adequately covers all material risk areas (¶57) — this requires a governance review of report content against the risk taxonomy, performed by risk management and internal audit
- Whether the balance of qualitative versus quantitative information is appropriate for the recipient's level (¶62) — this is a report design and communication judgement
- Whether production frequencies are set correctly for the risk type and stress scenario (¶70) — this requires a documented frequency framework approved by senior management, with periodic stress testing of production pipelines; the catalog may record metadata about refresh frequency, but it cannot validate that the frequency is appropriate
- Whether reports reach the right recipients and confidentiality is maintained (¶72) — this requires an access control framework, a distribution list management process, and periodic confirmation to recipients (¶73); these are IT security, compliance, and change management matters

**What would be needed instead (not catalog deliverables):**
- A report inventory maintained by risk management, mapping each report to its required frequency, recipient list, and coverage of the risk taxonomy
- A report quality assurance process, independent of the report producers, that periodically confirms coverage against Principle 8 requirements
- A stress-and-crisis production readiness programme that tests the end-to-end pipeline from data extraction to report delivery within stated SLAs (Principle 10 testing requirement at ¶70)
- A distribution and access control framework with documented recipient confirmations (¶73)
- A board and senior management feedback loop confirming that reports meet their needs (¶65, ¶69)

---

### Partial exception: Principle 8 (¶57) and Principle 9 (¶67) also drive data elements

This requires explicit acknowledgment to avoid an apparent contradiction.

**Principle 8 (¶57)** names industry sector and country as required dimensions in credit risk reports. This is why CDE-07 (Industry / Sector) and CDE-06 (Geography) appear in the CDE register: those two elements must exist and be governed to make the required report content *possible*. But whether the report that uses those elements is actually produced, distributed, and reviewed by the board is a governance matter outside catalog scope.

**Principle 9 (¶67)** requires *"an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports."* This is the closest the regulation comes to mandating what a data catalog does. A well-governed catalog, populated with CDEs and linked to the report inventory, directly satisfies this requirement. However, the surrounding obligations of Principle 9 — report clarity, recipient tailoring, periodic confirmation (¶69) — remain outside catalog scope.

The split is therefore: the *data substrate* for Principles 8 and 9 is addressable through the CDE register; the *reporting and governance obligations* of those principles are not.

---

### Principle 1: Governance — partially out of scope

**Principle 1 (¶27–31)** drives several catalog deliverables: data ownership assignments (¶34), the data dictionary (¶37), and the identification of data critical to risk data aggregation (¶30). These are all catalog-governable.

However, ¶28–31 also require board and senior management approval of the framework, independent validation of compliance with the Principles, and board awareness of aggregation limitations. These require a governance structure — a data governance committee, an independent validation function, and board reporting — that the catalog supports with evidence but cannot substitute for. A catalog that records data owners and stewards documents the assignment of roles; it does not create the accountability itself.

---

### Principle 3 (¶38): Judgment-based manual interventions

¶38 acknowledges that some manual interventions involving professional judgment are appropriate. CDE-10 (Source System Identifier and Manual Override Flag) captures *whether* a manual intervention occurred, and XDQ-02 tracks the proportion and trend. But whether the *judgment itself* was appropriate — whether the override was correct — is an internal audit and model validation matter, not a data quality monitoring matter. The catalog flags; it does not adjudicate.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | 2 (¶33), 4 (¶41), 5 (¶46) | Uniqueness, Completeness, Validity, Timeliness |
| CDE-02 | Legal Entity Identifier (Booking Entity) | 3 | 2 (¶33), 4 (header) | Completeness, Validity, Consistency, Uniqueness |
| CDE-03 | Gross Exposure Amount | 3 | 3 (¶36a), 4 (¶41), 7 (¶53a) | Accuracy, Completeness, Validity, Timeliness |
| CDE-04 | Risk Type Classification | 3 | 8 (¶57), 4 (header), 1 (¶37) | Validity, Completeness, Consistency, Accuracy |
| CDE-05 | Business Line | 2 | 4 (header, ¶43), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | 2 | 4 (header), 6 (¶50), 8 (¶57) | Completeness, Validity, Consistency |
| CDE-07 | Industry / Sector Classification | 2 | 4 (header), 8 (¶57), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-08 | Position / As-Of Date | 3 | 5 (¶44), 6 (¶50), 7 (¶52) | Completeness, Validity, Timeliness, Consistency |
| CDE-09 | GL / Source System Reconciliation Key | 3 | 3 (¶36c), 7 (¶53a) | Completeness, Validity, Uniqueness, Accuracy |
| CDE-10 | Source System Identifier and Manual Override Flag | 2 | 3 (¶36b, ¶39), 2 (¶34) | Completeness, Validity, Accuracy, Timeliness |
| CDE-11 | Collateral Value and Type | 2 | 4 (¶41), 3 (¶36a), 5 (¶46a) | Timeliness, Validity, Accuracy, Completeness |

**Cross-cutting requirements summary:**

| XDQ | Name | Spans | Dimensions |
|---|---|---|---|
| XDQ-01 | Counterparty Resolution Across Systems | CDE-01, CDE-03, CDE-05, CDE-06, CDE-07 | Uniqueness, Consistency |
| XDQ-02 | Risk-to-Finance Reconciliation | CDE-03, CDE-09, CDE-02, CDE-08, CDE-10 | Accuracy, Completeness |
| XDQ-03 | Temporal Consistency of Aggregation Runs | CDE-08, CDE-03, CDE-01, CDE-09 | Timeliness, Completeness |