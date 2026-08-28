#!/usr/bin/env python3
"""Split BCBS 239 into per-principle text chunks, repairing PDF extraction damage.

Why chunk: Agent Studio has no PDF ingestion, so text is passed in as an input
parameter, and a 413 ("payload exceeds the model's context window") is a real
risk for the whole document. BCBS 239's 14 principles are the natural boundary
and give you 14 small, independently reviewable runs.

Why NORMALISE (added 2026-08-28): the downstream agents are required to quote the
regulation verbatim, and those quotations are written into business policies that
a customer reads in Alation. pypdf's output carries kerning damage — `risk m
anagement`, `in- house`, `data -related` — plus curly quotes and en/em dashes. Two
consequences, both bad:

  1. A demo whose whole claim is "cited to the regulation" shows a customer a
     policy quoting "risk m anagement".
  2. A model asked for a verbatim quote will silently tidy the spacing, so the
     quote no longer matches the text it came from and the citation-provenance
     audit in authoring.py weakens to nothing.

Normalisation here is REPAIR, not rewriting: every transform moves the text
closer to what the PDF actually says. The intra-word repair uses the document as
its own dictionary — two adjacent tokens are joined only when the joined form
already appears elsewhere in the document as a real word and at least one of the
fragments does not. That rule cannot invent a word that is not already in the
source. `full.raw.txt` keeps the unrepaired extraction so every change is
auditable, and `normalisation-report.json` records exactly what moved.

Usage:
    python scripts/extract_bcbs239.py --download
    python scripts/extract_bcbs239.py --pdf artifacts/bcbs239.pdf
    python scripts/extract_bcbs239.py --no-normalise      # reproduce pre-2026-08-28 output

Output:
    artifacts/bcbs239/principle_01.txt … principle_14.txt
    artifacts/bcbs239/bank_principles.txt      (P1-P11 combined; the agent input)
    artifacts/bcbs239/full.txt                 (normalised)
    artifacts/bcbs239/full.raw.txt             (as pypdf produced it)
    artifacts/bcbs239/index.json               (principle -> file, section, paragraphs)
    artifacts/bcbs239/normalisation-report.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

SOURCE_URL = "https://www.bis.org/publ/bcbs239.pdf"
OUT_DIR = Path("artifacts/bcbs239")

# Verified structure of BCBS 239 (Jan 2013, never amended).
# Paragraph numbers are the stable citation unit — page numbers shift between
# reprints, paragraph numbers do not.
PRINCIPLES = [
    (1, "Governance", "I. Overarching governance and infrastructure", (27, 31), "bank"),
    (2, "Data architecture and IT infrastructure", "I. Overarching governance and infrastructure", (32, 35), "bank"),
    (3, "Accuracy and Integrity", "II. Risk data aggregation capabilities", (36, 40), "bank"),
    (4, "Completeness", "II. Risk data aggregation capabilities", (41, 43), "bank"),
    (5, "Timeliness", "II. Risk data aggregation capabilities", (44, 47), "bank"),
    (6, "Adaptability", "II. Risk data aggregation capabilities", (48, 51), "bank"),
    (7, "Accuracy", "III. Risk reporting practices", (52, 56), "bank"),
    (8, "Comprehensiveness", "III. Risk reporting practices", (57, 60), "bank"),
    (9, "Clarity and usefulness", "III. Risk reporting practices", (61, 69), "bank"),
    (10, "Frequency", "III. Risk reporting practices", (70, 71), "bank"),
    # 72-73, NOT 72-74. Corrected 2026-08-28. Paragraph 74 is the preamble to
    # Section IV (supervisory review), not part of Principle 11 — and because the
    # "Principle 12 / Review - Supervisors should ..." heading block sits between
    # 74 and 75 with no leading paragraph number, the splitter swallowed it into
    # 74's body. So bank_principles.txt ended with supervisor-facing text while
    # its own header line claimed principles 12-14 were excluded, and both
    # interpreter prompts had to exclude 12-14 by judgement rather than by
    # absence. Cutting at 73 removes the preamble and the leaked heading together.
    (11, "Distribution", "III. Risk reporting practices", (72, 73), "bank"),
    (12, "Review", "IV. Supervisory review, tools and cooperation", (75, 77), "supervisor"),
    (13, "Remedial actions and supervisory measures", "IV. Supervisory review, tools and cooperation", (78, 82), "supervisor"),
    (14, "Home/host cooperation", "IV. Supervisory review, tools and cooperation", (83, 89), "supervisor"),
]

# Alation's honest coverage, from the viability research. Carried into the index
# so the agent's output can be checked against it rather than overclaiming.
ADDRESSABILITY = {
    1: "direct", 2: "direct", 3: "direct", 4: "direct",
    5: "evidence_only", 6: "evidence_only", 7: "evidence_only",
    8: "out_of_scope", 9: "out_of_scope", 10: "out_of_scope", 11: "out_of_scope",
    12: "out_of_scope", 13: "out_of_scope", 14: "out_of_scope",
}


def download(dest: Path) -> Path:
    import urllib.request

    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {SOURCE_URL}")
    urllib.request.urlretrieve(SOURCE_URL, dest)  # noqa: S310 - fixed, known URL
    print(f"Saved {dest} ({dest.stat().st_size:,} bytes)")
    return dest


def pdf_to_text(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit(
            "pypdf is not available to this interpreter.\n\n"
            "It's a dependency of the kit, installed in the venv — you are probably\n"
            "running system python3. Use the venv interpreter instead:\n\n"
            "    uv venv && uv pip install -e \".[dev]\"      # first time only\n"
            "    .venv/bin/python scripts/extract_bcbs239.py --pdf artifacts/bcbs239.pdf\n\n"
            "(no uv? use: python3 -m venv .venv && .venv/bin/pip install -e \".[dev]\")"
        )
    reader = PdfReader(str(pdf_path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


# Characters pypdf emits that have no business in a quotation destined for an
# HTML policy body. policy_author is instructed to write &mdash;/&ndash; entities
# rather than raw non-ASCII, and a verbatim quote carrying a raw U+2014 puts that
# instruction in direct conflict with the requirement to quote exactly. Folding
# the source to ASCII removes the conflict at the root.
UNICODE_FOLD = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"',
    "–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-",
    "…": "...",
    " ": " ", " ": " ", " ": " ", " ": " ", " ": " ",
    "​": "", "­": "",          # zero-width space, soft hyphen
    "•": "-", "·": "-",
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl",
}

# A section header the splitter leaves trailing on the last paragraph of a
# section, e.g. paragraph 73 ending with "IV. Supervisory review, tools and
# cooperation". Harmless to the model but it reads as if the section belongs to
# the principle, so strip it.
SECTION_HEADER = re.compile(r"(?m)^\s*(?:I|II|III|IV|V)\.\s+[A-Z][^\n]{6,}\s*$")


def _fold_unicode(text: str, report: dict) -> str:
    counts: dict[str, int] = {}
    for ch, repl in UNICODE_FOLD.items():
        n = text.count(ch)
        if n:
            counts[f"U+{ord(ch):04X} -> {repl!r}"] = n
            text = text.replace(ch, repl)
    # Anything still non-ASCII is unexpected — surface it rather than dropping it
    # silently, then strip accents as a last resort.
    leftover = Counter(c for c in text if ord(c) > 127)
    if leftover:
        report["unexpected_non_ascii"] = {
            f"U+{ord(c):04X} {unicodedata.name(c, '?')}": n for c, n in leftover.most_common()
        }
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if ord(c) < 128)
    report["unicode_folded"] = counts
    return text


def _repair_hyphen_spacing(text: str, report: dict) -> str:
    """`in- house` -> `in-house`, `data -related` -> `data-related`.

    Both patterns are unambiguous: a hyphen touching one word and separated by a
    single space from the other is kerning damage, never intended typography —
    an intended dash in this document is spaced on both sides ("Review - Supervisors").
    """
    text, n1 = re.subn(r"(?<=\w)- (?=\w)", "-", text)
    text, n2 = re.subn(r"(?<=\w) -(?=\w)", "-", text)
    report["hyphen_space_repaired"] = n1
    report["space_hyphen_repaired"] = n2
    return text


# Words that legitimately precede a number in this document, so a digit after one
# is a cross-reference ("in accordance with paragraph 22"), never a footnote.
NUMBER_CONTEXT = {
    "paragraph", "paragraphs", "principle", "principles", "page", "pages",
    "section", "sections", "annex", "footnote", "chapter", "article", "table",
    "figure", "number", "no", "step", "phase", "tier", "basel",
}


def _strip_footnote_markers(text: str, report: dict) -> str:
    """Remove superscript footnote references that pypdf inlines into the prose.

    BCBS 239 carries footnotes as superscripts; extraction drops them inline, so
    the text reads `A bank should establish integrated 16 data taxonomies` and
    `country credit exposures18 as of a specified date`. A model quoting that
    sentence correctly omits the marker — which then makes its quotation fail a
    verbatim check against our own source file. So the marker breaks provenance
    in the one direction that matters: it makes correct quotations look invented.

    Four shapes, each narrow enough not to eat a real number:
      1. glued to a word      `exposures18`
      2. glued after a period  `expertise.14`
      3. spaced after a comma  `program , 13 and`
      4. standing alone between two lowercase words, where the preceding word is
         not one that legitimately introduces a number (see NUMBER_CONTEXT) —
         this is the only ambiguous case, and in the bank-facing text it matches
         exactly one place. Every removal is recorded in the report.
    """
    removed: list[str] = []

    def note(m, kind):
        ctx = re.sub(r"\s+", " ", text[max(0, m.start() - 45):m.end() + 35])
        removed.append(f"[{kind}] {m.group(0)!r} in ...{ctx}...")

    # 1 + 2: glued to a lowercase word, optionally across a sentence period.
    #        (?!\d) stops it biting the "239" in bcbs239.
    def sub_glued(m):
        note(m, "glued")
        return m.group(1)
    text = re.sub(r"([a-z]\.?)(\d{1,2})(?!\d)(?=\s|$)", sub_glued, text)

    # 3: space-comma-space-digits, e.g. "risk management program , 13 and"
    def sub_comma(m):
        note(m, "after-comma")
        return ", "
    text = re.sub(r"\s+,\s+\d{1,2}\s+(?=[a-z])", sub_comma, text)

    # 4: standalone between two lowercase words.
    #    The lookback is load-bearing: "See, inter alia, Principles 2 and 13 in
    #    the Basel Committee's ..." reaches this rule with "and" as the preceding
    #    word, which is not in NUMBER_CONTEXT — so testing only the immediately
    #    preceding word deleted a real cross-reference. Scan back far enough to
    #    see the noun that governs the enumeration.
    def sub_bare(m):
        if m.group(1).lower() in NUMBER_CONTEXT:
            return m.group(0)
        window = text[max(0, m.start() - 60):m.start()].lower()
        if any(re.search(rf"\b{w}\b", window) for w in NUMBER_CONTEXT):
            return m.group(0)
        note(m, "standalone")
        return f"{m.group(1)} "
    text = re.sub(r"\b([a-z]{3,})\s+\d{1,2}\s+(?=[a-z])", sub_bare, text)

    # The space-before-punctuation left behind by the original superscript.
    text, n = re.subn(r"\s+([,;:.])", r"\1", text)
    report["footnote_markers_removed"] = removed
    report["space_before_punctuation_fixed"] = n
    return text


def _repair_split_words(text: str, report: dict) -> str:
    """Rejoin words pypdf split mid-token, using the document as its own dictionary.

    Join `a b` only when ALL of these hold:
      - they are separated by exactly one space (never a newline — a line-break
        split is a different problem and is reported, not guessed at);
      - the joined form already appears >= 2 times elsewhere in the document, so
        it is demonstrably a real word *in this document*;
      - at least one fragment is not itself a word here (appears <= 1 time), so
        we never fuse two legitimate adjacent words;
      - one of the fragments is short (<= 3 chars), which is the shape kerning
        damage actually takes.

    The rule cannot invent a word that is not already in the source. That is the
    whole point: this is repair, and repair has to be checkable.
    """
    vocab = Counter(w.lower() for w in re.findall(r"[A-Za-z]{2,}", text))
    toks = list(re.finditer(r"[A-Za-z]+", text))
    fixes: list[tuple[int, int, str, str]] = []
    for i in range(len(toks) - 1):
        a, b = toks[i], toks[i + 1]
        if text[a.end():b.start()] != " ":
            continue
        joined = a.group() + b.group()
        if len(joined) < 5:
            continue
        if (vocab[joined.lower()] >= 2
                and (vocab[a.group().lower()] <= 1 or vocab[b.group().lower()] <= 1)
                and (len(a.group()) <= 3 or len(b.group()) <= 3)):
            fixes.append((a.start(), b.end(), joined,
                          f"{a.group()} {b.group()} -> {joined}"))

    for start, end, joined, _ in reversed(fixes):     # right-to-left keeps offsets valid
        text = text[:start] + joined + text[end:]

    report["split_words_rejoined"] = [label for *_, label in fixes]
    # Not repaired, only counted. A hyphen at a line break is ambiguous — it may
    # be a broken word or a genuine compound — and guessing would be the one kind
    # of change this function is designed not to make.
    report["line_break_hyphenations_left_alone"] = len(re.findall(r"\w-\n\w", text))
    return text


def normalise(text: str) -> tuple[str, dict]:
    """Repair PDF extraction damage. Returns (text, report)."""
    report: dict = {}
    text = _fold_unicode(text, report)
    text = _repair_hyphen_spacing(text, report)
    text = _repair_split_words(text, report)
    # After word repair, so `exposures18` is one token by the time we look at it.
    text = _strip_footnote_markers(text, report)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"(?m)[ \t]+$", "", text)
    return text, report


def split_by_paragraph_numbers(text: str) -> dict[int, str]:
    """Map paragraph number -> paragraph text.

    BCBS 239's body is numbered paragraphs 1-89. We match a line-leading integer
    followed by whitespace, which is how the extracted text presents them.
    """
    normalized = re.sub(r"[ \t]+", " ", text)
    matches = list(re.finditer(r"(?m)^\s*(\d{1,2})\.?\s+(?=[A-Z(\"'])", normalized))
    paras: dict[int, str] = {}
    for i, m in enumerate(matches):
        num = int(m.group(1))
        if not 1 <= num <= 89:
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(normalized)
        body = normalized[m.end():end].strip()
        # Keep the longest capture for a given number — headers and the Annex
        # restatements produce short spurious matches.
        if len(body) > len(paras.get(num, "")):
            paras[num] = body
    return paras


def main() -> int:
    ap = argparse.ArgumentParser(description="Split BCBS 239 into per-principle chunks")
    ap.add_argument("--pdf", default="artifacts/bcbs239.pdf")
    ap.add_argument("--download", action="store_true", help="Fetch the PDF from bis.org first")
    ap.add_argument("--out", default=str(OUT_DIR))
    ap.add_argument("--no-normalise", action="store_true",
                    help="Skip PDF-damage repair. Reproduces the pre-2026-08-28 "
                         "output, which is what the 10 committed v0.6.0 "
                         "interpreter runs were produced against.")
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    if args.download or not pdf_path.exists():
        download(pdf_path)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = pdf_to_text(pdf_path)
    (out_dir / "full.raw.txt").write_text(raw, encoding="utf-8")

    if args.no_normalise:
        text, report = raw, {"skipped": True}
        print("Normalisation SKIPPED (--no-normalise). Quotations will carry "
              "PDF extraction damage.")
    else:
        text, report = normalise(raw)
        print("Repaired PDF extraction damage:")
        folded = sum(report.get("unicode_folded", {}).values())
        print(f"  {folded:>3} non-ASCII character(s) folded to ASCII")
        print(f"  {report['hyphen_space_repaired']:>3} 'in- house' hyphen breaks rejoined")
        print(f"  {report['space_hyphen_repaired']:>3} 'data -related' hyphen breaks rejoined")
        rejoined = report["split_words_rejoined"]
        print(f"  {len(rejoined):>3} word(s) split mid-token, rejoined:")
        for label in rejoined:
            print(f"        {label}")
        fn = report["footnote_markers_removed"]
        print(f"  {len(fn):>3} inline footnote marker(s) removed:")
        for label in fn:
            print(f"        {label}")
        if report.get("unexpected_non_ascii"):
            print("  UNEXPECTED non-ASCII (stripped after NFKD — check these):")
            for k, n in report["unexpected_non_ascii"].items():
                print(f"        {n:>3}  {k}")
        left = report["line_break_hyphenations_left_alone"]
        if left:
            print(f"  {left:>3} hyphen(s) at a line break LEFT ALONE — ambiguous "
                  f"between a broken word and a real compound")
        print()

    (out_dir / "full.txt").write_text(text, encoding="utf-8")
    (out_dir / "normalisation-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")

    paras = split_by_paragraph_numbers(text)
    print(f"Parsed {len(paras)} of 89 numbered paragraphs")

    index = []
    for num, name, section, (start, end), audience in PRINCIPLES:
        chunk_paras = [(n, paras[n]) for n in range(start, end + 1) if n in paras]
        # Strip a section header the splitter left trailing on the section's last
        # paragraph — e.g. 73 ending with "IV. Supervisory review, tools and
        # cooperation", which reads as if the section belongs to the principle.
        chunk_paras = [(n, SECTION_HEADER.sub("", t).rstrip()) for n, t in chunk_paras]
        body = "\n\n".join(f"{n}. {t}" for n, t in chunk_paras)
        header = (
            f"BCBS 239 - Principle {num}: {name}\n"
            f"Section: {section}\n"
            f"Paragraphs: {start}-{end}\n"
            f"Audience: {audience}\n"
            f"Source: {SOURCE_URL}\n"
            f"{'-' * 60}\n"
        )
        fname = f"principle_{num:02d}.txt"
        (out_dir / fname).write_text(header + body + "\n", encoding="utf-8")

        index.append({
            "principle_id": f"BCBS239-P{num}",
            "principle_number": num,
            "principle_name": name,
            "section": section,
            "paragraphs": [start, end],
            "paragraphs_found": [n for n, _ in chunk_paras],
            "audience": audience,
            "expected_addressability": ADDRESSABILITY[num],
            "file": fname,
            "chars": len(body),
        })
        flag = "" if chunk_paras else "   <- EMPTY, check the parser"
        print(f"  P{num:>2} {name[:42]:42} {len(body):>6,} chars{flag}")

    (out_dir / "index.json").write_text(json.dumps(index, indent=2) + "\n")

    # Combined bank-facing principles (1-11). This is the input for CDE
    # identification: CDEs are cross-cutting, so the model needs P2/P3/P4/P7 in
    # view at once rather than one principle at a time. Principles 12-14 are
    # addressed to supervisors and are deliberately excluded.
    bank_files = [e for e in index if e["audience"] == "bank"]
    combined = [
        "BCBS 239 - Principles for effective risk data aggregation and risk reporting",
        "Basel Committee on Banking Supervision, January 2013",
        f"Source: {SOURCE_URL}",
        "Bank-facing principles 1-11. Principles 12-14 address supervisors and are excluded.",
        "=" * 70,
        "",
    ]
    for entry in bank_files:
        combined.append((out_dir / entry["file"]).read_text(encoding="utf-8").rstrip())
        combined.append("")
    bank_text = "\n".join(combined) + "\n"
    (out_dir / "bank_principles.txt").write_text(bank_text, encoding="utf-8")

    print(f"\nWrote {len(index)} chunks + index.json to {out_dir}")
    print(f"Wrote bank_principles.txt - P1-P11 combined, {len(bank_text):,} chars "
          f"(~{len(bank_text)//4:,} tokens)")

    # Assert the property the normalisation exists to give us, rather than
    # assuming it. A single stray character here means a quotation somewhere
    # downstream carries it into a customer-visible policy body.
    non_ascii = sorted({c for c in bank_text if ord(c) > 127})
    if non_ascii and not args.no_normalise:
        print("  WARNING: bank_principles.txt still contains non-ASCII: "
              + ", ".join(f"U+{ord(c):04X}" for c in non_ascii))
    elif not args.no_normalise:
        print("  Verified pure ASCII - quotations will round-trip unchanged.")
    leaked = [p for p in PRINCIPLES if p[4] == "supervisor"
              and f"Principle {p[0]} " in bank_text]
    if leaked:
        print("  WARNING: supervisor-facing content leaked into the bank file: "
              + ", ".join(f"P{p[0]}" for p in leaked))

    print("\nNext: interpret it. Two agents read this file, for different steps:")
    print("  prompts/bcbs239_obligation_interpreter.md   obligations -> policies (step 1)")
    print("  prompts/bcbs239_cde_dq_interpreter.md       CDE + DQ register (legacy path)")
    print("\n  ./run.sh run bcbs239_obligation_interpreter \\")
    print("      --input-file artifacts/bcbs239/bank_principles.txt \\")
    print("      -o docs/runs/obl-v0.1.0/run01.json")
    print("\n  Principles 12-14 are excluded - they address supervisors, not banks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
