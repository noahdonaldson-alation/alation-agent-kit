#!/usr/bin/env python3
"""Report the structure of a captured SSE stream so the parser can be written
against the real schema instead of a guess.

    ./run.sh run <agent> --input-file X --raw -o artifacts/probe.md
    python3 scripts/inspect_stream.py artifacts/probe.md.raw-stream.txt

Prints: event count, top-level key shapes, how many message ids appear, whether
content accumulates or arrives as deltas, and a preview of each distinct message.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def events(path: Path):
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("data:"):
            continue
        body = line[5:].strip()
        if not body or body == "[DONE]":
            continue
        try:
            yield json.loads(body)
        except json.JSONDecodeError:
            yield {"__unparsed__": body[:200]}


def parts_of(ev: dict) -> list[str]:
    out = []
    for key in ("model_message", "message", "user_message"):
        block = ev.get(key)
        if isinstance(block, dict):
            for p in block.get("parts") or []:
                if isinstance(p, dict) and isinstance(p.get("content"), str):
                    out.append(p["content"])
                elif isinstance(p, str):
                    out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Describe a captured SSE stream")
    ap.add_argument("path")
    ap.add_argument("--preview", type=int, default=140)
    args = ap.parse_args()

    evs = list(events(Path(args.path)))
    print(f"events: {len(evs)}\n")

    print("top-level key sets:")
    for keys, count in Counter(tuple(sorted(e.keys())) for e in evs).most_common():
        print(f"  {count:>5} x  {', '.join(keys)}")

    # Which message-ish blocks exist, and do they carry a role/type marker?
    blocks = Counter()
    markers = defaultdict(Counter)
    for e in evs:
        for k, v in e.items():
            if isinstance(v, dict) and "parts" in v:
                blocks[k] += 1
                for mk in ("role", "type", "author", "sender", "is_user"):
                    if mk in v:
                        markers[k][f"{mk}={v[mk]!r}"] += 1
    print(f"\nblocks containing 'parts': {dict(blocks) or 'none'}")
    for b, m in markers.items():
        print(f"  {b} markers: {dict(m)}")
    if not markers:
        print("  (no role/type marker found — group by message id instead)")

    # Group by message id: each distinct id is a separate message in the chat.
    by_id: dict[str, list[str]] = defaultdict(list)
    order: list[str] = []
    for e in evs:
        mid = str(e.get("id") or e.get("message_id") or "?")
        if mid not in by_id:
            order.append(mid)
        by_id[mid].extend(parts_of(e))

    print(f"\ndistinct message ids: {len(order)}")
    for i, mid in enumerate(order):
        chunks = by_id[mid]
        joined = "".join(chunks)
        longest = max(chunks, key=len) if chunks else ""
        # cumulative if each chunk extends the previous
        cumulative = sum(
            1 for a, b in zip(chunks, chunks[1:]) if len(b) > len(a) and b.startswith(a)
        )
        style = (
            "CUMULATIVE (each event resends the whole message)"
            if chunks and cumulative >= len(chunks) - 2
            else "DELTAS (concatenate)"
        )
        print(f"\n  [{i}] id={mid[:8]}  chunks={len(chunks)}  "
              f"joined={len(joined):,}  longest={len(longest):,}")
        print(f"      style: {style}")
        print(f"      starts: {longest[:args.preview]!r}")

    print("\n--- suggested extraction ---")
    if len(order) > 1:
        print(f"  {len(order)} messages: the first is almost certainly the echoed input.")
        print("  Take the LAST message id and, per the style above, either use its")
        print("  longest chunk (cumulative) or concatenate its chunks (deltas).")
    else:
        print("  single message — use the style reported above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
