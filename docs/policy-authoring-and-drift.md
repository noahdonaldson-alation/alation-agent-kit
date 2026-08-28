# Authoring policies from a document, and detecting when they need to change

Two capabilities that did not exist before, both answering questions the gap
analysis does not.

## The three questions, kept distinct

| Question | Answered by | Target |
|---|---|---|
| What does this regulation require of our data? | `bcbs239_cde_dq_interpreter` | the regulation |
| Does the catalog hold the **data** it needs? | `bcbs239_pde_mapper` | tables and columns |
| Does our **governance framework** cover what the document says? | `policy_author` + `policy assess` | policies and standards |

Conflating the second and third is easy and costly. The mapper reported 11/11
mapped after the SQL pack — the *data* is there. That says nothing about whether
a policy exists obliging anyone to keep it that way.

## `policy author` — regulation → policy spec

```
./run.sh policy author --register docs/runs/v0.6.0/run01.json \
    -o policies/bcbs239.generated.json
```

Input is the validated requirements register. Output is a policy spec that
validates against `schemas/policy_spec.schema.json` — the same schema the
hand-authored `policies/bcbs239.json` satisfies, so `policy apply` cannot tell
them apart structurally.

**Why this matters more than it looks.** Hand-authoring `bcbs239.json` cost a
day: four policies, four standards, twenty attestation fields, every citation
checked. That cost repeats per regulation, and it is exactly the cost that has to
disappear for solution #7 to be cheaper than solution #1. This is the engine
piece, not the content piece.

### Division of labour

Per the project convention *agent for judgement that varies, code for actions
that must be exact*:

- **Agent** writes policy titles, obligations, HTML descriptions with quotations,
  standard purposes and scopes, and the attestation fields.
- **Code** (`authoring.py`) computes `standard_attachment` — a pure function of
  each CDE's `driven_by` principles — audits every citation, and stamps
  provenance. The prompt explicitly forbids emitting `standard_attachment`,
  because asking a model for a derivable value invites a contradiction between
  the value and its inputs.

### The audit, and why it has two modes

`authoring.audit()` runs ten checks a JSON Schema cannot express. The
provenance ones — every paragraph number and every quotation must trace to the
register — are **on for agent-authored specs, off for hand-authored ones**.

That distinction was earned. Run strictly against the reviewed
`policies/bcbs239.json`, the check produces **nine false failures**: it cites
¶32, ¶34, ¶35, ¶47 and quotes ¶36(d), none of which reached the register, because
a human wrote it with the actual PDF open. The agent can only see the register,
so for the agent those same citations would be unverifiable and most likely
invented. Same check, opposite meaning, depending on what the author could see.
A check that cries wolf on known-good input is one people learn to ignore.

What the checks catch, verified against a deliberately bad spec — all ten fire:
duplicate refs, paragraphs absent from the register, principles above 11,
descriptions with no quotation, fabricated quotations, `from_policy` pointing at
nothing, text fields carrying `allowed_values`, model-emitted
`standard_attachment`, uncovered principles, and **pickers with no failing
option** ("Yes / Excellent / Great" is not a control).

### The review gate

Generated specs carry `generated: {..., "reviewed": false}`. **`policy apply`
refuses them** until a human sets `reviewed: true`. The kit never sets that flag.

This is the one agent in the pipeline whose output is written into a bank's
governance framework rather than reported to a person. Hand-authored specs have
no `generated` block and are unaffected — `policies/bcbs239.json` deploys exactly
as before.

## `policy assess` — is our governance current?

```
./run.sh policy assess --prefix "BCBS239 - "
./run.sh policy assess --prefix "BCBS239 - " --against policies/bcbs239.json
```

Reads only. Per policy, four states:

- **present** — in the spec and in the instance.
- **missing** — the spec requires it, the instance lacks it. Needs creating.
- **untracked** — in the instance but not recorded by this kit, so `destroy`
  will leave it behind.
- **orphaned** — namespaced like ours, in the instance, absent from the spec.
  The spec shrank, or the document changed. *Only reported when `--prefix` is
  given; without a namespace every unrelated policy in a customer's catalog
  would look orphaned.*

With a register it also reports **uncovered principles**: principles that drive
CDEs but have no policy at all.

**It already found something.** The register cites principles 2, 3, 4, 5, 6, 7
and 8. The hand-authored spec covers 2–5. So principles **6, 7 and 8 drive
critical data elements with no policy behind them** — uncovered regulatory
surface that has been sitting in the repo unnoticed. That is also the first real
test of the authoring agent: a correct run should produce ~7 policies, not the 4
I wrote. If it produces exactly my 4, suspect it is pattern-matching a familiar
answer rather than reading the register.

### `--against`: has the document changed what we need?

This is the piece that makes the unstructured story land. Re-author a spec from
the current document, diff it against the spec you deployed from, and the delta
*is* the answer:

- `+ NEW POLICY NEEDED` — the document now implies an obligation with no policy.
- `- NO LONGER IMPLIED` — a policy the current document does not support.
- `~ CHANGED` — same policy, changed citations or wording.
- `~ STANDARD … attestation fields changed` — field-level, because a document
  amendment usually lands in what a steward must attest, not in the policy title.

Matching is by `ref` with a title fallback, and renames are reported as renames
rather than as an add plus a remove, which would overstate churn.

## Status

| Piece | State |
|---|---|
| `schemas/policy_spec.schema.json` | Validates the reviewed hand-authored spec with 0 errors |
| `authoring.py` audit / derive / gate | Unit-tested offline; all ten checks fire |
| `policy assess` (instance + register) | Unit-tested against a fake instance |
| `diff_specs` | Unit-tested including the no-change case |
| `prompts/policy_author.md` v0.1.0 | **Never run against a live instance** |
| `agents/policy_author.json` | Not yet deployed |

The prompt is the untested part, and it is regulation-agnostic on purpose —
nothing in it mentions BCBS 239. Whether the same prompt authors a usable spec
for a second regulation is unverified.

## Next

```
./run.sh deploy agents/policy_author.json --prompt policy_author --dry-run
./run.sh deploy agents/policy_author.json --prompt policy_author
./run.sh policy author
```

Then read `policies/bcbs239.generated.json` against the watch items in
`prompts/policy_author.meta.yaml`, and compare it with the hand-authored spec.
The comparison is unusually informative here: one artifact a human wrote
carefully, one a model wrote from the same source, same schema, same audit.
