#!/usr/bin/env bash
# Run linting with Ruff
# Usage: ./scripts/lint.sh [--fix]

set -e

echo "🔍 Running Ruff linter..."

if [ "$1" == "--fix" ]; then
    echo "   (with auto-fix enabled)"
    python -m ruff check determinagent tests --fix
    python -m ruff format determinagent tests
else
    python -m ruff check determinagent tests
    python -m ruff format --check determinagent tests
fi

echo "✅ Linting passed!"
