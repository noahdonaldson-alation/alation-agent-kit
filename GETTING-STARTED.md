# Getting Started

A task-by-task walkthrough. The [README](README.md) explains *why* the code is
shaped the way it is; this file is *how to use it*.

> **Status honesty:** the kit is tested offline — it compiles, the CLI parses, the
> canonicalizer and extraction pipeline have passing checks. It has **not yet run
> against a live Alation instance.** Steps marked 🔵 are verified; steps marked
> ⚪ are expected-to-work and are where you'll find the first bugs. When something
> in a ⚪ step misbehaves, that's new information, not user error — the
> [Troubleshooting](#troubleshooting) table has the likely causes.

---

## The mental model

Three ideas. Everything else follows from them.

**1. The repo is the source of truth; Alation is a deployment target.**
Agent Studio has no version history, no drafts-vs-published beyond a single
flag, and no environments. Git is your version control. You edit files here and
push them up — never the reverse, except when deliberately capturing something
built in the UI.

**2. Prompts are system prompts and contain no variables.**
The thing the agent reasons about (a BCBS 239 principle) arrives at *runtime* as
the `message` input. That's why `prompts/*.md` has no `{{ placeholders }}`: the
prompt deployed to Alation is byte-identical to the one you test locally, so a
local pass actually means something. Agent Studio has no templating, so a
stray `{{ var }}` would reach the model as literal text — `deploy` warns if it
finds any.

**3. Deploy is an upsert, not an import.**
Alation's `import` endpoint only ever *creates* — re-importing clones your agent
rather than updating it. So `deploy` looks up the agent by name and PATCHes it.
This is why `.lockfile.json` exists and why you should commit it.

---

## Prerequisites

| What | Why | How |
|---|---|---|
| **An OAuth client, dedicated to you** | The only way to authenticate. **You cannot self-serve this** — a Server Admin creates it at `/admin/auth/` → OAuth Client Applications. | Ask, and ask for a **72-hour token duration** while you're at it. |
| An Alation instance you can write to | Deploy target. Agents land in `draft`. | Your dev/demo instance, not a customer's. |
| macOS/Linux terminal | `run.sh` handles Python. | Nothing to install first. |
| Node (optional) | Only for `promptfoo` evals. | `npx` fetches it on demand. |

**Ask for your own client, not a shared one.** Alation invalidates the previous
access token whenever a new one is issued, so two people on one client will
knock each other offline — and so will your own script versus your open browser
session. The kit caches tokens to `~/.alation/agent-kit-tokens.json` (mode 0600)
and reuses them until five minutes before expiry, which makes this a non-issue
*for you alone*.

---

## Step 1 — Configure and verify auth 🔵/⚪

```bash
cd ~/AIOSProject/alation-agent-kit
cp .env.example .env
$EDITOR .env          # ALATION_BASE_URL, ALATION_CLIENT_ID, ALATION_CLIENT_SECRET
./run.sh whoami
```

First run installs `uv` if missing (no admin rights, no Homebrew, no
pre-existing Python needed), creates `.venv`, and installs the package
editable — so edits under `src/` take effect with no reinstall.

Expected:

```
Instance: https://your-instance.alationcloud.com
Client ID: a1b2c3d4…
Token cache: /Users/you/.alation/agent-kit-tokens.json
Auth OK — 12 agent config(s) visible
```

`.env` is gitignored. Keep it that way — it holds a client secret.

## Step 2 — Look around ⚪

```bash
./run.sh list agents
./run.sh list tools
./run.sh list llms      # note an id here; you'll need one to create an agent
```

## Step 3 — Prepare the regulation text 🔵

```bash
.venv/bin/python scripts/extract_bcbs239.py --download
```

**Use the venv's interpreter, not bare `python`.** macOS ships no `python` on
PATH — only `python3` — and `pypdf` is installed in the venv, not globally. Any
of these work: `.venv/bin/python`, `./scripts/extract_bcbs239.py` (it has a
shebang and is executable), or `source .venv/bin/activate` first and then plain
`python`.

Downloads BCBS 239 from bis.org and splits it into 14 per-principle files plus
an index:

```
artifacts/bcbs239/principle_01.txt … principle_14.txt
artifacts/bcbs239/index.json
artifacts/bcbs239/full.txt
```

**Chunk by principle, always.** Agent Studio has no PDF ingestion — the text
arrives as the agent's `message` parameter — and the whole 28-page document
risks a `413 payload exceeds the model's context window`. One principle per run
also gives you 14 small reviewable outputs instead of one unreviewable blob.

Check the console output for any `<- EMPTY, check the parser` flags. The parser
matches line-leading paragraph numbers; if bis.org changes the PDF's text layer,
that's where it breaks.

## Step 4 — Deploy the agents ⚪

The agents already exist as files, so deploying is the normal path. Tools first,
because agents resolve their tools **by name** at deploy time and an unresolvable
tool aborts the deploy:

```bash
./run.sh tool deploy tools/create_blank_policy.json     # ... and the rest
./run.sh deploy agents/policy_creator.json --prompt policy_creator --dry-run
./run.sh deploy agents/policy_creator.json --prompt policy_creator
```

`--dry-run` works offline and shows exactly what would be sent.

**Never edit the `prompt` field in an agent JSON by hand.** The `.md` file is the
source of truth and `deploy` renders it in.

**Creating a brand-new agent?** Build it in the Agent Studio UI first —
hand-writing agent JSON is miserable, and export canonicalizes it on the way into
the repo:

```bash
./run.sh export <agent-name>          # -> agents/<agent-name>.json
```

Then cut the `prompt` value out and replace it with a placeholder note, so the
`.md` becomes the source of truth from that point on.

## Step 5 — Run it ⚪

Agents on the demo path are used **in the Alation UI** — that is the point, and
it is what the demo shows. The CLI runner is for prompt iteration, where you want
the same input every time and the output in a file:

```bash
./run.sh run bcbs239_obligation_interpreter \
  --input-file artifacts/bcbs239/bank_principles.txt \
  -o artifacts/obligations.json
```

Feed the interpreter the **combined** principles file rather than one principle
at a time — obligations are cross-cutting, so the model needs them in view
together.

Add `-v` to watch the stream. Invocation uses `/chats/agent/{id}/stream`, not the
polling path: `GET /task/{id}` 404s once a run succeeds, so a finished run looks
like a failed one.

## Step 6 — The daily loop 🔵

This is the part you'll actually spend time in.

```bash
$EDITOR prompts/cde_creator.md                            # 1. edit the prompt
./run.sh deploy agents/cde_creator.json \
  --prompt cde_creator                                    # 2. push it
#                                                           3. run it in the UI
git add -A && git commit -m "Nominate the gold column as control point"
```

Record what changed and why in the prompt's `.meta.yaml` changelog as you go —
those entries are the only record of *why* a prompt says what it says, and
several of them exist because a plausible-looking instruction failed in a way
that took a day to find.

`./run.sh prompts` shows each prompt's content hash and the git SHA of the last
commit touching it — so any output can be traced back to the exact prompt that
produced it.

**Iteration is nearly free here.** Metering is 0.25 ACU per metered action, but
only Alation *base* tools meter — custom tools are exempt and agent runs don't
consume quota directly. This agent calls no catalog tools. Budget
~0.5–0.75 ACU per message only once an agent starts hitting catalog or SQL tools.

## Step 7 — Evals, once the prompt stabilises ⚪

```bash
npx promptfoo@latest eval -c evals/promptfooconfig.yaml --repeat 3
npx promptfoo@latest view
```

Three structural assertions run on every case: the output validates against the
schema; a supervisor-facing principle (12–14) proposes zero Alation objects; and
no `cde_overlay_standard` appears without the `policy` it derives from — Alation
requires exactly one source policy and inherits its name.

**Gate on aggregate pass rate, never exact output match.** Model output is
non-deterministic even at temperature 0, because inference kernels aren't
batch-invariant and other tenants' load shifts the numerics. What *is*
deterministic is the rendered prompt — that's the thing worth snapshotting.

---

## How to add a new agent

**Don't hand-write `AgentExport` JSON.** Build it in the Agent Studio UI, then
capture it:

```bash
./run.sh list agents                    # find the name
./run.sh export my_new_agent            # -> agents/my_new_agent.json
```

The export is canonicalized on the way out: server-injected schema annotations
(`x-tool-bindings`, `x-original-agent-input`) are stripped, and `tools` are
reordered *together with* their positionally-matched `parameter_bindings`. That's
what stops every deploy from producing a phantom diff.

Then move the prompt into a file so it's reviewable:

1. Cut the `prompt` value out of the JSON into `prompts/my_new_agent.md`.
2. Replace the JSON value with a placeholder note.
3. Create `prompts/my_new_agent.meta.yaml` (copy the BCBS one; set
   `deploy_variables: {}`).
4. `./run.sh deploy agents/my_new_agent.json --prompt my_new_agent --dry-run`

**Auth is never exported**, by design — so exports are safe to commit, and after
importing to a *different* instance you must reattach auth configs. `import`
returns a `warnings` list telling you what needs manual attention.

---

## PyCharm setup

- **Interpreter:** Settings → Project → Python Interpreter → Add → Existing →
  `~/AIOSProject/alation-agent-kit/.venv/bin/python`
- **Sources root:** right-click `src/` → Mark Directory as → Sources Root, so
  imports resolve without the `PYTHONPATH` dance.
- **Run configuration:** Module name `alation_agent_kit.cli` (not script path),
  Parameters e.g. `run <agent-name> --input-file artifacts/bcbs239/bank_principles.txt`,
  Working directory the repo root.
- **`.env`:** PyCharm doesn't load it natively. Either install the EnvFile
  plugin, or just use `./run.sh`, which does load it.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ALATION_BASE_URL is not set` | No `.env` | `cp .env.example .env` and fill it in |
| `ALATION_CLIENT_ID and ALATION_CLIENT_SECRET are required` | No OAuth client | Server Admin must create one at `/admin/auth/` |
| `OAuth token request failed 401` | Wrong credentials, or the client was deleted | Verify with the admin. The client tries body-credentials then HTTP basic before giving up |
| Auth worked, then suddenly 401s | Someone else minted a token on the same client | Get your own client. The kit auto-retries once with a forced refresh |
| `402` | Tool-call quota exhausted on the instance | Check `GET /ai/api/v1/usage/aggregated_metrics`. Free-tier grants never reset |
| `409 Chat is busy` | Concurrent runs on one chat | Let it finish, or pass a fresh `chat_id` |
| `413` | Input exceeded the context window | Send one principle at a time, not `full.txt` |
| `N agents are named 'x'` | Duplicate names (Alation doesn't enforce uniqueness) | Rename/delete duplicates, or pin the UUID in `.lockfile.json` |
| `UndefinedError: 'x' is undefined` | Prompt has a `{{ var }}` not declared in `deploy_variables` | Either remove it (runtime inputs don't belong in the prompt) or declare it in the meta file |
| `! prompt still contains {{ }}` | Unrendered template syntax would ship to the model | Same as above — Studio has no templating |
| Deploy created a second agent instead of updating | Name mismatch between file and instance | Names must match exactly; check `./run.sh list agents` |
| Every deploy shows a diff on `input_json_schema` | Server-injected annotations | Re-`export` to canonicalize; if it persists, the annotation list in `store.py` needs extending |
| `run` prints raw JSON instead of text | `extract_text()` guessed wrong on the response shape | Expected — the task-result shape isn't documented. Paste the JSON and we'll tighten it |
| Principle file is empty | PDF text layer changed | Check `artifacts/bcbs239/full.txt`, then the regex in `split_by_paragraph_numbers` |

---

## Things that are known-unresolved

- **CDE API status.** Alation's product docs say CDE Manager standards and CDEs
  have no REST API, but `/cde-service/integration/` **is** documented on
  developer.alation.com, `CDEToken` header included — the product docs are
  stale. Confirm on a live instance before relying on it, since it decides
  whether creating CDEs and standards can be automated at all.
- **Gate 2 of the evals** needs `/stream` or a custom promptfoo provider, since
  `/call` is async and promptfoo can't poll.
- **`extract_text()`** is best-effort until we've seen real responses.
- **`Alation/alation-plugins`** covers more of this API surface than we do. Read
  `cli/clients/config.py` and `workflow.py` before extending the client.

---

## Command reference

| Command | Purpose |
|---|---|
| `./run.sh whoami` | Verify auth and token cache |
| `./run.sh list agents\|tools\|llms` | Inventory the instance |
| `./run.sh export <name> [-o file]` | Pull an agent down, canonicalized |
| `./run.sh deploy <file> [--prompt N] [--dry-run]` | Upsert an agent (`--dry-run` works offline) |
| `./run.sh run <name> [-m msg] [--input-file f] [--param k=v] [-o out] [-v]` | Invoke and block for the result |
| `./run.sh prompts` | List prompts with content hash and git SHA |
| `.venv/bin/python scripts/extract_bcbs239.py --download` | Fetch the PDF, chunk per principle, write `bank_principles.txt` |
| `.venv/bin/python scripts/extract_bcbs239.py --pdf artifacts/bcbs239.pdf` | Re-chunk an already-downloaded PDF |
