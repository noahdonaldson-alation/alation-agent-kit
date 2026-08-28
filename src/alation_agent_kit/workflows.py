"""Agent Studio Workflows (Flows): CRUD, execution, and run inspection.

A Flow is how this pipeline becomes a thing an SE runs from the Alation UI
instead of a terminal. Verified schema (spec 2026.7.1.0, `create_workflow.md`):

    POST /ai/api/v1/workflow/
    {"name", "description",
     "definition": {"nodes": [{"id", "type", "data": {"inputs", "config"}}]}}

## What a Flow can and cannot do

`NodeType` is a **closed enum of three**: `type_start`, `type_agent`,
`type_tool`. That is the whole vocabulary.

- **No conditional node. No transform node. No loops. No edges.**
  `WorkflowDefinition` has one field, `nodes`, and execution is *sequential from
  first to last*, each step exactly once.
- So anything shaped like "if the check found something, send the email" has to
  live in an agent's prompt. Alation's own recipe describes a conditional email
  step; there is no if-node, and the email sends every run. Do not design against
  it.
- Likewise, "reformat this JSON into markdown" cannot be a transform step. It has
  to be an agent, which is why the readable-report step is an agent rather than
  code.

## How data moves between steps — the important part

`NodeData.inputs` maps a **target parameter name** to one of exactly two things:

    {"type": "static",    "value": <any JSON>}
    {"type": "reference", "node_id": "<upstream id>", "output_key": "__agent_output__"}

The spec's own example wires a reference into an agent's **`message`** — the same
uncapped path the CLI already uses when it invokes an agent directly. Across the
whole workflow surface there is no `maxLength`, no `maxItems`, and no truncation
language, and `StaticInput.value` has no declared type at all.

**This matters because our register is ~56KB.** The ~10,000-character cap we know
about is documented as belonging to the *SQL Execution tool* formatting its own
results for a model — not to flow plumbing. So the risk is much lower than it
first appeared. But absence of a documented cap is not proof of absence, hence
`probe_payload()` below: push a known-size blob through a two-node flow and
compare what arrived against what was sent. That isolates the plumbing from
anything the model does.

There is **no pass-by-reference affordance** — only `context`, `StaticInput` and
`ReferenceInput`. Passing an id instead of a payload would mean persisting the
register as a catalog object ourselves.

## Executing

`POST /workflow/{id}/execute` runs in the background and survives client
disconnect; `execute-sync` is one HTTP request with no documented timeout, so an
undocumented gateway ceiling applies. For a chain whose first step emits 56KB,
prefer the background form.

Note the asymmetry that will trip a client: runs are **listed** under a workflow
(`GET /workflow/{id}/executions`) but **fetched** from a sibling collection
(`GET /workflow/executions/{execution_id}`).
"""

from __future__ import annotations

import json
import time
from typing import Any

from .client import AI_V1, AlationClient, AlationError

WORKFLOW = f"{AI_V1}/workflow"
EXECUTIONS = f"{AI_V1}/workflow/executions"

# The complete NodeType enum. Anything else is a 422.
NODE_TYPES = ("type_start", "type_agent", "type_tool")


def static(value: Any) -> dict:
    """A literal input baked into the flow definition."""
    return {"type": "static", "value": value}


# An agent node's output is keyed `__agent_output__`. The OpenAPI example wires
# `output_key: "result"`, which does not exist at runtime — a flow using it saves
# fine and then fails with "Key 'result' not found in node '<id>' output".
# Verified against a live run 2026-08-28. Workflow validation is runtime-only, so
# the definition is accepted and the error only appears on execution.
AGENT_OUTPUT_KEY = "__agent_output__"


def reference(node_id: str, output_key: str | None = AGENT_OUTPUT_KEY) -> dict:
    """An input read from an upstream node's output.

    Defaults to `__agent_output__`, which is what an agent node actually
    produces — NOT `result`, despite the spec's example. Pass `output_key=None`
    to reference the whole output dict instead of one key.
    """
    ref: dict[str, Any] = {"type": "reference", "node_id": node_id}
    if output_key:
        ref["output_key"] = output_key
    return ref


def start_node(node_id: str = "start", description: str = "") -> dict:
    """The trigger node. `StartTriggerConfig` carries only a description —
    there is no trigger type and no event source, which is why there are no
    webhooks."""
    return {"id": node_id, "type": "type_start",
            "data": {"inputs": {}, "config": {"description": description}}}


def agent_node(node_id: str, agent_id: str, inputs: dict,
               description: str = "") -> dict:
    return {"id": node_id, "type": "type_agent",
            "data": {"inputs": inputs,
                     "config": {"agent_id": agent_id,
                                "description": description}}}


def tool_node(node_id: str, tool_id: str, inputs: dict,
              description: str = "") -> dict:
    return {"id": node_id, "type": "type_tool",
            "data": {"inputs": inputs,
                     "config": {"tool_id": tool_id,
                                "description": description}}}


class Workflows:
    def __init__(self, client: AlationClient):
        self.c = client

    # -- read --------------------------------------------------------------
    def list(self, limit: int = 100) -> list[dict]:
        resp = self.c.get(f"{WORKFLOW}/", params={"limit": limit})
        if isinstance(resp, list):
            return resp
        for key in ("data", "results", "items", "workflows"):
            if isinstance(resp, dict) and isinstance(resp.get(key), list):
                return resp[key]
        return []

    def get(self, workflow_id: str) -> dict:
        return self.c.get(f"{WORKFLOW}/{workflow_id}")

    def resolve_id(self, name: str) -> str | None:
        """Name -> id. Names are not unique server-side, so a duplicate raises."""
        want = (name or "").strip().lower()
        hits = [w for w in self.list()
                if str(w.get("name") or "").strip().lower() == want]
        if len(hits) > 1:
            raise RuntimeError(
                f"{len(hits)} workflows named {name!r}: "
                f"{[h.get('id') for h in hits]}. Rename or delete one.")
        return hits[0].get("id") if hits else None

    # -- write -------------------------------------------------------------
    def resolve_agents(self, doc: dict, log: list[str] | None = None) -> dict:
        """Replace `config.agent` (a NAME) with `config.agent_id` (this
        instance's UUID), and likewise `config.tool` -> `config.tool_id`.

        Committed files carry names because ids are per-instance — the same
        reason table references are resolved at deploy time rather than pinned.
        Refuses on an unresolvable name rather than deploying a flow that will
        fail at runtime: workflow validation is runtime-only, so a bad agent_id
        saves cleanly and breaks later, which is the worst place to find out.
        """
        from .agents import AgentStudio

        studio = AgentStudio(self.c)
        out = json.loads(json.dumps(doc))
        agent_ids: dict[str, str] = {}
        tool_ids: dict[str, str] = {}

        for node in (out.get("definition") or {}).get("nodes") or []:
            cfg = (node.get("data") or {}).get("config") or {}
            name = cfg.pop("agent", None)
            if name:
                if name not in agent_ids:
                    resolved = studio.resolve_agent_id(name)
                    if not resolved:
                        raise RuntimeError(
                            f"node {node.get('id')!r} references agent {name!r}, "
                            f"which does not exist on this instance. Deploy it "
                            f"first: ./run.sh deploy agents/{name}.json "
                            f"--prompt {name}")
                    agent_ids[name] = resolved
                cfg["agent_id"] = agent_ids[name]
                if log is not None:
                    log.append(f"  resolved agent {name} -> {agent_ids[name]}")
            tname = cfg.pop("tool", None)
            if tname:
                if tname not in tool_ids:
                    resolved = studio.resolve_tool_id(tname)
                    if not resolved:
                        raise RuntimeError(
                            f"node {node.get('id')!r} references tool {tname!r}, "
                            f"which is not visible on this instance.")
                    tool_ids[tname] = resolved
                cfg["tool_id"] = tool_ids[tname]
                if log is not None:
                    log.append(f"  resolved tool {tname} -> {tool_ids[tname]}")
        return out

    def deploy(self, doc: dict, dry_run: bool = False) -> dict:
        """Upsert by name. Create is POST; update is PUT.

        `WorkflowUpdate` is partial at the top level, but sending `definition`
        replaces the **whole** node array — there is no per-node patch. Same
        replace-not-merge shape as agent PATCH, so a partial definition silently
        drops steps.
        """
        body = {k: v for k, v in doc.items() if not k.startswith("$")}
        for field in ("name", "definition"):
            if not body.get(field):
                raise ValueError(f"workflow file is missing required {field!r}")

        nodes = (body["definition"] or {}).get("nodes") or []
        if not nodes:
            raise ValueError("definition.nodes is empty")
        ids = [n.get("id") for n in nodes]
        if len(set(ids)) != len(ids):
            raise ValueError(f"duplicate node ids: {ids}")
        for n in nodes:
            if n.get("type") not in NODE_TYPES:
                raise ValueError(
                    f"node {n.get('id')!r} has type {n.get('type')!r}; the only "
                    f"valid values are {NODE_TYPES}")
            # A reference to a node that does not exist, or that runs later,
            # cannot resolve — execution is strictly sequential.
            for param, spec in ((n.get("data") or {}).get("inputs") or {}).items():
                if isinstance(spec, dict) and spec.get("type") == "reference":
                    src = spec.get("node_id")
                    if src not in ids:
                        raise ValueError(
                            f"node {n['id']!r} input {param!r} references unknown "
                            f"node {src!r}")
                    if ids.index(src) >= ids.index(n["id"]):
                        raise ValueError(
                            f"node {n['id']!r} input {param!r} references "
                            f"{src!r}, which does not run earlier. Flows are "
                            f"sequential from first to last.")
                    # An agent node's output key is `__agent_output__`. Catch a
                    # wrong key here rather than at runtime — the API accepts any
                    # string and fails only when the flow executes.
                    src_node = next(x for x in nodes if x.get("id") == src)
                    key = spec.get("output_key")
                    if (src_node.get("type") == "type_agent" and key
                            and key != AGENT_OUTPUT_KEY):
                        raise ValueError(
                            f"node {n['id']!r} input {param!r} reads "
                            f"output_key={key!r} from agent node {src!r}, but an "
                            f"agent's output is keyed {AGENT_OUTPUT_KEY!r}. The "
                            f"OpenAPI example says 'result'; that fails at "
                            f"runtime.")

        if dry_run:
            print(f"[dry-run] workflow {body['name']!r}: {len(nodes)} node(s)")
            for n in nodes:
                cfg = (n.get("data") or {}).get("config") or {}
                tgt = cfg.get("agent_id") or cfg.get("tool_id") or ""
                print(f"[dry-run]   {n['id']:20} {n['type']:12} {tgt}")
            return {"dry_run": True, "name": body["name"]}

        existing = self.resolve_id(body["name"])
        if existing:
            updated = self.c.put(f"{WORKFLOW}/{existing}", json_body=body)
            print(f"Updated workflow {body['name']!r} (id={existing})")
            return updated
        created = self.c.post(f"{WORKFLOW}/", json_body=body)
        wid = created.get("id") if isinstance(created, dict) else None
        print(f"Created workflow {body['name']!r} (id={wid})")
        return created

    def delete(self, workflow_id: str) -> None:
        self.c.delete(f"{WORKFLOW}/{workflow_id}")

    # -- run ---------------------------------------------------------------
    def execute(self, workflow_id: str, context: dict | None = None,
                background: bool = True) -> dict:
        """Start a run. Background by default — it survives client disconnect.

        `execute-sync` is a single HTTP request with no documented timeout, so a
        long chain risks an undocumented gateway cutoff.
        """
        path = f"{WORKFLOW}/{workflow_id}/" + ("execute" if background else "execute-sync")
        return self.c.post(path, json_body={"context": context or {}}, timeout=900)

    def runs(self, workflow_id: str, limit: int = 10) -> list[dict]:
        resp = self.c.get(f"{WORKFLOW}/{workflow_id}/executions",
                          params={"limit": limit})
        if isinstance(resp, list):
            return resp
        for key in ("data", "results", "items", "executions"):
            if isinstance(resp, dict) and isinstance(resp.get(key), list):
                return resp[key]
        return []

    def run(self, execution_id: str) -> dict:
        # Note: fetched from the sibling collection, not under the workflow.
        return self.c.get(f"{EXECUTIONS}/{execution_id}")

    def nodes(self, execution_id: str) -> list[dict]:
        resp = self.c.get(f"{EXECUTIONS}/{execution_id}/nodes")
        if isinstance(resp, list):
            return resp
        for key in ("data", "results", "items", "nodes"):
            if isinstance(resp, dict) and isinstance(resp.get(key), list):
                return resp[key]
        return []

    def await_run(self, execution_id: str, attempts: int = 120,
                  wait: float = 5.0) -> dict:
        """Poll to a terminal status. Returns the final execution record.

        Terminal values are read from the record rather than assumed — the
        `status` vocabulary is not enumerated in the spec, and inventing one is
        exactly how three policies went missing on the bulk-job path.
        """
        last: dict = {}
        for _ in range(attempts):
            last = self.run(execution_id) or {}
            status = str(last.get("status") or "").lower()
            if status in ("completed", "succeeded", "success", "failed", "error",
                          "cancelled", "canceled"):
                return last
            time.sleep(wait)
        last["_warning"] = (f"still {last.get('status')!r} after "
                            f"{attempts * wait:.0f}s")
        return last


def probe_payload(client: AlationClient, size_kb: int = 56,
                  agent_id: str | None = None) -> list[str]:
    """Does a large payload survive step-to-step passing intact?

    THE question for chaining this pipeline in a Flow. Our register is ~56KB and
    a ~10k truncation would silently deliver a fifth of it — which would look
    like a model that forgot the regulation, not like truncation.

    Method: build a throwaway two-node flow, push a blob of known size in as a
    STATIC input on the second node, run it, then read
    `GET /workflow/executions/{id}/nodes` and compare the recorded `input_data`
    length against what was sent. Static rather than a reference deliberately —
    it tests the plumbing without a model in the loop. Deletes the flow after.

    Returns log lines; never raises past the caller.
    """
    log: list[str] = []
    wf = Workflows(client)

    # A recognisable, incompressible-ish marker string so truncation is obvious
    # and a partial arrival can be measured rather than guessed at.
    chunk = "".join(f"[{i:06d}]" for i in range(size_kb * 1024 // 9))
    sent = len(chunk)
    log.append(f"probe payload: {sent:,} chars (~{sent/1024:.0f}KB)")

    if agent_id is None:
        from .agents import AgentStudio
        agents = AgentStudio(client).list_agents()
        if not agents:
            return log + ["! no agents visible; cannot build a probe flow"]
        agent_id = agents[0].get("id")
        log.append(f"using agent {agents[0].get('name')!r} as the sink")

    doc = {
        "name": "AGENTKIT PROBE - payload size - delete me",
        "description": "Throwaway flow testing whether a large step input "
                       "survives intact. Safe to delete.",
        "definition": {"nodes": [
            start_node("start", "probe"),
            agent_node("sink", agent_id,
                       {"message": static(
                           "Reply with only the number of characters you "
                           "received after the word PAYLOAD, nothing else.\n"
                           "PAYLOAD\n" + chunk)},
                       "receives the probe payload"),
        ]},
    }

    wid = None
    try:
        created = wf.deploy(doc)
        wid = created.get("id") if isinstance(created, dict) else None
        if not wid:
            return log + [f"! create returned no id: {created}"]

        started = wf.execute(wid, background=True)
        eid = (started or {}).get("id") or (started or {}).get("execution_id")
        if not eid:
            return log + [f"! execute returned no execution id: {started}"]
        log.append(f"execution {eid} started; polling")

        final = wf.await_run(eid)
        log.append(f"status: {final.get('status')}"
                   + (f"  ({final['_warning']})" if final.get("_warning") else ""))
        if final.get("error_message"):
            log.append(f"error: {final['error_message']}")

        for n in wf.nodes(eid):
            nid = n.get("node_id") or n.get("id")
            got = json.dumps(n.get("input_data") or {}, default=str)
            arrived = got.count("[0")  # marker occurrences survive intact
            log.append(f"  node {nid!r}: input_data {len(got):,} chars, "
                       f"{arrived:,} markers")
            if nid == "sink":
                if len(got) >= sent * 0.9:
                    log.append("  => PAYLOAD ARRIVED INTACT. Step-to-step "
                               "passing is not truncating at 56KB; chaining the "
                               "register through a Flow is safe.")
                else:
                    log.append(f"  => TRUNCATED: sent {sent:,}, recorded "
                               f"{len(got):,} ({len(got)/sent:.0%}). Chaining "
                               f"the register directly will lose most of it — "
                               f"persist it as a catalog object and pass an id.")
    except (AlationError, RuntimeError) as err:
        log.append(f"! probe failed: {str(err)[:300]}")
    finally:
        if wid:
            try:
                wf.delete(wid)
                log.append(f"probe flow {wid} deleted")
            except Exception as err:  # noqa: BLE001
                log.append(f"! probe flow {wid} NOT deleted ({str(err)[:80]}) "
                           f"— remove it in the UI")
    return log
