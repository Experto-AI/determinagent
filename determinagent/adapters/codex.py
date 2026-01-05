"""
Codex CLI adapter.

This adapter wraps the Codex CLI tool for use with DeterminAgent.
It handles command building, output parsing, and error mapping specific
to the Codex CLI interface.
"""

import json

from ..exceptions import (
    ExecutionError,
    ProviderAuthError,
    ProviderNotAvailable,
    SandboxViolation,
)
from .base import ProviderAdapter


class CodexAdapter(ProviderAdapter):
    """
    Adapter for Codex CLI.

    Supports:
    - Session management via `exec resume <id>` subcommand
    - Sandbox execution via --sandbox flag
    - JSONL output parsing (analyzing turn events)

    Example:
        ```python
        adapter = CodexAdapter()
        cmd = adapter.build_command(
            prompt="Refactor this",
            model="default",
            session_flags=["resume", "abc-123"],
            sandbox="workspace-write"
        )
        # Returns: ["codex", "exec", "resume", "abc-123", "Refactor this",
        #           "--sandbox", "workspace-write", "--full-auto"]
        ```
    """

    provider_name: str = "codex"

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
        Build Codex CLI command.

        Args:
            prompt: The user prompt.
            model: Model name (often unused for Codex/default).
            session_flags: Session flags (["resume", <id>] or []).
            allow_web: Enable web tools.
            tools: Additional tools.
            sandbox: Sandbox mode (read-only, workspace-write, etc).

        Returns:
            Command array for subprocess execution.
        """
        cmd = ["codex", "exec"]

        # Add session flags (subcommand arguments)
        cmd.extend(session_flags)

        # Prompt is positional for Codex exec
        cmd.append(prompt)

        # Sandbox configuration
        if sandbox:
            cmd.extend(["--sandbox", sandbox])

        # Always enable full automation
        cmd.append("--full-auto")

        return cmd

    def parse_output(self, raw_output: str) -> str:
        """
        Parse Codex JSONL output.

        Looks for 'turn.completed' event to extract the final response.

        Args:
            raw_output: Raw stdout from Codex CLI (JSONL stream).

        Returns:
            Cleaned response text.
        """
        lines = raw_output.strip().splitlines()

        # Iterate to find the completion event
        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)
                if event.get("type") == "turn.completed":
                    # Extract content from data payload
                    data = event.get("data", {})
                    return str(data.get("content", ""))
            except json.JSONDecodeError:
                continue

        # Fallback: if no structured event found, return raw output
        # (This helps debugging if CLI errors output plain text)
        return raw_output.strip()

    def handle_error(self, returncode: int, stderr: str) -> Exception:
        """
        Map Codex CLI errors to typed exceptions.

        Args:
            returncode: Process exit code.
            stderr: Standard error output.

        Returns:
            Appropriate exception type.
        """
        err_lower = stderr.lower()

        if "command not found" in err_lower or "not found" in err_lower:
            return ProviderNotAvailable(
                "Codex CLI not installed. Please install the Codex CLI tool.",
                provider=self.provider_name,
            )
        elif "sandbox" in err_lower and ("violation" in err_lower or "denied" in err_lower):
            return SandboxViolation(
                f"Sandbox violation detected: {stderr}",
                provider=self.provider_name,
            )
        elif "auth" in err_lower or "login" in err_lower:
            return ProviderAuthError(
                "Codex authentication failed.",
                provider=self.provider_name,
            )
        else:
            return ExecutionError(
                f"Codex CLI error (code {returncode}): {stderr}",
                provider=self.provider_name,
                returncode=returncode,
                stderr=stderr,
            )
