# DeterminAgent Architecture & Technical Design

**Version:** 3.0  
**Status:** Technical Source of Truth  
**Target Audience:** Developers & Contributors

---

## 1. Design Principles

### The Library-First Philosophy
DeterminAgent is a library, not a framework. It provides clean Pythonic abstractions over AI CLI tools without forcing a proprietary workflow engine.
- **Full Control**: Users write standard Python and LangGraph code.
- **Type Safety**: Pydantic models and strict type hinting for all public APIs.
- **Testability**: Designed for local unit testing without expensive API calls.

### The Strict Output Pattern
When orchestrating multi-agent systems, "meta-commentary" (e.g., "I've updated the code for you...") breaks downstream agents.
**Every prompt must include strict output rules:**
```markdown
CRITICAL OUTPUT RULES:
1. Start DIRECTLY with the content (e.g., "# Title" for blog, "import" for code)
2. Do NOT include ANY introductory text (e.g., "I've created...", "Sure, here is...")
3. Do NOT include ANY closing remarks (e.g., "I hope this helps", "Let me know...")
4. Output ONLY the raw content. Nothing else.
```

---

## 2. Value Proposition

### The Three Pillars
1. **Finite State Orchestration**: Replaces unpredictable autonomous agents with deterministic, graph-based logic using LangGraph.
2. **Subscription Arbitrage**: $0 additional cost by leveraging flat-rate CLI subscriptions (no per-token API charges).
3. **Binary-First Integration**: Directly controls local CLI tools via subprocess, avoiding API latency and behaving exactly like a human at the terminal.

### Competitive Comparison

| Feature | DeterminAgent | LangGraph/LangChain | CrewAI | AutoGen |
|---------|---------------|---------------------|--------|---------|
| **Cost** | $0 (CLI subs) | Per-token API | Per-token API | Per-token API |
| **Provider Focus** | CLI tools | Any API | Any API | Any API |
| **Orchestration** | Graph-based | Graph-based | Role-based | Conversational |

---

## 3. System Design

### Architecture Overview

![DeterminAgent Architecture](docs/assets/architecture.svg)

*The architecture follows a three-layer design:*

1. **Template Flows** (`flows/`): Pre-built Python workflow scripts for common use cases. Non-programmers can copy, customize, and run these directly.

2. **Configuration Layer**: YAML-based agent settings and prompts with auto-discovery via `load_config()`. Required for template flows.

3. **Core Library**: The foundation providing `UnifiedAgent`, provider adapters (Claude, Copilot, Gemini, Codex), `SessionManager`, and utilities. Full Python control with LangGraph integration.

### System Components

#### UnifiedAgent Interface
The main entry point for interaction. It abstracts the underlying CLI tools.
```python
class UnifiedAgent:
    def send(self, prompt: str, max_retries: int = 2) -> str: ...
    def send_structured(self, prompt: str, schema: Type[BaseModel]) -> BaseModel: ...
    def get_history(self) -> list[Message]: ...
    def clear_session(self): ...
```

#### SessionManager
Handles native session flags for providers that support custom session IDs.
- **Claude**: Full support via `--session-id <uuid>` for first call, `-r <uuid>` for resume.
- **Gemini**: No session resume (always fresh sessions)
- **Copilot**: No session resume (always fresh sessions)
- **Codex**: No session resume (always fresh sessions)

> **Note:** Only Claude supports creating sessions with a custom ID. Other providers generate session IDs internally, making them incompatible with multi-agent workflows where each agent needs its own persistent session.

#### Provider Adapters
Specific implementations for each CLI tool. Each adapter handles command building, output parsing, and error normalization.
- `build_command()`: Constructs the subprocess call.
- `parse_output()`: Extracts the response from raw stdout.
- `handle_error()`: Converts return codes and stderr into typed exceptions.

---

## 4. Provider Capabilities

| Feature | Claude Code | Gemini CLI | GitHub Copilot | OpenAI Codex |
|---------|-------------|------------|----------------|--------------|
| **Session IDs** | ✅ `--session-id`, `-r` | ❌ Not supported | ❌ Not supported | ❌ Not supported |
| **System Prompt** | ✅ `--system-prompt` | ⚠️ No direct flag | ⚠️ Via AGENTS/custom instructions | ⚠️ Via `AGENTS.md` |
| **Output Format** | text/json/stream-json (print mode) | text/json/stream-json | text (optional streaming) | text (JSONL with `--json`) |
| **Tool Permissions** | `--allowed-tools`, `--disallowed-tools` | `--allowed-tools`, `--approval-mode` | `--allow-all-tools`, `--allow-tool` | `--search` (web), config.toml |
| **Sandbox Mode** | ❌ No | ✅ `--sandbox` | ❌ No | ✅ `--sandbox` |

### When to Use Each Provider

| Provider | Best For | Model Strength |
|----------|----------|----------------|
| **Claude** | Writing, planning, complex reasoning | Most capable overall |
| **Copilot** | GitHub integration, PR workflows | Fastest for code |
| **Gemini** | Research, analysis, web search | Best free tier |
| **Codex** | Code execution, sandbox testing | Best for automation |

---

## 5. Decision Log & Alternatives

### Session Management
- **Alternative**: File-based (JSON) or SQLite store.
- **Decision**: **Native sessions**. Best performance, no additional storage overhead, and all 4 target CLIs now support it natively.

### Design Decisions
- **History Truncation**: Default to last 5 messages for token efficiency in long flows.
- **Codex Sandbox**: Default to `workspace-write` for maximum utility in automation.
- **Library vs Framework**: Focus on **Library-Only**. YAML is used for agent settings (provider/model) but NOT for flow logic. Flow logic belongs in Python.

---

## 6. Technical Reference

### Model Aliases
| Alias | Claude | Copilot | Gemini | Codex |
|-------|--------|---------|--------|-------|
| `fast` | haiku | claude-haiku-4.5 | gemini-2.5-flash | gpt-5.1-codex-mini |
| `balanced` | sonnet | claude-sonnet-4.5 | gemini-2.5-pro | gpt-5.1 |
| `powerful` | opus | gpt-5 | gemini-2.5-pro | gpt-5.1-codex-max |
| `reasoning` | opusplan | gpt-5 | gemini-2.5-pro | o3 |
| `free` | haiku | claude-haiku-4.5 | gemini-2.5-flash | gpt-5.1-codex-mini |

### Tool Permissions
- **Claude**: `["--allowed-tools", "..."]` or `["--disallowed-tools", "..."]`
- **Gemini**: `["--allowed-tools", "..."]` and `["--approval-mode", "..."]`
- **Copilot**: `["--allow-all-tools"]` (required for non-interactive prompts)
- **Codex**: `["--search"]` for web search; other permissions via config.toml

---

## 7. Testing & Risk Mitigation

### Strategy
- **Unit Tests**: Mock subprocess calls to verify command building and output parsing.
- **Integration Tests**: Run narrow, well-defined workflows against mock environments.
- **Error Normalization**: All adapters raise typed exceptions: `ProviderNotAvailable`, `RateLimitExceeded`, `ExecutionError`.

### Risk Mitigation
- **Output Parsing**: Use multi-pattern regex (battle-tested) and Pydantic validation.
- **Retries**: Implement configurable retry logic with session resets for transient CLI failures.
