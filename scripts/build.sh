#!/usr/bin/env bash
# Build package for distribution
# Usage: ./scripts/build.sh

set -e

echo "📦 Building package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build sdist and wheel
poetry build

echo ""
echo "✅ Build complete! Artifacts in dist/"
ls -la dist/
