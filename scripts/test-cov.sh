#!/usr/bin/env bash
# Run tests with coverage report
# Usage: ./scripts/test-cov.sh

set -e

echo "🧪 Running tests with coverage..."

python -m pytest tests/ -v --cov=determinagent --cov-report=term-missing --cov-report=html

echo ""
echo "📊 Coverage report generated in htmlcov/"
