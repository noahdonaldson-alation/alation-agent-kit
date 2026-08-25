# BCBS 239 — Data Catalog Interpretation: What to Build and Govern

---

## 1. Objectives and scope

**What the regulation is trying to achieve**

- **Reliable aggregation as a precondition for sound governance.** The regulation requires that a bank can assemble a complete, accurate, and timely picture of its risk exposures across the entire group — not just within a single system or business line — so that boards and senior management have information they can actually rely on for critical decisions. (¶35: *"banks should develop and maintain strong risk data aggregation capabilities to ensure that risk management reports reflect the risks in a reliable way"*; ¶52.)

- **Data quality is not optional and must be evidenced.** Accuracy, completeness, and timeliness must be *measured and monitored*, with escalation channels and remediation plans in place. Self-attestation is insufficient; the regulation expects banks to be able to demonstrate compliance. (¶40: *"Supervisors expect banks to measure and monitor the accuracy of data and to develop appropriate escalation channels and action plans to be in place to rectify poor data quality."*; ¶43.)

- **A single authoritative source per risk type, with reconciliation to accounting.** Risk data must be reconciled to accounting and source systems, and banks should strive toward one authoritative source per risk type. This closes the gap between what the risk function sees and what the books say. (¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*; ¶36(d).)

- **Integrated data architecture, not siloed systems.** The bank must establish integrated taxonomies and architecture across the banking *group*, using single identifiers and unified naming conventions for legal entities, counterparties, customers, and accounts — so that exposures can be joined and aggregated across systems. (¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*)

- **Transparency about manual processes and provenance.** All aggregation processes, whether automated or manual, must be documented. Where manual workarounds exist, their criticality and proposed remediation must be recorded. This directly creates the obligation to track source and process provenance at the data element level. (¶39: *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual."*; ¶36(b).)

- **Adaptability to stress, ad hoc requests, and regulatory change.** Risk data architecture must support not only routine reporting but also rapid aggregation under stress, supervisor queries, and scenarios. The data must be sliceable by business line, legal entity, geography, asset type, and industry on demand — without rebuilding the data model each time. (¶48–50; ¶4 Principle heading.)

**Who and what it applies to**

Principles 1–11 apply to *banks* — specifically to Global Systemically Important Banks (G-SIBs) as of the publication date, with the Basel Committee signalling broader applicability over time. The obligations fall on the bank as a whole: board, senior management, risk, IT, and finance functions collectively. The data catalog obligation falls on whichever function owns data governance implementation, typically the Chief Data Officer or equivalent, operating under board-approved frameworks per ¶28.

---

## 2. Critical Data Element candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** The unique, enterprise-wide identifier assigned to each counterparty (borrower, derivative counterparty, issuer, or guarantor) that is consistent across all systems where that counterparty appears — origination, trading, collateral, and risk. It is system-independent: the concept is "one code per counterparty, used everywhere."
- **Why critical:** Without a single resolvable counterparty identifier, exposures held in different systems cannot be joined. An aggregated credit or counterparty exposure figure cannot be produced at all — separate records for the same counterparty cannot be recognised as the same. The regulation requires aggregation across legal entities, business lines, and geographies (¶4 principle heading; ¶46(b)); that is arithmetically impossible if the joining key is absent or duplicated.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3.** *Without this element, the aggregate credit or counterparty exposure to a single counterparty cannot be computed at all, because records in different source systems cannot be identified as belonging to the same counterparty and therefore cannot be summed.*
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*
- **Search terms:** counterparty ID, counterparty code, obligor ID, legal entity identifier (LEI), client identifier, party ID, global counterparty identifier, GCID, counterparty master
- **Data quality requirements:**
  - *uniqueness* — Every counterparty record in the enterprise counterparty master must have exactly one identifier; no two distinct counterparties may share the same code | count of duplicate identifier values in the counterparty master; count of counterparty records without any identifier | threshold: zero — a duplicate or null identifier always produces a wrong aggregate, with no materiality defence possible | **(¶33)**
  - *consistency* — The counterparty identifier used on each exposure record must resolve to a record in the enterprise counterparty master | count of exposure records carrying a counterparty identifier not present in the master reference table | threshold: zero — an unresolvable identifier means the exposure is excluded from all counterparty-level aggregations without warning | **(¶33, ¶40)**
  - *completeness* — Every exposure record must carry a populated counterparty identifier | count of exposure records where the counterparty identifier field is null or blank | threshold: zero — a null means the exposure is silently excluded from aggregation | **(¶43)**

---

**CDE-02 — Legal Entity Identifier (Own Bank)**

- **Definition:** The identifier of the bank's own booking entity — the specific regulated legal entity within the banking group in which a transaction or position is recorded. This is distinct from the counterparty identifier; it identifies *which entity of the bank* holds the exposure, not who the exposure is with.
- **Why critical:** Group consolidation and subsidiary-level reporting both require the ability to assign every exposure record to a specific legal entity of the bank, then roll up correctly. If this identifier is missing or inconsistent, consolidation produces double-counts or omissions, and subsidiary reports cannot be separated from group totals. ¶33 requires unified naming conventions for legal entities; ¶4's completeness requirement demands data be available *by legal entity*.
- **Risk types:** Cross-cutting (applies to all risk types at group level), concentration
- **Criticality: 3.** *Without this element, the aggregate exposure of any specific subsidiary or consolidated group entity cannot be computed at all, because records cannot be attributed to the correct booking entity and therefore cannot be correctly consolidated or separated.*
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (¶4 principle heading) — *"data should be available by business line, legal entity, asset type, industry, region"*
- **Search terms:** legal entity ID, booking entity code, entity identifier, subsidiary code, LEI (own entity), organisational unit code, booking entity reference, company code
- **Data quality requirements:**
  - *uniqueness* — Each distinct legal entity of the banking group must be represented by exactly one identifier code; no entity may have multiple active codes | count of legal entity master records that share an identifier, or entities with more than one active code | threshold: zero — duplicate entity codes cause double-counting in consolidation, which is always an error | **(¶33)**
  - *completeness* — Every exposure, position, and transaction record must carry a populated legal entity identifier | count of records where the legal entity identifier is null | threshold: zero — an unattributed exposure cannot be included in any entity-level aggregate | **(¶43)**
  - *validity* — The legal entity identifier on each record must match a currently active entry in the legal entity reference master | count of records carrying a legal entity code not present or not active in the reference master | threshold: zero — an invalid code means the record is excluded from group reporting without audit trail | **(¶33, ¶40)**

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary amount representing the bank's risk exposure before any credit risk mitigation (collateral, guarantees, netting). For loans: outstanding principal balance. For derivatives: current mark-to-market exposure or replacement cost. For securities: market value or notional. The exact metric varies by risk type; the CDE is the pre-mitigation monetary measure from which risk figures are constructed.
- **Why critical:** This is the quantity being aggregated. Every risk report ultimately reports a sum, average, or function of this amount. If it is wrong, the aggregate risk figure is arithmetically wrong. No other CDE can compensate for an incorrect exposure amount; it is the operand, not the key.
- **Risk types:** Credit, counterparty credit, market, concentration, liquidity
- **Criticality: 3.** *Without this element, no aggregate risk exposure figure can be computed at all, because there is no monetary quantity to sum across counterparties, entities, or dimensions.*
- **Driven by:** Principle 3 (¶36) — *"A bank should aggregate risk data in a way that is accurate and reliable"*; Principle 7 (¶52) — *"Risk management reports should be accurate and precise"*; Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*
- **Search terms:** exposure amount, outstanding balance, current exposure, replacement cost, market value, notional amount, drawn amount, EAD (exposure at default), gross exposure, position value, mark-to-market
- **Data quality requirements:**
  - *accuracy* — The exposure amount on each risk record must reconcile to the corresponding balance in the system of record (general ledger or front-office system) within the bank's materiality tolerance | sum of absolute differences between risk system exposure amounts and system-of-record balances, expressed as a percentage of total portfolio | threshold: set by the bank's materiality framework per ¶56, not zero — the regulation explicitly analogises accuracy requirements to accounting materiality; the risk and finance functions jointly set the tolerance and must be able to support the rationale | **(¶36(c), ¶56)**
  - *completeness* — Every in-scope exposure, including off-balance-sheet items, must carry a populated, non-zero-where-material exposure amount | count and aggregate value of exposure records with null, zero, or negative amounts where a positive balance is expected | threshold: assessed against materiality per ¶56 — the impact of any incomplete population must not be critical to the bank's ability to manage risk; the threshold is set by the risk and finance functions | **(¶41, ¶43)**
  - *validity* — Exposure amounts must be in a known, recorded currency and must not be negative except where a negative exposure is a valid risk position (e.g., protection sold) | count of records with null currency code, or negative amounts in contexts where negative exposure is not permitted by product type | threshold: zero for null currency; any negative-where-invalid amount is a defect | **(¶40)**

---

**CDE-04 — Risk Type Classification**

- **Definition:** The classification code that assigns each exposure or position to a risk category — at minimum: credit risk, market risk, liquidity risk, operational risk. May be further subdivided (e.g., counterparty credit risk, interest rate risk in the banking book). This is the primary taxonomy that determines which aggregations and reports an exposure feeds into.
- **Why critical:** Risk reports are organised by risk type (¶57). An exposure with the wrong risk type classification feeds into the wrong report and is absent from the correct one. The aggregate for each risk type is wrong in both directions — overstated in the wrong category, understated in the correct one.
- **Risk types:** Cross-cutting (the classification applies to all risk types)
- **Criticality: 2.** A risk figure is produced, but it is partitioned incorrectly: the credit risk total is understated and market risk is overstated, or vice versa. The aggregate across all risk types may still be arithmetically correct, so the figure is not wholly invalid — but it cannot be trusted by risk type, which is how it is used.
- **Driven by:** Principle 7 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 2 (¶33) — *"A bank should establish integrated data taxonomies and architecture"*
- **Search terms:** risk type, risk category, risk class, risk taxonomy, risk classification, risk flag, asset class code, risk bucket
- **Data quality requirements:**
  - *validity* — Every exposure or position record must carry a risk type classification that belongs to the bank's approved risk taxonomy | count of records where the risk type code is null, blank, or not present in the approved taxonomy reference list | threshold: zero — any unclassified exposure is excluded from all risk-type reports silently | **(¶33, ¶40)**
  - *completeness* — All in-scope exposure records must have a populated risk type | count of records with null risk type | threshold: zero — a missing classification means the exposure appears in no risk-type aggregate | **(¶43)**
  - *consistency* — The same product or instrument type must receive the same risk type classification across all source systems | count of instrument types that carry more than one active risk type code across systems | threshold: zero — inconsistency means the same exposure may be double-counted or excluded depending on the system queried | **(¶33)**

---

**CDE-05 — Business Line**

- **Definition:** The internal organisational unit or business line to which an exposure or position is attributed — for example: retail banking, corporate banking, trading, wealth management, treasury. The specific taxonomy is bank-defined, but it must be consistent and stable enough to support reporting.
- **Why critical:** Principle 4 explicitly requires that risk data be available *by business line* (¶4 principle heading). Principle 8 requires that risk reports cover all material risk areas, and ¶59 expects aggregated reports to permit comparison across group institutions. Without a business line dimension, supervisors cannot determine whether a concentration is driven by one part of the bank or is spread across the group.
- **Risk types:** Cross-cutting, concentration
- **Criticality: 2.** A total exposure figure can be produced without business line, but it cannot be sliced by business line as Principle 4 requires. The aggregate is not invalid — it is unsliceable, which means the completeness and adaptability requirements (¶43, ¶48–50) cannot be met for this dimension.
- **Driven by:** Principle 4 (¶4 principle heading) — *"Data should be available by business line, legal entity, asset type, industry, region"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries, as well as industry credit exposures as of a specified date based on a list of industry types across all business lines"*
- **Search terms:** business line, line of business, business unit, segment, division, desk, product line, P&L unit, cost centre (as a proxy)
- **Data quality requirements:**
  - *completeness* — Every exposure and position record must carry a populated business line code | count of records with null or blank business line | threshold: zero — a record without a business line cannot be included in any business-line aggregate | **(¶43)**
  - *validity* — Business line codes must be drawn from an approved, current reference list | count of records carrying business line codes not present in the approved reference | threshold: zero — invalid codes produce phantom categories in reports | **(¶40)**
  - *consistency* — Each business line code must have a single, stable definition used consistently across source systems | count of business line codes with differing definitions across systems, as identified during data integration or lineage review | threshold: zero — inconsistent definitions make cross-system aggregation by business line unreliable | **(¶33)**

---

**CDE-06 — Geography / Country**

- **Definition:** The country or jurisdiction to which the exposure is attributed for risk reporting purposes — typically the country of the borrower's domicile, the country of the obligor, or the country of risk as defined by the bank's credit risk methodology. Distinct from the currency of the exposure or the booking location.
- **Why critical:** Principle 4 requires data to be available by region; ¶50 gives as a concrete supervisory expectation the ability to *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries."* Country/geography is also the dimension against which geopolitical and sovereign concentration risks are assessed (Principle 8, ¶57). Without it, the bank cannot respond to a supervisor query about exposure to a specific country or region.
- **Risk types:** Credit, market, concentration, liquidity
- **Criticality: 2.** A total exposure figure exists, but it cannot be sliced by country as Principle 4 and ¶50 require. The adaptability requirement (Principle 6) also fails: the bank cannot produce country-level aggregates on demand.
- **Driven by:** Principle 4 (¶4 principle heading) — *"Data should be available by … region"*; Principle 6 (¶50) — *"a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*
- **Search terms:** country of risk, country code, domicile country, obligor country, booking country, jurisdiction, region, geographic segment, ISO country code
- **Data quality requirements:**
  - *completeness* — Every credit and counterparty exposure record must carry a populated country-of-risk code | count of records with null or blank country code | threshold: zero — an unattributed exposure is excluded from all geographic aggregations | **(¶43)**
  - *validity* — Country codes must conform to the bank's approved geographic reference (typically ISO 3166-1 or an internal mapping to it) | count of records with country codes not present in the approved reference | threshold: zero — invalid codes cannot be aggregated into regions or matched against supervisory country lists | **(¶40)**
  - *consistency* — The country-of-risk assignment methodology must be applied consistently across business lines and source systems | count of instruments where country-of-risk assignment differs between two or more source systems for the same exposure | threshold: zero — inconsistency means geographic aggregates differ depending on which system is queried | **(¶33)**

---

**CDE-07 — Industry / Sector**

- **Definition:** The industry or economic sector classification of the borrower or counterparty — for example using a standard scheme such as NACE, SIC, GICS, or an internal equivalent. Applied at the counterparty or obligor level, not the instrument level.
- **Why critical:** ¶50 names industry as a required aggregation dimension explicitly: *"industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas."* ¶57 requires reports to include *"single name, country and industry sector for credit risk."* Sector concentrations are a key supervisory concern; without a consistent sector code, concentration risk by industry cannot be measured.
- **Risk types:** Credit, concentration
- **Criticality: 2.** A total credit exposure figure can be produced without industry, but sector-level aggregations — which the regulation explicitly names as required — cannot be produced. The figure is not invalid, but the bank cannot demonstrate compliance with the completeness and adaptability requirements for this dimension.
- **Driven by:** Principle 4 (¶4 principle heading) — *"Data should be available by … industry"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines"*; Principle 8 (¶57) — *"single name, country and industry sector for credit risk"*
- **Search terms:** industry code, sector code, industry classification, NACE code, SIC code, GICS, economic sector, borrower sector, obligor industry
- **Data quality requirements:**
  - *completeness* — Every counterparty or obligor record used in credit risk reporting must carry a populated industry/sector code | count of counterparty records with null or blank sector code | threshold: industry completeness is assessed against materiality — the impact of gaps on sector-level concentration measures must not be critical per ¶43; the risk function sets the materiality threshold | **(¶43)**
  - *validity* — Industry codes must be drawn from an approved classification scheme and must be current | count of records with codes not present in the approved scheme or marked as deprecated | threshold: zero for invalid codes — they cannot be included in any sector aggregate | **(¶40)**
  - *consistency* — The same counterparty must carry the same industry classification across all systems in which it appears | count of counterparties with differing sector codes across systems | threshold: zero — inconsistency means the same counterparty's exposure is split across different sectors depending on the source, distorting concentration measures | **(¶33)**

---

**CDE-08 — Position / As-of Date**

- **Definition:** The business date as of which an exposure, position, or balance is stated. Not the transaction date or the processing date — the date the snapshot of risk is valid for. Every aggregate risk figure is implicitly or explicitly a function of this date.
- **Why critical:** Every aggregated risk figure is stated *as of* a date. Without a reliable as-of date, the bank cannot confirm that all components of an aggregate are drawn from the same snapshot, cannot produce reports as of a specified date on demand (¶50), and cannot demonstrate timeliness compliance (¶44–47). Mixing records from different as-of dates in a single aggregate produces a figure that is neither accurate nor complete.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality: 3.** *Without this element, the aggregate exposure figure cannot be verified to represent a consistent point-in-time snapshot: records from different dates may be silently mixed, producing an aggregate that is neither accurate nor reconcilable to any specific date, which under ¶36(c) and ¶52 is an equivalent failure.*
- **Driven by:** Principle 5 (¶44–47) — *"A bank's risk data aggregation capabilities should ensure that it is able to produce aggregate risk information on a timely basis"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (¶52–53)
- **Search terms:** as-of date, position date, valuation date, snapshot date, reference date, reporting date, business date, effective date
- **Data quality requirements:**
  - *completeness* — Every exposure and position record must carry a populated as-of date | count of records with null or blank as-of date | threshold: zero — a record without a date cannot be assigned to any reporting snapshot | **(¶43, ¶44)**
  - *validity* — As-of dates must be valid calendar dates and must fall within the expected range for the reporting cycle (not in the future; not before the bank existed) | count of records with as-of dates outside the expected reporting window | threshold: zero — an invalid date means the record cannot be included in a time-consistent aggregate | **(¶40)**
  - *timeliness* — Risk data for each risk type must be available and complete as of the required as-of date within the bank's agreed production window for that risk type (which is shorter for market and counterparty credit risk under stress, longer for credit and operational risk in normal conditions) | elapsed time from business-date close to availability of complete risk dataset for each risk type, measured against the bank's agreed SLA | threshold: set by risk type per ¶45 — market and intraday positions faster than credit; stress windows shorter than normal windows; the specific SLA is set by the bank's board/senior management per ¶55 and reviewed by supervisors per ¶47 | **(¶44–47)**

---

**CDE-09 — General Ledger / System-of-Record Reconciliation Key**

- **Definition:** The identifier — typically an account number, transaction reference, or instrument identifier — that links a risk record to the corresponding entry in the general ledger (GL) or primary system of record. It is the join key used to perform the reconciliation that ¶36(c) requires. It is not the exposure amount itself; it is the reference that makes the exposure amount verifiable.
- **Why critical:** ¶36(c) states that *"risk data should be reconciled with bank's sources, including accounting data where appropriate."* Without this key, reconciliation cannot be performed mechanically or evidenced to a supervisor. A risk figure that cannot be reconciled to the GL is unverifiable — and an unverifiable figure is not a compliant one under ¶36(c). This is the element most commonly absent from data registers and most directly named by the regulation.
- **Risk types:** Cross-cutting (all risk types where accounting reconciliation applies — primarily credit, market, and liquidity)
- **Criticality: 3.** *Without this element, the aggregate risk exposure figure cannot be reconciled to the general ledger or system of record at all, because there is no key with which to join the risk record to the accounting entry; compliance with ¶36(c) cannot be evidenced, and an unverifiable figure is not a compliant aggregate.*
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** GL account number, general ledger account, system of record reference, source system transaction ID, instrument reference, trade ID (as GL key), account code, booking reference, ledger entry reference
- **Data quality requirements:**
  - *completeness* — Every in-scope risk record must carry a populated GL/system-of-record reconciliation key | count of risk records with null or blank reconciliation key | threshold: zero — a missing key means the record cannot be individually reconciled, even if the aggregate appears to balance | **(¶36(c), ¶43)**
  - *consistency* — The reconciliation key on each risk record must match a corresponding entry in the GL or system of record | count of risk records whose reconciliation key does not resolve to a GL entry; net difference between total risk exposure amount and total GL balance for reconciled records | threshold: the net difference is assessed against the bank's materiality framework per ¶56 — a zero target is appropriate for key matching; a materiality tolerance applies to value differences; both thresholds are set jointly by risk and finance | **(¶36(c), ¶56)**
  - *accuracy* — For records that do reconcile, the exposure amount in the risk system must equal the balance in the GL (or differences must be explained and within tolerance) | sum of unexplained differences between risk system amounts and GL amounts for matched records | threshold: materiality per ¶56 — unexplained differences above materiality are escalation triggers; the risk and finance functions set and review the tolerance | **(¶36(c), ¶40, ¶56)**

---

**CDE-10 — Source System / Provenance Flag**

- **Definition:** The identifier of the system from which each risk record originated — for example: loan origination system, trading system, collateral management system — together with a flag indicating whether the data was delivered by automated feed or entered manually (including end-user computing tools such as spreadsheets). These are two facets of the same provenance concept; both are required by the regulation.
- **Why critical:** ¶36(b) requires that where manual processes and desktop applications are used, effective mitigants and controls must be *consistently applied*. ¶39 requires banks to *document and explain all of their risk data aggregation processes whether automated or manual*, including the criticality of manual workarounds. Without a provenance flag, the bank cannot identify which records passed through manual processes, cannot apply differentiated controls, and cannot report the extent of manual intervention to management or supervisors. ¶36(d) drives the complementary need for a single authoritative source per risk type — which requires knowing what the source is.
- **Risk types:** Cross-cutting
- **Criticality: 2.** Aggregate risk figures are produced regardless of whether provenance is captured. However, without it: (a) manual-process controls required by ¶36(b) and ¶39 cannot be demonstrably applied to the right records; (b) data lineage required by ¶29(a) cannot be traced; (c) the distinction between authoritative-source data and supplementary data (¶36(d)) cannot be enforced. The aggregate is produced but cannot be quality-assured by source or process type.
- **Driven by:** Principle 3 (¶36(b)) — *"Where a bank relies on manual processes and desktop applications … it should have effective mitigants in place"*; Principle 3 (¶36(d)) — *"A bank should strive towards a single authoritative source for risk data per each type of risk"*; Principle 3 (¶39) — *"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual"*
- **Search terms:** source system, originating system, system of origin, feed source, data source code, manual entry flag, EUC flag, end-user computing indicator, automated feed indicator, upstream system, pipeline name
- **Data quality requirements:**
  - *completeness* — Every risk record must carry a populated source system identifier and a populated manual/automated indicator | count of records with null source system code or null manual/automated flag | threshold: zero — an unattributed record cannot be subject to source-specific controls or documented per ¶39 | **(¶39, ¶43)**
  - *validity* — Source system codes must be drawn from the bank's approved system inventory; the manual/automated flag must be drawn from an approved value set (e.g., "automated", "manual", "EUC") | count of records with source codes not in the system inventory, or flag values outside the approved set | threshold: zero — an unknown source code cannot be traced in lineage reviews | **(¶40)**
  - *accuracy* — The manual/automated flag must correctly reflect the actual processing path of the record (i.e., records processed through a spreadsheet or manual workaround must be flagged accordingly) | count of records flagged as automated whose lineage trace shows manual intervention; identified through periodic lineage audit against ¶39 documentation | threshold: zero — a misclassified flag defeats the control regime for manual processes required by ¶36(b); the audit cadence is set by the bank's governance framework under ¶28 | **(¶36(b), ¶40)**

---

**CDE-11 — Collateral / Credit Risk Mitigant Amount**

- **Definition:** The monetary value of credit risk mitigation recognised against an exposure — physical collateral, financial collateral, guarantees, or credit protection — used to compute net or post-mitigation exposure. Recorded at the instrument or facility level before aggregation.
- **Why critical:** Risk reports distinguish between gross and net exposure (¶57 requires position information for all significant risk areas; ¶58 references risk appetite and limits monitoring). Net exposure is the operative risk figure for credit risk management and capital adequacy. If collateral values are wrong or missing, net exposure is wrong — the bank may appear better-capitalised or less concentrated than it is. ¶41 requires off-balance-sheet items to be captured; many off-balance-sheet exposures (e.g., unfunded commitments backed by collateral) depend on collateral values for correct risk measurement.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 2.** The gross exposure figure (CDE-03) is still computable; a risk figure exists. However, the net exposure figure — which is what feeds capital adequacy and credit risk reports — is wrong or cannot be derived. The aggregate is produced but materially misleading for credit risk management purposes.
- **Driven by:** Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 7 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas"*; Principle 8 (¶58) — *"Reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance"*
- **Search terms:** collateral value, collateral amount, LGD collateral, recovery value, guarantee amount, credit protection value, CRM amount, net exposure, post-mitigation exposure, collateral haircut
- **Data quality requirements:**
  - *accuracy* — Collateral valuations must be current (re-valued at the frequency required by the bank's credit risk policy, which must align with the volatility of the collateral type) and must reconcile to the collateral management system | count of collateral records whose last valuation date exceeds the bank's re-valuation frequency threshold; sum of differences between risk system collateral values and collateral management system values | threshold for staleness: set by collateral type and risk policy (e.g., daily for liquid financial collateral; periodic for real estate) per ¶45's recognition that different data requires different speeds; threshold for value difference: materiality per ¶56 | **(¶36(c), ¶45, ¶56)**
  - *completeness* — Every exposure record where collateral is held must reference a collateral record | count of exposure records flagged as collateralised but with no linked collateral record; count of collateral records with no linked exposure | threshold: assessed against materiality per ¶43 — gaps that are individually immaterial may be material in aggregate, so the risk function monitors both record count and aggregate value | **(¶41, ¶43)**
  - *validity* — Collateral type codes must be drawn from the approved CRM classification (to ensure eligibility rules can be applied consistently) | count of collateral records with type codes outside the approved reference | threshold: zero — an unclassified collateral item cannot have eligibility or haircut applied, so the net exposure calculation is incorrect | **(¶40)**

---

**CDE-12 — Limit / Risk Appetite Threshold**

- **Definition:** The approved monetary or ratio limit assigned to a counterparty, business line, geography, sector, or portfolio — against which current exposure is monitored. Includes both internal risk appetite limits and regulatory limits where they are operationalised in data. The limit is associated with the same dimensions as the exposure it constrains (counterparty ID, legal entity, risk type, geography).
- **Why critical:** ¶58 requires reports to *"provide information in the context of limits and risk appetite/tolerance."* ¶46(c) names *"operating limits"* as a critical risk data item requiring rapid availability under stress. Without the limit value as a data element, the bank cannot produce utilisation figures (exposure as a percentage of limit), cannot identify breaches, and cannot populate the limit-context information that risk reports must include. The limit is also essential for concentration risk monitoring.
- **Risk types:** Credit, market, liquidity, counterparty, concentration
- **Criticality: 2.** Exposure aggregates can be computed without limit data. However, the report content required by ¶58 — specifically the presentation of exposure in the context of limits — cannot be produced, and limit-breach monitoring fails entirely. This degrades report comprehensiveness and risk management effectiveness but does not make the underlying exposure figure arithmetically wrong.
- **Driven by:** Principle 8 (¶58) — *"Reports should identify emerging risk concentrations, provide information in the context of limits and risk appetite/tolerance"*; Principle 5 (¶46(c)) — *"Trading exposures, positions, operating limits, and market concentrations by sector and region data"*
- **Search terms:** credit limit, exposure limit, risk limit, counterparty limit, concentration limit, risk appetite threshold, limit amount, limit utilisation, approved limit, facility limit
- **Data quality requirements:**
  - *accuracy* — Limit values in the risk data system must match the most recently board- or committee-approved limit for each limit dimension | count of limit records where the value in the risk system differs from the approved limit in the limit management or credit approval system | threshold: zero — a stale or incorrect limit value produces wrong utilisation calculations and may mask a real breach | **(¶40, ¶53(a))**
  - *completeness* — Every combination of risk dimension for which a limit has been approved (counterparty, entity, geography, sector, portfolio) must have a corresponding limit record in the risk data system | count of approved limits with no corresponding record in the risk system | threshold: zero — a missing limit means breaches cannot be detected for that dimension | **(¶43, ¶58)**
  - *timeliness* — Limit changes approved by the relevant authority must be reflected in the risk data system within the bank's agreed governance cycle | elapsed time between limit approval date and update date in the risk system, measured against the bank's agreed SLA | threshold: set by the bank's governance framework — the regulation does not specify a number, but ¶46(c) implies limits must be current for stress reporting; the SLA is set by the board/senior management per ¶28 | **(¶44–47)**

---

## 3. Cross-cutting data quality requirements

---

**XDQ-01 — Counterparty consolidation: resolving one entity across all source systems**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key)
- **Rule intent:** The total exposure to a single counterparty must be aggregated correctly across every system in which that counterparty appears — loan origination, trading, collateral management, treasury — using a single enterprise-wide counterparty identifier. Where source systems use local or legacy identifiers, a mapping to the enterprise master must exist and be current. The absence of this mapping means the same counterparty appears as multiple distinct entities, and the aggregate exposure is understated (concentration risk is invisible) even when the individual CDE-01 fields within each system are populated and valid.
- **Why this cannot be expressed as a single-element check:** The defect is in the *relationship* between identifiers across systems, not in any one identifier field. A system-level check on CDE-01 will pass in every system individually; the failure only appears when systems are compared.
- **Dimension:** *consistency*
- **Measurement:** Count of counterparties appearing in more than one source system where no enterprise identifier mapping exists; count of source-system identifiers that are not mapped to any record in the enterprise counterparty master; total exposure value carried by unmapped records (to assess materiality of the gap)
- **Threshold and justification:** Zero unmapped records is the target for identifier integrity — a null or unresolvable mapping is always a defect with no materiality defence, because any unmapped exposure is silently excluded from the consolidated counterparty total. The materiality framework per ¶56 applies to the *residual* value of exposures where mapping is contested or being remediated, not to the existence of mappings.
- **Paragraph citations:** ¶33 (*"use of single identifiers and/or unified naming conventions for data including … counterparties"*); ¶36(c) (reconciliation to sources); ¶40 (monitoring mandate)

---

**XDQ-02 — Risk-to-finance reconciliation: evidencing that risk aggregates tie to the general ledger**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-08 (As-of Date), CDE-09 (GL Reconciliation Key), CDE-02 (Legal Entity Identifier)
- **Rule intent:** The total risk exposure as reported by the risk function must be reconcilable to the corresponding balance reported by the finance/accounting function for the same legal entity, as of the same date. The reconciliation operates by joining CDE-09 (the GL key) across the risk and finance data stores, grouping by CDE-02 (legal entity) and CDE-08 (as-of date), and comparing the sum of CDE-03 (exposure amount) on each side. Where differences exist, they must be explained: either the difference is within the bank's materiality tolerance (set per ¶56), or there is an identified reconciling item (scope difference, valuation timing) that is documented and reported. An unexplained difference above materiality is a compliance failure.
- **Why this cannot be expressed as a single-element check:** The reconciliation is a *cross-system join* that requires all four CDEs to be populated, consistent, and correctly valued simultaneously. Monitoring any single CDE does not detect a net reconciling difference. The check only exists at the aggregate level, spanning risk and finance data stores.
- **Dimension:** *consistency* (cross-system agreement), *accuracy* (values match within tolerance)
- **Measurement:** Net difference between total risk exposure (sum of CDE-03 by legal entity and as-of date in the risk system) and total balance (sum of corresponding amounts in the GL for the same scope, entity, and date); count of reconciling items; age of unresolved reconciling items
- **Threshold and justification:** The value difference threshold is set by the bank's materiality framework, which the regulation explicitly analogises to accounting materiality (¶56: *"if omission or misstatement could influence the risk decisions of users, this may be considered material"*). The risk and finance functions jointly define and document the tolerance; it is reviewed by the board/senior management per ¶55 and subject to independent validation per ¶29(a). The count of unresolved reconciling items above materiality has a threshold of zero — every material difference must have an explanation and an action plan per ¶40.
- **Paragraph citations:** ¶36(c) (*"Risk data should be reconciled with bank's sources, including accounting data where appropriate"*); ¶53(a) (*"Defined requirements and processes to reconcile reports to risk data"*); ¶56 (materiality analogy); ¶40 (monitoring mandate and escalation)

---

**XDQ-03 — Provenance-stratified completeness: confirming that manual and EUC records meet the same completeness standards as automated records**

- **CDEs spanned:** CDE-10 (Source System / Provenance Flag), CDE-03 (Gross Exposure Amount), CDE-01 (Counterparty Identifier), CDE-09 (GL Reconciliation Key)
- **Rule intent:** ¶36(b) requires that where manual processes and end-user computing (EUC) tools are used, effective controls must be *consistently applied*. ¶39 requires documentation of the criticality of manual workarounds. This cross-cutting check stratifies the standard completeness and accuracy checks on CDE-01, CDE-03, and CDE-09 by the CDE-10 provenance flag, and compares defect rates between automated-feed records and manual/EUC records. The expected finding is that manual/EUC records have a materially higher defect rate; this is not automatically a compliance failure, but it must be measured, documented, and managed. Where the defect rate in manual records is unacceptably high, escalation and remediation plans must exist per ¶40.
- **Why this cannot be expressed as a single-element check:** The analysis requires two dimensions simultaneously — the quality dimension (completeness/accuracy of CDE-01, CDE-03, CDE-09) *and* the provenance dimension (CDE-10). Neither dimension alone surfaces the compliance gap; only the cross-tabulation does.
- **Dimension:** *completeness*, *accuracy* (stratified by provenance)
- **Measurement:** For CDE-01, CDE-03, and CDE-09 separately: null/defect rate in records flagged "automated" versus records flagged "manual" or "EUC"; count of manual/EUC records that lack an approved mitigant control documented per ¶36(b); count of manual workarounds without a documented remediation plan per ¶39
- **Threshold and justification:** The null/defect rate in automated records is the baseline; manual/EUC defect rates must not exceed the level at which manual records' inaccuracies become material to any aggregated risk figure (threshold set per ¶56 by risk and finance). The count of manual workarounds without documented mitigants has a threshold of zero — the regulation requires controls to be *in place* (¶36(b)), and absence of documentation means absence of the required control. The remediation-plan count also has a threshold of zero for material manual processes, per ¶39.
- **Paragraph citations:** ¶36(b) (*"it should have effective mitigants in place … and other effective controls that are consistently applied"*); ¶39 (*"Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual"*); ¶40 (monitoring and escalation); ¶43 (completeness monitoring); ¶56 (materiality)

---

## 4. Out of scope

The following principles, or aspects of principles, concern reporting governance, board processes, and information design. They are not addressable by a data catalog, a CDE register, or data quality monitoring. Stating this clearly is not an admission of failure — it reflects where the boundary of data management ends and reporting governance begins.

---

**Principle 1 (¶27–31) — Board and senior management governance**

The requirement that the board approve the risk data aggregation framework (¶28), that senior management understand its limitations (¶30), and that the board be aware of compliance status (¶31) are governance and accountability obligations. A data catalog can document metadata, data ownership, and data quality findings — and those findings *inform* the board's awareness — but the act of review, approval, and accountability cannot be automated or delegated to a catalog. The catalog supports governance; it does not discharge it.

Note: ¶30's requirement that senior management *"identify data critical to risk data aggregation"* is operationalised through the CDE register above, and ¶33's integrated taxonomy requirement is directly addressed by CDE-04 through CDE-07. The governance wrapper around those identification and taxonomy activities is out of scope.

---

**Principle 2 (¶32–34) — IT infrastructure, business continuity, and data ownership roles**

¶32 requires risk data aggregation to be included in business continuity planning. ¶34 requires that roles and responsibilities for data ownership be established between business and IT. These are organisational and IT-architecture matters. A catalog can *record* data owners and stewards, and can surface which elements are classified as critical — but designing the BCP, assigning ownership authority, and establishing accountability structures requires decisions outside the catalog. The catalog documents the outcome of those decisions; it does not make them.

---

**Principle 6 (¶48–51) — Adaptability of aggregation processes**

Principle 6 requires that the bank's *systems* be capable of producing arbitrary subsets, drill-downs, and ad hoc aggregations quickly. This is a capability requirement for risk systems and data infrastructure. A catalog can document that an element exists, is governed, and is of sufficient quality to support ad hoc queries — but whether the underlying risk systems can execute those queries rapidly under stress is an IT architecture and system performance question. The catalog provides the metadata layer; the query capability is in the risk data warehouse or analytical platform.

Note: ¶50's requirement to aggregate by country and industry sector drives CDE-06 and CDE-07 above, so Principle 6 is partially addressed at the data-element level. The system-capability aspect is out of scope.

---

**Principles 7–9 (¶52–69) — Report design, content, clarity, and usefulness**

Principle 7's report accuracy requirements are partially addressed: CDE-09 (GL reconciliation key) and XDQ-02 (risk-to-finance reconciliation) directly support ¶36(c) and ¶53(a). However, ¶53(b)'s requirement for an inventory of validation rules applied to quantitative report outputs, ¶53(c)'s exceptions reporting process, and ¶55's requirement that senior management establish accuracy and precision requirements for reports are reporting-process and governance obligations, not data catalog obligations.

Principle 8 (comprehensiveness): CDE-04 through CDE-07, CDE-11, and CDE-12 address the data dimensions that risk reports must cover. However, ¶57–60's requirements that reports contain forward-looking forecasts, stress test results, capital adequacy measures, and qualitative interpretation are *report content* obligations. The catalog governs the data inputs; what is written in the report, how it is interpreted, and whether it contains the right forward-looking analysis are editorial and governance decisions.

Principle 9 (clarity and usefulness): ¶61–69 are entirely about report presentation, recipient tailoring, and periodic confirmation that recipients find reports useful. ¶67's requirement for an inventory and classification of risk data items *is* a catalog obligation and is operationalised through the CDE register above. Everything else in Principle 9 — the balance of quantitative versus qualitative, the board's role in requesting the right information, periodic recipient confirmation — is out of scope.

Note on the Principle 8 split: Industry sector (CDE-07) is driven both by ¶50 (an aggregation-capability requirement, in scope) and ¶57 (a report-content requirement, partially out of scope). The data element and its quality monitoring are in scope; whether the *report* that uses it meets comprehensiveness standards is a reporting-governance matter outside the catalog.

---

**Principles 10–11 (¶70–74) — Frequency and distribution of reports**

These principles require the bank to set and review reporting frequencies, test its ability to produce reports within agreed timeframes, confirm that relevant recipients receive timely reports, and maintain confidentiality controls. CDE-08 (as-of date) and its timeliness checks support the frequency monitoring mechanically — they confirm that data *inputs* are available on time. But the decisions about what frequency is appropriate, who receives which reports, how confidentiality is enforced in the distribution channel, and the periodic confirmation with recipients are governance and process obligations that sit with the CRO, CIO, and board — not with a data catalog.

---

## 5. Summary table

| CDE | Name | Criticality | Principles | DQ Dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | P2 (¶33), P4 (¶41) | uniqueness, consistency, completeness |
| CDE-02 | Legal Entity Identifier (Own Bank) | 3 | P2 (¶33), P4 | uniqueness, completeness, validity |
| CDE-03 | Gross Exposure Amount | 3 | P3 (¶36), P4 (¶41), P7 (¶52) | accuracy, completeness, validity |
| CDE-04 | Risk Type Classification | 2 | P2 (¶33), P7 (¶57) | validity, completeness, consistency |
| CDE-05 | Business Line | 2 | P4, P6 (¶50) | completeness, validity, consistency |
| CDE-06 | Geography / Country | 2 | P4, P6 (¶50), P8 (¶57) | completeness, validity, consistency |
| CDE-07 | Industry / Sector | 2 | P4, P6 (¶50), P8 (¶57) | completeness, validity, consistency |
| CDE-08 | Position / As-of Date | 3 | P5 (¶44–47), P6 (¶50), P7 (¶52) | completeness, validity, timeliness |
| CDE-09 | GL / System-of-Record Reconciliation Key | 3 | P3 (¶36(c)), P7 (¶53(a)) | completeness, consistency, accuracy |
| CDE-10 | Source System / Provenance Flag | 2 | P3 (¶36(b), ¶36(d), ¶39) | completeness, validity, accuracy |
| CDE-11 | Collateral / Credit Risk Mitigant Amount | 2 | P4 (¶41), P7 (¶57), P8 (¶58) | accuracy, completeness, validity |
| CDE-12 | Limit / Risk Appetite Threshold | 2 | P5 (¶46(c)), P8 (¶58) | accuracy, completeness, timeliness |