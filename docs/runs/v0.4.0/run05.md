# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Board-level accountability for data quality as a risk discipline.** The framework must be board-approved, resourced, and subject to independent validation. Limitations in coverage or automation must be disclosed to the board and senior management, not absorbed silently by risk teams. (¶27–¶31: *"A bank's board and senior management should promote the identification, assessment and management of data quality risks as part of its overall risk management framework."*)

- **A single, integrated data architecture that enables group-wide aggregation.** Banks must establish integrated data taxonomies, unified naming conventions, and single identifiers across legal entities, counterparties, customers, and accounts — not system-by-system silos. (¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*)

- **Accurate, reconciled, and predominantly automated risk data.** Risk data must be reconciled to accounting sources. A single authoritative source per risk type is the target. Manual processes and end-user computing must be documented, controlled, and treated as a residual rather than a default. (¶36: *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."*)

- **Complete capture of material exposures across all aggregation dimensions.** All material risk exposures — including off-balance-sheet — must be capturable and sliceable by business line, legal entity, asset type, industry, region, and other relevant groupings. Gaps must be identified, measured, and explained. (¶41–¶43: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*)

- **Timeliness scaled to risk type and stress conditions.** Aggregated data must be producible rapidly under stress; specific critical risk categories — large credit exposures, counterparty credit risk, trading positions, liquidity indicators, and operational indicators — are named explicitly as requiring accelerated production capability. (¶45–¶46: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*)

- **Adaptability for ad hoc, on-demand, and regulatory queries.** Aggregation infrastructure must support drill-down, scenario slicing, and rapid re-aggregation on dimensions not anticipated in standing reports — including new regulatory frameworks. (¶48–¶50: *"A bank's risk data aggregation capabilities should be flexible and adaptable to meet ad hoc data requests, as needed, and to assess emerging risks."*)

**Who it applies to**

Principles 1–11 apply to Global Systemically Important Banks (G-SIBs) as the primary addressees (per the document's introduction and ¶22), with national supervisors expected to apply equivalent standards to Domestic Systemically Important Banks (D-SIBs). The unit of compliance is the banking *group* — consolidation across subsidiaries, legal entities, and geographies is a core obligation, not an option.

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** A persistent, system-independent identifier that uniquely and unambiguously represents a single legal counterparty across all booking systems, risk engines, and data stores within the banking group. It is the primary key for linking credit exposures, derivatives positions, and settlement obligations to the same obligor regardless of how that obligor was originally onboarded.
- **Why critical:** Without a resolved, consistent counterparty identifier, exposures recorded in different systems cannot be summed to produce a group-level counterparty credit exposure. The aggregate figure is either impossible to compute (because records cannot be joined) or structurally wrong (because the same counterparty appears as multiple distinct entities). This is the foundational join key for credit risk, counterparty credit risk, and concentration risk.
- **Risk types:** Credit, counterparty credit risk, concentration
- **Criticality: 3.** Without this element, the aggregate figure *total credit exposure to a named counterparty* cannot be computed at all, because records in different systems that represent the same obligor cannot be recognised as such and summed. ¶46(a) names aggregated credit exposure to a large corporate borrower as a critical risk requiring rapid production; that is literally impossible without a resolved identifier.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures"*; Principle 5 (¶46a, b) — counterparty credit exposures named as critical risks.
- **Search terms:** counterparty ID, legal entity identifier, LEI, obligor ID, counterparty reference, entity key, global counterparty ID, party identifier, GCID
- **Data quality requirements:**
  - *uniqueness* — Each real-world counterparty resolves to exactly one canonical identifier within the group; no two distinct counterparties share an identifier | count of duplicate canonical identifiers mapped to distinct legal entities | 0 duplicates; any exception requires documented business justification
  - *completeness* — Every exposure record carries a non-null counterparty identifier that resolves to a record in the counterparty reference register | count of exposure records with null or unmatched counterparty identifier as a percentage of total exposure records | target <0.1% by count; 0% for exposures above materiality threshold
  - *consistency* — The same counterparty is represented by the same identifier across all source systems (trading, lending, treasury, derivatives) | count of counterparty identifiers that refer to the same legal entity under different values across systems | 0 unresolved cross-system mismatches for material counterparties
  - *timeliness* — New counterparty reference data is available in downstream risk systems within the SLA required for the relevant risk report cycle | lag in hours between counterparty record creation and propagation to all consuming risk systems | within the shorter of 24 hours or the reporting cycle of the most time-sensitive risk type

---

**CDE-02 — Booking Legal Entity Identifier**

- **Definition:** The identifier of the legal entity within the banking group in whose name a position, trade, or credit exposure is recorded for accounting and regulatory purposes. Distinct from counterparty — this is the *bank's own* entity, not the obligor.
- **Why critical:** Group consolidation requires summing exposures booked across multiple legal entities while also reporting each subsidiary's standalone exposure. Without a reliable, standardised entity identifier on every risk record, neither consolidation nor subsidiary-level reporting is possible. It is also the key that links risk records to the correct segment of the general ledger for reconciliation.
- **Risk types:** Cross-cutting (all risk types at group consolidation level)
- **Criticality: 3.** Without this element, the aggregate figure *group-consolidated exposure by risk type* cannot be computed at all, because records belonging to different legal entities cannot be correctly attributed and summed or separated; nor can risk data be reconciled to the correct segment of the general ledger (¶36c).
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (¶41–¶43) — complete capture across the banking group; Principle 3 (¶36c) — reconciliation to accounting sources requires entity-level attribution.
- **Search terms:** legal entity ID, booking entity, entity code, subsidiary code, legal entity identifier, LEI (own-entity), organisation unit code, booking location, group entity key
- **Data quality requirements:**
  - *validity* — Every booking entity identifier on a risk record matches a current, active entry in the group's authoritative legal entity register | count of risk records carrying an entity identifier not present in the legal entity register | 0 invalid codes on live positions
  - *completeness* — No risk record is missing a booking entity identifier | count of risk records with null entity identifier | 0% null rate; null is not a permissible value
  - *consistency* — The entity identifier used in risk systems matches the identifier used in the general ledger for the same entity | count of entities for which the risk-system code and the GL code differ without a documented mapping | 0 unmapped mismatches

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary value of a risk exposure before the application of netting, collateral, guarantees, or credit risk mitigation — stated in a defined currency. This is the primary input from which all risk aggregation is performed: it is the number being summed, netted, risk-weighted, or stress-tested.
- **Why critical:** It is the quantity being aggregated. Every risk figure — total credit exposure, net market risk, concentration measure — is either this number or a transformation of it. An incorrect or missing exposure amount makes the aggregate figure arithmetically wrong; there is no fallback.
- **Risk types:** Credit, market, counterparty credit risk, concentration
- **Criticality: 3.** Without this element, the aggregate figure *total gross credit exposure* cannot be computed at all, because there is no value to sum. Every other CDE is a dimension or key that organises this number; this is the number itself.
- **Driven by:** Principle 3 (¶36a) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures"*; Principle 7 (¶52) — reports must *"accurately and precisely convey aggregated risk data."*
- **Search terms:** gross exposure, notional amount, outstanding balance, drawn amount, mark-to-market value, replacement cost, exposure at default, EAD, position value, face value, principal balance
- **Data quality requirements:**
  - *accuracy* — The exposure amount on each risk record agrees with the value in the system of record (general ledger or trading system) within defined materiality tolerance | sum of absolute differences between risk-system exposure amounts and GL/source-system amounts, expressed as a percentage of total portfolio exposure | <0.1% variance at portfolio level; individual record breaches above materiality threshold escalated same day
  - *completeness* — No active risk record carries a null or zero exposure amount where the position is known to be non-zero | count of active records with null or zero exposure amount | 0 for records above materiality threshold
  - *validity* — Exposure amounts are expressed in a valid, non-negative numeric format and in a stated currency | count of records where amount is non-numeric, negative without business justification, or lacks a currency code | 0 invalid values

---

**CDE-04 — Risk Type Classification**

- **Definition:** The categorical label that assigns a position or exposure to a primary risk type — at minimum: credit risk, market risk, liquidity risk, operational risk, and counterparty credit risk. This is the first-level partition of the risk taxonomy required for all risk reporting.
- **Why critical:** Aggregation is always aggregation *by something*. Risk type is the primary dimension along which total exposures are partitioned in regulatory capital calculations, board risk reports, and supervisory returns. An exposure with a wrong or missing risk type classification appears in the wrong bucket or in no bucket, distorting every aggregate built from that classification.
- **Risk types:** Cross-cutting (it *defines* the risk type for every position)
- **Criticality: 2.** The aggregate figure is produced — the exposure amount exists — but it appears in the wrong risk category or is excluded from categorised aggregates, meaning the *credit risk total* or *market risk total* is wrong without the overall portfolio total necessarily being wrong. This is a slice failure, not a total failure.
- **Driven by:** Principle 4 (¶41–¶42) — risk data aggregation capabilities should cover all risk types; Principle 7 (¶52–¶53) — reports must accurately convey aggregated risk; Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*
- **Search terms:** risk type, risk category, risk class, risk classification, asset class, risk taxonomy, product risk type, risk flag
- **Data quality requirements:**
  - *validity* — Every exposure record carries a risk type code that is present in the approved risk taxonomy | count of records with a risk type code not in the approved taxonomy list | 0 invalid codes
  - *completeness* — No active exposure record has a null risk type | count of active records with null risk type | 0% null rate
  - *consistency* — The risk type assigned to a position in the risk system matches the risk type used in the report that aggregates it | count of positions where risk system classification differs from the classification applied at reporting time without a documented mapping | 0 unmapped differences

---

**CDE-05 — Business Line**

- **Definition:** The organisational dimension that identifies the business unit or division responsible for originating or managing a risk position — for example: retail banking, corporate banking, investment banking, trading, treasury. This is one of the explicit aggregation slices required by Principle 4.
- **Why critical:** Principle 4 explicitly requires the ability to aggregate and report risk data by business line. Without this dimension, the bank cannot produce business-line-level risk reports, cannot identify concentrations within a business unit, and cannot demonstrate compliance with the completeness principle across the group's organisational structure.
- **Risk types:** Cross-cutting (required for all risk aggregations)
- **Criticality: 2.** The portfolio-level aggregate is computable, but the *business-line slice* of any aggregate — which is explicitly required by ¶41 and ¶57 — is unavailable or unreliable. This renders the bank non-compliant with the completeness and comprehensiveness requirements for the business-line dimension specifically.
- **Driven by:** Principle 4 (¶41) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 8 (¶57) — reports must cover all significant risk areas across the organisation.
- **Search terms:** business line, business unit, division, desk, product line, segment, cost centre, profit centre, reporting line, organisational unit
- **Data quality requirements:**
  - *completeness* — Every risk record carries a non-null business line code | count of records with null business line | 0% null rate
  - *validity* — Business line codes on risk records match entries in the current, approved organisational hierarchy | count of records with business line codes not in the approved hierarchy | 0 invalid codes
  - *consistency* — The business line attribution of a position is consistent between originating system and risk aggregation engine | count of positions where business line code differs across systems without a documented mapping | 0 unmapped inconsistencies

---

**CDE-06 — Geography / Country of Risk**

- **Definition:** The country or geographic region to which a risk exposure is attributed for risk aggregation purposes — typically the country of the counterparty's domicile, the country where collateral is located, or the country of the underlying obligor depending on the risk type. This is a separate dimension from booking entity.
- **Why critical:** Principle 4 requires aggregation by region; Principle 6 explicitly uses country credit exposures as the canonical example of an ad hoc aggregation the bank must be able to produce rapidly. Geographic concentration risk — a named supervisory concern — cannot be measured without this field. Supervisors expect banks to produce country-level credit exposure on demand (¶50).
- **Risk types:** Credit, market, concentration, liquidity
- **Criticality: 2.** Total portfolio exposure is computable, but the geographic slice — explicitly required by ¶41 and demanded as an ad hoc capability by ¶50 — is unavailable. The *country exposure aggregate* is the figure that cannot be sliced, not the total.
- **Driven by:** Principle 4 (¶41) — aggregation by *"region and other groupings"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
- **Search terms:** country of risk, country code, geography, region, domicile country, booking country, country of incorporation, ISO country code, geographic segment
- **Data quality requirements:**
  - *completeness* — Every material credit exposure record carries a non-null country of risk code | count of credit exposure records with null country code, weighted by exposure amount | <0.1% of total portfolio exposure value has null country
  - *validity* — Country codes conform to an approved reference list (e.g., ISO 3166-1) | count of records with non-standard or unrecognised country codes | 0 invalid codes
  - *accuracy* — Country of risk reflects the economic risk location, not merely the booking location, per the bank's stated country risk policy | count of records where country of risk equals booking country for counterparties known to be domiciled elsewhere | reviewed quarterly; exceptions documented with rationale

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The economic sector or industry to which a counterparty or underlying obligor belongs, assigned using an approved classification scheme (e.g., GICS, NACE, SIC, or internal equivalent). This is a required aggregation dimension for concentration risk identification.
- **Why critical:** Principle 4 requires aggregation by industry; Principle 8 names industry sector as a required report dimension for credit risk (¶57: *"single name, country and industry sector for credit risk"*); Principle 6 uses industry credit exposures as a second canonical ad hoc example (¶50). Sector concentration risk — a primary supervisory concern — is undetectable without this field.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Total credit exposure is computable, but the *industry-sector concentration aggregate* — explicitly required by ¶41, ¶50, and ¶57 — cannot be produced. The slice is unavailable, not the total.
- **Driven by:** Principle 4 (¶41) — aggregation by *"industry"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk."*
- **Search terms:** industry sector, sector code, GICS sector, NACE code, SIC code, industry classification, counterparty sector, borrower industry, economic sector
- **Data quality requirements:**
  - *completeness* — Every credit exposure record for a corporate, institutional, or sovereign counterparty carries a non-null sector code | count of corporate/institutional credit records with null sector code | <0.5% by count; 0% for exposures above materiality threshold
  - *validity* — Sector codes used on records match the bank's approved sector taxonomy | count of records with codes not in the approved taxonomy | 0 invalid codes
  - *consistency* — The sector assigned to a counterparty is consistent across all products and systems through which that counterparty has exposure | count of counterparties assigned different sector codes in different systems without documented rationale | 0 unresolved inconsistencies for material counterparties

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The date as of which a risk position or exposure is stated — the temporal reference point for the snapshot being aggregated. This is distinct from trade date, settlement date, or report-run date. Every aggregate risk figure is a statement as of a specific date; this is that date.
- **Why critical:** An aggregate risk figure without a defined as-of date is not a risk figure — it is a number without meaning. Reconciliation of risk data to the general ledger (¶36c) requires that both datasets be compared as of the same date. Timeliness compliance (Principle 5) is meaningless without knowing the as-of date of the data being reported. Stress scenarios and ad hoc queries (¶50) are always specified as of a date.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3.** Without this element, the aggregate figure *group credit exposure as of [date]* cannot be computed at all, because the temporal reference of the snapshot is undefined; positions from different dates would be mixed into a single aggregate that corresponds to no actual point in time, and reconciliation to the GL (which is also date-stamped) is impossible.
- **Driven by:** Principle 3 (¶36c) — reconciliation requires matching time references; Principle 5 (¶44–¶46) — timeliness requires knowing the date of the data; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date."*
- **Search terms:** as-of date, position date, valuation date, reporting date, snapshot date, reference date, business date, effective date, data vintage
- **Data quality requirements:**
  - *completeness* — Every risk record carries a non-null as-of date | count of risk records with null position date | 0% null rate; null is never permissible
  - *validity* — As-of dates fall within the valid operating calendar for the relevant risk system; future dates are not present on closed books | count of records with dates outside valid operating calendar or with future dates on finalised positions | 0 invalid dates
  - *timeliness* — The maximum lag between the as-of date of a risk record and its availability in the aggregation layer meets the SLA for the relevant risk type and report cycle | measured lag in hours between position date and availability in aggregation layer, by risk type | within the SLA defined per Principle 5 for each risk category; flagged when lag exceeds threshold
  - *consistency* — The as-of date on a risk record matches the as-of date on the corresponding GL entry used for reconciliation | count of risk-GL record pairs where as-of dates differ | 0 date mismatches on reconciled pairs

---

**CDE-09 — GL / System-of-Record Reconciliation Key**

- **Definition:** The identifier — typically a transaction reference, deal number, or journal entry reference — that uniquely ties a risk data record back to the corresponding entry in the general ledger or primary system of record. This is not an exposure measure; it is the linkage that makes verification and audit possible.
- **Why critical:** Principle 3 (¶36c) states that risk data *must* be reconciled to accounting data. Without a reconciliation key, a bank can assert reconciliation but cannot demonstrate it: two records that represent the same transaction cannot be matched. An unverifiable figure is, under ¶36a — which requires controls as robust as those on accounting data — not a compliant figure. The supervisory test is not whether the number looks right but whether it can be evidenced.
- **Risk types:** Cross-cutting (all risk types, because reconciliation applies to all)
- **Criticality: 3.** Without this element, the aggregate figure *total credit exposure reconciled to the general ledger* cannot be evidenced at all, because individual risk records cannot be matched to their corresponding GL entries. An unverifiable aggregate fails ¶36(c) and ¶36(a) in the same way as an arithmetically wrong one — an unreconciled figure is not a compliant one.
- **Driven by:** Principle 3 (¶36c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (¶36a) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 7 (¶53a) — *"Defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** deal reference, transaction ID, trade ID, GL entry reference, journal reference, source transaction key, booking reference, instrument ID, contract number, position ID
- **Data quality requirements:**
  - *uniqueness* — Each risk record carries exactly one reconciliation key; no key appears on more than one distinct risk record unless the many-to-one relationship is documented and expected | count of reconciliation keys that appear on multiple records without a documented mapping | 0 undocumented duplicates
  - *completeness* — Every risk record that is expected to have a corresponding GL entry carries a non-null reconciliation key | count of risk records with null reconciliation key where a GL counterpart is expected | 0% null rate for records in scope for GL reconciliation
  - *accuracy* — Each reconciliation key on a risk record resolves to an existing, active entry in the GL or system of record | count of risk records whose reconciliation key does not match any GL entry | 0 unmatched keys for material positions; all exceptions documented with resolution timeline
  - *consistency* — The exposure amount, as-of date, and booking entity on the risk record agree with the corresponding fields on the matched GL entry within tolerance | count of matched risk-GL pairs where amount, date, or entity differ beyond materiality threshold | 0 above-threshold mismatches; all differences documented as timing items or recognised adjustments

---

**CDE-10 — Source System / Data Provenance Indicator**

- **Definition:** The attribute — or combination of attributes — that identifies the originating system from which a risk record was sourced, and specifically flags whether the record originates from an automated feed, a manual entry, or an end-user computing tool (e.g., a spreadsheet or local database). This is a data lineage field, not a business measure.
- **Why critical:** Principle 3 (¶36b, ¶39) requires that manual processes and end-user computing tools be identified, documented, and controlled. Principle 3 (¶36d) targets a single authoritative source per risk type. Without a provenance indicator, a bank cannot segregate automated from manual data, cannot demonstrate that EUC controls are applied consistently, cannot quantify reliance on manual processes, and cannot evidence progress toward automation. Independent validation (¶29a) requires knowing which records passed through which controls.
- **Risk types:** Cross-cutting (governance and audit trail for all risk types)
- **Criticality: 2.** Aggregate figures are computable, but the bank cannot demonstrate that the controls required by ¶36(a) and ¶36(b) have been applied, cannot identify which portion of any aggregate derives from uncontrolled manual input, and cannot fulfil the documentation obligation of ¶39. The control framework degrades, not the arithmetic.
- **Driven by:** Principle 3 (¶36b) — *"Where a bank relies on manual processes and desktop applications… it should have effective mitigants in place"*; Principle 3 (¶36d) — *"strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (¶39) — *"document and explain all of their risk data aggregation processes whether automated or manual."*
- **Search terms:** source system, originating system, data source, feed type, manual flag, EUC flag, data provenance, input channel, system of origin, automation indicator, end-user computing tag, spreadsheet indicator
- **Data quality requirements:**
  - *completeness* — Every risk record carries a non-null source system identifier | count of risk records with null source system | 0% null rate; source is always known
  - *validity* — Source system codes match entries in the approved source system register maintained by IT/data governance | count of records with source codes not in the register | 0 unregistered source codes
  - *accuracy* — Records sourced from manual or EUC tools are correctly flagged as such; automated feed records are not incorrectly classified as manual | sample-based review count of records where manual/automated flag is inconsistent with actual ingestion route | reviewed quarterly; misclassification rate target 0%
  - *timeliness* — The source system register is updated within a defined SLA when a new source system is onboarded or decommissioned, so that records from new sources are not classified as provenance-unknown | lag in days between source system activation and registration | within the onboarding SLA; no active unregistered source

---

**CDE-11 — Collateral / Credit Risk Mitigation Indicator**

- **Definition:** The flag or reference that indicates whether credit risk mitigation (CRM) — collateral, guarantees, credit derivatives, netting agreements — has been applied to an exposure, and links the exposure to the mitigant record. This is distinct from the gross exposure amount (CDE-03); it enables calculation of net and collateralised exposure.
- **Why critical:** Risk reports are required to present information *in the context of risk appetite and limits* (¶58). Net exposure — the figure after CRM — is the figure against which limits are monitored and capital is calculated in most credit risk frameworks. Without knowing whether and what mitigation is applied, the bank cannot distinguish gross from net exposure in its aggregates, and reports comparing exposure to limits cannot be prepared correctly. Completeness of off-balance-sheet capture (¶41) specifically includes CRM instruments.
- **Risk types:** Credit, counterparty credit risk, concentration
- **Criticality: 2.** The gross aggregate is computable from CDE-03, but the *net exposure aggregate* — which is what risk limits and capital calculations operate on — cannot be reliably produced without knowing which mitigants apply and to which exposures. The figure is produced but cannot be correctly risk-weighted or compared to limits.
- **Driven by:** Principle 4 (¶41) — off-balance-sheet items include CRM instruments; Principle 8 (¶58) — *"Reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance."*
- **Search terms:** collateral flag, collateral ID, netting agreement reference, guarantee indicator, credit risk mitigation, CRM type, secured/unsecured indicator, collateral haircut, protection amount, eligible collateral
- **Data quality requirements:**
  - *completeness* — Every credit exposure record above the materiality threshold carries a CRM indicator (even if that indicator is "none") | count of material credit records with null CRM indicator | 0% null for material exposures
  - *accuracy* — Where a CRM reference is present, it resolves to an active mitigant record with a current valuation | count of CRM references that do not match an active mitigant record, or where the linked mitigant has no current valuation | 0 unresolved references for material exposures
  - *validity* — CRM type codes conform to the approved CRM taxonomy (e.g., financial collateral, physical collateral, guarantee, netting) | count of records with CRM type codes outside the approved taxonomy | 0 invalid codes

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Counterparty Resolution Across Systems (Single-Counterparty View)**

- **Spans:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-05 (Business Line), CDE-06 (Geography), CDE-07 (Industry/Sector), CDE-11 (Collateral/CRM Indicator)
- **The requirement:** Every exposure record in every source system that relates to the same legal counterparty must carry — or be mappable to — the same canonical counterparty identifier before aggregation. This is not a property of any single element; it is a cross-system consistency condition that requires a maintained golden-record counterparty master and documented mapping rules between local system identifiers and the canonical identifier.
- **Why it cannot be expressed as a single-CDE rule:** A CDE-01 completeness rule confirms that individual records have *a* counterparty identifier. This cross-cutting requirement confirms that the *same* counterparty has *the same* identifier — or a documented mapping — across all systems. The failure mode is not a null but a fragmentation: the counterparty exists under different names or codes in different systems, and the aggregation engine treats them as distinct.
- *Consistency* — The intent is that any counterparty with exposures in more than one source system resolves to a single canonical identifier in the group counterparty master | count of counterparties that appear under more than one canonical identifier across systems without a documented merge/split rationale | 0 unresolved duplicates for counterparties with exposure above the materiality threshold; full coverage of all counterparties reviewed on a defined cycle
- *Completeness* — Every source-system local counterparty identifier has an active mapping to a canonical group identifier in the counterparty master | count of source-system counterparty IDs with no mapping to the canonical register | 0 unmapped IDs for active positions
- **Regulatory basis:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties"*; Principle 5 (¶46a, b) — aggregated credit and counterparty credit exposures named as critical risks requiring rapid production.

---

**XDQ-02 — Risk-to-Finance Reconciliation (Risk Data vs. General Ledger)**

- **Spans:** CDE-03 (Gross Exposure Amount), CDE-02 (Booking Legal Entity), CDE-08 (Position/As-Of Date), CDE-09 (GL Reconciliation Key)
- **The requirement:** The aggregate exposure figure produced by the risk aggregation layer must be reconcilable to the general ledger (or designated system of record) at a defined level of granularity — at minimum by legal entity, risk type, and as-of date. This is not a property of CDE-09 alone; it is a process that requires CDE-03 (the amount), CDE-02 (the entity), CDE-08 (the date), and CDE-09 (the link) to all be correct *simultaneously and in relation to each other*. Any one of them being wrong — even if individually valid — can break the reconciliation.
- **Why it cannot be expressed as a single-CDE rule:** Individual DQ rules on CDE-03 check that exposure amounts are non-null and match source at record level. This cross-cutting requirement checks that the *sum* of those amounts, grouped by entity and date, equals the corresponding GL balance — a relationship that only exists when multiple CDEs are considered jointly. A record-level pass on every individual CDE can coexist with a portfolio-level reconciliation failure caused by scope differences (off-balance-sheet items present in risk but absent from GL, or vice versa).
- *Accuracy* — The intent is that the aggregate exposure reported by the risk system equals the aggregate balance in the GL for the same legal entity, risk type, and as-of date within defined materiality tolerance | sum of absolute differences between risk-system aggregate and GL aggregate, expressed as a percentage of total GL balance, measured by entity and date | <0.5% at entity level; any single reconciling item above materiality threshold documented with resolution timeline and escalation within one business day
- *Completeness* — All in-scope positions that are recorded in the GL have a corresponding record in the risk aggregation layer | count of GL positions with no matched risk record, weighted by GL balance | 0% of GL balance is unrepresented in the risk system for positions that are in-scope for risk reporting; off-balance-sheet items tracked separately
- **Regulatory basis:** Principle 3 (¶36a) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 3 (¶36c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 7 (¶53a) — *"Defined requirements and processes to reconcile reports to risk data."*

---

**XDQ-03 — End-User Computing and Manual Input Inventory (Automation Coverage)**

- **Spans:** CDE-10 (Source System / Data Provenance Indicator), CDE-03 (Gross Exposure Amount), CDE-01 (Counterparty Identifier), CDE-09 (GL Reconciliation Key)
- **The requirement:** The proportion of aggregate risk figures that derive from manual or EUC-originated data must be measurable, monitored, and subject to controls equivalent to those on automated feeds. This requires that CDE-10 (provenance flag) be cross-referenced against CDE-03 (the amounts it touches), CDE-01 (the counterparties it covers), and CDE-09 (whether reconciliation keys are present on manual records). No single element captures this — it requires joining provenance data to exposure data and assessing the combined picture.
- **Why it cannot be expressed as a single-CDE rule:** CDE-10 completeness rules confirm that all records have a source flag. This cross-cutting requirement addresses the *risk created by the distribution* of that flag — specifically: what percentage of total exposure value, counterparty coverage, and GL-reconciled positions relies on manual or EUC input? A bank could pass every individual CDE-10 DQ rule while having 40% of its credit exposure flowing through uncontrolled spreadsheets.
- *Accuracy* — The intent is that the share of total aggregate risk exposure attributable to manual or EUC sources is measured, reported to senior management, and is either within approved tolerance or subject to a documented remediation plan | percentage of total portfolio exposure value (by risk type) carried by records flagged as manual or EUC | reported quarterly; threshold set by governance; any increase of >5 percentage points triggers escalation
- *Completeness* — All manual and EUC sources used in risk data production are registered, with owner and control documentation | count of active manual/EUC data inputs not present in the approved EUC register | 0 unregistered manual inputs feeding into regulatory or board risk reports
- **Regulatory basis:** Principle 3 (¶36b) — *"Where a bank relies on manual processes and desktop applications… it should have effective mitigants in place"*; Principle 3 (¶39) — *"document and explain all of their risk data aggregation processes whether automated or manual"*; Principle 1 (¶30) — *"in technical terms (eg model performance indicators or degree of reliance on manual processes)"* named as a limitation senior management must understand.

---

## 4. Out of Scope

The following principles, or portions of them, address obligations that no CDE register or data quality monitoring framework can satisfy. Stating this plainly is part of responsible governance design — a catalog that claims to cover everything covers nothing credibly.

---

**Principle 1 (¶27–¶31) — Board and senior management governance obligations**

The data catalog addresses the underlying data quality conditions that governance should be monitoring. It does not — and cannot — constitute the governance framework itself. Board approval of the risk data aggregation framework (¶28), independent validation of that framework (¶29a), senior management's strategic IT planning obligations (¶30), and the board's awareness of aggregation limitations (¶31) are institutional accountability and oversight requirements. They require committee structures, documented terms of reference, validation programs, and board reporting. A CDE register is evidence that can inform these processes; it is not a substitute for them.

---

**Principle 2 (¶32–¶35) — IT architecture, infrastructure, and business continuity**

The data catalog addresses the *metadata layer* of the data architecture requirement: documenting what data exists, where it comes from, who owns it, and what quality standards apply. This is consistent with ¶33's explicit reference to metadata and naming conventions, which is why Principle 2 drives CDE-01 and CDE-02.

However, the infrastructure obligations in ¶32 (business continuity planning, business impact analysis), ¶34 (role and responsibility assignment across business and IT functions), and ¶35 (maintaining strong aggregation capabilities under stress) are operational, architectural, and organisational requirements. They require investment in resilient systems, documented RACI frameworks, DR/BCP testing, and technology programme governance. A catalog can record data ownership and lineage; it cannot build or test the infrastructure.

---

**Principle 5 (¶44–¶47) — Timeliness of data production (partially)**

CDE-08 (Position/As-Of Date) and its timeliness DQ rule address the *evidence* that data is dated and that lag is measurable. What Principle 5 requires beyond this — the actual capability to produce aggregated risk data within defined SLAs during stress (¶45–¶46), and the testing of that capability (¶47) — is a systems performance, data pipeline, and operational resilience requirement. Knowing that the as-of date is present on records does not make those records available faster. The SLA thresholds in CDE-08 are inputs to a production capability test, not the test itself.

---

**Principle 6 (¶48–¶51) — Adaptability of aggregation infrastructure (partially)**

CDE-05, CDE-06, and CDE-07 address the dimension data that makes ad hoc slicing *possible*. What Principle 6 actually requires — flexible, on-demand aggregation for unanticipated scenarios (¶48–¶49), the technical capability to rapidly re-aggregate on new dimension combinations (¶50), and drill-down functionality for user customisation (¶49b) — is an architectural and tooling requirement for the aggregation layer. Governing the dimension data in a catalog is a necessary but not sufficient condition for adaptability; the aggregation engine must also be capable of using that data flexibly.

---

**Principles 7 (¶52–¶56) and 8 (¶57–¶60) — Risk report accuracy and comprehensiveness (partially)**

Both of these principles partially drive CDEs and are partially out of scope. They are explained together because the split is identical in structure.

*What drives CDEs:* Principle 7's reconciliation requirements (¶53a) and edit/reasonableness check requirements (¶53b) support CDE-09 and CDE-03. Principle 8's named report dimensions — industry sector (¶57) and the business-line, country, and risk-type slices (¶57, ¶59) — drive CDE-05, CDE-06, CDE-07, and CDE-04.

*What the catalog cannot address:* The substance of the reports themselves. Principle 7 requires that reports accurately convey risk — but whether a particular Value-at-Risk model accurately represents market risk, or whether a stress test scenario is appropriately severe, is a risk methodology question. Principle 8 requires that reports cover all material risk areas, include capital adequacy, forward-looking assessments, and scenario analysis (¶59–¶60), and be calibrated to the depth and complexity of the bank's operations. These are report design, risk methodology, and governance content requirements. A CDE register ensures the underlying data feeding those reports is governed; it does not govern whether the report design is adequate, whether the right model has been applied, or whether the board is asking the right questions.

---

**Principle 9 (¶61–¶69) — Clarity and usefulness of reports**

This principle governs how information is *communicated* to recipients. Report format, qualitative-to-quantitative balance, tailoring to recipient need (¶62–¶66), and periodic confirmation that recipients find the information relevant (¶69) are design and governance obligations for the reporting function. ¶67 ("an inventory and classification of risk data items") could be interpreted as supporting a business glossary in the catalog — and a well-maintained business glossary does help — but the broader principle concerns the *communication design* of risk reports, which no metadata management tool addresses.

---

**Principle 10 (¶70–¶71) — Report production frequency**

Frequency requirements are set by the board and senior management based on risk type and stress conditions. Testing the bank's ability to produce reports within those timeframes (¶70) is an operational test of system performance. The data catalog has no role here beyond informing discussions about data pipeline latency.

---

**Principle 11 (¶72–¶74) — Report distribution and confidentiality**

Distribution controls, access management, and confidentiality of risk reports are security and workflow governance requirements. They are addressed by report distribution systems, entitlement management, and information security policy — not by a data catalog's CDE register, though a catalog's data sensitivity classifications may feed into access policy decisions.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | **3** | P2 (¶33), P4 (¶41), P5 (¶46a/b) | Uniqueness, Completeness, Consistency, Timeliness |
| CDE-02 | Booking Legal Entity Identifier | **3** | P2 (¶33), P3 (¶36c), P4 (¶41–43) | Validity, Completeness, Consistency |
| CDE-03 | Gross Exposure Amount | **3** | P3 (¶36a), P4 (¶41), P7 (¶52) | Accuracy, Completeness, Validity |
| CDE-04 | Risk Type Classification | **2** | P4 (¶41–42), P7 (¶52–53), P8 (¶57) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | **2** | P4 (¶41), P8 (¶57) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | **2** | P4 (¶41), P6 (¶50) | Completeness, Validity, Accuracy |
| CDE-07 | Industry / Sector Classification | **2** | P4 (¶41), P6 (¶50), P8 (¶57) | Completeness, Validity, Consistency |
| CDE-08 | Position / As-Of Date | **3** | P3 (¶36c), P5 (¶44–46), P6 (¶50) | Completeness, Validity, Timeliness, Consistency |
| CDE-09 | GL / System-of-Record Reconciliation Key | **3** | P3 (¶36a/c), P7 (¶53a) | Uniqueness, Completeness, Accuracy, Consistency |
| CDE-10 | Source System / Data Provenance Indicator | **2** | P3 (¶36b/d, ¶39), P1 (¶30) | Completeness, Validity, Accuracy, Timeliness |
| CDE-11 | Collateral / Credit Risk Mitigation Indicator | **2** | P4 (¶41), P8 (¶58) | Completeness, Accuracy, Validity |

**Criticality distribution:** 5 elements at criticality 3 (CDE-01, CDE-02, CDE-03, CDE-08, CDE-09); 6 elements at criticality 2 (CDE-04 through CDE-07, CDE-10, CDE-11); 0 elements at criticality 1 — no element in this register is purely contextual. Any element whose absence would not affect an aggregate risk figure was excluded at the candidate stage.