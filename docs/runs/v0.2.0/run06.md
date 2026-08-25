# BCBS 239 — Data Catalog Governance Interpretation

---

## 1. Objectives and Scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation across the group.** Banks must capture *all* material risk data across legal entities, business lines, asset types, geographies, and industries — including off-balance-sheet exposures — so that aggregated figures are complete and not misleading. (¶41–43: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet… Supervisors expect banks to produce aggregated risk data that is complete."*)

- **Accuracy and single-source integrity.** Risk data must be reconciled with source systems, including accounting data, and banks should strive toward *"a single authoritative source for risk data per each type of risk."* Manual overrides must be documented and controlled. (¶36(c)–(d): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate… A bank should strive towards a single authoritative source for risk data per each type of risk."*)

- **Timeliness under stress.** Aggregated risk figures must be producible rapidly — including intraday for certain exposures — during crisis conditions, not only under normal operating conditions. (¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*)

- **Adaptability for ad hoc and supervisory queries.** The data architecture must support slicing and re-aggregating risk data along arbitrary dimensions at short notice, including emerging-risk scenarios and regulatory requests. (¶48–50: *"A bank's risk data aggregation capabilities should be flexible and adaptable to meet ad hoc data requests… a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date."*)

- **Documented data architecture with metadata.** Banks must establish integrated data taxonomies, single or unified identifiers, and characteristics of data (metadata) across the banking group, underpinned by documented ownership and lifecycle controls. (¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*)

- **Board-level accountability for data limitations.** Senior management must understand and disclose the limitations of aggregation — coverage gaps, model limitations, manual process reliance, legal impediments — and the board must be aware of what is missing from the reports it receives. (¶30–31: *"Senior management should be fully aware of and understand the limitations that prevent full risk data aggregation… The board should also be aware of limitations that prevent full risk data aggregation in the reports it receives."*)

**Who it applies to**

Principles 1–11 are directed at **Global Systemically Important Banks (G-SIBs)** as the primary obligation, with the expectation that national supervisors apply equivalent standards to **Domestic Systemically Important Banks (D-SIBs)** and, in principle, to all internationally active banks subject to Basel Committee guidance. The obligations fall on the institution as a whole — board, senior management, business lines, risk functions, and IT — not on any single department.

---

## 2. Critical Data Element Candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** A unique, stable, system-independent identifier assigned to each legal counterparty (borrower, derivatives counterparty, issuer, guarantor) that resolves to the same entity record regardless of which booking system, product line, or geography originated the transaction.
- **Why critical:** Without a single resolved counterparty key, exposures from different systems — loans, derivatives, bonds, contingent liabilities — cannot be summed to produce a group-level counterparty exposure. The aggregate is arithmetically impossible to compute correctly, not merely degraded.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3.** Aggregation is *impossible* without it. Duplicate or unmatched counterparty records cause double-counting or omission; the resulting aggregate figure is invalid rather than approximate.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures"*; Principle 5 (¶46(b)) — *"Counterparty credit risk exposures, including, for example, derivatives"* named as a critical risk requiring rapid aggregation.
- **Search terms:** counterparty ID, party identifier, client ID, obligor ID, customer master, legal entity identifier (LEI), global party key, golden record, BIC, GFCID, counterparty master data
- **Data quality requirements:**
  - *Uniqueness* — Each real-world counterparty maps to exactly one active identifier in the authoritative master; no two records represent the same legal entity | Count of counterparty identifiers that resolve to duplicate legal entity names or LEIs after fuzzy-match deduplication | Target: 0 confirmed duplicates in the master registry
  - *Completeness* — Every exposure record carries a non-null, populated counterparty identifier | Count and percentage of exposure records where the counterparty identifier is null or not present in the master registry | Target: <0.1% unmatched
  - *Validity* — Counterparty identifiers on exposure records match an active entry in the authoritative counterparty master | Count of exposure records referencing an identifier that is inactive, merged, or purged in the master | Target: 0 references to inactive records in current-position data
  - *Consistency* — The same counterparty carries the same identifier across all source systems feeding risk aggregation | Count of counterparties where two or more source systems assign different primary keys to the same legal entity (detected via LEI cross-reference) | Target: 0 unresolved cross-system identity conflicts

---

**CDE-02 — Legal Entity / Booking Entity Identifier**

- **Definition:** The identifier of the bank's own legal entity in which a transaction is booked — the subsidiary, branch, or booking vehicle within the banking group that holds the position on its balance sheet.
- **Why critical:** Group-level risk consolidation requires summing positions across all booking entities. If an entity is mislabelled or missing, its positions are either omitted from the group aggregate or double-counted. The regulation explicitly requires aggregation "across the banking group" including subsidiaries.
- **Risk types:** Cross-cutting (all risk types), concentration
- **Criticality: 3.** Aggregation across the group is impossible without knowing which entity holds which position. A missing or incorrect booking entity causes a subset of positions to be excluded from the relevant subsidiary or group roll-up entirely.
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (title and ¶41) — *"capture and aggregate all material risk data across the banking group"*; Principle 3 (¶36(c)) — reconciliation requires tying risk data back to the entity's own accounting records.
- **Search terms:** legal entity identifier, booking entity, entity code, LEI, subsidiary code, branch code, entity hierarchy, organisational unit, group entity master
- **Data quality requirements:**
  - *Validity* — Every exposure record references a legal entity identifier that exists in the group's authoritative entity hierarchy | Count of exposure records whose entity code is absent from the current group entity master | Target: 0 references to non-existent entities
  - *Completeness* — No exposure record lacks a booking entity code | Percentage of exposure records with null or blank entity identifier | Target: 0%
  - *Consistency* — The entity identifier on a risk record matches the entity identifier on the corresponding general ledger entry for the same position | Count of risk-to-GL reconciliation breaks attributable to entity code mismatches | Target: 0 unresolved mismatches in current-day positions
  - *Accuracy* — The entity hierarchy used in aggregation reflects current corporate structure (acquisitions, divestitures, restructurings applied within agreed SLA) | Days elapsed since last structural change versus days elapsed since the entity hierarchy was updated | Target: hierarchy updated within the agreed change-management SLA after any structural event

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary amount of a bank's risk exposure to a counterparty or instrument before the application of credit risk mitigants (collateral, guarantees, netting), expressed in the transaction currency. This is the foundational quantity from which net exposure, regulatory capital calculations, and limit utilisation are derived.
- **Why critical:** Every aggregated credit, counterparty, and concentration figure is ultimately a sum or transformation of this amount. An inaccurate gross exposure propagates error into every downstream risk measure and report. It is explicitly named as critical data in ¶46(a)–(b).
- **Risk types:** Credit, counterparty credit, concentration, market (for traded instruments)
- **Criticality: 3.** Without an accurate exposure amount, all aggregated risk figures derived from it — concentration metrics, capital requirements, limit utilisation — are arithmetically incorrect. The figure is invalidated, not merely degraded.
- **Driven by:** Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 5 (¶46(a)) — *"The aggregated credit exposure to a large corporate borrower"* named as a critical risk; Principle 7 (¶52–53) — *"Risk management reports should be accurate and precise… reconciled and validated."*
- **Search terms:** notional amount, exposure at default (EAD), outstanding balance, drawn amount, mark-to-market value, fair value, current replacement cost, gross notional, loan outstanding, trade value
- **Data quality requirements:**
  - *Accuracy* — The exposure amount on a risk record agrees with the corresponding amount on the general ledger or system of record within the agreed materiality tolerance | Sum of absolute differences between risk system exposure amounts and GL balances at counterparty level, as a percentage of total portfolio | Target: within the bank's defined accounting materiality threshold (¶56)
  - *Completeness* — No exposure record has a null or zero-filled exposure amount unless that is genuinely the contractual position | Count of exposure records with null, blank, or implausible (negative where not expected) exposure amounts | Target: 0 null amounts; flagged and reviewed within 1 business day
  - *Timeliness* — Exposure amounts reflect positions as of the agreed position date, not stale data from a prior run | Maximum age of the source feed populating exposure amounts versus the agreed as-of date | Target: within the agreed intraday or end-of-day production SLA
  - *Validity* — Exposure amounts are expressed in a recognised transaction currency and pass sign-convention rules (e.g., drawn balances positive, credit balances within expected range) | Count of records failing currency code validation or sign-convention checks | Target: 0 failures after feed processing

---

**CDE-04 — Risk Type Classification**

- **Definition:** The categorical label that assigns each exposure or position to its primary risk type — at minimum: credit risk, market risk, liquidity risk, operational risk, and counterparty credit risk. Where finer granularity is needed (e.g., interest rate risk within market risk), sub-classifications should be captured.
- **Why critical:** Without a valid risk type label, it is impossible to partition the portfolio into the regulatory risk categories required by Principles 4, 7, and 8, or to apply the correct capital methodology. An exposure without a risk type cannot be routed to the correct aggregation, limit framework, or capital calculation.
- **Risk types:** Cross-cutting
- **Criticality: 3.** Partitioning by risk type is a structural prerequisite. An exposure record with a missing or incorrect risk type will be excluded from one aggregate and, if misclassified, incorrectly included in another — making both figures wrong simultaneously.
- **Driven by:** Principle 4 (¶41–42) — aggregation must cover all risk types; ¶42: *"each system should make clear the specific approach used to aggregate exposures for any given risk measure"*; Principle 7 (¶53(b)) — *"Automated and manual edit and reasonableness checks, including an inventory of the validation rules that are applied to quantitative information"*; Principle 8 (¶57) — *"Reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)."*
- **Search terms:** risk type code, risk category, risk classification, product risk type, asset class, risk dimension, BCBS risk category, risk taxonomy code
- **Data quality requirements:**
  - *Validity* — Every exposure record carries a risk type code drawn from the bank's approved risk taxonomy | Count of records with a risk type code not present in the authoritative taxonomy reference list | Target: 0 invalid codes
  - *Completeness* — No exposure record lacks a risk type classification | Percentage of exposure records with null or blank risk type | Target: 0%
  - *Consistency* — The risk type assigned in the risk system matches the classification used in the corresponding capital model feed for the same instrument | Count of risk-to-capital-model mapping breaks by risk type | Target: 0 unresolved breaks

---

**CDE-05 — Business Line**

- **Definition:** The organisational dimension that assigns each transaction or position to the bank's internal business line — for example, Corporate Banking, Investment Banking, Retail Banking, Transaction Banking, Trading — as defined in the bank's management reporting hierarchy.
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. Without it, the bank cannot produce business-line-level risk views, cannot monitor intra-risk concentrations, and cannot respond to supervisory queries that require slicing by business line. It is a required reporting dimension, not merely a useful label.
- **Risk types:** Cross-cutting
- **Criticality: 2.** The total group aggregate can still be produced, but the business-line slice is unavailable or inaccurate. The regulation specifically requires this slice; its absence is a direct principle breach rather than a reporting preference.
- **Driven by:** Principle 4 (title and ¶41) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas."*
- **Search terms:** business line code, line of business, LOB, division code, segment, business unit, profit centre, cost centre hierarchy, management reporting unit
- **Data quality requirements:**
  - *Completeness* — Every exposure record carries a non-null business line assignment | Percentage of exposure records with null or unmapped business line | Target: <0.5%
  - *Validity* — Business line codes reference an active entry in the current management reporting hierarchy | Count of exposure records referencing an inactive or retired business line code | Target: 0 references to inactive codes in current-position data
  - *Consistency* — The business line on a risk record matches the business line on the corresponding management accounting record for the same position | Count of risk-to-management-accounts mapping breaks by business line | Target: 0 unresolved breaks

---

**CDE-06 — Geography / Country of Risk**

- **Definition:** The country (or region) to which an exposure is assigned for risk purposes — typically the country of the counterparty's domicile, country of the collateral, or country of the ultimate risk obligor, depending on the bank's risk transfer methodology. This is distinct from the booking location.
- **Why critical:** Principle 4 requires data aggregable by region; Principle 6 specifically gives country credit exposure as the example of an ad hoc aggregation that must be achievable at short notice. Without an accurate country-of-risk field, geographic concentration cannot be measured and supervisory stress scenarios cannot be executed.
- **Risk types:** Credit, counterparty credit, concentration, market (sovereign)
- **Criticality: 2.** The overall aggregate is still producible, but geographic concentration reporting — a named supervisory expectation — is unavailable or unreliable. The failure is a direct breach of Principle 4 and Principle 6 rather than a loss of analytical depth.
- **Driven by:** Principle 4 (title) — *"Data should be available by… region"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
- **Search terms:** country of risk, country code, counterparty country, domicile, country of booking, obligor country, geographic region, ISO country code, cross-border flag, transfer risk country
- **Data quality requirements:**
  - *Validity* — Country codes conform to the ISO 3166-1 alpha-2/alpha-3 standard or the bank's approved country master list | Count of exposure records with country codes not present in the approved country reference list | Target: 0 invalid codes
  - *Completeness* — Every credit and counterparty credit exposure carries a non-null country-of-risk assignment | Percentage of in-scope exposure records with null or blank country code | Target: <0.5%
  - *Consistency* — Country of risk on risk records is consistent with country assigned in the bank's country limits system for the same counterparty | Count of counterparties where the country-of-risk differs between the risk aggregation system and the limits management system | Target: 0 unresolved conflicts

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The economic sector or industry to which a counterparty or issuer belongs, assigned using an approved taxonomy (e.g., NACE, GICS, SIC, or an internal equivalent). Applied at the counterparty level and inherited by all exposures to that counterparty.
- **Why critical:** Industry/sector is explicitly named in both Principle 4 (as a required aggregation dimension) and Principle 8 (as a required component of credit risk reports). Principle 6 uses industry credit exposure as an explicit example of a required ad hoc aggregation. Without it, sector concentration cannot be monitored and the named supervisory query cannot be answered.
- **Risk types:** Credit, concentration
- **Criticality: 2.** The aggregate portfolio figure is still correct, but the industry slice — a named regulatory requirement — is unavailable. As with geography, this is a direct principle breach rather than a missing-but-optional analysis.
- **Driven by:** Principle 4 (title) — *"Data should be available by… industry"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"* cited as required report components.
- **Search terms:** industry code, sector code, NACE code, GICS sector, SIC code, economic sector, counterparty industry, obligor sector, industry classification
- **Data quality requirements:**
  - *Validity* — Industry codes reference the bank's approved sector taxonomy | Count of counterparty records with an industry code absent from the approved reference list | Target: 0 invalid codes
  - *Completeness* — Every corporate, financial institution, and sovereign counterparty carries a non-null sector classification | Percentage of in-scope counterparty records with null sector code | Target: <1%
  - *Consistency* — Industry classification assigned in the counterparty master propagates consistently to all exposure records for that counterparty across all source systems | Count of exposure records where the industry code differs from the industry code on the counterparty master for the same entity | Target: 0 discrepancies

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The date as of which an exposure, position, or risk measure is stated — the temporal anchor that defines the snapshot being aggregated. Every risk aggregate is only meaningful relative to a specific as-of date.
- **Why critical:** Without a reliable as-of date, records from different snapshots may be mixed into a single aggregate, producing a figure that does not correspond to any real point in time. It is also the join key for reconciling a risk position to the corresponding general ledger date. Principle 6 specifically requires the ability to produce aggregates *"as of a specified date"*.
- **Risk types:** Cross-cutting
- **Criticality: 3.** If position dates are missing or inconsistent across source systems feeding an aggregate, the bank cannot guarantee it is summing positions from the same snapshot. The resulting figure is internally incoherent — a structural failure of aggregation, not a degraded result.
- **Driven by:** Principle 5 (¶44–45) — *"A bank's risk data aggregation capabilities should ensure… aggregate risk information on a timely basis"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** as-of date, position date, value date, snapshot date, reporting date, trade date, settlement date (where used as risk reference), effective date, run date
- **Data quality requirements:**
  - *Completeness* — Every exposure and position record carries a non-null as-of date | Percentage of risk records with null position date | Target: 0%
  - *Validity* — As-of dates fall within the permissible range (not future-dated beyond T+1, not older than the data retention window for active positions) | Count of records with as-of dates outside the expected range | Target: 0 outside agreed bounds
  - *Consistency* — All records included in a single risk aggregate share the same declared as-of date | Count of aggregation runs where the maximum spread between minimum and maximum as-of date across constituent records exceeds the agreed tolerance (e.g., 0 days for regulatory snapshots) | Target: 0 mixed-date aggregation runs for regulatory reporting

---

**CDE-09 — General Ledger / System-of-Record Reconciliation Key**

- **Definition:** The identifier — typically a trade reference number, account number, or journal entry key — that links a risk data record to its corresponding entry in the general ledger or the system of record (the authoritative source system). This is the technical key that makes Principle 3's reconciliation requirement operational.
- **Why critical:** Principle 3 explicitly requires risk data to be reconciled with accounting sources. Without a resolvable reconciliation key on each risk record, it is impossible to demonstrate that the risk data corresponds to the same positions the accounting system holds, and independent validation (Principle 1, ¶29) cannot be evidenced. This is one of the two elements most frequently absent from CDE registers, and one of the two that are most directly named in the regulation.
- **Risk types:** Cross-cutting (all risk types that must be evidenced to the GL)
- **Criticality: 3.** Without this key, the reconciliation mandated by ¶36(c) cannot be performed at all. The accuracy and completeness of risk data cannot be evidenced, not merely is it degraded. A supervisor examining compliance with Principle 3 will ask for this evidence first.
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (¶36(d)) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** trade reference, deal ID, trade ID, loan account number, GL account reference, journal reference, source system key, transaction ID, booking reference, account number, position ID, ISIN (where used as GL line key)
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null reconciliation key that references an entry in the designated system of record | Percentage of risk records with null or blank reconciliation keys | Target: 0%
  - *Validity* — Reconciliation keys on risk records resolve to an active, current entry in the GL or source system of record | Count of risk records whose reconciliation key does not match any record in the corresponding GL or source system | Target: 0 unmatched keys in current-position data; breaks investigated and resolved within T+1
  - *Uniqueness* — Where the reconciliation key is intended to be a one-to-one link (one risk record per GL entry), no two risk records share the same key for the same as-of date unless the data model intentionally allows splits | Count of duplicate reconciliation keys within the same as-of-date risk snapshot, excluding known intentional splits | Target: 0 unintended duplicates
  - *Accuracy* — The exposure amount on the risk record agrees with the balance on the corresponding GL entry within the agreed materiality tolerance, verifiable via the reconciliation key | Sum of absolute GL-to-risk differences, grouped by reconciliation key, as a percentage of total portfolio notional | Target: within the bank's defined materiality threshold per ¶56

---

**CDE-10 — Source System Identifier / Manual Intervention Flag**

- **Definition:** The identifier of the system from which a risk data record originated, plus a flag or attribute indicating whether the record — or any field within it — was subject to manual override, end-user-computing (EUC) input (e.g., a spreadsheet), or manual adjustment after automated processing. These are two logically distinct attributes that are treated as a single CDE because the regulation addresses them together and neither is meaningful without the other.
- **Why critical:** Principles 3 and 1 require banks to document all risk data aggregation processes, identify manual workarounds, measure their materiality, and apply the same controls to manual processes as to automated ones. A source system identifier without a manual flag cannot satisfy ¶39 (documentation of manual workarounds) or ¶36(b) (EUC controls). A manual flag without a source system identifier cannot support the lineage tracing that ¶36(d) requires. Together they are the minimum lineage/provenance record that makes the accuracy and integrity assertion auditable. This is the second of the two elements most frequently omitted from CDE registers.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Aggregated figures can still be produced, but the bank cannot discharge its obligation to document and control the accuracy of manual inputs (¶36(b), ¶39), nor can it support independent validation of data lineage (¶29(a)). A supervisor will treat the absence of this metadata as a governance failure even if the numbers happen to be correct.
- **Driven by:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications (eg spreadsheets, databases)… it should have effective mitigants in place"*; Principle 3 (¶36(d)) — single authoritative source requirement implies source must be identifiable; Principle 3 (¶39) — *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual… Documentation should include an explanation of the appropriateness of any manual workarounds."*; Principle 1 (¶29(a)) — *"Fully documented and subject to high standards of validation."*
- **Search terms:** source system code, source system name, data origin, feed identifier, upstream system, manual adjustment indicator, EUC flag, override flag, manual entry flag, spreadsheet flag, workaround indicator, data lineage tag, provenance attribute
- **Data quality requirements:**
  - *Completeness* — Every risk record carries a non-null source system identifier | Percentage of records with null source system code | Target: 0%
  - *Validity* — Source system identifiers reference an active, registered system in the bank's data architecture inventory | Count of records whose source system code does not match an approved system in the technology inventory | Target: 0 unregistered sources feeding production risk aggregation
  - *Accuracy* — The manual/EUC flag correctly identifies all records that originated from or were modified by manual or EUC processes, with no undetected manual overrides | Count of records where post-hoc audit (GL comparison or exception log) reveals a manual adjustment not reflected in the flag | Target: 0 undetected manual overrides; all flagged EUC inputs logged and reviewed per EUC policy
  - *Timeliness* — Manual adjustment flags are applied at point of entry, not retrospectively after the aggregation run that consumed the data | Count of instances where a manual flag was added to a record after the record had already been included in a completed risk aggregation run | Target: 0 retrospective flags in the current reporting period

---

**CDE-11 — Collateral / Credit Risk Mitigation Identifier**

- **Definition:** The identifier linking an exposure to its associated collateral, guarantee, netting agreement, or other credit risk mitigant, plus the mitigant's current recognised value. Together these are required to compute *net* exposure — the figure that drives regulatory capital and large-exposure calculations after mitigation.
- **Why critical:** Off-balance-sheet exposures and derivatives positions require collateral netting to produce the net counterparty exposure figure. Without the collateral linkage, the bank either over-states (ignoring eligible mitigation) or cannot produce a valid net exposure at all. Principle 4 explicitly requires off-balance-sheet exposures to be captured, and their risk-mitigated values are what supervisors act on.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 2.** Gross exposure can be aggregated without this element (CDE-03 stands alone). Net exposure — and therefore capital adequacy calculations — is degraded or impossible depending on how extensively collateral netting applies to the portfolio. The failure affects a specific, named sub-aggregate rather than invalidating the entire gross figure.
- **Driven by:** Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 5 (¶46(b)) — *"Counterparty credit risk exposures, including, for example, derivatives"* require timely aggregation; Principle 8 (¶57) — reports must cover risk-related measures including regulatory capital, which depends on net exposure.
- **Search terms:** collateral ID, collateral agreement reference, CSA identifier, netting set ID, ISDA master agreement ID, collateral value, eligible collateral amount, haircut, guarantee identifier, credit protection amount
- **Data quality requirements:**
  - *Completeness* — Every derivatives and repo/securities-financing exposure has a linked netting set or collateral agreement identifier where one contractually exists | Percentage of in-scope exposure records with no associated netting/collateral link where one is required by the contract inventory | Target: <1%
  - *Accuracy* — The recognised collateral value on the risk record agrees with the independently verified (or custodian-confirmed) collateral value within the agreed tolerance | Count of collateral records where the risk-system value differs from the custodian or third-party verification by more than the agreed threshold | Target: within the bank's defined materiality threshold; all breaches investigated same day
  - *Timeliness* — Collateral values and margin calls are updated within the agreed settlement/valuation cycle to reflect current market values | Maximum age of collateral valuations relative to the position as-of date | Target: within T+0 for variation margin on cleared trades; within T+1 for bilateral

---

## 3. Cross-Cutting Data Quality Requirements

These requirements cannot be expressed as rules against any single CDE. They describe system-spanning conditions whose failure invalidates entire categories of risk reporting.

---

**XDQ-01 — Cross-System Counterparty Identity Resolution**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-05 (Business Line), CDE-06 (Geography), CDE-07 (Industry / Sector), CDE-09 (Reconciliation Key), CDE-11 (Collateral)
- **Principle basis:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; Principle 4 (¶41–43); Principle 5 (¶46(a)–(b))
- **Rule intent:** The same real-world counterparty must resolve to a single, consistent master record across every source system that feeds risk aggregation — loans, derivatives, securities, trade finance, guarantees. Where systems assign different internal keys to the same counterparty, a cross-system identity map (golden record linkage) must exist and be maintained. Without this, CDE-01 is technically non-null in each system but is logically fragmented across the group, and the group-level counterparty aggregate cannot be trusted.
- *Consistency* — The number of counterparties that appear under two or more distinct primary identifiers across risk-feeding source systems, without a maintained cross-system identity mapping resolving them to a single golden record | Measured by: count of entity name / LEI combinations matched to more than one active primary key across all source systems, minus resolved mappings in the identity registry | Target: 0 unresolved cross-system identity splits for counterparties with total group exposure above the large-exposure notification threshold; ≤ agreed tolerance for smaller counterparties
- *Completeness* — The proportion of group-level counterparty exposure that is attributable to a counterparty with a fully resolved, LEI-verified golden record | Measured by: percentage of total gross credit exposure (by notional) assigned to counterparties with a verified, unique golden record | Target: ≥99% of gross notional covered by resolved records; residual investigated and resolved within agreed SLA

---

**XDQ-02 — Risk-to-General-Ledger Completeness Reconciliation**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-08 (As-Of Date), CDE-09 (GL Reconciliation Key), CDE-02 (Legal Entity), CDE-04 (Risk Type)
- **Principle basis:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*; Principle 7 (¶56) — accuracy requirements analogous to accounting materiality
- **Rule intent:** The total risk exposure captured in risk aggregation systems must be reconcilable, in aggregate and by legal entity, to the corresponding positions in the general ledger as of the same date. Two conditions must hold simultaneously: (a) every GL position with a risk character is represented in the risk data (no GL positions orphaned from the risk system); and (b) every risk record can be traced to a GL entry (no risk records floating without a GL anchor). The reconciliation must be performed as a routine operational control, not only at period-end.
- *Completeness (upward — GL to risk)* — The total notional/balance of on-balance-sheet positions recorded in the GL is fully represented in the risk aggregation data at the same as-of date and at the same entity level | Measured by: total GL balance for risk-bearing account types minus total risk-system exposure, by legal entity and as-of date, as a percentage of total GL balance | Target: difference within the bank's defined materiality threshold (¶56); any break exceeding threshold investigated and resolved within T+1
- *Completeness (downward — risk to GL)* — Every risk record for an on-balance-sheet position has a traceable GL entry via its reconciliation key | Measured by: count and notional of risk records that cannot be matched to a GL entry via CDE-09, by legal entity and risk type | Target: 0 unmatched risk records with notional above the materiality threshold; all unmatched records below threshold logged and aged-tracked
- *Consistency* — The entity-level risk aggregate and the entity-level GL balance move in the same direction between reporting periods (directional consistency check as a control before formal reconciliation) | Measured by: count of entity/risk-type combinations where the period-on-period direction of change differs between the risk system and the GL without a documented business reason | Target: 0 unexplained directional divergences

---

**XDQ-03 — Manual and EUC Contribution Materiality Monitoring**

- **CDEs spanned:** CDE-10 (Source System / Manual Flag), CDE-03 (Gross Exposure Amount), CDE-01 (Counterparty Identifier), CDE-09 (Reconciliation Key)
- **Principle basis:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications… it should have effective mitigants in place"*; Principle 3 (¶39) — *"Documentation should include an explanation of the appropriateness of any manual workarounds, a description of their criticality to the accuracy of risk data aggregation."*; Principle 1 (¶29(a)) — independent validation must encompass all components including manual
- **Rule intent:** Manual and EUC-sourced data must be tracked not only record-by-record (CDE-10) but in aggregate, so that senior management and independent validators can assess what proportion of the total risk aggregate rests on manually entered or spreadsheet-derived figures. A bank may have zero null values in CDE-10 and yet face a material accuracy risk if 30% of exposure notional originates from uncontrolled EUC processes. This cross-cutting check surfaces that systemic risk.
- *Accuracy* — The proportion of total risk exposure notional derived from manual or EUC sources is within the board-approved tolerance and does not exceed the threshold above which automatic escalation is required | Measured by: sum of gross exposure amount (CDE-03) on records flagged as manual or EUC origin (CDE-10), as a percentage of total portfolio notional, by risk type and legal entity | Target: within the bank's approved EUC materiality limit; automatic escalation to the data owner and risk function when the threshold is breached
- *Timeliness* — The EUC/manual contribution percentage is calculated and available to risk management within the same production cycle as the risk aggregate it informs | Measured by: elapsed time between the production of the risk aggregate and the availability of the corresponding EUC materiality report | Target: available within the same reporting run; never later than T+1

---

## 4. Out of Scope

The following principles, or aspects of them, describe obligations that a data catalog and its associated CDE register and DQ monitoring framework cannot satisfy. Stating this explicitly is itself a governance output — it defines the boundary between what the catalog delivers and what must be addressed through complementary controls.

---

**Principle 1 — Governance (¶27–31): Board and senior management accountabilities**

The catalog can document data ownership, publish SLA definitions, and expose data quality metrics to data stewards and risk managers. It cannot constitute the governance framework itself. The requirements in ¶27–28 — that the board review and approve the aggregation framework, that adequate resources be deployed, that service level standards be agreed — are organisational and fiduciary obligations. They require board mandates, committee terms of reference, resource allocation decisions, and audit trails of approval. None of these are artifacts a catalog produces or governs. Similarly, ¶29(a)'s requirement for *independent* validation means an organisational function separate from data management — typically Internal Audit or a dedicated Model/Data Validation team — performing structured assessments. The catalog can present evidence to that function; it cannot substitute for it.

**Principle 1 (¶29(b)) — Acquisition and divestiture due diligence:** The requirement that a bank assess a target's risk data aggregation capabilities and risk reporting practices as part of M&A due diligence is a project governance obligation. A catalog can be consulted as a reference, but the assessment process itself — scope definition, on-site review, gap analysis, board sign-off — is outside the scope of any metadata management tool.

---

**Principle 2 — Data Architecture and IT Infrastructure (¶32–35): System design and business continuity**

The catalog documents architecture; it does not constitute it. ¶32's requirement that risk data aggregation capabilities be subject to business continuity planning and business impact analysis is an IT resilience and operational risk management obligation. It requires BCP documentation, DR testing, RTO/RPO definitions, and scenario exercises — none of which are catalog outputs. ¶34's requirement for role-based ownership and lifecycle controls across IT infrastructure is a security and access management matter (PAM/IAM frameworks), not a metadata governance matter. The catalog can record who the data owner is; it cannot enforce IT access controls or evidence their adequacy.

---

**Principle 5 — Timeliness (¶44–47): Production SLA compliance and intraday capability**

The catalog can record the agreed as-of date for each CDE (CDE-08) and monitor whether data arrives within the agreed SLA window (the timeliness DQ dimension). It cannot itself produce risk data faster, compress batch processing cycles, or guarantee intraday availability. ¶45's requirement that systems be *capable* of producing aggregated risk data rapidly during stress is an IT infrastructure and systems design requirement — it depends on database performance, feed architecture, and netting engine throughput. Meeting this requirement requires engineering investment; cataloging timeliness failures evidences non-compliance but does not fix it.

---

**Principles 7–9 — Accuracy, Comprehensiveness, Clarity of Risk Reports (¶52–69): Report content and presentation**

This is the most important out-of-scope boundary. Principles 7–9 set requirements for what risk management reports must contain, how they must be presented, and to whom. A catalog governs the data that feeds reports; it does not govern the reports themselves.

Specifically:
- **¶53(b)** — maintaining an inventory of validation rules applied to quantitative information in reports is a report production governance requirement (a risk reporting framework artifact), not a data catalog artifact. A catalog can document field-level DQ rules; it cannot maintain the inventory of report-level validation logic.
- **¶57–60** — requirements that reports cover all significant risk areas, include risk-related measures such as regulatory and economic capital, identify emerging concentrations, provide forward-looking forecasts, and contain stress test results are **report content requirements**. They govern what information appears in a management report delivered to the board. No amount of CDE governance or DQ monitoring ensures a report is comprehensive, forward-looking, or appropriately contextualised. These require reporting framework design, report template governance, and board feedback loops (¶65, ¶69).
- **¶61–69** — clarity, usefulness, balance of qualitative versus quantitative content, tailoring to recipient needs, and periodic confirmation that recipients find the information relevant are **communication and governance requirements**. They require reporting policies, distribution procedures, feedback mechanisms between the board and senior management, and periodic review processes. A catalog has no role in any of these.

**Split principle note — Principles 4, 6, and 8:** Each of these principles simultaneously drives CDE requirements (§2 above) and contains reporting obligations that are out of scope. The split is as follows:
- **Principle 4** drives CDE-05 (Business Line), CDE-06 (Geography), and CDE-07 (Industry/Sector) as required aggregation dimensions. The catalog governs whether those dimensions are populated on data records. It cannot ensure that a *report* presents those dimensions comprehensively or that the board considers the results.
- **Principle 6** drives the requirement that the data architecture support ad hoc slicing (hence the need for CDE-06 and CDE-07 to be populated and CDE-08 to support date-specific queries). It cannot guarantee that the bank *has* built flexible aggregation tooling, or that risk personnel can actually execute ad hoc queries rapidly — that is an IT capability matter.
- **Principle 8** names industry sector (¶57) as a required report component, which supports CDE-07. The obligation that the report itself cover all significant risk areas, include capital projections, and address emerging concentrations remains a report content obligation outside the catalog's scope.

---

**Principles 10 and 11 — Frequency and Distribution (¶70–74)**

These principles govern *when* reports are produced and distributed, and *to whom*. They require the bank to define frequency requirements for normal and stress conditions, routinely test its ability to meet them, establish confidentiality controls on distribution, and periodically confirm recipients are receiving timely reports (¶73). All of these are operational and governance processes — they require scheduling frameworks, distribution lists, access controls, and management attestation. The catalog's timeliness DQ dimension (as applied to CDE-08) can surface whether data arrived late for a given run; it cannot govern report scheduling, distribution procedures, or recipient confirmation processes.

---

## 5. Summary Table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | P2 (¶33), P4 (¶41), P5 (¶46) | Uniqueness, Completeness, Validity, Consistency |
| CDE-02 | Legal Entity / Booking Entity Identifier | 3 | P2 (¶33), P4 (¶41), P3 (¶36c) | Validity, Completeness, Consistency, Accuracy |
| CDE-03 | Gross Exposure Amount | 3 | P4 (¶41), P5 (¶46a–b), P7 (¶52–53) | Accuracy, Completeness, Timeliness, Validity |
| CDE-04 | Risk Type Classification | 3 | P4 (¶41–42), P7 (¶53b), P8 (¶57) | Validity, Completeness, Consistency |
| CDE-05 | Business Line | 2 | P4 (title/¶41), P6 (¶50) | Completeness, Validity, Consistency |
| CDE-06 | Geography / Country of Risk | 2 | P4 (title), P6 (¶50) | Validity, Completeness, Consistency |
| CDE-07 | Industry / Sector Classification | 2 | P4 (title), P6 (¶50), P8 (¶57) | Validity, Completeness, Consistency |
| CDE-08 | Position / As-Of Date | 3 | P5 (¶44–45), P6 (¶50), P7 (¶53a) | Completeness, Validity, Consistency |
| CDE-09 | GL / System-of-Record Reconciliation Key | 3 | P3 (¶36c–d), P7 (¶53a) | Completeness, Validity, Uniqueness, Accuracy |
| CDE-10 | Source System ID / Manual Intervention Flag | 2 | P3 (¶36b, ¶39), P1 (¶29a) | Completeness, Validity, Accuracy, Timeliness |
| CDE-11 | Collateral / Credit Risk Mitigation Identifier | 2 | P4 (¶41), P5 (¶46b), P8 (¶57) | Completeness, Accuracy, Timeliness |

**Cross-cutting requirements summary:**

| XDQ | Name | CDEs Spanned | Key Principle | DQ Dimensions |
|---|---|---|---|---|
| XDQ-01 | Cross-System Counterparty Identity Resolution | CDE-01, 05, 06, 07, 09, 11 | P2 (¶33), P4 (¶41–43), P5 (¶46) | Consistency, Completeness |
| XDQ-02 | Risk-to-General-Ledger Completeness Reconciliation | CDE-02, 03, 04, 08, 09 | P3 (¶36a, ¶36c), P7 (¶53a, ¶56) | Completeness, Consistency |
| XDQ-03 | Manual and EUC Contribution Materiality Monitoring | CDE-01, 03, 09, 10 | P3 (¶36b, ¶39), P1 (¶29a) | Accuracy, Timeliness |