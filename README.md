# DeterminAgent

**CLI-First Deterministic Multi-Agent Orchestration Library**

[![PyPI version](https://img.shields.io/pypi/v/determinagent.svg)](https://pypi.org/project/determinagent/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Coverage](https://img.shields.io/badge/coverage-90%25-green.svg)](https://github.com/Experto-AI/determinagent)

> **Orchestrate powerful AI workflows at zero extra cost.** DeterminAgent controls multiple AI CLI tools (Claude Code, Copilot CLI, Gemini CLI, OpenAI Codex) using LangGraph to create deterministic pipelines powered by your existing flat-rate subscriptions.

---

## 🚀 First Contact

DeterminAgent is a **Python library** for developers who want to build complex, multi-agent systems without paying for expensive per-token API calls. By wrapping the CLI tools you already pay for, DeterminAgent allows you to build production-grade workflows for $0 in variable costs.

### Key Features
- **Library-Only**: Full control in pure Python. No proprietary YAML DSL.
- **Subscription Arbitrage**: Uses your flat-rate CLI subscriptions.
- **Deterministic**: Powered by LangGraph state machines.
- **Zero-Latency**: Controls local tools via subprocess.

---

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install determinagent
```

### From Source

For the latest development version or to contribute:

```bash
# Clone the repository
git clone https://github.com/Experto-AI/determinagent.git
cd determinagent

# Install dependencies and set up environment
poetry install

# Verify installation
poetry run python -c "import determinagent; print(determinagent.__version__)"
```

### Prerequisites

- **Python 3.10+**
- **At least one supported AI CLI tool** installed and authenticated:
  - [Claude Code](https://claude.ai/code) (`claude`)
  - [Copilot CLI](https://github.com/features/copilot/cli) (`copilot`)
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli) (`gemini`)
  - [OpenAI Codex](https://openai.com/codex) (`codex`)

---

## ⚡ Quick Start

### Library Usage

```python
from determinagent import UnifiedAgent, SessionManager

# Create a deterministic agent
writer = UnifiedAgent(
    provider="claude",
    model="balanced",
    role="Technical Blogger",
    session=SessionManager("claude")
)

# Send a prompt - zero per-token cost!
response = writer.send("Explain LangGraph in 3 sentences.")
print(response)
```

### Template Flows
Don't start from scratch. Use our pre-built Python templates in the `flows/` directory:
- `flows/blog/`: Complete Writer → Editor → Reviewer workflow with human review.

To run the blog flow:
```bash
python flows/blog/main.py "My Blog Topic" --writer claude --editor copilot
```

---

## 🧩 Compatibility Matrix

| Provider | Adapter Status | Session Support | Web Search | Model Aliases |
| :--- | :--- | :--- | :--- | :--- |
| **Claude Code** | ✅ Alpha | ✅ Native | ✅ Yes | fast, balanced, powerful, reasoning, free |
| **Copilot CLI** | ✅ Alpha | ✅ Native | ✅ Yes | fast, balanced, powerful, reasoning, free |
| **Gemini CLI** | ✅ Alpha | ✅ Native | ✅ Yes | fast, balanced, powerful, reasoning, free |
| **OpenAI Codex**| ✅ Alpha | ✅ Native | ❌ No | fast, balanced, powerful, reasoning, free |

---

## 🎯 Model Alias Map

DeterminAgent resolves model aliases per provider so you can keep flows consistent.

| Alias | Claude Code | Gemini CLI | Copilot CLI | OpenAI Codex |
| :--- | :--- | :--- | :--- | :--- |
| fast | haiku | gemini-3-flash-preview | claude-haiku-4.5 | gpt-5.1-codex-mini |
| balanced | sonnet | gemini-3-pro-preview | claude-sonnet-4.5 | gpt-5.1-codex |
| powerful | opus | gemini-3-pro-preview | claude-opus-4.5 | gpt-5.1-codex-max |
| reasoning | opus | gemini-3-pro-preview | gpt-5.2 | gpt-5.1-codex |
| free | haiku | gemini-3-flash-preview | claude-haiku-4.5 | gpt-5.1-codex-mini |

Notes:
- You can always pass an exact model string to override the alias.
- Availability depends on your provider plan and CLI version.
- Gemini 3 preview models require enabling Preview Features in Gemini CLI; if unavailable, pass `gemini-2.5-pro` or `gemini-2.5-flash`.
- Codex CLI does not enumerate models in `--help`; defaults mirror Codex model names exposed by Copilot CLI.

---

## 🛠️ Troubleshooting

### Common Issues

1. **`ProviderNotAvailable: CLI command 'claude' not found`**
   - Ensure the tool is installed and available in your `$PATH`.
   - Run `claude --version` manually to verify.

2. **Authentication Errors**
   - DeterminAgent uses your local sessions. Ensure you are logged in to the CLI tool (e.g., `copilot auth status` or `claude login`).

3. **Subprocess Timeouts**
   - Some agents (like Writer) can take a few minutes for long content. Ensure your environment doesn't kill long-running processes.

### Debug Mode
Set `LOG_LEVEL=DEBUG` to see the full subprocess commands and raw output.

---

## 📖 Documentation

### Core Documentation
- **[Technical Architecture](./ARCHITECTURE.md)**: Design principles and system internals.
- **[CLI Reference](./CLI-REFERENCE.md)**: Low-level flag mappings for each provider.
- **[Actionable Plan & Roadmap](./PLAN.md)**: Current status and next steps.

### API Reference
- **[UnifiedAgent](https://determinagent.github.io/determinagent/api/agent/)**: Core orchestration class.
- **[Provider Adapters](https://determinagent.github.io/determinagent/api/adapters/)**: Claude, Copilot, Gemini, Codex wrappers.
- **[SessionManager](https://determinagent.github.io/determinagent/api/sessions/)**: Conversation history management.
- **[Exceptions](https://determinagent.github.io/determinagent/api/exceptions/)**: Error handling hierarchy.

### Tutorials
- **[Your First Flow](https://determinagent.github.io/determinagent/tutorials/first_flow/)**: Step-by-step guide to building a workflow.

### Community
- **[Contributing](./CONTRIBUTING.md)**: How to help improve the project.
- **[Code of Conduct](./CODE_OF_CONDUCT.md)**: Community guidelines.
- **[Security Policy](./SECURITY.md)**: Reporting vulnerabilities.

---

## 📜 License
Apache License 2.0 - see [LICENSE](./LICENSE) for details.
