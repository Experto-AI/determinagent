"""
Provider adapters for CLI tools.

This module exports all available adapters and common types/exceptions.
"""

# Re-export exceptions from the exceptions module
from ..exceptions import (
    ExecutionError,
    ProviderAuthError,
    ProviderNotAvailable,
    RateLimitExceeded,
    SandboxViolation,
)
from .base import Provider, ProviderAdapter
from .claude import ClaudeAdapter
from .codex import CodexAdapter
from .copilot import CopilotAdapter
from .gemini import GeminiAdapter

__all__ = [
    # Adapters
    "ProviderAdapter",
    "ClaudeAdapter",
    "CopilotAdapter",
    "GeminiAdapter",
    "CodexAdapter",
    # Types
    "Provider",
    # Exceptions
    "ProviderNotAvailable",
    "ProviderAuthError",
    "RateLimitExceeded",
    "ExecutionError",
    "SandboxViolation",
]
