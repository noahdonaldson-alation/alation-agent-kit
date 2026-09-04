# BCBS 239 AI Governance — where this stands

For Aaron and the team. Companion to the recorded walkthrough.

---

## What it does

A Deployment Strategist pastes a regulation into Alation, and in the same
session ends up with a governance framework that traces from a numbered
paragraph to a column in a warehouse — with a human approving at every step.

```
regulation text
   → obligations, one per principle                  agent, in the UI
   → business policies                               agent, in the UI
   → CDE overlay standards                           Alation's own AI, in CDM
   → critical data elements + their columns          agent, in the UI
   → audit: what is governed, what is missing        agent, in the UI
```

Every scene is in the Alation UI. Nothing on the demo path runs from a terminal.

---

## What was built

**Four agents on the demo path.** An obligation interpreter that reads the
regulation; a policy creator that turns obligations into Policy Center entries; a
CDE creator that reads published standards, works out which data elements they
require, finds the physical columns and attaches both in one call; and a
governance reporter that audits the whole chain read-only.

**Fourteen custom HTTP tools**, plus five of Alation's own base tools where they
were better than anything we would have written.

**A CLI with fourteen commands** for the setup half — deploying prompts and
agents, provisioning and repairing objects, and measuring prompt quality across
runs.

Four earlier agents remain in the repo as the terminal pipeline. They are
superseded on the demo path but not deleted: one of them still offers a guarantee
the chat path cannot (see *Citations*, below).

---

## The three pillars

**Openness.** The bank's own regulation and policy language drive everything.
Nothing is hardcoded to BCBS 239 except the content — the machinery reads
whatever document it is given.

**Governed.** A single column ends up governed by several regulatory principles
at once, each traceable back through a standard to a policy to a paragraph. On
the current instance, `Position As-of Date` carries four BCBS 239 standards and
binds to three physical columns across bronze, silver and gold.

**Feedback loop.** The audit runs before anything exists and again afterwards.
The second run is the payoff: what remains is a *data* gap, not a governance gap
— three concrete engineering asks rather than a compliance score.

---

## How reusable it is

The bet was to separate the machinery from the content, and it held.

**The engine is regulation-agnostic.** Nothing in the agents, tools or CLI knows
what BCBS 239 says. The interpreter reads any regulation; the policy creator
takes any obligation register; the CDE creator reads whatever standards exist;
the reporter audits whatever chain it finds.

**A second regulation costs content, not code.** Point the interpreter at a new
document, review the obligations it proposes, and the rest of the chain runs
unchanged.

**The catalog side generalises too.** The CDE creator searches whatever catalog
it is pointed at, so a customer's own warehouse works the same way ours does — it
reads column names, types and descriptions and matches semantically.

**One real dependency on preparation:** the quality of the match depends on the
quality of the catalog's descriptions. This is measured, not asserted — on a bare
catalog one element found nine candidate columns; after Curation Automation with
finance-specific prompts, fifteen. Curation is a prerequisite, not a nicety.

---

## What was deliberately not built, and why

**Data quality monitors.** Scoped properly and closed as a point-in-time finding
against Alation 2026.7.1. Three writes are needed to provision DQ from an agent —
create a DQ standard, create a monitor, and set a column as a control point on an
existing element — and all three are blocked. Each takes a bare JSON array as its
request body, which an Agent Studio HTTP tool cannot produce, and the DQ standard
endpoint additionally has no public API at all and authenticates by browser
session cookie rather than by our token.

So DQ is a declared prerequisite: a human creates the standards once in the UI
and they are reusable across every element. **The product ask is three
body-shape decisions, not a capability gap** — object-bodied, bearer-authenticated
endpoints for those three operations. Alation's own policy API already concedes
the pattern in its error text: *"Single item payload processing not supported,
for now."*

**Column discovery by CDM.** Alation's `DATA_MAPPING` matches synonyms it
generates from an element's description — but that generation happens in the UI
wizard, so an API-created element has no synonyms and discovery matches nothing.
Measured across seven elements, every attempt, same result. The agent now reads
the catalog and matches semantically instead, which is the better result: it
reasons about a column's type and its table, and a lexical matcher cannot.

This is an honest cost to the story. The demo can no longer claim the product
found the columns unaided. What it claims instead is truer — an agent read the
catalog, explained why each column matched, and a steward accepts.

**Regulation as a PDF in the catalog.** Blocked on a feature flag only an FDE can
enable. The regulation currently arrives as pasted text. Nothing else changes
when it lands — the same agent, the same output.

**Authoring the standards ourselves.** Deliberate. Alation's AI derives them from
the policy prose, and it does it better than we would: one policy of about 3,700
characters produced nine requirements and roughly thirty-eight attestation
fields, with the register's evidence sentences converting almost one-for-one into
field names.

---

## What a customer needs to know before running this

**Published overlay standards are permanent.** They cannot be deleted,
unpublished or rolled back — and publishing is *required* for them to govern
anything. Reversible or functional, never both. Every working deployment leaves
objects behind.

**Policy churn orphans standards, silently.** A standard outlives its source
policy. Delete a policy and its standard remains, still attached to elements,
still claiming a derivation from a document that no longer exists — and nothing
in the UI shows it. We found this by accident on our own instance, where six of
seven standards were affected. It is the strongest argument for reviewing the
obligation register *before* policies are created: getting the set wrong does not
cost a re-run, it costs permanent debris.

**Curation Automation should run first**, with vertical-specific prompts against
the customer's own data.

---

## Citations, and one thing worth understanding

The pipeline reproduces the regulation's exact words in the policies it creates,
and that turned out to be the hardest thing in the project.

Asked to quote BCBS 239, a model produces quotations that are *verbatim correct
and absent from the source we gave it* — recalled from training rather than read.
Accurate recall is precisely what makes it dangerous: on a customer's internal
policy pack the same behaviour yields invented quotes indistinguishable from real
ones. Instruction reduced it and never eliminated it.

The terminal pipeline solves this structurally: the agent emits a *pointer* and
code substitutes the register's exact text, so an untraceable quote is impossible
by construction. The in-UI path cannot do that — there is no code step — so it
copies the quote and must show which obligation each came from, making the
approval gate a real check rather than a formality.

**Both paths are kept, and they differ in guarantee rather than capability.** The
demo uses the conversational one. Anything audited should use the other.

---

## What is left

**Rehearse on a clean tenant.** The opening audit is meant to run against a
catalog with nothing built. Our instance's standards are permanent, so that scene
can only be rehearsed properly somewhere fresh.

**Data quality**, if and when the endpoints change.

**Aaron's open question — the five horizontal building blocks.** Still
undefined, and it is what all of this is meant to decompose into.
