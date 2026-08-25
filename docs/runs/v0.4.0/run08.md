# BCBS 239 â Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable, aggregated risk data as a precondition for sound risk decisions.** The regulation requires that a bank can produce accurate, complete, and timely aggregated risk data â not just collect it â so that boards and senior management can act on it with confidence (Â¶35: *"risk data aggregation capabilities should ensure that risk management reports reflect the risks in a reliable way"*; Â¶52: *"board and senior management can rely with confidence on the aggregated information to make critical decisions about risk"*).

- **A single, governed data architecture with traceable lineage.** Banks must establish integrated data taxonomies, single identifiers, and unified naming conventions across the banking group, including metadata (Â¶33: *"integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*).

- **Reconciliation between risk data and authoritative sources.** Risk data must be reconciled back to accounting or other systems of record; the controls must be as robust as those applied to accounting data (Â¶36(a)â(c): *"Controls surrounding risk data should be as robust as those applicable to accounting dataâ¦ Risk data should be reconciled with bank's sources, including accounting data where appropriate"*).

- **Transparency over manual processes and end-user computing.** All aggregation processes â automated or manual â must be documented and explained. Manual workarounds must be identified, their criticality assessed, and plans made to reduce them (Â¶39: *"Documentation should include an explanation of the appropriateness of any manual workarounds, a description of their criticality to the accuracy of risk data aggregation"*).

- **Completeness across the full group, including off-balance-sheet.** All material risk exposures must be captured, by business line, legal entity, asset type, industry, region, and other relevant groupings, with exceptions identified and explained (Â¶41: *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Â¶43: *"any exceptions identified and explained"*).

- **A consistent data dictionary.** A shared dictionary of concepts ensures data is defined consistently across the organisation (Â¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"*).

**Who it applies to**

Globally systemically important banks (G-SIBs) from January 2016, with domestic systemically important banks (D-SIBs) expected to follow. The requirements apply at group level, spanning all legal entities, subsidiaries, business lines, and geographies within the banking group.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Identifier**

- **Definition:** The unique, persistent identifier that resolves a counterparty â borrower, issuer, derivatives counterpart, guarantor â to a single entity across all source systems, business lines, and legal entities within the banking group. This is distinct from any system-internal customer number; it is the enterprise-level key.
- **Why critical:** Without a single resolvable counterparty identifier, exposures held in different systems cannot be summed to produce a group-level credit or counterparty exposure. Aggregation across business lines and legal entities â the core obligation â is structurally impossible. This is precisely the joining key Â¶33 requires.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3** â *Without this element, the aggregate credit or counterparty exposure to a single counterparty across the banking group cannot be computed at all, because there is no key on which to join records from different systems.* A name-match or system-local ID is not a substitute; Â¶33 explicitly demands a single identifier. This is not a case of degraded accuracy â the aggregate literally does not exist.
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (Â¶41) â *"include all material risk exposures"*; Principle 5 (Â¶46(b)) â *"Counterparty credit risk exposures, including, for example, derivatives"*
- **Search terms:** counterparty ID, counterparty identifier, client ID, legal entity identifier, LEI, obligor ID, entity key, counterparty master, golden source counterparty, party identifier
- **Data quality requirements:**
  - *uniqueness* â Each real-world counterparty resolves to exactly one enterprise identifier; no two distinct counterparties share an identifier | Count of counterparty identifiers mapped to more than one distinct legal name or LEI | Target: 0 duplicates in the golden-source register
  - *completeness* â Every exposure record in every risk source system carries a non-null, populated counterparty identifier | Count of exposure records with null or unresolvable counterparty identifier, by source system | Target: <0.1% of records by exposure value
  - *consistency* â The counterparty identifier used in risk systems resolves to the same entity as in the accounting general ledger and the legal entity master | Count of identifiers present in risk systems but absent from the authoritative counterparty master | Target: 0 unmatched identifiers in production runs
  - *validity* â Where an LEI is used, it must be active and current in the GLEIF register at the position date | Count of LEI values that are lapsed, retired, or not found in GLEIF | Target: 0 lapsed LEIs on position records

---

**CDE-02 â Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier of the bank's own legal entity in which a risk position is booked â the subsidiary, branch, or parent entity within the banking group that is the legal owner of the exposure. Not the counterparty's entity; the bank's own booking entity.
- **Why critical:** Group-level risk consolidation requires summing or netting exposures across booking entities. Without a resolvable booking entity identifier, subsidiary-level reporting is impossible and the group aggregate cannot be decomposed back to individual legal entities â which supervisors require. Also required for identifying legal impediments to data sharing (Â¶30).
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 3** â *Without this element, the aggregate exposure for any individual subsidiary or branch within the banking group cannot be computed, nor can the group total be decomposed to subsidiary level for regulatory or management reporting â because there is no key identifying which legal entity holds each position.* Group consolidation, the foundational act of risk aggregation, fails without it.
- **Driven by:** Principle 2 (Â¶33) â *"integrated data taxonomies and architecture across the banking group, which includesâ¦ legal entities"*; Principle 4 (Â¶41) â *"capture and aggregate all material risk data across the banking group"*; Principle 1 (Â¶30) â *"limitations that prevent full risk data aggregation, in terms of coverage (eg risks not captured or subsidiaries not included)"*
- **Search terms:** legal entity, booking entity, entity code, subsidiary code, branch identifier, organisational entity, group entity, consolidation entity, LEI (own entity), booking unit
- **Data quality requirements:**
  - *completeness* â Every risk position record carries a non-null booking entity identifier | Count of position records with null booking entity field, by source system | Target: 0 null values in production
  - *validity* â Every booking entity code maps to an active entry in the group's legal entity hierarchy | Count of booking entity codes not present in the group entity master | Target: 0 unresolved codes
  - *consistency* â The booking entity hierarchy used in risk systems is identical to the entity hierarchy used in the group's consolidation accounting system | Count of entities present in risk systems but absent in the accounting consolidation perimeter, and vice versa | Target: 0 discrepancies at each reporting date

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary amount representing the bank's gross risk exposure to a counterparty or instrument before the application of netting, collateral, or credit risk mitigation. Expressed in the transaction currency and, where required for aggregation, in a reference currency.
- **Why critical:** This is the primary quantity being aggregated. Every risk figure â credit exposure, large exposure limit usage, concentration measure, capital calculation input â is built from sums or transformations of this amount. Without it, there is nothing to aggregate.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3** â *Without this element, no credit or counterparty exposure aggregate can be computed at all, because it is the quantity being summed.* The figure does not exist in degraded form; it is either present and correct or the aggregate is a fabrication.
- **Driven by:** Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (Â¶41) â *"include all material risk exposures, including those that are off-balance sheet"*; Principle 7 (Â¶52) â *"reports should be accurate and precise to ensure a bank's board and senior management can rely with confidence on the aggregated information"*
- **Search terms:** exposure amount, gross exposure, notional amount, nominal value, principal balance, drawn amount, outstanding balance, face value, gross position, mark-to-market exposure
- **Data quality requirements:**
  - *accuracy* â The exposure amount on each risk record agrees with the corresponding balance in the accounting system of record within defined materiality tolerance | Sum of absolute differences between risk-system exposure amounts and accounting balances, reconciled at portfolio level | Target: net difference <0.5% of total portfolio balance per reporting cycle
  - *completeness* â No exposure record carries a null or zero exposure amount unless the position is genuinely zero (e.g. fully matured) | Count of active position records with null or zero exposure amount where maturity date is in the future | Target: 0
  - *timeliness* â Exposure amounts reflect positions as of the stated position date; no stale carryforward from a prior date | Count of records where the last-updated timestamp predates the position date by more than the agreed cut-off window | Target: 0 stale records in the production dataset
  - *validity* â Exposure amounts are denominated in a recognised ISO 4217 currency code; no free-text or null currency fields | Count of records with missing or non-ISO currency denomination | Target: 0

---

**CDE-04 â Risk Type Classification**

- **Definition:** The categorical label that assigns each exposure or position to a primary risk type â credit risk, market risk, liquidity risk, operational risk, counterparty credit risk â according to the bank's risk taxonomy. This is the top-level partition of the risk inventory.
- **Why critical:** Risk reports are organised by risk type (Â¶57). Aggregation engines sum exposures within a risk type; capital calculations are performed separately per risk class. An incorrect or missing classification causes an exposure to be omitted from one risk aggregate and potentially double-counted in another, or excluded entirely.
- **Risk types:** Cross-cutting (applies across all risk types by definition)
- **Criticality: 2** â The gross aggregate of all exposures can be computed without this field; but without it, exposures cannot be partitioned into credit, market, liquidity, or operational buckets. The risk-type-specific aggregate (e.g. total credit risk exposure) is produced but cannot be verified as complete or correctly bounded â the figure is present but untrustworthy in each bucket.
- **Driven by:** Principle 7 (Â¶52, Â¶53) â *"Risk management reports should be accurate and precise"*; Principle 8 (Â¶57) â *"reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 4 (Â¶42) â *"each system should make clear the specific approach used to aggregate exposures for any given risk measure"*
- **Search terms:** risk type, risk category, risk class, risk classification, exposure category, risk flag, primary risk type, risk domain
- **Data quality requirements:**
  - *validity* â Every exposure record carries a risk type value drawn from the bank's approved risk taxonomy; no free-text or null entries | Count of records with null risk type or a value not present in the approved taxonomy code list | Target: 0
  - *completeness* â All positions in scope of the risk framework are classified; no unclassified residual pool | Count of position records with no risk type assignment | Target: 0
  - *consistency* â The risk type taxonomy applied in risk systems is identical to the taxonomy defined in the data dictionary required by Â¶37 | Count of risk type codes used in production systems not defined in the authoritative data dictionary | Target: 0

---

**CDE-05 â Business Line**

- **Definition:** The organisational or commercial segment to which a risk position is attributed â for example, retail banking, corporate banking, trading, wealth management â at the level of granularity required to produce business-line risk reports and to aggregate across the banking group.
- **Why critical:** Principle 4 explicitly requires data to be available by business line for aggregation. Principle 6 (Â¶50) requires the ability to produce exposures across all business lines for ad hoc queries. Without a consistent business line attribution, cross-business-line concentration reports cannot be produced and supervisory scenario responses cannot be fulfilled.
- **Risk types:** Credit, market, concentration, cross-cutting
- **Criticality: 2** â The total group exposure figure can be produced without this field; but without it, the business-line slice of any aggregate is unavailable, meaning Principle 4 completeness is violated for that dimension. The headline figure exists; its breakdown does not.
- **Driven by:** Principle 4 (Â¶41 and principle statement) â *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposuresâ¦ across all business lines and geographic areas"*
- **Search terms:** business line, business segment, line of business, division, product line, business unit, segment code, desk, portfolio segment
- **Data quality requirements:**
  - *completeness* â Every risk position carries a non-null business line attribution | Count of position records with null or blank business line field | Target: 0
  - *validity* â Business line codes used on position records map to entries in the approved organisational hierarchy | Count of codes not present in the current business line reference table | Target: 0
  - *consistency* â The business line hierarchy in risk systems is consistent with the hierarchy used in management accounting and performance reporting | Count of business line codes used in risk systems but absent from the management accounting hierarchy, and vice versa | Target: 0 unexplained discrepancies

---

**CDE-06 â Geography / Country of Risk**

- **Definition:** The country or jurisdiction associated with the primary risk of an exposure â typically the country of the counterparty's domicile or the country of the underlying asset, depending on the risk type and the bank's geographic risk allocation methodology. Distinct from the country of booking.
- **Why critical:** Principle 4 requires aggregation by region; Principle 6 (Â¶50) specifically names the ability to aggregate country credit exposures as an expected ad hoc capability. Country-of-risk is the primary field on which geographic concentration is measured. Without it, country-level stress scenarios mandated by Â¶50 cannot be run.
- **Risk types:** Credit, concentration, market, cross-cutting
- **Criticality: 2** â The aggregate exposure figure for the group is computable, but the country-of-risk slice is unavailable. The group total is produced but supervisors lose the ability to assess geographic concentration â a specific dimension Â¶50 names explicitly.
- **Driven by:** Principle 4 (principle statement) â *"Data should be available byâ¦ region and other groupings"*; Principle 6 (Â¶50) â *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*
- **Search terms:** country of risk, country code, risk country, domicile country, country of domicile, geography, region, country allocation, ISO country code, exposure country
- **Data quality requirements:**
  - *validity* â Every country-of-risk value is a valid ISO 3166-1 alpha-2 or alpha-3 code | Count of records with non-ISO, free-text, or null country values | Target: 0
  - *completeness* â Every exposure record carries a non-null country-of-risk attribution | Count of active exposure records with null country-of-risk | Target: 0
  - *consistency* â Country-of-risk attribution methodology is applied uniformly across business lines and source systems per the data dictionary | Count of records where the country-of-risk derivation rule differs from the methodology documented in the data dictionary | Target: 0 undocumented exceptions

---

**CDE-07 â Industry / Sector Classification**

- **Definition:** The economic sector or industry assigned to a counterparty or exposure â for example, using a standard scheme such as NACE, GICS, or SIC â that identifies the industry concentration of the bank's credit portfolio.
- **Why critical:** Principle 4 requires aggregation by industry; Principle 6 (Â¶50) specifically names industry credit exposures as a required ad hoc aggregation capability; Principle 8 (Â¶57) names industry sector as a required component of credit risk reports. Industry classification drives concentration monitoring, which is a named output of risk reporting.
- **Risk types:** Credit, concentration
- **Criticality: 2** â The total exposure aggregate exists without this field; but industry-level concentration â explicitly named in Â¶50 and Â¶57 â cannot be produced. The bank fails a named dimension of Principle 4 completeness and cannot respond to a defined category of supervisory ad hoc query.
- **Driven by:** Principle 4 (principle statement) â *"Data should be available byâ¦ industry, region and other groupings"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines"*; Principle 8 (Â¶57) â *"single name, country and industry sector for credit risk"*
- **Search terms:** industry sector, sector code, NACE code, SIC code, GICS, industry classification, counterparty sector, borrower industry, sector classification
- **Data quality requirements:**
  - *completeness* â Every counterparty record in the credit portfolio carries a non-null industry sector code | Count of counterparty or exposure records with null sector code, weighted by exposure amount | Target: <1% of total exposure value unclassified
  - *validity* â Sector codes used are drawn from a defined standard scheme (e.g. NACE, GICS) per the data dictionary | Count of sector codes not present in the reference classification scheme | Target: 0
  - *consistency* â The sector classification applied at counterparty level is inherited consistently by all exposure records linked to that counterparty | Count of exposure records where the sector code differs from the sector code on the linked counterparty master | Target: 0 unexplained discrepancies

---

**CDE-08 â Position / As-Of Date**

- **Definition:** The calendar date as of which a risk position, exposure balance, or risk measurement is stated. Every aggregate risk figure is implicitly a statement as of a specific date; this field makes that explicit and machine-readable.
- **Why critical:** Every aggregated risk figure is temporally bounded. Without the as-of date, it is impossible to know whether an aggregate reflects current positions or stale data. The as-of date is the temporal key that makes time-series comparison, trend analysis (Â¶58, Â¶60), and stress-scenario aggregation *as of a specified date* (Â¶50) possible. It is also required to evidence timeliness compliance under Principle 5.
- **Risk types:** Cross-cutting
- **Criticality: 3** â *Without this element, the aggregate figure for any risk measure cannot be stated as of a defined date, because the temporal reference is absent; a sum of positions with no date reference is not a valid risk aggregate â it cannot be placed in time, compared against a limit, or validated against a prior period.* Â¶50 explicitly requires aggregation *as of a specified date*; without a machine-readable position date on each record, that requirement cannot be fulfilled.
- **Driven by:** Principle 5 (Â¶44, Â¶45) â *"produce aggregate risk information on a timely basis"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (Â¶53) â reconciliation processes require a shared temporal reference
- **Search terms:** position date, as-of date, value date, reporting date, trade date, settlement date, snapshot date, reference date, run date, extraction date
- **Data quality requirements:**
  - *completeness* â Every risk position record carries a non-null as-of date | Count of records with null position date | Target: 0
  - *timeliness* â The as-of date on production records matches the intended reporting date; no records from prior days are included in the current snapshot without explicit carryforward logic | Count of records where the as-of date is earlier than the intended reporting date by more than the agreed cut-off tolerance | Target: 0 in production runs
  - *validity* â As-of date values are valid calendar dates (not default dates such as 01/01/1900, null substitutes, or future dates beyond T+1) | Count of records with as-of date outside the valid range for the reporting cycle | Target: 0
  - *consistency* â The same as-of date is applied uniformly across all source systems contributing to a single aggregation run | Count of source systems feeding a given aggregation run with a different as-of date than the canonical run date | Target: 0 mismatched systems per run

---

**CDE-09 â General Ledger / System-of-Record Reconciliation Key**

- **Definition:** The identifier â typically a transaction reference number, journal entry key, or account code â that links a risk data record to its corresponding entry in the bank's general ledger or authoritative system of record. This is the field that makes reconciliation between risk data and accounting data mechanically possible.
- **Why critical:** Â¶36(c) requires risk data to be reconciled with accounting data to ensure accuracy. Â¶36(a) requires controls on risk data to be as robust as those on accounting data. Without a reconciliation key on each risk record, the reconciliation required by Â¶36(c) cannot be performed systematically â it degrades to manual sampling or name-matching, which does not constitute the control Â¶36(a) demands. A risk figure whose accuracy cannot be evidenced through reconciliation is, for the purposes of BCBS 239, not a compliant figure (Â¶53(a): *"defined requirements and processes to reconcile reports to risk data"*).
- **Risk types:** Credit, market, liquidity, cross-cutting
- **Criticality: 3** â *Without this element, the accuracy of gross exposure amounts cannot be reconciled to the general ledger, because there is no key on which to join a risk record to its accounting counterpart; Â¶36(c) compliance cannot be evidenced, and under Â¶36(a), an unreconciled risk figure fails the same standard as an unaudited accounting entry.* An unverifiable figure is not a compliant one.
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 7 (Â¶53(a)) â *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** GL reference, general ledger key, journal entry ID, transaction reference, accounting reference, GL account code, source transaction ID, posting reference, reconciliation key, accounting identifier
- **Data quality requirements:**
  - *completeness* â Every risk record that corresponds to a balance-sheet or off-balance-sheet position carries a non-null GL reconciliation key | Count of risk records representing on- or off-balance-sheet positions with null reconciliation key | Target: 0 for balance-sheet items; documented exceptions permitted for off-balance-sheet with compensating controls
  - *validity* â Every reconciliation key present on a risk record resolves to an active entry in the general ledger or system of record | Count of reconciliation keys that do not match any current GL entry | Target: 0 unmatched keys at month-end
  - *accuracy* â The exposure amount on the risk record agrees with the balance on the matched GL entry within defined materiality tolerance | Sum of absolute differences between matched risk-record amounts and GL balances, at portfolio level | Target: net difference <0.5% of total portfolio as a trigger for investigation

---

**CDE-10 â Source System / Data Provenance Flag**

- **Definition:** The identifier of the originating source system from which a risk data record was extracted or loaded â for example, the name or code of the trade booking system, loan origination system, or collateral management system â together with a flag indicating whether the record was produced by an automated feed or entered or modified through a manual process or end-user computing application.
- **Why critical:** Â¶36(d) requires banks to strive toward a single authoritative source per risk type; Â¶36(b) requires effective mitigants for manual processes and end-user computing; Â¶39 requires documentation of all aggregation processes and explanation of manual workarounds. Without a source-system identifier and manual/EUC flag on each record, the bank cannot identify which records are subject to EUC risk, cannot demonstrate that authoritative-source policies are followed, and cannot produce the process documentation Â¶39 demands.
- **Risk types:** Cross-cutting
- **Criticality: 2** â Aggregate figures can be produced without this field; but the bank cannot identify whether any component of an aggregate originates from an uncontrolled EUC source, cannot demonstrate single-authoritative-source compliance, and cannot fulfil the process documentation obligation in Â¶39. The figure is produced but its provenance cannot be governed or evidenced.
- **Driven by:** Principle 3 (Â¶36(b)) â *"Where a bank relies on manual processes and desktop applicationsâ¦ it should have effective mitigants in place"*; Principle 3 (Â¶36(d)) â *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (Â¶39) â *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*
- **Search terms:** source system, source system code, system of origin, feeder system, data source, EUC flag, manual input flag, automated feed indicator, data origin, system identifier, pipeline name
- **Data quality requirements:**
  - *completeness* â Every risk record carries a non-null source system identifier and a non-null automated/manual flag | Count of records missing either the source system code or the manual/EUC flag | Target: 0
  - *validity* â Source system codes used on risk records are drawn from the approved source system register maintained in the data catalog | Count of source system codes not present in the authoritative source system register | Target: 0 unregistered source codes
  - *consistency* â The single-authoritative-source policy per risk type is reflected in production data: for each risk type, records sourced from designated authoritative systems should account for an agreed high proportion of total exposure value | Proportion of exposure value per risk type sourced from non-authoritative systems | Target: policy-defined threshold; any exception documented with compensating control

---

**CDE-11 â Net Exposure / Credit Risk Mitigation Amount**

- **Definition:** The monetary amount representing the risk exposure after the application of recognised credit risk mitigants â netting agreements, collateral, guarantees, credit derivatives â in accordance with the bank's risk mitigation framework. Where applicable, also the value of collateral held.
- **Why critical:** Â¶58 requires risk reports to provide information in the context of limits and risk appetite, and to identify concentrations. Limit utilisation and risk appetite monitoring are almost always expressed on a net, post-mitigation basis. Without the net exposure, limit-utilisation reports cannot be produced and concentration monitoring at the net level is impossible. Principle 4 (Â¶41) references off-balance-sheet items, many of which are mitigated positions.
- **Risk types:** Credit, counterparty, concentration
- **Criticality: 2** â The gross exposure aggregate (CDE-03) is computable without this field; but the net exposure figure used for limit monitoring and risk appetite reporting cannot be produced. The bank can report gross positions but cannot evidence limit compliance or net concentration, which Â¶58 requires. The figure is produced but is the wrong figure for limit-monitoring purposes.
- **Driven by:** Principle 8 (Â¶58) â *"provide information in the context of limits and risk appetite/tolerance"*; Principle 4 (Â¶41) â *"include all material risk exposures, including those that are off-balance sheet"*; Principle 5 (Â¶46(b)) â *"Counterparty credit risk exposures, including, for example, derivatives"*
- **Search terms:** net exposure, net credit exposure, post-mitigation exposure, collateral value, netting benefit, credit risk mitigation, CRM amount, haircut, eligible collateral, net position, EAD, exposure at default
- **Data quality requirements:**
  - *accuracy* â Net exposure amounts are derived from gross exposure amounts and recognised CRM inputs using documented calculation logic; the derivation is reproducible and auditable | Count of net exposure records where the derivation from gross exposure and CRM inputs cannot be traced step-by-step | Target: 0 unauditable derivations
  - *completeness* â Every counterparty exposure record that has an associated netting agreement or collateral arrangement carries a non-null net exposure figure | Count of exposure records with a linked netting or collateral agreement but a null net exposure amount | Target: 0
  - *timeliness* â Net exposure figures use collateral values that are current as of the position date; stale collateral valuations are flagged | Count of net exposure records where the collateral valuation date is more than the agreed staleness threshold prior to the position date | Target: 0 stale valuations in production

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Counterparty Resolution and Cross-System Deduplication**

- **Spans:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-07 (Industry/Sector), CDE-11 (Net Exposure)
- **Why cross-cutting:** The requirement is not that any single field is correctly populated â it is that the same real-world counterparty is resolved to the same enterprise identifier across every source system that contributes to a group-level aggregate. A counterparty may be represented under different local IDs in a loan origination system, a derivatives booking system, and a trade finance platform. Unless those representations are mapped to a single enterprise counterparty identifier, the aggregate credit exposure to that counterparty will be understated, and the industry and geographic concentrations associated with that counterparty will be fragmented. This is the cross-system joining problem that Â¶33 addresses by requiring single identifiers, and it cannot be detected or remediated by monitoring any individual CDE in isolation â it requires a cross-system entity resolution check.
- **Dimension:** *consistency*
- **Rule intent:** The same real-world counterparty must resolve to one and only one enterprise counterparty identifier across all source systems contributing positions to the group risk aggregate; no counterparty must appear under multiple distinct enterprise identifiers simultaneously.
- **Measurement:** Count of distinct real-world legal entities (identified by LEI or equivalent) that map to more than one enterprise counterparty identifier across the population of active source systems; and count of enterprise counterparty identifiers that are present in at least one source system but absent from the group counterparty master. Both counts are measured at each reporting cycle.
- **Suggested threshold:** 0 unresolved duplicates and 0 orphan identifiers in the production aggregate; any exceptions escalated before the risk report is signed off.

---

**XDQ-02 â Risk-to-Finance Reconciliation Completeness**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key), CDE-01 (Counterparty Identifier), CDE-08 (Position/As-Of Date)
- **Why cross-cutting:** Â¶36(c) requires risk data to be reconciled with accounting data; Â¶36(a) requires the controls to be as robust as those on accounting data. The reconciliation is not a property of any single CDE â it is a relationship between the entire risk data population (characterised by CDE-01, CDE-03, CDE-08) and the general ledger (joined via CDE-09). A reconciliation process that is 95% populated but has systematic gaps for a particular product type or legal entity will produce a materially inaccurate aggregate without any single-field quality rule detecting the problem. The cross-cutting requirement is that the population of risk records, at each position date, reconciles in aggregate to the corresponding GL balances, with documented explanations for any difference above materiality. This cannot be expressed as a rule on a single CDE; it requires a portfolio-level comparison.
- **Dimension:** *accuracy* and *completeness*
- **Rule intent:** The sum of gross exposure amounts on risk records, by legal entity and risk type, must agree with the corresponding balances in the general ledger at each reporting date; all differences above a defined materiality threshold must be identified, classified (timing, scope, methodology, data error), and escalated before the risk report is distributed.
- **Measurement:** Net difference between the total risk-system exposure balance and the corresponding GL balance, expressed in reference currency and as a percentage of total portfolio, by legal entity and risk type, at each reporting cycle; count of legal-entity/risk-type combinations where the reconciliation has not been completed by the report production deadline.
- **Suggested threshold:** Net difference <0.5% of total portfolio value as a trigger for investigation and documentation; 100% of legal-entity/risk-type combinations reconciled (even if with documented differences) before board-level risk reports are finalised.

---

## 4. Out of Scope

The following principles impose obligations that a CDE register and data quality monitoring framework, however well constructed, cannot satisfy. Cataloguing data elements and measuring their quality is a necessary but not sufficient condition for compliance with BCBS 239.

---

**Principle 1 â Governance (Â¶27â31): Board and senior management accountability**

Principle 1 requires the board and senior management to approve the risk data aggregation framework, review compliance, allocate resources, and be aware of limitations (Â¶28, Â¶30, Â¶31). A data catalog can surface evidence â an inventory of CDEs, documented limitations, DQ metric dashboards â but it cannot constitute, replace, or substitute for the governance structure itself. The required accountability belongs to people and committees; the catalog provides input to that governance, not governance itself. Board approval, the formation of a data governance committee, the allocation of budget, and the escalation of DQ exceptions to senior management are organisational acts that lie outside the scope of any data management tool.

---

**Principle 2 â Data Architecture and IT Infrastructure (Â¶32â35): Architectural design and business continuity**

Principle 2 drives CDE-01 (the single counterparty identifier, Â¶33) and the requirement for a data dictionary (Â¶37, treated here under Principle 3). However, the principle's infrastructure requirements â that risk data aggregation capabilities be considered in business continuity planning and subject to business impact analysis (Â¶32), that roles and responsibilities for data ownership be formally established (Â¶34), and that IT strategy incorporates risk data improvement plans (Â¶30) â are architectural, organisational, and governance obligations. A catalog can document lineage, ownership assignments, and system-of-record designations; it cannot design the IT architecture, enforce business continuity plans, or establish organisational accountability. The split is: the naming conventions and metadata requirements of Â¶33 drive CDEs; the infrastructure resilience and ownership governance obligations of Â¶32 and Â¶34 do not.

---

**Principle 3 â Accuracy and Integrity (Â¶36â40): Data dictionary and validation standards**

Principle 3 drives CDE-09 (reconciliation key), CDE-10 (source/provenance), and the reconciliation cross-cutting requirement (XDQ-02). However, Â¶37's requirement for a "dictionary of the concepts used, such that data is defined consistently across an organisation" is a data governance deliverable â the data dictionary â that a catalog can host but cannot generate autonomously. The bank must author the business definitions, approve them, and maintain version control. The catalog is the publication mechanism; the intellectual and governance work of defining and agreeing the concepts is organisational. Similarly, Â¶38's requirement for an appropriate balance between automated and manual systems, and Â¶39's requirement to document and justify all manual workarounds with remediation plans, are process and governance obligations that require human judgement and management accountability, not just metadata flags. The catalog's source/EUC flags (CDE-10) make the population of manual processes visible; the bank must then act on that visibility through governance channels the catalog does not provide.

---

**Principle 7 â Accuracy of Reports (Â¶52â56): Report validation and exception management**

Principle 7 drives the accuracy DQ requirements for CDEs 03 and 09 and the XDQ-02 reconciliation requirement. However, Â¶53(b) requires an inventory of validation rules applied to quantitative information in reports, including explanations of mathematical and logical relationships; Â¶53(c) requires integrated procedures for identifying and reporting data errors via exception reports; and Â¶54â56 require that banks establish and justify accuracy and materiality standards for approximations, models, and stress test outputs. These are report-production and model-governance obligations. A catalog can document that a validation rule exists and link it to a CDE; it cannot execute the validation in a reporting pipeline, generate exception reports, or govern model approximations. The data quality rules in this register describe what the catalog monitors at the data layer; the report-level validation inventory and exception management procedures are downstream systems and processes.

---

**Principle 8 â Comprehensiveness (Â¶57â60): Report content and forward-looking analysis**

Principle 8 partially drives data elements: Â¶57's named dimensions â country, industry sector â are reflected in CDE-06 and CDE-07; Â¶58's reference to limits and risk appetite monitoring supports CDE-11. This is stated explicitly to avoid the appearance of inconsistency. However, Principle 8's content obligations â that reports cover all significant risk areas, identify emerging concentrations, include forward-looking forecasts and stress test results (Â¶58, Â¶60), and cover regulatory and economic capital measures (Â¶59) â are report design and analytical obligations. They determine what a risk report must contain and what analytical capabilities must exist. No CDE register specifies or enforces report content; no DQ monitoring rule ensures that stress test results or capital projections are included in a board pack. These obligations fall to risk reporting teams, senior management, and the risk governance framework.

---

**Principle 9 â Clarity and Usefulness (Â¶61â69): Report design and recipient engagement**

Principle 9 is entirely out of scope for a data catalog. It governs how information is communicated â the balance between quantitative data and qualitative interpretation (Â¶62), the tailoring of reports to different recipient groups (Â¶63, Â¶66), and the periodic confirmation with recipients that reports remain relevant (Â¶69). Â¶67's requirement that a bank develop an inventory and classification of risk data items is the one element that a catalog could support â by hosting the CDE register â but the engagement with recipients, the assessment of report usefulness, and the governance of report design are human and organisational activities. No metadata attribute makes a report clear or useful.

---

**Principle 10 â Frequency (Â¶70â71): Report scheduling and stress-scenario turnaround**

Principle 10 requires that report frequency be set by the board and senior management, increased during stress, and routinely tested (Â¶70). Â¶71 names intraday position reporting as an expectation for critical risks in a crisis. These are report production scheduling obligations, dependent on the IT infrastructure's ability to produce aggregated figures rapidly (Principle 2) and on governance decisions about report cadence. The timeliness DQ rules in this register (particularly on CDE-08 and CDE-03) confirm that underlying data is current; they cannot ensure that the aggregation pipeline runs at the required frequency or that reports are produced within the required time window in a crisis scenario.

---

**Principle 11 â Distribution (Â¶72â74): Access control and confidentiality**

Principle 11 requires procedures for timely dissemination of reports to appropriate recipients while maintaining confidentiality (Â¶72, Â¶73). These are data access management, information security, and report distribution workflow obligations. A data catalog can document data sensitivity classifications and stewardship responsibilities, and in some implementations can enforce access control to catalog assets. However, the governance of who receives which risk report, the access control on the reporting platform, and the periodic confirmation that recipients are receiving reports in time (Â¶73) are report distribution and information security controls that sit outside the scope of a data catalog's CDE register.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | 2 (Â¶33), 4 (Â¶41), 5 (Â¶46b) | Uniqueness, completeness, consistency, validity |
| CDE-02 | Legal Entity (Booking Entity) | 3 | 2 (Â¶33), 4 (Â¶41), 1 (Â¶30) | Completeness, validity, consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3 (Â¶36aâc), 4 (Â¶41), 7 (Â¶52) | Accuracy, completeness, timeliness, validity |
| CDE-04 | Risk Type Classification | 2 | 7 (Â¶52â53), 8 (Â¶57), 4 (Â¶42) | Validity, completeness, consistency |
| CDE-05 | Business Line | 2 | 4 (Â¶41, principle), 6 (Â¶50) | Completeness, validity, consistency |
| CDE-06 | Geography / Country of Risk | 2 | 4 (principle), 6 (Â¶50), 8 (Â¶57) | Validity, completeness, consistency |
| CDE-07 | Industry / Sector Classification | 2 | 4 (principle), 6 (Â¶50), 8 (Â¶57) | Completeness, validity, consistency |
| CDE-08 | Position / As-Of Date | 3 | 5 (Â¶44â45), 6 (Â¶50), 7 (Â¶53) | Completeness, timeliness, validity, consistency |
| CDE-09 | GL / System-of-Record Reconciliation Key | 3 | 3 (Â¶36aâc), 7 (Â¶53a) | Completeness, validity, accuracy |
| CDE-10 | Source System / Data Provenance Flag | 2 | 3 (Â¶36b, Â¶36d, Â¶39) | Completeness, validity, consistency |
| CDE-11 | Net Exposure / Credit Risk Mitigation Amount | 2 | 8 (Â¶58), 4 (Â¶41), 5 (Â¶46b) | Accuracy, completeness, timeliness |

> **Criticality 3 elements (5):** CDE-01, CDE-02, CDE-03, CDE-08, CDE-09. These are the structural load-bearers: the joining keys that make aggregation possible (CDE-01, CDE-02), the quantity being aggregated (CDE-03), the temporal reference without which no aggregate is validly stated (CDE-08), and the reconciliation key without which accuracy cannot be evidenced (CDE-09).
>
> **Criticality 2 elements (6):** CDE-04, CDE-05, CDE-06, CDE-07, CDE-10, CDE-11. All produce valid aggregate figures when present; their absence or corruption degrades a specific slice, classification, or control â but does not prevent the headline aggregate from being computed.
>
> **Criticality 1:** No element in this register was assessed as a 1. Every element either makes aggregation structurally possible (3) or degrades a named regulatory dimension when wrong (2). Adding a 1 merely to populate the scale would lower the precision of the register.