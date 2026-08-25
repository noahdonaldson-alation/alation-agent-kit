# BCBS 239: Data Catalog Governance Interpretation

## 1. Objectives and scope

**What the regulation is trying to achieve**

- **Reliable risk aggregation as a governance obligation.** Boards and senior management must be able to aggregate all material risk exposures across the group, in normal and stress conditions, with results they can rely on for critical decisions. The standard is explicitly analogous to accounting: "Controls surrounding risk data should be as robust as those applicable to accounting data." (¶36(a))

- **Integrated data architecture with consistent identifiers.** A bank must "establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts." (¶33) This is the closest the regulation comes to mandating a data catalog.

- **Measured and monitored data quality, with escalation.** Quality is not assumed — it must be actively measured. "Supervisors expect banks to measure and monitor the accuracy of data and to develop appropriate escalation channels and action plans to be in place to rectify poor data quality." (¶40) Completeness carries the same obligation: "Supervisors expect banks to produce aggregated risk data that is complete and to measure and monitor the completeness of their risk data." (¶43)

- **Timeliness proportional to risk volatility.** Aggregation speed must match the nature of each risk type. In stress, critical risks — including counterparty credit exposures, trading positions, and liquidity indicators — must be available rapidly, potentially intraday. (¶¶44–47)

- **Reconciled and evidenced accuracy.** Reports must be reconcilable back to source data, and risk data must be reconciled to accounting data "where appropriate." (¶¶36(c), 53(a)) An unreconciled figure is not compliant, regardless of whether it looks correct.

- **Documented lineage for all processes, automated and manual.** "Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual." Documentation must cover manual workarounds, their criticality, and planned remediation. (¶39) Source system identification and end-user-computing flags are therefore structural requirements, not optional metadata.

**Who and what it applies to**

BCBS 239 applies to global systemically important banks (G-SIBs) as the primary mandatory audience, with the Basel Committee expecting domestic supervisors to extend the principles to other significant banks. The obligations fall on the banking group as a whole — consolidated and subsidiary level — covering all material risk types (credit, market, liquidity, operational, counterparty, concentration) and all aggregation layers (legal entity, business line, geography, asset type, industry sector).

---

## 2. Critical Data Element candidates

---

**CDE-01 — Counterparty Identifier**
- **Definition:** A unique, persistent identifier assigned to each external counterparty (borrower, trading counterparty, issuer, guarantor) that resolves to the same record across all systems holding exposure data — origination, risk, collateral, and finance.
- **Why critical:** Without a single resolvable counterparty key, exposures held in different systems cannot be summed to produce a total counterparty exposure. The aggregate figure for any counterparty is either impossible to compute or silent about double-counting. Large corporate credit and counterparty credit exposures are named as critical risks at ¶46(a) and ¶46(b).
- **Risk types:** Credit, counterparty, concentration, cross-cutting
- **Criticality:** **3** — *Without this element, the aggregate credit or counterparty exposure to a single counterparty cannot be computed at all, because exposures held in separate origination, trading, and collateral systems cannot be joined to the same legal person.*
- **Driven by:** Principle 2 (¶33) — "use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"; Principle 4 (¶41) — all material risk exposures must be capturable; Principle 5 (¶46(a), ¶46(b))
- **Search terms:** counterparty ID, counterparty reference, obligor ID, entity ID, BIC, LEI, CIF, customer number, counterparty key, GFCID, ultimate parent ID
- **Data quality requirements:**
  - *uniqueness* — Each active counterparty is represented by exactly one identifier in the authoritative counterparty register, with no duplicate records for the same legal person | count of counterparty identifiers that resolve to more than one active master record | threshold: zero, because any duplicate means the same legal person is counted more than once in an aggregation, which is always a defect | **(¶33)**
  - *validity* — Every exposure record carries a counterparty identifier that resolves to a record in the authoritative counterparty register | count of exposure records with a null, blank, or unmatched counterparty identifier | threshold: zero, because a non-resolvable key means that exposure is excluded from any counterparty-level aggregate — there is no materiality argument for leaving an exposure unattributed | **(¶33, ¶40)**
  - *consistency* — The same counterparty identifier is used for the same legal person across all source systems (origination, trading, collateral, risk) | count of counterparty records where the same legal entity carries different identifiers in two or more systems | threshold: zero; cross-system inconsistency is the primary mechanism by which group-level aggregation understates exposure | **(¶33)**

---

**CDE-02 — Legal Entity Identifier (Bank's Own)**
- **Definition:** The identifier of the bank's own legal entity (subsidiary, branch, or holding company) in which a transaction is booked, drawn from an authoritative group entity register.
- **Why critical:** Group consolidation requires summing exposures booked across all group entities; subsidiaries must also be reported separately. If the booking entity is missing or wrong, exposures are either excluded from the consolidated figure, double-counted, or attributed to the wrong subsidiary. ¶33 mandates unified naming for legal entities explicitly; ¶30 names coverage gaps (subsidiaries not included) as a known limitation that senior management must understand and remediate.
- **Risk types:** Cross-cutting (all risk types require legal entity attribution for group reporting)
- **Criticality:** **3** — *Without this element, the aggregate risk exposure at consolidated group level and at individual subsidiary level cannot be computed or evidenced, because there is no basis on which to assign each position to a reporting entity or to exclude intra-group transactions.*
- **Driven by:** Principle 2 (¶33) — "single identifiers and/or unified naming conventions for data including legal entities"; Principle 4 (¶41) — "all material risk exposures, including those that are off-balance sheet"; Principle 1 (¶30) — coverage gaps including "subsidiaries not included" are a named risk
- **Search terms:** legal entity ID, entity code, LEI, booking entity, subsidiary code, branch code, entity hierarchy, consolidated entity flag, MFI code, group entity register
- **Data quality requirements:**
  - *validity* — Every exposure or position record carries a legal entity identifier that resolves to a current record in the group entity register | count of records with a null or unresolvable legal entity identifier | threshold: zero; an exposure with no legal entity attribution is excluded from both consolidated and subsidiary aggregates | **(¶33, ¶40)**
  - *completeness* — All active legal entities that carry material risk are represented in the group entity register and are present in aggregated risk data | count of group entities on the official entity list that have no exposure records in the current reporting period (with a review step to confirm dormancy rather than a data gap) | threshold: no active entity carrying material risk is absent; exceptions require documented explanation per ¶43 | **(¶43)**
  - *consistency* — The legal entity identifier used in risk data matches the identifier used for the same entity in the general ledger and regulatory reporting systems | count of legal entity codes present in risk data that have no matching record in the finance / GL entity table | threshold: zero unresolved mismatches; differences must be explained as structural (e.g., GL uses a different granularity) and documented | **(¶36(c))**

---

**CDE-03 — Gross Exposure Amount**
- **Definition:** The pre-mitigation monetary value of a risk exposure at the transaction or position level — the principal amount, mark-to-market value, or notional, depending on the instrument type — expressed in the instrument's transaction currency.
- **Why critical:** This is the quantity being aggregated. Every risk figure — total credit exposure, VaR, liquidity gap — is constructed by summing, weighting, or transforming this amount. If it is wrong, the aggregate is wrong; if it is missing, the aggregate is understated. ¶46(a) through ¶46(d) enumerate the specific risk figures that must be producible rapidly in stress.
- **Risk types:** Credit, market, liquidity, counterparty, concentration
- **Criticality:** **3** — *Without this element, no aggregate risk figure can be computed at all, because there is no quantity to sum across positions.*
- **Driven by:** Principle 3 (¶36) — "aggregate risk data in a way that is accurate and reliable"; Principle 4 (¶41) — "capture and aggregate all material risk data"; Principle 5 (¶46(a)–(d)) — specific aggregated exposure figures required
- **Search terms:** exposure amount, gross exposure, principal amount, notional amount, mark-to-market value, fair value, outstanding balance, drawn amount, position value, EAD (exposure at default)
- **Data quality requirements:**
  - *accuracy* — Each recorded exposure amount agrees to the amount held in the authoritative system of record (origination system or trading system) at the same as-of date | sum of absolute differences between risk system exposure amounts and system-of-record amounts, by portfolio, compared to a materiality threshold | threshold: set by materiality — the same standard the bank applies to accounting; ¶56 states "Supervisors expect banks to consider accuracy requirements analogous to accounting materiality." The risk function, in consultation with finance, sets the materiality threshold; it is not zero | **(¶36(c), ¶40, ¶56)**
  - *completeness* — All transactions that are open as of the reporting date are present in the aggregated risk dataset; no material positions are missing | count of positions present in the system of record that are absent from the risk dataset; gross value of absent positions as a percentage of total portfolio | threshold: materially complete per ¶43; exceptions identified and explained; the acceptable gap is set by the bank's materiality standard, not zero | **(¶43)**
  - *validity* — No exposure record carries a negative gross exposure amount for an asset type where negative values are not structurally possible (e.g., loan outstanding balances) | count of records with amounts outside the valid range for the instrument type | threshold: zero invalid-range records; a negative loan balance is always a data error, not a materiality judgment | **(¶40)**

---

**CDE-04 — Risk Classification (Risk Type)**
- **Definition:** The categorical label that assigns each exposure or position to a primary risk type — at minimum: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk — using a controlled vocabulary maintained in a group-wide risk taxonomy.
- **Why critical:** Aggregates are always stated by risk type. A figure labelled "total credit risk exposure" is only meaningful if every record contributing to it is correctly classified as credit risk. Misclassification shifts amounts between risk buckets, potentially understating one risk while overstating another. ¶57 requires reports to cover "all significant risk areas" — which presupposes that every exposure is classified.
- **Risk types:** Cross-cutting (classification scheme spans all risk types)
- **Criticality:** **2** — If a risk classification is wrong, the aggregate for that risk type is produced but is wrong in a way that may not be visible: credit exposures counted as market, or vice versa. The total across all risk types would be unaffected, but the risk-type slice would be distorted. This degrades the reliability of disaggregated risk reports without making it impossible to produce a number.
- **Driven by:** Principle 3 (¶37) — "a bank should have a 'dictionary' of the concepts used, such that data is defined consistently across an organisation"; Principle 8 (¶57) — "exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"
- **Search terms:** risk type, risk category, risk classification, risk bucket, asset class, exposure class, risk flag, risk taxonomy code
- **Data quality requirements:**
  - *validity* — Every exposure record carries a risk classification value from the authorised controlled vocabulary | count of records with a null risk type, or a value not in the approved taxonomy | threshold: zero; an unclassified exposure cannot be included in any risk-type aggregate, which is a completeness defect | **(¶37, ¶40)**
  - *consistency* — The same classification scheme and controlled vocabulary are used for the same risk type across all business lines and legal entities | count of distinct risk-type labels in use across source systems that map to the same concept; flag any labels with no mapping to the canonical taxonomy | threshold: zero unmapped labels in production data; divergence in labelling is the primary mechanism by which cross-entity aggregation fails silently | **(¶33, ¶37)**

---

**CDE-05 — Business Line**
- **Definition:** The internal organisational dimension that classifies each exposure or position by the business unit or product line responsible for it — e.g., Retail Banking, Corporate Banking, Investment Banking, Treasury — using a standardised group-wide hierarchy.
- **Why critical:** Principle 4 explicitly requires that risk data be "available by business line" (¶ heading). ¶50 illustrates the expected capability: aggregating credit exposures across all business lines on demand. Without a populated, consistent business line attribute, the bank cannot produce disaggregated risk reports by business line, cannot identify concentrations within a line, and cannot respond to supervisory queries that cut by business line.
- **Risk types:** Credit, market, liquidity, counterparty, concentration (all risk types require this slice)
- **Criticality:** **2** — The aggregate total across all business lines is unaffected if this field is wrong; what degrades is the bank's ability to slice the aggregate by line of business. The figure is produced but cannot be validated or interrogated in the way ¶4 and ¶50 require.
- **Driven by:** Principle 4 (¶ heading and ¶41) — "Data should be available by business line … that permit identifying and reporting risk exposures, concentrations and emerging risks"; Principle 6 (¶50) — "aggregate risk data quickly … across all business lines and geographic areas"
- **Search terms:** business line, business unit, product line, segment code, line of business, LOB code, division, desk, profit centre, cost centre
- **Data quality requirements:**
  - *completeness* — Every exposure or position record carries a populated business line attribute | count and gross exposure value of records with a null or blank business line | threshold: materially complete per ¶43; a missing business line means that position cannot appear in any business-line-sliced report | **(¶43)**
  - *validity* — The business line value on each record matches a current entry in the authoritative group business line hierarchy | count of records carrying a business line code that is not in the current hierarchy (including retired codes) | threshold: zero records with an invalid code in current production data; retired codes must be remapped before reporting | **(¶40)**

---

**CDE-06 — Geography / Country of Risk**
- **Definition:** The country or region assigned to each exposure as the primary geography of risk — typically the country of the counterparty's domicile, the country of collateral, or the country where the risk is underwritten — using a standard country code list (e.g., ISO 3166).
- **Why critical:** Principle 4 requires risk data to be available "by region." ¶50 specifically illustrates the capability requirement: "a bank should be able to aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries." Country concentration is a named supervisory concern, and cross-border data sharing limitations are identified as a governance risk at ¶30.
- **Risk types:** Credit, counterparty, concentration, market
- **Criticality:** **2** — The total portfolio aggregate is unaffected if geography is wrong; what degrades is the ability to produce country-level concentration reports and to respond to supervisory country-risk queries. This is the slice that ¶50 specifically tests.
- **Driven by:** Principle 4 (¶ heading) — "Data should be available by … region"; Principle 6 (¶50) — "aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"
- **Search terms:** country of risk, country code, booking country, country of domicile, geographic region, ISO country, jurisdiction, sovereign code, country of exposure
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a populated country of risk | count and gross exposure value of records with a null or blank country of risk | threshold: materially complete per ¶43; a missing geography means the position is excluded from all country-level aggregates | **(¶43)**
  - *validity* — Country of risk values conform to the bank's approved country code standard (e.g., ISO 3166-1 alpha-2) | count of records with a country code not in the approved reference list | threshold: zero invalid codes in production data | **(¶40)**
  - *consistency* — The same country of risk assignment methodology (e.g., ultimate risk vs. immediate risk) is applied uniformly across business lines | flag business lines where the population of country codes differs structurally from group standard (e.g., one line uses ultimate risk, another uses immediate borrower country) | threshold: no undocumented divergence in methodology; documented differences require a mapping rule | **(¶33)**

---

**CDE-07 — Industry / Sector Classification**
- **Definition:** The industry or economic sector assigned to each counterparty or exposure — e.g., using a standard scheme such as NACE, GICS, or SIC — representing the primary business activity of the obligor or issuer.
- **Why critical:** Principle 4 requires risk data available "by … industry." ¶50 explicitly requires the ability to produce "industry credit exposures as of a specified date based on a list of industry types across all business lines and geographic areas." Principle 8 (¶57) lists "industry sector for credit risk" as a component of risk reporting. Sector concentration is a named regulatory concern.
- **Risk types:** Credit, concentration
- **Criticality:** **2** — The total portfolio aggregate is not affected if sector is misclassified; what degrades is the ability to identify and report sector concentrations, which is a specific requirement of both ¶50 and ¶57. Note: Principle 8 also drives a reporting obligation (see Section 4) that is beyond what a CDE can satisfy.
- **Driven by:** Principle 4 (¶ heading) — "Data should be available by … industry"; Principle 6 (¶50) — "industry credit exposures as of a specified date based on a list of industry types"; Principle 8 (¶57) — "single name, country and industry sector for credit risk"
- **Search terms:** industry code, sector code, NACE code, SIC code, GICS sector, industry classification, obligor industry, counterparty sector, economic sector
- **Data quality requirements:**
  - *completeness* — Every counterparty record in the authoritative counterparty register carries a populated industry/sector classification | count of counterparty records with a null or blank sector code; count of exposure records that join to a counterparty with no sector | threshold: materially complete per ¶43; an unclassified counterparty means all their exposures are excluded from sector-level concentration analysis | **(¶43)**
  - *validity* — All sector codes in use are drawn from the bank's approved sector classification scheme | count of sector codes not present in the approved reference list | threshold: zero invalid codes | **(¶40)**

---

**CDE-08 — As-of / Position Date**
- **Definition:** The business date as of which an exposure, position, or risk measure is stated — the snapshot date that defines which transactions are in scope, and to which all aggregated figures in a report are referenced.
- **Why critical:** Every aggregate is meaningless without knowing when it was measured. Mixing positions from different dates within a single aggregate produces a figure that is neither accurate nor complete — it does not represent the bank's position at any point in time. Under ¶44–47, the bank must produce risk data "on a timely basis"; that obligation is only verifiable if each record carries an as-of date that can be compared to the reporting deadline.
- **Risk types:** Cross-cutting (all risk types)
- **Criticality:** **3** — *Without this element, the aggregate figure for any risk type cannot be stated as of a specific date, and the timeliness obligation in ¶44–47 cannot be measured or evidenced. An aggregate computed from records with mixed or unknown dates is not a valid risk position.*
- **Driven by:** Principle 5 (¶44) — "produce aggregate risk information on a timely basis to meet all risk management reporting requirements"; Principle 5 (¶47) — supervisors will review that banks generate "aggregate and up-to-date risk data in a timely manner"; Principle 6 (¶50) — "aggregate risk data quickly … as of a specified date"
- **Search terms:** as-of date, position date, valuation date, reference date, snapshot date, reporting date, trade date, record date, effective date, settlement date
- **Data quality requirements:**
  - *timeliness* — Risk data for each risk type is available by the deadline set for that risk type under normal conditions, and by the accelerated deadline in stress conditions | time elapsed between the as-of date and the point at which aggregated data is available for reporting, measured by risk type and compared to the bank's stated frequency requirements | threshold: set by the bank's own frequency requirements (¶47); market and trading data will have a tighter threshold than credit; stress-scenario deadlines are tighter still (¶45) | **(¶44–47)**
  - *validity* — Every exposure and position record carries a populated, valid calendar date as its as-of date | count of records with a null, non-date, or future-dated as-of value (where future-dated is not expected for the instrument type) | threshold: zero; a record without a valid date cannot be assigned to any reporting period | **(¶40)**
  - *consistency* — All records included in a single aggregated risk figure share the same as-of date | count of records in a batch or dataset where the as-of date differs from the declared reporting date of the batch | threshold: zero unexplained date mismatches within a single reporting run; legitimate exceptions (e.g., settlement lag) must be documented | **(¶36(c))**

---

**CDE-09 — GL / Source System Reconciliation Key**
- **Definition:** The identifier — transaction reference, trade ID, facility ID, or account number — that links a risk record to its corresponding record in the general ledger or in the authoritative origination system of record, enabling line-by-line reconciliation between the risk dataset and the finance dataset.
- **Why critical:** ¶36(c) states directly: "Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate." ¶53(a) repeats this at the reporting layer: "Defined requirements and processes to reconcile reports to risk data." Without a joining key between the risk record and the GL or system-of-record record, reconciliation cannot be performed at all. A risk figure that cannot be reconciled cannot be evidenced as accurate — an unverifiable figure is not a compliant one.
- **Risk types:** Cross-cutting (reconciliation is required for all risk types)
- **Criticality:** **3** — *Without this element, the accuracy and integrity of any aggregated risk figure cannot be reconciled to the system of record or to accounting data, as explicitly required by ¶36(c). A risk figure that cannot be evidenced through reconciliation is not compliant, regardless of whether it appears correct.*
- **Driven by:** Principle 3 (¶36(c)) — "Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"; Principle 7 (¶53(a)) — "Defined requirements and processes to reconcile reports to risk data"
- **Search terms:** trade ID, transaction reference, facility ID, account number, deal reference, loan ID, position ID, GL account reference, source system key, system of record ID, origination reference
- **Data quality requirements:**
  - *accuracy* — For each risk record that has a corresponding GL or system-of-record entry, the exposure amount in the risk system agrees to the amount in the system of record within the materiality threshold | sum of absolute differences between matched risk and GL records as a percentage of total portfolio value, by asset class | threshold: set by accounting materiality per ¶56; the risk function sets the materiality standard in consultation with finance; it is not zero, but any breach above the materiality threshold triggers an escalation | **(¶36(c), ¶40, ¶56)**
  - *completeness* — Every risk record that should have a corresponding GL entry carries a populated reconciliation key | count of risk records with a null or blank reconciliation key where a GL entry is expected | threshold: zero for records where a GL entry is required by the bank's accounting policies; a null key means reconciliation cannot be performed for that record | **(¶43, ¶36(c))**
  - *consistency* — The reconciliation key on the risk record resolves to exactly one record in the GL or system of record | count of reconciliation keys that either match zero GL records or match more than one GL record | threshold: zero unresolvable keys in current production data; a key that matches nothing means that risk record is unreconciled by construction | **(¶36(c))**

---

**CDE-10 — Source System / Manual Process Flag**
- **Definition:** The attribute on each risk record that identifies the originating source system (e.g., loan origination platform, trading system, treasury system) and flags whether the record was produced by an automated process or entered or adjusted through a manual process or end-user computing tool (spreadsheet, desktop database).
- **Why critical:** ¶39 requires documentation of "all of their risk data aggregation processes whether automated or manual," including "the appropriateness of any manual workarounds" and "their criticality to the accuracy of risk data aggregation." ¶36(b) requires effective controls for manual processes and EUC tools. Without this attribute, it is impossible to identify which records are subject to heightened accuracy risk, to apply the specific controls required for EUC data, or to report the extent of manual processing to senior management as required by ¶30.
- **Risk types:** Cross-cutting (lineage and provenance apply to all risk types)
- **Criticality:** **2** — Individual aggregate figures are not made invalid by the absence of this flag; what degrades is the bank's ability to apply differential controls to manual inputs, to monitor the extent of EUC dependency, and to evidence to supervisors that manual process controls are in place. These are control and governance obligations under ¶36(b) and ¶39, not computational ones.
- **Driven by:** Principle 3 (¶36(b)) — "Where a bank relies on manual processes and desktop applications … it should have effective mitigants in place … and other effective controls that are consistently applied"; Principle 3 (¶39) — "Supervisors expect banks to document and explain all of their risk data aggregation processes whether automated or manual … a description of their criticality to the accuracy of risk data aggregation"
- **Search terms:** source system, data source, system of origin, source indicator, manual override flag, EUC flag, end-user computing indicator, manual input flag, upload source, data lineage, process flag, override indicator
- **Data quality requirements:**
  - *completeness* — Every risk record carries a populated source system identifier and a populated manual/automated process flag | count of records with a null source system or null process flag | threshold: zero; a record with no provenance cannot be subject to the correct control regime and cannot be included in manual-process monitoring | **(¶39, ¶43)**
  - *validity* — Source system values are drawn from the bank's authoritative system inventory | count of source system codes on risk records that are not registered in the system inventory | threshold: zero; an unregistered source means the record's provenance is unknown and the appropriate data quality controls cannot be determined | **(¶40)**
  - *accuracy* — The proportion of risk data sourced from manual or EUC processes is monitored over time, and changes above a defined threshold are escalated to senior management | trend in the percentage of records flagged as manual or EUC, by risk type and business line, measured each reporting cycle | threshold: an increasing trend or a breach of the bank's stated EUC tolerance (set by senior management per ¶30) triggers escalation; the specific threshold is set by the bank based on its EUC reduction targets | **(¶36(b), ¶39, ¶40)**

---

**CDE-11 — Net Exposure / Credit Risk Mitigant**
- **Definition:** The value of financial collateral, guarantees, or credit protection that offsets the gross exposure for a counterparty or facility, together with the resulting net exposure after mitigation — enabling both gross and net aggregation.
- **Why critical:** ¶41 requires aggregation of "all material risk exposures, including those that are off-balance sheet." Risk concentration analysis and regulatory capital calculation depend on net exposure after collateral and guarantees. ¶58 requires reports to include risk measures "in the context of limits and risk appetite/tolerance" — which presupposes that net, as well as gross, exposure is computable. Without collateral values tied to gross exposures, the bank cannot produce net exposure aggregates.
- **Risk types:** Credit, counterparty, concentration
- **Criticality:** **2** — Gross exposure aggregates (CDE-03) remain valid without this element. What degrades is the ability to compute net exposure, to assess capital adequacy correctly, and to identify concentrations on a net basis. Reports are produced but reflect gross rather than net positions, which distorts risk appetite monitoring.
- **Driven by:** Principle 4 (¶41) — "all material risk exposures, including those that are off-balance sheet"; Principle 8 (¶57) — risk-related measures including "regulatory and economic capital"; Principle 8 (¶58) — "information in the context of limits and risk appetite/tolerance"
- **Search terms:** collateral value, collateral amount, guarantee value, credit protection, netting agreement, net exposure, LGD input, recovery value, CRM value, haircut, eligible collateral, credit mitigant
- **Data quality requirements:**
  - *accuracy* — Collateral valuations are current (revalued at the frequency required by the bank's collateral management policy) and the net exposure derived from them agrees to the risk system's calculation | count of collateral records where the valuation date is older than the policy-permitted staleness threshold; sum of absolute differences between collateral system values and risk system net exposure amounts | threshold: staleness threshold is set by collateral type and market liquidity (illiquid collateral may be revalued less frequently; liquid securities daily); accuracy threshold is set by materiality per ¶56 | **(¶36(c), ¶40, ¶56)**
  - *completeness* — Every secured exposure carries a linked collateral or guarantee record; unsecured exposures are explicitly flagged as having no mitigation | count of exposure records classified as secured with no linked mitigant record; count of records with no mitigation flag at all | threshold: zero records with ambiguous mitigation status; a record that is neither confirmed as secured nor confirmed as unsecured cannot be correctly included in net exposure aggregates | **(¶43)**

---

## 3. Cross-cutting data quality requirements

---

**XDQ-01 — Risk-to-Finance Reconciliation**
- **Spans:** CDE-03 (Gross Exposure Amount), CDE-09 (GL / Source System Reconciliation Key), CDE-02 (Legal Entity Identifier), CDE-08 (As-of / Position Date)
- **Rule intent:** The total risk exposure aggregated by the risk function, at legal entity level, must be reconcilable to the corresponding balance or notional in the general ledger as of the same date. This cross-system check is the primary evidence that risk data is accurate and complete — it is not derivable by monitoring any single element, because it requires joining across the risk data repository and the GL using the reconciliation key, grouping by legal entity and date, and comparing totals.
- **Measurement:** Sum of gross exposure by asset class, legal entity, and as-of date in the risk system, compared to the corresponding balance in the general ledger for the same scope; differences expressed as an amount and as a percentage of the GL balance, by stratum.
- **Threshold:** Set by accounting materiality per ¶56 — "if omission or misstatement could influence the risk decisions of users, this may be considered material." The risk function and finance jointly set the materiality threshold by asset class. Differences above the materiality threshold trigger escalation per ¶40; differences below it are logged with explanation. The threshold is not zero, but the escalation process is mandatory.
- **Paragraph citations:** ¶36(c) — "Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"; ¶53(a) — "Defined requirements and processes to reconcile reports to risk data"; ¶40 — escalation and action plans; ¶56 — materiality standard for accuracy

---

**XDQ-02 — Single Counterparty / Entity Resolution Across Systems**
- **Spans:** CDE-01 (Counterparty Identifier), CDE-02 (Legal Entity Identifier — bank's own), CDE-04 (Risk Classification), CDE-05 (Business Line)
- **Rule intent:** The same external counterparty must resolve to a single record in the authoritative counterparty register regardless of which source system originated the exposure. This is not a property of any individual record; it is a property of the relationship between records across systems. A counterparty that appears under different identifiers in the loan origination system and the derivatives system will produce an understatement of aggregate counterparty exposure that no single-element check can detect.
- **Measurement:** For each counterparty in the authoritative register: count of distinct identifiers used for that counterparty across all contributing source systems; count of source systems that carry no mapping to the authoritative identifier; gross exposure attributed to records with no authoritative mapping.
- **Threshold:** Zero counterparties with more than one active identifier in the authoritative register; zero exposure records with no mapping to the authoritative counterparty identifier. There is no materiality tolerance for identifier integrity — a single unlinked record means a counterparty exposure aggregate is wrong, and the direction and magnitude of the error are unknown. The threshold is zero because the error is structural, not quantitative.
- **Paragraph citations:** ¶33 — "single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"; ¶40 — measurement, monitoring, escalation; ¶46(a) and (b) — aggregated credit and counterparty exposures to large corporates named as critical risks requiring rapid aggregation

---

## 4. Out of scope

The following principles establish obligations that a data catalog, CDE register, and data quality monitoring programme cannot satisfy. They require process controls, governance structures, management actions, and reporting artefacts that are outside the scope of metadata management.

---

**Principle 1 — Governance (¶27–31): Board and senior management responsibilities**

The CDE register and data quality monitoring contribute to Principle 1 by providing the evidence base that senior management needs to understand data quality limitations (¶30) and to identify data critical to risk data aggregation (¶30). However, the obligation itself — that the board reviews and approves the aggregation framework (¶28), that senior management deploys adequate resources (¶28), and that the bank maintains service level agreements for outsourced data processes (¶27) — is a governance structure matter, not a data content matter. A catalog can host documentation of the framework; it cannot constitute or enforce the framework.

**Principle 2 — Data architecture and IT infrastructure (¶32–35): Business continuity and IT strategy**

¶33 directly drives CDEs (counterparty ID, legal entity ID) and the single-identifier requirement underpins XDQ-02. This principle is therefore partially addressable through the CDE register. However, the remaining obligations — business continuity planning (¶32), IT infrastructure investment (¶30, ¶35), data ownership role assignments (¶34), and the determination that IT strategy includes remediation of aggregation shortcomings (¶30) — require organisational decisions, role charters, IT architecture choices, and funding decisions that are outside metadata management scope. A catalog can record data ownership; it cannot mandate that ownership is exercised.

**Principle 6 — Adaptability (¶48–51): System flexibility and on-demand aggregation**

CDE-05 (Business Line), CDE-06 (Geography), and CDE-07 (Industry Sector) are driven partly by Principle 6 (¶50), which illustrates the required on-demand aggregation capability. However, the capability itself — the ability to slice any dimension on demand, to incorporate new business structures, to support stress-testing scenarios at speed (¶48, ¶49) — is an IT systems capability, not a data element property. Tagging an exposure with a sector code does not deliver the ability to aggregate it on demand; that requires the right query and reporting infrastructure. The CDE ensures the raw material is present; Principle 6 requires that the infrastructure can use it.

**Principle 7 — Accuracy in reports (¶52–56): Report validation and exception management**

CDE-09 (Reconciliation Key) and XDQ-01 (Risk-to-Finance Reconciliation) directly support Principle 7. However, ¶53(b) requires "automated and manual edit and reasonableness checks, including an inventory of the validation rules applied to quantitative information" — which is a report production control, not a catalog control. ¶53(c) requires "integrated procedures for identifying, reporting and explaining data errors … via exceptions reports" — which is a workflow and escalation process. The catalog can host the inventory of validation rules; it cannot run the report-layer validation or operate the exceptions workflow.

**Principle 8 — Comprehensiveness (¶57–60): Report content and forward-looking analysis**

CDE-04 (Risk Classification) and CDE-07 (Industry Sector) are driven partly by Principle 8 (¶57). However, the report-content obligations of Principle 8 are entirely outside catalog scope: that reports cover all significant risk areas (¶57), that they identify emerging concentrations and include stress test results (¶58), and that they contain forward-looking forecasts (¶60). These are requirements about what information appears in a finished report, addressed to report designers and risk managers. Ensuring that the underlying data elements exist and are of sufficient quality is a necessary but not sufficient condition for meeting Principle 8; the report design, analysis, and interpretation obligations are separate.

**Principles 9 — Clarity and usefulness (¶61–69): Report design, recipient engagement, and inventory**

¶67 — "A bank should develop an inventory and classification of risk data items which includes a reference to the concepts used to elaborate the reports" — is the closest the reporting principles come to a catalog requirement. A data catalog can satisfy the spirit of ¶67 by hosting a business glossary and linking CDEs to the reports that use them. However, the remaining obligations of Principle 9 — that reports are tailored to recipients, that the board confirms relevance periodically (¶69), that there is an appropriate balance of qualitative and quantitative content (¶62, ¶68) — are report governance obligations addressed to the board, senior management, and report owners. They cannot be addressed by metadata management.

**Principle 10 — Frequency (¶70–71): Report scheduling and stress-test cadence**

The timeliness requirements of Principle 5 drive CDE-08 (As-of / Position Date) and the timeliness DQ checks. However, Principle 10's obligations are about the frequency at which finished reports are produced and distributed to recipients (¶70), and the requirement to test the ability to produce reports within established timeframes in stress conditions (¶70). These are operational and testing obligations for the report production function, not data element properties.

**Principle 11 — Distribution (¶72–74): Confidentiality and distribution controls**

No CDE or DQ monitor addresses report distribution. The confidentiality and access controls required by Principle 11 are access management and information security obligations. A data catalog can record data sensitivity classifications and intended audiences; it cannot enforce distribution controls on reports.

---

## 5. Summary table

| CDE | Name | Criticality | Principles | DQ dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | P2 (¶33), P4 (¶41), P5 (¶46) | Uniqueness, validity, consistency |
| CDE-02 | Legal Entity Identifier (Bank's Own) | 3 | P2 (¶33), P4 (¶41), P1 (¶30) | Validity, completeness, consistency |
| CDE-03 | Gross Exposure Amount | 3 | P3 (¶36), P4 (¶41), P5 (¶46) | Accuracy, completeness, validity |
| CDE-04 | Risk Classification (Risk Type) | 2 | P3 (¶37), P8 (¶57) | Validity, consistency |
| CDE-05 | Business Line | 2 | P4 (¶ heading, ¶41), P6 (¶50) | Completeness, validity |
| CDE-06 | Geography / Country of Risk | 2 | P4 (¶ heading), P6 (¶50) | Completeness, validity, consistency |
| CDE-07 | Industry / Sector Classification | 2 | P4 (¶ heading), P6 (¶50), P8 (¶57) | Completeness, validity |
| CDE-08 | As-of / Position Date | 3 | P5 (¶44–47), P6 (¶50) | Timeliness, validity, consistency |
| CDE-09 | GL / Source System Reconciliation Key | 3 | P3 (¶36(c)), P7 (¶53(a)) | Accuracy, completeness, consistency |
| CDE-10 | Source System / Manual Process Flag | 2 | P3 (¶36(b), ¶39) | Completeness, validity, accuracy |
| CDE-11 | Net Exposure / Credit Risk Mitigant | 2 | P4 (¶41), P8 (¶57, ¶58) | Accuracy, completeness |

**Criticality 3 count: 5** (CDE-01, CDE-02, CDE-03, CDE-08, CDE-09) — within the target range of 4–5.

**Cross-cutting requirements:** XDQ-01 (Risk-to-Finance Reconciliation) spans CDE-02, CDE-03, CDE-08, CDE-09; XDQ-02 (Single Counterparty Resolution) spans CDE-01, CDE-02, CDE-04, CDE-05.