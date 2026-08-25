# BCBS 239 — Data Catalog Governance Interpretation

---

## 1. Objectives and scope

**What the regulation is trying to achieve**

- **Reliable aggregation across the whole group.** Banks must be able to collapse risk exposures across legal entities, business lines, asset types, industries and regions into a single coherent picture — in normal times and, more demandingly, under stress. A catalog that cannot trace how individual records roll up to group totals is not compliant. (Principle 4, ¶41–43: *"A bank's risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet."*)

- **Accuracy that is provable, not just asserted.** Risk data must reconcile to accounting and source-system data. An aggregated figure that cannot be traced back to a system of record and verified is treated as untrustworthy regardless of whether it happens to be correct. (Principle 3, ¶36(c): *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate."*)

- **Timeliness scaled to risk velocity.** Different risk types have different speed requirements. Credit concentrations and liquidity indicators may need to be produced intraday in a crisis; retail portfolio aggregates may tolerate longer cycles. The regulation does not set a universal clock but requires the bank to set and meet its own frequency requirements per risk type. (Principle 5, ¶45: *"Banks need to build their risk systems to be capable of producing aggregated risk data rapidly during times of stress/crisis for all critical risks."*)

- **Governance and ownership, not just technology.** Boards and senior management must approve the aggregation framework, understand its limitations, and ensure that data ownership is assigned explicitly to both business and IT functions. A data catalog entry without a named owner satisfies neither ¶28 nor ¶34. (Principle 1, ¶34: *"Roles and responsibilities should be established as they relate to the ownership and quality of risk data and information for both the business and IT functions."*)

- **A single, documented vocabulary.** Integrated data taxonomies, single identifiers, and unified naming conventions across the banking group are prerequisites for consistent aggregation. Without them, the same counterparty or legal entity may appear under different names in different systems, making any cross-system aggregate unreliable. (Principle 2, ¶33: *"A bank should establish integrated data taxonomies and architecture across the banking group, which includes information on the characteristics of the data (metadata), as well as use of single identifiers and/or unified naming conventions."*)

- **Measured and monitored quality, with escalation.** Accuracy and completeness must be actively measured — not assumed — and gaps must be escalated and remediated. Passive monitoring without action plans is insufficient. (Principle 3, ¶40: *"Supervisors expect banks to measure and monitor the accuracy of data and to develop appropriate escalation channels and action plans to be in place to rectify poor data quality."*)

**Who it applies to**

Globally systemically important banks (G-SIBs) were the initial target, with explicit expectation of adoption by domestic systemically important banks (D-SIBs) and, over time, other significant banks. The principles apply at the **banking group level** — subsidiaries, branches, and material legal entities within the group are all in scope, not merely the parent entity.

---

## 2. Critical Data Element candidates

---

**CDE-01 — Counterparty Identifier**

- **Definition:** The unique, persistent identifier assigned to a legal-entity counterparty (borrower, trading counterparty, guarantor) that is consistent across all systems in the banking group. This is a key, not a name or description; it resolves to exactly one real-world party.
- **Why critical:** Without a stable, group-wide counterparty key, exposures held in different systems — lending, derivatives, securities financing — cannot be joined and summed. The aggregate credit exposure to a single counterparty, which ¶46(a) and ¶46(b) name as a critical risk measure, is either impossible to compute or will double-count or miss positions depending on which system is queried. The figure is structurally invalid, not merely imprecise.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 3** — *Without this element, the aggregate credit exposure to a single counterparty across systems cannot be computed at all, because there is no joining key to link records in the lending system, the derivatives system, and the securities financing system to the same real-world party.*
- **Driven by:** Principle 2 (¶33) — *"use of single identifiers and/or unified naming conventions for data including legal entities, counterparties, customers and accounts"*; and Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures"*
- **Search terms:** counterparty ID, legal entity identifier, LEI, counterparty code, obligor ID, client ID, entity key, BIC, party identifier
- **Data quality requirements:**
  - *uniqueness* — Every counterparty record in the risk data store maps to exactly one identifier; no two distinct real-world parties share an ID | count of duplicate counterparty identifiers across source systems after golden-record resolution | threshold: zero duplicates, because a single duplicate makes any concentration figure for those parties unreliable | **(¶33)**
  - *validity* — Every exposure record carries a counterparty identifier that resolves to an active record in the authoritative counterparty register | count of exposure records with null, blank, or unresolvable counterparty identifier | threshold: zero, because an unresolvable key excludes that exposure from every counterparty-level aggregate — the omission is silent and therefore always material | **(¶40)**
  - *consistency* — The same counterparty identifier is used for the same party across the lending, derivatives, and liquidity source systems | count of distinct identifiers resolving to the same LEI or golden record across systems | threshold: zero cross-system mismatches; set by the reconciliation requirement in ¶36(c) which cannot be met if the same party carries different keys in different feeds | **(¶36(c))**

---

**CDE-02 — Legal Entity Identifier (Own Entity)**

- **Definition:** The identifier for the bank's own booking legal entity — the subsidiary or branch that is the legal counterparty to a transaction. This is the bank's side of a trade or loan, not the external counterparty's side. It must be consistent with the group's legal entity hierarchy.
- **Why critical:** Group consolidation and subsidiary-level regulatory reporting both require that every exposure can be attributed to a specific booking entity. Without this, exposures cannot be rolled up from subsidiary to group, and subsidiary-level reports cannot be separated from group-level reports. ¶30 names coverage of subsidiaries as a known limitation that senior management must track; ¶50 requires the ability to cut risk data by geography and business line simultaneously, which is impossible if the booking entity is unknown.
- **Risk types:** Cross-cutting (credit, market, liquidity, concentration)
- **Criticality: 3** — *Without this element, the group-level aggregate risk exposure cannot be computed, because there is no basis on which to include or exclude positions held by specific subsidiaries, and ¶36(c) reconciliation to legal-entity-level accounting records is impossible.*
- **Driven by:** Principle 2 (¶33) — *"single identifiers and/or unified naming conventions for data including legal entities"*; Principle 4 (¶41) — *"capture and aggregate all material risk data across the banking group"*
- **Search terms:** legal entity ID, booking entity, entity code, subsidiary identifier, branch code, LEI (own), reporting entity, booking unit, organisational unit code
- **Data quality requirements:**
  - *validity* — Every risk exposure record carries a booking-entity identifier that resolves to an active node in the group's legal entity hierarchy | count of records with null or unresolvable booking entity | threshold: zero, because any record without a valid booking entity is excluded from both group consolidation and subsidiary reporting — there is no safe default | **(¶40)**
  - *completeness* — All material subsidiaries and branches that carry risk positions are represented in the entity hierarchy; no in-scope legal entity is absent | count of entities in the group structure that have no corresponding records in the risk data store during a reporting period where activity is known | threshold: zero absent in-scope entities; ¶43 requires completeness to be measured and any exception identified and explained | **(¶43)**
  - *consistency* — The legal entity code used on risk records matches the entity code on the corresponding general ledger and regulatory reporting submissions | count of risk records where the booking entity code does not match the GL entity code for the same transaction | threshold: zero mismatches; required by ¶36(c) reconciliation to accounting sources | **(¶36(c))**

---

**CDE-03 — Gross Exposure Amount**

- **Definition:** The monetary value representing the bank's gross risk exposure on a position or facility before the application of collateral, netting, or credit risk mitigants. Expressed in the transaction currency and in a base reporting currency. This is the raw exposure figure from which all risk aggregates are built.
- **Why critical:** Every aggregated risk measure — total credit exposure, trading book P&L, liquidity gap — is computed by summing or transforming individual exposure amounts. If this field is wrong, every aggregate built from it is wrong. The exposure amount is the quantity being aggregated; all other CDEs are dimensions or keys that control how it is aggregated.
- **Risk types:** Credit, market, counterparty credit, liquidity, concentration
- **Criticality: 3** — *Without this element, the aggregate credit or market exposure figure cannot be computed at all, because there is no monetary quantity to sum across positions.*
- **Driven by:** Principle 3 (¶36) — *"A bank should aggregate risk data in a way that is accurate and reliable"*; Principle 4 (¶41) — *"capture and aggregate all material risk data across the banking group"*; Principle 7 (¶52) — *"Risk management reports should be accurate and precise to ensure a bank's board and senior management can rely with confidence on the aggregated information"*
- **Search terms:** exposure amount, notional amount, outstanding balance, drawn exposure, current exposure, mark-to-market value, fair value, book value, principal balance, facility amount, EAD (exposure at default)
- **Data quality requirements:**
  - *accuracy* — Each exposure amount agrees with the corresponding value in the source booking system within the bank's stated materiality tolerance | sum of absolute differences between risk system exposure amounts and source system amounts for the same instrument | threshold: set by materiality assessment per ¶56 (*"analogous to accounting materiality"*); the threshold is not zero because approximations are acknowledged in ¶54, but it must be defined and owned by senior management | **(¶56, ¶40)**
  - *completeness* — Every in-scope instrument in the source system has a corresponding exposure record in the risk data store | count of source-system instruments with no matching risk record | threshold: zero for individually material instruments; for portfolios, determined by the materiality standard in ¶56 and ¶43; exceptions must be identified and explained | **(¶43)**
  - *validity* — Exposure amounts are non-null, non-zero where a position is known to exist, and fall within plausible ranges for the instrument type | count of records with null, zero, or out-of-range exposure amounts | threshold: zero null or zero values where a live position exists; range breaches flagged for review | **(¶40)**

---

**CDE-04 — Risk Type Classification**

- **Definition:** The categorical label that assigns each exposure to a primary risk type: credit risk, market risk, liquidity risk, operational risk, counterparty credit risk. This is the first-level partition of the risk taxonomy required by ¶57.
- **Why critical:** Principle 8 (¶57) requires reports to cover all significant risk areas. Aggregation by risk type is the minimum partition that separates credit risk totals from market risk totals from liquidity risk totals. Without a clean, validated classification, a bank cannot produce the risk-type-separated reports required, and cannot demonstrate that all risk types have been captured. It also drives the timeliness requirement — ¶45 sets different speed expectations for different risk types, which cannot be applied if the type is unknown or miscoded.
- **Risk types:** Cross-cutting
- **Criticality: 2** — The aggregate figure for any given risk type is produced but cannot be correctly partitioned if the classification is wrong; some exposures will appear in the wrong bucket. The aggregate across all types is unaffected, but type-specific figures — and the reports required by ¶57 — are unreliable.
- **Driven by:** Principle 8 (¶57) — *"Risk management reports should include exposure and position information for all significant risk areas (eg credit risk, market risk, liquidity risk, operational risk)"*; Principle 5 (¶45) — *"different types of data will be required at different speeds, depending on the type of risk"*
- **Search terms:** risk type, risk category, risk class, risk classification, risk domain, exposure type, product risk type
- **Data quality requirements:**
  - *validity* — Every exposure record carries a risk type value drawn from the bank's approved risk taxonomy; no free-text, null, or non-enumerated values | count of records where risk type is null or outside the approved value list | threshold: zero; an uncoded record cannot be routed to the correct report or timeliness regime | **(¶40)**
  - *completeness* — All in-scope risk types recognised in the bank's risk framework are populated across the record population; no systematic absence of any type | count of approved risk types with zero records in a reporting period where activity is expected | threshold: zero absent types during active periods; absence must be explained per ¶43 | **(¶43)**
  - *consistency* — The risk type assigned at origination or booking is consistent with the risk type used in downstream aggregation and reporting; reclassifications are documented | count of records where the risk type in the risk system differs from the risk type on the corresponding GL or booking record for the same instrument | threshold: zero undocumented discrepancies; reclassifications are permissible but must be recorded and explainable | **(¶36(c))**

---

**CDE-05 — Business Line**

- **Definition:** The organisational dimension that assigns each exposure to the internal business unit responsible for it — for example, retail banking, corporate banking, trading, transaction services. Must be consistent with the bank's management reporting hierarchy.
- **Why critical:** Principle 4 explicitly names business line as a required aggregation dimension. ¶50 requires the bank to be able to cut risk data by business line across all geographic areas simultaneously. Without a clean, populated business line dimension, neither the regulatory aggregation requirement nor management's ability to drill down is met.
- **Risk types:** Cross-cutting (credit, market, liquidity, concentration)
- **Criticality: 2** — The overall aggregate figure is produced, but the business-line slice required by Principle 4 and ¶50 cannot be produced or is incorrect, leaving a hole that a supervisor reviewing slice-and-dice capability would find immediately.
- **Driven by:** Principle 4 (¶41–43) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures … across all business lines and geographic areas"*
- **Search terms:** business line, business unit, division, segment, LOB (line of business), cost centre, product line, desk
- **Data quality requirements:**
  - *completeness* — Every exposure record carries a non-null business line code | count of records with null or missing business line | threshold: zero; an unattributed record cannot appear in any business-line report and is effectively excluded from the slice required by ¶41 | **(¶43)**
  - *validity* — Business line codes reference an active node in the current organisational hierarchy; codes for dissolved or renamed units are not used on current records | count of records with business line codes absent from the current hierarchy | threshold: zero for current-period records; historical records may carry legacy codes but must be mapped | **(¶40)**
  - *consistency* — The business line assignment on a risk record matches the business line on the management accounting record for the same instrument | count of records where the business line on the risk feed differs from the management accounts feed | threshold: zero undocumented differences; differences indicate either a data error or an intentional reclassification that must be documented per ¶36(c) | **(¶36(c))**

---

**CDE-06 — Geography / Country of Risk**

- **Definition:** The country or jurisdiction to which an exposure is attributed for risk purposes — typically the country of the obligor's domicile, the country where collateral is located, or the country of the booking branch, depending on the risk type. For credit risk this is usually obligor country; for market risk it may be country of instrument issuance.
- **Why critical:** ¶50 gives a concrete example of the adaptability requirement: a bank must be able to aggregate credit exposures by country as of a specified date, across all business lines. Geography is also a named aggregation dimension in Principle 4's header. Country concentration risk — a specific regulatory concern — cannot be measured without it.
- **Risk types:** Credit, market, liquidity, concentration
- **Criticality: 2** — The aggregate total exposure is produced, but the geographic slice required by ¶41 and ¶50 is unavailable or incorrect. Country concentration risk reports are either missing or unreliable.
- **Driven by:** Principle 4 (¶41) — *"Data should be available by business line, legal entity, asset type, industry, region and other groupings"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date based on a list of countries"*
- **Search terms:** country of risk, obligor country, country code, jurisdiction, region, geographic area, domicile country, ISO country code, booking country
- **Data quality requirements:**
  - *completeness* — Every credit and counterparty exposure record carries a country-of-risk code | count of records with null country-of-risk | threshold: zero for material exposures; ¶43 requires completeness to be measured and exceptions explained, and ¶50 makes country a specifically cited example | **(¶43)**
  - *validity* — Country codes conform to a controlled vocabulary (e.g. ISO 3166 or internal equivalent); no free-text or non-enumerated values | count of records with country codes outside the approved list | threshold: zero; an invalid code cannot be mapped to a region or regulatory geography | **(¶40)**
  - *accuracy* — Country of risk reflects the economic substance of the exposure (obligor domicile, not booking branch), consistent with the bank's country risk policy | sample reconciliation of country-of-risk assignments against origination documentation for a risk-weighted sample | threshold: set by materiality; systematic miscoding of a country with concentrated exposure is always material | **(¶56, ¶40)**

---

**CDE-07 — Industry / Sector Classification**

- **Definition:** The economic sector or industry to which a borrower or issuer belongs — typically aligned to a standard classification scheme (NACE, GICS, SIC, or internal equivalent). Used to measure industry concentration risk in credit portfolios.
- **Why critical:** ¶57 names industry sector as a required reporting dimension for credit risk alongside single-name and country. ¶50 requires the ability to aggregate industry credit exposures across all business lines and geographic areas as of a specified date. Industry concentration cannot be measured without this field. Note: while Principle 8 drives this as a data element, Principle 8's report-content obligations (what the report must say) fall outside catalog scope — see Section 4.
- **Risk types:** Credit, concentration
- **Criticality: 2** — The total credit exposure aggregate is produced, but the industry-sector slice required by ¶57 and ¶50 cannot be produced or is unreliable. Industry concentration reports are missing or distorted.
- **Driven by:** Principle 8 (¶57) — *"all significant components of those risk areas (eg single name, country and industry sector for credit risk)"*; Principle 6 (¶50) — *"industry credit exposures as of a specified date based on a list of industry types across all business lines"*
- **Search terms:** industry code, sector, NACE code, GICS sector, SIC code, industry classification, borrower industry, issuer sector, economic sector
- **Data quality requirements:**
  - *completeness* — Every credit exposure record for a corporate or institutional counterparty carries a non-null industry/sector code | count of corporate credit records with null industry code | threshold: zero for individual material exposures; for portfolio segments, governed by ¶43's materiality standard with exceptions documented | **(¶43)**
  - *validity* — Industry codes are drawn from the bank's approved classification scheme; no free-text values | count of records with codes outside the approved scheme | threshold: zero; an invalid code cannot be grouped with others in the same industry for concentration measurement | **(¶40)**
  - *consistency* — Industry classification is applied consistently to the same counterparty across business lines; the same obligor is not coded as "manufacturing" in one system and "industrial conglomerates" in another | count of counterparties with conflicting industry codes across source systems | threshold: zero; a conflict means the counterparty's industry exposure is split across buckets and concentration is understated | **(¶33)**

---

**CDE-08 — Position / As-Of Date**

- **Definition:** The date as of which an exposure or position is measured and stated — the business-date snapshot date. This is distinct from the trade date, settlement date, or report production date. It is the temporal anchor that makes aggregate figures comparable and reproducible.
- **Why critical:** Every aggregate risk figure is stated as of a date. Without a valid, populated as-of date, two records cannot be reliably combined into the same snapshot, and the bank cannot demonstrate that its aggregate covers the complete population as of the required date. ¶50 specifically requires the ability to produce aggregates "as of a specified date" — that capability depends entirely on every record carrying a reliable as-of date. It is also the key that a reconciliation to the general ledger uses to align populations.
- **Risk types:** Cross-cutting
- **Criticality: 3** — *Without this element, the aggregate risk figure for any given reporting date cannot be computed, because there is no basis on which to select the population of records that constitute the snapshot; records from different dates would be mixed, producing a figure that is neither accurate nor attributable to any defined point in time.*
- **Driven by:** Principle 5 (¶44–45) — *"produce aggregate risk information on a timely basis"*; Principle 6 (¶50) — *"aggregate risk data quickly on country credit exposures as of a specified date"*; Principle 7 (¶53) — reconciliation requirements presuppose a common reference date
- **Search terms:** as-of date, position date, valuation date, snapshot date, reference date, reporting date, business date, effective date
- **Data quality requirements:**
  - *validity* — Every risk record carries a non-null as-of date that is a valid business date in the bank's trading calendar | count of records with null or non-calendar as-of dates | threshold: zero; a record without a valid date cannot be assigned to any snapshot | **(¶40)**
  - *timeliness* — Risk records for a given business date are available in the aggregation layer within the latency window defined by the bank's frequency requirements for each risk type | count of records for business date D that are absent from the aggregation layer after the agreed cut-off time for risk type R | threshold: zero records missing after cut-off; the frequency requirement is set by the bank per ¶45 and ¶47, differentiated by risk type (e.g., intraday for trading exposures, next morning for credit) | **(¶45, ¶47)**
  - *consistency* — The as-of date on a risk record matches the value date or position date on the corresponding GL entry for the same instrument | count of records where risk as-of date differs from GL value date by more than the bank's stated tolerance | threshold: set by materiality; a systematic one-day lag is a reconciliation failure under ¶36(c) | **(¶36(c))**

---

**CDE-09 — GL / Source System Reconciliation Key**

- **Definition:** The identifier — typically a transaction reference, trade ID, or account number — that links a risk data record to the corresponding entry in the general ledger or the authoritative source booking system. This is not a risk-calculation field; it is the audit trail that makes accuracy provable.
- **Why critical:** ¶36(c) requires risk data to be reconciled with accounting sources. Without a reconciliation key on every risk record, the reconciliation cannot be performed at the record level: the bank can compare totals but cannot identify which specific records are causing differences. This makes ¶36(c) compliance a matter of assertion rather than evidence. ¶53(a) requires defined processes to reconcile reports to risk data, which presupposes that the linkage exists at the record level. A risk aggregate that cannot be reconciled to the GL is, under the standard, an untrustworthy figure.
- **Risk types:** Cross-cutting
- **Criticality: 3** — *Without this element, the reconciliation of risk data to the general ledger required by ¶36(c) cannot be performed at the record level; aggregate differences cannot be attributed to specific positions, so accuracy cannot be evidenced — only asserted.*
- **Driven by:** Principle 3 (¶36(c)) — *"Risk data should be reconciled with bank's sources, including accounting data where appropriate, to ensure that the risk data is accurate"*; Principle 7 (¶53(a)) — *"Defined requirements and processes to reconcile reports to risk data"*
- **Search terms:** trade reference, transaction ID, deal ID, account number, booking reference, GL account key, source transaction reference, position ID, instrument ID, folio number
- **Data quality requirements:**
  - *completeness* — Every risk record for an instrument that has a corresponding GL entry carries a non-null reconciliation key | count of risk records without a reconciliation key where a GL entry is expected | threshold: zero; a missing key makes that record unreconcilable and the accuracy of its exposure amount unverifiable — the failure is structural, not marginal | **(¶43, ¶36(c))**
  - *validity* — Every reconciliation key on a risk record resolves to an active record in the GL or source booking system | count of records where the reconciliation key does not match any GL or source-system record | threshold: zero; an unresolvable key is as bad as a missing one — the record is orphaned from the system of record | **(¶40)**
  - *uniqueness* — A single GL transaction is not represented by multiple conflicting risk records (i.e., the key is not duplicated in a way that would double-count exposure) | count of risk records sharing the same reconciliation key where only one GL entry exists | threshold: zero double-counted keys; a duplicate key inflates the aggregate and cannot be detected without this check | **(¶33, ¶36(c))**

---

**CDE-10 — Source System / Provenance Flag**

- **Definition:** The identifier of the system or process that originated a risk data record — for example, "core banking system," "derivatives platform," "spreadsheet/EUC," or "manual entry." Where the record originates from an end-user computing (EUC) tool or manual process, this flag is the primary control indicator.
- **Why critical:** ¶36(b) requires that where a bank relies on manual processes and desktop applications, effective mitigants and controls must be in place and consistently applied. ¶39 requires documentation and explanation of all manual processes, including their criticality to accuracy. Without a provenance flag, the bank cannot distinguish automated-system records from manual-entry or EUC records, cannot apply differentiated controls to each, and cannot produce the inventory of manual processes that ¶39 requires. Supervisors specifically look for this: a catalog with no source-system lineage has no way to demonstrate that EUC controls are operating.
- **Risk types:** Cross-cutting
- **Criticality: 2** — The aggregate figure is produced, but the bank cannot demonstrate whether it came from controlled automated sources or from unvalidated manual inputs. The aggregate is unverifiable in a regulatory examination context, and the EUC control regime of ¶36(b) cannot be evidenced.
- **Driven by:** Principle 3 (¶36(b)) — *"effective mitigants in place (eg end-user computing policies and procedures) and other effective controls that are consistently applied"*; ¶39 — *"banks to document and explain all of their risk data aggregation processes whether automated or manual"*
- **Search terms:** source system, source system ID, feed name, originating system, data source, system of origin, input method, EUC flag, manual override flag, data lineage, upstream system
- **Data quality requirements:**
  - *completeness* — Every risk record carries a non-null source system identifier | count of records with null or blank source system field | threshold: zero; a record without provenance cannot be classified for control purposes | **(¶43)**
  - *validity* — Source system codes reference an approved system inventory; unknown or ad hoc codes are flagged | count of records with source codes absent from the approved inventory | threshold: zero; an unrecognised source cannot be assessed for control adequacy under ¶36(b) | **(¶40)**
  - *accuracy* — Records flagged as originating from EUC or manual processes are subject to the additional controls required by ¶36(b); the volume and materiality of EUC-sourced exposure is tracked | percentage of total exposure amount attributable to EUC or manual-entry sources, reported separately | threshold: no fixed threshold — the requirement is that EUC exposure is identified and its materiality assessed; trend increases above a bank-defined threshold trigger review per ¶39 | **(¶39, ¶36(b))**

---

**CDE-11 — Collateral / Credit Risk Mitigant Identifier**

- **Definition:** The identifier linking an exposure to any collateral, guarantee, netting agreement, or credit risk mitigant that reduces net exposure. Captures whether mitigation exists and links to the mitigant record, not the valuation of the mitigant itself.
- **Why critical:** ¶41 requires coverage of all material risk exposures, including off-balance-sheet items. Net exposure — the figure used in capital adequacy and concentration reporting — cannot be correctly computed without knowing whether a mitigant applies. A missing or broken mitigant link overstates net exposure; an incorrectly applied one understates it. ¶58 requires reports to identify concentrations and provide information in the context of limits, which requires net exposures. This element does not drive the same structural invalidity as the keys in CDE-01, -02, -08, -09, but its absence distorts the net figure used in capital reports.
- **Risk types:** Credit, counterparty credit, concentration
- **Criticality: 2** — Gross exposure aggregates are produced correctly, but net exposure figures — used in capital adequacy and limit monitoring — are overstated or understated. The report exists but conveys a materially incorrect risk position where mitigants are significant.
- **Driven by:** Principle 4 (¶41) — *"risk data aggregation capabilities should include all material risk exposures, including those that are off-balance sheet"*; Principle 8 (¶58) — *"provide information in the context of limits and risk appetite/tolerance"*
- **Search terms:** collateral ID, collateral reference, netting agreement ID, guarantee reference, credit risk mitigant, ISDA agreement ID, collateral pool ID, mitigant type, eligible collateral flag
- **Data quality requirements:**
  - *completeness* — Every exposure record for which a collateral or netting agreement is known to exist carries a non-null mitigant identifier | count of exposure records where a mitigant is expected (based on facility terms) but no mitigant ID is populated | threshold: zero for material individual exposures; governed by ¶43's materiality standard for portfolios, with exceptions documented | **(¶43)**
  - *validity* — Mitigant identifiers resolve to active records in the collateral management or netting agreement register | count of mitigant identifiers on exposure records that do not resolve in the collateral register | threshold: zero; an unresolvable mitigant ID means the mitigation cannot be applied to the net exposure calculation | **(¶40)**
  - *accuracy* — The mitigant-to-exposure linkage reflects current legal enforceability; expired, challenged, or cross-jurisdictional mitigants are flagged | count of mitigant links where the mitigant record shows an expired or legally uncertain status | threshold: zero unreviewed expired links; materiality governed by ¶56 — if a large mitigant expires unnoticed, the net exposure figure is materially wrong | **(¶56, ¶40)**

---

## 3. Cross-cutting data quality requirements

---

**XDQ-01 — Cross-system counterparty reconciliation (golden-record resolution)**

- **CDEs spanned:** CDE-01 (Counterparty Identifier), CDE-03 (Gross Exposure Amount), CDE-05 (Business Line), CDE-06 (Geography)
- **Requirement intent:** A single real-world counterparty may appear under different internal identifiers in the lending system, the derivatives system, the securities financing system, and the collateral management system. Before any counterparty-level aggregate is computed, these must be resolved to a single golden record. This resolution cannot be verified by monitoring any single CDE in isolation — it requires cross-system matching. ¶33 requires single identifiers or unified naming conventions; ¶36(c) requires reconciliation to sources; ¶46(a) and ¶46(b) make counterparty concentration one of the named critical risk measures.
- **Rule intent:** Confirm that every counterparty appearing in more than one source system is linked to the same golden-record identifier, so that the sum of exposures across systems represents the true single-counterparty total.
- **Measurement:** Count of real-world counterparties (identified by LEI or other external reference) that carry two or more distinct internal counterparty identifiers across source systems without a documented golden-record mapping; separately, count of golden-record mappings that have not been reviewed within the bank's defined refresh cycle.
- **Threshold:** Zero unmapped multi-system counterparties. The threshold is zero — not a materiality percentage — because even a single large counterparty mapped to two identifiers causes a silent understatement of concentration. ¶33's requirement for single identifiers is absolute, not approximate; ¶46(a) names the aggregated credit exposure to a large corporate borrower as a critical risk requiring rapid production.
- **Paragraph authorisation:** (¶33) for the single-identifier requirement; (¶36(c)) for the reconciliation obligation; (¶46(a), ¶46(b)) for why counterparty aggregation is a named critical risk.

---

**XDQ-02 — Risk-to-finance reconciliation (aggregate-level)**

- **CDEs spanned:** CDE-03 (Gross Exposure Amount), CDE-08 (Position/As-Of Date), CDE-09 (GL Reconciliation Key), CDE-02 (Legal Entity Identifier)
- **Requirement intent:** At each reporting date, the total exposure amounts in the risk data aggregation layer must reconcile to the corresponding balances in the general ledger for the same legal entity and as-of date. This is a population-level check that sits above any individual record's reconciliation key: it verifies that the sum of matched records equals the GL total, and that unmatched records are explicitly identified and explained. It cannot be performed by monitoring any single CDE; it requires joining the risk population to the GL population and comparing totals. ¶36(c) mandates this reconciliation; ¶53(a) requires defined processes for it; ¶56 sets a materiality standard for accuracy thresholds.
- **Rule intent:** Confirm that the total gross exposure in the risk system for a given legal entity as of a given business date agrees with the corresponding balance in the general ledger, within the bank's materiality tolerance; and that all items in the break (where risk total ≠ GL total) are individually identified, valued, and escalated.
- **Measurement:** Absolute and percentage difference between the summed gross exposure amount in the risk aggregation layer and the corresponding GL balance, by legal entity and as-of date; count and aggregate value of unreconciled items (records in risk with no GL match, and GL items with no risk record); age of unreconciled items.
- **Threshold:** The reconciliation difference must not exceed the bank's stated materiality threshold, which is set by senior management per ¶56's analogy to accounting materiality. Zero is not the right threshold — ¶54 acknowledges that approximations are part of risk reporting. The appropriate standard is that no omission or misstatement could influence the risk decisions of users. The threshold is owned by the Chief Risk Officer or CFO, not by the data catalog team. Unreconciled items above the threshold must be escalated per the action plans required by ¶40.
- **Paragraph authorisation:** (¶36(c)) for the reconciliation mandate; (¶53(a)) for defined reconciliation processes; (¶56) for the materiality-based threshold; (¶40) for escalation requirements.

---

**XDQ-03 — EUC / manual-process exposure materiality**

- **CDEs spanned:** CDE-10 (Source System / Provenance Flag), CDE-03 (Gross Exposure Amount), CDE-09 (GL Reconciliation Key)
- **Requirement intent:** ¶36(b) requires effective mitigants for manual and EUC-sourced data, consistently applied. ¶39 requires documentation of all manual processes and their criticality to accuracy. Neither requirement can be evidenced by monitoring the provenance flag alone: the critical question is what proportion of the *monetary exposure* in the aggregate is derived from EUC or manual sources, and whether that proportion has grown. A provenance flag that marks 1% of records but 40% of exposure by value is a materially different control problem from one that marks 1% of both records and exposure.
- **Rule intent:** Measure the total exposure amount attributable to EUC or manual-entry source systems as a proportion of total aggregated exposure, by risk type and legal entity; flag trends that indicate growing reliance on uncontrolled manual inputs.
- **Measurement:** Ratio of total exposure amount where source-system flag = EUC or manual, to total exposure amount, computed by risk type and legal entity; month-on-month change in that ratio; count of distinct EUC processes contributing to the risk aggregate, compared to the inventory documented per ¶39.
- **Threshold:** No regulatory floor — ¶39 does not prohibit manual processes. The threshold is set by the bank's EUC policy, which must exist per ¶36(b). What the regulation requires is that the figure is measured, the trend is known, and any process above a bank-defined materiality level has documented controls and remediation plans. An undocumented EUC process of any size is a breach of ¶36(b) regardless of its monetary value.
- **Paragraph authorisation:** (¶36(b)) for the EUC control requirement; (¶39) for the documentation and criticality-assessment requirement; (¶40) for the measurement and escalation mandate.

---

## 4. Out of scope

The following matters arise from Principles 1–11 but cannot be addressed by CDE registration or data quality monitoring. They require governance processes, report design, human judgment, and board-level decisions that sit outside what a catalog can provide or enforce.

---

**Principles 1 (Governance) — ¶27–31**
Partially in scope, mostly out of scope. The CDE register supports ¶30's requirement to identify data critical to risk data aggregation, and ¶34's requirement for data ownership to be assigned. Catalog stewardship assignments and policy documentation partially address this.

What the catalog *cannot* deliver: board approval of the aggregation framework (¶28), independent validation of compliance with the Principles (¶29(a)), due-diligence assessment of acquisition targets' aggregation capabilities (¶29(b)), or senior management's escalation and remediation plans (¶30). These are governance and organisational matters. A catalog can record that a data owner exists; it cannot make the board accountable.

---

**Principle 2 (Data architecture and IT infrastructure) — ¶32–35**
Partially in scope. ¶33's requirements for integrated taxonomies, metadata, and single identifiers are directly addressed by CDE-01, CDE-02, and the uniqueness and consistency checks above.

What the catalog *cannot* deliver: the IT architecture decisions that make integration possible (¶32, ¶35), business continuity planning and business impact analysis for data systems (¶32), or the assignment and enforcement of data ownership roles across business and IT (¶34). A catalog can document ownership and flag gaps; it cannot create the IT infrastructure or enforce that controls operate throughout the data lifecycle.

---

**Principle 6 (Adaptability) — ¶48–51**
Partially in scope. The aggregation dimensions in CDE-05, CDE-06, CDE-07 and the as-of date in CDE-08 enable the specific slice-and-dice example in ¶50 (country exposures by industry across business lines as of a specified date). A well-governed catalog with complete, valid dimension fields is a precondition for adaptability.

What the catalog *cannot* deliver: the technical capability to execute ad hoc queries rapidly (¶48–49), the ability to incorporate new business structures or regulatory changes into live systems (¶49(c)–(d)), or stress-testing and scenario analysis capabilities (¶48). Adaptability is a system architecture and query capability requirement; catalog completeness is a necessary but not sufficient condition.

---

**Principle 7 (Accuracy in reports) — ¶52–56**
Partially in scope. ¶36(c) and ¶53(a) are directly addressed by CDE-09 and XDQ-02. The materiality standard in ¶56 is cited as the basis for exposure and reconciliation thresholds.

What the catalog *cannot* deliver: the actual reconciliation process (¶53(a)), the edit and reasonableness checks applied to reports (¶53(b)), exception reporting procedures (¶53(c)), or management's decision about what level of approximation is acceptable (¶55). These are operational processes and management judgments. The catalog provides the data lineage and the raw quality metrics; the reconciliation and sign-off process is outside it.

---

**Principle 8 (Comprehensiveness) — ¶57–60**
Partially in scope, and this is a case where the same principle drives both a CDE and an out-of-scope obligation — a split that must be explained rather than left as an apparent contradiction.

CDE-07 (Industry/Sector Classification) is driven by ¶57's requirement to report by industry sector. That is a *data* requirement: the field must exist, be populated, and be governed. The catalog addresses it.

What the catalog *cannot* deliver: the report itself covering all significant risk areas (¶57), forward-looking forecasts and stress-test results in reports (¶58, ¶60), the decisions about risk coverage, analysis and interpretation, scalability, and comparability across group institutions (¶59), or the board's assessment of whether it is receiving the right information (¶60). These are report-content, analytical, and governance obligations that no amount of data-quality monitoring fulfils.

---

**Principle 9 (Clarity and usefulness) — ¶61–69**
Entirely out of scope. Principle 9 governs the *design* and *content* of risk reports — the balance between quantitative and qualitative information (¶62), differentiated reporting for board versus senior management versus risk committees (¶63), and periodic confirmation that recipients find the reports useful (¶69). The catalog supports one sub-element: ¶67's requirement for an inventory and classification of risk data items, which is addressed by the CDE register itself. Everything else — how a report is written, whether it is clear, whether the board confirms it is adequate — is out of catalog scope.

---

**Principle 10 (Frequency) — ¶70–71**
Entirely out of scope. Setting report frequency (¶70), testing the ability to produce reports within required timeframes (¶70), and ensuring intraday availability of position reports in a crisis (¶71) are operational and reporting-process requirements. The timeliness DQ checks on CDE-08 measure whether records are available within the bank's stated latency window, but the catalog does not set that window, enforce report publication schedules, or test stress-scenario production. Those are system performance and operational resilience matters.

---

**Principle 11 (Distribution) — ¶72–74**
Entirely out of scope. Report distribution procedures, access controls, confidentiality management, and confirmation that recipients receive timely reports are information security and operational governance matters. A catalog can document data classification and sensitivity (which supports ¶27's confidentiality requirement), but it cannot govern who receives a report, by what channel, or within what deadline.

---

## 5. Summary table

| CDE | Name | Criticality | Principles | DQ dimensions |
|---|---|---|---|---|
| CDE-01 | Counterparty Identifier | 3 | 2 (¶33), 4 (¶41), 5 (¶46) | uniqueness, validity, consistency |
| CDE-02 | Legal Entity Identifier (Own Entity) | 3 | 2 (¶33), 4 (¶41), 3 (¶36c) | validity, completeness, consistency |
| CDE-03 | Gross Exposure Amount | 3 | 3 (¶36), 4 (¶41), 7 (¶52, ¶56) | accuracy, completeness, validity |
| CDE-04 | Risk Type Classification | 2 | 8 (¶57), 5 (¶45) | validity, completeness, consistency |
| CDE-05 | Business Line | 2 | 4 (¶41–43), 6 (¶50) | completeness, validity, consistency |
| CDE-06 | Geography / Country of Risk | 2 | 4 (¶41), 6 (¶50) | completeness, validity, accuracy |
| CDE-07 | Industry / Sector Classification | 2 | 8 (¶57), 6 (¶50) | completeness, validity, consistency |
| CDE-08 | Position / As-Of Date | 3 | 5 (¶44–45), 6 (¶50), 7 (¶53) | validity, timeliness, consistency |
| CDE-09 | GL / Source System Reconciliation Key | 3 | 3 (¶36c), 7 (¶53a) | completeness, validity, uniqueness |
| CDE-10 | Source System / Provenance Flag | 2 | 3 (¶36b, ¶39) | completeness, validity, accuracy |
| CDE-11 | Collateral / Credit Risk Mitigant Identifier | 2 | 4 (¶41), 8 (¶58) | completeness, validity, accuracy |
| XDQ-01 | Cross-system counterparty reconciliation | — | 2 (¶33), 3 (¶36c), 5 (¶46) | uniqueness, consistency |
| XDQ-02 | Risk-to-finance aggregate reconciliation | — | 3 (¶36c), 7 (¶53a, ¶56) | accuracy, completeness, consistency |
| XDQ-03 | EUC / manual-process exposure materiality | — | 3 (¶36b, ¶39), 3 (¶40) | accuracy, completeness |