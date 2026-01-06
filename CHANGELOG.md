# Changelog

All notable changes to DeterminAgent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.14.0] - 2026-01-06

### Changed
- **Codex Support**: Updated 'reasoning' model alias for OpenAI Codex to `gpt-5.1-codex-max`.
- **Documentation**: Updated Compatibility Matrix to reflect accurate session and web search support.
- **Documentation**: Integrated blog flow diagrams into README and documentation site.

---

## [0.13.0] - 2026-01-06

### Added
- **Gemini 3 Support**: Updated model aliases to support `gemini-3-flash-preview` and `gemini-3-pro-preview`.
- **Coverage Enforcement**: Added `scripts/check_coverage.py` to enforce strict 90% total and 80% per-file test coverage thresholds.
- **Provider Validation**: Implemented comprehensive provider validation logic to ensure CLI tools are correctly installed and configured before use.
- **Architecture Diagrams**: Added detailed architecture diagrams to documentation.
- **Alpha Status Unification**: Updated all provider adapters (Claude, Copilot, Gemini, Codex) to Alpha version across documentation.
- **Documentation SSOT**: Implemented Single Source of Truth pattern using `mkdocs-include-markdown-plugin`.
- **Documentation Wrappers**: Created wrapper files for root markdown documents in `docs/`.

### Changed
- **Session Management**: Refactored Gemini, Copilot, and Codex adapters to use stateless sessions (native session limitations prevented reliable resume).
- **Documentation Structure**: Refactored to eliminate duplicate documentation files.
- **Documentation Links**: Fixed cross-file references in all markdown files.

### Fixed
- **Session Recovery**: Added automatic session reset and retry logic for corrupted session files (e.g., Copilot).
- **Blog Flow**: Fixed output normalization issues in the blog writing workflow.
- **Documentation Build**: Resolved link warnings and sync issues.

---

## [0.11.0] - 2026-01-04

### Added
- Enhanced GitHub project URL documentation

### Changed
- Migrated from Hatch/venv to Poetry for unified dependency management

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


