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

import json
import os
import re

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


# Fields the tool CREATE body carries that the tool UPDATE body forbids. Both
# are immutable on an existing tool, so `PUT /config/tool/{id}` 422s on them with
# `extra_forbidden`. Verified by execution 2026-08-31 on four tools.
_TOOL_UPDATE_STRIP = {"tool_type"}
_TOOL_UPDATE_STRIP_AUTH = {"auth_type"}


def _expand_env(obj: Any) -> Any:
    """Substitute ${VAR} from the environment, recursively.

    Tool configs need an OAuth client_id and client_secret. Those must NOT live
    in a committed file, so the file carries ${ALATION_CLIENT_SECRET} and the
    value is filled at deploy time from .env — same secrets, one place.

    A missing variable raises rather than sending the literal "${VAR}" to
    Alation, which would otherwise be stored as a credential and fail later with
    an opaque auth error.
    """
    if isinstance(obj, dict):
        return {k: _expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env(v) for v in obj]
    if isinstance(obj, str):
        def sub(m):
            name = m.group(1)
            val = os.environ.get(name, "").strip()
            if not val:
                raise RuntimeError(
                    f"tool config references ${{{name}}} but it is not set in the "
                    f"environment or .env. Set it before deploying — sending the "
                    f"literal placeholder would store a broken credential.")
            return val
        return re.sub(r"\$\{([A-Z_][A-Z0-9_]*)\}", sub, obj)
    return obj


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

    # Verified from the AI API OpenAPI spec (2026.7.1.0): GET /config/tool takes
    # only limit / offset / visibility_labels, and visibility_labels DEFAULTS to
    # ["featured", "regular"] — so a bare GET silently hides `advanced` and
    # `alation_internal` tools. That default is very likely why
    # get_asset_content_tool looked absent. Ask for all four.
    VISIBILITY_LABELS = ("featured", "regular", "advanced", "alation_internal")

    def list_tools(self, all_visibilities: bool = True,
                   limit: int = 1000) -> list[dict]:
        params: dict = {"limit": limit}
        if all_visibilities:
            params["visibility_labels"] = list(self.VISIBILITY_LABELS)
        return _as_list(self.c.get(TOOL_PATH, params=params))

    def resolve_tool(self, name: str) -> dict | None:
        """Name -> the whole tool record. No name filter server-side, so match here.

        Matches `name` or `function_name`, since a file may sensibly key on
        either. Ids are UUID strings here, not ints.

        Returns the record rather than just the id because the caller needs
        `tool_type` to tell a custom tool from an Alation base tool — see
        `deploy_tool`, where writing to a base tool is a 400.
        """
        want = (name or "").strip().lower()
        hits = [t for t in self.list_tools()
                if want in {str(t.get("name") or "").strip().lower(),
                            str(t.get("function_name") or "").strip().lower()}]
        if len(hits) > 1:
            raise RuntimeError(
                f"{len(hits)} tools match {name!r} — names are not unique "
                f"server-side. Ids: {[h.get('id') for h in hits]}")
        return hits[0] if hits else None

    def resolve_tool_id(self, name: str) -> str | None:
        """Name -> id. Thin wrapper over `resolve_tool` for callers that only
        need the id (agent deploy mapping `tools[]` to `tool_config_ids`)."""
        hit = self.resolve_tool(name)
        return hit.get("id") if hit else None

    def deploy_tool(self, doc: dict, dry_run: bool = False) -> dict:
        """Upsert a custom tool from a file. Tools are PUT; agents are PATCH.

        Schema notes, all verified against the OpenAPI spec — each one is a trap:
          * `tool_type` values are LOWERCASE (`http`), while `auth_type` and
            `method` are UPPERCASE. Three casing conventions in one body.
          * Required: name, description, function_name, tool_type. An HTTP tool
            additionally needs http_config, auth_config AND
            input_parameter_schema — even a no-auth tool must send
            `auth_config: {"name": ..., "auth_type": "NONE"}`.
          * `ToolConfigCreate` is `additionalProperties: false`, so `$comment`
            and `visibility_label` are both 422s. Visibility is readable but not
            settable through the public API.
          * Secrets do NOT round-trip: a read returns `custom_headers_preview`
            and truncated `client_secret`, so an exported tool cannot be
            re-deployed without re-supplying them.
        """
        body = _expand_env(
            {k: v for k, v in doc.items() if not k.startswith("$")})
        body.pop("visibility_label", None)      # read-only; sending it is a 422
        body.pop("id", None)

        for field in ("name", "description", "function_name", "tool_type"):
            if not body.get(field):
                raise ValueError(f"tool file is missing required {field!r}")
        if body.get("tool_type") == "http":
            for field in ("http_config", "auth_config", "input_parameter_schema"):
                if not body.get(field):
                    raise ValueError(
                        f"an http tool needs {field!r} — the API rejects it "
                        f"otherwise (a public endpoint still needs "
                        f"auth_config with auth_type NONE)")

        name = body["name"]
        hit = self.resolve_tool(name) if not dry_run else None

        # A NAME MATCH IS NOT NECESSARILY OUR TOOL. Alation ships base tools, and
        # `resolve_tool` matches on name alone, so a custom tool file that
        # collides with a built-in resolves to the BUILT-IN and the upsert aims a
        # PUT at it. Observed 2026-09-03 deploying a hand-written
        # `List Critical Data Elements`, which Alation already ships:
        #   400 {"detail": "Unsupported tool type: default"}
        # `default` is the base-tool type; only `http` (and other custom types)
        # are writable. The 400 saved us, but it is the server refusing rather
        # than the kit declining — and a base tool whose type happened to be
        # writable would have been silently overwritten. So check first.
        if hit and hit.get("tool_type") != body["tool_type"]:
            raise RuntimeError(
                f"tool {name!r} already exists on this instance as tool_type "
                f"{hit.get('tool_type')!r}, but this file declares "
                f"{body['tool_type']!r}. `tool_type` is immutable on an existing "
                f"tool, so this cannot be an update.\n"
                f"  If that is an Alation BASE tool (tool_type 'default'), you "
                f"do not need a custom one — delete the file and reference the "
                f"base tool by name in the agent's tools[].\n"
                f"  If you genuinely need a different tool, rename this one; "
                f"names are how everything here resolves.\n"
                f"  Existing id: {hit.get('id')}")

        existing = hit.get("id") if hit else None
        if dry_run:
            print(f"[dry-run] tool {name!r} ({body['tool_type']}) "
                  f"{body.get('http_config', {}).get('method', '')} "
                  f"{body.get('http_config', {}).get('url', '')}")
            print(f"[dry-run] fields: {sorted(body)}")
            return {"dry_run": True, "name": name}

        if existing:
            # CREATE SHAPE != UPDATE SHAPE, verified by execution 2026-08-31.
            # `PUT /config/tool/{id}` rejects `tool_type` and
            # `auth_config.auth_type`:
            #   422 extra_forbidden loc:["body","tool_type"]
            #   422 extra_forbidden loc:["body","auth_config","auth_type"]
            # Both are immutable properties of an existing tool — you cannot turn
            # an http tool into something else, or switch its auth scheme — so
            # the update model does not accept them at all. Sending the create
            # body verbatim made every redeploy of an existing tool fail while
            # first-time creates succeeded, which is a failure mode that only
            # shows up on the SECOND run.
            #
            # Same class as the agent trap: an export/create body is not a valid
            # update body on this API. If a further field turns out to be
            # forbidden here, add it to _TOOL_UPDATE_STRIP rather than
            # hand-editing at the call site.
            update = {k: v for k, v in body.items() if k not in _TOOL_UPDATE_STRIP}
            auth = {k: v for k, v in (update.get("auth_config") or {}).items()
                    if k not in _TOOL_UPDATE_STRIP_AUTH}
            if auth:
                update["auth_config"] = auth
            updated = self.c.put(f"{TOOL_PATH}/{existing}", json_body=update)
            print(f"Updated tool {name!r} (id={existing})")
            return updated
        created = self.c.post(TOOL_PATH, json_body=body)
        tid = created.get("id") if isinstance(created, dict) else None
        print(f"Created tool {name!r} (id={tid})")
        return created

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
    @staticmethod
    def _sendable(doc: dict) -> dict:
        """Drop `$`-prefixed keys before writing.

        Agent files carry `$comment` to explain non-obvious choices — the whole
        point of files-as-source-of-truth. Alation's request models are strict
        (`extra_forbidden`), so those keys must not travel. `patch_body` already
        filters to _CREATE_FIELDS; this is for the /import fallback, which sends
        the file as-is and 422'd on `$comment`.
        """
        return {k: v for k, v in doc.items() if not k.startswith("$")}

    def import_agent(self, export_doc: dict) -> dict:
        """Create a NEW agent from an export payload. Never use this to update —
        it will clone. Returns {"agent": ..., "warnings": [...]}"""
        result = self.c.post(f"{AGENT_PATH}/import",
                             json_body=self._sendable(export_doc))
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
        # `tool_config_ids` is REQUIRED on create even for a tool-less agent —
        # verified 2026-08-27: omitting it gives
        # 422 {"type":"missing","loc":["body","tool_config_ids"]}. An empty list
        # is the correct value, and resolution above only sets it when `tools` is
        # non-empty, so default it here.
        #
        # CREATE ONLY. On PATCH, sending tool_config_ids=[] would CLEAR an
        # agent's tools — PATCH replaces rather than merges (proven earlier with
        # input_json_schema), so a "harmless" default there would silently strip
        # the tools off a working agent.
        patch_body.setdefault("tool_config_ids", [])

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
            # Print the BODY, not just the status. Reporting only "failed (422)"
            # and then falling back means a second, unrelated error becomes the
            # one the user sees — which is exactly how the $comment failure
            # masked whatever the config path actually objected to.
            print(f"  ! POST {AGENT_PATH} failed ({err.status}): "
                  f"{json.dumps(err.body, default=str)[:600]}")
            print(f"  ! falling back to /import (needs full inline tool defs)")
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
