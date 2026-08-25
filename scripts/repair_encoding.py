#!/usr/bin/env python3
"""Repair mojibake in captured run files.

Streams captured before the encoding fix were decoded as ISO-8859-1, so every
multi-byte character is double-encoded: "¶" appears as "Â¶", "—" as "â\x80\x94".
That is losslessly reversible — re-encode as latin-1, decode as UTF-8.

    python3 scripts/repair_encoding.py --check docs/runs/**/*.md
    python3 scripts/repair_encoding.py docs/runs/v0.5.0/*.md

Only rewrites a file if the round trip succeeds and demonstrably reduces
mojibake, so it is safe to run twice.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKERS = ("Â¶", "â\x80\x94", "â\x80\x93", "â\x80\x99", "â\x80\x9c", "â\x80\x9d", "Â ")


def count_mojibake(text: str) -> int:
    return sum(text.count(m) for m in MARKERS)


def repair(text: str) -> str | None:
    """latin-1 -> utf-8 round trip, or None if it isn't applicable."""
    try:
        fixed = text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None
    return fixed if count_mojibake(fixed) < count_mojibake(text) else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Repair double-encoded run files")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--check", action="store_true", help="Report only, change nothing")
    args = ap.parse_args()

    total_bad = repaired = clean = 0
    for name in args.files:
        p = Path(name)
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        bad = count_mojibake(text)
        if not bad:
            clean += 1
            continue
        total_bad += bad
        fixed = repair(text)
        if fixed is None:
            print(f"  {p}: {bad} markers — NOT cleanly repairable, left alone")
            continue
        if args.check:
            print(f"  {p}: {bad} markers -> {count_mojibake(fixed)} after repair")
        else:
            p.write_text(fixed, encoding="utf-8")
            print(f"  {p}: repaired {bad} markers")
        repaired += 1

    verb = "would repair" if args.check else "repaired"
    print(f"\n{clean} already clean, {verb} {repaired} file(s), "
          f"{total_bad} mojibake markers total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
