"""agentkit CLI.

    agentkit whoami                        # probe all three auth surfaces
    agentkit refresh-token <username>      # mint a refresh token + user_id
    agentkit userid <email>                # find the numeric ALATION_USER_ID
    agentkit list agents|tools|llms [--raw]
    agentkit export <agent-name> [-o agents/foo.json]
    agentkit deploy agents/foo.json [--prompt <prompt-stem>] [--dry-run]
    agentkit run <agent-name> [--input-file FILE] [-o out.md] [-v] [--raw]
    agentkit prompts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agents import AgentStudio
from .auth import Settings, load_dotenv
from .client import AI_V1, AlationClient
from .invoke import extract_text, run_agent, run_agent_stream
from .prompts import list_prompts, load_prompt, sync_prompt_into_agent
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
        if "{{" in doc["prompt"] or "}}" in doc["prompt"]:
            print(
                "  ! prompt still contains {{ }} after rendering. Agent Studio has no "
                "templating, so this would reach the model literally."
            )

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


def cmd_policy(args) -> int:
    """plan / apply / destroy over policy groups, policies and standards."""
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
                choices=["plan", "apply", "verify", "standards",
                         "publish", "destroy"])
    pp.add_argument("spec", nargs="?", default="policies/bcbs239.json")
    pp.add_argument("--prefix", default=None,
                    help="Namespace prefix for created objects, e.g. 'BCBS239 - '. "
                         "Recorded in the state file and reused.")
    pp.add_argument("--state", default=".deployment-state.json",
                    help="Deployment state file. One per target instance.")
    pp.add_argument("--only", help="Comma-separated kinds: policy_group,policy,standard")
    pp.add_argument("--yes", action="store_true",
                    help="Actually write. Without it, apply and destroy only report.")
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
