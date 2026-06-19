#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm is required but was not found."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found."
  exit 1
fi

cd "$ROOT_DIR"

if [ ! -d node_modules ]; then
  echo "[start] Installing frontend dependencies..."
  pnpm install
fi

if [ -d "$BACKEND_DIR" ]; then
  if [ ! -f "$BACKEND_DIR/.env" ] && [ -f "$BACKEND_DIR/.env.example" ]; then
    echo "[start] Creating backend/.env from .env.example..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
  fi

  echo "[start] Ensuring backend dependencies are installed..."
  python3 -m pip install -r "$BACKEND_DIR/requirements.txt"
fi

echo
echo "[start] Frontend: http://127.0.0.1:5173"
echo "[start] Backend CLI example:"
echo "        cd \"$BACKEND_DIR\" && ./run_cli.sh \"Analyze NVDA\""
echo

pnpm dev --host 127.0.0.1
