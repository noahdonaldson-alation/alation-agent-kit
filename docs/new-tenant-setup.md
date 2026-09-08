# Standing this up in a new tenant

Ordered so that everything reversible happens before anything permanent.

---

## Answer this first: where does the data come from?

**The warehouse is not in this repo.** `sql/` holds only the prompt that
generated the dimension pack, not the DDL or the data. Without catalogued
columns there is nothing for the CDE agent to find, and scenes 3, 6 and 7 have
nothing to say.

Three options, in order of preference:

1. **Point the new tenant at the same Snowflake** and harvest it. Fastest by far,
   and the demo is identical to the one you recorded.
2. **Regenerate the warehouse** from `sql/generate-bcbs239-dimensions.prompt.md`
   into a Snowflake the new tenant can reach. Costs a build and a load, and the
   column names will differ slightly, which means re-checking scene 6.
3. **Use the customer's own data.** The most compelling version and the most
   work: every column name in the demo script changes, the elements the agent
   proposes will differ, and you cannot rehearse against a fixed script.

Settle this before booking anything. Everything below assumes catalogued columns
exist.

---

## Check the tenant has the entitlements

Not all of these are on by default, and two of them cost days if you find out
late.

| Needs to be on | How you find out it isn't |
|---|---|
| **Agent Studio** | No Agents section in the UI |
| **Critical Data Manager** | No CDM, and `/cde-service/` calls fail |
| **Policy Center** | `GET /integration/v1/policy_group/` returns `403 "Authentication credentials were not provided"` — **which is a lie.** That 403 means the feature is off, not that auth failed. We lost time to this once |
| **Data Quality** | No Data Quality section. Only needed if you show the DQ half of scene 6 |
| **A Bedrock LLM config** | `./run.sh list llms` — the agents reference `bedrock_us-east-1:us.anthropic.claude-sonnet-4-6`. If the tenant has a different model, the agent files need updating |

Also confirm the **base tools** exist and are visible: `Search Catalog`,
`Get Object Fields`, `List Critical Data Elements`, `Query CDE Physical Data
Elements`, `Get Users`. `./run.sh list tools` shows all visibility labels.

---

## Phase 1 — prerequisites nobody can automate

All UI, all before the kit touches anything.

1. **An OAuth client for you.** Minting a token invalidates the previous one, so
   use a client dedicated to you rather than sharing.
2. **Connect the data source and harvest it.**
3. **Create the three custom fields** — `PII Classification`,
   `Sensitivity Classification`, `CDM (contains CDE)`.
4. **Run Curation Automation across all objects**, with vertical-specific
   prompts. **Start this early** — it takes time, and everything downstream reads
   what it writes. Measured effect: 9 → 15 columns found for the same element.
5. **Create the policy group.** Groups have no create API. Match the title
   exactly; `BCBS 239` and `BCBS239` are different groups.
6. **Note your numeric user id** — `./run.sh userid <email>`.

---

## Phase 2 — the kit

**Clone into its own folder, with its own `.env`.** One checkout per tenant.
`.env`, `.lockfile.json` and `.deployment-state*.json` are all instance-specific
and all gitignored, so a fresh clone starts clean — and two checkouts cannot
quietly deploy into each other's tenant.

```bash
git clone <repo> bcbs239-<tenant>
cd bcbs239-<tenant>
cp .env.example .env          # base URL + an OAuth client dedicated to you
./run.sh whoami               # probes Agent Studio, catalog, CDE service
./run.sh list llms            # ← do this BEFORE deploying agents
./run.sh preflight            # asserts prerequisites, read-only
```

**`list llms` is the one that stops a deploy.** Every agent references
`bedrock_us-east-1:us.anthropic.claude-sonnet-4-6`. If the tenant has a different
provider or model, `deploy` refuses to guess and every agent JSON needs its
`default_llm_ref` updated. Cheaper to find out now than halfway through.

**Confirm the base tools exist**, too — `./run.sh list tools`. A missing one
aborts an agent deploy, since tools resolve by name.

> **`.lockfile.json` was committed until 2026-09-08.** If your clone predates
> that, delete it before deploying — it holds another tenant's UUIDs, and
> `deploy` checks it before doing a live name match.

**And `CLAUDE.md` does not travel.** It lives in the workspace root, above the
repo, and is not version controlled. A fresh clone has none of the accumulated
API facts. Copy it across, or the next person rediscovers a week of findings the
expensive way.

Then tools first, agents second — agents resolve tools by name at deploy time
and an unresolvable tool aborts the deploy:

```bash
for f in tools/*.json; do [ "${f#*raw}" = "$f" ] && ./run.sh tool deploy "$f"; done

./run.sh deploy agents/bcbs239_obligation_interpreter.json --prompt bcbs239_obligation_interpreter
./run.sh deploy agents/policy_creator.json                 --prompt policy_creator
./run.sh deploy agents/cde_creator.json                    --prompt cde_creator
./run.sh deploy agents/governance_reporter.json            --prompt governance_reporter
```

---

## Phase 3 — content, in an order that protects you

**The rule: everything is reversible until you publish a standard.** Policies can
be deleted. CDE drafts can be deleted. A published overlay standard cannot be
deleted, unpublished or rolled back — ever. So get the policies right *first*,
and publish standards only once you are happy with them.

1. **Run the obligation interpreter** on the regulation text and read the
   register. This is the review gate that matters most: the obligations decide
   the policy set, and the policy set decides what the standards derive from.
2. **Create the policies** with `policy_creator`. Read the bodies before
   approving. Wrong ones are deletable at this stage — that stops being true in
   step 3.
3. **Generate the standards in CDM**, one per policy. Trim each draft. **Then
   publish.** This is the one-way door.
4. **Run `cde_creator`** against the published standards.
5. **Optionally build DQ standards and a monitor** in CDM if you are showing that
   half of scene 6.

If step 2 produced policies you later want to change, fix them **before** step 3.
Deleting a policy after its standard exists leaves the standard behind
permanently, still attached to elements, still claiming a derivation from a
document that no longer exists — and nothing in the UI shows it.

---

## Per-tenant values you must change

Every one of these is instance-specific. The demo script's appendix has our
values baked in.

| Value | Ours | Where it appears |
|---|---|---|
| Data source key | `alation://data/2` | Scene 3, 6 and 7 prompts |
| Overlay standard ids | `641, 656, 657, 658, 659` | Scene 6 prompt — **get the new ones from `./run.sh policy standards`** |
| Policy group id | `1` | Scene 4b prompt |
| Owner user id | `1` | Scene 4b prompt |
| Column and table names | `mcf_risk_gold.fact_risk_exposure`, … | Scene 6 narration, if the warehouse differs |
| LLM ref | `bedrock_us-east-1:us.anthropic.claude-sonnet-4-6` | All four agent JSONs |

**The standard ids are the one that will silently misbehave.** Naming them
explicitly in the scene 6 prompt is what keeps the agent off standards that
shouldn't be used. Copy the wrong ids and it will confidently build elements
against the wrong governance.

---

## Phase 4 — verify before you show anyone

```bash
./run.sh policy standards      # ids, versions, status, source policies
./run.sh policy assess         # drift: what exists vs what the spec expects
```

Then run `governance_reporter` and read it properly. It is the cheapest full
check you have — it will tell you if a standard is orphaned, if an element has no
control point, or if nothing is attached where you thought it was.

And open one CDE in CDM. You want to see: several standards attached, physical
columns with source paths, and one of them marked `control_point`.

---

## What will bite you

**Curation Automation not finished.** Start it first, check it completed.

**Stale ids in the prompts.** See the table above.

**Publishing standards too early.** They are permanent. Get the policies right
first.

**Reusing `.lockfile.json`.** Delete it.

**Assuming the 403 on Policy Center is an auth problem.** It means the feature is
off.

**No control points.** `cde_creator` sets one per element at create time. If you
build elements with an older prompt, every column lands as `suggested` and the DQ
wizard shows an empty list — nine manual promotions before you can demo DQ.

---

## Rehearse the opening

Scene 3's audit is supposed to run against a catalog with nothing built, and a
new tenant is the only place you can actually rehearse that — our instance's
standards are permanent, so it always shows a half-built framework.

Run it once on the fresh tenant **before phase 3**, and see whether the empty
state is interesting enough to open on. If it is thin, open on scene 1 and 2
instead and let the first audit come after the policies exist.
