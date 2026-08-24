"""Prompt loading and rendering.

Prompts live as plain Markdown, never inside YAML. A YAML block scalar is
indentation-scoped, so one structural edit re-indents the whole body and you
lose word-level diffs and GitHub suggested-edits. Metadata goes in a sidecar
`.meta.yaml`.

    prompts/foo.md            <- the prompt body
    prompts/foo.meta.yaml     <- model, params, target agent, changelog

StrictUndefined is deliberate: a typo'd variable should fail loudly at render
time, not quietly ship an empty string to the model.
"""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, StrictUndefined

PROMPTS_DIR = Path("prompts")

_env = Environment(undefined=StrictUndefined, keep_trailing_newline=True, autoescape=False)


@dataclass
class Prompt:
    name: str
    body: str
    meta: dict[str, Any] = field(default_factory=dict)
    path: Path | None = None

    def render(self, **vars_: Any) -> str:
        return _env.from_string(self.body).render(**vars_)

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.body.encode("utf-8")).hexdigest()[:12]

    def git_sha(self) -> str:
        """Short git SHA of the last commit touching this prompt file.
        Record it alongside any output so behavior is always attributable."""
        if not self.path:
            return "unknown"
        try:
            out = subprocess.run(
                ["git", "log", "-1", "--format=%h", "--", str(self.path)],
                capture_output=True, text=True, check=False, timeout=10,
            )
            return out.stdout.strip() or "uncommitted"
        except (OSError, subprocess.SubprocessError):
            return "unknown"


def load_prompt(name: str, prompts_dir: Path | str = PROMPTS_DIR) -> Prompt:
    d = Path(prompts_dir)
    body_path = d / f"{name}.md"
    if not body_path.exists():
        raise FileNotFoundError(f"No prompt at {body_path}")
    meta_path = d / f"{name}.meta.yaml"
    meta = yaml.safe_load(meta_path.read_text()) if meta_path.exists() else {}
    return Prompt(
        name=name,
        body=body_path.read_text(encoding="utf-8"),
        meta=meta or {},
        path=body_path,
    )


def list_prompts(prompts_dir: Path | str = PROMPTS_DIR) -> list[str]:
    return sorted(p.stem for p in Path(prompts_dir).glob("*.md"))


def sync_prompt_into_agent(agent_doc: dict, prompt: Prompt, **render_vars: Any) -> dict:
    """Render a prompt file into an agent export doc's `prompt` field.

    This is the seam between the repo (source of truth) and Alation (which
    stores a rendered blob and has no prompt versioning of its own).

    Only DEPLOY-TIME variables are rendered — those declared under
    `deploy_variables` in the sidecar meta file, overridable by kwargs. Runtime
    inputs (the user's message, per-run parameters) must NOT appear as template
    variables in the prompt body: Agent Studio has no templating, so anything
    left unrendered ships to the model as literal `{{ ... }}` text.
    """
    doc = dict(agent_doc)
    declared = prompt.meta.get("deploy_variables") or {}
    if not isinstance(declared, dict):
        raise TypeError(
            f"{prompt.name}: meta 'deploy_variables' must be a mapping, got {type(declared).__name__}"
        )
    doc["prompt"] = prompt.render(**{**declared, **render_vars})
    return doc
