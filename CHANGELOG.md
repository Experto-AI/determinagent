# Changelog

All notable changes to DeterminAgent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Alpha Status Unification**: Updated all provider adapters (Claude, Copilot, Gemini, Codex) to Alpha version across documentation for consistency.
- **Documentation SSOT**: Implemented Single Source of Truth pattern for documentation using `mkdocs-include-markdown-plugin`
- **Documentation Wrappers**: Created minimal wrapper files in `docs/` directory that include root markdown files
- **Documentation Navigation**: Added PLAN and Release Checklist pages to mkdocs navigation

### Changed
- **Documentation Structure**: Refactored to eliminate duplicate documentation files between root and `docs/` folder
- **Documentation Links**: Updated cross-file references in CONTRIBUTING.md to use proper markdown file paths

### Fixed
- **Documentation Build**: Resolved all link warnings in documentation build process
- **Documentation Sync**: Eliminated manual sync issues by using include-markdown plugin

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


