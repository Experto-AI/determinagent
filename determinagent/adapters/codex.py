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
    - Sandbox execution via --sandbox flag
    - JSONL output parsing via --json
    - Model selection via --model

    Note:
        Codex doesn't support custom session IDs on creation (unlike Claude's
        --session-id). Its `exec resume` only works with IDs that Codex itself
        created internally. For reliability in multi-agent workflows, session
        resume is disabled - each call starts a fresh session.

    Example:
        ```python
        adapter = CodexAdapter()
        cmd = adapter.build_command(
            prompt="Refactor this",
            model="default",
            session_flags=[],  # Ignored for Codex
            sandbox="workspace-write"
        )
        # Returns: ["codex", "exec", "Refactor this",
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
            session_flags: Unused (Codex doesn't support session resume).
            allow_web: Enable web tools.
            tools: Additional tools.
            sandbox: Sandbox mode (read-only, workspace-write, etc).

        Returns:
            Command array for subprocess execution.

        Note:
            Codex doesn't support custom session IDs, so session_flags is ignored.
            Each call starts a fresh session.
        """
        cmd = ["codex", "exec", "--json"]

        # session_flags ignored - Codex doesn't support custom session IDs

        if model:
            cmd.extend(["--model", model])

        # Sandbox configuration
        if sandbox:
            cmd.extend(["--sandbox", sandbox])

        # Keep explicit sandbox values authoritative. --full-auto aliases
        # workspace-write, so only use it when the caller did not request
        # a specific sandbox mode.
        if sandbox is None:
            cmd.append("--full-auto")

        # Prompt is positional for Codex exec
        cmd.append(prompt)

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
                extracted = self._extract_event_content(event)
                if extracted:
                    return extracted
            except json.JSONDecodeError:
                continue

        # Fallback: if no structured event found, return raw output
        # (This helps debugging if CLI errors output plain text)
        return raw_output.strip()

    def _extract_event_content(self, event: dict[str, object]) -> str | None:
        """Extract the final assistant text from known Codex JSONL events."""
        event_type = str(event.get("type", ""))
        if event_type not in {"turn.completed", "response.completed", "message.completed"}:
            return None

        data = event.get("data")
        if isinstance(data, dict):
            for key in ("content", "text", "output_text"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
                if isinstance(value, list):
                    joined = "\n".join(
                        part.strip() for part in value if isinstance(part, str) and part.strip()
                    )
                    if joined:
                        return joined

            message = data.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()

        return None

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
