#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Backend checks"
cd backend
if command -v uv >/dev/null 2>&1; then
  uv run ruff check .
  uv run pytest
else
  .venv/bin/ruff check .
  .venv/bin/pytest
fi

echo "Frontend checks"
cd ../frontend
npm run lint
npm run test
npm run build
