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
        "gemini": "gemini-2.5-flash",
        "copilot": "claude-haiku-4.5",
        "codex": "gpt-5.1-codex-mini",
    },
    "balanced": {
        "claude": "sonnet",
        "gemini": "gemini-2.5-pro",
        "copilot": "claude-sonnet-4-5",
        "codex": "gpt-5.1",
    },
    "powerful": {
        "claude": "opus",
        "gemini": "gemini-2.5-pro",  # No opus equivalent
        "copilot": "gpt-5",
        "codex": "gpt-5.1-codex-max",
    },
    "reasoning": {
        "claude": "opusplan",
        "gemini": "gemini-2.5-pro",
        "copilot": "gpt-5",
        "codex": "o3",
    },
    # "free" category: Models with no additional per-token cost.
    # Since CLI tools use subscription-based access (not API billing),
    # all models are effectively $0 cost. We default to fast/efficient models.
    # For Gemini, gemini-2.5-flash is available in the free tier via Google AI Studio.
    "free": {
        "claude": "haiku",  # Fastest, included in subscription
        "gemini": "gemini-2.5-flash",  # Free tier available
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
        resolve_model_alias("balanced", "copilot") → "claude-sonnet-4-5"
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
    "copilot": ["--allow-all-tools", "--allow-all-urls"],
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
