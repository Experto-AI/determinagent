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
   instructions="Write concise, technically accurate content.",
    session=SessionManager("claude")
)

# Send a prompt - zero per-token cost!
response = writer.send("Explain LangGraph in 3 sentences.")
print(response)
```

### Template Flows
Don't start from scratch. Use our pre-built Python templates in the `flows/` directory:
- `flows/blog/`: Complete Writer → Editor → Reviewer workflow with human review.

<img src="https://raw.githubusercontent.com/Experto-AI/determinagent/main/docs/assets/blog_flow.svg" alt="Blog Flow" width="600">

To run the blog flow:
```bash
python flows/blog/main.py "My Blog Topic" --writer claude --editor copilot
```

---

## 🧩 Compatibility Matrix

| Provider | Adapter Status | DeterminAgent Session Mode | Upstream CLI Resume | Search / Web in Upstream CLI | Current Library Surface |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Claude Code** | ✅ Alpha | ✅ Deterministic `--session-id` + `--resume` | ✅ Yes | ✅ Yes | Models, deterministic sessions, web tools, custom allowed tools |
| **Copilot CLI** | ✅ Alpha | ⚠️ Fresh session by default | ✅ Yes (provider-managed) | ✅ Yes | Models, non-interactive prompts, tool/url permission flags |
| **Gemini CLI** | ✅ Alpha | ⚠️ Fresh session by default | ✅ Yes (provider-managed) | ✅ Yes | Models, headless `--prompt`, JSON output, sandbox/tool passthrough |
| **OpenAI Codex**| ✅ Alpha | ⚠️ Fresh session by default | ✅ Yes (provider-managed) | ✅ Yes | Models, JSON exec mode, sandbox, structured event parsing |

### Audit Snapshot — March 2026

- `Claude Code` remains the only provider where DeterminAgent can create a deterministic first-call session ID itself.
- `Copilot CLI`, `Gemini CLI`, and `Codex CLI` now document resume flows upstream, but those session IDs are provider-owned. DeterminAgent still defaults to fresh sessions there to keep multi-agent orchestration deterministic.
- The library now aligns better with current CLIs by:
   - using Gemini headless mode via `--prompt`
   - emitting Codex `exec --json` with `--model`
   - forwarding configured `sandbox` and `tools` from `UnifiedAgent` into adapters
   - using current Claude `--allowed-tools` / `--resume` forms

If you need a provider capability that exists upstream but is not yet abstracted cleanly here, pass an exact model string or extend the adapter directly.

---

## 🎯 Model Alias Map

DeterminAgent resolves model aliases per provider so you can keep flows consistent.

| Alias | Claude Code | Gemini CLI | Copilot CLI | OpenAI Codex |
| :--- | :--- | :--- | :--- | :--- |
| fast | haiku | gemini-3-flash-preview | claude-haiku-4.5 | gpt-5.1-codex-mini |
| balanced | sonnet | gemini-3-flash-preview | gpt-5-mini | gpt-5.4 |
| powerful | opus | gemini-3.1-pro-preview | claude-opus-4.6 | gpt-5.3-codex |
| reasoning | opus | gemini-3.1-pro-preview | gpt-5.4 | gpt-5.4 |
| free | haiku | gemini-3-flash-preview | gpt-5-mini | gpt-5.1-codex-mini |

Notes:
- You can always pass an exact model string to override the alias.
- Availability depends on your provider plan and CLI version.
- Gemini aliases now target current Gemini 3.x CLI-safe models: `gemini-3-flash-preview` for fast/default work and `gemini-3.1-pro-preview` for top-end reasoning.
- `gemini-3.1-flash-lite-preview` exists in the Gemini API, but current Gemini CLI validation does not reliably expose it yet.
- Copilot `powerful` and `reasoning` use newer premium models and may require broader plan access than `gpt-5-mini`.
- Codex and Copilot model inventories change frequently; aliases are conservative defaults, not an exhaustive upstream model list.

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

<img src="https://raw.githubusercontent.com/Experto-AI/determinagent/main/docs/assets/architecture.svg" alt="DeterminAgent Architecture" width="800">

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
