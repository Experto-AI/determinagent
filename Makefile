# DeterminAgent Makefile
# Cross-platform development commands
# 
# Primary target: Linux/WSL
# Secondary: Windows (via WSL or Git Bash)
#
# Usage:
#   make setup     - Initialize Poetry environment and dependencies
#   make test      - Run tests (via poetry run)
#   make lint      - Run linting (via poetry run)
#   make typecheck - Run type checking (via poetry run)
#   make security  - Run security scans
#   make check     - Run all checks
#   make env-check - Verify environment and tools
#   make verify-integrations - Run interactive integration verification
#   make build     - Build distribution package

.PHONY: setup test test-cov lint lint-fix typecheck security check env-check verify-integrations docs-build docs-serve build clean help version-check bump-version

# Default Python command
PYTHON ?= poetry run python

help:
	@echo "DeterminAgent Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup                - Initialize Poetry environment and dependencies"
	@echo "  make env-check            - Verify local environment and CLI tools"
	@echo ""
	@echo "Quality Checks (via poetry run):"
	@echo "  make test                 - Run tests"
	@echo "  make test-cov             - Run tests with coverage (90% threshold)"
	@echo "  make lint                 - Check linting (no changes)"
	@echo "  make lint-fix             - Fix linting issues"
	@echo "  make typecheck            - Run type checking"
	@echo "  make security             - Run security scans (bandit, pip-audit)"
	@echo "  make check                - Run all checks"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs-build           - Build documentation (with link checking)"
	@echo "  make docs-serve           - Serve documentation locally"
	@echo ""
	@echo "Integration:"
	@echo "  make verify-integrations  - Run interactive pre-release integration checks"
	@echo ""
	@echo "Release:"
	@echo "  make version-check        - Verify version sync across files"
	@echo "  make build                - Build distribution package"
	@echo "  make clean                - Remove build artifacts"

# Setup development environment
setup:
	@poetry install

# Verify environment
env-check:
	@$(PYTHON) scripts/check_env.py

# Documentation
docs-build:
	@./scripts/docs.sh build

docs-serve:
	@./scripts/docs.sh serve $(filter-out $@,$(MAKECMDGOALS))

# Catch-all target to allow positional arguments (like port numbers)
%:
	@:

# Run tests
test:
	@$(PYTHON) -m pytest tests/ -v --tb=short

# Run tests with coverage (strict 90% threshold)
test-cov:
	@$(PYTHON) -m pytest tests/ -v --cov=determinagent --cov-report=term-missing --cov-report=html --cov-fail-under=90
	@echo "📊 Coverage report: htmlcov/index.html"

# Run linting (check only)
lint:
	@$(PYTHON) -m ruff check determinagent tests flows
	@$(PYTHON) -m ruff format --check determinagent tests flows
	@echo "✅ Linting passed!"

# Run linting with auto-fix
lint-fix:
	@$(PYTHON) -m ruff check determinagent tests flows --fix
	@$(PYTHON) -m ruff format determinagent tests flows
	@echo "✅ Linting fixed!"

# Run type checking
typecheck:
	@$(PYTHON) -m mypy determinagent flows --show-error-codes
	@echo "✅ Type checking passed!"

# Run security scans
security:
	@echo "🔒 Running Bandit security linter..."
	@$(PYTHON) -m bandit -r determinagent -c pyproject.toml || (echo "❌ Bandit found issues" && exit 1)
	@echo ""
	@echo "🔒 Running pip-audit dependency check..."
	@poetry run pip-audit --desc on || (echo "⚠️ pip-audit found vulnerabilities" && exit 0)
	@echo "✅ Security scan passed!"

# Run all checks
check: lint typecheck security test
	@echo ""
	@echo "🎉 All checks passed!"

# Verify version sync
version-check:
	@$(PYTHON) scripts/bump_version.py --check

# Bump version
bump-version:
	@$(PYTHON) scripts/bump_version.py $(filter-out $@,$(MAKECMDGOALS))

# Verify integrations (Interactive)
verify-integrations:
	@./scripts/verify_integrations.sh

# Build distribution
build:
	@rm -rf dist/ build/ *.egg-info/
	@poetry build
	@echo "✅ Build complete! See dist/"

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned!"
