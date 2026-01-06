"""
Copilot CLI adapter.

This adapter wraps the standalone `copilot` CLI tool for use with
DeterminAgent. It handles command building, output parsing, and error
mapping specific to the Copilot CLI interface.
"""

from ..exceptions import (
    ExecutionError,
    ProviderAuthError,
    ProviderNotAvailable,
    RateLimitExceeded,
    SessionError,
)
from .base import ProviderAdapter


class CopilotAdapter(ProviderAdapter):
    """
    Adapter for the standalone Copilot CLI.

    Supports:
    - Model selection via --model flag
    - Tool access via --allow-all-tools (required for non-interactive prompts)

    Note:
        Copilot doesn't support custom session IDs on creation (unlike Claude's
        --session-id). Its --resume only works with IDs that copilot itself
        created internally. For reliability in multi-agent workflows, session
        resume is disabled - each call starts a fresh session.

    Example:
        ```python
        adapter = CopilotAdapter()
        cmd = adapter.build_command(
            prompt="Explain this code",
            model="balanced",
            session_flags=[],  # Ignored for copilot
        )
        ```
    """

    provider_name: str = "copilot"

    # Copilot-specific model name mappings
    MODEL_MAPPING: dict[str, str] = {
        "haiku": "claude-haiku-4.5",
        "sonnet": "claude-sonnet-4.5",
        "opus": "claude-opus-4.5",
        "fast": "claude-haiku-4.5",
        "balanced": "claude-sonnet-4.5",
        "powerful": "claude-opus-4.5",
        "reasoning": "gpt-5.2",
        "free": "claude-haiku-4.5",
    }

    def build_command(
        self,
        prompt: str,
        model: str,
        session_flags: list[str],
        allow_web: bool = False,
        tools: list[str] | None = None,
        sandbox: str | None = None,  # Unused for Copilot
    ) -> list[str]:
        """
        Build Copilot CLI command.

        Args:
            prompt: The prompt to send to Copilot.
            model: Model name or alias (will be mapped to Copilot model names).
            session_flags: Unused (copilot doesn't support session resume).
            allow_web: Enable broader tool access via --allow-all-tools.
            tools: Additional tools (Copilot uses --allow-all-tools).
            sandbox: Unused (Copilot doesn't support sandbox mode).

        Returns:
            Command array for subprocess execution.

        Note:
            Copilot doesn't support custom session IDs, so session_flags is ignored.
            Each call starts a fresh session.
        """
        cmd = ["copilot", "-p", prompt, "--allow-all-tools"]

        # Add session flags
        cmd.extend(session_flags)

        # Map model name to Copilot-specific name
        copilot_model = self.MODEL_MAPPING.get(model, model)
        if copilot_model:
            cmd.extend(["--model", copilot_model])

        # --allow-all-tools is required for non-interactive mode.

        return cmd

    def parse_output(self, raw_output: str) -> str:
        """
        Parse Copilot output.

        Copilot outputs plain text, so we just strip whitespace.

        Args:
            raw_output: Raw stdout from Copilot CLI.

        Returns:
            Cleaned response text.
        """
        return raw_output.strip()

    def handle_error(self, returncode: int, stderr: str) -> Exception:
        """
        Map Copilot CLI errors to typed exceptions.

        Args:
            returncode: Process exit code.
            stderr: Standard error output.

        Returns:
            Appropriate exception type based on error content.
        """
        err_lower = stderr.lower()

        if "command not found" in err_lower or "not found" in err_lower:
            return ProviderNotAvailable(
                "Copilot CLI not installed. Install: https://github.com/github/copilot-cli",
                provider=self.provider_name,
            )
        elif "rate limit" in err_lower or "too many requests" in err_lower:
            return RateLimitExceeded(
                "Copilot rate limit exceeded. Please wait before retrying.",
                provider=self.provider_name,
            )
        elif (
            "auth" in err_lower
            or "login" in err_lower
            or "unauthorized" in err_lower
            or "not logged in" in err_lower
        ):
            return ProviderAuthError(
                "Copilot authentication failed. Run 'gh auth login' and retry.",
                provider=self.provider_name,
            )
        elif "github copilot" in err_lower and "access" in err_lower:
            return ProviderAuthError(
                "Copilot access required. Ensure your account has an active Copilot subscription.",
                provider=self.provider_name,
            )
        elif "session file is corrupted" in err_lower or "incompatible" in err_lower:
            return SessionError(
                "Copilot session file is corrupted. "
                "Fix: Delete session files with 'rm -rf ~/.copilot/sessions' and retry.",
                provider=self.provider_name,
            )
        else:
            return ExecutionError(
                f"Copilot CLI error (code {returncode}): {stderr}",
                provider=self.provider_name,
                returncode=returncode,
                stderr=stderr,
            )
