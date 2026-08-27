"""Deployment state: what this kit created, in a customer's catalog.

The agent lockfile maps a name to a UUID so deploy can find an agent again. This
is different and higher-stakes: it is the record of every object we *created*,
so teardown can remove exactly those and nothing else.

**Teardown deletes by recorded ID, never by name.** A teardown that matched on
name could remove a same-named policy the customer already had — the worst bug
this project could ship. If an object is not in the state file, we did not create
it, and we do not touch it.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

DEFAULT_PATH = ".deployment-state.json"


@dataclass
class Record:
    kind: str          # policy_group | policy | standard | cde | dq_monitor
    ref: str           # our stable reference from the source file
    id: str            # the id the instance assigned
    name: str          # as created, including any namespace prefix
    created_at: str
    extra: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {"kind": self.kind, "ref": self.ref, "id": self.id,
                "name": self.name, "created_at": self.created_at, **self.extra}


class DeploymentState:
    """Append-only within a run; keyed by (kind, ref) so apply is idempotent."""

    def __init__(self, path: str | Path = DEFAULT_PATH, instance: str = ""):
        self.path = Path(path)
        raw = json.loads(self.path.read_text()) if self.path.exists() else {}
        self.instance: str = raw.get("instance") or instance
        self.prefix: str = raw.get("namespace_prefix", "")
        self.objects: dict[str, dict] = raw.get("objects", {})

        if instance and self.instance and instance != self.instance:
            raise RuntimeError(
                f"State file {self.path} records deployments to {self.instance!r}, "
                f"but you are targeting {instance!r}. Use a separate state file per "
                f"instance — mixing them would let teardown delete IDs that belong "
                f"to a different catalog."
            )
        self.instance = self.instance or instance

    # -- lookup ------------------------------------------------------------
    @staticmethod
    def key(kind: str, ref: str) -> str:
        return f"{kind}:{ref}"

    def get(self, kind: str, ref: str) -> dict | None:
        return self.objects.get(self.key(kind, ref))

    def id_for(self, kind: str, ref: str) -> str | None:
        rec = self.get(kind, ref)
        return rec.get("id") if rec else None

    def of_kind(self, kind: str) -> Iterator[dict]:
        for rec in self.objects.values():
            if rec.get("kind") == kind:
                yield rec

    def __len__(self) -> int:
        return len(self.objects)

    # -- write -------------------------------------------------------------
    def record(self, kind: str, ref: str, obj_id: str, name: str, **extra) -> None:
        self.objects[self.key(kind, ref)] = Record(
            kind=kind, ref=ref, id=str(obj_id), name=name,
            created_at=datetime.now(timezone.utc).isoformat(),
            extra=extra,
        ).as_dict()
        self.save()

    def forget(self, kind: str, ref: str) -> None:
        self.objects.pop(self.key(kind, ref), None)
        self.save()

    def set_prefix(self, prefix: str) -> None:
        self.prefix = prefix
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps({
            "instance": self.instance,
            "namespace_prefix": self.prefix,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "objects": self.objects,
        }, indent=2, sort_keys=True) + "\n")
        os.replace(tmp, self.path)   # atomic: never leave a half-written state file

    # -- teardown ordering -------------------------------------------------
    def teardown_order(self, order: list[str]) -> list[dict]:
        """Records in reverse dependency order, so dependents go before their
        dependencies. Anything of an unlisted kind is deleted first, on the
        assumption that an unknown object is a leaf."""
        rank = {k: i for i, k in enumerate(order)}
        return sorted(
            self.objects.values(),
            key=lambda r: -rank.get(r.get("kind", ""), len(order)),
        )
