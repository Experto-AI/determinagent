# Contributing to DeterminAgent

Thank you for your interest in contributing to DeterminAgent! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)
- [Testing Standards](#testing-standards)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the maintainers.

---

## Getting Started

### Prerequisites

- **Python 3.10+** (3.11 or 3.12 recommended)
- **Git** for version control
- At least one supported CLI tool installed:
  - [Claude Code](https://claude.ai/code) (`claude`)
  - [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli/) (`gh copilot`)
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli) (`gemini`)
  - [OpenAI Codex](https://openai.com/codex) (`codex`)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/determinagent.git
   cd determinagent
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/determinagent/determinagent.git
   ```

---

## Development Setup

### Install Dependencies

```bash
# Install package with development dependencies using Poetry
poetry install

# Optionally activate the Poetry shell
poetry shell
```

### Verify Setup

```bash
# Run all quality checks
make check

# Or run individually:
make lint       # Linting with ruff
make typecheck  # Type checking with mypy
make test       # Unit tests with pytest
```

---

## Making Changes

### Branch Naming

Create a descriptive branch from `main`:

```bash
git checkout main
git pull upstream main
git checkout -b <type>/<short-description>
```

**Branch types:**
- `feature/` - New functionality
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

**Examples:**
- `feature/openai-adapter`
- `fix/session-timeout`
- `docs/api-reference`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**
```
feat(adapters): add support for Anthropic Claude API
fix(sessions): handle timeout errors gracefully
docs(readme): add installation instructions
```

---

## Pull Request Process

### Before Submitting

1. **Update from upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks:**
   ```bash
   make check
   ```
   All checks must pass:
   - ✅ Linting (ruff)
   - ✅ Type checking (mypy)
   - ✅ Unit tests (pytest)
   - ✅ Coverage ≥ 70% per file

3. **Update documentation** if needed

### Submitting

1. Push your branch:
   ```bash
   git push origin <branch-name>
   ```

2. Open a Pull Request against `main`

3. Fill out the PR template completely

4. Request review from maintainers

### Review Process

- PRs require at least one maintainer approval
- Address all review comments
- Keep the PR focused (one feature/fix per PR)
- Squash commits if requested

---

## Style Guide

### Python Code

We use **Ruff** for linting and **Black** for formatting:

```bash
# Auto-fix linting issues
make lint-fix

# Check formatting
ruff format --check determinagent/ flows/ tests/
```

**Key conventions:**
- Line length: 100 characters
- Use type hints for all function signatures
- Use docstrings for all public APIs (Google style)
- Prefer f-strings over `.format()` or `%`

### Docstrings

```python
def send(self, prompt: str, allow_web: bool = False) -> str:
    """
    Send a prompt to the AI provider and return the response.

    Args:
        prompt: The user prompt to send.
        allow_web: Whether to allow web search for context.

    Returns:
        The AI-generated response text.

    Raises:
        ProviderNotAvailable: If the CLI tool is not installed.
        ProviderError: If the provider returns an error.
    """
```

---

## Testing Standards

### Test Structure

We follow the **ZOMBIES** testing approach and **AAA** (Arrange-Act-Assert) pattern:

```python
def test_send_prompt_valid_input_returns_response():
    """Test that send() returns a response for valid input."""
    # Arrange
    agent = UnifiedAgent(provider="claude", model="balanced")
    prompt = "Hello, world!"

    # Act
    with patch.object(agent, '_execute_cli', return_value="Hi there!"):
        result = agent.send(prompt)

    # Assert
    assert result == "Hi there!"
```

### Naming Convention

```
test_<function_name>_<scenario>_<expected_result>
```

**Examples:**
- `test_send_empty_prompt_raises_validation_error`
- `test_parse_review_valid_format_returns_scores`
- `test_session_expired_creates_new_session`

### Coverage Requirements

- **Minimum 70% coverage per file**
- Run with coverage report:
  ```bash
  make test-cov
  ```

---

## Versioning Policy

DeterminAgent follows [Semantic Versioning 2.0.0](https://semver.org/) (SemVer).

### Version Format: `MAJOR.MINOR.PATCH`

- **MAJOR** (e.g., 1.0.0 → 2.0.0): Breaking changes to public API
  - Removing or renaming public classes, methods, or functions
  - Changing method signatures in incompatible ways
  - Removing support for a Python version

- **MINOR** (e.g., 1.0.0 → 1.1.0): New features, backwards compatible
  - Adding new adapters, methods, or configuration options
  - Deprecating (but not removing) existing functionality
  - Adding support for new CLI tools

- **PATCH** (e.g., 1.0.0 → 1.0.1): Bug fixes, backwards compatible
  - Fixing bugs without changing public API
  - Documentation updates
  - Performance improvements

### API Stability

The following are considered **public API** and follow SemVer:
- All exports from `determinagent/__init__.py`
- All public classes: `UnifiedAgent`, `SessionManager`, `ProviderAdapter`
- All public functions: `get_adapter`, `load_config`, `parse_review`
- Exception hierarchy: `DeterminAgentError` and subclasses
- Type aliases: `Provider`, `Model`

The following are **internal** and may change without notice:
- Private methods (prefixed with `_`)
- Module internals not exported via `__init__.py`
- Test utilities and fixtures

### Pre-release Versions

- **Alpha** (e.g., `1.0.0-alpha.1`): Experimental, API may change
- **Beta** (e.g., `1.0.0-beta.1`): Feature complete, API stabilizing
- **Release Candidate** (e.g., `1.0.0-rc.1`): Ready for release, final testing

---

## Reporting Issues

### Bug Reports

Use the **Bug Report** issue template and include:
- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
- Error messages and tracebacks
- Relevant configuration

### Feature Requests

Use the **Feature Request** issue template and include:
- Use case description
- Proposed solution
- Alternative approaches considered

### Security Issues

**Do not** open public issues for security vulnerabilities. See [SECURITY.md](./SECURITY.md) for responsible disclosure.

---

## Questions?

- Check existing [Issues](https://github.com/determinagent/determinagent/issues)
- Open a [Discussion](https://github.com/determinagent/determinagent/discussions)
- Read the [Architecture](./ARCHITECTURE.md) documentation

Thank you for contributing! 🎉
