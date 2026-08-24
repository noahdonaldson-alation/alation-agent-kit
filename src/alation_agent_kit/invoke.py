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

import json
import time
from pathlib import Path
from typing import Any

from .client import AI_V1, AlationClient, AlationError

CHAT_PATH = f"{AI_V1}/chats/agent"
TASK_PATH = f"{AI_V1}/task"

_TERMINAL_OK = {"succeeded", "success", "completed", "complete", "done", "finished"}
_TERMINAL_BAD = {"failed", "error", "cancelled", "canceled"}


class AgentRunError(RuntimeError):
    pass


_TEXT_KEYS = ("text", "delta", "content", "message", "output", "answer", "chunk")

# Keys that carry the request back to us. Harvesting these re-collects the whole
# input on every event — which turned a 30KB answer into a 28MB file once.
_ECHO_KEYS = ("input", "request", "user", "prompt", "history", "messages", "payload")


def _harvest_text(obj: Any, acc: list[str], echo: set[str] | None = None) -> None:
    """Collect text-ish values out of an SSE event of unknown shape.

    The event schema is undocumented, so walk the structure and pick up strings
    under keys that plausibly carry model output — while skipping branches that
    echo the request back, and dropping anything that matches what we sent.
    """
    echo = echo or set()
    if isinstance(obj, str):
        s = obj.strip()
        if s and s not in echo and not any(s in e for e in echo):
            acc.append(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            kl = k.lower()
            if any(e in kl for e in _ECHO_KEYS):
                continue  # request echo, not model output
            if kl in _TEXT_KEYS or kl.endswith("_text"):
                _harvest_text(v, acc, echo)
            elif isinstance(v, (dict, list)):
                _harvest_text(v, acc, echo)
    elif isinstance(obj, list):
        for v in obj:
            _harvest_text(v, acc, echo)


def _assemble(pieces: list[str]) -> str:
    """Turn harvested pieces into one answer, tolerating either streaming style.

    Some APIs send incremental deltas (concatenate them); others resend the whole
    answer each event (take the longest). Detect which by comparing the longest
    single piece against the naive concatenation.
    """
    if not pieces:
        return ""

    # Do NOT drop repeated identical pieces: a model can legitimately emit the
    # same delta twice, and dropping them silently corrupts the answer.
    #
    # Cumulative style is detected by a piece being STRICTLY LONGER than the
    # previous one while extending it. The strictness matters — every string
    # starts with itself, so a loose prefix test would swallow identical deltas.
    collapsed: list[str] = []
    for p in pieces:
        if collapsed and len(p) > len(collapsed[-1]) and p.startswith(collapsed[-1]):
            collapsed[-1] = p
        else:
            collapsed.append(p)

    joined = "".join(pieces)
    result = "".join(collapsed)

    # Last resort: if a single piece already carries nearly everything, the
    # stream was sending whole answers and concatenating would duplicate.
    longest = max(pieces, key=len)
    if len(longest) > 0.9 * len(result) and len(collapsed) > 1:
        return longest
    return result if len(result) <= len(joined) else joined


def run_agent_stream(
    client: AlationClient,
    agent_id: str,
    payload: dict[str, Any],
    chat_id: str | None = None,
    verbose: bool = False,
    raw_path: str | None = None,
) -> str:
    """Invoke an agent over SSE and return the accumulated text.

    Preferred over run_agent(): the task-polling endpoint deletes tasks on
    success, so a completed run 404s.
    """
    path = f"{CHAT_PATH}/{agent_id}/stream"
    if chat_id:
        path += f"?chat_id={chat_id}"

    # Everything we sent, so it can be filtered out of the response if the
    # stream echoes the request back.
    echo = {v.strip() for v in payload.values() if isinstance(v, str) and len(v.strip()) > 40}

    raw_lines: list[str] = []
    pieces: list[str] = []
    try:
        for line in client.stream_lines(path, json_body=payload):
            if line is None:
                continue
            raw_lines.append(line)
            if verbose and line.strip():
                print(f"  | {line[:160]}")
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if not data or data == "[DONE]":
                continue
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                if data.strip() not in echo:
                    pieces.append(data)
                continue
            _harvest_text(event, pieces, echo)
    except AlationError as err:
        if err.status == 413:
            raise AgentRunError(
                "413 — input exceeded the model's context window. Send less text."
            ) from err
        if err.status == 402:
            raise AgentRunError("402 — tool-call quota exceeded on this instance.") from err
        raise

    if raw_path:
        Path(raw_path).parent.mkdir(parents=True, exist_ok=True)
        Path(raw_path).write_text("\n".join(raw_lines), encoding="utf-8")

    text = _assemble(pieces)

    # A response many times the size of the input almost certainly means the
    # parser duplicated. Fail loudly rather than write a 28MB file.
    sent = sum(len(v) for v in payload.values() if isinstance(v, str)) or 1
    if len(text) > max(200_000, sent * 6):
        raise AgentRunError(
            f"Assembled response is {len(text):,} chars against {sent:,} sent — the "
            f"stream parser is almost certainly duplicating. Re-run with `--raw -o <file>` "
            f"and inspect the raw SSE to fix the event shape."
        )

    if not text.strip():
        raise AgentRunError(
            "Stream produced no text. The event shape is undocumented — re-run with "
            "--raw to dump the stream and we can adjust the parser."
        )
    return text


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
        try:
            result = client.get(f"{TASK_PATH}/{task_id}")
        except AlationError as err:
            # "Successfully completed tasks are deleted" — a 404 here usually
            # means the run finished before we polled, not that it failed. The
            # output is gone with the task, so there is nothing to return.
            if err.status == 404:
                raise AgentRunError(
                    "Task finished and was deleted before its result could be read. "
                    "Use the streaming path (run_agent_stream) instead — polling "
                    "cannot reliably retrieve output from this API."
                ) from err
            raise
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
