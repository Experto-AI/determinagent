# CLI Reference
<!--
  DOCUMENT SCOPE:
  - Purpose: Technical dictionary of CLI provider interactions.
  - Include: Command flags, environment variables, and configuration file paths.
  - Do NOT include: Project roadmap, installation steps, or general architectural design.
-->


Complete command-line reference for all supported AI CLI tools.

---

## Table of Contents

1. [Claude Code CLI](#claude-code-cli)
2. [Gemini CLI](#gemini-cli)
3. [Copilot CLI](#copilot-cli)
4. [OpenAI Codex CLI](#openai-codex-cli)
5. [Configuration Priority](#configuration-priority)

---

## Claude Code CLI

### Session Management

| Flag | Format | Purpose |
|------|--------|---------|
| `-p` | `claude -p "query"` | Print/headless mode (non-interactive) |
| `-c` / `--continue` | `claude -c` | Continue most recent conversation |
| `-r` / `--resume` | `claude -r "session-id"` | Resume specific session by ID |
| `--session-id` | `claude --session-id "uuid"` | Create/use specific session ID |

### Model Selection

| Flag | Format | Purpose |
|------|--------|---------|
| `--model` | `claude --model <alias>` | Specify model: `sonnet`, `opus`, `haiku`, `opusplan` |

**Available Models:** `sonnet` (latest), `opus` (latest), `haiku`, `opusplan` (hybrid)

### System Prompt

| Flag | Format | Purpose |
|------|--------|---------|
| `--system-prompt` | `claude --system-prompt "..."` | Override default instructions |
| `--system-prompt-file` | `claude --system-prompt-file /path` | Load from file |
| `--append-system-prompt` | `claude --append-system-prompt "..."` | Add to defaults |

### Tool Control

| Flag | Format | Purpose |
|------|--------|---------|
| `--allowedTools` | `claude --allowedTools "Read,Bash(git:*)"` | Allow only specified tools |
| `--disallowedTools` | `claude --disallowedTools "Bash(rm:*)"` | Deny specific tools |

**Available Tools:** `Read`, `Write`, `Bash`, `Grep`, `Glob`, `WebSearch`, `WebFetch`

### Output & Debug

| Flag | Format | Purpose |
|------|--------|---------|
| `--output-format` | `claude -p --output-format json` | Format: `text`, `json`, `stream-json` |
| `--verbose` | `claude --verbose` | Enable verbose logging |
| `--mcp-debug` | `claude --mcp-debug` | Debug MCP server connections |

### Examples

```bash
# Headless with specific model and JSON output
claude -p "analyze this" --model opus --output-format json

# Continue conversation with custom instructions
claude -c --append-system-prompt "Focus on security"

# Use only safe tools
claude --allowedTools "Read,Grep" "search the codebase"

# Resume with debugging
claude --continue --verbose "next steps"
```

---

## Gemini CLI

### Execution & Prompts

| Flag | Format | Purpose |
|------|--------|---------|
| `-p` / `--prompt` | `gemini -p "query"` | Single prompt (non-interactive) |
| `-i` / `--prompt-interactive` | `gemini -i "text"` | Start interactive with prompt |

### Model Selection

| Flag | Format | Purpose |
|------|--------|---------|
| `-m` / `--model` | `gemini -m gemini-2.5-flash` | Specify model |

**Available Models:** `gemini-2.5-flash`, `gemini-2.5-pro`

### Session Management

| Flag | Format | Purpose |
|------|--------|---------|
| `--resume` | `gemini --resume` | Resume most recent session |
| `--resume <index>` | `gemini --resume 1` | Resume by index |
| `--resume <uuid>` | `gemini --resume abc-123` | Resume by UUID |
| `--list-sessions` | `gemini --list-sessions` | List all sessions |
| `--delete-session` | `gemini --delete-session 2` | Delete session |

### Safety & Approval

| Flag | Format | Purpose |
|------|--------|---------|
| `-s` / `--sandbox` | `gemini --sandbox` | Enable sandbox mode |
| `--sandbox-image` | `gemini --sandbox-image ubuntu:22.04` | Custom Docker image |
| `-y` / `--yolo` | `gemini --yolo` | Auto-approve all tool calls |
| `--approval-mode` | `gemini --approval-mode default` | `default`, `auto_edit`, `yolo` |

### Output Formatting

| Flag | Format | Purpose |
|------|--------|---------|
| `--output-format` | `gemini --output-format json` | `text`, `json`, `stream-json` |

### Model Parameters

| Flag | Format | Purpose |
|------|--------|---------|
| `-t` / `--temperature` | `gemini -t 0.5` | Set temperature (0.0-2.0) |
| `-b` / `--thinking-budget` | `gemini -b 8192` | Max thinking tokens |

### Examples

```bash
# Headless with JSON output
gemini -p "analyze code" --output-format json

# Resume with auto-approval and streaming
gemini --resume --yolo --output-format stream-json

# Custom model and temperature
gemini -m gemini-2.5-pro -t 0.3 -p "complex task"
```

---

## Copilot CLI

### Session Management

| Flag | Format | Purpose |
|------|--------|---------|
| `--resume` | `copilot --resume` | Resume previous session |
| `--resume <id>` | `copilot --resume abc123` | Resume by session ID |
| `--continue` | `copilot --continue` | Resume most recent session |

### Execution Mode

| Flag | Format | Purpose |
|------|--------|---------|
| `-p` / `--prompt` | `copilot -p "task"` | Programmatic (non-interactive) mode |

### Model Selection

| Flag | Format | Purpose |
|------|--------|---------|
| `--model` | `copilot --model "claude-sonnet-4-5"` | Specify model (run `copilot help config` for valid names) |

**Available Models:** `claude-sonnet-4-5` (default), `claude-sonnet-4`, `gpt-5`

### Tool Approval

| Flag | Format | Purpose |
|------|--------|---------|
| `--allow-all-tools` | `copilot --allow-all-tools` | Allow any tool without approval |
| `--allow-tool` | `copilot --allow-tool 'My-MCP-Server'` | Allow specific tool (supports glob patterns) |
| `--deny-tool` | `copilot --deny-tool 'My-MCP-Server(tool_name)'` | Deny specific tool (takes precedence) |

### Output Format

| Flag | Format | Purpose |
|------|--------|---------|
| `--format` | `copilot --format json` | Output format (verify with `copilot help` for current support) |

*Note: JSON output support is in development. Check `copilot help` for currently available format options.*

### Agent Selection

| Flag | Format | Purpose |
|------|--------|---------|
| `--agent` | `copilot --agent=refactor-agent` | Use custom agent |

### Examples

```bash
# Programmatic mode with tool control
copilot -p "List all open issues assigned to me" --allow-tool 'gh-cli'

# Using custom agent
copilot --agent=refactor-agent -p "Refactor this code block"

# Allow all tools (use with caution)
copilot --allow-all-tools -p "Run comprehensive analysis"

# Resume previous session
copilot --resume

# Continue most recent session
copilot --continue

# Select specific model
copilot --model "claude-sonnet-4-5" -p "Analyze this code"
```

---

## OpenAI Codex CLI

### Execution Modes

| Command | Purpose |
|---------|---------|
| `codex` | Interactive TUI mode |
| `codex "prompt"` | Interactive with initial prompt |
| `codex exec "prompt"` | Non-interactive automation |
| `codex exec resume <id>` | Resume non-interactive session |
| `codex resume` | Resume picker for interactive |
| `codex resume --last` | Resume most recent session |

### Model Selection

| Flag | Format | Purpose |
|------|--------|---------|
| `-m` / `--model` | `codex -m gpt-5.1` | Specify model |

**Available Models:** `gpt-5.1-codex-max` (default), `gpt-5.1`, `gpt-5.1-codex-mini`, `o3`, `o4-mini`

### Approval Policies

| Flag | Format | Purpose |
|------|--------|---------|
| `-a` / `--ask-for-approval` | `codex -a untrusted` | Set approval policy |
| `--full-auto` | `codex --full-auto` | Auto-approve (on-failure + workspace-write) |

**Approval Values:** `suggest`, `auto-edit`, `untrusted`, `on-failure`, `on-request`, `never`

### Sandbox Modes

| Flag | Format | Purpose |
|------|--------|---------|
| `--sandbox` | `codex --sandbox read-only` | Set sandbox mode |

**Sandbox Values:**
- `read-only` - Read files only (default for exec)
- `workspace-write` - Allow writes to cwd and $TMPDIR
- `danger-full-access` - No restrictions

### Output & Debugging

| Flag | Format | Purpose |
|------|--------|---------|
| `--json` | `codex exec --json "task"` | Stream JSON Lines output |
| `-o` / `--output-last-message` | `codex exec -o file.txt "task"` | Write final output to file |
| `--output-schema` | `codex exec --output-schema schema.json` | Structured JSON output |
| `-d` / `--debug` | `codex --debug` | Enable debug logging |

### Directory & Context

| Flag | Format | Purpose |
|------|--------|---------|
| `-C` / `--cd` | `codex -C /path/to/project` | Set working directory |
| `--add-dir` | `codex --add-dir ../backend` | Add extra writable roots |
| `-i` / `--image` | `codex -i screenshot.png "explain"` | Attach images |

### MCP Server Management

| Command | Purpose |
|---------|---------|
| `codex mcp add name -- command args` | Add STDIO MCP server |
| `codex mcp list` | List configured servers |
| `codex mcp get server-name` | Show server config |
| `codex mcp remove server-name` | Remove MCP server |

### Examples

```bash
# Non-interactive with full automation
codex exec --full-auto "add unit tests for auth"

# Read-only analysis with JSON output
codex exec --json "count lines of code"

# Full access for network operations
codex exec --sandbox danger-full-access "fetch and summarize API docs"

# Resume and continue previous work
codex exec resume --last "fix the remaining issues"

# Multi-directory project
codex --cd frontend --add-dir ../backend --add-dir ../shared

# With specific model
codex -m o3 "optimize this algorithm"
```

---

## Configuration Priority

All four CLIs apply settings in this order (highest to lowest priority):

1. **Command-line arguments** (always wins)
2. **Environment variables**
3. **Project/local config** (`./<cli>/settings.json`, `.github/`, `.codex/config.toml`)
4. **User config** (`~/.claude/`, `~/.gemini/`, `~/.copilot/`, `~/.codex/`)
5. **System defaults**

**Key Insight:** Command-line flags override everything, making them ideal for orchestration scripts.

---

## Environment Variables

| Provider | Variable | Purpose |
|----------|----------|---------|
| Claude | `ANTHROPIC_MODEL` | Default model |
| Gemini | `GEMINI_API_KEY` | API authentication |
| Gemini | `GEMINI_MODEL` | Default model |
| Codex | `OPENAI_API_KEY` | API authentication (alternative to login) |
| Codex | `CODEX_HOME` | Override config directory |

---

## Configuration Files

| Provider | User Config | Project Config |
|----------|-------------|----------------|
| Claude | `~/.claude/settings.json` | `.claude/settings.json` |
| Gemini | `~/.gemini/settings.json` | `.gemini/settings.json` |
| Copilot | `~/.copilot/config` | `.github/copilot-instructions.md` |
| Codex | `~/.codex/config.toml` | `.codex/config.toml`, `AGENTS.md` |

---

*See official documentation for complete reference:*
- [Claude Code CLI](https://code.claude.com/docs/en/cli-reference)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- [Copilot CLI](https://docs.github.com/en/copilot/github-copilot-in-the-cli)
- [OpenAI Codex CLI](https://github.com/openai/codex)
