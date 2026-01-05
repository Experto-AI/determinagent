#!/usr/bin/env bash
# Development environment setup script
# Tested on: Linux, macOS, WSL
# Usage: ./scripts/setup.sh

set -e

echo "🔧 Setting up DeterminAgent development environment with Poetry..."

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install it first: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run commands in the environment, use:"
echo "  poetry run <command>"
echo "Or activate the environment with:"
echo "  poetry shell"
echo ""
echo "Available commands:"
echo "  make test      - Run tests"
echo "  make lint      - Run linting"
echo "  make typecheck - Run type checking"
echo "  make check     - Run all checks"
