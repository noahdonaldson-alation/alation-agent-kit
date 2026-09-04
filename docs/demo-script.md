# BCBS 239 demo script — v0.2

For a Deployment Strategist. Roughly 25 minutes, seven scenes, three pillars.

**The arc:** show a real gap → build the governance that closes it → show what is
still genuinely missing. It opens on tension and ends on a remediation list, not
on "all green."

**The claim:** *upload a regulation, and build your governance framework in
conversation with it.*

> **What changed from v0.1.** Scene 6 has been rewritten. CDM's `DATA_MAPPING`
> discovery does not work on API-created CDEs — synonym generation is a UI step,
> so an agent-created element has no synonyms and discovery matches nothing.
> Measured across seven elements, every trigger, same error. The agent now finds
> the columns itself by reading the catalog, which is a *different claim* and a
> truer one. Scene 3's hook also changed: business line, legal entity and
> geography turned out to be present all along.

---

## Before the room

| Prerequisite | Where | Notes |
|---|---|---|
| Data source connected, metadata harvested | UI | MCF Snowflake, `alation://data/2` |
| Custom fields created | UI | `PII Classification`, `Sensitivity Classification`, `CDM (contains CDE)` |
| **Curation Automation run, vertical-specific prompts** | UI | Load-bearing. See scene 2 |
| Policy group exists | UI | Groups have no create API. `BCBS 239`, id 1 |
| Agents + tools deployed | kit | `./run.sh deploy …`, `./run.sh tool deploy …` |
| **Published overlay standards** | CDM, once | Permanent. Published in setup, reused every run |

Everything above is **setup**, and Aaron's ruling covers it: setup may be
scripts, the end-to-end experience must be in the UI.

**Reset between demos.** Delete the CDEs from scene 6 and the policies from
scene 4 — both are deletable while they are drafts. Delete the draft standard
you generate in scene 5. **The published standards stay and are reused**, which
is what makes this repeatable rather than one-and-done. Scene 5 shows the
generation and the trim; it does not publish.

> **Say this to a customer before running anything in their instance:** a
> published overlay standard is permanent — it cannot be deleted, unpublished or
> rolled back — and publishing is *required* for it to govern anything. Reversible
> or functional, never both. Every working deployment of this leaves objects
> behind. Alation ships `recall`, `restore` and `bulk_delete` for CDEs and has not
> extended them to Standards; that is the product ask.

---

## 1 — The catalog (2 min) · *context*

Open the data source. Tables, columns, lineage — technical metadata, harvested.

> "This is what most catalogs are. It tells you what exists. It doesn't tell you
> what matters, who owns it, or whether a regulator would accept it."

Sets up why the rest is needed. Do not linger.

---

## 2 — Curation (3 min) · *pillar 1: openness*

Show the curation rule and what it produced — descriptions, owners, trust flags
and classification fields that a steward didn't hand-write.

**The best-practice point, and say it explicitly:** run **vertical-specific**
Curation Automation prompts against the customer's own data, not the stock ones.
Ours came from `#industry-vertical-financialservices`. A financial-services
prompt set describes columns in the vocabulary the *regulation* uses — which is
what every downstream step reads.

**This scene is load-bearing, not decorative, and now you can say why.** In scene
6 an agent reads these descriptions to decide which physical columns hold a
regulated data element. Generic descriptions produce generic matches.

The measured version, if someone pushes: on a bare catalog with keywords held
constant, discovery for one element found 9 columns; after curation, 15. That is
the only clean before/after we have — the other two comparisons changed more than
one variable — so quote that one and no other.

---

## 3 — The gap, before anything exists (4 min) · *the hook*

Agent Studio chat. Ask what the catalog can evidence against BCBS 239 as it
stands.

> "Here's BCBS 239. Here's your catalog. What can you actually evidence?"

The output names what is missing and why it matters — not "6 gaps found" but a
specific, checkable claim.

**This is the strongest moment in the demo.** Let it sit.

> ⚠️ **The v0.1 hook is dead — do not use it.** It said there was no business
> line, legal entity or geography attribute on any risk record. All three exist:
> `BUS_LINE_CD`, `LE_CD`, `COUNTRY_OF_RISK_CD`, plus `NACE_CD` and
> `RISK_TYPE_CD`. They were never missing; nobody had searched with the right
> vocabulary.

**The real gaps, all found by the agent unprompted, all still true:**

- **No reconciliation run date.** The policy requires the identifier, date and
  outcome of every reconciliation run. There is no `RECON_RUN_DT` anywhere; the
  reconciliation view carries the position date instead.
- **No accuracy measurement.** No `DQ_SCORE`, `ACCURACY_RATE` or threshold
  column. The obligation to measure accuracy against an approved threshold cannot
  be evidenced from this warehouse at all.
- **A schema defect it found while doing something else.**
  `COUNTRY_OF_RISK_CD` is `VARCHAR(2)` in bronze and `VARCHAR(16777216)` —
  Snowflake's unbounded string — in silver and gold. Nobody asked it to check
  column types.

That last one is worth a beat of its own. It is the difference between a search
and an analyst.

---

## 4 — Policies, in conversation (5 min) · *pillar 1: openness*

Same chat. Paste the BCBS 239 text.

The agent proposes the policies the regulation implies — one per principle, each
cited to numbered paragraphs. You review the list on screen. You say yes. It
creates them: shell, title, description, policy group, one at a time.

> "You didn't fill in a form. You agreed to a list."

Open Policy Center. Seven policies, each quoting the paragraphs it derives from.

**What to point at:** the verbatim quotations. Every one is reproduced from the
source document by code, not written by a model — the agent emits a *pointer* and
the kit substitutes the exact text, so a citation cannot drift. That design
exists because a model asked to transcribe quotes it accurately from memory
instead, which is worse than getting them wrong.

> 📌 Interpretation still runs in the kit; only creation is conversational.
> Folding both into one chat agent is what makes this scene land as written.

---

## 5 — Standards, generated by Alation (4 min) · *pillar 2: governed*

CDM → Standards → **Add new Standard** → pick a policy → **Create**.

Alation's own AI reads the policy body and derives the requirements. Wait for it.

> "We didn't write these. Alation read the policy and worked out what a steward
> has to be able to prove."

Open it: requirements, attestation fields, pickers with real answer sets.
**Trim it live** — drop the requirements that are enterprise-level rather than
per-element, and say why. Then explain that publishing is the step that makes it
govern, and that it is deliberate, reviewed and permanent.

**Do not publish.** Delete this draft afterwards; that is the reset. The
standards you attach in scene 6 were published during setup.

**The point to make, because it is the design principle:** the specificity of the
policy prose is what makes the standard useful. One ~3.7k-character policy
produced nine requirements and around thirty-eight attestation fields, and the
evidence sentences in the policy became field names almost one for one. A vague
policy does not produce a vague standard — it produces a generic one.

---

## 6 — Critical data elements, in conversation (6 min) · *pillar 2: governed*

Same chat, different agent. Point it at the published standards.

> "These are the standards. What data do we need to prove any of it, and where
> does that data live?"

It reads every standard's derived requirements, works out the elements they
require, searches the catalog for the physical columns, and proposes — with the
reasoning visible.

**Four things to point at, in this order:**

**It reasons about types, not just names.** Bronze `EXPOSURE_AMT` is
`VARCHAR(20)` — a staging string, not the amount being aggregated — and it says
so while including it for lineage. A keyword match cannot make that distinction.

**It refuses to invent elements.** Asked what the standards require, it declines
to create CDEs for *Approved Accuracy Threshold* or *Reconciliation Frequency*,
because those are attestation fields inside the standard rather than columns in a
warehouse.

**One element, several principles.** `Position As-of Date` carries four
standards; `Gross Exposure Amount` three. This is the Governed pillar in a single
screen — one column, governed by four principles, each traceable to a policy and
back to a numbered paragraph.

**Everything lands as a suggestion.** You approve the list, then open the created
CDE in CDM: standards attached, physical columns marked `Suggested`, source paths
showing which table each came from, the whole element at **In Draft** on a
Candidate → Draft → In Review → Certified stepper. Nothing was asserted; a
steward accepts.

> ⚠️ **Say what this is, precisely.** The agent found the columns — Alation did
> not. Earlier versions of this demo claimed CDM's discovery found them from the
> element's description; that does not work on API-created elements. The honest
> claim is stronger anyway: an agent read your catalog, explained why each column
> matched, named what was missing, and a human accepts.

**Data quality — optional, and worth knowing why.**

The Data Quality tile reads `N/A`, and that is a deliberate stopping point rather
than an unfinished one. Monitors cannot be created by an agent on Alation
2026.7.1: creating a DQ standard, creating a monitor, and changing a PDE's
relationship on an existing element are all blocked by request bodies we cannot
produce from a tool, and the DQ standard endpoint additionally has no public API
and authenticates by session cookie. Full detail in CLAUDE.md.

**So DQ is setup, like RBAC and policy groups — and the demoer chooses.** Two
honest ways to play the scene:

- **Leave it empty and make it the finding.** "Nothing is monitoring these
  elements yet, and the framework has just told you which nine need it." That
  leads straight into scene 7 and costs nothing.
- **Build it live, if you have five minutes and a prepared standard.** Data
  Quality → Standards → New Standard once, then on a CDE: Add Data Quality →
  pick the control point → apply the standard → schedule. It is four steps in the
  UI and it makes the tile real.

If you do build it, the alignment is worth saying out loud: Alation's check
categories are **Completeness, Accuracy, Validity, Uniqueness, Timeliness** — the
same dimensions BCBS 239 names, and the same ones the obligation register
carries. The regulation's vocabulary and the product's are the same vocabulary.

**One prerequisite the agent handles for you:** monitors can only be applied to
PDEs marked `control_point`, and `cde_creator` nominates the authoritative gold
column as the control point at create time. Without that, the wizard's column
list comes up empty and every element needs a manual promotion first.

---

## 7 — The loop (2 min) · *pillar 3: feedback*

Re-run the gap analysis.

What you built is now covered. What remains is a **data** gap, not a governance
gap — no reconciliation run date, no accuracy measurement — and that distinction
is the payoff.

> "That's your remediation list. And it's not a one-off — run it monthly, or when
> the regulation changes, and it tells you what moved."

End there. Do not end on "no gaps."

---

## Close

Three claims, in the customer's terms:

- **Open** — your regulation, your policy pack, read by the platform. Not ours.
- **Governed** — traceable from a paragraph in a regulation to a column in a
  warehouse, with a named human at every gate.
- **Feedback loop** — it re-runs, and it tells you what changed.

---

## Known seams

Honest list, because an SE walking into this should know where it is thin.

1. **Scene 6 has no DQ scores by default, and cannot have them without a human.**
   Scoped 2026-09-04 and closed as a point-in-time finding: DQ standard create,
   monitor create and PDE relationship update are all bare-array bodies, and the
   DQ standard endpoint has no public API and uses cookie auth. So monitors are a
   declared prerequisite built in the UI, not something the pipeline provisions.
   This is the biggest remaining hole in the pillar Aaron cares most about, and
   the fix is a product ask rather than a build — see CLAUDE.md for the exact
   three endpoints.
2. **Scene 4 is split** across kit and chat. Interpretation is a terminal step.
3. **Real PDF ingestion is blocked** on an FDE feature flag, so the regulation
   arrives as pasted text rather than as an S3 document in the catalog. That is
   the version of scene 4 you actually want.
4. **Published standards are permanent**, and publishing is required for them to
   function. State it before running anything in a customer instance.
5. **Policy churn orphans standards permanently.** A standard outlives its source
   policy and cannot be deleted, so deleting a policy leaves a standard behind
   claiming a derivation from a document that no longer exists. Get the policy set
   right before creating it; there is no cheap re-run.
6. **The agent's judgement varies between runs.** The mechanism is stable — it
   searches, reasons and merges every time — but three runs against the same
   standards produced nine, ten and six elements, and it reversed itself on
   whether surrogate keys belong to an element. An SE gets one take. Either
   rehearse against a pinned expectation, or make the variance the point: a
   customer's answer *should* differ from ours.
