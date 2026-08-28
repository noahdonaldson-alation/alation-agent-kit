"""One command for the whole assessment: regulation in, gap analysis out.

    source -> interpret -> validate -> map -> validate -> manifest

The stages already existed as separate CLI calls. Collecting them here buys
three things that mattered once we started making claims about results:

  * **Provenance.** A run manifest records which document (hash included), which
    prompt versions, which agent ids, and how long each stage took. Without it,
    `pde-mapping-postsql-01.json` is a file with no attribution — we could not
    prove which register produced it.
  * **A fail-fast gate.** The register is validated BEFORE spending ACU on the
    mapper. The mapper costs ~5-6 ACU per run; feeding it a malformed register
    burns that for nothing.
  * **Re-runnability.** "Assess the current policy for gaps" becomes one
    command, so it can be scheduled or handed to someone who did not build it.

This is the dev/iteration runtime. The eventual production runtime is an Agent
Studio Flow — see docs/pipeline-and-unstructured.md for why both exist and what
has to be true for the Flow to carry the same chain.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .agents import AgentStudio
from .invoke import run_agent_stream
from .prompts import load_prompt
from .sources import Regulation, RegulationSource
from .store import extract_json

# Alation truncates tool results near 10k chars. The register is ~56KB, so a
# Flow that passes it as a TOOL RESULT would silently lose most of it. Checked
# explicitly rather than trusted, because silent truncation here would look like
# a model that forgot most of the regulation.
TOOL_RESULT_CAP_CHARS = 10_000


@dataclass
class Stage:
    name: str
    ok: bool
    detail: str
    seconds: float = 0.0
    output: Path | None = None
    problems: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        mark = "OK  " if self.ok else "FAIL"
        line = f"  [{mark}] {self.name} ({self.seconds:.1f}s) {self.detail}"
        for p in self.problems[:6]:
            line += f"\n         ! {p}"
        if len(self.problems) > 6:
            line += f"\n         ! ... and {len(self.problems) - 6} more"
        return line


class Pipeline:
    def __init__(self, studio: AgentStudio, outdir: Path,
                 interpreter: str = "bcbs239_cde_dq_interpreter",
                 mapper: str = "bcbs239_pde_mapper",
                 log: Callable[[str], None] = print):
        self.st = studio
        self.outdir = Path(outdir)
        self.interpreter = interpreter
        self.mapper = mapper
        self.log = log
        self.stages: list[Stage] = []

    # -- helpers -----------------------------------------------------------
    def _validate(self, doc: Any, kind: str) -> list[str]:
        """Reuse the same structural checks the standalone validator applies.

        Imported lazily and by path because the checks live in scripts/, which
        is not an installed package — duplicating them here is how the two
        copies would drift.
        """
        import importlib.util

        spec_path = Path(__file__).resolve().parents[2] / "scripts" / "validate_output.py"
        if not spec_path.is_file():
            return [f"validator not found at {spec_path}; structural checks skipped"]
        spec = importlib.util.spec_from_file_location("_validate_output", spec_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        try:
            return list(mod.structural_checks(doc))
        except Exception as exc:  # noqa: BLE001
            return [f"validator raised: {exc}"]

    def _run_agent(self, name: str, message: str, out: Path) -> tuple[dict | None, str]:
        agent_id = self.st.resolve_agent_id(name) or name
        text = run_agent_stream(self.st.c, agent_id, {"message": message})
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        return extract_json(text), agent_id

    # -- stages ------------------------------------------------------------
    def fetch(self, source: RegulationSource) -> Regulation | None:
        t0 = time.time()
        try:
            reg = source.fetch()
        except Exception as exc:  # noqa: BLE001
            self.stages.append(Stage("fetch regulation", False, str(exc)[:400],
                                     time.time() - t0))
            return None
        self.stages.append(Stage(
            "fetch regulation", True,
            f"{source.describe()} — {len(reg.text):,} chars, sha={reg.sha256}",
            time.time() - t0))
        return reg

    def interpret(self, reg: Regulation, tag: str) -> dict | None:
        t0 = time.time()
        out = self.outdir / f"register-{tag}.json"
        try:
            doc, agent_id = self._run_agent(self.interpreter, reg.text, out)
        except Exception as exc:  # noqa: BLE001
            self.stages.append(Stage("interpret regulation", False,
                                     str(exc)[:300], time.time() - t0))
            return None
        if doc is None:
            self.stages.append(Stage(
                "interpret regulation", False,
                f"no JSON object in the response (raw kept at {out})",
                time.time() - t0, out))
            return None
        problems = self._validate(doc, "register")
        n = len(doc.get("cde_candidates") or [])
        self.stages.append(Stage(
            "interpret regulation", not problems,
            f"{n} CDE candidate(s) -> {out}",
            time.time() - t0, out, problems))
        return doc

    def map_gaps(self, register: dict, tag: str) -> dict | None:
        t0 = time.time()
        out = self.outdir / f"mapping-{tag}.json"
        payload = json.dumps(register, separators=(",", ":"))
        if len(payload) > TOOL_RESULT_CAP_CHARS:
            # Not fatal here: the kit passes the register as the message, which
            # has no such cap. It IS fatal for a Flow that passes it as a tool
            # result, so say so once, loudly, where someone will see it.
            self.log(f"  note: register is {len(payload):,} chars, "
                     f"{len(payload) / TOOL_RESULT_CAP_CHARS:.1f}x the ~"
                     f"{TOOL_RESULT_CAP_CHARS:,}-char tool-result cap. Fine as a "
                     f"message; would truncate as a Flow tool result.")
        try:
            doc, agent_id = self._run_agent(self.mapper, payload, out)
        except Exception as exc:  # noqa: BLE001
            self.stages.append(Stage("map gaps", False, str(exc)[:300],
                                     time.time() - t0))
            return None
        if doc is None:
            self.stages.append(Stage(
                "map gaps", False, f"no JSON object in the response (raw at {out})",
                time.time() - t0, out))
            return None
        problems = self._validate(doc, "mapping")
        cov = doc.get("coverage_summary") or {}
        detail = ("  ".join(f"{k}={cov.get(k, 0)}" for k in
                            ("mapped", "partial", "not_found", "already_exists"))
                  + f"  -> {out}")
        self.stages.append(Stage("map gaps", not problems, detail,
                                 time.time() - t0, out, problems))
        return doc

    # -- orchestration -----------------------------------------------------
    def run(self, source: RegulationSource, tag: str | None = None,
            stop_after: str | None = None) -> dict:
        tag = tag or time.strftime("%Y%m%d-%H%M%S")
        manifest: dict[str, Any] = {
            "tag": tag,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "instance": self.st.c.s.base_url,
        }

        reg = self.fetch(source)
        if reg is None:
            return self._finish(manifest, tag)
        manifest["regulation"] = reg.provenance

        # Prompt provenance: which prompt text actually ran. A sha here is what
        # lets a result be reproduced, or blamed on a specific revision.
        manifest["prompts"] = {}
        for label, name in (("interpreter", self.interpreter),
                            ("mapper", self.mapper)):
            try:
                p = load_prompt(name)
                manifest["prompts"][label] = {
                    "name": name, "sha256": p.sha256, "git": p.git_sha()}
            except Exception:  # noqa: BLE001 - provenance is best-effort
                manifest["prompts"][label] = {"name": name, "sha256": None}

        if stop_after == "fetch":
            return self._finish(manifest, tag)

        register = self.interpret(reg, tag)
        if register is None:
            return self._finish(manifest, tag)
        # Fail closed: a malformed register would waste the mapper's ACU.
        if not self.stages[-1].ok:
            self.log("\n  Stopping before the mapper: the register has structural "
                     "problems, and the mapper costs ~5-6 ACU per run.")
            return self._finish(manifest, tag)
        manifest["register"] = {
            "cde_count": len(register.get("cde_candidates") or []),
            "file": str(self.stages[-1].output),
        }

        if stop_after == "interpret":
            return self._finish(manifest, tag)

        mapping = self.map_gaps(register, tag)
        if mapping is not None:
            manifest["mapping"] = {
                "coverage_summary": mapping.get("coverage_summary"),
                "file": str(self.stages[-1].output),
            }
        return self._finish(manifest, tag)

    def _finish(self, manifest: dict, tag: str) -> dict:
        manifest["stages"] = [
            {"name": s.name, "ok": s.ok, "seconds": round(s.seconds, 1),
             "detail": s.detail, "problems": s.problems,
             "output": str(s.output) if s.output else None}
            for s in self.stages
        ]
        manifest["ok"] = all(s.ok for s in self.stages)
        path = self.outdir / f"manifest-{tag}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        manifest["manifest_file"] = str(path)
        return manifest
