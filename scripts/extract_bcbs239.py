#!/usr/bin/env python3
"""Split BCBS 239 into per-principle text chunks.

Why chunk: Agent Studio has no PDF ingestion, so text is passed in as an input
parameter, and a 413 ("payload exceeds the model's context window") is a real
risk for the whole document. BCBS 239's 14 principles are the natural boundary
and give you 14 small, independently reviewable runs.

Usage:
    python scripts/extract_bcbs239.py --download
    python scripts/extract_bcbs239.py --pdf artifacts/bcbs239.pdf

Output:
    artifacts/bcbs239/principle_01.txt … principle_14.txt
    artifacts/bcbs239/index.json      (principle -> file, section, paragraphs)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
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
    (11, "Distribution", "III. Risk reporting practices", (72, 74), "bank"),
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
        sys.exit("pypdf is required: pip install pypdf")
    reader = PdfReader(str(pdf_path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


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
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    if args.download or not pdf_path.exists():
        download(pdf_path)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    text = pdf_to_text(pdf_path)
    (out_dir / "full.txt").write_text(text, encoding="utf-8")
    paras = split_by_paragraph_numbers(text)
    print(f"Parsed {len(paras)} of 89 numbered paragraphs")

    index = []
    for num, name, section, (start, end), audience in PRINCIPLES:
        chunk_paras = [(n, paras[n]) for n in range(start, end + 1) if n in paras]
        body = "\n\n".join(f"{n}. {t}" for n, t in chunk_paras)
        header = (
            f"BCBS 239 — Principle {num}: {name}\n"
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
        "BCBS 239 — Principles for effective risk data aggregation and risk reporting",
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
    print(f"Wrote bank_principles.txt — P1-P11 combined, {len(bank_text):,} chars "
          f"(~{len(bank_text)//4:,} tokens)")
    print("\nNext:")
    print("  CDE identification (send all bank principles at once):")
    print("    ./run.sh run bcbs239_cde_advisor --input-file artifacts/bcbs239/bank_principles.txt -o artifacts/cdes.json")
    print("  Per-principle governance mapping (one principle at a time):")
    print("    ./run.sh run bcbs239_interpreter --input-file artifacts/bcbs239/principle_03.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
