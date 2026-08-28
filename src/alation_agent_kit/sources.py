"""Where the regulation text comes from.

One interface, two backends, so the pipeline does not care which is in use:

  * `FileSource` — a text file on disk. Verified, fast, free, deterministic.
    This is the prompt-iteration path and it stays the default.
  * `UnstructuredSource` — `get_asset_content` against an Alation Unstructured
    Data Collection, returning the processed markdown Alation extracted from the
    PDF. **UNVERIFIED**: the feature is flagged off on our instance and the tool
    is `ALATION_INTERNAL`, so this code has never executed against a live
    collection. It is written to the documented contract and marked accordingly.

Why an abstraction rather than just swapping the input later: the interesting
output of this pipeline is a *gap analysis traceable to a document version*. That
requires provenance travelling alongside the text — which document, retrieved
when, and a hash so two registers can be compared honestly. Bolting provenance
on afterwards means every artifact produced before then is unattributable.

Design note on where retrieval eventually lives. The target runtime is an Agent
Studio Flow, where an agent holds `get_asset_content` and reads the regulation
itself. That does not make this module redundant: a Flow cannot be iterated on
(30-60s per PDF retrieval, no caching, ACU per call, nondeterministic), so the
kit remains the harness that develops and tests the prompts the Flow will run.
Same prompt, two runtimes.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .client import AlationClient

# Alation caps get_asset_content at 1MB of markdown and sets a `truncated` flag.
# BCBS 239 is ~120KB, so this is generous — but a bank's internal policy pack
# will not be, and silently analysing 1MB of a 3MB document would be the worst
# possible failure: a confident gap analysis of a fragment.
CONTENT_CAP_BYTES = 1_000_000


@dataclass
class Regulation:
    """Regulation text plus enough provenance to attribute a finding to it."""

    text: str
    source_type: str
    locator: str
    retrieved_at: str
    sha256: str
    truncated: bool = False
    extra: dict = field(default_factory=dict)

    @property
    def provenance(self) -> dict:
        """Embedded in run manifests so a register can be traced to its input."""
        return {
            "source_type": self.source_type,
            "locator": self.locator,
            "retrieved_at": self.retrieved_at,
            "sha256": self.sha256,
            "chars": len(self.text),
            "truncated": self.truncated,
            **self.extra,
        }


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class RegulationSource:
    """Base interface. `fetch()` must be side-effect free."""

    source_type = "abstract"

    def fetch(self) -> Regulation:  # pragma: no cover - interface
        raise NotImplementedError

    def describe(self) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class FileSource(RegulationSource):
    """Text extracted ahead of time (scripts/extract_bcbs239.py)."""

    source_type = "file"

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def describe(self) -> str:
        return f"file:{self.path}"

    def fetch(self) -> Regulation:
        if not self.path.is_file():
            raise FileNotFoundError(
                f"{self.path} not found. Extract it first:\n"
                f"    python3 scripts/extract_bcbs239.py artifacts/bcbs239.pdf"
            )
        text = self.path.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError(f"{self.path} is empty")
        return Regulation(
            text=text,
            source_type=self.source_type,
            locator=str(self.path),
            retrieved_at=_now(),
            sha256=_digest(text),
        )


class UnstructuredSource(RegulationSource):
    """`get_asset_content` against an Unstructured Data Collection.

    **NOT VERIFIED AGAINST A LIVE INSTANCE.** Prerequisites, none of which this
    kit can satisfy (see `preflight`):

      1. `alation.feature_flags.enable_unstructured_data` = true, plus
         `unstructured_data_source,unstructured_data_file` appended to
         `DEV_otype_service_enabled_otypes`. Needs SSH or the Cloud console.
      2. `get_asset_content_tool` visibility raised from `ALATION_INTERNAL`,
         which uses a non-public admin API authenticated by browser session
         cookies — an OAuth client cannot do it.
      3. The PDF landed in S3/SharePoint/Confluence, an unstructured OCF
         connector harvested it, and it is indexed as `unstructured_data_file`.

    Route 1 and 2 through an FDE together; discovered serially they cost two
    round trips.

    Object ids here are **UUIDs**, not integers — `get_object_fields` fails on
    them by design, so do not try to resolve one that way.
    """

    source_type = "unstructured_collection"

    # Documented tool parameters. Kept as constants so a rename shows up in one
    # place rather than being buried in a request body.
    ASSET_TYPE = "unstructured_data_file"

    def __init__(self, client: AlationClient, object_id: str,
                 asset_type_name: str | None = None, timeout: int = 180):
        self.c = client
        self.object_id = object_id
        self.asset_type_name = asset_type_name or self.ASSET_TYPE
        # PDFs go through AWS Textract on a cold path: ~1s warm, ~14s cold pod,
        # 30-60s for a PDF. Alation's own tool timeout is 120s; allow headroom.
        self.timeout = timeout

    def describe(self) -> str:
        return f"unstructured:{self.asset_type_name}/{self.object_id}"

    def fetch(self) -> Regulation:
        text, raw = self._call_tool()
        truncated = bool(raw.get("truncated")) or len(text.encode()) >= CONTENT_CAP_BYTES
        if truncated:
            # Loud, not a footnote. A gap analysis over a truncated regulation
            # reports absent requirements that are merely unread.
            raise ValueError(
                f"get_asset_content returned TRUNCATED content for "
                f"{self.object_id} ({len(text):,} chars, cap is "
                f"{CONTENT_CAP_BYTES:,} bytes). Analysing it would produce false "
                f"gaps — requirements that were never read look absent. Split the "
                f"document, or pass --allow-truncated if you accept that."
            )
        if not text.strip():
            raise ValueError(
                f"get_asset_content returned no content for {self.object_id}. "
                f"Check the file is indexed as {self.asset_type_name!r} and that "
                f"extraction completed."
            )
        return Regulation(
            text=text,
            source_type=self.source_type,
            locator=self.describe(),
            retrieved_at=_now(),
            sha256=_digest(text),
            truncated=False,
            extra={"object_id": self.object_id,
                   "asset_type_name": self.asset_type_name},
        )

    def _call_tool(self) -> tuple[str, dict]:
        """Invoke the tool through the AI API.

        The exact invocation path is the unverified part. Alation exposes
        `get_asset_content` as a *tool* to agents, so the reliable route from
        outside is an agent that holds it. Rather than guess a direct
        tool-invocation endpoint and have it 404 in a customer environment, this
        refuses clearly and names the two supported routes.
        """
        raise NotImplementedError(
            "UnstructuredSource is a placeholder until the feature is enabled.\n"
            "\n"
            "get_asset_content is exposed to AGENTS, not as a standalone REST\n"
            "endpoint we have verified, so there are two real routes:\n"
            "  1. Give an agent the tool and invoke that agent (this is also the\n"
            "     Agent Studio Flow design), then read its output; or\n"
            "  2. Confirm a direct tool-invocation endpoint exists on the\n"
            "     instance and implement it here.\n"
            "\n"
            "Guessing a path is how this project lost time twice already. Until\n"
            "one of the two is verified, use --source file.\n"
            f"Requested: {self.describe()}"
        )


def build_source(kind: str, *, path: str | Path | None = None,
                 client: AlationClient | None = None,
                 object_id: str | None = None,
                 asset_type_name: str | None = None) -> RegulationSource:
    """Resolve a `--source` choice into a source object."""
    if kind == "file":
        if not path:
            raise ValueError("--source file requires --input-file")
        return FileSource(path)
    if kind == "unstructured":
        if not (client and object_id):
            raise ValueError(
                "--source unstructured requires --object-id (a UUID) and "
                "working credentials")
        return UnstructuredSource(client, object_id, asset_type_name)
    raise ValueError(f"unknown source {kind!r}")
