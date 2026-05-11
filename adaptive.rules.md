---
domain: root
merge_strategy: append
---

# Shared

- **Project purpose**:
    - DeterminAgent is a Python library for CLI-first deterministic multi-agent orchestration.
    - It wraps AI CLI tools (Claude Code, Copilot CLI, Gemini CLI, OpenAI Codex) via subprocess and uses LangGraph for graph-based pipelines.
    - Zero additional cost by leveraging flat-rate CLI subscriptions (no per-token API charges).
- **Repository SSOT**:
    - `README.md` is authoritative for project purpose, installation, and quickstart.
    - `ARCHITECTURE.md` is authoritative for design principles, component layout, and system design.
    - `CHANGELOG.md` is authoritative for version history and release notes.
    - `CONTRIBUTING.md` is authoritative for contributor workflow, coding standards, and release process.
    - `pyproject.toml` is authoritative for package metadata, dependencies, and tool configuration.
- **Primary repository shape**:
    - `determinagent/` — core library: `agent.py` (UnifiedAgent), `adapters/` (Claude, Copilot, Gemini, Codex), `sessions.py`, `config.py`, `parsers.py`, `validation.py`, `utils.py`, `ui.py`, `cli_utils.py`, `constants.py`, `exceptions.py`.
    - `flows/` — pre-built Python workflow scripts for common use cases.
    - `tests/` — pytest test suite with 90%+ coverage threshold.
    - `scripts/` — development helper scripts (lint, test, build, docs, version bump).
    - `docs/` — MkDocs documentation source.
- **Core ownership boundaries**:
    - `determinagent/agent.py` owns the `UnifiedAgent` public API.
    - `determinagent/adapters/` owns all provider-specific subprocess integration.
    - `determinagent/sessions.py` owns session lifecycle.
    - `determinagent/config.py` owns YAML config loading and auto-discovery.
    - `determinagent/parsers.py` owns structured output parsing.
    - `determinagent/validation.py` owns input/output validation.
- **Cross-cutting rules**:
    - The Strict Output Pattern must be preserved in all prompt templates: prompts must instruct agents to start directly with content and omit meta-commentary.
    - Only Claude supports deterministic custom session IDs (`--session-id`); all other providers generate IDs internally and are treated as non-deterministic for session orchestration.
    - All public APIs use Pydantic models and strict type hints.
    - Test coverage must remain at or above 90%.

# Adaptive
[include](#shared)

# Plan
[include](#shared)

# Codebase Discovery
[include](#shared)

# External Research
[include](#shared)

# Implement
[include](#shared)

# Quality Gate
[include](#shared)
- **Validation policy**: run `make test` (pytest, 90% coverage threshold), `make lint` (ruff), `make typecheck` (mypy), `make security` (bandit, pip-audit).
- **Required commands before deploy**: `make test`.

# Change Review
[include](#shared)
