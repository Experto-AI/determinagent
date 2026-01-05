#!/usr/bin/env bash
# Run tests
# Usage: ./scripts/test.sh [pytest-args]

set -e

echo "🧪 Running tests..."

# Run pytest with coverage
poetry run pytest tests/ -v --tb=short "$@"
