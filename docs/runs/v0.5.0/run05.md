# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and scope

**What the regulation is trying to achieve**

- **Reliable aggregation of risk data across the banking group, including in stress.** Banks must aggregate all material risk exposures — across legal entities, business lines, geographies, and asset types — accurately and completely, not just under normal conditions but also during crises when speed and precision matter most. (Principle 4, ¶41–43; Principle 5, ¶44–47)

- **Accuracy and integrity of risk figures, with reconciliation to accounting.** Risk data must be reconciled to source systems and accounting data; controls must be as robust as those applied to accounting. An unreconciled figure is not a compliant figure, regardless of how it was derived. (Principle 3, ¶36(a), ¶36(c))

- **A single, governed data architecture with documented lineage.** The bank must maintain integrated data taxonomies, single identifiers for counterparties and legal entities, metadata characteristics, and documentation of all aggregation processes — automated or manual. (Principle 2, ¶33; ¶36(d), ¶39)

- **Timely production of risk data, with faster cadences for critical risks.** Different risk types require different speeds; systems must be capable of producing aggregated data rapidly in stress. The as-of date and the lag between position date and report production are therefore material. (Principle 5, ¶44–47)

- **Accurate, comprehensive risk reporting to decision-makers, covering all material risk areas.** Reports must be reconciled and validated, cover all significant risk areas and components (including off-balance sheet), and include forward-looking content. (Principle 7, ¶52–56; Principle 8, ¶57–60)

- **Board and senior management accountability for data quality governance.** The board and senior management are responsible for approving the framework, understanding its limitations, ensuring adequate resources, and identifying data critical to IT infrastructure. Known gaps in coverage must be disclosed, not concealed. (Principle 1, ¶27–31)

**Who and what it applies to**

BCBS 239 applies to **Global Systemically Important Banks (G-SIBs)** as of its January 2013 publication, with national supervisors encouraged to extend it to **Domestic SIBs (D-SIBs)** and other significant institutions over time. It applies to the **consolidated banking group** — parent entity and all subsidiaries — and covers all material risk types: credit, market, liquidity, operational, counterparty credit, and concentration risk. It does not apply to immaterial subsidiaries or non-risk data, but the threshold of materiality is the bank's own, subject to supervisory challenge.

---

## 2. Critical Data Element candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** A single, persistent, system-independent identifier that uniquely and unambiguously resolves to one legal counterparty across all risk systems, booking systems, and the general ledger. This is the entity to which a credit or counterparty exposure is owed, not the internal account or facility.
- **Why critical:** Without a resolvable counterparty identifier, exposures from different systems (loans, derivatives, securities lending, off-balance sheet commitments) cannot be joined into a single aggregate exposure. The bank cannot produce a correct total credit exposure to a large corporate borrower — the explicit example given at ¶46(a). Every credit and counterparty concentration figure depends on this join being possible.
- **Risk types:** Credit, counterparty credit risk, concentration
- **Criticality: 3.** Without this element, the aggregate credit exposure to a single counterparty — CDE-03 summed per counterparty — cannot be computed at all, because records from disparate systems cannot be joined to the same entity. The failure is not degradation; it is the absence of the aggregate. Step-2 sentence: *"Without a resolvable counterparty identifier, the aggregate credit exposure to counterparty X cannot be computed, because exposure records from trading, lending, and off-balance sheet systems cannot be joined to the same legal entity."*
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; and Principle 5 (¶46(a)–(b)) — aggregated credit exposure to a large corporate borrower and counterparty credit risk exposures are named critical risks requiring rapid aggregation.
- **Search terms:** counterparty ID, party identifier, client ID, legal entity identifier, LEI, obligor ID, counterparty reference, customer master ID, GFCID, global counterparty key
- **Data quality requirements:**
  - *uniqueness* — Every counterparty identifier must resolve to exactly one legal entity with no duplicates across or within systems | Count of counterparty identifiers that map to more than one distinct legal entity in the reference data store | Threshold: zero — any duplicate invalidates the aggregation join; there is no materiality tolerance for identifier cardinality | **(¶33)**
  - *completeness* — Every exposure record must carry a non-null, populated counterparty identifier | Count and percentage of exposure records with a null or blank counterparty identifier | Threshold: zero — a record without an identifier cannot be attributed to any counterparty and cannot enter any aggregate | **(¶43)**
  - *validity* — Every counterparty identifier on an exposure record must resolve to an active record in the authoritative counterparty reference system | Count of exposure records whose counterparty identifier does not match any record in the master reference | Threshold: zero — an unresolvable identifier is the functional equivalent of a null for aggregation purposes | **(¶40)**
  - *consistency* — The same counterparty must carry the same identifier across all source systems contributing to risk aggregation | Count of counterparties with differing identifier values for the same legal entity across systems | Threshold: zero — cross-system inconsistency makes de-duplication impossible and distorts concentration measures | **(¶33)**

---

**CDE-02 — Legal Entity Identifier (Booking Entity)**

- **Definition:** The identifier of the bank's own legal entity in which a transaction is booked — the subsidiary, branch, or parent entity that is a party to the instrument. Distinct from CDE-01, which identifies the external counterparty.
- **Why critical:** Group-level risk aggregation requires that every exposure be attributed to a booking entity so that the consolidated group view can be built by summing across subsidiaries, and so that subsidiary-level reports can be produced separately. Without this, the bank cannot demonstrate completeness of coverage across the banking group, nor can it isolate subsidiary risk profiles for regulatory reporting.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3.** Without a booking entity identifier, the aggregate risk exposure for the consolidated banking group cannot be computed, because the bank cannot establish which legal entities have been included and which have not — a group aggregate of unknown coverage is not a compliant aggregate. Step-2 sentence: *"Without a booking entity identifier, the consolidated group aggregate of exposure X cannot be computed, because the bank cannot establish the population of legal entities contributing to it or reconcile coverage against the group structure."*
- **Driven by:** Principle 4 (¶41) — *"A bank's risk data aggregation capabilities should include all material risk exposures"* across the banking group; Principle 2 (¶33) — single identifiers for legal entities; Principle 1 (¶30) — senior management must understand limitations including *"subsidiaries not included."*
- **Search terms:** legal entity ID, booking entity, entity code, subsidiary code, legal entity identifier, LEI (own entity), branch code, reporting entity, group entity hierarchy
- **Data quality requirements:**
  - *completeness* — Every exposure record must carry a non-null booking entity identifier | Count of exposure records with a null booking entity | Threshold: zero — a record without a booking entity cannot be included in or excluded from the group aggregate in a controlled way | **(¶43)**
  - *validity* — Every booking entity identifier must resolve to an active entity in the group legal entity hierarchy | Count of booking entity codes on exposure records that do not match an active node in the group entity register | Threshold: zero — an unresolvable entity code means the exposure cannot be attributed to the group structure | **(¶40)**
  - *consistency* — The group legal entity hierarchy used in risk aggregation must match the structure used in regulatory and statutory reporting | Count of entities present in one hierarchy but absent in the other | Threshold: zero — a mismatch means the group aggregate population differs between risk and regulatory reports | **(¶36(c))**

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary amount representing the bank's gross risk exposure on an instrument or position before the application of collateral, netting, or credit risk mitigants. Denominated in the instrument's native currency. This is the fundamental quantity from which all risk aggregates are constructed.
- **Why critical:** Every aggregated risk figure — total credit exposure, counterparty exposure, concentration — is arithmetically derived from summing this amount. If the amount is wrong, the aggregate is wrong. It is the quantity ¶36(a) requires to be as accurate as accounting data, and ¶53(a) requires to be reconciled to source.
- **Risk types:** Credit, counterparty credit risk, market (for position values), concentration
- **Criticality: 3.** Without a correct gross exposure amount, the aggregate credit or counterparty exposure figure cannot be computed correctly — errors here propagate directly and proportionally into every aggregate built from it. Step-2 sentence: *"Without an accurate gross exposure amount, the aggregate exposure figure for counterparty X or business line Y is arithmetically incorrect, not merely incomplete, because the aggregate is the direct sum of this element."*
- **Driven by:** Principle 3 (¶36(a)) — *"Controls surrounding risk data should be as robust as those applicable to accounting data"*; Principle 4 (¶41) — all material risk exposures must be captured; Principle 7 (¶56) — accuracy requirements analogous to accounting materiality.
- **Search terms:** exposure amount, gross exposure, notional amount, outstanding balance, mark-to-market value, current exposure, EAD (exposure at default), position value, drawn balance, fair value
- **Data quality requirements:**
  - *accuracy* — The gross exposure amount on each risk record must agree with the corresponding value in the authoritative source system within a materiality tolerance | Sum of absolute differences between risk system exposure amounts and source system amounts, as a percentage of total portfolio | Threshold: set by the bank's materiality standard per ¶56 — *"if omission or misstatement could influence the risk decisions of users, this may be considered material"*; the threshold must be formally approved by senior management and documented | **(¶56, ¶40)**
  - *completeness* — All material exposure records, including off-balance sheet items, must be present | Count of off-balance sheet commitments and contingent exposures present in source origination systems but absent from the risk aggregation dataset | Threshold: zero off-balance sheet omissions — ¶41 explicitly requires their inclusion, so any omission is non-compliant regardless of individual size | **(¶43, ¶41)**
  - *validity* — Exposure amounts must be non-negative (or within defined valid ranges for instruments where negative values are permissible, such as derivatives) and denominated in a recognised currency | Count of records with amounts outside the defined valid range for their instrument type | Threshold: zero — invalid amounts cannot be summed correctly | **(¶40)**

---

**CDE-04 — Risk Type Classification**

- **Definition:** The classification code that assigns each exposure or position to its primary risk type — credit risk, market risk, liquidity risk, operational risk, counterparty credit risk, or concentration risk. This is the taxonomy that partitions the portfolio for separate aggregation and reporting by risk type.
- **Why critical:** Risk aggregation is performed within risk type boundaries; credit risk aggregates and market risk aggregates use different methods and appear in different sections of risk reports. Without a valid, consistent risk type classification, exposures are aggregated into the wrong buckets or double-counted, and reports covering "all significant risk areas" (¶57) cannot be produced. It also drives which timeliness standard applies (¶45–46).
- **Risk types:** Cross-cutting (classifies all risk types)
- **Criticality: 2.** An exposure with a missing or wrong risk type classification still contributes a value to some aggregate but contributes it to the wrong one, or is excluded from its correct aggregate. The figure is produced but cannot be trusted for its stated risk category. Which slice is wrong depends on the error: a credit exposure mis-coded as operational inflates the operational aggregate and deflates the credit aggregate.
- **Driven by:** Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 4 (¶41) — capabilities must capture all material risk exposures.
- **Search terms:** risk type, risk category, risk class, risk classification, risk taxonomy, product risk type, risk pillar, Basel risk category, risk bucket
- **Data quality requirements:**
  - *validity* — Every exposure record must carry a risk type classification drawn from the bank's approved risk taxonomy | Count of records with a null risk type or a value not present in the approved taxonomy | Threshold: zero — an unclassified record cannot be routed to the correct aggregate | **(¶40)**
  - *consistency* — The risk type taxonomy used in risk aggregation must match the taxonomy used in risk reporting and regulatory capital calculations | Count of taxonomy codes used in aggregation but absent from the reporting taxonomy, and vice versa | Threshold: zero — a mismatch produces reports that do not correspond to the data they purport to summarise | **(¶36(c))**
  - *completeness* — All exposure types the bank originates must be represented in the risk taxonomy, with no orphaned instrument types | Count of instrument types present in source systems that have no mapping to a risk type | Threshold: zero — unmapped instrument types are silently excluded from all risk aggregates | **(¶43)**

---

**CDE-05 — Business Line**

- **Definition:** The organisational or commercial classification that assigns each exposure or position to the business activity that originated or owns it — for example, retail banking, corporate banking, trading, treasury, private banking. Used as an aggregation dimension, not a cost-centre or management reporting label.
- **Why critical:** Principle 4 explicitly requires data to be available by business line to permit identifying risk exposures and concentrations. Principle 8 requires reports to be consistent with the bank's operations. Aggregates produced without business line dimension cannot be sliced to show where risk is concentrated by activity.
- **Risk types:** Cross-cutting (aggregation dimension for all risk types)
- **Criticality: 2.** The total portfolio aggregate can still be computed without business line, but the business-line slice required by ¶41 and ¶57 cannot. The figure exists but cannot be broken down as required. Which slice degrades: any report that shows risk by business line or compares business lines.
- **Driven by:** Principle 4 (¶41) — data *"should be available by business line, legal entity, asset type, industry, region"*; Principle 8 (¶57) — reports must be *"consistent with the size and complexity of the bank's operations."*
- **Search terms:** business line, business unit, line of business, LOB, division, product line, operating segment, front office group, originating desk
- **Data quality requirements:**
  - *completeness* — Every exposure record must carry a non-null business line assignment | Count and percentage of exposure records with a null or missing business line code | Threshold: zero — a record with no business line cannot contribute to any business-line slice, silently distorting all business-line aggregates | **(¶43)**
  - *validity* — Business line codes must be drawn from the bank's approved business line hierarchy | Count of records carrying codes not present in the approved hierarchy | Threshold: zero — non-standard codes cannot be aggregated consistently | **(¶40)**
  - *consistency* — Business line assignments must be consistent between the risk system and the general ledger for the same transactions | Count of records where the business line code in the risk system differs from the corresponding code in the general ledger | Threshold: set by materiality per ¶56 — small definitional differences may exist at instrument level provided they are explained; systematic differences are non-compliant | **(¶36(c))**

---

**CDE-06 — Geography / Country of Risk**

- **Definition:** The country or jurisdiction assigned to an exposure as the primary location of the risk — typically the country of the borrower's domicile or the country in which a position is held. Distinct from booking location (CDE-02) and collateral location.
- **Why critical:** Principle 4 requires data by region; Principle 6 (¶50) gives the explicit supervisory example of aggregating country credit exposures on an ad hoc basis across all business lines. Concentration by country is a named required report dimension (¶57). Without a reliable geography dimension, country-level concentration risks are invisible.
- **Risk types:** Credit, concentration, market
- **Criticality: 2.** The total credit aggregate is computable without geography, but the geographic slice mandated by ¶41 and ¶50 cannot be produced. The figure exists but cannot be sliced by region as required. Which slice degrades: country credit concentration reports, and any ad hoc geographic query under Principle 6.
- **Driven by:** Principle 4 (¶41) — data must be *"available by … region"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."*
- **Search terms:** country of risk, country code, borrower country, jurisdiction, geographic region, country domicile, booking country, ISO country code, risk country
- **Data quality requirements:**
  - *completeness* — Every credit and counterparty exposure record must carry a non-null country of risk | Count and percentage of credit exposure records with null or missing country code | Threshold: zero — a missing geography makes the exposure invisible to any country-concentration or geographic-slice analysis | **(¶43)**
  - *validity* — Country codes must conform to the bank's approved geography taxonomy (typically ISO 3166) | Count of country codes not matching an approved code in the reference list | Threshold: zero — non-standard codes cannot be consistently aggregated into regional groups | **(¶40)**
  - *accuracy* — The country of risk must reflect the economic risk location, not merely the booking or administrative location | Sample-based review comparing country of risk against counterparty domicile and collateral location, with exception rate tracked | Threshold: exception rate set by materiality per ¶56; systematic misclassification (e.g., booking country used in lieu of country of risk) is a structural defect requiring remediation | **(¶40, ¶56)**

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The classification of the counterparty or borrower by economic sector or industry — for example, using a standard taxonomy such as NACE, SIC, or GICS, or the bank's own internally approved sector hierarchy. Applied at counterparty level and used to aggregate sector concentration.
- **Why critical:** ¶57 explicitly names industry sector as a required component of credit risk reports. ¶50 gives the supervisory example of aggregating industry credit exposures across all business lines and geographic areas. Sector concentration is a primary lens through which concentration risk is detected.
- **Risk types:** Credit, concentration
- **Criticality: 2.** Total credit aggregates are computable without sector, but the sector-level concentration dimension named in ¶57 and ¶50 cannot be produced. Which slice degrades: industry concentration analysis, and any ad hoc sector query under Principle 6.
- **Driven by:** Principle 8 (¶57) — *"single name, country and industry sector for credit risk"* are named required report components; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines."*

  *Note on dual applicability:* Principle 8 both drives this CDE (by naming industry sector as a required dimension) and imposes report-content obligations that a data catalog cannot satisfy — see Section 4.

- **Search terms:** industry sector, sector code, industry classification, NACE code, SIC code, GICS sector, borrower industry, counterparty sector, economic sector
- **Data quality requirements:**
  - *completeness* — Every credit counterparty record must carry a non-null industry sector code | Count and percentage of counterparty records with null or missing sector classification | Threshold: zero — an unclassified counterparty's exposure is invisible in any sector-level aggregate | **(¶43)**
  - *validity* — Sector codes must be drawn from the bank's approved sector taxonomy | Count of sector codes not matching an approved code in the reference taxonomy | Threshold: zero — non-standard codes cannot be grouped consistently | **(¶40)**
  - *consistency* — The sector classification applied to the same counterparty must be identical across all systems that carry the counterparty (credit, trading, treasury) | Count of counterparties with differing sector codes across systems | Threshold: zero — cross-system inconsistency produces different sector totals depending on which system is queried | **(¶33)**

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The date as of which a risk exposure, position, or balance is stated — the business date for which the data is current. Not the trade date, settlement date, or report production date, though those may coincide with it.
- **Why critical:** Every risk aggregate is defined as of a specific date. Without a reliable as-of date, aggregates from records with different reference dates are mixed, producing a figure that does not correspond to any coherent point in time. Timeliness monitoring (¶44–47) is also impossible without knowing when the data was last valid. ¶50 explicitly requires the ability to aggregate exposures *"as of a specified date."*
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3.** Without a correct as-of date, the aggregate risk figure cannot be stated as of any defined point in time — records from different dates are summed together, producing a figure that is neither yesterday's nor today's and that cannot be reconciled to any source snapshot. Step-2 sentence: *"Without a correct as-of date, the aggregate exposure figure for portfolio X cannot be stated as of any defined date, because records from multiple reference dates are mixed, and no reconciliation to a source snapshot is possible for any given business day."*
- **Driven by:** Principle 5 (¶44–47) — timeliness requires the bank to produce *"aggregate and up-to-date risk data"* and to meet frequency requirements; Principle 6 (¶50) — ad hoc aggregation must be possible *"as of a specified date."*
- **Search terms:** as-of date, position date, value date, reference date, reporting date, business date, snapshot date, effective date, extraction date
- **Data quality requirements:**
  - *completeness* — Every exposure and position record must carry a non-null as-of date | Count of records with a null or missing position date | Threshold: zero — a record without a date cannot be included in or excluded from any date-specific aggregate | **(¶43)**
  - *validity* — As-of dates must be valid business dates and must not be in the future at the time of extract | Count of records with as-of dates that are non-business days or future dates | Threshold: zero — invalid dates cannot be correctly sequenced or compared against timeliness requirements | **(¶40)**
  - *timeliness* — The lag between the as-of date and the availability of the aggregated dataset must meet the bank's defined frequency requirements per risk type, with shorter lags required for critical risks in stress | Count and percentage of risk type/business day combinations where aggregated data is available later than the defined SLA for that risk type | Threshold: zero breaches of the defined SLA — the SLA itself is set by the bank in accordance with ¶45–46, with critical risks (large credit exposures, CCR, trading positions, liquidity indicators) subject to the most demanding cadence | **(¶44–47)**

---

**CDE-09 — General Ledger / Source System Reconciliation Key**

- **Definition:** The identifier — or combination of identifiers — that ties a risk data record back to its corresponding entry in the general ledger or in the authoritative source system of record. This may be a transaction reference, contract identifier, or facility identifier, provided it uniquely identifies the same instrument in both the risk system and the accounting or origination system.
- **Why critical:** ¶36(c) requires risk data to be reconciled with the bank's sources, including accounting data. Without a reconciliation key, the bank cannot evidence that its risk aggregates are complete and accurate relative to the accounting record. An aggregate that cannot be reconciled is not a compliant aggregate, even if it happens to be correct — completeness and accuracy are claims that must be demonstrated, not assumed.
- **Risk types:** Cross-cutting (all risk types — reconciliation is required across all risk categories)
- **Criticality: 3.** Without a reconciliation key, the completeness and accuracy of any risk aggregate cannot be evidenced against the general ledger, which under ¶36(c) is an explicit requirement. An unverifiable figure is not a compliant one. Step-2 sentence: *"Without a reconciliation key linking each risk record to its general ledger entry, the accuracy and completeness of the aggregate credit exposure figure cannot be reconciled to the accounting system of record, which ¶36(c) requires — an unverifiable aggregate is not a compliant one."*
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 3 (¶36(d)) — strive towards a single authoritative source per risk type; Principle 7 (¶53(a)) — *"defined requirements and processes to reconcile reports to risk data."*
- **Search terms:** transaction reference, contract ID, facility ID, deal ID, GL reference, source system key, accounting reference, booking reference, trade ID, reconciliation identifier, source transaction key
- **Data quality requirements:**
  - *completeness* — Every risk record must carry a non-null reconciliation key linking it to the general ledger or source system | Count and percentage of risk records with a null or missing reconciliation key | Threshold: zero — a record without a reconciliation key cannot participate in the GL reconciliation process and its inclusion in any aggregate cannot be verified | **(¶36(c), ¶43)**
  - *uniqueness* — Each reconciliation key must resolve to exactly one instrument in the general ledger or source system (no duplicate keys in the risk dataset for the same GL entry, and no one-to-many mappings that cannot be explained by a defined aggregation rule) | Count of risk records sharing a reconciliation key where the GL carries only one corresponding entry without an approved mapping explanation | Threshold: zero unexplained duplicates — duplicates produce double-counting in the aggregate | **(¶36(c))**
  - *consistency* — The gross exposure amount on each risk record must reconcile to the corresponding balance in the general ledger within the bank's materiality tolerance | Sum of absolute differences between risk system balances and GL balances for matched keys, expressed as a percentage of total portfolio | Threshold: set by the bank's materiality standard per ¶56, formally approved and documented; systematic differences at any single entity or portfolio level must be investigated regardless of aggregate materiality | **(¶36(c), ¶56)**

---

**CDE-10 — Source System / Provenance Flag**

- **Definition:** The identifier or attribute that records the originating source system for each risk data record, and flags whether the data was loaded via an automated feed or entered manually (including end-user computing tools such as spreadsheets or local databases).
- **Why critical:** ¶36(b) and ¶39 require banks to document all aggregation processes, explain manual workarounds, and have effective controls over end-user computing. Without provenance, the bank cannot identify which records are subject to heightened error risk, cannot support the documentation required by ¶39, and cannot demonstrate to supervisors that manual inputs are controlled. It is also the attribute that enables lineage tracing from report back to source.
- **Risk types:** Cross-cutting (governance and control dimension for all risk types)
- **Criticality: 2.** Aggregated figures can be produced without provenance, but the bank cannot demonstrate that the controls required by ¶36(b) apply consistently, cannot produce the documentation required by ¶39, and cannot explain exceptions. Which control degrades: the entire audit trail from report to source, and the evidence base for accuracy claims.
- **Driven by:** Principle 3 (¶36(b)) — *"effective mitigants in place (eg end-user computing policies and procedures)"* for manual processes; Principle 3 (¶39) — *"document and explain all of their risk data aggregation processes whether automated or manual"*; Principle 2 (¶33) — *"information on the characteristics of the data (metadata)"* as part of integrated data architecture.
- **Search terms:** source system, data source, feed name, originating system, manual flag, EUC flag, end-user computing indicator, automated/manual indicator, data lineage, input channel, extract source
- **Data quality requirements:**
  - *completeness* — Every risk record must carry a non-null source system identifier and a populated automated/manual indicator | Count and percentage of risk records with a null source system code or missing manual/automated flag | Threshold: zero — a record without provenance cannot be assessed for control adequacy under ¶36(b) | **(¶43, ¶39)**
  - *validity* — Source system codes must be drawn from the bank's approved source system register | Count of records carrying source system codes not present in the approved register | Threshold: zero — an unregistered source system has no documented controls and is per se non-compliant with ¶36(d) | **(¶40)**
  - *accuracy* — The manual/automated flag must correctly reflect how the data was loaded; manual entries must not be coded as automated | Periodic reconciliation between the flag value and the actual load mechanism as documented in the data lineage register, with the count of mismatches tracked | Threshold: zero — a manual input incorrectly coded as automated bypasses the controls specifically required for manual processes by ¶36(b) | **(¶40, ¶36(b))**

---

**CDE-11 — Collateral Value and Type**

- **Definition:** The current fair value of collateral pledged against an exposure, together with the type of collateral (e.g., cash, government securities, real estate, guarantee). These are the mitigants that reduce net credit exposure in risk calculations and regulatory capital.
- **Why critical:** Credit risk figures reported to senior management and the board are typically net of collateral. An overstated collateral value inflates apparent mitigation and understates true credit risk. ¶58 requires reports to provide information *"in the context of limits and risk appetite/tolerance"* — a figure that excludes or misstates collateral cannot be assessed against a net-exposure limit. Additionally, ¶41 requires completeness including off-balance sheet, and collateral arrangements (particularly over derivatives) are often off-balance sheet in nature.
- **Risk types:** Credit, counterparty credit risk, concentration
- **Criticality: 2.** The gross exposure aggregate (CDE-03) can be produced without collateral data, but net credit exposure — the figure that typically appears in board risk reports and against which limits are set — cannot. Which slice degrades: any report showing net exposure or coverage ratios, and any limit-utilisation calculation.
- **Driven by:** Principle 8 (¶58) — reports should *"provide information in the context of limits and risk appetite/tolerance"*; Principle 4 (¶41) — all material risk exposures including off-balance sheet; Principle 7 (¶52) — reports must *"accurately and precisely convey aggregated risk data and reflect risk in an exact manner."*
- **Search terms:** collateral value, collateral type, security type, haircut, collateral amount, pledge value, margin, LTV (loan-to-value), credit risk mitigant, CRM value, collateral code
- **Data quality requirements:**
  - *accuracy* — Collateral values must reflect current fair value, not stale or unapproved estimates | Count and percentage of collateral records where the valuation date is older than the bank's defined maximum staleness period for each collateral type | Threshold: set by the bank's materiality standard per ¶56, differentiated by collateral type — liquid securities may require near-daily re-valuation while property valuations may have a longer approved cycle | **(¶40, ¶56)**
  - *completeness* — Every exposure record that has documented collateral arrangements must carry at least one linked collateral record | Count of facilities with a legal collateral agreement in the origination system that have no corresponding collateral record in the risk system | Threshold: zero — a missing collateral record causes the gross exposure to be treated as uncollateralised, overstating risk consumption | **(¶43)**
  - *validity* — Collateral type codes must be drawn from the approved collateral type taxonomy | Count of collateral records with unrecognised type codes | Threshold: zero — unrecognised types cannot be correctly haircut or aggregated by collateral category | **(¶40)**

---

**CDE-12 — Limit / Risk Appetite Threshold**

- **Definition:** The approved maximum exposure value — by counterparty, sector, country, business line, or risk type — against which actual exposure aggregates are compared to assess limit utilisation. This includes both hard limits and risk appetite thresholds set by the board or senior management.
- **Why critical:** ¶58 requires reports to provide information *"in the context of limits and risk appetite/tolerance."* A limit value that is stale, incorrectly attributed, or absent from the risk data makes the comparison between actual exposure and approved appetite impossible. Without current, correctly attributed limits, the bank cannot report whether it is operating within its risk tolerance — a core obligation of Principles 7 and 8.
- **Risk types:** Credit, market, liquidity, concentration, cross-cutting
- **Criticality: 2.** Exposure aggregates (CDE-03) can be computed without limits, but the limit-utilisation context that ¶58 requires cannot be reported. Which slice degrades: any report showing headroom, breach status, or risk appetite consumption.
- **Driven by:** Principle 8 (¶58) — *"provide information in the context of limits and risk appetite/tolerance"*; Principle 7 (¶53(b)) — *"automated and manual edit and reasonableness checks"* including validation rules for quantitative information.
- **Search terms:** limit value, credit limit, market risk limit, VaR limit, concentration limit, risk appetite threshold, approved limit, sanctioned limit, utilisation threshold, board-approved limit
- **Data quality requirements:**
  - *accuracy* — Limit values must reflect the most recently board- or senior-management-approved figure, with an auditable approval record | Count of limit records where the current value differs from the most recent approved value in the limit approval system | Threshold: zero — a stale limit produces incorrect utilisation calculations and may mask a breach | **(¶40)**
  - *completeness* — Every dimension for which the bank has a defined risk appetite (counterparty, sector, country, business line) must have a corresponding limit record | Count of approved appetite dimensions with no corresponding limit record in the risk system | Threshold: zero — a dimension with no limit record cannot be monitored for appetite compliance | **(¶43)**
  - *timeliness* — Limit amendments approved by the board or senior management must be reflected in the risk system within the bank's defined implementation SLA | Count of limit records where the date of system update lags the approval date by more than the defined SLA | Threshold: zero breaches of the SLA — a limit that has been raised but not yet updated may allow a true breach to go undetected | **(¶44–47)**

---

## 3. Cross-cutting data quality requirements

---

**XDQ-01 — Cross-system counterparty resolution: single legal entity view**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-04 (Risk Type Classification), CDE-05 (Business Line), CDE-06 (Geography), CDE-07 (Industry Sector)
- **Rule intent:** The bank must be able to aggregate all exposures to a single legal counterparty — across credit, trading, off-balance sheet, and derivatives — into one consolidated view, regardless of which source systems they originate from. This requires that the counterparty identifier on every exposure record in every source system resolves to the same master counterparty record. This is a cross-system property; it cannot be verified by checking any one system in isolation.
- **Measurement:** For each counterparty that appears in more than one source system, compare the counterparty identifier values across systems. Count the number of counterparties where the same legal entity is represented by different identifiers in different systems, with no approved mapping between them. Additionally, for each counterparty with a mapped identifier, compute the total exposure aggregated using the mapping and compare it to the sum of each system's standalone total — unexplained differences indicate that the mapping is incomplete.
- **Threshold:** Zero counterparties with unresolvable identifier conflicts. Mapped but divergent totals are investigated under the materiality standard set per ¶56, but identifier conflicts themselves have no materiality tolerance — a counterparty that cannot be resolved across systems cannot be aggregated at all, regardless of exposure size.
- **Why this threshold:** Identifier integrity is binary. A partially resolvable identifier either joins or it does not; the exposure either enters the aggregate or it does not. Unlike valuation differences, there is no "close enough" for a join key.
- **Authorising paragraphs:** ¶33 — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties"*; ¶46(a) — aggregated credit exposure to a large corporate borrower is a named critical risk; ¶40 — measure and monitor accuracy with escalation channels.

---

**XDQ-02 — Risk-to-finance reconciliation: completeness and accuracy at portfolio level**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key), CDE-02 (Legal Entity Identifier), CDE-08 (Position / As-Of Date)
- **Rule intent:** For each legal entity and as-of date, the total gross exposure captured in the risk aggregation system must reconcile to the total of corresponding balances in the general ledger. This reconciliation must be performed at a defined frequency and must be documented. It cannot be performed by checking any single CDE in isolation — it requires matching populations across the risk system and the GL using CDE-09 as the join key, within the legal entity boundary (CDE-02) for the same as-of date (CDE-08). Unexplained differences are non-compliant regardless of their direction (risk > GL may indicate double-counting; risk < GL may indicate omitted exposures).
- **Measurement:** For each legal entity and as-of date:
  1. Count of GL entries that have no matching record in the risk system — these are omissions from the risk aggregate.
  2. Count of risk records that have no matching GL entry — these may represent risk records without an accounting basis, or valid items not yet settled.
  3. Sum of absolute differences between matched risk record amounts and GL balances, expressed as a percentage of total GL balance for that entity and date.
  
  All three metrics are tracked separately; a small aggregate difference can mask large gross omissions and additions that cancel.

- **Threshold:** Zero unmatched GL entries (items 1 and 2) unless formally explained and approved. The monetary difference (item 3) is assessed against the materiality standard set per ¶56, formally approved by senior management, documented, and reviewed at least annually. *Materiality is not a licence to tolerate known omissions — it is a threshold for investigation priority.* Any single entity or portfolio where the difference is systematic (consistently in the same direction) is treated as a structural defect requiring remediation regardless of magnitude.
- **Why this threshold:** ¶36(c) requires reconciliation to ensure risk data is accurate. ¶56 permits materiality-based precision requirements, but this applies to valuation differences, not to population completeness — a missing counterparty has zero amount in the risk system regardless of its actual size. Item 3's threshold is therefore governed by ¶56; items 1 and 2 have no materiality tolerance.
- **Authorising paragraphs:** ¶36(c) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; ¶53(a) — *"defined requirements and processes to reconcile reports to risk data"*; ¶56 — accuracy requirements analogous to accounting materiality.

---

**XDQ-03 — Manual and EUC input concentration monitoring**

- **CDEs spanned:** CDE-10 (Source System / Provenance Flag), CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key)
- **Rule intent:** The proportion of total risk exposure that flows through manual or end-user computing inputs — rather than automated feeds — must be measured and monitored. A high or growing manual proportion signals aggregation processes that depend on human intervention, which are subject to heightened error risk and require specific controls per ¶36(b). This cannot be measured from any single CDE; it requires combining the provenance flag (CDE-10) with the exposure amount (CDE-03) to compute the manual-input share of total exposure.
- **Measurement:** For each risk type and source system, compute: (i) the count of records flagged as manual or EUC input, and (ii) their associated gross exposure amount, as a percentage of total records and total exposure respectively, for each as-of date. Track trends over time to identify whether reliance on manual processes is increasing or decreasing.
- **Threshold:** No absolute threshold is prescribed — the regulation does not prohibit manual processes. The threshold is the bank's own defined tolerance, set by senior management in the framework approved under ¶27–28, with escalation required when the manual share exceeds that tolerance or trends upward without a documented business reason. Any manual input that contributes to a critical risk aggregate (as defined at ¶46) must have an explicitly documented mitigant per ¶36(b) and ¶39.
- **Why this threshold:** ¶36(b) requires *"effective mitigants in place"* for manual processes — it does not set a maximum proportion, but the mitigant requirement makes it necessary to know the proportion. ¶39 requires all processes to be documented; a process that is not identified as manual cannot be documented as such.
- **Authorising paragraphs:** ¶36(b) — *"effective mitigants in place (eg end-user computing policies and procedures)"*; ¶39 — *"document and explain all of their risk data aggregation processes whether automated or manual"*; ¶40 — measure and monitor accuracy with appropriate escalation.

---

## 4. Out of scope

The following obligations arise from Principles 1–11 but cannot be addressed by a data catalog, a CDE register, or data quality monitoring. Stating this plainly is not a limitation of this analysis — it is what makes the analysis trustworthy. A supervisor who asked whether the catalog "covers BCBS 239" should receive a direct answer that distinguishes what it covers from what requires governance, technology, or operational controls outside metadata management.

---

**Principle 1 — Board governance and senior management accountability (¶27–31)**

A data catalog can publish data ownership assignments (¶34) and document known data quality limitations (¶30) — these are metadata. It cannot constitute the governance framework itself. The board approval of the risk data aggregation and reporting framework (¶28), the allocation of financial and human resources (¶30), and the board's awareness of aggregation limitations (¶31) are organisational governance acts. They require documented board decisions, terms of reference, escalation protocols, and management reporting — not catalog configuration.

---

**Principle 2 — IT architecture and business continuity (¶32–35)**

A catalog can implement ¶33 in part: it is the natural home for integrated data taxonomies, metadata, single identifier standards, and naming conventions. That portion of Principle 2 is addressed in this register (CDE-01, CDE-02, CDE-09). However, the business continuity and business impact analysis requirements of ¶32, and the data ownership and lifecycle controls of ¶34, require IT architecture decisions, BCP plans, RACI frameworks, and data stewardship programmes that operate outside the catalog.

---

**Principle 3 — Automated aggregation and end-user computing controls (¶36–40)**

Data quality monitoring (Section 2 and Section 3 of this document, especially XDQ-02 and XDQ-03) addresses the measurement obligations of ¶40. CDE-09 and CDE-10 address reconciliation and provenance. However, ¶36(a)–(b) require that controls be *in place and operating*, not merely measured. The catalog cannot implement accounting-grade controls over risk data, enforce EUC policies, or remediate identified failures. It can surface them; remediation requires operational process owners and IT controls. ¶37 (the data dictionary requirement) is addressed in part by the catalog's business glossary function, but the organisation-wide agreement on concept definitions is a governance act, not a catalog configuration.

---

**Principle 6 — Adaptability (¶48–51)**

No CDE addresses adaptability directly because adaptability is a system capability, not a data attribute. The ability to *"generate subsets of data based on requested scenarios"* (¶50) and to *"incorporate changes in the regulatory framework"* (¶49(d)) requires flexible aggregation infrastructure and on-demand reporting tools. A catalog can support adaptability by ensuring dimensions are well-governed and documented so that new slices can be added quickly, but the underlying technical capability must exist in the risk systems themselves.

---

**Principle 7 — Report accuracy and validation processes (¶52–56)**

CDE-09 (reconciliation key) and XDQ-02 (risk-to-finance reconciliation) address the data side of ¶53(a) and ¶56. However, ¶53(b) requires an inventory of validation rules with explanations of mathematical and logical relationships, and ¶53(c) requires integrated exception reporting procedures. These are report-production controls — validation rule inventories, exception workflows, sign-off procedures — that belong in the reporting system and its governance framework, not in a data catalog.

---

**Principle 8 — Report comprehensiveness (¶57–60)**

*Dual applicability note:* Principle 8 both drives CDE-07 (Industry/Sector Classification) and CDE-12 (Limit/Risk Appetite Threshold) — because it names industry sector and limit context as required report content, establishing them as data elements the bank must govern — and imposes obligations that no data element can satisfy. The report-content obligations of ¶57–60 — covering all significant risk areas, including emerging concentration identification, forward-looking forecasts, stress test results, and capital projections — are reporting design, analytical, and governance requirements. A catalog that contains well-governed sector and limit data does not thereby produce comprehensive reports; those still require report templates, analytical models, and board-level decisions about risk coverage.

---

**Principle 9 — Report clarity and usefulness (¶61–69)**

¶67 — the requirement to develop an inventory and classification of risk data items linked to report concepts — is partially addressed by a business glossary in a catalog. However, the substance of Principle 9 concerns how information is presented, the balance between quantitative data and qualitative interpretation, tailoring to recipients' needs, and periodic confirmation with recipients that reports remain relevant (¶69). These are communication design and governance obligations that no catalog feature addresses.

---

**Principles 10 and 11 — Report frequency and distribution (¶70–74)**

Report frequency (¶70–71) is a board and senior management decision about how often reports are produced and distributed. CDE-08 (Position/As-Of Date) and its timeliness monitoring measure whether risk data is available on time to support those decisions, but the decision itself, and the stress-testing of report production speed required by ¶70, are operational and governance matters. Report distribution and confidentiality controls (¶72–73) are access management and workflow obligations — they belong in the reporting platform and information security framework, not in a data catalog.

---

## 5. Summary table

| CDE | Name | Criticality | Principles | DQ dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | P2 (¶33), P5 (¶46) | uniqueness, completeness, validity, consistency |
| CDE-02 | Legal Entity Identifier (Booking Entity) | 3 | P1 (¶30), P2 (¶33), P4 (¶41) | completeness, validity, consistency |
| CDE-03 | Gross Exposure Amount | 3 | P3 (¶36a), P4 (¶41), P7 (¶56) | accuracy, completeness, validity |
| CDE-04 | Risk Type Classification | 2 | P4 (¶41), P8 (¶57) | validity, consistency, completeness |
| CDE-05 | Business Line | 2 | P4 (¶41), P8 (¶57) | completeness, validity, consistency |
| CDE-06 | Geography / Country of Risk | 2 | P4 (¶41), P6 (¶50) | completeness, validity, accuracy |
| CDE-07 | Industry / Sector Classification | 2 | P8 (¶57), P6 (¶50) | completeness, validity, consistency |
| CDE-08 | Position / As-Of Date | 3 | P5 (¶44–47), P6 (¶50) | completeness, validity, timeliness |
| CDE-09 | GL / Source System Reconciliation Key | 3 | P3 (¶36c), P7 (¶53a) | completeness, uniqueness, consistency |
| CDE-10 | Source System / Provenance Flag | 2 | P3 (¶36b, ¶39), P2 (¶33) | completeness, validity, accuracy |
| CDE-11 | Collateral Value and Type | 2 | P4 (¶41), P8 (¶58), P7 (¶52) | accuracy, completeness, validity |
| CDE-12 | Limit / Risk Appetite Threshold | 2 | P8 (¶58), P7 (¶53b) | accuracy, completeness, timeliness |
| XDQ-01 | Cross-system counterparty resolution | — | P2 (¶33), P5 (¶46), P3 (¶40) | uniqueness, consistency |
| XDQ-02 | Risk-to-finance reconciliation | — | P3 (¶36c), P7 (¶53a), P7 (¶56) | completeness, accuracy, consistency |
| XDQ-03 | Manual/EUC input concentration monitoring | — | P3 (¶36b, ¶39), P3 (¶40) | completeness, accuracy |

**Criticality distribution:** 5 elements at criticality 3 (CDE-01, CDE-02, CDE-03, CDE-08, CDE-09); 7 elements at criticality 2 (CDE-04 through CDE-07, CDE-10 through CDE-12); 0 elements at criticality 1. No element was assessed as a 1 because every element in this register either invalidates an aggregate figure if wrong (3) or makes a required slice, reconciliation, or control evidence unavailable (2). An element that is merely descriptive or contextual would qualify as a 1, but no such element met the CDE inclusion criteria.