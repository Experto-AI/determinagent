#!/usr/bin/env bash
# Build package for distribution
# Usage: ./scripts/build.sh

set -e

echo "📦 Building package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build sdist and wheel
python -m pip install --upgrade build
python -m build

echo ""
echo "✅ Build complete! Artifacts in dist/"
ls -la dist/
