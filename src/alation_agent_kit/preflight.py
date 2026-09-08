"""Read-only assertions about a target instance. Provisions nothing.

Settled decision: anything not API-addressable is a **declared prerequisite**
asserted by preflight, never provisioned. This module is where those assertions
live, so a field SE learns what is missing in one command instead of by hitting
a 403 mid-deploy.

Every check returns a Check rather than raising, so one missing prerequisite does
not hide the other five. Exit code is non-zero if any REQUIRED check fails;
optional checks report and do not fail the run.
"""

from __future__ import annotations

from dataclasses import dataclass

from .client import AI_V1, AlationClient, AlationError


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    required: bool = True
    fix: str = ""

    def __str__(self) -> str:
        mark = "OK  " if self.ok else ("FAIL" if self.required else "WARN")
        line = f"  [{mark}] {self.name}: {self.detail}"
        if not self.ok and self.fix:
            line += f"\n         -> {self.fix}"
        return line


# The tool an agent needs in order to read document content. Invisible in Agent
# Studio until an FDE raises its visibility from ALATION_INTERNAL, which uses a
# non-public admin API authenticated by browser SESSION COOKIES, not OAuth. Our
# client cannot do it, hence: prerequisite, not automation.
CONTENT_TOOL_NAMES = ("get_asset_content", "get_asset_content_tool")
# Display names differ from function names: the tool shows as "Get Asset
# Content" in the UI and the list response. Match both forms.


def check_agent_studio(c: AlationClient) -> list[Check]:
    out = []
    try:
        agents = c.get(f"{AI_V1}/config/agent")
        n = len(agents) if isinstance(agents, list) else "?"
        out.append(Check("Agent Studio reachable", True,
                         f"{n} agent config(s) visible"))
    except Exception as exc:  # noqa: BLE001
        out.append(Check("Agent Studio reachable", False, str(exc)[:160],
                         fix="Check ALATION_CLIENT_ID/SECRET and that the OAuth "
                             "client has an appropriate role."))
    return out


def check_catalog(c: AlationClient) -> list[Check]:
    out = []
    try:
        groups = c.get("/integration/v1/policy_group/", params={"limit": 500})
        titles = [g.get("title") for g in groups] if isinstance(groups, list) else []
        out.append(Check("Policy Center enabled", True,
                         f"{len(titles)} policy group(s)"))
        out.append(Check(
            "Policy group exists (namespace target)",
            bool(titles), f"groups: {', '.join(str(t) for t in titles[:5]) or 'none'}",
            fix="Policy groups have no create API. Make the group in the UI: "
                "Governance -> Policy Center -> Policy Groups."))
    except AlationError as exc:
        # This 403 is famously misleading on this instance: it means "feature
        # off" at least as often as it means "bad credentials".
        out.append(Check(
            "Policy Center enabled", False, str(exc)[:200],
            fix="A 403 here usually means the FEATURE is disabled, not that auth "
                "failed. Enable Policy Center in Admin Settings, then re-run."))
    except Exception as exc:  # noqa: BLE001
        out.append(Check("Policy Center enabled", False, str(exc)[:160]))
    return out


def check_cde_service(c: AlationClient) -> list[Check]:
    out = []
    tok = None
    try:
        tok = c.catalog_token()
    except Exception as exc:  # noqa: BLE001
        out.append(Check("Legacy API token available", False, str(exc)[:160],
                         fix="Run: ./run.sh refresh-token <username>"))
    if tok:
        out.append(Check("Legacy API token available", True,
                         f"{len(tok)} chars"))
        try:
            auth = c.request("POST", "/cde-service/integration/auth/", None,
                             extra_headers={"TOKEN": tok})
            cde = auth if isinstance(auth, str) else (
                auth.get("token") or auth.get("access_token"))
            c.get("/cde-service/integration/standard/?limit=1",
                  extra_headers={"CDEToken": cde})
            out.append(Check("CDE service reachable", True,
                             "auth + standards list OK"))
        except Exception as exc:  # noqa: BLE001
            out.append(Check("CDE service reachable", False, str(exc)[:200],
                             fix="Overlay standards need this. Policies do not — "
                                 "deploy with `policy apply --only policy`."))
    return out


def check_cde_bearer(c: AlationClient) -> list[Check]:
    """Does the CDE service accept the OAuth bearer alone?

    This decides whether chat-driven creation is possible at all.
    `POST /cde-service/integration/standard/` is the only create in this domain
    that is HTTP-tool shaped: a single JSON OBJECT body, synchronous, returning
    {id, key}. Business policies are array-bodied and therefore unreachable from
    an Agent Studio HTTP tool.

    If the bearer works here, a CLIENT_CREDENTIALS HTTP tool can create overlay
    standards from a chat turn. If it needs CDEToken, the tool would have to
    carry a static custom header that expires daily — workable for a scheduled
    demo, not for a customer deployment.

    Note `/cde-service/integration/` does NOT start with `/integration/`, so the
    client attaches no TOKEN header here: a plain GET is a clean bearer-only test.
    """
    try:
        c.get("/cde-service/integration/standard/?limit=1")
        return [Check(
            "CDE service accepts the OAuth bearer alone", True,
            "GET /cde-service/integration/standard/ answered with no CDEToken — "
            "an HTTP tool with CLIENT_CREDENTIALS auth can reach this service",
            required=False)]
    except Exception as exc:  # noqa: BLE001
        return [Check(
            "CDE service accepts the OAuth bearer alone", False, str(exc)[:180],
            required=False,
            fix="Bearer alone is refused, so the service needs the CDEToken "
                "bootstrap. For a chat demo an HTTP tool would need a static "
                "CDEToken in custom_headers, which expires — fine for a demo "
                "you re-arm, not for a customer deployment.")]


def probe_cde_create_with_bearer(c: AlationClient) -> list[Check]:
    """Can a standard be CREATED with the OAuth bearer alone? WRITES, then cleans up.

    This is the gate on chat-driven creation. A bearer-only GET already works,
    but read and write permissions are routinely different, and an Agent Studio
    HTTP tool can only offer CLIENT_CREDENTIALS (OAuth) — it cannot bootstrap a
    CDEToken, because that needs a second call with a dynamic header.

    Creates a throwaway standard with an unmistakable name, then deletes it by
    the returned integer id. Not part of the default preflight: preflight is
    read-only by contract, and this is not.
    """
    name = "AGENTKIT PROBE - delete me"
    body = {
        "name": name,
        "purpose": "Throwaway probe created by agentkit to test whether the CDE "
                   "service accepts the OAuth bearer for writes. Safe to delete.",
        "scope": "None. This object exists only to answer an auth question.",
        "derived_requirements": [{
            "name": "Probe",
            "description": "Probe requirement.",
            "fields": [{"name": "Probe field", "type": "text"}],
        }],
        "options": {"allow_duplicates": True},
    }
    try:
        resp = c.post("/cde-service/integration/standard/", json_body=body)
    except Exception as exc:  # noqa: BLE001
        return [Check(
            "CDE standard CREATE with bearer alone", False, str(exc)[:220],
            required=False,
            fix="Writes need the CDEToken bootstrap, which an Agent Studio HTTP "
                "tool cannot do (its auth options are NONE/BASIC/"
                "CLIENT_CREDENTIALS/AUTHORIZATION_CODE, all static). A chat "
                "demo would need a static CDEToken in custom_headers, which "
                "expires daily.")]

    sid = (resp or {}).get("id") if isinstance(resp, dict) else None
    cleanup = "no id returned, so nothing to clean up — CHECK THE UI"
    if sid:
        try:
            c.delete(f"/cde-service/integration/standard/{sid}/")
            cleanup = f"probe id={sid} deleted"
        except Exception as exc:  # noqa: BLE001
            cleanup = (f"probe id={sid} COULD NOT BE DELETED ({str(exc)[:80]}) — "
                       f"remove it by hand")
    return [Check(
        "CDE standard CREATE with bearer alone", True,
        f"created and cleaned up ({cleanup}). An HTTP tool with "
        f"CLIENT_CREDENTIALS auth can create standards from a chat turn.",
        required=False)]


def check_unstructured(c: AlationClient) -> list[Check]:
    """The prerequisites for reading document content out of the catalog.

    All OPTIONAL: the pipeline runs today from extracted text, and this path is
    an upgrade rather than a dependency. Marking them required would make
    preflight fail on every instance until the feature ships.
    """
    out: list[Check] = []

    # 1. Is the content-retrieval tool visible to Agent Studio? This is the
    #    single most informative check, because it is the last gate an FDE has
    #    to open and it is invisible until they do.
    try:
        # Must go through AgentStudio.list_tools(): it asks for all four
        # visibility labels (the API defaults to featured+regular and silently
        # hides `advanced`) and it unwraps the DataPage envelope. Reading
        # GET /config/tool directly returned {data, total}, which iterated as
        # zero tools and reported this as absent when it was present all along.
        from .agents import AgentStudio

        tools = AgentStudio(c).list_tools()
        matches = [
            t for t in tools
            if any(k in str(t.get("name") or t.get("function_name") or "")
                   .lower().replace(" ", "_") for k in CONTENT_TOOL_NAMES)
        ]
        # PRESENCE IN THIS LISTING IS NOT EVIDENCE OF USABILITY. list_tools()
        # deliberately asks for all four visibility labels, so a tool that ships
        # as `alation_internal` appears here while being unbindable in Agent
        # Studio until an FDE raises it. This check previously matched on name
        # alone and reported OK on gartner2026.mtse (2026-09-08) for a tool whose
        # record read `"visibility_label": "alation_internal"` — a false green on
        # the single prerequisite it exists to catch.
        # `visibility_label` on the tool record is the authoritative field.
        usable = [t for t in matches
                  if str(t.get("visibility_label") or "").lower()
                  != "alation_internal"]
        if usable:
            detail = ", ".join(str(t.get("name")) for t in usable)
        elif matches:
            detail = ", ".join(
                f"{t.get('name')} is present but visibility_label="
                f"{t.get('visibility_label')!r} — NOT bindable to an agent"
                for t in matches)
        else:
            detail = f"not among {len(tools)} visible tool(s)"
        out.append(Check(
            "get_asset_content tool bindable", bool(usable), detail,
            required=False,
            fix="The tool ships as ALATION_INTERNAL. An FDE must raise its "
                "visibility via PUT /ai/api/v1/admin/tool_configs/{uuid}/"
                "visibility?visibility_label=advanced — a non-public admin API "
                "authenticated by browser session cookies, so OAuth cannot do "
                "it. Bundle this ask WITH the feature-flag ask (Jon Lanham)."))
    except Exception as exc:  # noqa: BLE001
        out.append(Check("get_asset_content tool visible", False,
                         str(exc)[:160], required=False))

    # 2. Are unstructured object types enabled? If the feature flag is off, the
    #    otype is not served and searching for it fails or returns nothing.
    try:
        hits = c.get("/integration/v1/search/",
                     params={"otype": "unstructured_data_file", "limit": 1})
        n = len(hits) if isinstance(hits, list) else (
            (hits or {}).get("total") if isinstance(hits, dict) else "?")
        out.append(Check(
            "unstructured_data_file otype served", True,
            f"search answered ({n} result(s))", required=False))
    except Exception as exc:  # noqa: BLE001
        out.append(Check(
            "unstructured_data_file otype served", False, str(exc)[:160],
            required=False,
            fix="Needs alation.feature_flags.enable_unstructured_data=true and "
                "unstructured_data_source,unstructured_data_file appended to "
                "DEV_otype_service_enabled_otypes, then a deployment restart. "
                "Requires SSH or the Cloud console — route through an FDE."))
    return out


def run_preflight(c: AlationClient, include_unstructured: bool = True,
                  probe_cde_create: bool = False) -> tuple[list[Check], bool]:
    checks: list[Check] = []
    checks += check_agent_studio(c)
    checks += check_catalog(c)
    checks += check_cde_service(c)
    checks += check_cde_bearer(c)
    if probe_cde_create:
        checks += probe_cde_create_with_bearer(c)
    if include_unstructured:
        checks += check_unstructured(c)
    ok = all(ch.ok for ch in checks if ch.required)
    return checks, ok
