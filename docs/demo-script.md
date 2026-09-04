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

## Read this before you book the meeting

Three things will bite you if you find them out on the day.

### 1. Run full Curation Automation on the catalog first

**This is not optional and it is not cosmetic.** In scene 6 an agent reads column
descriptions to decide which physical columns hold a regulated data element. On a
bare catalog it has nothing to read and the scene falls flat.

Run Curation Automation across **all objects** on the instance, and use
**vertical-specific prompts** rather than the stock ones — ours came from
`#industry-vertical-financialservices`. A finance prompt set describes columns in
the vocabulary the regulation itself uses, which is what every downstream step
matches against.

Measured, with keywords held constant: one element found **9** candidate columns
on a bare catalog and **15** after curation. Allow time for the run to finish
before you demo.

### 2. You must create DQ standards and DQ rules yourself, in CDM

Data quality cannot be provisioned by any agent or script on Alation 2026.7.1 —
the endpoints take a request shape our tools cannot produce, and the DQ standard
endpoint has no public API at all. See CLAUDE.md for the detail.

So before the demo, if you intend to show data quality at all:

- **Data Quality → Standards → New Standard.** Create at least one — Completeness
  with a missing-count check is the simplest. A standard is reusable across every
  element, so you only do this once.
- **Then apply it** to a CDE's control point via **Add Data Quality** on the
  element, and let a monitor run so the tile shows a real score.

If you skip this, the Data Quality tile reads `N/A` — which is a perfectly good
scene, see scene 6. Just decide which version you are doing beforehand.

### 3. Standards must be published to work, and can never be deleted

**A CDE cannot inherit anything from a draft standard.** Draft standards are not
even offered when attaching one to an element. Publishing is what makes a
standard govern.

**And a published standard is permanent.** It cannot be deleted, unpublished, or
rolled back. Editing one creates a new version; the old version stays in the
selector forever. There is no undo.

So: **reversible or functional, never both.** Every working deployment of this
leaves permanent objects in the customer's instance. Say so before you run
anything in their tenant, not after.

One more that follows from it, and it is the one nobody expects: **deleting a
policy orphans its standard, permanently and silently.** The standard survives,
still attached to elements, still claiming it derives from a document that no
longer exists — and nothing in the UI shows it. Get the policy set right before
you create it.

---

## Before the room

| Prerequisite | Where | Notes |
|---|---|---|
| Data source connected, metadata harvested | UI | MCF Snowflake, `alation://data/2` |
| Custom fields created | UI | `PII Classification`, `Sensitivity Classification`, `CDM (contains CDE)` |
| **Curation Automation run, vertical-specific prompts** | UI | See above. Load-bearing |
| Policy group exists | UI | Groups have no create API. `BCBS 239`, id 1 |
| Agents + tools deployed | kit | `./run.sh deploy …`, `./run.sh tool deploy …` |
| **Published overlay standards** | CDM, once | Permanent. Published in setup, reused every run |
| **DQ standards created** | CDM, once | Only if you are showing scene 6's DQ half |

Everything above is **setup**, and Aaron's ruling covers it: setup may be
scripts, the end-to-end experience must be in the UI.

**Reset between demos.** Delete the CDEs from scene 6 — they are drafts and they
delete cleanly. Delete the draft standard you generate in scene 5. **The policies
do not need deleting**: scene 4's agent finds the existing ones and offers to
update them rather than duplicate, which is both repeatable and a more realistic
customer scenario than pretending the catalog is empty. **The published standards
stay and are reused**, which is what makes this repeatable rather than
one-and-done.

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

**Two agents, one after the other. Both in Agent Studio.**

**First, `bcbs239_obligation_interpreter`.** Paste the regulation text —
`artifacts/bcbs239/bank_principles.txt`, about 25KB, pastes fine.

It returns an obligation register: one obligation per principle, each with the
quality dimensions it implies, what a steward must be able to produce, and the
paragraphs it derives from — quoted verbatim.

> "Nobody wrote these. It read the regulation."

**Then `policy_creator`.** Copy the register out and paste it in, with the owner
and group:

> Create the policies from this obligation register. Owner 1, policy group 1.

It maps each obligation to a policy, shows you the titles and the bodies, and
waits. You read them. You say yes. It creates each one — shell, title,
description, group — before starting the next.

> "You didn't fill in a form. You agreed to a list."

Open Policy Center and show one.

**Two things to point at:**

**The duplicate check.** On a second run it finds the existing policies, maps
each obligation to the one already there, and offers to update rather than
duplicate — matching on *meaning*, not on title. A real bank walks in with a
policy pack already, so this is the more credible scene, and it is what makes the
demo repeatable.

**Every quotation carries the obligation it came from.** That is what makes the
approval gate real: a citation without a reference beside it is visible on sight.
Say why it matters if asked — a model asked to quote a well-known regulation will
produce quotations that are word-perfect and *not in the source document*,
recalled rather than read. Showing the source is how a reviewer catches that.

> 📌 **The register is ~57KB of JSON on screen between the two agents.** Scroll
> past it, or have the interpreter lead with a readable summary. Know it is
> coming.

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

## Appendix — what to paste, in order

Everything below goes into Agent Studio. Nothing here is typed at a terminal.

### The regulation text

`artifacts/bcbs239/bank_principles.txt` — the bank-facing principles, about 25KB.
It is gitignored, so generate it once:

```bash
.venv/bin/python scripts/extract_bcbs239.py --download
```

That downloads BCBS 239 and writes per-principle files plus the combined one.
**Use the combined file** — obligations are cross-cutting, and the interpreter
needs the principles in view together.

When unstructured ingestion lands, this step becomes "point the interpreter at
the PDF in the catalog" and nothing else changes.

### Scene 3 — the "before" audit · `governance_reporter`

> Audit the BCBS 239 governance framework on this instance. Scope catalog
> searches to `alation://data/2` (MCF Snowflake). Walk the whole chain —
> policies, overlay standards, critical data elements, physical columns, data
> quality — and tell me where it breaks. Separate governance gaps from data gaps.

### Scene 4a — obligations · `bcbs239_obligation_interpreter`

Paste the contents of `bank_principles.txt`. No other instruction needed; the
prompt does the rest.

### Scene 4b — policies · `policy_creator`

Paste the register from 4a, then:

> Create the policies from this obligation register. Owner 1, policy group 1.

On a repeat run it will find the existing policies and offer to update them. Take
that option and tell it:

> Replace the descriptions only — leave the existing titles unchanged.

Keeping the titles preserves the `BCBS239 - ` prefix, which is how `policy
assess` identifies our objects.

### Scene 5 — standards · CDM, no prompt

Critical Data Manager → Standards → **Add new Standard** → choose a policy →
Create. Trim the generated draft live. **Do not publish** — the standards you
attach in scene 6 were published during setup. Delete the draft afterwards.

### Scene 6 — elements and columns · `cde_creator`

> Read overlay standards 641, 656, 657, 658 and 659 — ignore any others,
> including any standard derived from a policy that no longer exists. Work out
> the full set of critical data elements needed to evidence them, and for each
> element attach every standard it evidences. Search `alation://data/2` for the
> physical columns, including every medallion layer an element appears in, and
> nominate the authoritative gold-layer column as the control point. Propose
> before creating anything.

**Replace the standard ids with the ones on your instance** — `./run.sh policy
standards` lists them, or read them in CDM. Naming them explicitly is what keeps
the agent off any standard whose source policy has been deleted.

### Scene 7 — the "after" audit · `governance_reporter`

**Exactly the same prompt as scene 3, word for word.** Same question, different
answer, is the entire point. Do not reword it.

---

## Known seams

Honest list, because an SE walking into this should know where it is thin.

0. **Every prompt you need is in the appendix above**, along with where the
   regulation text lives and how to generate it. If you are running this for the
   first time, read the appendix before the scenes — the scenes explain what to
   say, the appendix has what to paste.

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
