# BCBS 239 â Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation at group level, including under stress.** Banks must aggregate all material risk exposures across legal entities, business lines, and geographies, and do so rapidly when conditions deteriorate. A figure that can only be produced under normal conditions is non-compliant. (Principle 4, Â¶41; Principle 5, Â¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*)

- **Accuracy with evidenced reconciliation.** Risk data must be reconciled to accounting and other source systems. An unverified figure is not a compliant one; the regulation treats unreconciled accuracy as equivalent to inaccuracy. (Principle 3, Â¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."*)

- **A single authoritative source per risk type, with documented provenance.** Manual processes and end-user computing are permitted but must be identified, documented, and controlled. Proliferation of untracked copies of risk data is the structural failure the regulation targets. (Principle 3, Â¶36(d): *"A bank should strive towards a single authoritative source for risk data per each type of risk."*; Â¶39.)

- **Integrated data taxonomy and consistent definitions across the group.** A shared dictionary of concepts, unified naming conventions, and single identifiers for counterparties, legal entities, and accounts are preconditions for any aggregation. Without them, aggregates across systems cannot be trusted. (Principle 2, Â¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata)."*; Principle 3, Â¶37.)

- **Governance with board-level accountability.** The board approves the aggregation and reporting framework, must be told about coverage gaps, and is responsible for its own reporting requirements. Data quality risk management is an explicit board and senior management obligation, not a back-office function. (Principle 1, Â¶27â28, Â¶31.)

- **Adaptability for ad hoc and regulatory queries.** The aggregation infrastructure must be capable of re-slicing data on demand â by country, industry, business line â as of any requested date. This requires that the slicing dimensions are consistently populated, not merely present. (Principle 6, Â¶50: *"A bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries, as well as industry credit exposuresâ¦ across all business lines and geographic areas."*)

**Who it applies to**

BCBS 239 applies to **global systemically important banks (G-SIBs)** as its primary population, with national supervisors expected to extend it to domestically systemically important banks (D-SIBs). The regulation addresses the **banking group in its entirety**, including subsidiaries, legal entities in multiple jurisdictions, and both on- and off-balance-sheet exposures. It is not limited to a single risk type; it applies to credit, market, liquidity, operational, and counterparty risk, and any concentration arising from them.

---

## 2. Critical Data Element Candidates

---

**CDE-01 â Counterparty Identifier**

- **Definition:** The unique, persistent identifier that represents a single counterparty (obligor, issuer, trading counterparty, guarantor) across all source systems. It resolves one real-world legal entity to one key, regardless of how many local system records represent it.
- **Why critical:** Without a single resolvable counterparty identifier, exposures held in different systems â loans in a core banking platform, derivatives in a trading system, bonds in a custody system â cannot be summed to produce group-wide credit exposure to that counterparty. The aggregate cannot be computed at all, not merely degraded.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality:** **3.** *Without this element, the aggregate figure "total group exposure to counterparty X" cannot be computed at all, because records from different source systems have no common key on which to join and sum.*
- **Driven by:** Principle 2 (Â¶33) â *"use of single identifiers and/or unified naming conventions for data includingâ¦ counterparties"*; Principle 4 (Â¶41) â capture of all material risk exposures across the banking group; Principle 5 (Â¶46(b)) â counterparty credit risk exposures as a critical risk class.
- **Search terms:** counterparty ID, obligor ID, legal entity identifier, LEI, counterparty reference, party key, client ID, global counterparty code, entity reference number
- **Data quality requirements:**
  - *Uniqueness* â Each distinct real-world counterparty resolves to exactly one identifier in the authoritative reference system; no two identifiers refer to the same legal entity | Count of counterparty identifiers mapped to more than one canonical entity record | Target: 0
  - *Completeness* â Every exposure record carries a populated, non-null counterparty identifier | Count of exposure records with null or unresolvable counterparty identifier as a proportion of all exposure records | Target: <0.1%
  - *Validity* â Each counterparty identifier on an exposure record exists and is active in the counterparty reference system | Count of exposure records whose counterparty identifier does not match any record in the authoritative counterparty register | Target: 0

---

**CDE-02 â Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier of the bank's own legal entity in which a position or exposure is booked â i.e., the subsidiary, branch, or holding company that owns the risk. Distinct from the counterparty identifier (CDE-01), which identifies the external party.
- **Why critical:** Group-wide consolidation and subsidiary-level reporting both depend on being able to attribute every exposure to a booking entity and then aggregate or filter by it. A missing or misassigned booking entity means the group aggregate either double-counts or omits that exposure; subsidiary reporting is impossible.
- **Risk types:** Cross-cutting (all risk types require legal entity attribution for group reporting)
- **Criticality:** **3.** *Without this element, the aggregate figure "group-level total credit exposure" cannot be correctly computed because exposures cannot be attributed to entities, preventing both consolidation and the elimination of intragroup double-counts.*
- **Driven by:** Principle 2 (Â¶33) â *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (Â¶41, Â¶43) â aggregation across the banking group; Principle 8 (Â¶57) â reports covering all significant risk areas across the organisation.
- **Search terms:** legal entity ID, booking entity, entity code, reporting entity, subsidiary code, branch code, LEI (own entity), organisational unit identifier, consolidation entity
- **Data quality requirements:**
  - *Completeness* â Every exposure and position record carries a populated booking-entity identifier | Count of records with null booking entity as a proportion of all risk records | Target: <0.1%
  - *Validity* â Each booking-entity identifier exists in the authoritative legal entity hierarchy used for group consolidation | Count of exposure records referencing a booking entity not present in the group legal entity register | Target: 0
  - *Consistency* â The same exposure record references the same booking entity in the risk system and in the general ledger | Count of exposure records where the booking entity in the risk system differs from the booking entity in the GL for the same transaction key | Target: 0

---

**CDE-03 â Gross Exposure Amount**

- **Definition:** The monetary value of a risk exposure before credit risk mitigants (collateral, guarantees, netting) are applied â the raw quantity being aggregated into risk figures. Denominated in a stated currency.
- **Why critical:** This is the quantity that all exposure aggregations sum. If the exposure amount is wrong or missing, every aggregate built from it â total credit exposure, concentration measure, capital calculation â is arithmetically invalid. No amount, no aggregate.
- **Risk types:** Credit, counterparty, market, concentration
- **Criticality:** **3.** *Without this element, the aggregate figure "total group credit exposure to sector Y" cannot be computed at all, because there is no monetary quantity to sum across records.*
- **Driven by:** Principle 3 (Â¶36(a)) â controls surrounding risk data should be as robust as those applicable to accounting data; Principle 4 (Â¶41) â capture all material risk exposures including off-balance sheet; Principle 7 (Â¶52â53) â reports must be accurate and precise.
- **Search terms:** exposure amount, gross exposure, notional amount, outstanding balance, drawn amount, mark-to-market value, fair value, EAD, exposure at default, principal balance, position value
- **Data quality requirements:**
  - *Accuracy* â Each exposure amount agrees with the corresponding value in the system of record (core banking, trading system, or GL) within a defined materiality tolerance | Sum of absolute differences between risk system exposure amounts and system-of-record balances as a proportion of total portfolio | Target: <0.5% of total portfolio value
  - *Completeness* â No exposure record carries a null or zero amount where a non-zero balance is expected based on the instrument type | Count of exposure records with null or zero gross exposure amount where instrument type implies an outstanding balance | Target: 0
  - *Timeliness* â Exposure amounts reflect positions as of the stated as-of date, not a prior business day | Maximum lag in hours between system-of-record position update and risk system update, per risk class | Threshold set by risk class per Principle 5 requirements

---

**CDE-04 â Risk Type Classification**

- **Definition:** The categorical label that assigns an exposure or position to a primary risk type: credit, market, liquidity, operational, counterparty credit risk. May include sub-classifications (e.g., trading book vs. banking book for market risk).
- **Why critical:** Risk type classification controls which aggregation pipeline, capital model, and report a record flows into. A misclassified record flows into the wrong aggregate and is absent from the correct one â producing simultaneous overstatement in one risk class and understatement in another. The bank cannot demonstrate that reports cover all significant risk areas (Â¶57) if the classification is unreliable.
- **Risk types:** Cross-cutting (the element itself defines risk type for all other classes)
- **Criticality:** **2.** The aggregate figure is produced, but it cannot be trusted to represent the correct population: a record classified as market risk when it is counterparty credit risk inflates one aggregate and deflates another. The error is in slicing, not in the inability to compute a number at all.
- **Driven by:** Principle 4 (Â¶41â42) â aggregation capabilities consistent regardless of risk aggregation system; Principle 8 (Â¶57) â *"exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*
- **Search terms:** risk type, risk class, risk category, asset class, book type, banking book, trading book, risk taxonomy, exposure class
- **Data quality requirements:**
  - *Validity* â Each risk type value is drawn from the approved enterprise risk taxonomy; no free-text or non-standard values | Count of records with a risk type value not on the approved taxonomy list | Target: 0
  - *Completeness* â Every exposure and position record carries a populated risk type classification | Count of records with null risk type | Target: 0
  - *Consistency* â The risk type assigned in the risk system agrees with the risk type in the general ledger or product system for the same instrument | Count of records where risk type in risk system differs from risk type in the product master or GL | Target tracked and investigated above a defined materiality threshold

---

**CDE-05 â Business Line**

- **Definition:** The internal organisational dimension that attributes an exposure or position to a business unit (e.g., Corporate Banking, Global Markets, Retail Banking, Transaction Services). Defined in the enterprise organisational hierarchy.
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. Without it, the bank cannot produce the business-line slice of any risk aggregate, and ad hoc requests that require this breakdown (Principle 6, Â¶50) cannot be answered. Concentration analysis by business line is impossible.
- **Risk types:** Cross-cutting
- **Criticality:** **2.** Aggregates are produced at the total level, but cannot be decomposed by business line; the required slice is unavailable, and concentration within a business line cannot be measured.
- **Driven by:** Principle 4 (title and Â¶41) â *"Data should be available by business lineâ¦ that permit identifying and reporting risk exposures, concentrations and emerging risks"*; Principle 6 (Â¶50) â industry credit exposures *"across all business lines and geographic areas"*.
- **Search terms:** business line, business unit, division, segment, cost centre, profit centre, front office unit, product line
- **Data quality requirements:**
  - *Completeness* â Every exposure record carries a populated business line attribution | Count of records with null or missing business line | Target: <0.5%
  - *Validity* â Each business line value maps to an active node in the enterprise organisational hierarchy | Count of records with a business line code not present in the current organisational master | Target: 0
  - *Consistency* â Business line attribution is consistent across the risk system and the general ledger for the same record | Count of mismatches between risk system and GL business line for the same booking key | Target: tracked and escalated above materiality threshold

---

**CDE-06 â Geography / Country**

- **Definition:** The country or jurisdiction associated with an exposure â typically the country of counterparty incorporation or domicile, or the country of booking, depending on the risk measure. Must be distinguished clearly (which geography concept is in use) and consistently applied.
- **Why critical:** Principle 4 names region as an aggregation dimension; Principle 6 (Â¶50) specifically requires the bank to produce country credit exposures on demand, as of a specified date. Without consistently populated country data, neither regulatory geographic concentration reporting nor supervisory ad hoc queries can be answered.
- **Risk types:** Credit, counterparty, concentration, market
- **Criticality:** **2.** The aggregate at the total level is produced, but the geographic slice â including the specific regulatory use case of country exposure aggregation named at Â¶50 â cannot be reliably produced. Concentration by geography is invisible.
- **Driven by:** Principle 4 (Â¶41) â *"Data should be available byâ¦ region"*; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 8 (Â¶57) â country as a component of credit risk reporting.
- **Search terms:** country code, country of risk, country of booking, jurisdiction, region, ISO country code, country of domicile, country of incorporation, geographic area
- **Data quality requirements:**
  - *Completeness* â Every credit and counterparty exposure record carries a populated country-of-risk value | Count of such records with null country | Target: <0.5%
  - *Validity* â All country values conform to a controlled reference list (e.g., ISO 3166) | Count of non-conforming country values | Target: 0
  - *Consistency* â Where both country-of-booking and country-of-risk are maintained, each is populated and clearly labelled so that aggregations are not inadvertently mixed | Count of records where the geography concept is ambiguous or the two fields are conflated | Target: 0

---

**CDE-07 â Industry / Sector Classification**

- **Definition:** The sector or industry to which a counterparty belongs, classified using an approved taxonomy (e.g., NACE, GICS, SIC, or internal equivalent). Applied at the counterparty or facility level.
- **Why critical:** Principle 4 names industry as a required aggregation dimension; Principle 6 (Â¶50) specifically requires the bank to produce industry credit exposures on demand across all business lines and geographic areas. Principle 8 (Â¶57) names industry sector as a component of credit risk reports. Without it, sector concentration cannot be measured and the explicit regulatory use case at Â¶50 cannot be fulfilled.
- **Risk types:** Credit, concentration
- **Criticality:** **2.** Total exposure aggregates are produced, but sector concentration â named explicitly in the regulation as a reportable dimension â cannot be measured. The comprehensiveness of reports (Principle 8) is directly degraded.
- **Driven by:** Principle 4 (Â¶41) â *"Data should be available byâ¦ industry"*; Principle 6 (Â¶50) â *"industry credit exposures as of a specified date based on a list of industry types across all business lines"*; Principle 8 (Â¶57) â *"industry sector for credit risk"*.
- **Search terms:** industry code, sector code, NACE, GICS, SIC, industry classification, sector classification, counterparty sector, obligor industry
- **Data quality requirements:**
  - *Completeness* â Every credit exposure record where the counterparty is a non-retail entity carries a populated industry/sector code | Count of such records with null sector | Target: <1%
  - *Validity* â All sector values are drawn from the approved classification taxonomy; no free-text entries | Count of records with sector values outside the approved taxonomy | Target: 0
  - *Consistency* â The sector assigned to a counterparty is consistent across all facilities and positions referencing that counterparty | Count of counterparties with more than one distinct sector code applied across their exposure records | Target: tracked; exceptions require documented rationale

---

**CDE-08 â As-Of / Position Date**

- **Definition:** The business date as of which a risk position, exposure, or aggregate is stated. It is the temporal reference point of a record â the date the data represents, as distinct from the date it was processed or loaded.
- **Why critical:** Every risk aggregate is meaningful only with respect to a specific date. The as-of date is the dimension on which timeliness is assessed (Principle 5), on which reconciliation to the general ledger is anchored (Principle 3, Â¶36(c)), and on which ad hoc queries are answered ("aggregate risk dataâ¦ as of a specified date", Â¶50). Without it, there is no way to know which snapshot an aggregate represents, making it impossible to confirm the figure is current or to reconcile it to anything.
- **Risk types:** Cross-cutting
- **Criticality:** **3.** *Without this element, the aggregate figure "total group credit exposure as of [date]" cannot be computed â or reconciled to the system of record â at all, because there is no temporal key on which to filter, join, or validate the snapshot being represented.*
- **Driven by:** Principle 5 (Â¶44â46) â timely production of aggregate risk data; Principle 6 (Â¶50) â *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 3 (Â¶36(c)) â reconciliation to accounting sources.
- **Search terms:** as-of date, position date, value date, reference date, reporting date, snapshot date, business date, effective date
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a populated, non-null as-of date | Count of records with null position date | Target: 0
  - *Accuracy* â The as-of date on a risk record matches the date of the underlying transaction or balance in the system of record | Count of records where the risk system as-of date differs from the system-of-record value date for the same transaction key | Target: 0
  - *Timeliness* â Risk records for a given as-of date are available in the aggregation layer within the frequency window defined for each risk class | Maximum elapsed time between close of business on the as-of date and availability of all records for that date in the risk aggregation system | Threshold by risk class, per Principle 5 requirements

---

**CDE-09 â General Ledger / System-of-Record Reconciliation Key**

- **Definition:** The identifier â typically a transaction reference, deal number, or account number â that allows a specific risk record to be matched back to its originating entry in the general ledger or primary system of record. This is the joining key for the reconciliation process mandated by Â¶36(c).
- **Why critical:** Â¶36(c) explicitly requires that risk data be reconciled to source systems including accounting data. Â¶36(a) requires controls on risk data to be as robust as those on accounting data. Without this key, reconciliation is impossible: the bank cannot demonstrate that the exposure in its risk system corresponds to the balance in its GL, and therefore cannot evidence accuracy. An unverifiable figure is not compliant even if it happens to be numerically correct.
- **Risk types:** Cross-cutting (reconciliation is required for all risk types)
- **Criticality:** **3.** *Without this element, the aggregate figure's accuracy cannot be reconciled to the system of record at all, because there is no key on which to join the risk record to its accounting counterpart â and under Â¶36(c), an unreconciled figure is an inaccurate one for compliance purposes.*
- **Driven by:** Principle 3 (Â¶36(c)) â *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 7 (Â¶53(a)) â *"processes to reconcile reports to risk data"*.
- **Search terms:** deal ID, transaction reference, trade ID, account number, GL account key, source transaction key, booking reference, origination ID, instrument ID, position ID
- **Data quality requirements:**
  - *Completeness* â Every material risk record carries a populated reconciliation key | Count of risk records with null or missing reconciliation key | Target: 0 for on-balance-sheet items; tracked with documented rationale for off-balance-sheet
  - *Uniqueness* â Each reconciliation key on a risk record resolves to exactly one record in the system of record | Count of reconciliation keys that match zero records or more than one record in the GL/system of record | Target: 0
  - *Accuracy* â The exposure amount on the risk record agrees with the balance on the matched GL record within materiality tolerance | Sum of absolute differences between matched risk and GL amounts as a proportion of total matched portfolio | Target: <0.5%; exceptions reported and investigated

---

**CDE-10 â Source System / Provenance Flag**

- **Definition:** The identifier of the system from which a risk record originates, combined with a flag indicating whether the record was produced by an automated feed or entered via a manual process or end-user computing tool (e.g., spreadsheet, access database).
- **Why critical:** Â¶36(b) requires that manual processes and end-user computing tools be subject to effective controls and that their use be documented. Â¶39 requires documentation of all risk data aggregation processes and an explanation of any manual workarounds. Without source system identification, it is impossible to apply differential controls, to assess reliance on manual processes, or to conduct the independent validation required at Â¶29(a). The completeness of coverage â which systems are feeding the aggregation â also cannot be confirmed.
- **Risk types:** Cross-cutting
- **Criticality:** **2.** Aggregate figures may be produced, but the bank cannot identify which records arrived via uncontrolled manual channels, cannot apply the differential controls required by Â¶36(b), and cannot evidence the completeness of system coverage. Independent validation (Â¶29(a)) is degraded because the scope of manual input is unknown.
- **Driven by:** Principle 3 (Â¶36(b)) â *"Where a bank relies on manual processes and desktop applicationsâ¦ it should have effective mitigants in place"*; Principle 3 (Â¶36(d)) â strive towards single authoritative source; Principle 3 (Â¶39) â *"document and explain all of their risk data aggregation processes whether automated or manual"*; Principle 1 (Â¶29(a)) â independent validation of all components.
- **Search terms:** source system, feed name, system of origin, data source indicator, manual override flag, EUC flag, end-user computing indicator, automated feed flag, data lineage, provenance tag, upload source
- **Data quality requirements:**
  - *Completeness* â Every risk record carries a populated source system identifier and a manual/automated indicator | Count of records with null source system or null provenance flag | Target: 0
  - *Validity* â All source system values appear in the authoritative inventory of approved data feeds | Count of records referencing a source system not registered in the feed inventory | Target: 0; such records escalated immediately
  - *Accuracy* â The proportion of records flagged as manual input is measured per reporting period and compared against the prior period | Trend in manual-input proportion by risk class and source system, reported to data owners | Threshold: material increases trigger review per Â¶39

---

**CDE-11 â Net / Collateralised Exposure Amount**

- **Definition:** The exposure amount remaining after recognised credit risk mitigants â netting agreements, financial collateral, guarantees â are applied. This is the figure that feeds regulatory capital calculations and concentration limit monitoring, as distinct from the gross exposure (CDE-03).
- **Why critical:** Principle 8 (Â¶58) requires reports to provide information in the context of limits and risk appetite. Regulatory and economic capital (Â¶59) are computed from net exposures, not gross. Limit utilisation monitoring and single-name concentration monitoring depend on the post-mitigation figure. If the net exposure is missing or wrong, capital adequacy reporting is distorted and limit breaches may be invisible.
- **Risk types:** Credit, counterparty, concentration
- **Criticality:** **2.** The gross aggregate (CDE-03) is still computable, but capital figures, limit utilisation, and net concentration measures â which are distinct regulatory requirements â are degraded or unavailable. The report exists but misrepresents the risk after mitigation.
- **Driven by:** Principle 8 (Â¶57) â *"risk-related measures (eg regulatory and economic capital)"*; Principle 8 (Â¶58) â *"information in the context of limits and risk appetite/tolerance"*; Principle 4 (Â¶41) â *"including those that are off-balance sheet"* (where netting is often material).
- **Search terms:** net exposure, net credit exposure, post-mitigation exposure, EAD after CRM, collateralised exposure, guaranteed exposure, netting benefit, net replacement cost, adjusted exposure
- **Data quality requirements:**
  - *Accuracy* â The net exposure is arithmetically consistent with the gross exposure minus recognised mitigants; mitigant values are sourced from an authoritative collateral or guarantee system | Count of records where gross exposure minus documented mitigants does not reconcile to the stated net exposure within tolerance | Target: 0
  - *Completeness* â Every counterparty exposure record where a netting agreement or collateral arrangement exists carries a populated net exposure value | Count of such records with null net exposure | Target: 0
  - *Validity* â Applied mitigants reference recognised instruments from the approved collateral register; no undocumented or expired collateral arrangements are reflected | Count of records applying a mitigant not found in the active collateral or guarantee register | Target: 0

---

## 3. Cross-Cutting Data Quality Requirements

These requirements span multiple CDEs and cannot be satisfied by monitoring any single element in isolation. A catalog that only governs individual fields and ignores these will pass element-level checks while missing the structural failures the regulation is actually targeting.

---

**XDQ-01 â Cross-System Counterparty Resolution (Golden Record Completeness)**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-11 (Net Exposure Amount), CDE-06 (Geography), CDE-07 (Industry/Sector)
- **What this monitors:** The same real-world counterparty may be represented by different local identifiers across source systems (trading system, core banking, derivatives platform, trade finance system). CDE-01 assumes this resolution has been done. This cross-cutting requirement verifies that the mapping from each local identifier to the canonical counterparty identifier is complete, current, and unambiguous. Without it, CDE-01's completeness score is misleading: records may carry a populated identifier that maps to a local system key, not to the group-wide canonical entity â making the exposure aggregate for that counterparty incomplete even though no individual record appears null.
- **Why it cannot be expressed as a single-element rule:** The failure mode is a missing *mapping*, not a missing *field*. No element-level null check detects it. Detection requires joining the local identifier population in each source system against the counterparty master and identifying local IDs with no canonical mapping.
- **Dimension:** Completeness
- **Rule intent:** Every local system identifier for a counterparty that appears on an exposure record in any source system has a current, active mapping to exactly one canonical counterparty identifier in the enterprise counterparty master
- **Measurement:** Count of distinct local counterparty identifiers appearing on exposure records across all source systems that have no mapping to the canonical counterparty master, expressed as a count and as a proportion of total distinct local identifiers; reported by source system
- **Suggested threshold:** 0 unmapped identifiers on material exposures; a maximum tolerated count established for immaterial exposures with all exceptions documented and aged
- **Regulatory grounding:** Principle 2 (Â¶33) â *"use of single identifiersâ¦ for data includingâ¦ counterparties"*; Principle 4 (Â¶41, Â¶43) â complete capture of all material risk exposures; Principle 3 (Â¶36(c)) â reconciliation to source systems

---

**XDQ-02 â Risk-to-Finance Reconciliation Coverage**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key), CDE-02 (Legal Entity), CDE-08 (As-Of Date)
- **What this monitors:** CDE-09 ensures that individual records carry a reconciliation key. This cross-cutting requirement verifies that the *reconciliation process as a whole* covers all material portfolios and that the aggregate risk balance reconciles to the aggregate GL balance at the legal-entity and as-of-date level. It detects two failure modes that element-level monitoring of CDE-09 alone cannot catch: (a) reconciliation keys are populated but the reconciliation process does not run for a given legal entity or product type (coverage gap), and (b) individual records reconcile but the totals do not (aggregation error or missing records).
- **Why it cannot be expressed as a single-element rule:** It requires comparing totals across two systems â the risk aggregation layer and the general ledger â aggregated by legal entity (CDE-02) and as-of date (CDE-08). No single field's null rate or validity check captures this.
- **Dimension:** Accuracy; Completeness
- **Rule intent:** For each legal entity and each as-of date in scope, the total gross exposure in the risk aggregation system reconciles to the corresponding balance in the general ledger within an established materiality tolerance; and the proportion of risk records that have been through a formal reconciliation process is tracked and reported
- **Measurement:** (a) Sum of absolute differences between risk-system total exposure and GL total balance, by legal entity and as-of date, as a proportion of total portfolio; (b) Count of legal entity / risk class / as-of date combinations where no reconciliation has been performed, as a proportion of all combinations in scope
- **Suggested threshold:** (a) Monetary variance <0.5% of total portfolio per legal entity; exceptions documented with root-cause and remediation timeline; (b) 100% of material legal entities and risk classes reconciled for each reporting period; any gap escalated to data owner
- **Regulatory grounding:** Principle 3 (Â¶36(a)) â *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 3 (Â¶36(c)) â reconciliation with accounting sources; Principle 7 (Â¶53(a)) â *"processes to reconcile reports to risk data"*

---

## 4. Out of Scope

This section states plainly what the CDE register and data quality monitoring framework described above cannot deliver. A governance programme that conflates these with catalog work will misallocate effort and leave genuine compliance gaps unaddressed.

---

### Principle 1 â Governance (Â¶27â31): Board and senior management accountability

**What CDEs address:** Principle 1 motivates the entire register â board accountability for data quality risk (Â¶27), the requirement to identify data critical to risk aggregation (Â¶30), and the requirement for agreed service level standards are the governance context for every element and rule above.

**What CDEs and DQ monitoring cannot address:** The obligation is for the board to *approve* the framework (Â¶28), for senior management to be *aware of and understand* coverage limitations (Â¶30), and for the board to be *aware of* implementation compliance (Â¶31). These are accountability and governance structure requirements. A catalog cannot create a board-approved policy, assign data ownership roles (Â¶34), establish service level agreements, or provide evidence that senior management has reviewed and understood the limitations. These require a data governance operating model â RACI, policies, governance committee terms of reference, documented escalation, and audit trails of board review â none of which a catalog produces on its own.

---

### Principle 2 â Data Architecture and IT Infrastructure (Â¶32â35): IT build requirements

**What CDEs address:** Â¶33's requirement for integrated data taxonomies, metadata, and single identifiers drives CDE-01 (Counterparty Identifier), CDE-02 (Legal Entity), and CDE-10 (Source System Provenance). The catalog is the natural home for the metadata layer Â¶33 describes.

**What CDEs and DQ monitoring cannot address:** Â¶32 requires business continuity planning for risk data aggregation â a technology resilience and BCP matter. Â¶34 requires that roles and responsibilities be established for data ownership â a governance operating model matter. Â¶35 requires that the aggregation infrastructure be built to meet all principles simultaneously â an IT architecture matter. None of these are satisfied by cataloguing and monitoring data elements; they require engineering decisions, organisational design, and documented controls that exist independently of the catalog.

---

### Principle 3 â Accuracy and Integrity (Â¶36â40): Controls and automation requirements

**What CDEs address:** Â¶36(c) drives CDE-09 (Reconciliation Key) and XDQ-02. Â¶36(b) and Â¶39 drive CDE-10 (Provenance). Â¶37's requirement for a data dictionary is directly deliverable via the catalog's business glossary and CDE definitions.

**What CDEs and DQ monitoring cannot address:** Â¶36(b) requires that effective mitigants â policies, procedures, controls â be in place for manual and EUC processes. Cataloguing the provenance flag (CDE-10) identifies where manual input exists; it does not create or enforce the controls. Â¶38 requires an appropriate balance between automated and manual systems â an architecture decision. Â¶40 requires escalation channels and action plans for poor data quality â an operational process that must exist outside the catalog and be triggered by the monitoring outputs.

---

### Principle 5 â Timeliness (Â¶44â47): System throughput and SLA enforcement

**What CDEs address:** CDE-08 (As-Of Date) enables measurement of the lag between position date and availability. CDE-10 (Source System) enables identification of slow or late feeds.

**What CDEs and DQ monitoring cannot address:** Whether the system can physically produce aggregates within the required windows â including intraday under stress (Â¶45, Â¶71) â is a function of IT architecture, batch scheduling, and infrastructure capacity. Monitoring can detect that a feed was late; it cannot fix the underlying throughput constraint or guarantee intraday availability. Stress-readiness testing (Â¶70) is an operational discipline, not a catalog function.

---

### Principles 7â11 â Risk Reporting Practices: Report content, comprehensiveness, clarity, frequency, and distribution

**The general position:** Principles 8 through 11 are primarily about the *outputs* â what reports contain, how they are presented, how often they are produced, and to whom they are distributed. These are report design, content governance, and distribution-control matters. A data catalog governs the inputs; it has no mechanism to mandate the content of a report, assess whether it is comprehensible to the board, enforce a production frequency, or control distribution lists and confidentiality classifications.

**Where a principle also drives CDEs (and why that does not resolve the tension):**

- **Principle 7 (Â¶53):** The requirement for reconciliation processes (Â¶53(a)) and exception reporting (Â¶53(c)) drives CDE-09 and XDQ-02. However, the principle's requirements for validated edit checks, reasonableness checks, and an inventory of validation rules (Â¶53(b)) go beyond element-level DQ monitoring â they require a testing and validation framework applied to reports themselves, which a catalog does not execute.

- **Principle 8 (Â¶57â58):** The requirement that reports cover all significant risk areas (Â¶57) drives the risk type classification CDE (CDE-04) and the industry sector CDE (CDE-07) â ensuring those dimensions exist and are populated is a catalog contribution. But the principle's requirement that reports *include* capital adequacy, stress testing results, inter- and intra-risk concentrations, and forward-looking forecasts (Â¶59â60) is a report content requirement. Whether those sections appear in a report, whether they are analytically sound, and whether the board finds them useful (Â¶64â65) are outside catalog scope.

- **Principle 9 (Â¶67):** The requirement to *"develop an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"* (Â¶67) is directly deliverable by the business glossary and CDE register. This is among the most concrete catalog deliverables in the entire regulation. However, the surrounding requirements â that reports be clear, that the balance of qualitative and quantitative information be appropriate (Â¶62), that recipients periodically confirm relevance (Â¶69) â are content design and feedback-process requirements that no catalog addresses.

- **Principle 10 (Â¶70â71):** Frequency requirements are set by the board and senior management and depend on risk type and recipient needs. The catalog has no role in setting, enforcing, or evidencing report frequency. The timeliness monitoring on CDE-08 measures whether *data* arrives on time; it does not measure whether *reports* are produced and delivered within required windows.

- **Principle 11 (Â¶72â73):** Distribution controls and confidentiality management for reports are access management and records management matters. The catalog may carry sensitivity classifications on data assets, which supports access decisions, but the end-to-end distribution control and confidentiality enforcement for report outputs requires document management, entitlement management, and periodic attestation processes outside the catalog.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | **3** | 2 (Â¶33), 4 (Â¶41), 5 (Â¶46) | Uniqueness, Completeness, Validity |
| CDE-02 | Legal Entity (Booking Entity) | **3** | 2 (Â¶33), 4 (Â¶41, Â¶43), 8 (Â¶57) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | **3** | 3 (Â¶36(a)), 4 (Â¶41), 7 (Â¶52â53) | Accuracy, Completeness, Timeliness |
| CDE-04 | Risk Type Classification | **2** | 4 (Â¶41â42), 8 (Â¶57) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | **2** | 4 (Â¶41), 6 (Â¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country | **2** | 4 (Â¶41), 6 (Â¶50), 8 (Â¶57) | Completeness, Validity, Consistency |
| CDE-07 | Industry / Sector Classification | **2** | 4 (Â¶41), 6 (Â¶50), 8 (Â¶57) | Completeness, Validity, Consistency |
| CDE-08 | As-Of / Position Date | **3** | 5 (Â¶44â46), 6 (Â¶50), 3 (Â¶36(c)) | Completeness, Accuracy, Timeliness |
| CDE-09 | GL / System-of-Record Reconciliation Key | **3** | 3 (Â¶36(a), Â¶36(c)), 7 (Â¶53(a)) | Completeness, Uniqueness, Accuracy |
| CDE-10 | Source System / Provenance Flag | **2** | 3 (Â¶36(b), Â¶36(d), Â¶39), 1 (Â¶29(a)) | Completeness, Validity, Accuracy |
| CDE-11 | Net / Collateralised Exposure Amount | **2** | 8 (Â¶57â58), 4 (Â¶41) | Accuracy, Completeness, Validity |

**Criticality 3 elements: CDE-01, CDE-02, CDE-03, CDE-08, CDE-09 â exactly 5.**