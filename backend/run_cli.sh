#!/usr/bin/env bash
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONWARNINGS="ignore"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found."
  exit 1
fi

cd "$BACKEND_DIR"

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  echo "[run_cli] Creating .env from .env.example..."
  cp ".env.example" ".env"
fi

if ! python3 -c "import langgraph, langchain, langchain_openai, pydantic, yfinance, pandas, numpy, dotenv, rich" >/dev/null 2>&1; then
  echo "[run_cli] Installing backend dependencies..."
  python3 -m pip install -r requirements.txt
fi

run_cli() {
  python3 -W ignore -m app.main_cli "$@" \
    2> >(grep -v "LangChainPendingDeprecationWarning" | grep -v "from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer" >&2)
}

if [ "$#" -eq 0 ]; then
  run_cli
else
  run_cli "$*"
fi
