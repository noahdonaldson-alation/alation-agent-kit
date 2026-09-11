# BCBS 239 — click-through capture spec

For building a Storyline walkthrough. Six steps, one screen each.

**Instance:** `finance-industry.mtse.alationcloud.com`
**Everything happens in the Alation UI.** No terminal, no code.

Each step below gives the screen, the action, the exact text to paste, what
appears, and what must be in frame for the capture.

---

## Step 1 — What can you evidence today?

| | |
|---|---|
| **Screen** | Agent Studio → Agents → `governance_reporter` |
| **Do** | Paste the prompt, send |
| **Shows** | A report: the framework exists, almost nothing is evidenced |
| **Capture** | The findings list. Scroll to the "data gaps" section |

**Paste:**

> Audit the BCBS 239 governance framework. Scope catalog searches to
> `alation://data/2`. Separate governance gaps from data gaps.

**Callout:** *"Before we build anything — what does the catalog actually prove?"*

---

## Step 2 — The regulation becomes obligations

| | |
|---|---|
| **Screen** | Agent Studio → Agents → `bcbs239_obligation_interpreter` |
| **Do** | Paste the BCBS 239 principles text, send |
| **Shows** | One obligation per principle, each with the quality dimensions it implies and the paragraphs it cites |
| **Capture** | Two or three obligations expanded — enough to see the citations |

**Paste:** contents of `artifacts/bcbs239/bank_principles.txt` (~25KB).

**Callout:** *"Nobody wrote these. It read the regulation."*

> **Capture note:** the output is long JSON. Frame on two obligations rather
> than the whole response.

---

## Step 3 — Obligations become policies

| | |
|---|---|
| **Screen** | Agent Studio → Agents → `policy_creator` |
| **Do** | Paste the register from step 2, then the prompt below |
| **Shows** | A proposed policy per obligation, then a confirmation table with ids and links after approval |
| **Capture** | The proposal list, then the created-policies table |

**Paste:**

> Based on the following obligations, tell me which policies I need to create for BCBS 239 <paste json from step 2>.

Then, when it asks:

> Do nothing else - Policies are staged for this already.

**Callout:** *"You didn't fill in a form. You agreed to a list."*

> **Capture note:** the register paste is ~57KB and looks bad on screen. Paste
> it off-camera and start the capture at the agent's proposal.

> Open Policy Center, one policy open in group BCBS 239, showing the quoted
paragraphs in the body.

---

## Step 4 — Alation derives the standard

| | |
|---|---|
| **Screen** | Critical Data Manager → Standards → **+ Add new Standard** |
| **Do** | Choose a BCBS 239 policy as the source → **Create** → wait |
| **Shows** | Requirements and attestation fields, generated from the policy prose |
| **Capture** | The generated requirements list, expanded to show field types |

No prompt. This is Alation's own AI doing the work.

**Callout:** *"We didn't write these. Alation read the policy and worked out what
a steward has to prove."*

> Have Standard open in CDM - "BCBS239 - Risk Data Timeliness"

---

## Step 5 — Elements and their columns

| | |
|---|---|
| **Screen** | Agent Studio → Agents → `cde_creator` |
| **Do** | Paste the prompt, review the proposal, approve |
| **Shows** | Proposed data elements, each with the standards it evidences and the physical columns found — with the reason each matched |
| **Capture** | The proposal table showing columns across bronze, silver and gold |

**Paste:**

> Read overlay standards 641, 656, 657, 658 and 659. Work out the critical data
> elements needed to evidence them, and for each one attach every standard it
> evidences. Search `alation://data/2` for the physical columns across every
> layer, and nominate the gold column as the control point. Propose first.

Then:

> Approved, create them.

**Callout:** *"It read the catalog and explained why each column matched."*

**Second screen, and this is the money shot:** CDM → Critical Data Elements →
**Position As-of Date**. Capture the Standards panel showing four BCBS 239
standards, and the Physical Data Elements table showing three columns with their
source paths.

**Callout:** *"One column. Four regulatory principles. Traceable to the
paragraph."*

---

## Step 6 — Run the check again

| | |
|---|---|
| **Screen** | Agent Studio → Agents → `governance_reporter` |
| **Do** | Paste **the same prompt as step 1**, send |
| **Shows** | Governance gaps closed. What remains is data the warehouse does not hold |
| **Capture** | The data-gaps section — side by side with step 1 if the format allows |

**Paste:**

> Audit the BCBS 239 governance framework. Scope catalog searches to
> `alation://data/2`. Separate governance gaps from data gaps.


**Callout:** *"What's left isn't a governance gap. It's three things engineering
has to build."*
