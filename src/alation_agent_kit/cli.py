"""agentkit CLI.

    agentkit whoami                        # probe all three auth surfaces
    agentkit refresh-token <username>      # mint a refresh token + user_id
    agentkit userid <email>                # find the numeric ALATION_USER_ID
    agentkit list agents|tools|llms [--raw]
    agentkit export <agent-name> [-o agents/foo.json]
    agentkit deploy agents/foo.json [--prompt <prompt-stem>] [--dry-run]
    agentkit run <agent-name> [--input-file FILE] [-o out.md] [-v] [--raw]
    agentkit prompts
    agentkit tool show <name> | deploy <file.json>
    agentkit workflow deploy|run|runs|list|probe-payload
    agentkit preflight [--skip-unstructured]
    agentkit pipeline [--source file|unstructured] [--stop-after interpret]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from .agents import AgentStudio
from .auth import Settings, load_dotenv
from .client import AI_V1, AlationClient
from .invoke import extract_text, run_agent, run_agent_stream
from .prompts import list_prompts, load_prompt, sync_prompt_into_agent
from .store import extract_json as extract_json_text
from .store import read_json, write_json


def _studio() -> AgentStudio:
    return AgentStudio(AlationClient(Settings.from_env()))


def cmd_whoami(args) -> int:
    s = Settings.from_env()
    client = AlationClient(s)
    print(f"Instance: {s.base_url}")
    print(f"Client ID: {s.client_id[:8]}…")
    print(f"Token cache: {s.token_cache or 'disabled'}")

    agents = AgentStudio(client).list_agents()
    print(f"Agent Studio (OAuth bearer): OK — {len(agents)} agent config(s) visible")

    # The catalog APIs are a separate auth surface, and the policy provider
    # needs them. Probe rather than assume: a green Agent Studio check says
    # nothing about whether /integration/v1/ will answer.
    print("\nCatalog APIs (/integration/v1/):")
    if s.force_catalog_token:
        if s.access_token:
            cred = "legacy TOKEN header from ALATION_ACCESS_TOKEN (pasted)"
        elif s.refresh_token and s.user_id:
            cred = f"legacy TOKEN header, minted for user_id {s.user_id}"
        else:
            print("  ALATION_FORCE_CATALOG_TOKEN is on but no legacy credential is set.")
            return 1
        print(f"  Credential: {cred}")
        print("  NOTE: this overrides the OAuth bearer. If this 403s, try unsetting")
        print("  ALATION_FORCE_CATALOG_TOKEN — the bearer works here on cloud instances.")
    else:
        print("  Credential: OAuth bearer (the same one Agent Studio uses)")

    try:
        groups = client.get("/integration/v1/policy_group/", params={"limit": 1})
        n = len(groups) if isinstance(groups, list) else "?"
        print(f"  Probe GET /integration/v1/policy_group/: OK ({n} row(s) returned)")
    except Exception as exc:  # surfaced verbatim; the message is the diagnosis
        print(f"  Probe FAILED: {exc}")
        return 1

    # The CDE service is a third auth surface and the one that actually needs
    # the legacy token, to bootstrap its CDEToken. Report it separately so a
    # green catalog check is not mistaken for standards being deployable.
    print("\nCDE service (/cde-service/, CDEToken header):")

    # Diagnose before minting: "Refresh token provided is invalid" covers
    # expired, revoked, wrong user_id, and never-was-a-refresh-token. Guessing
    # between those has already cost us two wrong fixes.
    from .auth import CatalogTokenProvider
    d = CatalogTokenProvider(s).diagnose()
    print(f"  ALATION_REFRESH_TOKEN: {d['fingerprint']}")
    print(f"  ALATION_USER_ID: {s.user_id}")
    print(f"  Mint access token: {'OK' if d['ok'] else d['status']}")
    if not d["ok"]:
        print(f"  Detail: {d['detail']}")
        print("  -> Compare the length above with the token you pasted. A refresh")
        print("     token from this instance is ~86 chars; a 43-char value is an")
        print("     ACCESS token in the wrong slot. If it does not match what you")
        print("     pasted, .env did not save, or a duplicate")
        print("     ALATION_REFRESH_TOKEN line further down is winning.")
        print("     Mint a fresh pair with: ./run.sh refresh-token <username>")
        return 1
    print(f"  Access token expires: {d['detail'].get('token_expires_at')}")

    tok = client.catalog_token()
    if not tok:
        print("  Credential: NONE — needs ALATION_ACCESS_TOKEN, or")
        print("  ALATION_REFRESH_TOKEN + numeric ALATION_USER_ID. Only overlay")
        print("  standards need this; policies deploy without it.")
        return 0
    print(f"  Credential: legacy API token ({len(tok)} chars)")
    from .policies import PolicyProvisioner
    from .state import DeploymentState
    ok, why = PolicyProvisioner(
        client, DeploymentState(instance=s.base_url)
    ).verify_standards_api()
    print(f"  Standards API: {'OK' if ok else 'UNAVAILABLE — ' + why}")
    return 0


def cmd_list(args) -> int:
    st = _studio()
    rows = {"agents": st.list_agents, "tools": st.list_tools, "llms": st.list_llms}[args.kind]()
    if not rows:
        print(f"No {args.kind} found")
        return 0

    if args.raw:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0

    for row in rows:
        rid = str(row.get("id", "?"))
        if args.kind == "llms":
            # Same scavenging deploy uses to match a file's llm block, so what
            # you see here is what resolution actually compares against.
            i = llm_identity(row)
            bits = [b for b in (i["name"], i["refs"][0] if i["refs"] else "") if b and b != i["provider"]]
            label = f"{i['provider']}   {'  |  '.join(bits)}" if bits else i["provider"]
            print(f"  {rid:38}  {label}")
        else:
            print(f"  {rid:38}  {row.get('name') or '(unnamed)'}")

    print(f"\n{len(rows)} {args.kind}   (add --raw to see every field)")
    if args.kind == "llms" and not any(llm_identity(r)["refs"] or llm_identity(r)["name"] for r in rows):
        print(
            "\nNote: no name or model field came back — only provider. Run\n"
            "`list llms --raw` and share it, or pin llm_config_id in the agent file."
        )
    return 0


def cmd_export(args) -> int:
    doc = _studio().export_agent(args.name)
    out = Path(args.output) if args.output else Path("agents") / f"{args.name}.json"
    write_json(out, doc)
    print(f"Exported {args.name!r} -> {out}")
    if "_warning" in doc:
        print(f"  ! {doc['_warning']}")
    return 0


def cmd_deploy(args) -> int:
    doc = read_json(args.file)
    if args.prompt:
        prompt = load_prompt(args.prompt)
        doc = sync_prompt_into_agent(doc, prompt)
        print(f"Using prompt {args.prompt!r} (sha={prompt.sha256}, git={prompt.git_sha()})")
        # Match an actual Jinja construct, not a lone delimiter. The previous
        # test was `"{{" in prompt or "}}" in prompt`, which fired on any prompt
        # whose JSON example has a nested object closing at the same point as its
        # parent — `"quote": "verbatim"}}`. Both interpreter prompts do, so this
        # warned on every deploy of known-good prompts, which is how a check
        # teaches you to ignore it. Jinja only substitutes a matched pair; a bare
        # `}}` is literal text and reaches the model correctly.
        leftover = re.findall(r"\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\}",
                              doc["prompt"], re.S)
        if leftover:
            print(
                "  ! prompt still contains unrendered Jinja after rendering. "
                "Agent Studio has no templating, so this reaches the model "
                "literally. Either declare it under deploy_variables in the "
                "sidecar meta, or it is runtime input and does not belong in "
                "the prompt body at all:"
            )
            for frag in leftover[:5]:
                print(f"      {frag[:90]!r}")
            if len(leftover) > 5:
                print(f"      ... and {len(leftover) - 5} more")

    # --dry-run must work with no credentials — it is the offline sanity check.
    if args.dry_run:
        try:
            _studio().deploy_agent(doc, dry_run=True)
        except Exception as exc:  # noqa: BLE001 - offline fallback is the point
            print(f"[dry-run] offline (no live instance: {exc})")
            print(f"[dry-run] agent {doc.get('name')!r}")
            print(f"[dry-run] prompt: {len(doc.get('prompt') or '')} chars")
            print(f"[dry-run] tools: {len(doc.get('tools') or [])}, "
                  f"bindings: {len(doc.get('parameter_bindings') or [])}")
            print("[dry-run] cannot tell create-vs-update without credentials")
        return 0

    _studio().deploy_agent(doc, dry_run=False)
    return 0


def cmd_run(args) -> int:
    st = _studio()
    agent_id = st.resolve_agent_id(args.name) or args.name

    message = args.message or ""
    if args.input_file:
        text = Path(args.input_file).read_text(encoding="utf-8")
        message = f"{message}\n\n{text}".strip() if message else text

    payload: dict = {"message": message}
    if args.param:
        for kv in args.param:
            key, _, val = kv.partition("=")
            payload[key] = val

    if args.poll:
        # Legacy path. Kept for diagnosis only — the API deletes tasks on
        # success, so this usually cannot retrieve output.
        result = run_agent(st.c, agent_id, payload, verbose=args.verbose)
        text = extract_text(result) or json.dumps(result, indent=2)
    else:
        raw_path = f"{args.output}.raw-stream.txt" if (args.raw and args.output) else None
        text = run_agent_stream(
            st.c, agent_id, payload, verbose=args.verbose, raw_path=raw_path,
            attempts=args.retries,
        )

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Wrote {args.output}  ({len(text):,} chars)")
    else:
        print(text)
    return 0


def _provisioner(args):
    from .policies import PolicyProvisioner
    from .state import DeploymentState
    s = Settings.from_env()
    state = DeploymentState(args.state, instance=s.base_url)
    prefix = args.prefix if args.prefix is not None else state.prefix
    if args.prefix is not None:
        state.set_prefix(args.prefix)
    return PolicyProvisioner(AlationClient(s), state, prefix), state


def _cmd_policy_assemble(args) -> int:
    """Obligation register + policy_body_author draft -> a provisionable spec.

    Deliberately OFFLINE — no client, no credentials, no instance. Assembly is
    pure transformation, so it can be re-run against a saved draft without
    burning another agent call, and it can be tested with nothing configured.
    """
    import hashlib
    from .authoring import assemble_policy_spec, verify_quotes_against_register

    register = extract_json_text(Path(args.register).read_text(encoding="utf-8"))
    if register is None:
        print(f"ERROR: no JSON object found in {args.register}")
        return 1
    if not register.get("obligations"):
        print(f"ERROR: {args.register} has no `obligations` — this action takes "
              f"an OBLIGATION register (bcbs239_obligation_interpreter), not a "
              f"CDE register. For the CDE path use `policy author`.")
        return 1

    bodies = extract_json_text(Path(args.bodies).read_text(encoding="utf-8"))
    if bodies is None or "policies" not in bodies:
        print(f"ERROR: {args.bodies} is not a policy_body_author draft "
              f"(expected a `policies` array)")
        return 1

    reg_sha = hashlib.sha256(
        json.dumps(register, sort_keys=True).encode()).hexdigest()[:16]
    spec, problems = assemble_policy_spec(register, bodies, register_sha=reg_sha)

    # Policy groups have no create API — they are resolved by EXACT title and
    # never created. The register carries `regulation.id` ("BCBS239"), but the
    # group on an instance may be titled differently ("BCBS 239"), and a miss
    # means the policies land ungrouped. Overridable rather than hand-edited,
    # because this is a per-instance fact and the spec is regenerated output.
    if args.group_title:
        spec["policy_group"]["title"] = args.group_title
    problems += verify_quotes_against_register(spec, register)

    print(f"Assembling {args.register} (sha={reg_sha}) + {args.bodies}")
    print(f"  {len(register['obligations'])} obligation(s) -> "
          f"{len(spec['policies'])} policy(ies), no standards "
          f"(CDM derives those from the policy)\n")
    for p in spec["policies"]:
        print(f"  {p['ref']:<10} {p['title'][:44]:44} "
              f"para {str(p['derived_from']['paragraphs']):<16} "
              f"{p['description'].count('<em>&para;')} quote(s)  "
              f"{len(p['description']):>5} chars")

    if problems:
        print(f"\n{len(problems)} problem(s) — nothing written:")
        for pr in problems:
            print(f"  ! {pr}")
        return 1

    write_json(args.output, spec)
    print(f"\nWrote {args.output}")
    print("Marked reviewed:false — `policy apply` refuses it until a human "
          "approves. Read it, then:")
    print(f"  ./run.sh policy review {args.output} --approve --by \"Your Name\"")
    return 0


def cmd_policy(args) -> int:
    """plan / apply / destroy over policy groups, policies and standards."""
    # `assemble` runs BEFORE the spec is read or a provisioner is built: it is
    # the action that PRODUCES a spec, so requiring one as input would be
    # circular, and it touches no instance, so requiring credentials would make
    # a pure transformation unrunnable offline.
    if args.action == "assemble":
        return _cmd_policy_assemble(args)

    spec = read_json(args.spec)
    prov, state = _provisioner(args)

    if args.action == "plan":
        actions = prov.plan(spec)
        print(f"Plan for {spec.get('regulation', {}).get('id', args.spec)} "
              f"on {state.instance}")
        print(f"Namespace prefix: {prov.prefix!r}" if prov.prefix
              else "Namespace prefix: (none) — consider --prefix for a customer instance")
        print()
        for a in actions:
            print(a)
        creates = sum(1 for a in actions if a.verb == "create")
        unsupported = [a for a in actions if a.verb == "unsupported"]
        print(f"\n{creates} to create, "
              f"{sum(1 for a in actions if a.verb == 'skip')} already present"
              + (f", {len(unsupported)} unsupported" if unsupported else ""))
        if unsupported:
            print("\nUnsupported objects must be created in the UI and become a "
                  "documented prerequisite.")
        if creates:
            print("\nNothing has been created. Re-run with `policy apply` to proceed.")
        return 0

    if args.action == "apply":
        from .authoring import review_gate
        refusal = review_gate(spec, args.spec)
        if refusal:
            print("REFUSING TO APPLY\n")
            print(refusal)
            return 1
        # Refuse a write when the state file belongs to a different spec.
        # Otherwise apply "succeeds" while silently skipping the objects whose
        # refs collide — which is exactly how three policies went missing.
        conflicts = prov.state_conflicts(spec)
        if conflicts:
            print(f"REFUSING TO APPLY — {len(conflicts)} state conflict(s):\n")
            for c in conflicts:
                print(f"  ! {c}")
            print("\nThe state file records objects from a different spec. Run")
            print("`policy destroy --yes` first, or point --state at a separate file")
            print("to keep the two deployments independently tearable.")
            return 1

        actions = prov.plan(spec)
        creates = [a for a in actions if a.verb == "create"]
        if not creates:
            print("Nothing to create — everything in the spec is already present.")
            return 0
        if not args.yes:
            print(f"About to create {len(creates)} object(s) in {state.instance}:")
            for a in creates:
                print(a)
            print("\nRe-run with --yes to proceed. Nothing has been created.")
            return 0
        only = set(args.only.split(",")) if args.only else None
        for line in prov.apply(spec, only=only):
            print(line)
        print(f"\nState: {state.path} now records {len(state)} object(s)")

        # Verify immediately rather than trusting the write. Ids are recovered
        # by title search, so this is the only thing standing between a bad
        # recovery and destroy deleting someone else's policy.
        print("\nVerifying recorded ids against the instance:")
        log, ok = prov.verify(spec)
        for line in log:
            print(line)
        if not ok:
            print("\nDo not run destroy until the above is resolved.")
        return 0 if ok else 1

    if args.action == "publish":
        log, ok = prov.publish(new_status=args.status, comment=args.comment,
                               dry_run=not args.yes)
        for line in log:
            print(line)
        if not args.yes:
            print("\nDry run. Re-run with --yes to change status.")
        return 0 if ok else 1

    if args.action == "author":
        from .authoring import audit, finalize
        from .invoke import run_agent_stream
        from .authoring import _plain  # noqa: F401  (kept importable for tests)
        import hashlib

        register_raw = Path(args.register).read_text(encoding="utf-8")
        register = extract_json_text(register_raw)
        if register is None:
            print(f"ERROR: no JSON object found in {args.register}")
            return 1
        reg_sha = hashlib.sha256(
            json.dumps(register, sort_keys=True).encode()).hexdigest()[:16]

        from .authoring import authoring_instruction, required_principles

        st = AgentStudio(AlationClient(Settings.from_env()))
        agent_id = st.resolve_agent_id(args.agent) or args.agent
        need = required_principles(register)
        payload = (authoring_instruction(register)
                   + json.dumps(register, separators=(",", ":")))
        print(f"Authoring from {args.register} (register sha={reg_sha}, "
              f"{len(payload):,} chars) via {args.agent}")
        print(f"Required coverage (derived): principles "
              f"{', '.join(map(str, need))}\n")
        text = run_agent_stream(st.c, agent_id, {"message": payload})
        draft = extract_json_text(text)
        if draft is None:
            raw = Path(args.output + ".raw.md")
            raw.write_text(text, encoding="utf-8")
            print(f"ERROR: no JSON object in the response; raw kept at {raw}")
            return 1

        prompt_sha = None
        try:
            prompt_sha = load_prompt(args.agent).sha256
        except Exception:  # noqa: BLE001 - provenance is best-effort
            pass

        problems = audit(draft, register, strict_citations=True)
        spec = finalize(draft, register, register_sha=reg_sha,
                        prompt_sha=prompt_sha)
        out = Path(args.output)
        write_json(out, spec)

        print(f"Wrote {out}")
        print(f"  policies:  {len(spec.get('policies') or [])}")
        print(f"  standards: {len(spec.get('standards') or [])}")
        att = (spec.get("standard_attachment") or {}).get("by_principle") or {}
        covered = sorted(int(k) for k, v in att.items() if v)
        missing = [p for p in need if p not in covered]
        extra = [p for p in covered if p not in need]
        print(f"  principles covered: {', '.join(map(str, covered)) or 'none'}"
              f"  (required: {', '.join(map(str, need))})")
        if missing:
            print(f"  ! MISSING principle(s) {missing} — re-run; coverage has "
                  f"been unstable across runs")
        if extra:
            print(f"  ! UNREQUESTED principle(s) {extra}")
        if problems:
            print(f"\n{len(problems)} audit problem(s) — fix before review:")
            for pr in problems:
                print(f"  ! {pr}")
        else:
            print("\nAudit clean.")
        print(f"\nNOT DEPLOYABLE YET. `policy apply` will refuse this file until a")
        print(f"human reads it and sets \"reviewed\": true in its `generated` block.")
        return 0 if not problems else 1

    if args.action == "review":
        from .authoring import approve, render_for_review

        register = None
        if args.register and Path(args.register).is_file():
            register = extract_json_text(Path(args.register).read_text(encoding="utf-8"))
        if register is None:
            print(f"ERROR: need the register to check citations; "
                  f"{args.register} not readable")
            return 1

        for line in render_for_review(spec, register):
            print(line)

        if not args.approve:
            print("\nThis is a review view. Nothing has been changed.")
            gen = spec.get("generated") or {}
            if gen and not gen.get("reviewed"):
                print("To approve after reading:")
                print(f"  ./run.sh policy review {args.spec} --approve "
                      f"--by \"Your Name\"")
            return 0

        from .authoring import audit
        problems = audit(spec, register)
        if problems and not args.force:
            print(f"\nREFUSING to approve: {len(problems)} audit problem(s) above.")
            print("Fix the spec, or re-run with --force if you have judged each one")
            print("acceptable — the not-traceable quotes are accurate BCBS 239 text,")
            print("so --force is a legitimate choice here, but it should be a choice.")
            return 1
        try:
            approved = approve(spec, args.by or "")
        except ValueError as exc:
            print(f"\nERROR: {exc}")
            return 1
        write_json(args.spec, approved)
        print(f"\nApproved by {approved['generated']['reviewed_by']} "
              f"at {approved['generated']['reviewed_at']}")
        print(f"Wrote {args.spec} — `policy apply` will now accept it.")
        return 0

    if args.action == "assess":
        register = None
        if args.register and Path(args.register).is_file():
            register = extract_json_text(Path(args.register).read_text(encoding="utf-8"))
        log, summary = prov.assess(spec, register)
        print(f"Governance coverage on {state.instance}")
        print(f"Spec: {args.spec}   prefix: {prov.prefix!r}\n")
        for line in log:
            print(line)
        print(f"\n{summary['present']} present, {summary['missing']} missing, "
              f"{summary['untracked']} untracked, {summary['orphaned']} orphaned")

        if args.against:
            from .authoring import diff_specs
            older = read_json(args.against)
            d = diff_specs(older, spec)
            print(f"\n=== Spec change vs {args.against} ===")
            if not d["material"]:
                print("  No material change — the document implies the same policies.")
            for item in d["policies_added"]:
                print(f"  + NEW POLICY NEEDED  {item['title']} "
                      f"(principle {item['principle']})")
            for item in d["policies_removed"]:
                print(f"  - NO LONGER IMPLIED  {item['title']} "
                      f"(principle {item['principle']})")
            for item in d["policies_renamed"]:
                print(f"  ~ RENAMED  {item['from_ref']} -> {item['to_ref']} "
                      f"({item['title']})")
            for item in d["policies_changed"]:
                print(f"  ~ CHANGED  {item['ref']}: {'; '.join(item['deltas'])}")
            for item in d["standards_changed"]:
                bits = [item["change"]]
                if item.get("fields_added"):
                    bits.append(f"+{len(item['fields_added'])} field(s)")
                if item.get("fields_removed"):
                    bits.append(f"-{len(item['fields_removed'])} field(s)")
                print(f"  ~ STANDARD {item['ref']}: {', '.join(bits)}")
        missing = summary["missing"] or summary.get("uncovered_principles")
        return 1 if missing else 0

    if args.action == "standards":
        print(json.dumps(prov.dump_standards(), indent=2, default=str))
        return 0

    if args.action == "verify":
        log, ok = prov.verify(spec)
        for line in log:
            print(line)
        print("\nVerified: every recorded id still matches its object."
              if ok else
              "\nPROBLEMS FOUND above. Resolve them before running destroy —"
              "\ndestroy deletes by recorded id and does not re-check titles.")
        return 0 if ok else 1

    if args.action == "destroy":
        log = prov.destroy(dry_run=not args.yes)
        for line in log:
            print(line)
        if not args.yes:
            print("\nDry run. Re-run with --yes to delete.")
            print("Only objects this kit recorded creating are ever deleted, "
                  "by recorded ID — never matched by name.")
        return 0

    return 1


def cmd_userid(args) -> int:
    """Look up a numeric Alation user id via the bearer-authenticated User API.

    Exists because ALATION_USER_ID has to be exact and there is no documented
    "who am I" endpoint — guessing it (we tried 1) mints a token for the wrong
    user, and Alation then rejects the refresh-token/user-id pair as if the
    token itself were bad.
    """
    client = AlationClient(Settings.from_env())
    email = args.email.strip().lower()

    # Server-side filter first; fall back to paging, since the filter parameter
    # is undocumented and may simply be ignored (which would silently return
    # page one and look like a miss).
    try:
        rows = client.get("/integration/v1/user/", params={"email": email})
        if isinstance(rows, list):
            for u in rows:
                if str(u.get("email", "")).lower() == email:
                    print(f"{u['id']}\t{u.get('email')}\t{u.get('display_name') or ''}")
                    print("\nPut that number in ALATION_USER_ID.")
                    return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Filtered lookup failed ({exc}); paging instead.")

    seen = 0
    for skip in range(0, args.max_scan, 100):
        try:
            rows = client.get("/integration/v1/user/",
                              params={"limit": 100, "skip": skip})
        except Exception as exc:  # noqa: BLE001
            print(f"User API unavailable: {exc}")
            print("\nThe User API is Server-Admin-scoped. If your OAuth client "
                  "lacks that role, read the id from the URL of your own profile "
                  "page in the Alation UI instead.")
            return 1
        if not isinstance(rows, list) or not rows:
            break
        seen += len(rows)
        for u in rows:
            if str(u.get("email", "")).lower() == email:
                print(f"{u['id']}\t{u.get('email')}\t{u.get('display_name') or ''}")
                print("\nPut that number in ALATION_USER_ID.")
                return 0

    print(f"No user matched {email} in {seen} record(s) scanned.")
    print("Raise --max-scan, or read the id from your profile page URL.")
    return 1


def cmd_refresh_token(args) -> int:
    """Mint a refresh token and print it plus the numeric user_id.

    Removes two failure modes we hit by hand: pasting the wrong value into
    ALATION_REFRESH_TOKEN, and guessing ALATION_USER_ID.
    """
    import getpass

    from .auth import create_refresh_token

    s = Settings.from_env()
    password = args.password or getpass.getpass(f"Alation password for {args.username}: ")
    print("\nNOTE: this revokes any previous refresh token for this user.\n")
    try:
        body = create_refresh_token(s.base_url, args.username, password,
                                    name=args.name, verify_ssl=s.verify_ssl)
    except RuntimeError as exc:
        print(exc)
        return 1

    tok, uid = body.get("refresh_token"), body.get("user_id")
    print(f"refresh_token : {tok}")
    print(f"user_id       : {uid}")
    print(f"expires       : {body.get('token_expires_at')}")
    print(f"status        : {body.get('token_status')}")
    print("\nPut these in .env (replace any existing values):")
    print(f"  ALATION_REFRESH_TOKEN={tok}")
    print(f"  ALATION_USER_ID={uid}")
    print("\nThen: ./run.sh whoami")
    return 0


def cmd_preflight(args) -> int:
    """Assert prerequisites read-only. Provisions nothing."""
    from .preflight import run_preflight

    s = Settings.from_env()
    client = AlationClient(s)
    print(f"Preflight against {s.base_url}\n")
    if args.probe_cde_create:
        print("NOTE: --probe-cde-create WRITES a throwaway standard and deletes "
              "it again.\n")
    checks, ok = run_preflight(
        client, include_unstructured=not args.skip_unstructured,
        probe_cde_create=args.probe_cde_create)
    for ch in checks:
        print(ch)
    required_failed = [c for c in checks if c.required and not c.ok]
    optional_failed = [c for c in checks if not c.required and not c.ok]
    print(f"\n{len(checks) - len(required_failed) - len(optional_failed)} passed, "
          f"{len(required_failed)} required failure(s), "
          f"{len(optional_failed)} optional not yet available")
    if optional_failed:
        print("\nOptional items are the unstructured-document path. The pipeline "
              "runs today from extracted text without them.")
    return 0 if ok else 1


def cmd_pipeline(args) -> int:
    """Regulation -> register -> gap analysis, in one command."""
    from .pipeline import Pipeline
    from .sources import build_source

    s = Settings.from_env()
    client = AlationClient(s)
    try:
        source = build_source(
            args.source, path=args.input_file, client=client,
            object_id=args.object_id, asset_type_name=args.asset_type)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    pipe = Pipeline(AgentStudio(client), outdir=Path(args.outdir),
                    interpreter=args.interpreter, mapper=args.mapper)
    print(f"Pipeline on {s.base_url}")
    print(f"Source: {source.describe()}\n")
    result = pipe.run(source, tag=args.tag, stop_after=args.stop_after)
    for st in pipe.stages:
        print(st)
    print(f"\nManifest: {result.get('manifest_file')}")
    if result.get("mapping"):
        print("Coverage: " + json.dumps(result["mapping"]["coverage_summary"]))
    return 0 if result.get("ok") else 1


def cmd_tool(args) -> int:
    """Inspect a tool's real schema, or deploy one from a file.

    `show` exists because a tool's input_parameter_schema is the only reliable
    statement of what it can actually do — and the docs do not list per-tool
    schemas for built-ins.
    """
    st = _studio()
    if args.action == "show":
        want = args.target.strip().lower()
        hits = [t for t in st.list_tools()
                if want in str(t.get("name") or "").lower()
                or want in str(t.get("function_name") or "").lower()]
        if not hits:
            print(f"No tool matching {args.target!r}")
            return 1
        if args.raw:
            # Every field, including http_config — which `show` otherwise never
            # prints. This is the recovery path for a custom tool that exists on
            # the instance but has no source file in the repo: dump it here and
            # write it back to tools/. Earned 2026-08-28, when the cleanup pass
            # deleted the definitions for two live HTTP tools on the strength of
            # an inventory note that wrongly said they were never deployed.
            print(json.dumps(hits, indent=2, sort_keys=True))
            return 0
        for tool in hits:
            print(f"\n=== {tool.get('name')} ===")
            print(f"  id:            {tool.get('id')}")
            print(f"  function_name: {tool.get('function_name')}")
            print(f"  tool_type:     {tool.get('tool_type')}")
            print(f"  visibility:    {tool.get('visibility_label')}")
            print(f"  default_ref:   {tool.get('default_ref')}")
            desc = str(tool.get("description") or "")
            schema = json.dumps(tool.get("input_parameter_schema"), indent=4)
            if args.full:
                print(f"  description:\n{desc}")
                print("  input_parameter_schema:")
                print(schema)
            else:
                print(f"  description:   {desc[:300]}"
                      + (f"\n                 ... +{len(desc)-300} chars "
                         f"(--full to see all)" if len(desc) > 300 else ""))
                print("  input_parameter_schema:")
                print(schema[:2500])
                if len(schema) > 2500:
                    print(f"    ... +{len(schema)-2500} chars (--full to see all)")
        return 0

    doc = read_json(args.target)
    st.deploy_tool(doc, dry_run=args.dry_run)
    return 0


def cmd_workflow(args) -> int:
    """Deploy, run and inspect Agent Studio Flows."""
    from .workflows import Workflows, probe_payload

    client = AlationClient(Settings.from_env())
    wf = Workflows(client)

    if args.action == "list":
        rows = wf.list()
        for w in rows:
            nodes = len(((w.get("definition") or {}).get("nodes")) or [])
            print(f"  {str(w.get('id')):38}  {w.get('name')}  ({nodes} node(s))")
        print(f"\n{len(rows)} workflow(s)")
        return 0

    if args.action == "probe-payload":
        print("Testing whether a large payload survives step-to-step passing.")
        print("Creates a throwaway flow and deletes it again.\n")
        for line in probe_payload(client, size_kb=args.size_kb):
            print(line)
        return 0

    if args.action == "deploy":
        doc = read_json(args.target)
        log: list[str] = []

        # The regulation text is a placeholder in the committed file so a ~120KB
        # blob is not sitting in git. Substitute at deploy time.
        text_path = Path(args.regulation)
        raw = json.dumps(doc)
        if "__REGULATION_TEXT__" in raw:
            if not text_path.is_file():
                print(f"ERROR: the flow needs the regulation text, but "
                      f"{text_path} is missing.\n"
                      f"Extract it first: python3 scripts/extract_bcbs239.py "
                      f"artifacts/bcbs239.pdf")
                return 1
            text = text_path.read_text(encoding="utf-8")
            doc = json.loads(raw.replace("__REGULATION_TEXT__",
                                         json.dumps(text)[1:-1]))
            print(f"Embedded {len(text):,} chars of regulation text from "
                  f"{text_path}")

        if not args.dry_run:
            doc = wf.resolve_agents(doc, log)
            for line in log:
                print(line)
        wf.deploy(doc, dry_run=args.dry_run)
        return 0

    if args.action == "run":
        wid = wf.resolve_id(args.target) or args.target
        started = wf.execute(wid, background=not args.sync)
        eid = (started or {}).get("id") or (started or {}).get("execution_id")
        print(f"Started execution {eid}")
        if args.no_wait:
            print(f"Check progress: ./run.sh workflow runs {args.target}")
            return 0
        final = wf.await_run(eid)
        print(f"Status: {final.get('status')}")
        if final.get("error_message"):
            print(f"Error: {final['error_message']}")
        print()
        # Print INPUT size as well as output. The input is the truncation
        # evidence: if `map` receives far less than `interpret` produced, the
        # register was clipped in transit and the mapper's poor result would
        # look like a model failure rather than a plumbing one.
        prev_out = None
        for n in wf.nodes(eid):
            nid = n.get("node_id") or n.get("id")
            in_size = len(json.dumps(n.get("input_data") or {}, default=str))
            out = n.get("output_data")
            out_size = len(json.dumps(out, default=str)) if out else 0
            flag = ""
            if prev_out and in_size < prev_out * 0.9:
                flag = (f"   <- INPUT SMALLER THAN UPSTREAM OUTPUT "
                        f"({prev_out:,} -> {in_size:,}): possible truncation")
            print(f"--- node {nid!r}  status={n.get('status')}  "
                  f"in {in_size:,} / out {out_size:,} chars{flag}")
            prev_out = out_size or prev_out
        # The last node's output is the readable report — print it in full.
        nodes = wf.nodes(eid)
        if nodes:
            last = nodes[-1]
            out = last.get("output_data")
            text = out if isinstance(out, str) else json.dumps(out, indent=2, default=str)
            if args.output:
                Path(args.output).parent.mkdir(parents=True, exist_ok=True)
                Path(args.output).write_text(str(text), encoding="utf-8")
                print(f"\nFinal output -> {args.output}")
            else:
                print(f"\n=== final output ({last.get('node_id')}) ===")
                print(text)
        ok = str(final.get("status", "")).lower() in (
            "completed", "succeeded", "success")
        return 0 if ok else 1

    if args.action == "runs":
        wid = wf.resolve_id(args.target) or args.target
        for r in wf.runs(wid):
            print(f"  {str(r.get('id')):38}  {r.get('status'):12}  "
                  f"{r.get('trigger_type', '')}  {r.get('created_at', '')}")
        return 0

    return 1


def cmd_prompts(args) -> int:
    for name in list_prompts():
        p = load_prompt(name)
        model = (p.meta.get("model") or {}) if isinstance(p.meta.get("model"), dict) else {}
        print(f"  {name:44} sha={p.sha256}  git={p.git_sha()}  model={model.get('name', '-')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="agentkit", description="Alation Agent Studio dev kit")
    p.add_argument("--env-file", default=".env")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("whoami").set_defaults(func=cmd_whoami)

    prt = sub.add_parser("refresh-token",
                         help="Mint a refresh token + learn your numeric user id")
    prt.add_argument("username")
    prt.add_argument("--password", help="Omit to be prompted (does not hit shell history)")
    prt.add_argument("--name", default="alation-agent-kit")
    prt.set_defaults(func=cmd_refresh_token)

    pu = sub.add_parser("userid", help="Find the numeric user id for an email")
    pu.add_argument("email")
    pu.add_argument("--max-scan", type=int, default=2000)
    pu.set_defaults(func=cmd_userid)

    pf = sub.add_parser("preflight",
                        help="Assert prerequisites on the target instance (read-only)")
    pf.add_argument("--probe-cde-create", action="store_true",
                    help="WRITES: create+delete a throwaway standard to test "
                         "whether the CDE service accepts the bearer for writes")
    pf.add_argument("--skip-unstructured", action="store_true",
                    help="Omit the unstructured-document checks")
    pf.set_defaults(func=cmd_preflight)

    pi = sub.add_parser("pipeline",
                        help="regulation -> register -> gap analysis, one command")
    pi.add_argument("--source", default="file", choices=["file", "unstructured"],
                    help="Where the regulation text comes from")
    pi.add_argument("--input-file",
                    default="artifacts/bcbs239/bank_principles.txt",
                    help="For --source file")
    pi.add_argument("--object-id",
                    help="For --source unstructured: the document's UUID")
    pi.add_argument("--asset-type", default=None,
                    help="For --source unstructured (default unstructured_data_file)")
    pi.add_argument("--outdir", default="artifacts/pipeline")
    pi.add_argument("--tag", help="Names the outputs; defaults to a timestamp")
    pi.add_argument("--stop-after", choices=["fetch", "interpret"],
                    help="Stop early — `interpret` skips the mapper's ACU cost")
    pi.add_argument("--interpreter", default="bcbs239_cde_dq_interpreter")
    pi.add_argument("--mapper", default="bcbs239_pde_mapper")
    pi.set_defaults(func=cmd_pipeline)

    ts = sub.add_parser("tool", help="Inspect or deploy custom tools")
    ts.add_argument("action", choices=["show", "deploy"])
    ts.add_argument("target", help="Tool name (show) or file path (deploy)")
    ts.add_argument("--dry-run", action="store_true")
    ts.add_argument("--full", action="store_true",
                    help="Print the whole description and schema — built-in tools "
                         "document their contract there and truncating it means "
                         "guessing")
    ts.add_argument("--raw", action="store_true",
                    help="Dump every field as JSON, including http_config — use "
                         "this to recover a custom tool's definition from the "
                         "instance when the source file is missing")
    ts.set_defaults(func=cmd_tool)

    pw = sub.add_parser("workflow", help="Agent Studio Flows")
    pw.add_argument("action",
                    choices=["list", "deploy", "run", "runs", "probe-payload"])
    pw.add_argument("target", nargs="?", default="workflows/bcbs239-gap-analysis.json",
                    help="File path (deploy) or workflow name (run/runs)")
    pw.add_argument("--regulation",
                    default="artifacts/bcbs239/bank_principles.txt",
                    help="Text substituted for __REGULATION_TEXT__ at deploy time")
    pw.add_argument("--dry-run", action="store_true")
    pw.add_argument("--sync", action="store_true",
                    help="Use execute-sync. Background is safer for big payloads")
    pw.add_argument("--no-wait", action="store_true")
    pw.add_argument("-o", "--output", help="Write the final step's output here")
    pw.add_argument("--size-kb", type=int, default=56,
                    help="For probe-payload: blob size to push through")
    pw.set_defaults(func=cmd_workflow)

    pl = sub.add_parser("list")
    pl.add_argument("kind", choices=["agents", "tools", "llms"])
    pl.add_argument("--raw", action="store_true", help="Dump every field as JSON")
    pl.set_defaults(func=cmd_list)

    pe = sub.add_parser("export")
    pe.add_argument("name")
    pe.add_argument("-o", "--output")
    pe.set_defaults(func=cmd_export)

    pd = sub.add_parser("deploy")
    pd.add_argument("file")
    pd.add_argument("--prompt", help="Prompt file stem to render into the agent's prompt field")
    pd.add_argument("--dry-run", action="store_true")
    pd.set_defaults(func=cmd_deploy)

    pr = sub.add_parser("run")
    pr.add_argument("name")
    pr.add_argument("-m", "--message", default="")
    pr.add_argument("--input-file", help="File whose text is appended to the message")
    pr.add_argument("--param", action="append", help="Extra input param, key=value")
    pr.add_argument("-o", "--output")
    pr.add_argument("-v", "--verbose", action="store_true", help="Echo raw SSE lines")
    pr.add_argument("--raw", action="store_true",
                    help="Also save the raw SSE stream next to --output (for debugging)")
    pr.add_argument("--retries", type=int, default=3,
                    help="Stream attempts before giving up (default 3). Long "
                         "generations occasionally die with a read timeout.")
    pr.add_argument("--poll", action="store_true",
                    help="Use the legacy /call + task-polling path (usually 404s on success)")
    pr.set_defaults(func=cmd_run)

    pp = sub.add_parser("policy", help="Provision policy groups, policies, standards")
    pp.add_argument("action",
                choices=["plan", "apply", "verify", "standards", "author",
                         "assemble", "review", "assess", "publish", "destroy"])
    pp.add_argument("spec", nargs="?", default="policies/bcbs239.json")
    pp.add_argument("--prefix", default=None,
                    help="Namespace prefix for created objects, e.g. 'BCBS239 - '. "
                         "Recorded in the state file and reused.")
    pp.add_argument("--state", default=".deployment-state.json",
                    help="Deployment state file. One per target instance.")
    pp.add_argument("--only", help="Comma-separated kinds: policy_group,policy,standard")
    pp.add_argument("--yes", action="store_true",
                    help="Actually write. Without it, apply and destroy only report.")
    pp.add_argument("--register", default="docs/runs/v0.6.0/run01.json",
                    help="For `policy author`: the CDE requirements register. "
                         "For `policy assemble`: the OBLIGATION register from "
                         "bcbs239_obligation_interpreter.")
    pp.add_argument("--bodies", default="docs/runs/pba-v0.1.0/run01.json",
                    help="For `policy assemble`: the policy_body_author draft "
                         "(prose plus citation pointers).")
    pp.add_argument("--group-title",
                    help="For `policy assemble`: the EXACT title of the existing "
                         "policy group. Groups have no create API and are matched "
                         "by exact title, so 'BCBS239' and 'BCBS 239' are "
                         "different groups. Defaults to the register's "
                         "regulation.id.")
    pp.add_argument("--agent", default="policy_author",
                    help="For `policy author`: the authoring agent")
    pp.add_argument("-o", "--output", default="policies/bcbs239.generated.json",
                    help="For `policy author`: where to write the spec")
    pp.add_argument("--approve", action="store_true",
                    help="For `policy review`: record YOUR approval after reading")
    pp.add_argument("--by", help="Your name, required with --approve")
    pp.add_argument("--force", action="store_true",
                    help="Approve despite audit problems you have judged acceptable")
    pp.add_argument("--against",
                    help="For `policy assess`: an earlier spec to diff against, "
                         "answering 'has the document changed what we need?'")
    pp.add_argument("--status", default="PUBLISHED",
                    choices=["DRAFT", "PENDING_APPROVAL", "PUBLISHED"],
                    help="Target status for `policy publish`")
    pp.add_argument("--comment", default="",
                    help="Optional comment recorded with a status change")
    pp.set_defaults(func=cmd_policy)

    sub.add_parser("prompts").set_defaults(func=cmd_prompts)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv(args.env_file)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
