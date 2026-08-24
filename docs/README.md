# docs/

Reviews and curated evidence for the prompts in this repo.

| Path | What it is |
|---|---|
| `bcbs239-interpretation-review.md` | Review of the `bcbs239_cde_dq_interpreter` output — citation verification, strengths, weaknesses, and the run-to-run drift finding that justifies the next prompt revision |
| `runs/` | Curated agent outputs kept as evidence. Named `YYYY-MM-DD-HHMM-<label>.md` |

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
