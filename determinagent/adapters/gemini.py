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
    - Headless prompts via --prompt
    - Sandbox and allowed-tool passthrough

    Note:
        Gemini doesn't support custom session IDs on creation (unlike Claude's
        --session-id). Its --resume only works with IDs/indices that Gemini itself
        created internally. `SessionManager` therefore keeps Gemini fresh by default,
        but the low-level adapter will forward any explicit provider-managed
        resume flags passed into `build_command()`.

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
            session_flags: Optional provider-managed resume flags.
            allow_web: Enable web tools (if supported).
            tools: Additional tools.
            sandbox: Unused.

        Returns:
            Command array for subprocess execution.

        Note:
            `SessionManager` does not generate Gemini resume flags, so high-level
            `UnifiedAgent` usage stays on fresh sessions by default.
        """
        cmd = ["gemini", "--prompt", prompt]

        cmd.extend(session_flags)

        # Force JSON output format
        cmd.extend(["--output-format", "json"])

        if model:
            cmd.extend(["--model", model])

        if sandbox:
            cmd.append("--sandbox")

        if tools:
            for tool in tools:
                cmd.extend(["--allowed-tools", tool])

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
            data: Any = json.loads(raw_output)
            extracted = self._extract_text(data)
            return extracted if extracted is not None else raw_output.strip()
        except json.JSONDecodeError:
            # Fallback for plain text or malformed JSON
            return raw_output.strip()

    def _extract_text(self, data: Any) -> str | None:
        """Extract useful text from current Gemini JSON response shapes."""
        if isinstance(data, str):
            text = data.strip()
            return text or None

        if isinstance(data, list):
            for item in data:
                extracted = self._extract_text(item)
                if extracted:
                    return extracted
            return None

        if not isinstance(data, dict):
            return None

        for key in ("response", "text", "content", "output", "message"):
            extracted = self._extract_text(data.get(key))
            if extracted:
                return extracted

        candidates = data.get("candidates")
        if candidates:
            extracted = self._extract_text(candidates)
            if extracted:
                return extracted

        parts = data.get("parts")
        if parts:
            extracted = self._extract_text(parts)
            if extracted:
                return extracted

        for value in data.values():
            extracted = self._extract_text(value)
            if extracted:
                return extracted

        return None

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
