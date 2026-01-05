# DeterminAgent

**CLI-First Deterministic Multi-Agent Orchestration Library**

[![PyPI version](https://img.shields.io/pypi/v/determinagent.svg)](https://pypi.org/project/determinagent/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Coverage](https://img.shields.io/badge/coverage-90%25-green.svg)](https://github.com/determinagent/determinagent)

> **Orchestrate powerful AI workflows at zero extra cost.** DeterminAgent controls multiple AI CLI tools (Claude Code, GH Copilot, Gemini CLI, OpenAI Codex) using LangGraph to create deterministic pipelines powered by your existing flat-rate subscriptions.

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
git clone https://github.com/determinagent/determinagent.git
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
  - [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli/) (`gh copilot`)
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

| Provider | Adapter Status | Session Support | Web Search | Native Models |
| :--- | :--- | :--- | :--- | :--- |
| **Claude Code** | ✅ Stable | ✅ Native | ✅ Yes | fast, balanced, powerful |
| **GH Copilot** | ✅ Stable | ✅ Native | ✅ Yes | fast, balanced, powerful |
| **Gemini CLI** | ✅ Beta | ✅ Native | ✅ Yes | flash, pro |
| **OpenAI Codex**| ✅ Beta | ✅ Native | ❌ No | fast, balanced |

---

## 🛠️ Troubleshooting

### Common Issues

1. **`ProviderNotAvailable: CLI command 'claude' not found`**
   - Ensure the tool is installed and available in your `$PATH`.
   - Run `claude --version` manually to verify.

2. **Authentication Errors**
   - DeterminAgent uses your local sessions. Ensure you are logged in to the CLI tool (e.g., `gh auth status` or `claude login`).

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

