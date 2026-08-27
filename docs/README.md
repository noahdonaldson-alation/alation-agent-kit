# docs/

Reviews and curated evidence for the prompts in this repo.

| Path | What it is |
|---|---|
| **`prompt-iteration.md`** | **How prompt improvement is tracked** — the measure/change/re-measure loop, what to record, and the traps that produced wrong conclusions. Read this before revising any prompt. |
| **`bcbs239-gap-findings.md`** | **The first end-to-end pipeline result** — what the gap analysis found in a real warehouse, why it makes a better demo opening than a list of proposals, and a before/after showing output tracking catalogue maturity |
| `bcbs239-interpretation-review.md` | Review of the `bcbs239_cde_dq_interpreter` output — citation verification, strengths, weaknesses, and the run-to-run drift findings that drove each prompt revision |
| `runs/<prompt-version>/` | Curated agent outputs kept as evidence, **one directory per prompt version** |

## Runs are grouped by prompt version

```
runs/v0.1.0/   the original prompt — 33% stability, 8 runs
runs/v0.2.0/   required categories added — 77%, 9 runs
runs/v0.3.0/   criticality procedure — drift eliminated, 10 runs
runs/v0.4.0/   reconcilability added to the promotion test
```

The version comes from the `changelog` in the prompt's `.meta.yaml`. Grouping
this way is what makes the comparison meaningful — you measure a version against
a version, never a mixed pile:

```bash
python3 scripts/compare_runs.py docs/runs/v0.3.0/*.md      # one version
python3 scripts/compare_runs.py docs/runs/v0.2.0/*.md      # compare to another
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

Cross-cutting planning documents that span both this kit and the masterclass
engine live outside this repo, in the workspace `docs/` folder — they aren't
specific to the agent kit and would be a confusing home here.
