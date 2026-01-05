"""
Abstract base class for CLI provider adapters.

This module defines the interface that all provider adapters must implement,
providing a consistent API for building commands, parsing output, and handling errors.
"""

import subprocess
from abc import ABC, abstractmethod
from typing import Literal

from ..exceptions import (
    ExecutionError,
    ProviderNotAvailable,
    RateLimitExceeded,
)
from ..exceptions import (
    TimeoutError as DeterminAgentTimeoutError,
)

# Type alias for supported providers
Provider = Literal["claude", "gemini", "copilot", "codex"]


class ProviderAdapter(ABC):
    """
    Abstract base for CLI provider adapters.

    Each adapter handles:
    - Command building (subprocess args)
    - Output parsing (text/JSON/JSONL)
    - Error mapping (stderr → typed exceptions)

    Subclasses must implement:
    - build_command(): Construct CLI command array
    - parse_output(): Parse raw stdout to clean response
    - handle_error(): Map stderr to typed exceptions

    Example:
        ```python
        class MyAdapter(ProviderAdapter):
            def build_command(self, prompt, model, session_flags, ...):
                return ["mycli", "-p", prompt, "-m", model]

            def parse_output(self, raw_output):
                return raw_output.strip()

            def handle_error(self, returncode, stderr):
                return ExecutionError(stderr, provider="mycli")
        ```
    """

    # Provider name for error messages
    provider_name: str = "unknown"

    @abstractmethod
    def build_command(
        self,
        prompt: str,
        model: str,
        session_flags: list[str],
        allow_web: bool = False,
        tools: list[str] | None = None,
        sandbox: str | None = None,
    ) -> list[str]:
        """
        Build the subprocess command array.

        Args:
            prompt: The user prompt to send to the CLI.
            model: Model name (provider-specific, e.g., "sonnet", "gpt-4").
            session_flags: Session management flags from SessionManager.
            allow_web: Enable web search/fetch tools if supported.
            tools: Specific tools to allow (provider-specific).
            sandbox: Sandbox mode (Codex only: read-only/workspace-write/full-access).

        Returns:
            Command array suitable for subprocess.run().

        Example:
            ```python
            cmd = adapter.build_command(
                "Write a poem",
                "sonnet",
                ["--session-id", "abc123"],
                allow_web=True
            )
            # Returns: ["claude", "-p", "Write a poem", "-m", "sonnet", ...]
            ```
        """
        pass

    @abstractmethod
    def parse_output(self, raw_output: str) -> str:
        """
        Parse provider-specific output format.

        Args:
            raw_output: Raw stdout from CLI command.

        Returns:
            Cleaned response text ready for use.

        Notes:
            Different providers use different output formats:
            - Claude/Copilot: Plain text (strip whitespace)
            - Gemini: JSON {"response": "..."}
            - Codex: JSONL events (find turn.completed)
        """
        pass

    @abstractmethod
    def handle_error(self, returncode: int, stderr: str) -> Exception:
        """
        Map provider-specific errors to unified exceptions.

        Args:
            returncode: Process exit code (non-zero).
            stderr: Standard error output from the process.

        Returns:
            Appropriate exception instance:
            - ProviderNotAvailable: CLI not installed
            - RateLimitExceeded: Rate limit hit
            - ExecutionError: Generic execution failure

        Example:
            ```python
            if "command not found" in stderr:
                return ProviderNotAvailable("Claude CLI not installed")
            elif "rate limit" in stderr:
                return RateLimitExceeded("Too many requests")
            return ExecutionError(f"Failed: {stderr}")
            ```
        """
        pass

    def execute(
        self,
        prompt: str,
        model: str,
        session_flags: list[str],
        allow_web: bool = False,
        timeout: int = 120,
    ) -> str:
        """
        Execute the CLI command and return parsed response.

        This is the main entry point for adapter usage. It:
        1. Builds the command using build_command()
        2. Executes via subprocess
        3. Handles errors using handle_error()
        4. Parses output using parse_output()

        Args:
            prompt: The user prompt to send.
            model: Model name or alias.
            session_flags: Session management flags.
            allow_web: Enable web tools.
            timeout: Command timeout in seconds (default: 120).

        Returns:
            Parsed response text.

        Raises:
            ProviderNotAvailable: CLI not installed.
            RateLimitExceeded: Rate limit exceeded.
            ExecutionError: Command execution failed.
            DeterminAgentTimeoutError: Command timed out.
            KeyboardInterrupt: User interrupted.
        """
        cmd = self.build_command(prompt, model, session_flags, allow_web)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode != 0:
                raise self.handle_error(result.returncode, result.stderr)

            return self.parse_output(result.stdout)

        except FileNotFoundError:
            raise ProviderNotAvailable(
                f"CLI command '{cmd[0]}' not found. Please verify the provider is installed.",
                provider=self.provider_name,
            ) from None
        except KeyboardInterrupt:
            # Propagate up to UnifiedAgent/main for graceful exit
            raise
        except subprocess.TimeoutExpired:
            raise DeterminAgentTimeoutError(
                f"CLI command timed out after {timeout}s",
                provider=self.provider_name,
                timeout=timeout,
            ) from None


# Compatibility alias for mkdocstrings and legacy imports
class BaseAdapter(ProviderAdapter):
    """Alias for ProviderAdapter to maintain backward compatibility.

    The documentation generation expects a class named ``BaseAdapter``.
    This subclass does not add any new behavior; it simply inherits all
    functionality from ``ProviderAdapter``.
    """

    pass


# Re-export exceptions and classes for backwards compatibility
__all__ = [
    "ProviderAdapter",
    "BaseAdapter",
    "Provider",
    "ProviderNotAvailable",
    "RateLimitExceeded",
    "ExecutionError",
]
