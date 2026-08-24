"""Run a deployed agent and get its output — the inner loop of iteration.

Two paths exist. We default to the non-streaming one because it is far easier to
assert against in tests:

    POST /chats/agent/{id}/call  -> {task_id, chat_id}
    GET  /task/{task_id}         -> poll until terminal

Errors worth recognizing:
    402  tool-call quota exceeded
    409  "Chat is busy."
    413  payload exceeds the model's context window  <- chunk your input
"""

from __future__ import annotations

import time
from typing import Any

from .client import AI_V1, AlationClient, AlationError

CHAT_PATH = f"{AI_V1}/chats/agent"
TASK_PATH = f"{AI_V1}/task"

_TERMINAL_OK = {"succeeded", "success", "completed", "complete", "done", "finished"}
_TERMINAL_BAD = {"failed", "error", "cancelled", "canceled"}


class AgentRunError(RuntimeError):
    pass


def run_agent(
    client: AlationClient,
    agent_id: str,
    payload: dict[str, Any],
    chat_id: str | None = None,
    poll_interval: float = 2.0,
    timeout_sec: float = 300.0,
    verbose: bool = False,
) -> dict:
    """Invoke an agent and block until it finishes.

    `payload` must conform to the agent's input_json_schema — usually
    {"message": "..."} plus any user-sourced parameters.
    """
    params = {"chat_id": chat_id} if chat_id else None
    try:
        task = client.post(f"{CHAT_PATH}/{agent_id}/call", json_body=payload, params=params)
    except AlationError as err:
        if err.status == 413:
            raise AgentRunError(
                "413 — input exceeded the model's context window. Chunk the input "
                "(for BCBS 239, send one principle at a time)."
            ) from err
        if err.status == 402:
            raise AgentRunError("402 — tool-call quota exceeded on this instance.") from err
        if err.status == 409:
            raise AgentRunError("409 — chat is busy. Start a new chat_id or wait.") from err
        raise

    task_id = task.get("task_id") if isinstance(task, dict) else None
    if not task_id:
        # Some deployments answer synchronously; pass it straight back.
        return task if isinstance(task, dict) else {"raw": task}

    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        result = client.get(f"{TASK_PATH}/{task_id}")
        status = str(result.get("status") or result.get("state") or "").lower()
        if verbose:
            print(f"  task {task_id} status={status or 'unknown'}")
        if status in _TERMINAL_OK:
            return result
        if status in _TERMINAL_BAD:
            raise AgentRunError(f"Agent run failed: {result}")
        time.sleep(poll_interval)

    raise AgentRunError(f"Agent run did not finish within {timeout_sec}s (task {task_id})")


def extract_text(result: dict) -> str:
    """Best-effort pull of the assistant's text out of a task result.

    The exact response shape is not fully documented; this checks the likely
    keys and falls back to returning the whole thing so nothing is silently
    lost. Tighten this once you have seen real responses from your instance.
    """
    for key in ("output", "response", "result", "content", "message", "answer"):
        val = result.get(key)
        if isinstance(val, str) and val.strip():
            return val
        if isinstance(val, dict):
            nested = extract_text(val)
            if nested:
                return nested
        if isinstance(val, list) and val:
            parts = [p if isinstance(p, str) else extract_text(p) for p in val if p]
            joined = "\n".join(p for p in parts if p)
            if joined.strip():
                return joined
    return ""
