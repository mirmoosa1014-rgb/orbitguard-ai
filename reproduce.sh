#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
.venv/bin/python -m orbitguard.experiment --full
.venv/bin/python -m orbitguard.visuals
.venv/bin/python -m orbitguard.animation
.venv/bin/python -m pytest -q
npm --prefix frontend run build
