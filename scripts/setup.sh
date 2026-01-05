#!/usr/bin/env bash
# Development environment setup script
# Tested on: Linux, macOS, WSL
# Usage: ./scripts/setup.sh

set -e

echo "🔧 Setting up DeterminAgent development environment..."

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.10"

if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required (found: $PYTHON_VERSION)"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install package in editable mode with dev dependencies
echo "📦 Installing package with dev dependencies..."
pip install -e ".[dev]"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "Available commands:"
echo "  ./scripts/test.sh      - Run tests"
echo "  ./scripts/lint.sh      - Run linting"
echo "  ./scripts/typecheck.sh - Run type checking"
echo "  ./scripts/check-all.sh - Run all checks"
