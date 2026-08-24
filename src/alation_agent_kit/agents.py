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

from .client import AI_V1, AlationClient
from .store import Lockfile, canonicalize_agent

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

        if dry_run:
            action = f"PATCH {existing_id}" if existing_id else "CREATE (import)"
            print(f"[dry-run] {action} agent {name!r}")
            print(f"[dry-run] fields: {sorted(patch_body)}")
            return {"dry_run": True, "action": action, "name": name}

        if existing_id:
            updated = self.c.patch(f"{AGENT_PATH}/{existing_id}", json_body=patch_body)
            print(f"Updated agent {name!r} (id={existing_id})")
            return updated

        result = self.import_agent(export_doc)
        agent = result.get("agent", result) if isinstance(result, dict) else result
        print(f"Created agent {name!r} (id={agent.get('id')})")
        return result

    def delete_agent(self, name: str) -> None:
        agent_id = self.resolve_agent_id(name)
        if not agent_id:
            print(f"No agent named {name!r}; nothing to delete")
            return
        self.c.delete(f"{AGENT_PATH}/{agent_id}")
        self.lock.forget("agents", name)
        print(f"Deleted agent {name!r} (id={agent_id})")
