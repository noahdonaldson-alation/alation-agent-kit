# alation-agent-kit

Git-backed development and deployment kit for Alation Agent Studio. Prompts,
agents, and custom tools live as files in this repo; the CLI deploys them into an
Alation instance and runs them so you can iterate from your laptop.

First workload: interpreting **BCBS 239** and proposing the Alation governance
objects a bank should create to demonstrate compliance.

---

## Quick start

```bash
cp .env.example .env      # then fill in base URL + OAuth client
./run.sh whoami           # verifies auth, lists visible agents
./run.sh list agents

# Prepare the regulation text (one file per principle)
python scripts/extract_bcbs239.py --download

# Deploy the agent with the prompt rendered in
./run.sh deploy agents/bcbs239_interpreter.json --prompt bcbs239_principle_extract --dry-run
./run.sh deploy agents/bcbs239_interpreter.json --prompt bcbs239_principle_extract

# Run it against one principle
./run.sh run bcbs239_interpreter --input-file artifacts/bcbs239/principle_03.txt -o artifacts/p03.json
```

`run.sh` installs `uv` if missing (no admin rights, no Homebrew, no pre-existing
Python), creates `.venv`, and installs the package editable so edits under
`src/` take effect immediately. In PyCharm, point the interpreter at `.venv` and
set the run configuration to module `alation_agent_kit.cli`.

---

## Layout

```
prompts/          prompt bodies (.md) + sidecar metadata (.meta.yaml)
agents/           agent definitions in AgentExport shape
tools/            custom tool definitions (auth never committed)
workflows/        workflow `definition` blobs
schemas/          JSON Schema for agent output
scripts/          extract_bcbs239.py — PDF -> per-principle chunks
evals/            promptfoo config + golden cases
artifacts/        extracted text and generated output (gitignored by default)
src/              the CLI and API client
.lockfile.json    name -> UUID map. Commit this.
```

---

## Commands

| Command | What it does |
|---|---|
| `whoami` | Verify auth and token cache; list agent count |
| `list agents\|tools\|llms` | Inventory the instance |
| `export <name> [-o file]` | Pull an agent down, canonicalized for git |
| `deploy <file> [--prompt N] [--dry-run]` | Upsert an agent. `--dry-run` works offline |
| `run <name> [-m msg] [--input-file f] [-o out]` | Invoke and block for the result |
| `prompts` | List prompts with content hash and git SHA |

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

Also worth knowing: **no PDF ingestion exists.** No file upload, no RAG, no
knowledge base. That's why `scripts/extract_bcbs239.py` runs locally and the text
arrives as the agent's `message` parameter. Chunk by principle — the whole
document risks a `413 payload exceeds the model's context window`.

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

## Evals

```bash
npx promptfoo@latest eval -c evals/promptfooconfig.yaml --repeat 3
npx promptfoo@latest view
```

Two gates, one dataset. **Gate 1** runs the prompt against the raw model API —
fast and cheap. **Gate 2** (commented in the config) replays the same cases
against the deployed agent, because local testing has none of Studio's
scaffolding and a prompt can behave differently there.

Three structural assertions run on every case: output validates against
`schemas/policy_proposal.schema.json`; a supervisor-facing principle proposes no
Alation objects; and no `cde_overlay_standard` appears without the `policy` it
derives from (Alation requires exactly one source policy, and inherits its name).

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

- **CDE API status is unresolved.** Alation's public docs say CDE Manager
  standards and CDEs have no REST API, but the masterclass provisioning script
  successfully calls `/cde-service/integration/standard/` and `.../cde/` with a
  `CDEToken` header. Working code beats documentation; confirm on a live
  instance, because it decides whether `creation_mode: cde_service` is real.
- **`extract_text()` in `invoke.py` is best-effort.** The task-result shape isn't
  fully documented; tighten it once you've seen real responses.
- **`/call` is async** (returns `task_id`, then poll). promptfoo can't poll, so
  Gate 2 needs either `/stream` or a custom provider wrapping `run_agent`.
- Read `Alation/alation-plugins` (`cli/clients/config.py`, `workflow.py`) before
  extending the client — it covers more of the surface than this does.
