#!/usr/bin/env bash
set -euo pipefail

service="${1:-gateway}"
port="${2:-8000}"

uvicorn app.main:app --reload --host 0.0.0.0 --port "${port}"
