#!/usr/bin/env bash
# Run type checking with Mypy
# Usage: ./scripts/typecheck.sh

set -e

echo "🔬 Running Mypy type checker..."

poetry run mypy determinagent --show-error-codes

echo "✅ Type checking passed!"
