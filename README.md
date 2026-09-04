# alation-agent-kit

Git-backed development and deployment kit for Alation Agent Studio. Prompts,
agents, and custom tools live as files in this repo; the CLI deploys them into an
Alation instance and runs them so you can iterate from your laptop.

First workload: **BCBS 239** — reading the regulation and building the Alation
governance objects a bank needs to evidence compliance, from a numbered paragraph
down to a column in a warehouse.

> **Running the demo?** Read [docs/demo-script.md](docs/demo-script.md). It has
> the prerequisites, the scenes, and three things that will bite you if you
> discover them on the day.
>
> **Want the summary for a leader?** [docs/executive-summary.md](docs/executive-summary.md)
> — what was built, how reusable it is, and what was deliberately skipped.
>
> **New to the kit?** [GETTING-STARTED.md](GETTING-STARTED.md) is the
> step-by-step: prerequisites, the iteration loop, adding an agent, PyCharm
> setup, troubleshooting. This README covers the *why* — the API hazards the code
> works around and the decisions behind them.

---

## What runs where

**The demo path is entirely in the Alation UI.** Four agents, in sequence:

| Agent | Does |
|---|---|
| `bcbs239_obligation_interpreter` | regulation text → obligations, one per principle |
| `policy_creator` | obligations → business policies, with a human approving |
| `cde_creator` | published standards → critical data elements + their columns |
| `governance_reporter` | audits the whole chain, read-only, before and after |

Between the second and third, **CDM's own AI derives the overlay standards** from
the policy prose. We do not author those.

**The kit is the setup half** — deploying prompts, agents and tools, provisioning
and repairing objects, and measuring prompt quality across runs. That split is
deliberate: setup may be scripted, the end-to-end experience must be in the UI.

---

## Quick start

```bash
cp .env.example .env      # then fill in base URL + OAuth client
./run.sh whoami           # verifies auth across all three surfaces
./run.sh preflight        # asserts the prerequisites, read-only

# Prepare the regulation text: per-principle files + bank_principles.txt
.venv/bin/python scripts/extract_bcbs239.py --download

# Deploy the tools, then the agents that use them
./run.sh tool deploy tools/create_blank_policy.json      # ... and the rest
./run.sh deploy agents/policy_creator.json --prompt policy_creator

# Iterate on a prompt: edit the .md, redeploy, run again
./run.sh deploy agents/cde_creator.json --prompt cde_creator --dry-run
./run.sh deploy agents/cde_creator.json --prompt cde_creator
```

The prompt `.md` file is the source of truth; `deploy` pushes it into the agent.
Never edit the `prompt` field in an agent JSON by hand.

`run.sh` installs `uv` if missing (no admin rights, no Homebrew, no pre-existing
Python), creates `.venv`, and installs the package editable so edits under
`src/` take effect immediately. In PyCharm, point the interpreter at `.venv` and
set the run configuration to module `alation_agent_kit.cli`.

---

## Layout

```
prompts/          prompt bodies (.md) + sidecar metadata (.meta.yaml)
agents/           agent definitions in AgentExport shape
policies/         policy specs: bcbs239.json (hand-authored),
                  bcbs239.generated.json (agent-authored, needs review)
schemas/          JSON Schemas for each agent contract + the policy spec
scripts/          extract_bcbs239.py   PDF -> per-principle chunks
                  compare_runs.py      interpreter stability across runs
                  compare_mappings.py  mapper runs vs a baseline
                  validate_output.py   schema + structural checks (auto-detects contract)
                  normalize_mapping.py recompute derivable fields in a mapping
                  inspect_stream.py    report a raw SSE stream's event schema
                  repair_encoding.py   retired: fixes pre-UTF-8-fix mojibake
                  render_report.py     ORPHAN, unfinished — see ../INVENTORY.md
sql/              the prompt that generated the warehouse dimension pack
docs/             prompt-iteration method, reviews, and runs/ evidence
artifacts/        extracted text and everyday output (gitignored)
src/              the CLI and API client
.lockfile.json    name -> UUID map. Commit this.
```

`tools/` holds the custom Agent Studio HTTP tools — the agents on the demo path
are built from these plus a handful of Alation's own base tools. Each file
carries a `$comment` block explaining why it exists and what is known to fail;
read those before changing one. `tools/README.md` covers the conventions.

`agentkit tool show <name>` inspects an instance's tools, including base tools,
and dumps the real input schema — the only reliable statement of what a tool can
do. Use it before writing a custom tool: Alation ships more than you expect, and
a custom tool whose name collides with a base tool will aim a write at the
built-in.

---

## Commands

**Auth and environment**

| Command | What it does |
|---|---|
| `whoami` | Probe all three auth surfaces: Agent Studio, catalog, CDE service |
| `refresh-token <username>` | Mint a legacy refresh token; returns it **and** your numeric user id |
| `userid <email>` | Look up a numeric Alation user id (for `ALATION_USER_ID`) |
| `preflight [--skip-unstructured] [--probe-cde-create]` | Assert prerequisites. Read-only, except `--probe-cde-create` which creates and deletes a throwaway standard |

**Agents, prompts, tools**

| Command | What it does |
|---|---|
| `list agents\|tools\|llms [--raw]` | Inventory the instance. Tools are listed at **all four visibility labels** — the API defaults to hiding `advanced` and `alation_internal` |
| `export <name> [-o file]` | Pull an agent down, canonicalized for git |
| `deploy <file> [--prompt N] [--dry-run]` | Upsert an agent. `--dry-run` works offline |
| `run <name> [-m msg] [--input-file f] [-o out]` | Invoke and block for the result |
| `tool show <name>` | Dump a tool's real `input_parameter_schema` — the only reliable statement of what it can do |
| `tool deploy <file.json> [--dry-run]` | Upsert a custom tool. `${VAR}` placeholders are filled from `.env`, so no secret is committed |
| `prompts` | List prompts with content hash and git SHA |

**Pipeline and policy** — full detail in `docs/policy-commands.md`

| Command | What it does |
|---|---|
| `pipeline [--source file\|unstructured] [--stop-after interpret]` | regulation → register → gap analysis, with a provenance manifest |
| `policy plan\|apply\|verify\|publish\|destroy` | Provision, check and tear down policies + overlay standards |
| `policy author\|review\|assess` | Generate a spec from a register, review and approve it, check for drift |
| `policy standards` | Dump existing overlay standards verbatim (authoritative field shapes) |
| `policy rename --id N --from-source-policy` | Republish a standard under the right name. A published standard cannot be edited, so this creates a new version, carries its requirements forward untouched, and publishes it |
| `policy relink --id N --source-policy P` | Re-point a standard at a live policy. **Changes the label, not the derivation** — the requirements still came from the previous policy's prose. For repairing a dev instance, never for manufacturing traceability |
| `cde plan\|apply\|map\|score\|destroy` | Provision CDEs from a register. Superseded on the demo path by `cde_creator`; kept for setup and reset |

---

## Six things about this API that will bite you

These are the reasons the code looks the way it does. All verified against the
Alation AI API OpenAPI spec (`/ai/api/v1`) and the Agent Studio docs.

**1. Minting a token invalidates the previous one.** Straight from the docs:
*"Generating a new Access Token automatically invalidates the previous token."*
One live token per OAuth client. So: **use a client dedicated to you**, and note
that `auth.py` caches the token to `~/.alation/agent-kit-tokens.json` (mode 0600)
and reuses it until five minutes before expiry. Without that cache, every CLI
invocation would kill your last one — and your open browser session.

**2. `import` is create-only.** `POST /config/agent/import` has no `id` field,
returns a new agent, and regenerates UUIDs. Re-importing **clones**. So
`deploy` does `list → match by name → PATCH`, and only imports when the agent
genuinely doesn't exist yet.

**3. Agents PATCH, tools PUT.** Agent update is a partial PATCH; tool update is
a full-replace PUT. Inconsistent, and an easy way to silently wipe tool fields.

**4. Custom agents have no human-readable key.** They're addressable only by
server-generated UUID; the name-addressable route accepts only an enum of ~28
built-ins. Names aren't enforced unique either. Hence `.lockfile.json`, and
hence `resolve_agent_id` raising on duplicate names instead of guessing.

**5. The server rewrites your schema.** Alation injects `x-tool-bindings` and
`x-original-agent-input` into `input_json_schema`, and a binding with
`source: "user"` auto-adds that parameter. **What you PUT is not what you GET.**
`store.canonicalize_agent` strips those annotations so re-exporting doesn't
produce a phantom diff on every deploy.

**6. `tools` and `parameter_bindings` are positionally matched** and must be the
same length. Sorting them independently silently rewires an agent's bindings —
so the canonicalizer reorders them **as pairs**, and flags a length mismatch
rather than guessing.

Also worth knowing about document input: **there is no file upload and no RAG**,
but PDF *content* is reachable — via **Unstructured Data Collections** plus the
`get_asset_content` tool (PDF lands in S3/SharePoint/Confluence → unstructured
OCF connector → collection → agent reads processed markdown). That path is
feature-flagged and needs an FDE to enable, and it re-fetches on every call with
no cache, costing 30–60s per PDF through Textract.

So `scripts/extract_bcbs239.py` extracts locally and the text arrives as the
agent's `message` parameter: fast, free, and deterministic for the iteration
loop. Unstructured Collections are the right choice for a delivered demo, where
Alation doing the extraction *is* the story. Details in `../docs/agent-kit-viability.md`.

---

## How prompts work here

Prompt bodies are plain Markdown, never embedded in YAML. A YAML block scalar is
indentation-scoped, so one structural edit re-indents the entire body and you
lose word-level diffs and GitHub suggested-edits. Metadata goes in a sidecar
`.meta.yaml`.

**The prompt body is a system prompt and contains no template variables.**
Runtime input (the principle text) arrives as the user message, locally and in
Studio alike, so the prompt deployed to Alation is byte-identical to the one
tested locally. Agent Studio has no templating of its own — an unrendered
`{{ var }}` would reach the model as literal text. `deploy` warns if any survive.

Deploy-time variables, if you ever need them, are declared under
`deploy_variables` in the meta file and rendered with `StrictUndefined`, so a
typo fails loudly rather than shipping an empty string.

---

## Measuring prompt changes

**Read [`docs/prompt-iteration.md`](docs/prompt-iteration.md) before revising a
prompt.** Model output is non-deterministic, so a single run cannot distinguish a
prompt weakness from sampling noise — you need a batch, a baseline, and a
prediction written down before you change anything.

```bash
mkdir -p docs/runs/v0.3.0
for i in $(seq -w 1 10); do
  f=docs/runs/v0.3.0/run$i.md
  [ -s "$f" ] && continue
  ./run.sh run <agent> --input-file <input> -o "$f" || echo "FAILED: run$i"
done
python3 scripts/compare_runs.py docs/runs/v0.3.0/*.md
```

`compare_runs.py` groups the items an output proposes into concepts and reports
which appear in *every* run. It also detects duplicated or input-echoing captures
and refuses to hide files it can't parse — both of which previously produced
wrong conclusions.

This approach took the BCBS 239 interpreter from 33% to 77% stability and
eliminated criticality-rating drift entirely. The version history, with what each
change taught, is in `docs/prompt-iteration.md`.

`scripts/inspect_stream.py` is the companion tool for when a *capture* misbehaves
rather than a prompt: point it at a `--raw` stream dump and it reports the event
schema.

**Gate on aggregate pass rate, never exact output match.** Model output is
non-deterministic even at temperature 0 — inference kernels aren't
batch-invariant, so other tenants' load changes your numerics. What *is*
deterministic is the rendered prompt, so that's what's worth snapshotting.

---

## Iteration cost

Metering is 0.25 ACU per metered action, and only Alation base tools meter —
custom HTTP/SMTP tools are exempt, and agent runs don't consume quota directly.
The BCBS 239 agent calls no catalog tools, so iterating on it is effectively
free. Budget ~0.5–0.75 ACU per message once agents start hitting catalog or SQL
tools. `GET /ai/api/v1/usage/aggregated_metrics` tracks it.

Errors the client recognizes: **402** quota exceeded, **409** chat busy,
**413** context window exceeded.

---

## BCBS 239 notes

Source: https://www.bis.org/publ/bcbs239.pdf — 28 pages, January 2013, never
amended. 14 principles in four sections. **Principles 1–11 address banks; 12–14
address supervisors**, so the agent proposes nothing for 12–14.

Cite by **paragraph number, not page** — paragraphs are stable across reprints.

Honest scope, which is what keeps this credible with a risk audience: of the 11
bank-facing principles Alation materially implements about **4** (P1 Governance,
P2 Data architecture, P3 Accuracy & Integrity, P4 Completeness), *evidences*
**3** (P5 Timeliness, P6 Adaptability, P7 Report accuracy), and **cannot
satisfy 4** (P8–P11, which concern report content, clarity, cadence and
distribution). The output schema encodes this as `catalog_addressability` plus a
required `unaddressed_by_catalog` list.

Useful positioning: the BCBS newsletter of 6 January 2026 names **data lineage**
as the capability banks find hardest, and the ECB's *Guide on effective RDARR*
(May 2024) makes these expectations enforceable in the EU.

---

## Open items

- **`policy_author` is unstable at N=1.** Two identical runs produced 7 and 6
  policies. A runtime coverage contract (derived from the register) now states the
  required principles explicitly, but that fix is unproven. Run it twice before
  showing it.
- **Three policies failed to create** in the first full run of the generated
  spec. Root cause was ours — the bulk-job status vocabulary was invented — and
  is fixed, but one job also hit a genuine Alation-side traceback. Not re-verified.
- **Two policy specs have colliding refs.** `bcbs239.json` and
  `bcbs239.generated.json` share four refs with different titles, which makes
  `apply` skip creating the newer object. Pick one as authoritative.
- **Unstructured document ingestion is prerequisite-blocked**, not code-blocked.
  `Get Asset Content` is visible on the instance; the feature flag and a
  collection are what's missing. See `docs/pipeline-and-unstructured.md`.
- Read `Alation/alation-plugins` (`cli/clients/config.py`, `workflow.py`) before
  extending the client — it covers more of the surface than this does.

**Resolved since first draft:** the CDE service is confirmed reachable and
documented (`CDEToken`, and the OAuth bearer works too, including for writes);
agent invocation uses `/chats/agent/{id}/stream` because the polling path 404s
once a task succeeds.
