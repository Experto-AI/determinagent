"""
Claude Code CLI adapter.

This adapter wraps the Claude Code CLI tool for use with DeterminAgent.
It handles command building, output parsing, and error mapping specific
to the Claude CLI interface.
"""

from ..exceptions import (
    ExecutionError,
    ProviderAuthError,
    ProviderNotAvailable,
    RateLimitExceeded,
)
from .base import ProviderAdapter


class ClaudeAdapter(ProviderAdapter):
    """
    Adapter for Claude Code CLI.

    Supports:
    - Session management via --session-id and -r flags
    - Model selection via --model flag
    - Web search via --allowedTools WebSearch,WebFetch
    - Custom tool permissions

    Example:
        ```python
        adapter = ClaudeAdapter()
        cmd = adapter.build_command(
            prompt="Write a haiku",
            model="sonnet",
            session_flags=["--session-id", "abc-123"],
        )
        # Returns: ["claude", "--model", "sonnet", "--session-id", "abc-123", "-p", "Write a haiku"]
        ```
    """

    provider_name: str = "claude"

    def build_command(
        self,
        prompt: str,
        model: str,
        session_flags: list[str],
        allow_web: bool = False,
        tools: list[str] | None = None,
        sandbox: str | None = None,  # Unused for Claude
    ) -> list[str]:
        """
        Build Claude CLI command.

        Args:
            prompt: The prompt to send to Claude.
            model: Model name (e.g., "haiku", "sonnet", "opus").
            session_flags: Session management flags (--session-id or -r).
            allow_web: Enable WebSearch and WebFetch tools.
            tools: Additional tools to allow.
            sandbox: Unused (Claude doesn't support sandbox mode).

        Returns:
            Command array for subprocess execution.

        Examples:
            First call:  ["claude", "-p", "prompt", "--session-id", "uuid"]
            Resume:      ["claude", "-p", "prompt", "-r", "uuid"]
            With web:    ["claude", "-p", "prompt", "-r", "uuid",
                          "--allowedTools", "WebSearch,WebFetch"]
        """
        cmd = ["claude"]

        # Add model if specified (put flags before prompt)
        if model:
            cmd.extend(["--model", model])

        # Add session flags (--session-id or -r)
        cmd.extend(session_flags)

        # Add prompt
        cmd.extend(["-p", prompt])

        # Build allowed tools list
        allowed_tools: list[str] = []
        if allow_web:
            allowed_tools.extend(["WebSearch", "WebFetch"])
        if tools:
            allowed_tools.extend(tools)

        if allowed_tools:
            cmd.extend(["--allowedTools", ",".join(allowed_tools)])

        return cmd

    def parse_output(self, raw_output: str) -> str:
        """
        Parse Claude output.

        Claude outputs plain text, so we just strip whitespace.

        Args:
            raw_output: Raw stdout from Claude CLI.

        Returns:
            Cleaned response text.
        """
        return raw_output.strip()

    def handle_error(self, returncode: int, stderr: str) -> Exception:
        """
        Map Claude CLI errors to typed exceptions.

        Args:
            returncode: Process exit code.
            stderr: Standard error output.

        Returns:
            Appropriate exception type based on error content.
        """
        err_lower = stderr.lower()

        if "command not found" in err_lower or "not found" in err_lower:
            return ProviderNotAvailable(
                "Claude CLI not installed. Install with: npm install -g @anthropic-ai/claude-cli",
                provider=self.provider_name,
            )
        elif "rate limit" in err_lower or "too many requests" in err_lower:
            return RateLimitExceeded(
                "Claude rate limit exceeded. Please wait before retrying.",
                provider=self.provider_name,
            )
        elif "api key" in err_lower or "unauthorized" in err_lower or "auth" in err_lower:
            return ProviderAuthError(
                "Claude authentication failed. Check your API key configuration.",
                provider=self.provider_name,
            )
        elif "invalid model" in err_lower:
            return ExecutionError(
                f"Invalid model specified: {stderr}",
                provider=self.provider_name,
                returncode=returncode,
                stderr=stderr,
            )
        else:
            return ExecutionError(
                f"Claude CLI error (code {returncode}): {stderr}",
                provider=self.provider_name,
                returncode=returncode,
                stderr=stderr,
            )
