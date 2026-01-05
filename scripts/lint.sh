#!/usr/bin/env bash
# Run linting with Ruff
# Usage: ./scripts/lint.sh [--fix]

set -e

echo "🔍 Running Ruff linter..."

if [ "$1" == "--fix" ]; then
    echo "   (with auto-fix enabled)"
    poetry run ruff check determinagent tests --fix
    poetry run ruff format determinagent tests
else
    poetry run ruff check determinagent tests
    poetry run ruff format --check determinagent tests
fi

echo "✅ Linting passed!"
