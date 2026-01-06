#!/usr/bin/env bash
# Run tests with coverage report
# Usage: ./scripts/test-cov.sh

set -e

echo "🧪 Running tests with coverage..."

python -m pytest tests/ -v --cov=determinagent --cov-report=term-missing --cov-report=html --cov-report=json

python scripts/check_coverage.py --total 90 --file 80

echo ""
echo "📊 Coverage report generated in htmlcov/"
