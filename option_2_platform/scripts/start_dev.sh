#!/usr/bin/env bash
set -euo pipefail

# Dev start helper: frees port 8000, ensures deps installed, starts uvicorn with proper PYTHONPATH
cd "$(dirname "$0")/.."
ROOT_DIR="$PWD"
PORT=8000

# 1) Kill old uvicorn on port
if lsof -n -iTCP:${PORT} -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Killing process on port ${PORT}..."
  lsof -n -iTCP:${PORT} -sTCP:LISTEN | awk 'NR>1{print $2}' | xargs -r kill -9
fi

# 2) Ensure venv & deps
if [ ! -d .venv ]; then
  uv venv
fi
uv sync

# 3) Start server with explicit app-dir and PYTHONPATH
export PYTHONPATH="${ROOT_DIR}/src"
exec uv run uvicorn src.api.main:app --app-dir "${ROOT_DIR}" --host 127.0.0.1 --port ${PORT} --reload
