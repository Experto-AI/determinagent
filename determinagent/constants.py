"""
Configuration constants for the library.
"""

from collections.abc import Callable

# ============================================================================
# Model Aliases
# ============================================================================

MODEL_MAPPING: dict[str, dict[str, str]] = {
    "fast": {
        "claude": "haiku",
        "gemini": "gemini-3-flash-preview",
        "copilot": "claude-haiku-4.5",
        "codex": "gpt-5.1-codex-mini",
    },
    "balanced": {
        "claude": "sonnet",
        "gemini": "gemini-3-pro-preview",
        "copilot": "claude-sonnet-4.5",
        "codex": "gpt-5.1-codex",
    },
    "powerful": {
        "claude": "opus",
        "gemini": "gemini-3-pro-preview",  # Requires Gemini CLI preview features
        "copilot": "claude-opus-4.5",
        "codex": "gpt-5.1-codex-max",
    },
    "reasoning": {
        "claude": "opus",  # Best available reasoning model alias in Claude Code
        "gemini": "gemini-3-pro-preview",
        "copilot": "gpt-5.2",
        "codex": "gpt-5.1-codex",
    },
    # "free" category: Models with no additional per-token cost.
    # Since CLI tools use subscription-based access, we default to fast/efficient models.
    # Gemini's free tier commonly exposes Flash-class models, but Gemini 3
    # requires preview features and may not be enabled for all accounts.
    "free": {
        "claude": "haiku",  # Fastest, included in subscription
        "gemini": "gemini-3-flash-preview",  # Requires Gemini CLI preview features
        "copilot": "claude-haiku-4.5",  # Fastest, included in subscription
        "codex": "gpt-5.1-codex-mini",  # Fastest, included in subscription
    },
}


def resolve_model_alias(alias: str, provider: str) -> str:
    """
    Resolve model alias to provider-specific name.

    Args:
        alias: Model alias (fast/balanced/powerful/reasoning) or exact name
        provider: CLI provider

    Returns:
        Provider-specific model name

    Examples:
        resolve_model_alias("fast", "claude") → "haiku"
        resolve_model_alias("balanced", "copilot") → "claude-sonnet-4.5"
        resolve_model_alias("opus", "claude") → "opus" (passthrough)
    """
    if alias in MODEL_MAPPING:
        return MODEL_MAPPING[alias].get(provider, alias)
    return alias  # Passthrough if not an alias


# ============================================================================
# Tool Permission Configs
# ============================================================================

TOOL_COMMANDS: dict[str, Callable[[list[str]], list[str]]] = {
    "claude": lambda tools: ["--allowedTools", ",".join(tools)],
    "gemini": lambda _: [],  # Built-in, configured via extensions
    "copilot": lambda tools: ["--allow-all-tools"] if tools else [],
    "codex": lambda _: [],  # Configured via config.toml features
}

WEB_SEARCH_CONFIG: dict[str, list[str]] = {
    "claude": ["--allowedTools", "WebSearch,WebFetch"],
    "gemini": [],  # Built-in
    "copilot": ["--allow-all-tools"],
    "codex": [],  # Enabled via config.toml: web_search_request = true
}

# ============================================================================
# Codex-Specific Configs
# ============================================================================

CODEX_SANDBOX_MODES = {
    "safe": "read-only",
    "write": "workspace-write",
    "full": "danger-full-access",
}

CODEX_APPROVAL_POLICIES = {
    "interactive": "suggest",
    "auto_edit": "auto-edit",
    "auto": "on-failure",  # --full-auto is shortcut for this + workspace-write
}

# ============================================================================
# Session Configs
# ============================================================================

DEFAULT_MAX_HISTORY = 5  # For file-based sessions
DEFAULT_TIMEOUT = 180  # Seconds for CLI commands
