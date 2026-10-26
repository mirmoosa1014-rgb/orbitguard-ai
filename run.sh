#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then echo 'Install first: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt'; exit 1; fi
if [[ ! -d frontend/node_modules ]]; then echo 'Install frontend: cd frontend && npm ci'; exit 1; fi
.venv/bin/python -m uvicorn orbitguard.api:app --host 127.0.0.1 --port 8102 &
api_pid=$!
trap 'kill "$api_pid" 2>/dev/null || true' EXIT INT TERM
npm --prefix frontend run dev
