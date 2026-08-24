"""Canonicalization and the name->uuid lockfile.

Two problems this solves:

1. Agent Studio server-mutates what you send. It injects `x-tool-bindings` and
   `x-original-agent-input` into `input_json_schema`, and a binding with
   source="user" auto-adds that parameter to the schema. So GET != PUT, and a
   naive round-trip produces a diff on every deploy.

2. Array ordering in exports is not guaranteed. `tools` and `parameter_bindings`
   are positionally correlated, so they must be reordered TOGETHER or not at
   all — sorting them independently silently rewires an agent's bindings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SERVER_ANNOTATIONS = ("x-tool-bindings", "x-original-agent-input")


def _strip_annotations(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_annotations(v) for k, v in obj.items() if k not in SERVER_ANNOTATIONS}
    if isinstance(obj, list):
        return [_strip_annotations(v) for v in obj]
    return obj


def canonicalize_agent(export: dict) -> dict:
    """Normalize an AgentExport payload so it is stable and diffable in git."""
    doc = _strip_annotations(json.loads(json.dumps(export)))

    # Alation strips trailing whitespace from `prompt`. Without matching that,
    # a prompt file ending in a newline (as every sane text file does) shows a
    # one-character diff on every single export. Verified against a live export.
    if isinstance(doc.get("prompt"), str):
        doc["prompt"] = doc["prompt"].rstrip()

    tools = doc.get("tools") or []
    bindings = doc.get("parameter_bindings") or []

    # Reorder tools and their positionally-matched bindings as pairs.
    if tools and len(bindings) == len(tools):
        paired = sorted(
            zip(tools, bindings), key=lambda pair: (pair[0].get("name") or "").lower()
        )
        doc["tools"] = [t for t, _ in paired]
        doc["parameter_bindings"] = [b for _, b in paired]
    elif tools:
        # Lengths disagree — the API expects them equal, so flag rather than guess.
        doc["tools"] = sorted(tools, key=lambda t: (t.get("name") or "").lower())
        doc["_warning"] = (
            f"tools ({len(tools)}) and parameter_bindings ({len(bindings)}) "
            "have different lengths; the API expects them equal and positionally matched"
        )

    return doc


def write_json(path: str | Path, doc: Any) -> Path:
    """Write with sorted keys and a trailing newline — stable diffs."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return p


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text())


def llm_identity(row: dict) -> dict:
    """Pull provider / friendly name / model-reference strings out of an LLM row.

    The `GET /config/llm` list and an agent's exported `llm` block do not use the
    same field names, and the list's exact schema is undocumented. So scavenge
    every plausible key instead of hard-coding one, and let callers match on any
    of the collected reference strings.
    """
    provider = row.get("provider") or ""
    name = row.get("name") or row.get("display_name") or row.get("title") or ""

    refs: list[str] = []
    for key in ("default_llm_ref", "llm_ref", "model_name", "model", "model_id", "llm_model_id"):
        val = row.get(key)
        if isinstance(val, str) and val:
            refs.append(val)
    # Anything else that looks like a model identifier.
    for key, val in row.items():
        if (
            isinstance(val, str)
            and val
            and val not in refs
            and key not in ("id", "provider", "name", "display_name", "title")
            and ("model" in key.lower() or key.lower().endswith("_ref"))
        ):
            refs.append(val)

    return {"provider": provider, "name": name, "refs": refs}


class Lockfile:
    """Maps human-readable names to server UUIDs.

    Necessary because custom agents and tools are addressable only by
    server-generated UUID; the name-addressable route accepts only built-ins.
    Commit this file.
    """

    def __init__(self, path: str | Path = ".lockfile.json"):
        self.path = Path(path)
        self.data: dict[str, dict[str, str]] = (
            json.loads(self.path.read_text()) if self.path.exists() else {}
        )

    def get(self, kind: str, name: str) -> str | None:
        return self.data.get(kind, {}).get(name)

    def set(self, kind: str, name: str, uuid: str) -> None:
        self.data.setdefault(kind, {})[name] = uuid
        self.save()

    def forget(self, kind: str, name: str) -> None:
        self.data.get(kind, {}).pop(name, None)
        self.save()

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2, sort_keys=True) + "\n")
