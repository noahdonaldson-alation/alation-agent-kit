# docs/

Reviews and curated evidence for the prompts in this repo.

### Method

| Path | What it is |
|---|---|
| **`prompt-iteration.md`** | **How prompt improvement is tracked** — the measure/change/re-measure loop, what to record, and the traps that produced wrong conclusions. Read this before revising any prompt. |
| `runs/<prompt-version>/` | Curated agent outputs kept as evidence, **one directory per prompt version** |

### Results — what the pipeline actually found

| Path | What it is |
|---|---|
| **`bcbs239-gap-findings.md`** | **The first end-to-end pipeline result** — what the gap analysis found in a real warehouse, why it makes a better demo opening than a list of proposals, and a before/after showing output tracking catalogue maturity |
| **`bcbs239-postsql-findings.md`** | The same analysis after the warehouse gained its missing dimensions: 1→11 mapped across 3 matched runs, 0 regressions. Also the two things not to oversell — confidence inflation, and only 48% agreement on *which* columns support each match |
| `bcbs239-interpretation-review.md` | Review of the `bcbs239_cde_dq_interpreter` output — citation verification, strengths, weaknesses, and the run-to-run drift findings that drove each prompt revision |

### Design and reference

| Path | What it is |
|---|---|
| **`policy-commands.md`** | **Every `policy` command and the exact API each one calls.** Start here for the provisioning half of the kit |
| `policy-authoring-and-drift.md` | How a policy spec gets generated from a register, the review gate, the two-mode citation audit, and the drift check that answers "do we need new policies?" |
| `pipeline-and-unstructured.md` | The three runtimes (kit+file, kit+unstructured, Agent Studio Flow), what changes when the unstructured feature lands, and the 56KB-register vs 10k-tool-result-cap constraint that shapes any Flow |
| `bcbs239-policy-design.md` | How BCBS 239 should exist as Alation **policies and CDE standards** — the grouping argument, the attestation fields each CDE must answer, and creation ordering. *Note: written when the plan was four policies; the register supports seven (principles 2–8)* |

## Runs are grouped by prompt version

```
runs/v0.1.0/   the original prompt — 33% stability, 8 runs
runs/v0.2.0/   required categories added — 77%, 9 runs
runs/v0.3.0/   criticality procedure — drift eliminated, 10 runs
runs/v0.4.0/   reconcilability added to the promotion test
runs/v0.5.0/   further coverage tightening
runs/v0.6.0/   converged: 100% required coverage, zero criticality drift,
               100% DQ citation coverage, 10 runs (JSON output)
```

`run01.json` from v0.6.0 is the register every downstream step uses — the mapper
and `policy_author` both take it as input, so it is effectively a fixture.

The version comes from the `changelog` in the prompt's `.meta.yaml`. Grouping
this way is what makes the comparison meaningful — you measure a version against
a version, never a mixed pile:

```bash
python3 scripts/compare_runs.py docs/runs/v0.3.0/*.md      # one version
python3 scripts/compare_runs.py docs/runs/v0.2.0/*.md      # compare to another
```

`compare_runs.py` reads the **interpreter's** markdown summary table. Mapper
output is JSON with a different shape, so it has its own comparer:

```bash
python3 scripts/compare_mappings.py artifacts/pde-mapping-postsql-*.json \
    --baseline artifacts/pde-mapping-v040.json
```

**Compare equal run counts.** Stability is the fraction of concepts appearing in
*every* run, so more runs mechanically lowers it — 10 runs will always score
below 8 runs of identical quality. When versions have different run counts,
score a subset of the larger one to match.

## Why this exists separately from `artifacts/`

`artifacts/` is gitignored: extracted source text and everyday run output are
regenerable and noisy, so they stay local. `docs/runs/` is tracked, and holds
only the outputs a review actually cites. The distinction is
**regenerable vs. evidentiary** — if a document makes a claim about model
behaviour, the run behind it belongs here so the claim can be checked later.

## Convention for reviews

A review should be able to answer, months later, "why did we change the prompt?"
So each one records:

- the **prompt sha and git sha** it reviewed (`./run.sh prompts` prints both)
- the **model** and instance
- what was **verified programmatically** versus judged by reading
- **run-to-run variance**, because a single run cannot distinguish a prompt
  weakness from sampling noise

Cross-cutting planning notes live outside this repo, in the workspace `docs/`
folder. Anything specific to a prompt or an agent in this kit belongs here.
