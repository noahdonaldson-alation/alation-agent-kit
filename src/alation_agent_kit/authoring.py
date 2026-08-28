"""Post-processing and gating for agent-authored policy specs.

Division of labour, per the project convention *agent for judgement that varies,
code for actions that must be exact*:

  * The agent writes policy wording, purposes, scopes and attestation fields —
    judgement, and the reason to use a model at all.
  * This module computes `standard_attachment` (a pure function of the register),
    verifies every citation against the register, and enforces the review gate.

The citation check is the important one, and the reason is subtler than
"models make things up".

Verified 2026-08-27, first live run of policy_author: it produced four
quotations absent from the register, and **all four are verbatim-correct BCBS
239 text**. The model was not hallucinating — it knows this regulation and
quoted it from training knowledge rather than from the document it was handed.

That is a latent failure, not a success. BCBS 239 is famous, so recall happens
to be accurate. A customer's internal policy PDF is not in any training set, so
the same behaviour there yields confident, plausible, invented quotations with
nothing to distinguish them from real ones. The whole reusability goal depends on
this pipeline working over documents the model has never seen.

Hence: the audit does not ask "is this quote true?" — it cannot know that. It
asks "could the agent have read this in the input it was given?" A quote that
fails is reported as **not traceable**, never as fabricated, because the two are
different claims and only the first is one we can actually support.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
from pathlib import Path
from typing import Any

# Quotes get normalised before comparison: the prompt asks for HTML entities and
# the register holds real characters, so a byte comparison would report every
# correct quote as invented.
_ENTITIES = {
    "&mdash;": "—", "&ndash;": "–", "&para;": "¶", "&amp;": "&",
    "&quot;": '"', "&rsquo;": "’", "&lsquo;": "‘",
    "&ldquo;": "“", "&rdquo;": "”", "&nbsp;": " ",
}


def _plain(html: str) -> str:
    text = html or ""
    for ent, char in _ENTITIES.items():
        text = text.replace(ent, char)
    text = re.sub(r"<[^>]+>", " ", text)
    # Straighten quotes and collapse whitespace so formatting differences do not
    # masquerade as content differences.
    text = (text.replace("“", '"').replace("”", '"')
                .replace("’", "'").replace("‘", "'"))
    return " ".join(text.split())


def register_facts(register: dict) -> dict:
    """The citable universe: which paragraphs and quotes the register supports.

    Reads EITHER register shape. The CDE register keys citations under
    `cde_candidates[].driven_by[]`; the obligation register keys them under
    `obligations[].citations[]` and `obligations[].measurable_expectations[]`.
    Both feed the same downstream checks, and teaching this one function both
    shapes is what lets `audit` and `render_for_review` work unchanged on either
    path — the alternative was a second review command, which would have meant
    two places to keep the citation rules correct.
    """
    if register.get("obligations"):
        return _obligation_register_facts(register)

    by_principle: dict[int, set[int]] = {}
    dq_paragraphs: set[int] = set()
    quotes: list[str] = []
    for cde in register.get("cde_candidates") or []:
        for d in cde.get("driven_by") or []:
            p = d.get("principle")
            if isinstance(p, int):
                by_principle.setdefault(p, set()).update(
                    x for x in (d.get("paragraphs") or []) if isinstance(x, int))
            if d.get("quote"):
                quotes.append(_plain(d["quote"]))
        # DQ citations look like "¶36(c)". They name paragraphs the register
        # supports, so harvest them into the permitted set — a policy may
        # legitimately cite a paragraph that reached the register via a DQ
        # requirement rather than via driven_by.
        for r in cde.get("dq_requirements") or []:
            for n in re.findall(r"\d+", str(r.get("citation") or "")):
                dq_paragraphs.add(int(n))
    all_paras = {n for s in by_principle.values() for n in s} | dq_paragraphs
    return {"paragraphs_by_principle": by_principle,
            "all_paragraphs": all_paras,
            "quotes": quotes}


def _obligation_register_facts(register: dict) -> dict:
    """`register_facts` for the obligation register shape.

    One obligation per principle, so `paragraphs_by_principle` is built from the
    obligation's own citations plus the citations on its measurable expectations.
    Cross-cutting quotations go into the quote pool but belong to no single
    principle, so they are added to `all_paragraphs` only — a policy citing a
    paragraph that only reached the register via a cross-cutting entry is
    legitimate, and attributing it to one principle would be a guess.
    """
    by_principle: dict[int, set[int]] = {}
    quotes: list[str] = []
    extra: set[int] = set()

    def take(cit: dict, principle: int | None) -> None:
        if not cit:
            return
        paras = {p for p in (cit.get("paragraphs") or []) if isinstance(p, int)}
        if isinstance(principle, int):
            by_principle.setdefault(principle, set()).update(paras)
        else:
            extra.update(paras)
        if cit.get("quote"):
            quotes.append(_plain(cit["quote"]))

    for o in register.get("obligations") or []:
        principle = o.get("principle")
        for c in o.get("citations") or []:
            take(c, principle)
        for e in o.get("measurable_expectations") or []:
            take(e.get("citation") or {}, principle)

    for x in register.get("cross_cutting") or []:
        take(x.get("citation") or {}, None)

    all_paras = {n for s in by_principle.values() for n in s} | extra
    return {"paragraphs_by_principle": by_principle,
            "all_paragraphs": all_paras,
            "quotes": quotes}


def derive_attachment(spec: dict, register: dict) -> dict:
    """Map principle -> [standard refs], computed, never asked of the model.

    Every bank-facing principle 1-11 gets a key, including empty lists, so the
    absence of a standard for a principle is explicit rather than a missing key
    somebody has to notice.
    """
    pol_by_principle: dict[int, list[str]] = {}
    for pol in spec.get("policies") or []:
        p = (pol.get("derived_from") or {}).get("principle")
        if isinstance(p, int):
            pol_by_principle.setdefault(p, []).append(pol["ref"])

    std_by_policy: dict[str, list[str]] = {}
    for std in spec.get("standards") or []:
        std_by_policy.setdefault(std.get("from_policy"), []).append(std["ref"])

    by_principle: dict[str, list[str]] = {}
    for principle in range(1, 12):
        refs: list[str] = []
        for pol_ref in pol_by_principle.get(principle, []):
            refs.extend(std_by_policy.get(pol_ref, []))
        by_principle[str(principle)] = sorted(set(refs))
    return {
        "$comment": "DERIVED by alation_agent_kit.authoring.derive_attachment "
                    "from each policy's principle. Not model output: it is a "
                    "function of the policies and standards above, and asking a "
                    "model for a derivable value invites a contradiction.",
        "by_principle": by_principle,
    }


def audit(spec: dict, register: dict,
          strict_citations: bool | None = None) -> list[str]:
    """Everything a schema cannot express. Returns problems; empty means clean.

    `strict_citations` controls the provenance checks — that every paragraph and
    quotation traces back to the register. Default: on for agent-authored specs,
    off for hand-authored ones.

    The distinction matters. The agent can only see the register, so a citation
    outside it is by definition unverifiable and probably invented. A human
    author reads the actual regulation, so citing ¶32-35 or quoting ¶36(d) when
    the register only carried ¶33 is correct work, not fabrication. Running the
    strict check against the reviewed bcbs239.json produced nine false failures
    — and a check that cries wolf on known-good input is one people learn to
    ignore.
    """
    problems: list[str] = []
    if strict_citations is None:
        strict_citations = bool(spec.get("generated"))
    facts = register_facts(register)
    paras_by_p = facts["paragraphs_by_principle"]
    reg_quotes = facts["quotes"]

    driven = set(paras_by_p)
    # The two register shapes name this field differently — `also_drives_cde` on
    # a CDE register, `also_obligates` on an obligation register — and they mean
    # the same thing: this principle is partly out of scope AND still produces
    # something. Checking only the CDE name reported a correct P8 policy as one
    # that should not exist, which is the cries-wolf failure this module has
    # already been bitten by once.
    overlap_keys = ("also_drives_cde", "also_obligates")
    out_of_scope_only: set[int] = set()
    for entry in register.get("out_of_scope") or []:
        if not any(entry.get(k) for k in overlap_keys):
            out_of_scope_only.update(
                p for p in (entry.get("principles") or []) if isinstance(p, int))

    policies = spec.get("policies") or []
    refs = [p.get("ref") for p in policies]
    if len(set(refs)) != len(refs):
        problems.append("duplicate policy refs")

    covered: set[int] = set()
    for pol in policies:
        ref = pol.get("ref", "?")
        df = pol.get("derived_from") or {}
        principle = df.get("principle")
        covered.add(principle)

        if principle not in driven:
            problems.append(
                f"{ref}: principle {principle} does not drive any CDE in the "
                f"register (register cites {sorted(driven)})")
        if isinstance(principle, int) and principle > 11:
            problems.append(f"{ref}: principle {principle} — only 1-11 are bank-facing")
        if principle in out_of_scope_only:
            problems.append(
                f"{ref}: principle {principle} is out_of_scope without "
                f"also_drives_cde/also_obligates, so it should not have a policy")

        # Paragraph citations must exist in the register — generated specs only.
        if strict_citations:
            supported = paras_by_p.get(principle, set()) | facts["all_paragraphs"]
            for para in df.get("paragraphs") or []:
                if para not in supported:
                    problems.append(
                        f"{ref}: cites paragraph {para}, which is not in the "
                        f"register (the agent cannot have read it — likely "
                        f"invented)")

        desc = pol.get("description") or ""
        if "&para;" not in desc and "¶" not in desc:
            problems.append(f"{ref}: description has no paragraph quotation — "
                            f"no audit trail to the source text")

        # Every quoted span must appear in some register quote. Checked on
        # normalised text, so entity-vs-character differences do not false-alarm.
        if strict_citations:
            seen_quotes: set[str] = set()
            for quoted in re.findall(r'"([^"]{40,})"', _plain(desc)):
                if any(quoted[:120] in rq for rq in reg_quotes):
                    continue
                # Distinguish two very different situations. Both are failures,
                # but they need different fixes, and calling either one
                # "fabricated" is wrong — see the note below.
                head = quoted[:60]
                extended = any(head in rq for rq in reg_quotes)
                if extended:
                    problems.append(
                        f"{ref}: quotation STARTS in the register but continues "
                        f"beyond it: {quoted[:70]!r}… — the tail came from "
                        f"outside the provided source")
                else:
                    problems.append(
                        f"{ref}: quotation is not traceable to the register: "
                        f"{quoted[:70]!r}… — it may still be accurate, but the "
                        f"agent could not have read it here")
                if quoted[:80] in seen_quotes:
                    problems.append(f"{ref}: the same quotation appears twice")
                seen_quotes.add(quoted[:80])

    missing = sorted(driven - covered - out_of_scope_only)
    if missing:
        problems.append(
            f"principles {missing} drive CDEs but have no policy — "
            f"that is uncovered regulatory surface")

    # Standards
    pol_refs = set(refs)
    std_refs = [s.get("ref") for s in spec.get("standards") or []]
    if len(set(std_refs)) != len(std_refs):
        problems.append("duplicate standard refs")
    for std in spec.get("standards") or []:
        sref = std.get("ref", "?")
        if std.get("from_policy") not in pol_refs:
            problems.append(f"{sref}: from_policy {std.get('from_policy')!r} "
                            f"matches no policy ref")
        for req in std.get("derived_requirements") or []:
            for f in req.get("fields") or []:
                name, ftype = f.get("name", "?"), f.get("type")
                vals = f.get("allowed_values")
                if ftype == "picker":
                    if not vals:
                        problems.append(f"{sref}/{name}: picker without allowed_values")
                    elif not any(
                        re.search(r"\b(no|none|not|never|un\w+|fail\w*|absent|"
                                  r"undocumented|planned|in progress)\b", str(v), re.I)
                        for v in vals
                    ):
                        # A control whose every option is affirmative cannot
                        # record non-compliance, so it is decoration.
                        problems.append(
                            f"{sref}/{name}: no negative or 'not done' option in "
                            f"{vals} — a picker that cannot record failure is not "
                            f"a control")
                elif ftype == "text" and vals:
                    problems.append(f"{sref}/{name}: text field with allowed_values")

    # Only a MODEL emitting this is a problem; a hand-authored spec may carry it
    # legitimately, and finalize() recomputes it either way.
    if strict_citations and "standard_attachment" in spec:
        problems.append("model emitted 'standard_attachment', which the kit derives")
    return problems


def finalize(spec: dict, register: dict, *, register_sha: str,
             prompt_sha: str | None = None) -> dict:
    """Attach derived fields and the unreviewed provenance stamp."""
    out = {k: v for k, v in spec.items() if k != "standard_attachment"}
    out["standard_attachment"] = derive_attachment(spec, register)
    out["generated"] = {
        "by": "policy_author",
        "at": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ",
                                         __import__("time").gmtime()),
        "register_sha": register_sha,
        "prompt_sha": prompt_sha,
        "reviewed": False,
    }
    return out


def review_gate(spec: dict, path: str | Path = "<spec>") -> str | None:
    """Return a refusal message if this spec must not be provisioned yet.

    Hand-authored specs have no `generated` block and pass untouched — the
    existing reviewed bcbs239.json keeps working exactly as before.
    """
    gen = spec.get("generated")
    if not gen:
        return None
    if gen.get("reviewed") is True:
        return None
    return (
        f"{path} is agent-authored and not marked reviewed.\n"
        f"  Generated by {gen.get('by')} at {gen.get('at')} from register "
        f"{gen.get('register_sha')}.\n"
        f"\n"
        f"  This spec would create governance objects in a customer's catalog. "
        f"Read it,\n"
        f"  edit anything wrong, then set \"reviewed\": true (and ideally "
        f"\"reviewed_by\").\n"
        f"  The kit will not set that flag for you — that is the entire point "
        f"of it.\n"
        f"\n"
        f"  Check especially: paragraph citations and quotations against the "
        f"register,\n"
        f"  and that every picker can record a failing answer."
    )


def diff_specs(old: dict, new: dict) -> dict:
    """Compare two policy specs — e.g. before and after the document changed.

    This is the "do we need new policies?" question in its purest form: author a
    spec from the current document, diff it against the spec you deployed from,
    and the delta IS the answer.

    Matching is by `ref`, with a title fallback, because a re-authored spec may
    pick a different token for the same obligation. Anything that cannot be
    matched is reported rather than assumed new — an unmatched pair silently
    counted as "added + removed" would overstate churn.
    """
    def index(spec: dict, key: str) -> dict[str, dict]:
        out = {}
        for item in spec.get(key) or []:
            out[item.get("ref")] = item
        return out

    def by_title(spec: dict, key: str) -> dict[str, dict]:
        return {(i.get("title") or i.get("ref") or "").strip().lower(): i
                for i in spec.get(key) or []}

    old_p, new_p = index(old, "policies"), index(new, "policies")
    old_t, new_t = by_title(old, "policies"), by_title(new, "policies")

    added, removed, changed, renamed = [], [], [], []

    for ref, item in new_p.items():
        if ref in old_p:
            continue
        title = (item.get("title") or "").strip().lower()
        if title in old_t:
            renamed.append({"from_ref": old_t[title].get("ref"), "to_ref": ref,
                            "title": item.get("title")})
        else:
            added.append({"ref": ref, "title": item.get("title"),
                          "principle": (item.get("derived_from") or {}).get("principle")})

    renamed_old = {r["from_ref"] for r in renamed}
    for ref, item in old_p.items():
        if ref not in new_p and ref not in renamed_old:
            removed.append({"ref": ref, "title": item.get("title"),
                            "principle": (item.get("derived_from") or {}).get("principle")})

    for ref in set(old_p) & set(new_p):
        o, n = old_p[ref], new_p[ref]
        deltas = []
        if (o.get("derived_from") or {}) != (n.get("derived_from") or {}):
            deltas.append(f"derived_from {o.get('derived_from')} -> "
                          f"{n.get('derived_from')}")
        if _plain(o.get("description", "")) != _plain(n.get("description", "")):
            deltas.append("description text changed")
        if (o.get("title") or "") != (n.get("title") or ""):
            deltas.append(f"title {o.get('title')!r} -> {n.get('title')!r}")
        if deltas:
            changed.append({"ref": ref, "deltas": deltas})

    # Standards: attestation fields are where a document change usually lands,
    # so compare the field NAME SETS rather than only counting requirements.
    def fieldset(spec: dict) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        for std in spec.get("standards") or []:
            names = {f.get("name") for req in std.get("derived_requirements") or []
                     for f in req.get("fields") or []}
            out[std.get("ref")] = names
        return out

    of, nf = fieldset(old), fieldset(new)
    std_changes = []
    for ref in sorted(set(of) | set(nf)):
        if ref not in of:
            std_changes.append({"ref": ref, "change": "new standard",
                                "fields_added": sorted(nf[ref])})
        elif ref not in nf:
            std_changes.append({"ref": ref, "change": "standard removed"})
        elif of[ref] != nf[ref]:
            std_changes.append({
                "ref": ref, "change": "attestation fields changed",
                "fields_added": sorted(nf[ref] - of[ref]),
                "fields_removed": sorted(of[ref] - nf[ref])})

    return {"policies_added": added, "policies_removed": removed,
            "policies_changed": changed, "policies_renamed": renamed,
            "standards_changed": std_changes,
            "material": bool(added or removed or changed or std_changes)}


def render_for_review(spec: dict, register: dict, width: int = 78) -> list[str]:
    """Human-readable rendering of a policy spec, for the review step.

    `policy author` prints counts; nobody can review counts. This prints what a
    reviewer actually has to judge: the obligation, its citations, whether each
    quotation is traceable to the register, and every attestation field a steward
    will be asked to answer.

    Quote provenance is marked inline (OK / NOT TRACEABLE) rather than listed
    separately at the end, because the reviewer's decision is per-policy and a
    problem list at the bottom is read last or not at all.
    """
    import textwrap

    out: list[str] = []
    facts = register_facts(register)
    reg_quotes = facts["quotes"]
    gen = spec.get("generated") or {}

    reg = spec.get("regulation") or {}
    out.append("=" * width)
    out.append(f"POLICY SPEC — {reg.get('id', '?')}: {reg.get('title', '')}"[:width])
    if gen:
        out.append(f"  generated by {gen.get('by')} at {gen.get('at')}")
        out.append(f"  register {gen.get('register_sha')}  prompt {gen.get('prompt_sha')}")
        out.append(f"  reviewed: {gen.get('reviewed')}"
                   + (f" by {gen['reviewed_by']}" if gen.get("reviewed_by") else ""))
    else:
        out.append("  hand-authored (no `generated` block)")
    grp = spec.get("policy_group") or {}
    out.append(f"  policy group (PREREQUISITE, not created): {grp.get('title')!r}")
    out.append("=" * width)

    std_by_policy: dict[str, list[dict]] = {}
    for std in spec.get("standards") or []:
        std_by_policy.setdefault(std.get("from_policy"), []).append(std)

    for pol in spec.get("policies") or []:
        df = pol.get("derived_from") or {}
        out.append("")
        out.append(f"POLICY {pol.get('ref')} — {pol.get('title')}")
        out.append(f"  principle {df.get('principle')}, "
                   f"paragraphs {df.get('paragraphs')}")

        body = _plain(pol.get("description") or "")
        # Split the obligation from the quoted material so a reviewer can see
        # what the bank is being told to do without wading through citations.
        quotes = re.findall(r'"([^"]{40,})"', body)
        obligation = re.split(r'\u00b6\s*\d+', body)[0].strip()
        for line in textwrap.wrap(obligation, width - 4):
            out.append(f"    {line}")
        for q in quotes:
            traceable = any(q[:120] in rq for rq in reg_quotes)
            mark = "OK          " if traceable else "NOT TRACEABLE"
            out.append(f"    [{mark}] quoted:")
            for line in textwrap.wrap(f'"{q}"', width - 8):
                out.append(f"        {line}")

        for std in std_by_policy.get(pol.get("ref"), []):
            out.append(f"  STANDARD {std.get('ref')}")
            for line in textwrap.wrap(f"purpose: {_plain(std.get('purpose') or '')}", width - 6):
                out.append(f"      {line}")
            for line in textwrap.wrap(f"scope: {_plain(std.get('scope') or '')}", width - 6):
                out.append(f"      {line}")
            for req in std.get("derived_requirements") or []:
                # Entities are correct on the wire but unreadable in a review
                # view; a reviewer skimming past "&para;36(c)" is a reviewer who
                # did not check the citation.
                out.append(f"      - {_plain(req.get('name') or '')}")
                if req.get("description"):
                    for line in textwrap.wrap(_plain(req["description"]), width - 10):
                        out.append(f"          {line}")
                for f in req.get("fields") or []:
                    if f.get("type") == "picker":
                        vals = f.get("allowed_values") or []
                        has_neg = any(
                            re.search(r"\b(no|none|not|never|un\w+|fail\w*|absent|"
                                      r"undocumented|planned|in progress)\b", str(v), re.I)
                            for v in vals)
                        flag = "" if has_neg else "   <- NO FAILING OPTION"
                        shown = " / ".join(_plain(str(v)) for v in vals)
                        out.append(f"          [picker] {_plain(f.get('name') or '')}:"
                                   f"{flag}")
                        for line in textwrap.wrap(shown, width - 22):
                            out.append(f"                     {line}")
                    else:
                        out.append(f"          [text]   {_plain(f.get('name') or '')}")

    problems = audit(spec, register)
    out.append("")
    out.append("-" * width)
    if problems:
        out.append(f"{len(problems)} AUDIT PROBLEM(S):")
        for pr in problems:
            for line in textwrap.wrap(pr, width - 4):
                out.append(f"  {line}")
    else:
        out.append("Audit clean.")
    return out


def approve(spec: dict, reviewed_by: str) -> dict:
    """Record a HUMAN approval. Only ever called from an explicit --approve.

    Note the distinction that keeps the gate meaningful: the kit still never
    approves on its own initiative. This is a person acting through the tool
    instead of hand-editing JSON, and it records WHO, which hand-editing does
    not. If it is ever called from anywhere other than an explicit user
    instruction, the gate has been defeated.
    """
    if not spec.get("generated"):
        raise ValueError("this spec is hand-authored; there is nothing to approve")
    if not reviewed_by.strip():
        raise ValueError("--by is required: an approval with no name is not one")
    out = json.loads(json.dumps(spec))
    out["generated"]["reviewed"] = True
    out["generated"]["reviewed_by"] = reviewed_by.strip()
    out["generated"]["reviewed_at"] = __import__("time").strftime(
        "%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime())
    return out


def required_principles(register: dict) -> list[int]:
    """Principles that MUST get a policy: derived, not left to the model.

    Coverage proved unstable across runs of the same prompt — 7 policies once,
    6 the next time with principle 6 silently dropped. That is not a wording
    problem to be argued with; the required set is a pure function of the
    register (principles that drive a CDE, minus those out of scope with no
    also_drives_cde). So compute it and state it in the invocation.
    """
    facts = register_facts(register)
    driven = {p for p in facts["paragraphs_by_principle"] if 1 <= p <= 11}
    out_only: set[int] = set()
    for entry in register.get("out_of_scope") or []:
        if not entry.get("also_drives_cde"):
            out_only.update(x for x in (entry.get("principles") or [])
                            if isinstance(x, int))
    return sorted(driven - out_only)


def authoring_instruction(register: dict) -> str:
    """Runtime coverage contract, prepended to the register in the message.

    Deliberately NOT in the prompt file: the prompt stays regulation-agnostic
    and variable-free (so the deployed prompt is byte-identical to the tested
    one), while per-document facts travel as runtime input — which is the same
    split the rest of the kit uses.
    """
    need = required_principles(register)
    reg_id = (register.get("regulation") or {}).get("id", "this regulation")
    return (
        f"Author the policy spec for {reg_id}.\n"
        f"\n"
        f"REQUIRED COVERAGE — exactly one policy for each of these "
        f"{len(need)} principles: {', '.join(map(str, need))}.\n"
        f"This list is computed from the register; it is not a suggestion and "
        f"not your judgement to revise. Omitting one leaves regulatory surface "
        f"uncovered, and producing one for a principle not listed means citing "
        f"something the register does not support. Count your policies against "
        f"this list before you return.\n"
        f"\n"
        f"Do not emit `standard_attachment`.\n"
        f"\n"
        f"REGISTER:\n"
    )


# ---------------------------------------------------------------------------
# Obligation path: assembling a policy spec from prose + citation POINTERS.
#
# This is the half of the v0.3.0 design that lives in code. policy_body_author
# emits paragraphs and `{"from": "citations", "index": 0}`; everything exact —
# the quotation text, the paragraph numbers, the refs, the HTML — is produced
# here. The model never touches a quotation, so a citation cannot drift from its
# source by construction rather than by instruction.
#
# The division is the project convention applied literally: judgement (which
# quotation supports this obligation, how to phrase the obligation) to the
# agent; actions that must be exact (reproducing text, computing a union of
# paragraph numbers, escaping markup) to Python.
# ---------------------------------------------------------------------------

# Non-ASCII that can legitimately appear in prose, mapped to the entities the
# Policy Center descriptions use. The source text is normalised to ASCII by
# scripts/extract_bcbs239.py, so this is a belt-and-braces pass for characters a
# model introduces in its OWN prose (em dashes, curly apostrophes) rather than in
# a quotation.
_TO_ENTITY = {
    "—": "&mdash;", "–": "&ndash;", "¶": "&para;",
    "’": "&rsquo;", "‘": "&lsquo;", "“": "&ldquo;", "”": "&rdquo;",
    "…": "&hellip;", " ": "&nbsp;",
}


def _html_text(text: str) -> str:
    """Escape a plain-text run for embedding in an HTML description.

    Order matters: `&` first, or the entities introduced below get re-escaped
    into `&amp;mdash;`.
    """
    # `"` must be escaped, not just the angle brackets. A quotation block wraps
    # its text in literal double quotes, and the register contains at least one
    # sentence with an embedded pair — para 37's `a "dictionary" of the concepts
    # used`. Left raw, that produces nested quotes in the rendered description
    # AND truncates verify_quotes_against_register's own extraction at the inner
    # quote, which reports a correctly-copied citation as not present in the
    # register. `_plain` maps &quot; back, so comparison is unaffected.
    out = ((text or "").replace("&", "&amp;").replace("<", "&lt;")
           .replace(">", "&gt;").replace('"', "&quot;"))
    for char, ent in _TO_ENTITY.items():
        out = out.replace(char, ent)
    # Anything still non-ASCII would reach Policy Center as a raw byte in HTML.
    # Numeric-escape rather than drop it: losing a character silently is worse
    # than an ugly entity, and this should be empty in practice.
    return "".join(c if ord(c) < 128 else f"&#{ord(c)};" for c in out)


def _para_label(paragraphs: list[int]) -> str:
    """`[36]` -> '36'; `[44, 45, 46]` -> '44&ndash;46'; `[33, 40]` -> '33, 40'."""
    ps = sorted({int(p) for p in paragraphs or []})
    if not ps:
        return "?"
    if len(ps) > 2 and ps == list(range(ps[0], ps[-1] + 1)):
        return f"{ps[0]}&ndash;{ps[-1]}"
    return ", ".join(str(p) for p in ps)


def resolve_citations(obligation: dict, cite: list[dict]) -> tuple[list[dict], list[str]]:
    """Turn pointers into the register's exact citations, deduplicated.

    Returns (citations, problems). A pointer that does not resolve is a PROBLEM,
    never a silent skip: dropping it would leave a policy with less audit trail
    than its author intended, and nothing downstream would show that anything
    had gone missing.

    Deduplication is by normalised quote text, keeping first occurrence. The
    register genuinely reuses quotations — an obligation's `citations[0]` is
    often the same sentence as one of its expectations' citations — so pointing
    at both is reasonable behaviour that should cost nothing rather than produce
    the same paragraph twice in one description.
    """
    problems: list[str] = []
    out: list[dict] = []
    seen: set[str] = set()
    ref = obligation.get("ref", "?")

    for ptr in cite or []:
        src, idx = ptr.get("from"), ptr.get("index")
        if src == "citations":
            arr = obligation.get("citations") or []
            item = arr[idx] if isinstance(idx, int) and 0 <= idx < len(arr) else None
        elif src == "measurable_expectations":
            arr = obligation.get("measurable_expectations") or []
            exp = arr[idx] if isinstance(idx, int) and 0 <= idx < len(arr) else None
            item = (exp or {}).get("citation")
        else:
            problems.append(f"{ref}: cite.from={src!r} is not a known array")
            continue

        if not item or not item.get("quote"):
            problems.append(
                f"{ref}: cite {{from: {src}, index: {idx}}} does not resolve "
                f"(array has {len(arr)} entr{'y' if len(arr) == 1 else 'ies'})")
            continue

        key = " ".join((item.get("quote") or "").split()).lower()
        if key in seen:
            continue
        seen.add(key)
        out.append({"paragraphs": item.get("paragraphs") or [],
                    "quote": item["quote"]})

    if not out:
        problems.append(f"{ref}: no citation resolved — a policy description "
                        f"without a quotation cannot be audited to its source")
    return out, problems


def build_description(obligation: dict, body_paragraphs: list[str],
                      citations: list[dict]) -> str:
    """Compose the Policy Center HTML description.

    Shape matches the hand-authored policies/bcbs239.json, which is the spec
    verified to create four policies and four published standards on a live
    instance: a bolded principle lead-in, the body, then one block per quotation.

    The quotation text is inserted VERBATIM from the register and is the only
    part of this string not written by a model.
    """
    name = obligation.get("principle_name") or ""
    lead = f"Principle {obligation.get('principle')}"
    if name:
        lead = f"{lead} &mdash; {_html_text(name)}"

    paras = [p for p in (body_paragraphs or []) if (p or "").strip()]
    blocks: list[str] = []
    if paras:
        blocks.append(f"<p><strong>{lead}.</strong> {_html_text(paras[0])}</p>")
        blocks.extend(f"<p>{_html_text(p)}</p>" for p in paras[1:])
    else:
        blocks.append(f"<p><strong>{lead}.</strong></p>")

    for c in citations:
        label = _para_label(c["paragraphs"])
        blocks.append(f'<p><em>&para;{label}:</em> "{_html_text(c["quote"])}"</p>')
    return "".join(blocks)


def assemble_policy_spec(register: dict, bodies: dict, *,
                         register_sha: str = "", prompt_sha: str = "",
                         by: str = "policy_body_author") -> tuple[dict, list[str]]:
    """Obligation register + policy_body_author output -> a provisionable spec.

    Refuses rather than proceeds on any 1:1 violation. policy_author's measured
    instability was in policy COUNT (7 one run, 6 the next), and the whole point
    of driving the count from the register is that it can no longer vary — so a
    mismatch here means the model dropped, merged or invented an entry, and
    quietly provisioning six policies for seven obligations is the exact failure
    this design was built to remove.

    Emits NO `standards`. Alation's Critical Data Manager generates the overlay
    standard from the policy's own prose; a standard authored here would bypass
    that generation. `policies.py:plan()` already guards standards with
    `if spec.get("standards")`, so their absence needs no change there.
    """
    problems: list[str] = []
    obligations = register.get("obligations") or []
    by_ref = {o.get("ref"): o for o in obligations}
    entries = bodies.get("policies") or []

    seen_refs = [e.get("ref") for e in entries]
    dupes = {r for r in seen_refs if seen_refs.count(r) > 1}
    if dupes:
        problems.append(f"duplicate refs in the body draft: {sorted(dupes)}")
    missing = [r for r in by_ref if r not in seen_refs]
    if missing:
        problems.append(f"no policy body for {sorted(missing)} — the register "
                        f"has {len(by_ref)} obligations, the draft has "
                        f"{len(entries)} entries")
    extra = [r for r in seen_refs if r not in by_ref]
    if extra:
        problems.append(f"policy body for {sorted(set(extra))}, which is not an "
                        f"obligation in this register")

    reg = register.get("regulation") or {}
    reg_id = reg.get("id") or "REG"
    spec: dict[str, Any] = {
        "regulation": {k: v for k, v in reg.items()
                       if k in {"id", "title", "publisher", "published", "source_url"}},
        "policy_group": {
            "ref": f"PG-{reg_id}",
            "title": reg.get("title_short") or reg_id,
            "$comment": "PREREQUISITE. Policy groups have no create API — this "
                        "is resolved by title and never created.",
        },
        "policies": [],
        "generated": {
            "by": by,
            "at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "register_sha": register_sha,
            "prompt_sha": prompt_sha,
            # The kit NEVER sets this true. `policy apply` refuses an unreviewed
            # spec, and that gate is the only thing standing between a model's
            # output and writes into a customer's Policy Center.
            "reviewed": False,
        },
    }

    # Register order, not draft order: the register is the authority on which
    # obligations exist and in what sequence.
    drafts = {e.get("ref"): e for e in entries}
    for o in obligations:
        ref = o.get("ref")
        draft = drafts.get(ref)
        if not draft:
            continue
        citations, probs = resolve_citations(o, draft.get("cite") or [])
        problems.extend(probs)

        paragraphs = sorted({p for c in citations for p in (c["paragraphs"] or [])})
        if not paragraphs:
            problems.append(f"{ref}: no paragraph numbers on any resolved citation")

        title = (o.get("title") or "").strip()
        if len(title) < 8:
            problems.append(f"{ref}: obligation title {title!r} is too short to "
                            f"be a policy title")

        spec["policies"].append({
            # POL- rather than OBL-, because the ref namespace belongs to the
            # spec and the state file, not to the register it came from.
            "ref": f"POL-P{int(o.get('principle')):02d}",
            "title": title,
            "derived_from": {"principle": o.get("principle"),
                             "paragraphs": paragraphs},
            "description": build_description(o, draft.get("body_paragraphs") or [],
                                             citations),
        })

    for p in spec["policies"]:
        if len(p["description"]) < 200:
            problems.append(f"{p['ref']}: description is {len(p['description'])} "
                            f"chars; the spec schema requires 200")

    return spec, problems


def verify_quotes_against_register(spec: dict, register: dict) -> list[str]:
    """Every quotation in the assembled spec appears verbatim in the register.

    Should be vacuously true — the quotations were copied out of the register a
    few lines above. It is checked anyway because it is nearly free and because
    it is the claim the whole demo rests on; an assertion that cannot fail is
    still worth making when the alternative is trusting that it cannot.
    """
    pool = set()
    for o in register.get("obligations") or []:
        for c in o.get("citations") or []:
            pool.add(" ".join((c.get("quote") or "").split()))
        for e in o.get("measurable_expectations") or []:
            q = (e.get("citation") or {}).get("quote")
            if q:
                pool.add(" ".join(q.split()))
    for x in register.get("cross_cutting") or []:
        q = (x.get("citation") or {}).get("quote")
        if q:
            pool.add(" ".join(q.split()))

    problems: list[str] = []
    for p in spec.get("policies") or []:
        for quoted in re.findall(r'<em>&para;[^<]*</em>\s*"([^"]+)"',
                                 p.get("description") or ""):
            plain = " ".join(_plain(quoted).split())
            if not any(plain == " ".join(_plain(q).split()) for q in pool):
                problems.append(f"{p['ref']}: quoted text is not in the register: "
                                f"{plain[:70]!r}")
    return problems
