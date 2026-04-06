#!/usr/bin/env bash
set -euo pipefail

for dir in services/*; do
  if [[ -f "$dir/pyproject.toml" ]]; then
    (cd "$dir" && python -m ruff format app tests)
  fi
done
