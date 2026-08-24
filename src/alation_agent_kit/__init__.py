"""alation-agent-kit — git-backed dev/deploy kit for Alation Agent Studio."""

__version__ = "0.1.0"

from .agents import AgentStudio
from .auth import Settings, TokenProvider, load_dotenv
from .client import AI_V1, AlationClient, AlationError
from .invoke import extract_text, run_agent
from .prompts import Prompt, load_prompt
from .store import Lockfile, canonicalize_agent, read_json, write_json

__all__ = [
    "AI_V1",
    "AgentStudio",
    "AlationClient",
    "AlationError",
    "Lockfile",
    "Prompt",
    "Settings",
    "TokenProvider",
    "canonicalize_agent",
    "extract_text",
    "load_dotenv",
    "load_prompt",
    "read_json",
    "run_agent",
    "write_json",
]
