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
5. [Configuration and Environment](#configuration-and-environment)

---

## Claude Code CLI

### Execution & Prompts

| Flag | Format | Purpose |
|------|--------|---------|
| `-p` / `--print` | `claude -p "query"` | Print response and exit (non-interactive) |
| `prompt` | `claude "query"` | Start interactive with initial prompt |

### Session Management

| Flag | Format | Purpose |
|------|--------|---------|
| `-c` / `--continue` | `claude -c` | Continue most recent conversation |
| `-r` / `--resume` | `claude -r "session-id"` | Resume by session ID or open picker |
| `--session-id` | `claude --session-id "uuid"` | Create/use specific session ID |

### Model Selection

| Flag | Format | Purpose |
|------|--------|---------|
| `--model` | `claude --model <model>` | Use a model alias (e.g., `sonnet`, `opus`) or full model name |

### System Prompt

| Flag | Format | Purpose |
|------|--------|---------|
| `--system-prompt` | `claude --system-prompt "..."` | Override default instructions |
| `--append-system-prompt` | `claude --append-system-prompt "..."` | Add to defaults |

### Tool Control

| Flag | Format | Purpose |
|------|--------|---------|
| `--allowedTools` / `--allowed-tools` | `claude --allowed-tools "Bash,Read"` | Allow only specified tools |
| `--disallowedTools` / `--disallowed-tools` | `claude --disallowed-tools "Bash(rm:*)"` | Deny specific tools |
| `--tools` | `claude --tools "Bash,Edit,Read"` | Select which built-in tools are available (print mode only) |

### Output & Debug

| Flag | Format | Purpose |
|------|--------|---------|
| `--output-format` | `claude -p --output-format json` | `text`, `json`, `stream-json` (print mode only) |
| `--json-schema` | `claude -p --json-schema '{"type":"object"}'` | Validate structured output against JSON schema |
| `--input-format` | `claude -p --input-format stream-json` | `text`, `stream-json` (print mode only) |
| `--include-partial-messages` | `claude -p --output-format stream-json --include-partial-messages` | Include partial chunks (print mode only) |
| `--debug` | `claude --debug` | Enable debug mode (optional category filter) |
| `--verbose` | `claude --verbose` | Override verbose mode setting |

### Examples

```bash
# Headless with specific model and JSON output
claude -p "analyze this" --model sonnet --output-format json

# Continue conversation with custom instructions
claude -c --append-system-prompt "Focus on security"

# Restrict tools (print mode)
claude -p "search the codebase" --allowed-tools "Bash,Read"

# Resume with debugging
claude --continue --debug "next steps"
```

---

## Gemini CLI

### Execution & Prompts

| Flag | Format | Purpose |
|------|--------|---------|
| `prompt` | `gemini "query"` | One-shot prompt (non-interactive) |
| `-i` / `--prompt-interactive` | `gemini -i "text"` | Execute prompt and continue interactively |
| `-p` / `--prompt` | `gemini -p "query"` | Deprecated (use positional prompt) |

### Model Selection

| Flag | Format | Purpose |
|------|--------|---------|
| `-m` / `--model` | `gemini -m <model>` | Specify model |

### Session Management

| Flag | Format | Purpose |
|------|--------|---------|
| `-r` / `--resume` | `gemini --resume latest` | Resume most recent session or by index |
| `--list-sessions` | `gemini --list-sessions` | List all sessions |
| `--delete-session` | `gemini --delete-session 2` | Delete session by index |

### Safety & Approval

| Flag | Format | Purpose |
|------|--------|---------|
| `-s` / `--sandbox` | `gemini --sandbox` | Run in sandbox mode |
| `-y` / `--yolo` | `gemini --yolo` | Auto-approve all actions |
| `--approval-mode` | `gemini --approval-mode auto_edit` | `default`, `auto_edit`, `yolo` |
| `--allowed-tools` | `gemini --allowed-tools read_file` | Allow tools without confirmation |
| `--allowed-mcp-server-names` | `gemini --allowed-mcp-server-names foo` | Allow MCP servers by name |

### Output Formatting

| Flag | Format | Purpose |
|------|--------|---------|
| `-o` / `--output-format` | `gemini --output-format json` | `text`, `json`, `stream-json` |

### Workspace & Extensions

| Flag | Format | Purpose |
|------|--------|---------|
| `--include-directories` | `gemini --include-directories ../shared` | Add extra workspace roots |
| `-e` / `--extensions` | `gemini --extensions a b` | Use specific extensions |
| `-l` / `--list-extensions` | `gemini --list-extensions` | List available extensions |

### Examples

```bash
# One-shot with JSON output
gemini "analyze code" --output-format json

# Resume most recent session with auto-approval and streaming
gemini --resume latest --yolo --output-format stream-json

# Custom model and interactive follow-up
gemini -m <model> -i "complex task"
```

---

## Copilot CLI

### Execution Mode

| Flag | Format | Purpose |
|------|--------|---------|
| `-p` / `--prompt` | `copilot -p "task"` | Non-interactive prompt (requires `--allow-all-tools`) |
| `-i` / `--interactive` | `copilot -i "prompt"` | Start interactive mode and run prompt |

### Session Management

| Flag | Format | Purpose |
|------|--------|---------|
| `--resume` | `copilot --resume` | Resume previous session (picker) |
| `--resume <id>` | `copilot --resume abc123` | Resume by session ID |
| `--continue` | `copilot --continue` | Resume most recent session |

### Model Selection

| Flag | Format | Purpose |
|------|--------|---------|
| `--model` | `copilot --model gpt-5` | Specify model (see `copilot --help` for choices) |

**Available Models:** `claude-sonnet-4.5`, `claude-haiku-4.5`, `claude-opus-4.5`, `claude-sonnet-4`, `gpt-5.1-codex-max`, `gpt-5.1-codex`, `gpt-5.2`, `gpt-5.1`, `gpt-5`, `gpt-5.1-codex-mini`, `gpt-5-mini`, `gpt-4.1`, `gemini-3-pro-preview`

### Tool & URL Permissions

| Flag | Format | Purpose |
|------|--------|---------|
| `--allow-all-tools` | `copilot --allow-all-tools` | Allow all tools without confirmation |
| `--allow-tool` | `copilot --allow-tool 'shell(git:*)'` | Allow specific tools |
| `--deny-tool` | `copilot --deny-tool 'shell(git push)'` | Deny specific tools |
| `--available-tools` | `copilot --available-tools write` | Limit tools to this set |
| `--excluded-tools` | `copilot --excluded-tools shell` | Exclude tools from availability |
| `--allow-url` | `copilot --allow-url github.com` | Allow URLs or domains |
| `--deny-url` | `copilot --deny-url https://example.com` | Deny URLs or domains |
| `--allow-all-urls` | `copilot --allow-all-urls` | Allow all URLs without confirmation |

### Output & Logging

| Flag | Format | Purpose |
|------|--------|---------|
| `-s` / `--silent` | `copilot -s -p "task"` | Output only response (no stats) |
| `--stream` | `copilot --stream off` | Toggle streaming (`on`/`off`) |
| `--log-level` | `copilot --log-level debug` | Set log level |

### Examples

```bash
# Non-interactive mode (requires allow-all-tools)
copilot -p "List all open issues assigned to me" --allow-all-tools

# Using custom agent
copilot --agent=refactor-agent -p "Refactor this code" --allow-all-tools

# Resume previous session
copilot --resume

# Select specific model
copilot --model "claude-sonnet-4.5" -p "Analyze this code" --allow-all-tools
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
| `codex exec resume --last` | Resume most recent non-interactive session |
| `codex resume` | Resume picker for interactive |
| `codex resume --last` | Resume most recent interactive session |
| `codex review` | Non-interactive code review |

### Model Selection

| Flag | Format | Purpose |
|------|--------|---------|
| `-m` / `--model` | `codex -m o3` | Specify model |
| `--oss` | `codex --oss` | Use local open-source model provider |
| `--local-provider` | `codex --local-provider ollama` | Choose local provider |

### Approval Policies

| Flag | Format | Purpose |
|------|--------|---------|
| `-a` / `--ask-for-approval` | `codex -a on-request` | `untrusted`, `on-failure`, `on-request`, `never` |
| `--full-auto` | `codex --full-auto` | Alias for `-a on-request` + `--sandbox workspace-write` |
| `--dangerously-bypass-approvals-and-sandbox` | `codex --dangerously-bypass-approvals-and-sandbox` | Disable approvals and sandboxing |

### Sandbox Modes

| Flag | Format | Purpose |
|------|--------|---------|
| `-s` / `--sandbox` | `codex --sandbox read-only` | `read-only`, `workspace-write`, `danger-full-access` |

### Output & Debugging

| Flag | Format | Purpose |
|------|--------|---------|
| `--json` | `codex exec --json "task"` | Stream JSONL events |
| `-o` / `--output-last-message` | `codex exec -o output.txt "task"` | Write final response to file |
| `--output-schema` | `codex exec --output-schema schema.json "task"` | Enforce JSON schema on final response |

### Directory & Context

| Flag | Format | Purpose |
|------|--------|---------|
| `-C` / `--cd` | `codex -C /path/to/project` | Set working directory |
| `--add-dir` | `codex --add-dir ../backend` | Add extra writable roots |
| `-i` / `--image` | `codex -i screenshot.png "explain"` | Attach images |
| `--search` | `codex --search` | Enable web search tool |

### MCP Server Management

| Command | Purpose |
|---------|---------|
| `codex mcp add name -- command args` | Add STDIO MCP server |
| `codex mcp add name --url https://...` | Add HTTP MCP server |
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
codex -m <model> "optimize this algorithm"
```

---

## Configuration and Environment

### Codex Config

| Item | Location | Notes |
|------|----------|-------|
| Config file | `~/.codex/config.toml` | Primary configuration file |
| Override config | `codex -c key=value` | Inline TOML overrides |

### Copilot Environment Variables

From `copilot help environment`:

| Variable | Purpose |
|----------|---------|
| `COPILOT_ALLOW_ALL` | Allow all tools without confirmation (`true`) |
| `COPILOT_AUTO_UPDATE` | Disable auto-updates when set to `false` |
| `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` | Extra dirs for custom instructions |
| `COPILOT_MODEL` | Default model override |
| `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN` | Auth token precedence |
| `USE_BUILTIN_RIPGREP` | Use bundled `rg` when not `false` |
| `PLAIN_DIFF` | Disable rich diff rendering when `true` |
| `XDG_CONFIG_HOME` | Override config root (defaults to `~/.copilot`) |
| `XDG_STATE_HOME` | Override state root (defaults to `~/.copilot`) |

For Claude and Gemini environment variables, refer to each provider's official documentation.
