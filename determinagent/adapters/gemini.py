"""
Gemini CLI adapter.

This adapter wraps the Google Gemini CLI tool for use with DeterminAgent.
It handles command building, output parsing, and error mapping specific
to the Gemini CLI interface.
"""

import json
from typing import Any

from ..exceptions import (
    ExecutionError,
    ProviderAuthError,
    ProviderNotAvailable,
    RateLimitExceeded,
)
from .base import ProviderAdapter


class GeminiAdapter(ProviderAdapter):
    """
    Adapter for Google Gemini CLI.

    Supports:
    - JSON output parsing via --output-format json
    - Model selection via --model flag

    Note:
        Gemini doesn't support custom session IDs on creation (unlike Claude's
        --session-id). Its --resume only works with IDs/indices that Gemini itself
        created internally. For reliability in multi-agent workflows, session
        resume is disabled - each call starts a fresh session.

    Example:
        ```python
        adapter = GeminiAdapter()
        cmd = adapter.build_command(
            prompt="Explain this",
            model="gemini-1.5-pro",
            session_flags=[],  # Ignored for Gemini
        )
        # Returns: ["gemini", "Explain this", "--output-format", "json",
        #           "--model", "gemini-1.5-pro"]
        ```
    """

    provider_name: str = "gemini"

    def build_command(
        self,
        prompt: str,
        model: str,
        session_flags: list[str],
        allow_web: bool = False,
        tools: list[str] | None = None,
        sandbox: str | None = None,  # Unused for Gemini
    ) -> list[str]:
        """
        Build Gemini CLI command.

        Args:
            prompt: The prompt to send to Gemini.
            model: Model name.
            session_flags: Unused (Gemini doesn't support session resume).
            allow_web: Enable web tools (if supported).
            tools: Additional tools.
            sandbox: Unused.

        Returns:
            Command array for subprocess execution.

        Note:
            Gemini doesn't support custom session IDs, so session_flags is ignored.
            Each call starts a fresh session.
        """
        # Prompt is positional; -p/--prompt is deprecated.
        cmd = ["gemini", prompt]

        # session_flags ignored - Gemini doesn't support custom session IDs

        # Force JSON output format
        cmd.extend(["--output-format", "json"])

        if model:
            cmd.extend(["--model", model])

        return cmd

    def parse_output(self, raw_output: str) -> str:
        """
        Parse Gemini JSON output.

        Args:
            raw_output: Raw stdout from Gemini CLI.

        Returns:
            Cleaned response text.
        """
        try:
            data: dict[str, Any] = json.loads(raw_output)
            # Assuming the JSON structure has a "response" key based on PLAN.md notes
            # If not, we might need to adjust.
            return str(data.get("response", raw_output))
        except json.JSONDecodeError:
            # Fallback for plain text or malformed JSON
            return raw_output.strip()

    def handle_error(self, returncode: int, stderr: str) -> Exception:
        """
        Map Gemini CLI errors to typed exceptions.

        Args:
            returncode: Process exit code.
            stderr: Standard error output.

        Returns:
            Appropriate exception type.
        """
        err_lower = stderr.lower()

        if "command not found" in err_lower or "not found" in err_lower:
            return ProviderNotAvailable(
                "Gemini CLI not installed. Please install the Gemini CLI tool.",
                provider=self.provider_name,
            )
        elif "quota" in err_lower or "limit" in err_lower:
            return RateLimitExceeded(
                "Gemini quota/rate limit exceeded.",
                provider=self.provider_name,
            )
        elif "auth" in err_lower or "credential" in err_lower:
            return ProviderAuthError(
                "Gemini authentication failed. Check your credentials.",
                provider=self.provider_name,
            )
        else:
            return ExecutionError(
                f"Gemini CLI error (code {returncode}): {stderr}",
                provider=self.provider_name,
                returncode=returncode,
                stderr=stderr,
            )
