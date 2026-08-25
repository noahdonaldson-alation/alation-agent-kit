# How prompt improvement is tracked

A method for changing a prompt and knowing whether it got better. Written from
the BCBS 239 interpreter, but nothing here is specific to it.

The problem it solves: **model output is non-deterministic, so a single run
cannot tell you whether a weakness is in the prompt or is sampling noise.** Read
one output and you will "fix" things that were never broken and miss things that
fail half the time.

---

## The loop

```
1. Run the prompt N times, capture every output to a file
2. Measure. Record the numbers.
3. Write down the failures the numbers show — not the ones you feel
4. Write down what you predict a fix will do, BEFORE changing anything
5. Change the prompt, bump the version, record the hypothesis in the changelog
6. Re-run N times into a new version directory
7. Compare at matched N. Did the prediction hold?
```

Steps 4 and 7 are what make this different from tinkering. A prediction you
wrote down can be wrong, and finding out it was wrong is the point.

## Mechanics

```bash
# 1. Capture N runs of the current prompt version
mkdir -p docs/runs/v0.3.0
for i in $(seq -w 1 10); do
  f=docs/runs/v0.3.0/run$i.md
  [ -s "$f" ] && continue
  ./run.sh run <agent> --input-file <input> -o "$f" || echo "FAILED: run$i"
done

# 2. Measure
python3 scripts/compare_runs.py docs/runs/v0.3.0/*.md

# 3. Compare against the previous version
python3 scripts/compare_runs.py docs/runs/v0.2.0/*.md
```

The `[ -s "$f" ] && continue` guard means you can re-run the block to fill gaps
from failed runs without regenerating what you already have.

**One directory per prompt version**, named for the version in the prompt's
`.meta.yaml` changelog. Never mix versions in one measurement.

**Runs live in `docs/runs/`, not `artifacts/`.** `artifacts/` is gitignored
scratch; a run that a review cites is evidence and belongs in version control.

## What to record in the prompt's `.meta.yaml`

Each changelog entry carries the reasoning, so six months later the question
"why is this prompt shaped like this?" has an answer:

```yaml
  - version: 0.3.0
    date: 2026-08-24
    note: >
      v0.2.0 lifted stability 33% -> 77% but criticality ratings still drifted
      between identical runs (risk classification 2 in 3 of 9 runs).
      Change: replace the descriptive rubric with a decision PROCEDURE.
      Hypothesis: drift came from describing levels without saying how to choose
      between them, so each run re-derived the boundary.
      RESULT (10 runs): confirmed. Drift eliminated; crit3 exactly 4 every run.
      If ratings had still moved, the next step was to drop the 1-3 scale and
      ask only "load-bearing: yes/no".
```

Note the shape: **what the last version left broken → what changed → what was
predicted → what happened → what the fallback would have been.** The fallback
matters: it stops you from flailing when a fix fails.

## Don't read the headline number alone

Stability — the fraction of concepts appearing in *every* run — is one number and
it hides a lot. Read these separately:

| Metric | Why |
|---|---|
| **Required coverage** | Are the things you mandated present in *every* run? This is usually what you actually care about. |
| **Discretionary churn** | Variation in things the prompt says are optional is not a defect. Don't fix it. |
| **Rating / classification stability** | Is the same item labelled the same way each run? |
| **Section presence** | Is a mandated section ever silently dropped? |
| **Count adherence** | If you asked for 10–12 items, do you get 10–12? |

v0.3.0 is the case in point: its headline stability *fell* versus v0.2.0, while
it actually eliminated criticality drift entirely and hit the target count in
every single run. Judged on one number it looked like a regression.

---

## Traps we actually hit

Every one of these produced a wrong conclusion before being caught.

**0. The headline stability number can rank a worse prompt higher.** Stability is
`stable ÷ total concepts`, so a prompt that proposes *more discretionary variety*
scores *lower* even with every mandated element rock solid. At matched n=9,
v0.2.0 scores 77% and v0.4.0 only 71% — yet v0.2.0 has drifting ratings and
v0.4.0 has none. **Read required coverage first.** `compare_runs.py` now prints
it above the stability line for exactly this reason; `--required` sets the list.

**1. N changes the number.** Stability is "present in every run", so more runs
mechanically lowers it. 10 runs will score below 8 runs of identical quality.
**Always compare equal N**, scoring a subset of the larger set if needed.

**2. Naming variance masquerades as concept variance.** Runs called the same
element "MTM Value" and "Mark-to-Market Value". Counted as two concepts, that
invented instability. The comparator buckets by keyword and prints anything
unmatched as `OTHER:` so naming drift stays visible instead of silently
inflating the denominator.

**3. Increased precision looks like instability.** Later runs split "Exposure
Amount" into gross and net — a genuine improvement — and the tool read one
bucket holding two differently-rated elements as a rating that drifts. The
comparator now separates *several elements within one run* from *one concept
rated differently between runs*.

**3b. Bucketing errors are the most persistent failure here — they misled us
three separate times.** The worst was a required concept appearing to be missing
from a run: it was present as "GL / System-of-Record Reference Key", which the
*lineage* bucket had claimed because it also matched "system-of-record". The
comparator had even flagged that bucket as holding two elements in one run, and
that signal was dismissed as benign. It now says `CHECK: may be mis-bucketed`
instead. **Before believing any "missing from N runs" result, open the run and
look at the element names.** Two mitigations help: unmatched names print as
`OTHER:` rather than vanishing, and the most specific buckets are tested first.

**4. A tool that silently drops input will flatter a bad prompt.** Two runs wrote
criticality as `**3**` (bold), failed a bare-digit regex, parsed as zero items,
and were dropped without a word — the run reported "Comparing 7 runs" when nine
existed. Unparseable files are now reported loudly. **If a measurement improves,
check the measuring device before believing it.**

**5. Contaminated captures.** A streaming bug duplicated answers, so item counts
doubled and looked like wild prompt drift. The comparator now detects duplicated
and input-echoing output, deduplicates, and flags the file as unreliable.

**6. Transient failures leave silent gaps.** A read timeout mid-batch just meant
one fewer file, quietly. `run` now retries (3 attempts, backoff), and the capture
loop reports failures by name.

**7. Bundling changes costs attribution.** v0.2.0 changed four things at once and
stability went 33% → 77%. We cannot say which change did how much. That was an
acceptable trade — all four were separately justified and speed mattered — but it
is a real cost. Change one thing when you want to *learn*, several when you want
to *ship*.

---

## Worked example: this prompt

All figures below are measured with the *current* comparator. Earlier numbers
quoted during the work were distorted by bucketing bugs since fixed — which is
itself the point of trap 4.

| Version | N | Required coverage | Rating drift | crit3 / run | Stability |
|---|---|---|---|---|---|
| v0.1.0 | 8 | — (nothing mandated) | yes | 3–7 | 33% (7/21) |
| v0.2.0 | 9 | **10/10** | yes — exposure 2/3, risk class 2/3 | 5–6 | 77% (10/13) |
| v0.3.0 | 10 | **10/10** | **none** | **4, every run** | 67% (10/15) |
| v0.4.0 | 10 | **10/10** | **none** | **5, every run** | 71% (10/14) |

**v0.4.0 is the converged version**: every required concept present in every
run, each with one consistent and correct rating. Note it does *not* have the
highest stability — v0.2.0 does, at n=9, despite drifting ratings. See the
warning below.

What each change taught:

- **v0.2.0 — naming the required categories was the single highest-leverage
  change.** The set had been free-floating, so each run picked a different dozen
  from a larger pool. Mandating coverage of eight named categories moved
  stability more than everything else combined.
- **v0.3.0 — a rubric that describes levels is not a rubric.** Describing what 1,
  2 and 3 mean left the boundary to be re-derived each run. Replacing the
  description with a *procedure* — default to 2, promote only if you can complete
  this specific sentence — eliminated drift completely.
- **v0.3.0 also showed that precise instructions have precise side effects.** The
  promotion test said "cannot be **computed**", which literally demoted the
  reconciliation key, because you *can* compute an aggregate you cannot verify.
  v0.4.0 widened it to "computed **or reconciled**". Tighten a rule and check
  what falls outside it.
- **v0.4.0 confirmed all three of its predictions** and is where iteration
  stopped. Not because the numbers hit a target, but because every mandated
  element was present in every run with one correct rating — there was no
  measured failure left to fix. Further change should be driven by a new
  requirement, not by chasing the stability percentage.

## Rules of thumb

- **N ≥ 8.** Below that, one unlucky run swings the number.
- **Write the prediction down first.** Retrofitted explanations always fit.
- **Fix what the measurement shows**, not what reading one output suggests.
- **Leave discretionary variation alone.** If the prompt permits it, it isn't a defect.
- **Keep a fallback for each change.** If the fix fails, you should already know
  the next move rather than inventing one under pressure.
- **Suspect the tool when results move a lot**, in either direction.
