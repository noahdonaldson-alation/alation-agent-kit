# Custom tool definitions

Agent Studio custom tools, as files, for the same reason agents and prompts are
files: ids are per-instance, so the definition is the durable thing and the id is
not.

## Read this before adding anything here

**Nothing in Agent Studio creates a business policy, and nothing here ever
will.** Policies are created by the kit — `policies.py`, via `policy apply` —
and by nothing else. Agent Studio can *read* policies (`Find Business Policies`)
and *delete* them (`Delete Business Policies`), because those endpoints take
object bodies. `POST`/`PUT /integration/v1/business_policies/` take a bare
array, and an HTTP tool's body can only ever be the tool-call arguments object.
Four executions closed that search space; the verbatim errors are in
`docs/policy-commands.md`.

Standards are a separate question and the answer changed: **CDM generates the
overlay standard from the policy**, in the UI, using its own AI. So
`Create CDE Overlay Standard` below is not the intended creation path either —
it exists, it has never been successfully invoked, and its bearer-only auth is
unproven. Do not build on it without testing it first.

If a file appears in this directory that looks like it creates a policy, it is a
probe or a mistake. Probe definitions are deliberately not kept — a file named
`create_business_policy.json` sitting beside four live tools reads as a
capability we have.

## These are LIVE on finance-industry.mtse — do not delete

| Tool | `function_name` | `tool_type` | What depends on it |
|---|---|---|---|
| `Find Business Policies` | `find_business_policies` | `http` | The lifecycle Flow's read path. It is the only way an agent can resolve a policy title to its integer id — **and it is the safety guard on the delete tool below.** |
| `Create CDE Overlay Standard` | `create_cde_overlay_standard` | `http` | Standard creation from chat — the reason the setup half is not wholly terminal-bound. |
| `Fetch CDE Overlay Standards` | `fetch_cde_overlay_standards` | `http` | Reading published standards; the lifecycle Flow's coverage check. |
| `Delete Business Policies` | `delete_business_policies` | `http` | Teardown from chat. **`DELETE` is the only business-policy write that takes an object** (`{"ids": [...]}`, synchronous, 204), which is why this one is buildable and create is not. |

All four are **custom HTTP tools we built**, not Alation base tools. Confirmed
live 2026-08-28 by `./run.sh list tools`.

**`Delete Business Policies` has no namespace guard and cannot have one.** The
endpoint takes integer ids, so nothing in the tool config can enforce the
`BCBS239 - ` prefix. The guard lives in the agent prompt: resolve titles with
`Find Business Policies`, delete only ids whose title was read and confirmed,
never an id the agent did not itself just resolve. A hallucinated integer
deletes a customer's real policy. **Do not bind the delete tool to an agent that
lacks `Find Business Policies`** — that combination is a destructive tool with no
way to check what it is destroying.

## It happened again on 2026-08-28

A second cleanup pass — this time removing the throwaway probe tools from the
business-policy-create investigation — also deleted `Create CDE Overlay
Standard`. Same tool family, same root cause: a delete list assembled by name
resemblance (everything that looked like a probe) rather than by checking what
each tool was for. Caught only because `./run.sh list tools | grep` was run
afterwards.

It came back with a **new UUID** (`9ce16bd1…`, was `ac3522a7…`), which is the
part that bites quietly: agents store `tool_config_ids` as instance UUIDs
resolved from names at deploy time, so a delete-and-recreate leaves any agent
that bound the old id pointing at nothing. Nothing bound it this time. Redeploy
the agent to re-resolve if it ever does.

Two consequences worth acting on:

* **Always `list tools | grep` after deleting anything**, and compare against
  the table above. That check is what found this.
* The kit has **no `tool delete`** — `cmd_tool` is `show|deploy` only, though
  `agents.py` has `delete_agent` and `TOOL_PATH` is right there. So tool
  deletion happens in the UI, which offers no confirmation and no record of what
  was removed. Both incidents in this file trace to that gap.

## Why this README exists

On 2026-08-28 the cleanup pass deleted this directory and both definitions. The
retired-items audit said the `standards_provisioner` agent *and* its two tool
defs had been **"never deployed to the instance."** The agent hadn't been. The
tools had.

The consequence: two live custom tools on a customer-facing instance with no
source in the repo — so they could not be versioned, redeployed to a second
instance, or torn down by recorded id, which is the one teardown rule this
project treats as non-negotiable. They were recovered by dumping them back out
of the instance.

Two lessons worth keeping:

1. **"Never deployed" is a claim about the instance, and it needs checking
   against the instance.** The audit inferred it from the agent's status, which
   was true of the agent and false of its tools. Anything on a delete list that
   asserts a fact about a remote system gets verified there first.
2. **`list tools` shows tools of every visibility**, including
   `alation_internal` ones that are invisible in the Agent Studio UI and cannot
   be bound to an agent without an FDE flipping them. Presence in that listing
   is not evidence of usability — `Fetch DQ Standards` and `Get Asset Content`
   both appear there and both are internal. Check `visibility` before designing
   on a tool.

## Recovering a definition from the instance

`tool show` does not print `http_config`, so use `--raw`:

```bash
mkdir -p tools
./run.sh tool show "Find Business Policies" --raw > tools/find_business_policies.json
```

The dump is a **list** and carries the server-side `id`. Trim to a single object
and drop `id` before committing — `deploy_tool` matches by name and PUTs to the
resolved id, so a pinned id in a file is at best redundant and at worst wrong on
a different instance.
