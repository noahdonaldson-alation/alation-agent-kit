"""Agent, tool, and LLM config operations.

The important asymmetries, learned the hard way from the API spec:
  * Agent update is PATCH (partial). Tool update is PUT (full replace).
  * `POST /config/agent/import` is CREATE-ONLY. It has no `id` field, returns a
    new agent, and regenerates UUIDs. Re-importing CLONES rather than updates.
    So deploy() does list -> match by name -> PATCH, and only falls back to
    create when the agent genuinely does not exist.
  * Auth/credentials are excluded from exports, by design. After importing to a
    new instance you must reattach auth configs; `import` returns `warnings`
    listing what needs manual attention.
"""

from __future__ import annotations

from typing import Any

from .client import AI_V1, AlationClient, AlationError
from .store import Lockfile, canonicalize_agent, llm_identity

AGENT_PATH = f"{AI_V1}/config/agent"
TOOL_PATH = f"{AI_V1}/config/tool"
LLM_PATH = f"{AI_V1}/config/llm"

# Fields accepted on create. Anything else the server rejects
# (AgentConfigCreate is additionalProperties: false).
_CREATE_FIELDS = {
    "name", "description", "prompt", "llm_config_id", "tool_config_ids",
    "parameter_bindings", "llm_extra_config", "input_json_schema",
    "output_json_schema", "mcp_server_config_ids", "tags",
}


def _as_list(payload: Any) -> list[dict]:
    if isinstance(payload, list):
        return payload
    for key in ("results", "items", "data", "agents", "tools"):
        if isinstance(payload, dict) and isinstance(payload.get(key), list):
            return payload[key]
    return []


class AgentStudio:
    def __init__(self, client: AlationClient | None = None, lockfile: Lockfile | None = None):
        self.c = client or AlationClient()
        self.lock = lockfile or Lockfile()

    # -- read --------------------------------------------------------------
    def list_agents(self) -> list[dict]:
        return _as_list(self.c.get(AGENT_PATH))

    def list_tools(self) -> list[dict]:
        return _as_list(self.c.get(TOOL_PATH))

    def list_llms(self) -> list[dict]:
        return _as_list(self.c.get(LLM_PATH))

    def get_agent(self, agent_id: str) -> dict:
        return self.c.get(f"{AGENT_PATH}/{agent_id}")

    def resolve_agent_id(self, name: str) -> str | None:
        """Lockfile first, then a live list-and-match. Names are not enforced
        unique server-side, so a duplicate is an error worth raising."""
        cached = self.lock.get("agents", name)
        if cached:
            return cached
        matches = [a for a in self.list_agents() if a.get("name") == name]
        if len(matches) > 1:
            raise RuntimeError(
                f"{len(matches)} agents are named {name!r}. Names are not unique in Alation; "
                "rename or delete the duplicates, or pin the UUID in .lockfile.json."
            )
        if matches:
            agent_id = matches[0].get("id")
            if agent_id:
                self.lock.set("agents", name, agent_id)
            return agent_id
        return None

    # -- export-shape -> config-shape resolution ---------------------------
    def resolve_llm_config_id(self, llm: dict) -> str | None:
        """Find the instance UUID for a portable `llm` block from an export.

        Exports describe the model portably; PATCH and POST want an
        `llm_config_id` UUID. The list endpoint and the export use different
        field names, so matching goes through `llm_identity()` and compares
        against every reference string a row exposes. Most specific first:

          1. any reference string matches (e.g. the composite provider:model ref)
          2. provider + model_name together
          3. friendly name match
          4. provider alone, only if unambiguous

        Returns None rather than guessing when the match is ambiguous.
        """
        if not llm:
            return None
        candidates = self.list_llms()
        if not candidates:
            return None

        idents = [(c, llm_identity(c)) for c in candidates]

        # Every string the file offers as an identifier for this model.
        wanted = [
            v for v in (llm.get("default_llm_ref"), llm.get("model_name"), llm.get("model"))
            if isinstance(v, str) and v
        ]

        for w in wanted:
            hits = [c for c, i in idents if w in i["refs"]]
            if len(hits) == 1:
                return hits[0].get("id")

        provider, model = llm.get("provider"), llm.get("model_name")
        if provider and model:
            hits = [
                c for c, i in idents
                if i["provider"] == provider and model in i["refs"]
            ]
            if len(hits) == 1:
                return hits[0].get("id")

        name = llm.get("name") or llm.get("llm_config_name")
        if name:
            hits = [c for c, i in idents if i["name"] == name]
            if len(hits) == 1:
                return hits[0].get("id")

        if provider:
            hits = [(c, i) for c, i in idents if i["provider"] == provider]
            if len(hits) == 1:
                return hits[0][0].get("id")
            if len(hits) > 1:
                print(
                    f"  ! {len(hits)} LLM configs share provider {provider!r} and nothing "
                    f"more specific matched:"
                )
                for c, i in hits:
                    print(f"      {c.get('id')}  {i['name'] or '(unnamed)'}  {i['refs'][:1]}")
                print(
                    '    Pin it explicitly: add "llm_config_id": "<uuid>" to the agent file.'
                )
        return None

    def resolve_tool_config_ids(self, tools: list[dict]) -> list[str] | None:
        """Map exported tool definitions to instance UUIDs, preserving order.

        Order matters: `tool_config_ids` and `parameter_bindings` are matched
        positionally and must be the same length. Returns None if any tool is
        unresolvable, so we never send a partial, misaligned list.
        """
        if not tools:
            return []
        by_name = {t.get("name"): t.get("id") for t in self.list_tools()}
        resolved, missing = [], []
        for t in tools:
            tid = by_name.get(t.get("name"))
            if tid:
                resolved.append(tid)
            else:
                missing.append(t.get("name"))
        if missing:
            print(
                f"  ! tools not found on this instance: {', '.join(map(str, missing))}. "
                f"Create them first (tools are not created by agent deploy)."
            )
            return None
        return resolved

    # -- export ------------------------------------------------------------
    def export_agent(self, name_or_id: str, canonical: bool = True) -> dict:
        agent_id = name_or_id
        if "-" not in name_or_id or len(name_or_id) < 32:
            resolved = self.resolve_agent_id(name_or_id)
            if not resolved:
                raise RuntimeError(f"No agent found named {name_or_id!r}")
            agent_id = resolved
        doc = self.c.get(f"{AGENT_PATH}/{agent_id}/export")
        return canonicalize_agent(doc) if canonical else doc

    # -- write -------------------------------------------------------------
    def import_agent(self, export_doc: dict) -> dict:
        """Create a NEW agent from an export payload. Never use this to update —
        it will clone. Returns {"agent": ..., "warnings": [...]}"""
        result = self.c.post(f"{AGENT_PATH}/import", json_body=export_doc)
        agent = result.get("agent", result) if isinstance(result, dict) else result
        name, agent_id = agent.get("name"), agent.get("id")
        if name and agent_id:
            self.lock.set("agents", name, agent_id)
        for w in (result.get("warnings") or []) if isinstance(result, dict) else []:
            print(f"  ! import warning: {w}")
        return result

    def deploy_agent(self, export_doc: dict, dry_run: bool = False) -> dict:
        """Upsert. PATCH if an agent of this name exists, else create."""
        name = export_doc.get("name")
        if not name:
            raise ValueError("Agent document has no 'name'")

        existing_id = self.resolve_agent_id(name)
        patch_body = {k: v for k, v in export_doc.items() if k in _CREATE_FIELDS}

        # Export shape and config shape disagree: exports carry portable `llm`
        # and `tools`; PATCH/POST want `llm_config_id` and `tool_config_ids`
        # (instance UUIDs). Translate here so a model or tool change in the file
        # actually takes effect instead of silently no-op'ing.
        #
        # This runs for CREATE as well as UPDATE. /config/agent/import demands
        # full inline tool definitions (description, function_name, tool_type) —
        # it is built for seeding an instance that lacks the tools. When the
        # tools already exist, POST /config/agent with resolved UUIDs is the
        # right path, and it keeps create and update speaking the same shape.
        if not dry_run:
            if export_doc.get("llm") and "llm_config_id" not in patch_body:
                llm_id = self.resolve_llm_config_id(export_doc["llm"])
                if llm_id:
                    patch_body["llm_config_id"] = llm_id
                    ref = export_doc["llm"].get("default_llm_ref") or export_doc["llm"].get("provider")
                    print(f"  resolved llm {ref} -> {llm_id}")
                else:
                    print(
                        "  ! could not resolve llm to an llm_config_id; the model will "
                        "NOT be updated. Set it in the UI, or add an explicit "
                        "\"llm_config_id\" to the agent file."
                    )
            if export_doc.get("tools") and "tool_config_ids" not in patch_body:
                tool_ids = self.resolve_tool_config_ids(export_doc["tools"])
                if tool_ids is not None:
                    patch_body["tool_config_ids"] = tool_ids
                    bindings = export_doc.get("parameter_bindings") or []
                    if bindings and len(bindings) != len(tool_ids):
                        raise RuntimeError(
                            f"parameter_bindings ({len(bindings)}) and tools ({len(tool_ids)}) "
                            "must be the same length — they are matched positionally. "
                            "Re-export to fix the pairing."
                        )
                    print(f"  resolved {len(tool_ids)} tool(s) -> tool_config_ids")
                else:
                    print("  ! tools will NOT be updated (see above)")

        # The API rejects `parameter_bindings` unless `tool_config_ids` comes with
        # it — 422 "tool_config_ids must be provided when parameter_bindings is
        # provided". An export of a tool-less agent carries an empty bindings
        # list, so sending it verbatim fails. Drop it when there are no tools.
        if "parameter_bindings" in patch_body and "tool_config_ids" not in patch_body:
            if patch_body["parameter_bindings"]:
                raise RuntimeError(
                    "parameter_bindings is set but tools could not be resolved to "
                    "tool_config_ids. Sending bindings without tool ids is rejected by "
                    "the API, and sending them mismatched would silently rewire the "
                    "agent. Fix the tools first, or re-export."
                )
            patch_body.pop("parameter_bindings")

        # Nulls in an export mean "not set" rather than "clear this", and some
        # endpoints reject them outright. Drop them.
        patch_body = {k: v for k, v in patch_body.items() if v is not None}

        if dry_run:
            action = f"PATCH {existing_id}" if existing_id else "CREATE"
            print(f"[dry-run] {action} agent {name!r}")
            print(f"[dry-run] fields: {sorted(patch_body)}")
            return {"dry_run": True, "action": action, "name": name}

        if existing_id:
            updated = self.c.patch(f"{AGENT_PATH}/{existing_id}", json_body=patch_body)
            print(f"Updated agent {name!r} (id={existing_id})")
            return updated

        # Create via the config path, which takes resolved UUIDs. Falls back to
        # /import only if the config path rejects the body — import needs full
        # inline tool definitions, so it suits cross-instance seeding rather
        # than creating against an instance that already has the tools.
        missing = [f for f in ("prompt", "llm_config_id") if not patch_body.get(f)]
        if missing:
            raise RuntimeError(
                f"Cannot create agent {name!r}: missing {', '.join(missing)}. "
                "A create needs a prompt and a resolvable llm — check `list llms` "
                "and the file's llm block."
            )
        try:
            created = self.c.post(AGENT_PATH, json_body=patch_body)
        except AlationError as err:
            print(f"  ! POST {AGENT_PATH} failed ({err.status}); trying /import")
            result = self.import_agent(export_doc)
            agent = result.get("agent", result) if isinstance(result, dict) else result
            print(f"Created agent {name!r} via import (id={agent.get('id')})")
            return result

        agent_id = created.get("id") if isinstance(created, dict) else None
        if agent_id:
            self.lock.set("agents", name, agent_id)
        print(f"Created agent {name!r} (id={agent_id})")
        return created

    def delete_agent(self, name: str) -> None:
        agent_id = self.resolve_agent_id(name)
        if not agent_id:
            print(f"No agent named {name!r}; nothing to delete")
            return
        self.c.delete(f"{AGENT_PATH}/{agent_id}")
        self.lock.forget("agents", name)
        print(f"Deleted agent {name!r} (id={agent_id})")
