"""
DeterminAgent - CLI-First Deterministic Multi-Agent Orchestration Library

A library for orchestrating AI CLI tools (Claude Code, GitHub Copilot, Gemini CLI, OpenAI Codex)
to create cost-effective, deterministic workflows.

Example:
    ```python
    from determinagent import UnifiedAgent, SessionManager

    # Create a session
    session = SessionManager("claude")

    # Create an agent
    agent = UnifiedAgent(
        provider="claude",
        model="balanced",
        role="writer",
        instructions="You are a helpful writing assistant.",
        session=session,
    )

    # Send a prompt
    response = agent.send("Write a haiku about coding")
    print(response)
    ```
"""

__version__ = "0.11.0"

# Core classes
# Adapters
from .adapters import (
    ClaudeAdapter,
    CopilotAdapter,
    Provider,
    ProviderAdapter,
)
from .agent import ADAPTERS, UnifiedAgent, get_adapter
from .config import load_config

# Utilities
from .constants import (
    MODEL_MAPPING,
    TOOL_COMMANDS,
    WEB_SEARCH_CONFIG,
    resolve_model_alias,
)

# Exceptions
from .exceptions import (
    ConfigurationError,
    DeterminAgentError,
    ExecutionError,
    ParseError,
    ProviderAuthError,
    ProviderNotAvailable,
    QuotaExceeded,
    RateLimitExceeded,
    SandboxViolation,
    SessionError,
    TimeoutError,
    ValidationError,
)
from .parsers import CategoryScore, ReviewResult, parse_review
from .sessions import SessionManager

__all__ = [
    # Version
    "__version__",
    # Core
    "UnifiedAgent",
    "SessionManager",
    "get_adapter",
    "ADAPTERS",
    # Adapters
    "ProviderAdapter",
    "ClaudeAdapter",
    "CopilotAdapter",
    "Provider",
    # Exceptions
    "DeterminAgentError",
    "ProviderNotAvailable",
    "ProviderAuthError",
    "RateLimitExceeded",
    "QuotaExceeded",
    "ExecutionError",
    "TimeoutError",
    "SandboxViolation",
    "ParseError",
    "ValidationError",
    "SessionError",
    "ConfigurationError",
    # Utilities
    "MODEL_MAPPING",
    "resolve_model_alias",
    "WEB_SEARCH_CONFIG",
    "TOOL_COMMANDS",
    "load_config",
    "parse_review",
    "ReviewResult",
    "CategoryScore",
]
