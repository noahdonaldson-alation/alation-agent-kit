# `agentkit policy` — commands and the APIs behind them

Reference for the policy provisioning half of the kit. Extracted from the code,
not from memory: every endpoint below is one the kit actually calls.

Run everything as `./run.sh policy <action>`. The default spec is
`policies/bcbs239.json`; pass a path to use another (e.g.
`policies/bcbs239.generated.json`).

## Auth: three separate surfaces

This is the thing that costs newcomers a day, so it is first.

| Surface | Paths | Credential |
|---|---|---|
| Agent Studio | `/ai/api/v1/…` | OAuth bearer (`client_credentials`) |
| Catalog | `/integration/v1/…` | **OAuth bearer works.** Do not add a `TOKEN` header |
| CDE service | `/cde-service/…` | `CDEToken`, bootstrapped from a legacy API token — *and* the bearer works for reads and writes |

- **Bearer:** `POST /oauth/v2/token/` with `grant_type=client_credentials`.
  Cached to `~/.alation/agent-kit-tokens.json`, because minting a new token
  revokes the previous one.
- **Legacy token** (CDE service only): `POST /integration/v1/createAPIAccessToken/`
  with `{refresh_token, user_id}` → `api_access_token`. `token_expires_at` is an
  absolute ISO-8601 instant. Get a refresh token with
  `./run.sh refresh-token <username>`, which returns the token *and* your numeric
  user id.
- **Never send `TOKEN` alongside the bearer on `/integration/`.** Alation
  authenticates as the TOKEN's user, so a token for the wrong user turns a
  working call into `403 "Authentication credentials were not provided"`.
  `ALATION_FORCE_CATALOG_TOKEN=true` exists only for instances with no OAuth
  client.

---

## The commands

### `policy plan [spec] --prefix "BCBS239 - "`
Read-only. Shows what would be created, skipped, or is an unmeetable
prerequisite. Nothing is written.

- `GET /integration/v1/policy_group/?limit=500` — resolve the group by title
  (tries with and without the trailing slash; Allie-SDK and the spec disagree)
- `GET /integration/v1/business_policies/?limit=500&search=<title>` — is each
  policy already there?

### `policy author [--register FILE] [-o OUT]`
Runs the `policy_author` agent: requirements register → policy spec. Computes
the required principles from the register and states that contract in the
invocation, then checks the result against it. Writes
`policies/<reg>.generated.json` with `generated.reviewed: false`.

- `GET /ai/api/v1/config/agent` — resolve the agent by name
- `POST /ai/api/v1/chats/agent/{id}/stream` — invoke it (SSE; the polling path is
  unusable because completed tasks are deleted)
- No catalog calls at all. Policies state obligations, not this bank's tables.

### `policy review <spec> [--approve --by "Name"] [--force]`
Human-readable rendering: each policy's obligation, its paragraph citations,
every quotation marked `[OK]` or `[NOT TRACEABLE]` against the register, and
every attestation field with its options — pickers flagged when they have no
failing answer. `--approve` records *your* approval; it refuses while audit
problems remain unless you pass `--force`.

- No API calls. Entirely local: spec file + register file.

### `policy apply [spec] --prefix "…" --yes`
Creates policies, then the standards derived from them, then self-verifies.
Refuses a generated spec whose `generated.reviewed` is not `true`.

- `GET /integration/v1/policy_group/` — resolve the group id
- `POST /integration/v1/business_policies/` — **body is a bare array**, returns
  `202 {"task": {"id": N}}` and **no object ids**
- `GET /api/v1/bulk_metadata/job/?id=N` — poll to a terminal state. Terminal is
  `state == "finished"` or `status ∈ {succeeded, failed, partial_success,
  skipped}`. **`na` is not terminal.**
- `GET /api/job_error/?job_id=N` — per-row errors when a job did not fully succeed
- `GET /integration/v1/business_policies/?search=<title>` — recover the new id by
  its namespaced title, since the job does not return ids
- `POST /cde-service/integration/auth/` (header `TOKEN`) → `CDEToken`
- `POST /cde-service/integration/standard/` (header `CDEToken`) — one object per
  call, synchronous, returns `{id, key}`. Record the **integer `id`**; the
  update and delete paths take it, not the UUID.

### `policy verify [spec] --prefix "…"`
Reads every recorded id back and confirms it is the object the state file claims
— and that the state matches *this spec*. Reports `STALE RECORD` (right ref,
wrong title, so `apply` skipped creating the current one) and `ORPHAN RECORD`
(left over from an earlier spec). Also reports each standard's status.

- `GET /integration/v1/business_policies/?limit=500`
- `GET /cde-service/integration/standard/{id}/` (header `CDEToken`)

### `policy publish --prefix "…" --yes`
Moves standards to `PUBLISHED`. Status is a **state machine**: `DRAFT →
PUBLISHED` is refused, so it walks `DRAFT → PENDING_APPROVAL → PUBLISHED`,
reading the status back after every hop because the approval workflow can divert
one. CDM applies only published versions.

- `GET /cde-service/integration/standard/{id}/`
- `POST /cde-service/integration/standard/{id}/status/` with
  `{new_status, comment}`. Settable values: `DRAFT`, `PENDING_APPROVAL`,
  `PUBLISHED`. `IN_REVIEW` is observable but not settable.

### `policy assess [spec] [--against OLDSPEC] --prefix "…"`
Read-only drift check. Per policy: **present / missing / untracked / orphaned**,
plus principles that drive CDEs but have no policy. `--against` diffs a freshly
authored spec against the deployed one — `+ NEW POLICY NEEDED`,
`- NO LONGER IMPLIED`, `~ STANDARD … attestation fields changed`.

- `GET /integration/v1/business_policies/?limit=500`
- No writes.

### `policy standards`
Dumps existing overlay standards verbatim — the cheapest authoritative source
for field shapes and the real `type` vocabulary, which the OpenAPI spec leaves
unconstrained.

- `POST /cde-service/integration/auth/`, then
  `GET /cde-service/integration/standard/?limit=50`

### `policy destroy [--yes]`
Deletes **only** objects this kit recorded creating, **by recorded id, never by
name**, in reverse dependency order (standards, then policies). A **published
standard cannot be deleted**, so it walks back to `DRAFT` first. Reads back after
each delete; a survivor **keeps** its state record so teardown can retry — an
object that exists un-recorded is invisible to teardown forever.

- `GET /cde-service/integration/standard/{id}/` — current status
- `POST /cde-service/integration/standard/{id}/status/` — walk back to `DRAFT`
- `DELETE /cde-service/integration/standard/{id}/`
- `DELETE /integration/v1/business_policies/` with `{"ids": [1,2,3]}` — the one
  policy write that takes an **object**, synchronous, 204
- Policy groups are never deleted: the kit cannot create them, so it does not
  own them.

---

## Full sequence

```bash
./run.sh preflight                      # assert prerequisites, read-only
./run.sh policy author                  # register -> spec (agent)
./run.sh policy review policies/bcbs239.generated.json
./run.sh policy review policies/bcbs239.generated.json --approve --by "Your Name" --force
./run.sh policy plan  policies/bcbs239.generated.json --prefix "BCBS239 - "
./run.sh policy apply policies/bcbs239.generated.json --prefix "BCBS239 - " --yes
./run.sh policy publish --prefix "BCBS239 - " --yes
./run.sh policy verify  policies/bcbs239.generated.json --prefix "BCBS239 - "
./run.sh policy assess  policies/bcbs239.generated.json --prefix "BCBS239 - "
./run.sh policy destroy --yes           # teardown, by recorded id only
```

## What is NOT reachable, and why

**Business policies cannot be created from an Agent Studio tool.** Three
independent walls:

1. `Update a Catalog Object` has a closed otype enum — `schema, table, column,
   bi_*` — with no `business_policy`.
2. `POST` **and** `PUT /integration/v1/business_policies/` take a bare **array**,
   while an HTTP tool's body can only ever be a JSON **object**. Two independent
   reasons, and the second is now proven by execution rather than inferred:
   * `HTTPConfigCreate` is `additionalProperties: false` with only
     `url`/`method`/`timeout_seconds` — there is no `body` field and no
     templating layer anywhere in the tool surface, so the body can only be the
     tool-call arguments object.
   * **`input_parameter_schema` is validated to be `type: "object"` at tool
     CREATE time.** Verified 2026-08-28 by deploying
     a throwaway tool definition with a top-level array schema:
     `422 {"loc": ["body", "input_parameter_schema"], "msg": "Value error, Input
     schema must have type 'object'"}`.
     **The OpenAPI spec does not show this.** It declares the field as
     `{"anyOf": [{"additionalProperties": true, "type": "object"}, {"type":
     "null"}]}`, where `type: "object"` constrains the field's *value* and
     `additionalProperties: true` reads as "no constraint on contents" — so the
     spec suggests an array schema is allowed. A Pydantic field validator
     enforces more than the schema declares. Generalise: on this surface, a
     permissive-looking `additionalProperties: true` is not evidence of
     permissiveness. Only the call is.
   * **And the endpoint says so in plain words.** Sending a flat single policy
     object instead returns
     `400 {"detail": "Single item payload processing not supported, for now. Put
     it into a list and resubmit the data.", "code": "400010"}`.
     Quote that verbatim in any product conversation — note **"for now"**, which
     is Alation acknowledging the limitation as temporary.

   The probe tool definitions were **deliberately not kept in `tools/`.** A file
   called `create_business_policy.json` sitting beside four live tools reads as a
   capability this project has; the error strings above are both the stronger
   evidence and the safer artifact.

   Three independent executions, all negative: array-typed input schema → 422 at
   tool-create time; nested `{"policies": [{…}]}` → the outer object is validated
   *as* a policy and fails on missing `title`; flat single object → refused for
   single-item processing. An HTTP tool's body is always a JSON object and this
   endpoint always requires a JSON array.

   **Do not read a field-level 400 as progress.** The validator runs in stages,
   all returning `400010` — `"Syntactic validation failed"` (JSON Schema), then
   `"Semantic validation failed"` (business rules), then processing. Walking
   forward through those stages looks like converging on success and is not;
   reaching a later stage proves only that the body was *parseable* as a policy
   item. This produced one full wrong reversal on 2026-08-28 before the
   processing step was ever reached.
3. `Create or Update Document` *can* write synchronously, but produces Document
   Hub documents — and CDM standards only source from Policy Center policies
   (tested directly).

Standards, by contrast, are object-bodied, synchronous, return `{id, key}`, and
accept the bearer alone — so a Flow step could create them. The missing
capability is a `create_business_policy` tool.

**What IS reachable, and it is an uncomfortable asymmetry.** `DELETE
/integration/v1/business_policies/` takes an **object** — `{"ids": [1,2,3]}`,
synchronous, 204, no bulk job — which maps onto the named-parameter model
exactly. So a custom HTTP tool can delete business policies, and
`tools/delete_business_policies.json` does. Read together with the wall above:
**as the product stands an agent can be given the power to delete business
policies but not to create them.** Scope who gets that tool accordingly.

Note the endpoint takes ids, so **no namespace guard is possible in the tool
config** — nothing there can enforce the `BCBS239 - ` prefix. That guard has to
live in the agent's prompt (resolve titles with `Find Business Policies` first,
delete only ids whose title was read and confirmed, never pass an id the agent
did not itself just resolve). A hallucinated integer deletes a customer's real
policy. This is precisely why the kit deletes by *recorded* id from a state
file; an agent has no equivalent ledger, so in chat the human is the ledger.

**Why three tools still would not replace the kit.** Even granting a working
create tool, the write is async: `202` with a task id and no object ids. So
policy creation from an agent is create → confirm-by-search → record, and the
recording has nowhere durable to live — chat context is not a state file, Flows
have no memory between runs, and `Save Asset` expires in 4 hours. Three tools
buy a self-contained create-and-clean-up demo **inside one conversation**. They
do not buy provisioning, because the state file is the part with no in-product
equivalent.

## Reading the API before guessing

`developer.alation.com/dev/reference/<slug>` renders client-side and fetches as
nav only. **Append `.md` and you get the full OpenAPI spec inline.** To find
slugs, fetch a reference page *without* `.md` — the nav lists them all. For
docs.alation.com use
`https://docs.alation.com/en/latest/_sources/<path>.rst.txt`.

Every bug in this module came from inventing a schema instead of doing that:
`accepted_values` (should be `allowed_values`), the job status enum, the CDE
token header, `tool_config_ids` on a tool-less agent, and the status state
machine.
