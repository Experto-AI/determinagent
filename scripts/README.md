# Development Scripts

Development tools for DeterminAgent. Run all scripts from the **project root**.

## Prerequisites

- Python 3.10+
- Virtual environment recommended

## Scripts

### `setup.sh`
Initialize dev environment: creates venv, installs dependencies with dev extras.
```bash
./scripts/setup.sh
source venv/bin/activate
```

### `test.sh`
Run test suite with pytest. Accepts additional pytest arguments.
```bash
./scripts/test.sh              # All tests
./scripts/test.sh tests/test_flow_loader.py  # Specific file
```

### `test-cov.sh`
Run tests with coverage report. Generates HTML report in `htmlcov/`.
```bash
./scripts/test-cov.sh
```

### `lint.sh`
Check code style with Ruff. Use `--fix` to auto-format.
```bash
./scripts/lint.sh              # Check only
./scripts/lint.sh --fix        # Fix issues
```

### `typecheck.sh`
Run Mypy type checker in strict mode.
```bash
./scripts/typecheck.sh
```

### `check-all.sh`
Run complete QA pipeline: lint → typecheck → tests. Use before commits.
```bash
./scripts/check-all.sh
```

### `build.sh`
Build distribution packages (sdist + wheel) in `dist/`.
```bash
./scripts/build.sh
```

### `verify_integrations.sh`
Pre-release verification of CLI tool integrations. Checks availability and authentication of Claude, Copilot, Gemini, and Codex CLIs.
```bash
./scripts/verify_integrations.sh          # Full verification (interactive)
./scripts/verify_integrations.sh --quick  # Quick mode (version checks only)
```

## Common Workflows

```bash
# Daily development
./scripts/lint.sh --fix && ./scripts/test.sh

# Pre-commit
./scripts/check-all.sh

# Pre-release
./scripts/check-all.sh && ./scripts/test-cov.sh && ./scripts/verify_integrations.sh --quick && ./scripts/build.sh
```

## Makefile Integration

Also available via make:
```bash
make setup      # → ./scripts/setup.sh
make test       # → ./scripts/test.sh
make lint       # → ./scripts/lint.sh
make typecheck  # → ./scripts/typecheck.sh
make check      # → ./scripts/check-all.sh
make build      # → ./scripts/build.sh
```

---

*See [PLAN.md](../PLAN.md) for roadmap and status, [ARCHITECTURE.md](../ARCHITECTURE.md) for architecture deep-dives.*
