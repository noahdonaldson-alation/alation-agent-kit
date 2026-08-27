"""agentkit CLI.

    agentkit whoami                        # verify auth and token cache
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
    print(f"Auth OK — {len(agents)} agent config(s) visible")
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
        return 0

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
    pp.add_argument("action", choices=["plan", "apply", "destroy"])
    pp.add_argument("spec", nargs="?", default="policies/bcbs239.json")
    pp.add_argument("--prefix", default=None,
                    help="Namespace prefix for created objects, e.g. 'BCBS239 - '. "
                         "Recorded in the state file and reused.")
    pp.add_argument("--state", default=".deployment-state.json",
                    help="Deployment state file. One per target instance.")
    pp.add_argument("--only", help="Comma-separated kinds: policy_group,policy,standard")
    pp.add_argument("--yes", action="store_true",
                    help="Actually write. Without it, apply and destroy only report.")
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
