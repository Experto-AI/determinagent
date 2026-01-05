#!/usr/bin/env bash
# Run all quality checks (lint, typecheck, test)
# Usage: ./scripts/check-all.sh

set -e

echo "🔧 Running all quality checks..."
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run linting
"$SCRIPT_DIR/lint.sh"
echo ""

# Run type checking
"$SCRIPT_DIR/typecheck.sh"
echo ""

# Run tests
"$SCRIPT_DIR/test.sh"
echo ""

echo "🎉 All checks passed!"
