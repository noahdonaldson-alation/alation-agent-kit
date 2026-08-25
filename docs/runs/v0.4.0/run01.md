# BCBS 239 â Data Catalog Governance Analysis

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a structural capability, not a reporting exercise.** The regulation requires banks to build data architecture and IT infrastructure that supports risk data aggregation in normal conditions *and* under stress, with automated processes minimising manual error. A bank that can only produce correct risk figures under normal conditions is non-compliant. (Principle 2, Â¶35: *"risk data aggregation capabilities should meet all Principles below simultaneously"*; Principle 5, Â¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis"*)

- **Accuracy traceable to source, not asserted.** Risk data must be reconciled to accounting and other authoritative sources. A risk figure that cannot be tied back to a system of record is not demonstrably accurate, regardless of whether it looks plausible. (Principle 3, Â¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."*)

- **Completeness across every material dimension of the group.** Aggregation must capture all material risk exposures â including off-balance-sheet â and must be sliceable by business line, legal entity, asset type, industry, and region. Gaps must be identified, measured, and explained, not silently tolerated. (Principle 4, Â¶41: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."* Â¶43: *"Supervisors expect banks to produce aggregated risk data that is complete and to measure and monitor the completeness of their risk data."*)

- **A single authoritative source and a consistent data dictionary.** The regulation explicitly requires banks to maintain a dictionary of data concepts defined consistently across the organisation, and to strive toward a single authoritative source per risk type. Ad hoc, fragmented, or contradictory definitions across business units are a structural deficiency. (Principle 3, Â¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation."* Â¶36(d): *"A bank should strive towards a single authoritative source for risk data per each type of risk."*)

- **Documented lineage for every aggregation process, automated or manual.** All risk data aggregation processes â including manual workarounds and end-user computing inputs â must be documented, their criticality assessed, and their limitations disclosed to senior management. (Principle 3, Â¶39: *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual."* Principle 1, Â¶30: *"Senior management should be fully aware of and understand the limitations that prevent full risk data aggregation."*)

- **Board-level accountability for the framework.** The board must approve the risk data aggregation framework, understand its limitations, and be aware of any gaps in coverage. This is not a technical matter delegated entirely to IT or risk functions. (Principle 1, Â¶28: *"A bank's board and senior management should review and approve the bank's group risk data aggregation and risk reporting framework."*)

**Who it applies to**

BCBS 239 is directed at **Global Systemically Important Banks (G-SIBs)** as a primary obligation (with implementation expected from D-SIBs on national supervisory timelines). In practice, many regulators have extended its spirit to a broader range of significant institutions. The unit of analysis is the **banking group** â consolidation across legal entities, subsidiaries, and geographies is explicitly required, not optional.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Identifier**

- **Definition:** The unique, persistent identifier that resolves a counterparty â borrower, derivative counterparty, issuer, guarantor â to a single entity record across all systems, business lines, and legal entities within the banking group. Distinct from account numbers or relationship codes, which may be system-local.
- **Why critical:** Without a single resolved counterparty key, exposures recorded in different systems cannot be summed to produce a group-wide counterparty exposure. Duplicate or mismatched counterparty records cause aggregated credit exposure to be either overstated (double-counting) or understated (missed linkage). This is the structural join key for all counterparty-level risk aggregation.
- **Risk types:** Credit, counterparty credit risk, concentration
- **Criticality: 3.** *Without a resolved counterparty identifier, the aggregate credit exposure to a single counterparty cannot be computed at all, because exposures recorded under different local identifiers cannot be linked across systems.*
- **Driven by:**
  - Principle 2 (Â¶33): *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts."*
  - Principle 4 (Â¶41): *"A bank's risk data aggregation capabilities should include all material risk exposures."*
  - Principle 5 (Â¶46(a)): *"The aggregated credit exposure to a large corporate borrower."* (named as a critical risk requiring rapid aggregation)
- **Search terms:** counterparty ID, global counterparty identifier, party ID, legal entity identifier, LEI, obligor ID, customer master, golden record, entity resolution
- **Data quality requirements:**
  - *Uniqueness* â Each real-world counterparty entity maps to exactly one active identifier in the authoritative counterparty master | Count of counterparty identifiers that resolve to more than one active master record, or master records that map to more than one identifier | Target: 0 duplicates
  - *Completeness* â Every exposure record carries a populated, non-null counterparty identifier | Count of exposure records with null or blank counterparty identifier field | Target: 0 nulls
  - *Validity* â Every counterparty identifier on an exposure record matches a record in the authoritative counterparty master | Count of exposure records whose counterparty identifier has no corresponding master record | Target: 0 unmatched
  - *Consistency* â The same counterparty identifier is used for the same entity across all contributing source systems | Count of cases where the same LEI or external reference maps to different internal identifiers across systems | Target: 0 cross-system splits for the same legal entity

---

**CDE-02 â Legal Entity / Booking Entity Identifier**

- **Definition:** The identifier of the bank's own legal entity in which a risk position or exposure is booked, drawn from a group-maintained legal entity hierarchy. Distinct from business line or cost centre; this is the regulated subsidiary or branch legal identity.
- **Why critical:** Group-level risk consolidation and subsidiary-level regulatory reporting both require that every exposure can be attributed to a specific booking entity. Without this, the bank cannot produce legal-entity-level risk views or consolidate correctly to group. It is also the primary dimension for jurisdictional aggregation.
- **Risk types:** Cross-cutting (credit, market, liquidity, operational â all risk types require entity attribution for consolidation)
- **Criticality: 3.** *Without a booking entity identifier, the aggregate risk exposure for any given legal entity or the consolidated group cannot be computed, because exposures cannot be attributed to a node in the group legal entity hierarchy.*
- **Driven by:**
  - Principle 2 (Â¶33): *"single identifiers and/or unified naming conventions for data including legal entities."*
  - Principle 4 (Â¶41, header): data must be available by *"legal entity"* as an explicit aggregation dimension.
  - Principle 1 (Â¶30): limitations in coverage including *"subsidiaries not included"* are named as a specific risk the board must understand.
- **Search terms:** legal entity ID, booking entity, entity code, subsidiary code, LEI, organisational unit, group entity hierarchy, consolidation entity
- **Data quality requirements:**
  - *Completeness* â Every exposure and position record carries a non-null booking entity identifier | Count of records with null booking entity | Target: 0 nulls
  - *Validity* â Every booking entity identifier resolves to a node in the current group legal entity hierarchy | Count of records with an entity code not present in the authoritative hierarchy | Target: 0 unmatched
  - *Consistency* â The same legal entity is represented by the same identifier across all source systems contributing to group consolidation | Count of legal entities with more than one active identifier across contributing systems | Target: 0

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary amount representing the bank's risk exposure before application of collateral, netting, or credit risk mitigation. Stated in the currency of the transaction. For credit risk, this is typically the outstanding principal or notional; for derivatives, the mark-to-market or replacement cost before netting.
- **Why critical:** This is the quantity being aggregated. Every risk report â capital adequacy, large exposure limits, concentration reporting â is ultimately built from summed exposure amounts. If this element is wrong, every downstream aggregate is wrong. It is also the primary reconciliation target against accounting balances.
- **Risk types:** Credit, counterparty credit risk, concentration, market
- **Criticality: 3.** *Without a gross exposure amount, the aggregate exposure figure X cannot be computed at all, because there is no quantity to sum across records.*
- **Driven by:**
  - Principle 3 (Â¶36(a)): *"Controls surrounding risk data should be as robust as those applicable to accounting data."*
  - Principle 3 (Â¶36(c)): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate."*
  - Principle 5 (Â¶46(a,b)): aggregated credit and counterparty exposures named as critical risk data.
- **Search terms:** exposure amount, outstanding balance, notional amount, gross exposure, drawn amount, mark-to-market, replacement cost, EAD (exposure at default), loan balance, gross receivable
- **Data quality requirements:**
  - *Accuracy* â Exposure amounts agree to the corresponding accounting balance or system-of-record figure within defined tolerance | Sum of absolute differences between risk exposure amounts and accounting balances at instrument level; tolerance defined per materiality threshold | Target: within agreed materiality band, with exceptions escalated
  - *Completeness* â Every exposure record carries a non-null, non-zero exposure amount (or a documented and approved reason for zero) | Count of exposure records with null exposure amount | Target: 0 nulls
  - *Validity* â Exposure amounts are positive for asset exposures and are denominated in an ISO 4217 currency code | Count of records with negative gross exposure or invalid currency denomination | Target: 0
  - *Timeliness* â Exposure amounts reflect the position as of the stated as-of date, updated within the required production cycle | Count of exposure records whose value date lags the stated as-of date beyond the permitted tolerance | Target: per production SLA

---

**CDE-04 â Risk Type Classification**

- **Definition:** The classification that assigns a risk record to a primary risk category â credit risk, market risk, liquidity risk, operational risk, counterparty credit risk â consistent with the bank's risk taxonomy as defined in its risk framework and regulatory submissions.
- **Why critical:** Risk type classification partitions the exposure universe for aggregation, capital calculation, and reporting. Reports that mix risk types, or that route an exposure to the wrong risk category, produce incorrect regulatory capital figures and mislead the board on the composition of the risk profile. It is the primary dimension by which Principle 8's requirement to cover all significant risk areas is operationalised.
- **Risk types:** Cross-cutting
- **Criticality: 2.** The gross aggregate across all exposures is still computable; however, the aggregate *by risk type* â which is the figure that appears in capital and risk reports â is wrong if classification is incorrect. Slices required by Principles 4 and 8 are distorted.
- **Driven by:**
  - Principle 4 (Â¶42): *"each system should make clear the specific approach used to aggregate exposures for any given risk measure."*
  - Principle 8 (Â¶57): *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*
  - Principle 3 (Â¶37): *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation."*
- **Search terms:** risk type, risk category, risk class, Basel risk category, risk classification, exposure type, asset class
- **Data quality requirements:**
  - *Validity* â Every risk record carries a risk type value drawn from the authoritative, board-approved risk taxonomy | Count of records with a risk type value not present in the approved taxonomy reference list | Target: 0 invalid values
  - *Completeness* â Every exposure record has a non-null risk type classification | Count of records with null risk type | Target: 0 nulls
  - *Consistency* â The same instrument type is classified to the same risk type across all source systems and business lines | Count of instrument types mapped to more than one risk type across contributing systems | Target: 0 cross-system inconsistencies for the same product

---

**CDE-05 â Business Line**

- **Definition:** The internal business division or segment to which a risk position is attributed, drawn from the bank's authoritative organisational taxonomy. Examples include retail banking, corporate banking, trading, private banking, treasury. Defined consistently at the level of granularity required for management and regulatory reporting.
- **Why critical:** Business line is one of the explicit aggregation dimensions named in Principle 4. Without it, the bank cannot slice its total risk exposure by business segment for either internal risk management or regulatory reporting. It is also required for stress scenario analysis (e.g., trading exposures by sector and region, Â¶46(c)).
- **Risk types:** Cross-cutting
- **Criticality: 2.** The total aggregate is still computable; the business-line slice required by Principle 4 and referenced in Â¶46(c) is unavailable or unreliable without this element.
- **Driven by:**
  - Principle 4 (header): *"Data should be available by business line, legal entity, asset type, industry, region and other groupings."*
  - Principle 5 (Â¶46(c)): *"Trading exposures, positions, operating limits, and market concentrations by sector and region data."*
- **Search terms:** business line, business unit, segment, division, desk, product line, LOB (line of business), profit centre, reporting unit
- **Data quality requirements:**
  - *Validity* â Every exposure record carries a business line code from the current approved organisational hierarchy | Count of records with a business line code absent from the current hierarchy | Target: 0 invalid values
  - *Completeness* â Every exposure record has a non-null business line assignment | Count of records with null business line | Target: 0 nulls
  - *Consistency* â Business line assignments are consistent for the same product or desk across front-office, risk, and finance systems | Count of instruments with different business line assignments across systems | Monitored and exceptions reviewed

---

**CDE-06 â Geography / Country of Risk**

- **Definition:** The country or jurisdiction assigned to a risk exposure, representing the primary country of risk (typically the country of the ultimate obligor or counterparty domicile, or the country of the underlying asset). Distinct from the booking entity's jurisdiction.
- **Why critical:** Geography is an explicit aggregation dimension under Principle 4 and is named directly in Principle 6's example of ad hoc aggregation capability (Â¶50: country credit exposures by specified date). Without a reliable country-of-risk field, the bank cannot produce country concentration reports or respond to supervisory queries about geographic exposure.
- **Risk types:** Credit, market, concentration
- **Criticality: 2.** The total aggregate is computable; geographic slices required by Principle 4 and the specific adaptability example in Â¶50 are unavailable or wrong without this element.
- **Driven by:**
  - Principle 4 (header): *"Data should be available byâ¦ region."*
  - Principle 6 (Â¶50): *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
  - Principle 5 (Â¶46(c)): *"market concentrations by sector and region."*
- **Search terms:** country of risk, country code, jurisdiction, region, geographic region, country of domicile, country of obligor, ISO country code
- **Data quality requirements:**
  - *Validity* â Every exposure record carries a country code drawn from the ISO 3166-1 standard or the bank's approved jurisdiction reference list | Count of records with a country code absent from the reference list | Target: 0 invalid values
  - *Completeness* â Every exposure record has a non-null country of risk | Count of records with null country field | Target: 0 nulls; country-unknown records to be flagged and quantified separately

---

**CDE-07 â Industry / Sector Classification**

- **Definition:** The industry or economic sector to which a counterparty or exposure is assigned, using a defined classification scheme (e.g., NACE, GICS, SIC, or a bank-internal taxonomy mapped to one of these). Applied at the counterparty or obligor level.
- **Why critical:** Industry sector is an explicit named dimension in Principle 4 and appears in Principle 8's description of required report content (Â¶57: *"single name, country and industry sector for credit risk"*). It is also the dimension in Principle 6's canonical adaptability example (Â¶50: *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*). Concentration risk by industry is a core supervisory expectation.
- **Risk types:** Credit, concentration
- **Criticality: 2.** The total aggregate is computable; the industry-sector slice required by Principles 4 and 8 and the Â¶50 adaptability example cannot be produced without reliable sector classification. Principle 8 also drives a reporting obligation (see Section 4 for the split).
- **Driven by:**
  - Principle 4 (header): *"Data should be available byâ¦ industry."*
  - Principle 8 (Â¶57): *"single name, country and industry sector for credit risk."*
  - Principle 6 (Â¶50): *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas."*
- **Search terms:** industry sector, sector code, NACE code, GICS sector, SIC code, industry classification, counterparty industry, obligor sector
- **Data quality requirements:**
  - *Validity* â Every counterparty record carries a sector code from the bank's approved classification scheme | Count of counterparty records with a sector code not present in the approved scheme | Target: 0 invalid values
  - *Completeness* â Every exposure record resolves to a counterparty with a non-null industry sector | Count of exposure records that join to a counterparty record with null sector | Target: to be defined against materiality; exceptions documented
  - *Consistency* â Industry classification is applied consistently at the counterparty level, not varied by product or system | Count of counterparties assigned different sector codes across systems | Target: 0

---

**CDE-08 â Position / As-Of Date**

- **Definition:** The date as of which a risk exposure or position is stated. This is the reference date for the risk snapshot â not the trade date, settlement date, or report production date. Every aggregated risk figure is implicitly or explicitly tied to an as-of date.
- **Why critical:** Every aggregated risk figure is stated *as of* a date. An exposure record with a wrong, missing, or ambiguous as-of date cannot be correctly included in or excluded from a time-specific aggregate. Under Principle 5, the bank must demonstrate timeliness and must be able to produce risk data as of a specified date on demand. Without a reliable as-of date, neither of these can be demonstrated or audited.
- **Risk types:** Cross-cutting
- **Criticality: 3.** *Without a reliable as-of date, the aggregate exposure figure as of date D cannot be computed, because records cannot be correctly attributed to the intended reporting period â and the figure cannot be reconciled to confirm it represents the right snapshot.*
- **Driven by:**
  - Principle 5 (Â¶44): *"A bank's risk data aggregation capabilities should ensure that it is able to produce aggregate risk information on a timely basis."*
  - Principle 6 (Â¶50): *"aggregate risk data quickly on country credit exposures as of a specified date."* (Repeated emphasis on specified-date aggregation)
  - Principle 7 (Â¶53(a)): *"Defined requirements and processes to reconcile reports to risk data."* (Reconciliation is date-bound)
- **Search terms:** as-of date, position date, value date, reference date, business date, reporting date, snap date, trade date (distinguish from as-of), data extraction date
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a non-null as-of date | Count of records with null position date | Target: 0 nulls
  - *Validity* â As-of dates are valid calendar dates and fall within the permissible range for the reporting cycle | Count of records with dates outside valid range or non-parseable date values | Target: 0
  - *Timeliness* â Exposure records for a given as-of date are available within the agreed production window | Elapsed time from business close of as-of date to availability of complete exposure dataset | Target: per production SLA; stress/crisis SLA separately defined per Â¶45

---

**CDE-09 â Reconciliation Key (Risk-to-Finance Link)**

- **Definition:** The identifier â typically a trade reference, instrument identifier, or account number â that ties a risk data record to its corresponding entry in the general ledger or the authoritative system of record (e.g., core banking, trade processing). This is not a risk classification; it is the structural link that makes verification possible.
- **Why critical:** Principle 3 Â¶36(c) requires that risk data be reconciled to accounting sources. This reconciliation cannot be performed without a shared identifier that is present in both the risk data layer and the finance/accounting layer. Without it, reconciliation is either impossible or requires fragile, assumption-dependent matching â which is itself a control weakness the regulation targets. An unverifiable risk figure is not a compliant one, regardless of how plausible it looks.
- **Risk types:** Cross-cutting (the reconciliation obligation applies across credit, market, and liquidity risk data)
- **Criticality: 3.** *Without the reconciliation key, the accuracy of the aggregate exposure figure cannot be evidenced against the system of record, because there is no structural link between the risk record and the accounting entry â making the figure unverifiable under Â¶36(c), which is an equivalent failure to the figure being wrong.*
- **Driven by:**
  - Principle 3 (Â¶36(c)): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."*
  - Principle 7 (Â¶53(a)): *"Defined requirements and processes to reconcile reports to risk data."*
  - Principle 3 (Â¶36(d)): *"A bank should strive towards a single authoritative source for risk data per each type of risk."*
- **Search terms:** trade ID, instrument ID, deal reference, account number, GL account, transaction reference, system key, source system ID, primary key, booking reference, CUSIP, ISIN (where applicable as the system-of-record identifier)
- **Data quality requirements:**
  - *Completeness* â Every risk data record carries a non-null reconciliation key | Count of risk records with null reconciliation key | Target: 0 nulls
  - *Validity* â Every reconciliation key on a risk record matches a record in the identified system of record or general ledger | Count of risk records whose reconciliation key has no match in the system of record | Target: 0 unmatched; exceptions escalated
  - *Uniqueness* â Each reconciliation key maps to exactly one instrument or account in the system of record (or the many-to-one relationship is explicitly documented) | Count of reconciliation keys that return more than one unrelated record in the system of record | Target: 0 ambiguous mappings
  - *Accuracy* â Exposure amount on the risk record agrees to the balance on the matched system-of-record entry within defined materiality | Sum of absolute differences at matched record level; exceptions reported | Target: within agreed materiality tolerance

---

**CDE-10 â Source System / Provenance Flag**

- **Definition:** The identifier of the system or process from which a risk data record originated, combined with a flag indicating whether the input was automated (system-generated) or manual (including end-user computing tools such as spreadsheets or local databases). This is a metadata attribute carried on each record, not a separate data domain.
- **Why critical:** Principle 3 Â¶36(b) and Â¶39 require that manual processes and end-user computing inputs be identified, documented, and subject to specific controls. Principle 3 Â¶36(d) requires a single authoritative source. Without source system and manual-input provenance captured at the record level, it is impossible to: (a) apply differentiated controls to EUC versus system-generated data; (b) identify which aggregates depend on manual inputs; (c) respond to supervisory requests to quantify reliance on manual processes; or (d) support lineage tracing for any individual risk figure.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Aggregates are still computable; however, the bank cannot demonstrate compliance with Â¶36(b), Â¶39, or Â¶36(d), cannot quantify manual-process dependency, and cannot support data lineage â all of which are direct regulatory requirements. The integrity of the aggregate cannot be fully assessed without this element.
- **Driven by:**
  - Principle 3 (Â¶36(b)): *"Where a bank relies on manual processes and desktop applicationsâ¦ it should have effective mitigants in placeâ¦ and other effective controls that are consistently applied."*
  - Principle 3 (Â¶39): *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual."*
  - Principle 3 (Â¶36(d)): *"A bank should strive towards a single authoritative source for risk data per each type of risk."*
- **Search terms:** source system, system of origin, data source, feed ID, upstream system, manual override flag, EUC flag, end-user computing indicator, data lineage, provenance, manual adjustment, spreadsheet input
- **Data quality requirements:**
  - *Completeness* â Every risk data record carries a non-null source system identifier | Count of records with null source system | Target: 0 nulls
  - *Validity* â Every source system identifier references a registered, documented system in the bank's authoritative system inventory | Count of records with a source system identifier not in the registered system inventory | Target: 0; unknown sources investigated
  - *Completeness (manual flag)* â Every record originating from a manual process or EUC tool carries a populated manual/EUC indicator | Count of records from known EUC sources that lack the manual indicator | Target: 0; requires cross-reference against source system registry
  - *Accuracy* â Manual-input records are subject to the same validation and reconciliation checks as automated records | Count of manual-flagged records excluded from reconciliation or accuracy monitoring | Target: 0 exclusions

---

**CDE-11 â Net Exposure / Collateral-Adjusted Exposure**

- **Definition:** The exposure amount after application of recognised credit risk mitigation â specifically, collateral values and netting agreements â used as the basis for regulatory capital calculations and large exposure limit monitoring. Distinct from gross exposure (CDE-03); the relationship between the two must be traceable.
- **Why critical:** Regulatory capital figures and limit utilisation are calculated against net, not gross, exposure. Errors in collateral valuation or netting recognition directly distort capital adequacy reporting. Principle 8 (Â¶58) requires reports to identify risk concentrations in the context of limits â which requires net exposure. The element is included because its failure would produce a materially wrong capital figure, not merely less complete information.
- **Risk types:** Credit, counterparty credit risk, concentration
- **Criticality: 2.** Gross aggregate (CDE-03) is still computable; the regulatory capital figure and limit utilisation â which are the figures reported to the board and submitted to supervisors â are wrong if net exposure is misstated. This is a degradation of a specific, important slice rather than structural invalidity of all aggregation.
- **Driven by:**
  - Principle 4 (Â¶41): *"A bank's risk data aggregation capabilities should include all material risk exposures."*
  - Principle 8 (Â¶57): *"Risk management reports should also cover risk-related measures (eg regulatory and economic capital)."*
  - Principle 8 (Â¶58): *"Reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance."*
- **Search terms:** net exposure, collateral-adjusted exposure, post-netting exposure, EAD (net), collateral value, haircut, netting set, credit risk mitigation, CVA, LGD input exposure
- **Data quality requirements:**
  - *Accuracy* â Net exposure equals gross exposure minus recognised collateral and netting, within defined tolerance; the calculation is independently replicable from inputs | Difference between reported net exposure and independently computed net exposure from gross exposure and collateral records | Target: within agreed materiality
  - *Completeness* â Every exposure for which collateral or netting exists has the mitigant recorded and associated | Count of exposures with a known collateral agreement that carry null collateral value | Target: 0 nulls for material exposures
  - *Timeliness* â Collateral values are refreshed at the frequency required by the bank's collateral management policy | Count of collateral records whose valuation date lags the position date beyond the permitted staleness threshold | Target: per policy; daily for material counterparties
  - *Validity* â Netting agreements are only recognised where legally enforceable documentation exists in the bank's legal inventory | Count of netting sets applied in exposure calculation for which no executed legal agreement is recorded | Target: 0

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 â Group-Wide Counterparty Resolution (Single View of Counterparty)**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-02 (Legal Entity), CDE-07 (Industry/Sector), CDE-11 (Net Exposure)
- **What this is:** The requirement that exposures recorded under different local counterparty identifiers â across trading, lending, treasury, and derivatives systems â are unified into a single group-wide view before aggregation. This is not a property of any individual record; it is a property of the reconciliation process between the local identifiers and the group counterparty master.
- **Why it cannot be expressed as a single-element DQ rule:** A trading system may have a clean, internally unique counterparty ID. A lending system may have a clean, internally unique counterparty ID. Neither system's ID is wrong in isolation. The failure occurs when the two IDs refer to the same real-world entity and are never linked â meaning the group-level aggregate silently double-counts or misses the exposure. This is only visible at the group level.
- **Regulatory basis:** Principle 2 (Â¶33): *"single identifiers and/or unified naming conventions for data includingâ¦ counterparties."* Principle 5 (Â¶46(a)): *"The aggregated credit exposure to a large corporate borrower."*
- **Dimension:** Consistency
- **Rule intent:** The group counterparty master must contain a complete, current mapping from every local counterparty identifier across all source systems to a single canonical group identifier. No local identifier should be unmapped.
- **Measurement:** (a) Count of distinct local counterparty identifiers across all contributing systems that have no mapping to a group-level canonical identifier. (b) Count of group-level counterparty records that aggregate exposures from only one source system, for counterparties known to have positions across multiple systems. (c) Proportion of total group exposure amount attributable to locally-identified-only (unmapped) counterparties.
- **Suggested threshold:** (a) Target 0 unmapped identifiers for counterparties above a defined materiality threshold; (b) exceptions below materiality documented and quantified; (c) total exposure on unmapped counterparties below defined materiality ceiling

---

**XDQ-02 â Risk-to-Finance Reconciliation Coverage and Completeness**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-08 (As-Of Date), CDE-09 (Reconciliation Key), CDE-10 (Source System / Provenance)
- **What this is:** The requirement that the aggregate risk exposure figure, as stated as of a given date, can be reconciled in full to the corresponding accounting or general ledger balance â and that this reconciliation is documented, its coverage is measured, and all exceptions are explained. This is a process-level control, not a field-level check. It requires that the join between risk records (CDE-09) and finance records is performed, that the population of risk records is confirmed complete (CDE-03, CDE-08), and that any manual adjustments (CDE-10) are included in scope.
- **Why it cannot be expressed as a single-element DQ rule:** Reconciliation is a bilateral comparison between two populations â the risk dataset and the accounting dataset. Validating CDE-09 (reconciliation key) tells you whether the key is present and matched; it does not tell you whether the *population* is complete (i.e., whether risk records exist for every GL position), whether the *amounts agree* in aggregate, or whether manual adjustments have been correctly captured. These are properties of the comparison, not of either dataset individually.
- **Regulatory basis:** Principle 3 (Â¶36(c)): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."* Principle 7 (Â¶53(a)): *"Defined requirements and processes to reconcile reports to risk data."*
- **Dimension:** Accuracy, Completeness
- **Rule intent:** For each risk type and as-of date, the total exposure in the risk dataset should agree to the corresponding accounting balance within defined materiality tolerance. All positions in the general ledger that meet the criteria for risk capture should have a corresponding risk record. All differences should be identified, categorised (timing, methodology, scope), and reported through the exception process.
- **Measurement:** (a) Absolute and percentage difference between the sum of risk exposure amounts and the corresponding accounting balance, by risk type and as-of date. (b) Count and value of GL positions with no corresponding risk record (population gap). (c) Count and value of risk records with no corresponding GL entry (orphan risk records). (d) Count of unresolved reconciling items older than the defined resolution SLA.
- **Suggested threshold:** Net difference within agreed materiality tolerance (defined by analogy to accounting materiality, per Â¶56); population gap and orphan count at 0 for material exposures; all reconciling items assigned an explanation within the production cycle

---

## 4. Out of Scope

The following principles â or aspects of principles â address requirements that no CDE register, no data quality monitoring regime, and no data catalog configuration can satisfy. Stating this plainly is not a limitation of the analysis; it is what makes the register above trustworthy.

---

**Principle 7 (Â¶52â56) â Report accuracy and reconciliation obligations: partially in scope, partially out of scope**

The data-layer obligations of Principle 7 â that risk data is reconcilable to sources (Â¶36(c) by cross-reference, Â¶53(a)) â are addressed by CDE-09 and XDQ-02 above. What Principle 7 requires *beyond* the data layer is outside catalog scope: the bank must establish defined accuracy and precision *requirements* for risk reports (Â¶55), determine what constitutes reporting materiality (Â¶56), maintain an inventory of validation rules applied to quantitative information (Â¶53(b)), and operate integrated exception procedures for reporting errors (Â¶53(c)). These are governance, process, and reporting-system obligations. A data catalog can document the reconciliation key and flag mismatches; it cannot define what constitutes an acceptable mismatch for a regulatory capital report, and it cannot operate the exception escalation workflow.

---

**Principle 8 (Â¶57â60) â Report comprehensiveness: partially in scope, partially out of scope**

Principle 8 names industry sector (Â¶57) and business line as required report dimensions â these drive CDE-05, CDE-06, and CDE-07 above, which is why those elements appear in the register. That is the in-scope portion. The out-of-scope portion is substantial: Principle 8 requires that risk reports cover all material risk areas with depth and scope appropriate to the bank's complexity (Â¶57), include forward-looking forecasts and stress test results (Â¶60), identify emerging concentrations and present them in the context of limits and risk appetite (Â¶58), and cover regulatory and economic capital (Â¶57, Â¶59). None of these are data element or data quality questions. They are report design, content, and coverage obligations. A catalog can confirm that industry sector is populated; it cannot confirm that the report adequately covers all material risk concentrations or that stress test scenarios are appropriate. Principle 8 also drives a CDE and remains largely out of scope â this is not a contradiction, it is a split: the dimension fields are a necessary but not sufficient condition for compliance.

---

**Principle 9 (Â¶61â69) â Clarity and usefulness: out of scope**

Principle 9 requires that risk reports be clear, concise, and meaningful to their intended recipients (Â¶61â62); that reporting policies recognise the differing information needs of the board, senior management, and risk committees (Â¶63); that the board actively confirm its reporting requirements are being met (Â¶64â65); and that banks periodically confirm with recipients that the information is relevant and appropriate (Â¶69). These are board governance, stakeholder engagement, and report design obligations. A data catalog documents what data exists and whether it is of adequate quality; it has no mechanism to assess whether a risk report is comprehensible to a non-executive director, whether the board is asking the right questions, or whether the balance of quantitative and qualitative content is appropriate. Principle 9 also mentions that banks should develop an inventory and classification of risk data items (Â¶67) â this is the closest Principle 9 comes to catalog scope, and it supports the case for a CDE register, but it does not render the rest of Principle 9 addressable by catalog governance.

---

**Principle 10 (Â¶70â71) â Frequency: out of scope**

Principle 10 requires that report frequency be set by the board and senior management, reflect the nature and volatility of each risk type, be increased during stress, and be routinely tested (Â¶70â71). Frequency is a scheduling, governance, and infrastructure capacity question. A catalog can record that a dataset has a defined refresh SLA (CDE-08's timeliness dimension gets close), but it cannot govern the board's decision on report cadence, manage stress-period escalation of reporting frequency, or test whether the bank can actually produce accurate reports within crisis timeframes. The distinction is between recording a timeliness expectation on a data element versus governing the end-to-end report production and distribution cycle.

---

**Principle 11 (Â¶72â74) â Distribution: out of scope**

Principle 11 requires that procedures be in place for rapid dissemination of reports to appropriate recipients while maintaining confidentiality (Â¶72), and that the bank periodically confirm recipients receive timely reports (Â¶73). This is an information security, access control, and report distribution governance obligation. A data catalog can carry metadata about data sensitivity and assist in identifying what should be restricted â but it cannot manage report distribution workflows, enforce recipient access controls in report delivery systems, or provide the periodic confirmation process required by Â¶73.

---

**Principle 1 (Â¶27â31) and Principle 2 (Â¶32â35) â Governance and architecture: substantially out of scope**

These principles drive the entire framework â the requirement to maintain a data dictionary (Â¶37), assign data ownership (Â¶34), document aggregation processes (Â¶39), and establish integrated data taxonomies (Â¶33) â and they provide the strongest justification for building and governing a data catalog at all. However, the catalog is an instrument of these principles, not a substitute for them. What the catalog cannot deliver: board and senior management approval of the framework (Â¶28); allocation of financial and human resources (Â¶30); business continuity planning for risk data systems (Â¶32); independent validation of the entire risk data aggregation and reporting process (Â¶29(a)); due diligence on acquired entities' data capabilities (Â¶29(b)); or senior management awareness of legal and jurisdictional impediments to data sharing (Â¶30). These require governance decisions, organisational authority, and assurance processes that operate above and around the catalog.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | **3** | 2 (Â¶33), 4 (Â¶41), 5 (Â¶46a) | Uniqueness, Completeness, Validity, Consistency |
| CDE-02 | Legal Entity / Booking Entity Identifier | **3** | 2 (Â¶33), 4 (header), 1 (Â¶30) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | **3** | 3 (Â¶36a, Â¶36c), 5 (Â¶46a,b) | Accuracy, Completeness, Validity, Timeliness |
| CDE-04 | Risk Type Classification | **2** | 4 (Â¶42), 8 (Â¶57), 3 (Â¶37) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | **2** | 4 (header), 5 (Â¶46c) | Validity, Completeness, Consistency |
| CDE-06 | Geography / Country of Risk | **2** | 4 (header), 6 (Â¶50), 5 (Â¶46c) | Validity, Completeness |
| CDE-07 | Industry / Sector Classification | **2** | 4 (header), 8 (Â¶57), 6 (Â¶50) | Validity, Completeness, Consistency |
| CDE-08 | Position / As-Of Date | **3** | 5 (Â¶44), 6 (Â¶50), 7 (Â¶53a) | Completeness, Validity, Timeliness |
| CDE-09 | Reconciliation Key (Risk-to-Finance Link) | **3** | 3 (Â¶36c), 7 (Â¶53a), 3 (Â¶36d) | Completeness, Validity, Uniqueness, Accuracy |
| CDE-10 | Source System / Provenance Flag | **2** | 3 (Â¶36b), 3 (Â¶39), 3 (Â¶36d) | Completeness, Validity, Accuracy |
| CDE-11 | Net Exposure / Collateral-Adjusted Exposure | **2** | 4 (Â¶41), 8 (Â¶57, Â¶58) | Accuracy, Completeness, Timeliness, Validity |

**Criticality 3 elements: CDE-01, CDE-02, CDE-03, CDE-08, CDE-09 â five elements.** These are the elements without which either a risk aggregate cannot be computed at all, or cannot be reconciled and therefore cannot be evidenced as compliant. All others are rated 2: their absence degrades specific slices, controls, or the bank's ability to demonstrate integrity, but does not structurally prevent all aggregation.