# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and Scope

### What the regulation is trying to achieve

- **Reliable aggregation as a precondition for risk management.** The regulation requires banks to produce accurate, complete, timely, and adaptable aggregated risk data — not merely to report it, but so that boards and senior management can make sound decisions in both normal and stress conditions. ¶35: *"risk management reports reflect the risks in a reliable way (ie meeting data aggregation expectations is necessary to meet reporting expectations)."*

- **A single authoritative source per risk type, with reconciliation to accounting.** ¶36(c)–(d): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"* and *"A bank should strive towards a single authoritative source for risk data per each type of risk."* This directly mandates lineage and source-system governance.

- **Integrated data architecture with defined metadata and common identifiers.** ¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts."*

- **A data dictionary enforcing consistent concept definitions.** ¶37: *"a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation."* This is the closest the text comes to directly mandating a business glossary.

- **Documented processes distinguishing automated from manual input, with mitigants for EUC.** ¶36(b), ¶39: banks must document manual workarounds, explain their criticality to aggregation accuracy, and have end-user-computing controls. The documentation obligation implies metadata that flags manual touchpoints.

- **Completeness across all material exposures, sliceable by multiple dimensions.** ¶41, ¶43: risk data must cover all material exposures including off-balance-sheet items; aggregated data must be measurably complete, with exceptions identified and explained.

### Who it applies to

Principles 1–11 apply to **Global Systemically Important Banks (G-SIBs)** as of 2016 and any bank that supervisors subsequently determine should comply. In practice, many non-G-SIB institutions in major jurisdictions are expected to meet the spirit of the principles. The unit of compliance is the **banking group**, meaning requirements apply across subsidiaries, legal entities, and geographies — not only the parent.

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** The unique, persistent identifier assigned to each counterparty (obligor, borrower, trading counterparty, or issuer) that is consistent across all systems within the banking group. Includes natural persons, corporates, sovereigns, and financial institutions.
- **Why critical:** Without a single resolvable counterparty key, exposures recorded in different systems — lending, derivatives, securities — cannot be joined into a group-level aggregate. The entire credit concentration calculation collapses. This is the joining key the regulation specifically names.
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality: 3.** Aggregation of exposure to a single counterparty across business lines and legal entities is impossible without this key. Its failure does not degrade an aggregate — it invalidates it. ¶46(a)–(b) explicitly list aggregated credit exposure to a large corporate borrower and counterparty credit risk exposures as critical risks requiring rapid aggregation under stress.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures"*; Principle 5 (¶46) — *"aggregated credit exposure to a large corporate borrower"* named as a critical risk.
- **Search terms:** counterparty ID, obligor ID, client ID, party identifier, global party ID, GPID, LEI (Legal Entity Identifier), counterparty master, entity reference
- **Data quality requirements:**
  - *Uniqueness* — Each counterparty in the enterprise reference system should have exactly one active identifier; no two records should represent the same real-world counterparty | Count of duplicate counterparty identifiers per entity type per period | Target: 0 duplicates; escalation threshold at any occurrence
  - *Completeness* — Every exposure record must carry a populated, non-null counterparty identifier | Count and percentage of exposure records with null or missing counterparty identifier | Target: 0%; alert above 0.1%
  - *Validity* — Every counterparty identifier on an exposure record must resolve to an active record in the authoritative counterparty reference system | Count of exposure records with counterparty identifiers that have no match in the reference master | Target: 0%; alert above 0%
  - *Consistency* — The same counterparty identifier must refer to the same legal entity or natural person across all systems that consume it | Count of identifier-to-entity pairings that differ across systems for the same identifier value | Target: 0 inconsistencies

---

**CDE-02 — Legal Entity Identifier (Own Entity)**

- **Definition:** The unique identifier for each legal entity within the banking group itself — the booking entity, subsidiary, or branch that holds or records the exposure. Distinct from the counterparty identifier, which identifies the external party.
- **Why critical:** Group consolidation and subsidiary-level reporting both require that every exposure can be attributed to a specific legal entity within the group. Without this, roll-up to the consolidated group total and drill-down to entity level are both broken.
- **Risk types:** Cross-cutting (credit, market, liquidity, operational all require entity attribution)
- **Criticality: 3.** Consolidation across the banking group — the foundational requirement of Principle 4 — is impossible if exposures cannot be reliably attributed to a legal entity. A missing or incorrect booking entity identifier makes the consolidated group figure unauditable. Principle 8 (¶57) also requires risk reports to cover all significant risk areas across the group.
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (¶41) — *"capture and aggregate all material risk data across the banking group"*; Principle 1 (¶30) — *"limitations that prevent full risk data aggregation, in terms of coverage (eg risks not captured or subsidiaries not included)"*
- **Search terms:** legal entity code, booking entity, entity ID, subsidiary code, branch code, LE identifier, group entity, LEI (own-entity usage), organisational unit
- **Data quality requirements:**
  - *Completeness* — Every exposure record must carry a non-null legal entity identifier | Count and percentage of exposure records with null legal entity identifier | Target: 0%
  - *Validity* — Every legal entity identifier on an exposure record must correspond to an active entry in the group's authoritative legal entity hierarchy | Count of exposure records referencing unknown or decommissioned entity codes | Target: 0%
  - *Consistency* — The legal entity hierarchy used in risk systems must match the hierarchy used in the consolidated financial accounts | Count of entity codes present in risk systems but absent from, or differently named in, the finance hierarchy | Review monthly; target: 0 unreconciled differences

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The pre-mitigation monetary amount representing the bank's exposure to a counterparty or instrument for a given risk position, denominated in the transaction currency and converted to a reporting currency equivalent. Covers on-balance-sheet drawn amounts, undrawn commitments, and replacement-cost or mark-to-market values for derivatives.
- **Why critical:** This is the foundational monetary input to every credit, market, and concentration risk aggregate. Without it, no exposure sum can be produced. It is also the reconciliation bridge to the general ledger — accounting data is the named benchmark in ¶36(c).
- **Risk types:** Credit, counterparty, concentration, market
- **Criticality: 3.** Every risk figure — single-name exposure, sector concentration, large-exposure limit — is an arithmetic function of exposure amounts. An invalid or missing exposure amount does not degrade the aggregate; it directly falsifies it. ¶36(a): *"Controls surrounding risk data should be as robust as those applicable to accounting data."*
- **Driven by:** Principle 3 (¶36(a), ¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 7 (¶56) — *"if omission or misstatement could influence the risk decisions of users, this may be considered material"*
- **Search terms:** gross exposure, EAD (exposure at default), notional amount, drawn balance, commitment amount, replacement cost, mark to market, current exposure, nominal value
- **Data quality requirements:**
  - *Accuracy* — Aggregated exposure amounts by legal entity and counterparty must reconcile to the general ledger within agreed materiality tolerances | Sum of risk-system exposure amounts versus corresponding general ledger balances, broken out by legal entity; count and value of reconciling items exceeding materiality threshold | Target: zero unresolved reconciling items above materiality threshold within reporting cycle
  - *Completeness* — Off-balance-sheet exposures (undrawn commitments, derivatives, contingent liabilities) must be present alongside on-balance-sheet amounts | Count of exposure records flagged as off-balance-sheet with null or zero exposure amount; percentage of off-balance-sheet facility types with no corresponding risk record | Target: 0% unexplained off-balance-sheet gaps
  - *Validity* — Exposure amounts must be non-negative for products where negative exposure is not meaningful, and must fall within instrument-type-specific reasonableness bounds | Count of records where exposure amount is outside the expected range for the product type | Alert on any occurrence; review daily
  - *Timeliness* — Exposure amounts must reflect positions as of the stated position date, updated within the latency agreed for each risk type | Age of the most recent exposure feed versus the position date on the record; count of records where feed lag exceeds the SLA | Target: 100% of records within SLA; alert on any breach during stress

---

**CDE-04 — Risk Type Classification**

- **Definition:** The categorical label that assigns a risk record to a defined risk type — credit risk, market risk, liquidity risk, operational risk, counterparty credit risk — in accordance with the bank's risk taxonomy. This is the primary partition for risk aggregation.
- **Why critical:** It is the top-level dimension by which all risk aggregates are partitioned. Without a consistent risk type classification, the bank cannot produce the risk-type-segregated reports that Principle 8 mandates, cannot apply type-specific limits, and cannot evidence that all material risk types are covered.
- **Risk types:** Cross-cutting (it classifies into credit, market, liquidity, operational, counterparty)
- **Criticality: 2.** The aggregate for each risk type degrades — it is incomplete or contaminated by misclassifications — but the system can still produce a number. A misclassification does not invalidate the total book; it misattributes it. This is a Category 2 degradation rather than a Category 3 invalidation.
- **Driven by:** Principle 4 (Principle statement) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings, as relevant for the risk in question"*; Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*
- **Search terms:** risk type, risk category, risk class, risk taxonomy code, risk domain, Basel risk category, Pillar 1 risk type
- **Data quality requirements:**
  - *Validity* — Every risk record must carry a risk type classification drawn from the bank's approved risk taxonomy; no free-text, deprecated, or unrecognised values | Count of records with risk type values outside the approved controlled vocabulary | Target: 0%
  - *Completeness* — Every risk record must have a populated risk type classification | Count and percentage of risk records with null or blank risk type | Target: 0%
  - *Consistency* — The risk type classification used in risk systems must map 1:1 to the risk taxonomy described in the bank's risk appetite framework and board-approved risk reports | Count of risk type codes used in systems that have no approved definition in the business glossary | Target: 0 unmapped codes

---

**CDE-05 — Business Line**

- **Definition:** The organisational or product-line dimension that identifies which business segment — for example, retail banking, corporate banking, trading, transaction banking, asset management — originated or holds the risk exposure.
- **Why critical:** Principle 4 names business line as one of the mandatory aggregation dimensions. Risk concentrations within a business line, and comparisons of risk profile across business lines, require that every exposure is attributable to one.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Business-line-level aggregates degrade when business line is missing or inconsistent, but the group total is still computable. This is a required slicing dimension, not a joining key. The failure mode is an unsliceable or incompletely sliced aggregate, which is Category 2.
- **Driven by:** Principle 4 (Principle statement and ¶41) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*
- **Search terms:** business line, business segment, division, product line, LOB (line of business), profit centre, business unit, organisational segment
- **Data quality requirements:**
  - *Completeness* — Every exposure record must carry a populated business line attribution | Count and percentage of exposure records with null business line | Target: 0%; alert above 0.5%
  - *Validity* — Business line values must be drawn from the bank's approved organisational taxonomy | Count of records with business line values not in the approved hierarchy | Target: 0%
  - *Consistency* — Business line attributions in risk systems should agree with the same attributions in the general ledger and management accounts for the same exposure | Count of exposures where risk-system business line differs from finance-system business line for the same instrument | Review at each reporting cycle; target: 0 unreconciled differences

---

**CDE-06 — Geography / Country of Risk**

- **Definition:** The country or geographic region to which an exposure is attributed for risk measurement purposes — typically the country of the counterparty's domicile, the country of the collateral, or the country in which the risk is ultimately borne, depending on the risk type and the bank's methodology.
- **Why critical:** Geography is explicitly named in Principle 4 as a mandatory aggregation dimension and in ¶50 as the first example of an ad hoc scenario query a bank must be able to execute rapidly. Country concentration risk is a canonical stress use case.
- **Risk types:** Credit, market, liquidity, concentration
- **Criticality: 2.** Geographic aggregates degrade without it, but the book-wide total is unaffected. The failure is an inability to produce a country-level or regional slice, which the regulation explicitly requires. Category 2.
- **Driven by:** Principle 4 (Principle statement) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*; Principle 5 (¶46(c)) — *"market concentrations by sector and region data"*
- **Search terms:** country of risk, country code, geographic region, booking location, domicile country, risk country, ISO country code, region code, jurisdiction
- **Data quality requirements:**
  - *Completeness* — Every exposure record must carry a non-null country-of-risk attribute | Count and percentage of exposure records with null or unrecognised country code | Target: 0%; alert above 0.5%
  - *Validity* — Country codes must conform to the approved reference list (ISO 3166 or internal equivalent); deprecated or non-standard codes must be rejected | Count of records with country values outside the approved reference list | Target: 0%
  - *Consistency* — Where the same exposure appears in multiple systems, the country-of-risk attribution must be identical across those systems | Count of multi-system exposures where country-of-risk differs across systems | Target: 0 unreconciled differences

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The economic sector or industry classification assigned to a counterparty or exposure — for example, using NACE, SIC, GICS, or an internal taxonomy — that identifies the industry in which the counterparty principally operates.
- **Why critical:** Industry concentration is explicitly named in ¶57 as a required component of credit risk reporting, and ¶50 names industry credit exposures as a specific ad hoc scenario that banks must be able to produce rapidly across all business lines and geographies.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Industry-slice aggregates degrade without it. The book total is unaffected. Category 2.
- **Driven by:** Principle 4 (Principle statement) — *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types"*
- **Search terms:** industry sector, sector code, NACE code, SIC code, GICS sector, industry classification, obligor industry, client sector, counterparty sector
- **Data quality requirements:**
  - *Completeness* — Every counterparty and associated exposure record must carry a populated industry/sector classification | Count and percentage of counterparty records and exposure records with null sector code | Target: 0%; alert above 1%
  - *Validity* — Sector codes must be drawn from the bank's approved classification scheme; codes outside the scheme must be flagged | Count of records with sector codes not in the approved taxonomy | Target: 0%
  - *Consistency* — Where counterparty records exist in multiple systems, the sector classification must be identical or mapped to a common standard | Count of counterparty identifiers with conflicting sector codes across systems | Target: 0 unreconciled conflicts

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The calendar date as of which a risk position, exposure balance, or risk measure is stated. This is the temporal key that anchors every aggregate to a specific point in time and enables comparison across periods.
- **Why critical:** Every risk aggregate — and every reconciliation — is stated as of a specific date. Without a reliable position date, it is impossible to verify that the data in an aggregate all relates to the same moment, to comply with timeliness SLAs, or to reconstruct a historical snapshot for audit or supervisory review.
- **Risk types:** Cross-cutting
- **Criticality: 3.** A risk aggregate that mixes positions from different dates is not a valid aggregate — it is an internally inconsistent blend that cannot be defended. Its failure does not degrade an aggregate; it invalidates the temporal integrity of the figure. Category 3.
- **Driven by:** Principle 5 (¶44) — *"A bank's risk data aggregation capabilities should ensure that it is able to produce aggregate risk information on a timely basis"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"* (emphasis on the as-of date requirement); Principle 7 (¶53(a)) — defined reconciliation processes between reports and risk data, which require a common reference date.
- **Search terms:** position date, as-of date, snapshot date, value date, reporting date, trade date, settlement date, data as of, reference date, cut-off date
- **Data quality requirements:**
  - *Completeness* — Every risk record must carry a populated position date | Count and percentage of risk records with null position date | Target: 0%
  - *Validity* — Position dates must be valid calendar dates, not future dates for a completed reporting run, and must fall within the expected reporting period | Count of records with position dates that are null, in the future relative to the run date, or outside the declared reporting window | Target: 0%
  - *Timeliness* — The gap between the position date and the time the record is available for aggregation must be within the agreed SLA for each risk type and reporting frequency | Maximum and median lag (hours) between position date and record availability; percentage of records exceeding SLA per risk type | Target: 100% within SLA; immediate escalation for breaches in stress periods
  - *Consistency* — All records contributing to the same aggregate must share the same position date; mixed-date aggregates must be flagged as exceptions | Count of aggregate batches containing records with more than one distinct position date where a single date was expected | Target: 0 mixed-date aggregates at the point of a scheduled run

---

**CDE-09 — General Ledger / Source System Reconciliation Key**

- **Definition:** The identifier or reference that links a risk data record back to its originating transaction or balance in the general ledger or authoritative system of record. This may be a transaction reference number, a facility ID, a trade ID, or another primary key that exists in both the risk system and the finance system.
- **Why critical:** ¶36(c) requires risk data to be reconciled to accounting sources. Without a reconciliation key, this reconciliation is either impossible or must be performed on aggregated totals only, which is insufficient for identifying the source of individual discrepancies. This is the element that makes accuracy claims evidenceable.
- **Risk types:** Cross-cutting (required for all risk types where exposure originates in the ledger)
- **Criticality: 3.** The reconciliation obligation in ¶36(c) cannot be satisfied at the record level without this key. Without it, the bank can demonstrate agreement of totals but cannot explain individual differences — which supervisors will regard as an evidential gap. Its absence does not degrade a reported figure; it makes the accuracy of that figure unverifiable. Category 3.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** transaction reference, facility ID, trade ID, deal number, instrument ID, source system key, GL account reference, ledger reference, booking reference, ISIN, internal deal ID
- **Data quality requirements:**
  - *Completeness* — Every risk record that relates to a position originating in the general ledger must carry a populated reconciliation key | Count and percentage of risk records of ledger-originated types with null or blank reconciliation key | Target: 0%; alert above 0%
  - *Validity* — Every reconciliation key on a risk record must resolve to a matching record in the source system or general ledger | Count of risk records whose reconciliation key returns no match in the authoritative source | Target: 0%; any occurrence triggers an exception report
  - *Uniqueness* — Each reconciliation key must identify exactly one source record; duplicate keys shared across distinct risk records must be flagged | Count of duplicate reconciliation key values pointing to different source records | Target: 0 unresolved duplicates
  - *Accuracy* — The exposure amount on the risk record must agree to the corresponding balance in the source system within the agreed tolerance | Sum of absolute differences between risk-record amounts and source-system amounts, grouped by reconciliation key; count of pairs exceeding materiality threshold | Target: 0 pairs exceeding materiality threshold at close of reconciliation cycle

---

**CDE-10 — Source System / Input Method Flag**

- **Definition:** The attribute that identifies the system from which a risk data record originated and, where applicable, flags whether the data was produced by an automated feed, a manual entry process, or an end-user-computing application (spreadsheet, desktop database, or similar).
- **Why critical:** ¶36(b) and ¶39 together require banks to document all risk data aggregation processes whether automated or manual, and to have effective controls and mitigants for EUC. A data catalog cannot enforce those controls, but it must record which records are EUC-sourced so that downstream aggregation processes can apply the appropriate scrutiny and escalation. This is also the element that supports the ¶30 obligation on senior management to understand technical limitations including degree of reliance on manual processes.
- **Risk types:** Cross-cutting (applies to all risk types and data elements)
- **Criticality: 2.** The aggregate figures remain producible, but the bank cannot evidence which portion of its risk data flows through controlled automated pipelines and which passes through manual or EUC channels. This is a required evidential dimension rather than a computational one. Category 2.
- **Driven by:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications…it should have effective mitigants in place"*; Principle 3 (¶39) — *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*; Principle 1 (¶30) — *"limitations…in technical terms (eg model performance indicators or degree of reliance on manual processes)"*
- **Search terms:** source system, data source, system of origin, feed type, input method, EUC flag, manual override flag, automated feed, spreadsheet source, data origin, pipeline identifier
- **Data quality requirements:**
  - *Completeness* — Every risk data record must carry a populated source system identifier and an input method classification | Count and percentage of risk records with null source system or null input method flag | Target: 0%
  - *Validity* — Source system codes and input method values must be drawn from the bank's approved inventory of authorised data sources and input types | Count of records with source system codes or input method values not in the approved inventory | Target: 0%; any new code triggers a governance workflow
  - *Accuracy* — The proportion of risk data volume attributable to EUC or manual sources must be tracked over time and compared to the bank's stated target for automation | Percentage of risk records by exposure value flagged as EUC or manual, reported by risk type and business line, trend over rolling 12 months | Target: declining trend; absolute threshold set by senior management per ¶30
  - *Consistency* — The same source system identifier must be used consistently to refer to the same system across all consuming datasets | Count of distinct names or codes used to refer to the same source system across different datasets | Target: exactly 1 canonical identifier per source system

---

**CDE-11 — Collateral / Credit Risk Mitigant Amount**

- **Definition:** The monetary value of eligible collateral or credit risk mitigation (guarantees, credit derivatives, netting agreements) recognised against a gross exposure, expressed in the transaction or reporting currency. The net exposure is gross minus recognised mitigation.
- **Why critical:** Risk reports routinely present both gross and net exposure figures. ¶57 requires reports to cover all significant components of credit risk, and ¶41 requires all material risk exposures including off-balance-sheet items. A collateral figure that is inaccurate inflates or deflates the net credit risk figure, distorting concentration and capital adequacy measures.
- **Risk types:** Credit, counterparty, concentration
- **Criticality: 2.** Net exposure aggregates degrade if collateral values are wrong or missing, but the gross exposure aggregate (CDE-03) remains valid. The net figure is distorted, not the underlying position record. Category 2.
- **Driven by:** Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas…and all significant components of those risk areas"*; Principle 7 (¶56) — *"if omission or misstatement could influence the risk decisions of users, this may be considered material"*
- **Search terms:** collateral value, collateral amount, eligible collateral, recognised mitigation, netting agreement value, guarantee amount, CRM value, haircut value, net exposure, secured exposure
- **Data quality requirements:**
  - *Completeness* — Every secured exposure record must carry a populated collateral or CRM value; unsecured exposures must explicitly carry a zero or null with an appropriate indicator | Count and percentage of exposure records classified as secured with null or missing collateral value | Target: 0%
  - *Accuracy* — Collateral values must be revalued at least as frequently as the exposure amount and must not be stale beyond the agreed revaluation SLA | Count of collateral records whose last revaluation date exceeds the agreed staleness threshold | Target: 0 stale collateral records in any risk report
  - *Validity* — Collateral values must not exceed the gross exposure they are assigned against; over-collateralisation exceptions must be flagged for review | Count of exposure records where recognised collateral value exceeds the gross exposure amount by more than the permitted margin | Alert on any occurrence; subject to methodology review
  - *Consistency* — Collateral values used in risk systems must reconcile to collateral management system records for the same collateral identifier | Count and value of collateral records where the risk-system valuation differs from the collateral-system valuation beyond materiality | Target: 0 unreconciled differences at reporting cycle close

---

## 3. Cross-Cutting Data Quality Requirements

---

**XDQ-01 — Group-wide counterparty reconciliation: one counterparty, one identity across all systems**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-05 (Business Line), CDE-06 (Geography), CDE-09 (Reconciliation Key)
- **Regulatory basis:** ¶33 — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties"*; ¶36(d) — *"a single authoritative source for risk data per each type of risk"*; ¶46(a) — aggregated credit exposure to a large corporate borrower named as a critical risk.
- **Why this cannot be reduced to a single-element rule:** The problem is not whether a counterparty identifier is valid in one system; it is whether the same real-world counterparty carries the same identifier across the lending system, the derivatives system, the securities system, and the collateral management system. This is a cross-system relationship. No single-element DQ rule can detect fragmentation across systems — it requires a matching or golden-record process whose output can be measured.

| Dimension | Rule intent | Measurement | Suggested threshold |
|---|---|---|---|
| *Uniqueness* | Each real-world counterparty should be represented by exactly one active identifier in the authoritative counterparty master, and all downstream risk systems should reference only that canonical identifier | Count of distinct counterparty identifiers across all risk-contributing systems that resolve to the same real-world entity but have not been linked in the master; percentage of exposure value carried under non-canonical identifiers | Target: 0% of material exposure (above group materiality threshold) carried under non-canonical or unlinked identifiers |
| *Completeness* | All exposure records across all systems must carry a counterparty identifier that has been mapped to the enterprise master | Count and value of exposure records in any contributing system whose counterparty identifier has no mapping to the enterprise counterparty master | Target: 0 unlinked records above individual materiality threshold; full population resolved within 30 days of onboarding a new system |
| *Consistency* | The name, legal structure, country of domicile, and industry sector of a counterparty must be identical in the enterprise master and in all systems that independently hold counterparty attributes | Count of counterparty-attribute pairs where the value in a source system differs from the value in the enterprise master for the same canonical identifier | Target: 0 unresolved attribute conflicts for material counterparties; governance workflow triggered within 1 business day of detection |

---

**XDQ-02 — Risk-to-finance reconciliation: risk data aggregates must be reconcilable to the general ledger**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-09 (GL / Source System Reconciliation Key), CDE-02 (Legal Entity Identifier), CDE-08 (Position / As-Of Date), CDE-10 (Source System / Input Method Flag)
- **Regulatory basis:** ¶36(a) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; ¶36(c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; ¶53(a) — *"Defined requirements and processes to reconcile reports to risk data"*.
- **Why this cannot be reduced to a single-element rule:** Reconciliation is a relationship between two populations — risk records and ledger entries — joined through the reconciliation key (CDE-09), attributed to a legal entity (CDE-02), stated as of a common date (CDE-08). A broken link in any one of these elements breaks the reconciliation chain. The DQ requirement must be stated across all contributing elements simultaneously. Furthermore, the completeness dimension here tests whether the risk population covers the entire ledger population — a test that requires both datasets to be present and joined, not a test on either alone.

| Dimension | Rule intent | Measurement | Suggested threshold |
|---|---|---|---|
| *Accuracy* | The sum of gross exposure amounts in the risk system must agree to the sum of the corresponding balances in the general ledger or source system, at the level of legal entity, product type, and position date | Total absolute variance between risk-system aggregate and GL aggregate by legal entity and product type; count and value of line-item reconciling items exceeding materiality threshold | Target: aggregate variance ≤ agreed materiality threshold; 0 unresolved line items above materiality threshold within the reporting-cycle deadline |
| *Completeness* | Every material ledger entry of a risk-bearing type must have a corresponding record in the risk system; ledger entries with no risk counterpart must be enumerated and explained | Count and value of general ledger entries of risk-bearing product types with no matching risk record by reconciliation key; percentage of total ledger balance unrepresented in risk systems | Target: 0 unmatched items above individual materiality threshold; full explanation of any residual population within reconciliation SLA |
| *Timeliness* | The reconciliation must be completed within the SLA for each reporting cycle and for stress/crisis frequencies; late or incomplete reconciliations must be flagged before reports are distributed | Time elapsed between position date close and completion of risk-to-finance reconciliation sign-off; count of reporting cycles where reconciliation was incomplete at report distribution | Target: 100% of scheduled reconciliations signed off within SLA; 0 reports distributed with open material reconciling items |
| *Consistency* | Reconciliation outcomes must be consistent across legal entities — the same methodology and materiality thresholds must apply to all entities within the group | Count of legal entities where reconciliation methodology or materiality threshold differs from the group standard without documented rationale | Target: 0 unexplained methodology deviations |

---

## 4. Out of Scope

The following principles and obligations cannot be satisfied by building or governing a data catalog, registering CDEs, or running data quality monitors. Stating this explicitly is what makes the CDE register trustworthy: it does not overclaim.

---

### Principle 7 — split treatment

Principle 7 partially drives CDEs. The reconciliation obligation in ¶53(a) directly supports CDE-09 and XDQ-02. The validation-rules inventory in ¶53(b) — *"an inventory of the validation rules that are applied to quantitative information"* — can be hosted in or linked from a data catalog. The exceptions reporting process in ¶53(c) can be triggered by DQ monitors.

However, Principle 7 also demands that senior management **establish accuracy and precision requirements** (¶55) and that the bank **support the rationale for those requirements** (¶56). These are governance and policy decisions. A catalog can record the thresholds that management sets, but it cannot set them, enforce board approval of them, or document the rationale. Those require a risk governance framework with documented policy artefacts, board minutes, and a validation programme per ¶29(a).

---

### Principle 8 — split treatment

Principle 8 partially drives CDEs: ¶57's requirement for industry sector, country, single-name breakdown, and risk-related measures (regulatory and economic capital) directly supports CDE-07, CDE-06, and CDE-04. These are data elements; their governance belongs in the catalog.

However, Principle 8's substantive obligations concern **report content and scope**: ensuring that every significant risk area is covered, that limits and risk appetite are shown in context, that forward-looking forecasts and stress tests are included, and that capital adequacy measures appear in board reports (¶57–¶60). These are decisions about what management chooses to disclose to the board and how. No CDE register or DQ monitor determines whether a report is comprehensive. This requires report design standards, a reporting governance framework, and periodic review of report content against the bank's risk profile.

---

### Principle 9 — entirely out of scope

Principle 9 addresses the clarity, usefulness, and tailoring of risk reports — the balance of quantitative and qualitative information, the appropriateness of content for different recipients, the board's obligation to challenge reports that do not meet its needs (¶61–¶69). ¶67 notes that banks should develop *"an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports"* — this is a business glossary obligation that a catalog can satisfy. But the communication quality, interpretive narrative, recipient-appropriateness, and forward-looking content of reports are editorial and governance matters. A catalog has no purchase on them. These require a reporting governance policy, report templates reviewed by risk committees, and periodic recipient feedback processes per ¶69.

---

### Principle 10 — entirely out of scope

Principle 10 requires the board and senior management to **set the frequency** of risk report production and distribution, to test the bank's ability to produce accurate reports within timeframes especially under stress, and to ensure intraday capability for critical positions (¶70–¶71). CDE-08 (Position Date) and the timeliness dimension in CDE-03 and XDQ-02 capture whether data arrives on time relative to a defined SLA — but the SLA itself, the governance decision about which reports are needed intraday versus daily versus weekly, and the stress-testing of report production capacity are operational and board-governance matters entirely outside the scope of a data catalog.

---

### Principle 11 — entirely out of scope

Principle 11 concerns the distribution of reports to the right people while maintaining confidentiality (¶72–¶73). This is an access-control, information-security, and workflow matter. While a data catalog can record data sensitivity classifications and support stewardship assignments, it does not control report routing, cannot enforce recipient entitlements for finished risk reports, and cannot confirm that distribution has occurred. These require a distribution management system, information classification policy, and access-control governance.

---

### Principle 1 and Principle 2 governance obligations — partially out of scope

Principles 1 and 2 impose **organisational and process obligations** that go beyond metadata: independent validation of risk data aggregation and reporting practices (¶29(a)); inclusion of data aggregation impacts in acquisition due diligence (¶29(b)); IT strategic planning to remediate shortcomings (¶30); board approval of the group framework (¶28); business continuity planning for risk data systems (¶32); and defined roles and responsibilities for data ownership (¶34).

A data catalog can host stewardship assignments, document data owners and custodians, and record whether elements have been through a validation process. But it cannot constitute the independent validation function, approve IT strategy, govern acquisition due diligence, or run business continuity tests. These require programme governance, an independent model/data validation team, board and senior management artefacts, and IT resilience testing.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | 2 (¶33), 4 (¶41), 5 (¶46) | Uniqueness, Completeness, Validity, Consistency |
| CDE-02 | Legal Entity Identifier (Own Entity) | 3 | 1 (¶30), 2 (¶33), 4 (¶41) | Completeness, Validity, Consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3 (¶36), 4 (¶41), 7 (¶56) | Accuracy, Completeness, Validity, Timeliness |
| CDE-04 | Risk Type Classification | 2 | 4 (Principle statement), 8 (¶57) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | 2 | 4 (Principle statement), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | 2 | 4 (Principle statement), 5 (¶46), 6 (¶50) | Completeness, Validity, Consistency |
| CDE-07 | Industry / Sector Classification | 2 | 4 (Principle statement), 6 (¶50), 8 (¶57) | Completeness, Validity, Consistency |
| CDE-08 | Position / As-Of Date | 3 | 5 (¶44), 6 (¶50), 7 (¶53) | Completeness, Validity, Timeliness, Consistency |
| CDE-09 | GL / Source System Reconciliation Key | 3 | 3 (¶36(c)), 7 (¶53(a)) | Completeness, Validity, Uniqueness, Accuracy |
| CDE-10 | Source System / Input Method Flag | 2 | 3 (¶36(b), ¶39), 1 (¶30) | Completeness, Validity, Accuracy, Consistency |
| CDE-11 | Collateral / Credit Risk Mitigant Amount | 2 | 4 (¶41), 7 (¶56), 8 (¶57) | Completeness, Accuracy, Validity, Consistency |
| XDQ-01 | Cross-system counterparty reconciliation | — | 2 (¶33), 3 (¶36(d)), 5 (¶46) | Uniqueness, Completeness, Consistency |
| XDQ-02 | Risk-to-finance reconciliation | — | 3 (¶36(a), ¶36(c)), 7 (¶53(a)) | Accuracy, Completeness, Timeliness, Consistency |