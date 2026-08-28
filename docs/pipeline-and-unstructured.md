# The pipeline, and folding in unstructured documents

**Goal.** One runnable pipeline that assesses a catalog for gaps against
*whatever regulation or policy document currently sits in Alation's unstructured
data* — not against a text file someone extracted months ago.

The unstructured feature is not available on our instance yet. This document
records what is built now, what is deliberately stubbed, and exactly what changes
when the feature lands, so folding it in is a config change rather than a rewrite.

## The three runtimes, and why there are three

| Runtime | Purpose | Status |
|---|---|---|
| **Kit, file source** | Prompt iteration. Fast, free, deterministic, no ACU. | Working |
| **Kit, unstructured source** | Reproducible assessment of the *current* document, with provenance. | Stubbed, prerequisites blocked |
| **Agent Studio Flow** | The delivered artifact: runs inside the customer's Alation, no laptop involved. | Designed, not built |

These are not competing options and the abstraction is not indecision. A Flow
cannot be iterated on — 30–60s per PDF retrieval, no caching, ACU per call,
nondeterministic search — so prompt development has to happen in the kit
regardless. The same prompt then runs in the Flow. **One prompt, three
runtimes** is the property worth protecting.

## What exists now

- **`sources.py`** — `RegulationSource` with `FileSource` (working) and
  `UnstructuredSource` (stubbed). Every fetch returns a `Regulation` carrying
  provenance: source type, locator, `retrieved_at`, content `sha256`, char
  count, truncation flag.
- **`preflight.py`** — read-only prerequisite assertions. Unstructured checks are
  marked **optional**, so preflight passes today; they flip to informative the
  moment an FDE enables things.
- **`pipeline.py`** + `agentkit pipeline` — source → interpret → validate → map
  → validate → manifest, in one command.
- **`agentkit preflight`** — tells a field SE what is missing before they deploy,
  rather than after a mid-deploy 403.

Why provenance was worth building before the feature: the point of the pipeline
is a gap analysis *traceable to a document version*. Without a content hash,
`pde-mapping-postsql-01.json` is a file with no attribution — we could not prove
which register produced it, and re-running after a document is amended would
produce two indistinguishable results.

## The constraint that shapes the Flow design

**The register is ~56KB compact JSON. Alation truncates tool results near 10k
characters — 5.6× over.**

This is the single most important fact for a Flow-based version. The kit passes
the register as the agent *message*, which has no such cap, so it works today.
A Flow that chains interpreter → mapper by passing the register as a **tool
result** would silently deliver about a fifth of it, and the failure would look
like a model that forgot most of the regulation rather than like truncation.

`pipeline.py` checks the size and says so on every run (`TOOL_RESULT_CAP_CHARS`).
Three ways out, in order of preference:

1. **Verify Flow step-to-step passing is not tool-result-capped.** Alation's Flow
   docs describe step output becoming step input; if that path is a message
   rather than a tool result, the problem disappears. **Unverified — test this
   first, it is the cheapest possible answer.**
2. **Persist the register as a catalog object** (a document or data product) and
   have the mapper retrieve it by id. Turns a 56KB payload into a reference.
   More moving parts, but it also gives the register a home and a version.
3. **Shard the register** — run the mapper per CDE, ~11 invocations. Correct but
   costly: ~11× the ACU, and it loses the cross-CDE view the mapper currently
   uses for `cross_cutting_dq`.

Option 3 is a real fallback; option 1 needs one experiment to confirm or kill.

## What changes when unstructured lands

Nothing about the prompts, the register schema, the mapper, or the policy
provisioning. Specifically:

1. **`UnstructuredSource._call_tool()`** — the one stubbed method. It currently
   refuses with an explanation rather than guessing an endpoint, because guessing
   API paths has cost this project time twice. Two supported routes:
   - Give an agent `get_asset_content` and invoke that agent, reading its output
     (this is also the Flow design, so it is the same work twice over); or
   - Confirm a direct tool-invocation endpoint exists and implement it.
2. **`preflight`** optional checks start passing. No code change.
3. **`--source unstructured --object-id <uuid>`** starts working. Note ids here
   are **UUIDs**, not integers — `get_object_fields` fails on them by design.
4. Truncation becomes a live concern. Content is capped at 1MB with a
   `truncated` flag; `UnstructuredSource` **raises** rather than analysing a
   fragment, because a gap analysis over a truncated regulation reports absent
   requirements that were merely unread. BCBS 239 is ~120KB, so this is only a
   risk for larger internal policy packs.

## Prerequisites we cannot satisfy ourselves

Bundle these into **one** request to an FDE (Jon Lanham) — discovered serially
they cost two round trips:

1. `alation.feature_flags.enable_unstructured_data = true`, plus
   `unstructured_data_source,unstructured_data_file` appended to
   `DEV_otype_service_enabled_otypes`, then a deployment restart. Needs SSH or
   the Cloud console conf-flags editor.
2. **`get_asset_content_tool` visibility raised from `ALATION_INTERNAL`.** Uses a
   non-public admin API authenticated by browser session cookies
   (`PUT /ai/api/v1/admin/tool_configs/{uuid}/visibility?visibility_label=advanced`)
   — an OAuth client cannot do this. It is a prerequisite, not automation.
3. An unstructured OCF connector (S3 / SharePoint / Confluence, zip installs)
   harvesting the PDF into a collection, indexed as `unstructured_data_file`.

## The end state

```
PDF in S3/SharePoint/Confluence
  -> unstructured OCF connector -> Unstructured Collection
  -> [Flow step 1] agent + get_asset_content   -> regulation markdown
  -> [Flow step 2] bcbs239_cde_dq_interpreter  -> requirements register
  -> [Flow step 3] bcbs239_pde_mapper          -> gap analysis
  -> policies + overlay standards (already provisioned by `agentkit policy`)
```

Steps 2 and 3 are verified working today via the kit. Step 1 is blocked on
prerequisites. The join between steps 2 and 3 is the 56KB/10k question above.

Note also: **Flows are cron-triggered (60-minute minimum) or externally
invoked — there are no inbound webhooks or event triggers.** So "reassess when
the document changes" is a schedule that polls, not an event. If a narrative
needs true event-driven reassessment, that is a product gap, not a config
problem.
