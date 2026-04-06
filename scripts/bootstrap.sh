#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv || true
source .venv/bin/activate
python -m pip install --upgrade pip wheel

echo "Bootstrap complete."
echo "Copy .env.example to .env and run: make up"
