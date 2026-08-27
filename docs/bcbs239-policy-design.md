# BCBS 239 as Alation policies and CDE standards

Design note. The question: how should BCBS 239 exist as **policy** in Alation, so
that creating a CDE forces specific, auditable actions against it?

---

## The mechanism

```
Business Policy            the authority — what the regulation demands
   └─ Overlay Standard     derived requirements; requires EXACTLY ONE source
      │                    policy and INHERITS ITS NAME
      └─ attached to CDE   the CDE must answer the derived requirements
         └─ approval       Draft → In Review → Published, with rationale
```

Two consequences of the name inheritance:

1. **Policy naming is standard naming.** Name them for what they *demand*, not
   for a section number. "BCBS 239 §II" tells a steward nothing; "Risk Data
   Accuracy and Reconciliation" tells them what they must attest to.
2. **One policy per coherent set of demands.** A single "BCBS 239" policy means
   one giant standard asking every CDE every question — including irrelevant
   ones. A counterparty identifier does not need the same timeliness attestation
   as a position date.

## Recommendation: four policies in one group, not one and not eleven

**One policy** produces a standard that over-asks. **Eleven policies** (one per
principle) is too granular — the principles overlap heavily, and a steward would
face near-duplicate questions.

**Four**, grouped under a `BCBS 239` policy group so the umbrella still exists
for reporting:

| Policy / Standard name | Derived from | Demands, in one line |
|---|---|---|
| **Risk Data Architecture and Identification** | P2 ¶32–35 | Single identifiers, integrated taxonomy, one authoritative source |
| **Risk Data Accuracy and Reconciliation** | P3 ¶36–40 | Controls as robust as accounting; reconciled to source; accuracy measured |
| **Risk Data Completeness** | P4 ¶41–43 | All material exposures captured; completeness measured; gaps assessed |
| **Risk Data Timeliness** | P5 ¶44–47 | Produced within defined SLAs, including under stress |

P1 (Governance) is deliberately **not** a policy here — it is satisfied by
ownership and stewardship assignment on the CDE itself, plus the approval
workflow, rather than by an attestation field. P6–P11 are reporting-practice
matters our own register already classifies as out of scope.

Each CDE then attaches only the standards that apply to it. A counterparty
identifier attaches Architecture + Completeness; a position date attaches
Timeliness + Accuracy. **That selectivity is the point** — it is what makes the
attestations meaningful rather than boilerplate.

## The derived requirements: attestations, not restatements

A derived requirement in Alation is `{name, description, fields: [{name, type,
accepted_values}]}`. The mistake to avoid is restating the regulation in the
description and calling it done. The value is in **fields a steward has to fill
in per CDE**, each traceable to a paragraph.

Proposed fields, by standard:

### Risk Data Architecture and Identification (P2)

| Field | Type | Accepted values | Paragraph |
|---|---|---|---|
| Single authoritative source identified | picker | Yes / No / In progress | ¶36(d) |
| Authoritative source system | text | — | ¶36(d) |
| Uses enterprise-standard identifier | picker | Yes / Local identifier only / Not applicable | ¶33 |
| Taxonomy or code set governing values | text | — | ¶33 |

### Risk Data Accuracy and Reconciliation (P3)

| Field | Type | Accepted values | Paragraph |
|---|---|---|---|
| Reconciled to system of record | picker | Yes — automated / Yes — manual / No | ¶36(c) |
| Reconciliation frequency | picker | Intraday / Daily / Monthly / None | ¶36(c) |
| Accuracy monitoring in place | picker | Yes / No / Planned | ¶40 |
| Escalation path for poor quality | text | — | ¶40 |
| Manual or EUC intervention in the flow | picker | None / Documented / Undocumented | ¶36(b), ¶39 |

### Risk Data Completeness (P4)

| Field | Type | Accepted values | Paragraph |
|---|---|---|---|
| Completeness measured and monitored | picker | Yes / No / Planned | ¶43 |
| Known coverage exclusions | text | — | ¶43 |
| Materiality of exclusions assessed | picker | Yes / No / No exclusions | ¶43 |
| Covers off-balance-sheet exposures | picker | Yes / No / Not applicable | ¶41 |

### Risk Data Timeliness (P5)

| Field | Type | Accepted values | Paragraph |
|---|---|---|---|
| Availability SLA defined | picker | Yes / No | ¶44–45 |
| SLA target | text | — | ¶45 |
| Meets SLA under stress conditions | picker | Tested — passes / Tested — fails / Not tested | ¶46–47 |

**`Undocumented`, `No`, and `Not tested` are the useful answers.** A register
where every field reads "Yes" is either a mature bank or an unread form. The
demo value is in a CDE that shows *"Manual or EUC intervention: Undocumented"*
against ¶39 — that is a finding a supervisor would act on, surfaced by the
catalog rather than an audit.

## Where this fits the pipeline

The policy set is **regulation-specific and customer-independent** — the same
four policies apply to every bank. So it belongs with the register, as a
reviewed artifact in the solution package, not something re-derived per run.

```
step 2  interpret regulation ──→ requirements register        } ship in package,
        (existing)                + policy / standard set     } reviewed once
step 3  map to catalog       ──→ gap analysis                 } per customer
step 4  build                ──→ policies, standards, CDEs, monitors
```

**And by our own rule — ask the model for judgement, compute the rest — the
policy set should not be a new agent.** The judgement (four policies, these
attestation fields) is a one-time design decision, made once and reviewed by
someone who knows the regulation. Deriving it fresh on every run would
reintroduce exactly the drift we spent six prompt versions eliminating.

So: a hand-authored `policies/bcbs239.json`, versioned in the repo, consumed by
the build step.

### Standard attachment is derivable, not inferred

Which standards attach to a given CDE follows from the principles already
recorded in its `driven_by`:

| Principle cited | Standard attached |
|---|---|
| 2 | Risk Data Architecture and Identification |
| 3 | Risk Data Accuracy and Reconciliation |
| 4 | Risk Data Completeness |
| 5 | Risk Data Timeliness |
| 6–11 | none — reporting practice, out of scope |

That is a lookup, so **neither agent needs to know that policies exist.** The
interpreter interprets the regulation; the mapper searches the catalog; the build
step joins `driven_by` to this table. Keeping policy awareness out of the prompts
means a change to the policy design does not require re-running or re-validating
either agent.

## Deployment sequence

**Authored once, shipped in the package** — these are regulation-specific and
identical for every bank:

1. Policy and standard set (`policies/bcbs239.json`), hand-authored, reviewed by
   someone who knows the regulation
2. The requirements register, produced by the interpreter and reviewed once

**Per customer:**

| # | Step | Touches Alation? | Notes |
|---|---|---|---|
| 0 | Prerequisites | — | Data source crawled **with columns and descriptions**; unstructured collection configured if using that path |
| 1 | Ingest the PDF into an unstructured collection | read/write | Optional. Demo theatre — Alation doing the extraction *is* the story. Feature-flagged; needs an FDE |
| 2 | Create policy group, policies, overlay standards | **writes** | Can run here or later; must precede CDE creation. Early is better for narrative |
| 3 | Run `bcbs239_cde_dq_interpreter` | no | Or use the packaged register. Running live is good theatre; the packaged one is the reviewed truth |
| 4 | Run `bcbs239_pde_mapper` | reads only | Gap analysis against the real catalog |
| 5 | **Human review** | — | **The gate.** Confirm the `partial` matches, triage the `not_found` ones |
| 6 | Build: CDEs with standards attached, risk levels, DQ monitors | **writes** | Attachment derived per the table above |
| 7 | Approval workflow | writes | Draft → In Review → Published |

Two ordering constraints are real; everything else is preference:

- **A policy must exist before its overlay standard**, because the standard
  inherits the policy's name.
- **Step 4 must precede step 6**, because a monitor needs a confirmed physical
  element and a CDE needs something to point at.

Step 5 is where the human belongs — it is the last point before anything is
created, and Alation flows cannot pause for approval, so it is a manual boundary
by necessity as well as by design.

## Creation order, which is not negotiable

```
1. Policy group           "BCBS 239"
2. Business policies      4x, into that group
3. Overlay standards      4x, each from exactly one policy, inheriting its name
4. CDEs                   with the applicable standards attached
5. Risk assessment        level + rationale per CDE
6. DQ monitors            against confirmed physical elements
7. Approval               Draft → In Review → Published
```

Steps 2 and 3 cannot be reordered — the standard has no name until the policy
exists. Step 6 depends on step 3 of the pipeline having found real columns.

## Two things to verify before building

**1. Can overlay standards be created via API at all?** The Policy API
(`/integration/v2/business_policies/`) is documented and unambiguous. CDE
Manager standards are the question: Alation's product docs say there is no REST
API, while `/cde-service/integration/standard/` **is** documented on
developer.alation.com with the `CDEToken` header, and takes exactly the
`{name, purpose, scope, derived_requirements}` shape this design needs. Confirm
on the instance before committing to an automated build; if it is UI-only, the
policy and standard set becomes a documented prerequisite rather than part of
the deploy.

**2. Do derived-requirement field types support what is proposed above?**
`picker` with `accepted_values` and free `text` are the two used here. Confirm
the type names and whether a picker can be made mandatory — an optional
attestation field is a suggestion, not a control.

## Why this is worth doing

Without policies, a CDE register is a list of important columns. With them,
every CDE carries **a specific set of questions it must answer, each traceable
to a paragraph of the regulation** — and the unanswered ones are visible.

That is the difference between "we catalogued our critical data" and "we can
show a supervisor which critical data elements do not yet have a reconciliation
control, and who owns fixing it."
