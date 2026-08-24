#!/usr/bin/env bash
# Bootstrap and run agentkit. Installs uv if missing (no admin, no Homebrew,
# no pre-existing Python needed), creates .venv, installs the package.
#
#   ./run.sh whoami
#   ./run.sh list agents
#   ./run.sh deploy agents/bcbs239_interpreter.json --prompt bcbs239_principle_extract --dry-run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -f .env && "${1:-}" != "--help" && "${1:-}" != "-h" ]]; then
  echo ""
  echo "No .env found. Run:"
  echo "    cp .env.example .env"
  echo "    \$EDITOR .env"
  echo ""
  echo "You need ALATION_BASE_URL plus an OAuth client ID/secret. A Server Admin"
  echo "must create the client at /admin/auth/ — it cannot be self-served."
  echo ""
  exit 1
fi

if ! command -v uv &>/dev/null; then
  if [[ -x "$HOME/.local/bin/uv" ]]; then
    export PATH="$HOME/.local/bin:$PATH"
  else
    echo "Installing uv (no admin rights required)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
  fi
fi

if [[ ! -d .venv ]]; then
  echo "Creating .venv..."
  uv venv
fi

# -e so edits to src/ take effect without reinstalling — this is a dev kit.
uv pip install --quiet -e ".[dev]"

exec .venv/bin/python -m alation_agent_kit.cli "$@"
