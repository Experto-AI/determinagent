# Changelog

All notable changes to DeterminAgent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Production readiness documentation (CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY)
- GitHub Issue and PR templates
- Enhanced README with installation instructions and troubleshooting

### Changed
- Improved error handling in Blog Flow (uses exception type inspection instead of string matching)

### Fixed
- Removed unused `filename_template` configuration option from Blog Flow

---

## [0.10.0] - 2026-01-03

### Added
- **Phase 6: Code Efficiency & Utilities**
  - `determinagent.ui` module for console formatting
  - `determinagent.utils` module for general utilities (`sanitize_filename`, `truncate_id`)
  - `determinagent.cli_utils` module for argparse helpers
- **Phase 5: Additional Adapters**
  - Gemini CLI adapter with native session support
  - OpenAI Codex adapter with sandbox mode
- **Phase 4: Template Flows**
  - `flows/blog/` directory with complete Writer → Editor → Reviewer workflow
  - YAML configuration support for prompts and defaults
- **Phase 3: Configuration Support**
  - Optional YAML configuration loading via `determinagent.config`
  - Prompt templates externalized to YAML
- **Phase 2: Library Polish**
  - Pydantic-based type validation across all models
  - Unified exception hierarchy (`DeterminAgentError` and subclasses)
  - 90%+ test coverage with strict type checking
- **Phase 1: Core Library**
  - `UnifiedAgent` for provider-agnostic AI interaction
  - `SessionManager` for conversation history management
  - Provider adapters: Claude, Copilot, Gemini, Codex

### Changed
- Migrated from `examples/` to `flows/` directory structure
- Removed legacy CLI framework in favor of library-only approach

### Removed
- Global CLI entry point (replaced by template flows)
- Legacy framework components

---

## [0.1.0] - 2025-12-15

### Added
- Initial prototype with Claude and Copilot adapters
- Basic workflow orchestration using LangGraph
- Proof-of-concept blog generation workflow

---

[Unreleased]: https://github.com/determinagent/determinagent/compare/v0.10.0...HEAD
[0.10.0]: https://github.com/determinagent/determinagent/compare/v0.1.0...v0.10.0
[0.1.0]: https://github.com/determinagent/determinagent/releases/tag/v0.1.0
