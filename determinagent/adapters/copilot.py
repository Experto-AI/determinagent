"""
GitHub Copilot CLI adapter.

This adapter wraps the GitHub Copilot CLI tool for use with DeterminAgent.
It handles command building, output parsing, and error mapping specific
to the Copilot CLI interface.
"""

from ..exceptions import (
    ExecutionError,
    ProviderAuthError,
    ProviderNotAvailable,
    RateLimitExceeded,
)
from .base import ProviderAdapter


class CopilotAdapter(ProviderAdapter):
    """
    Adapter for GitHub Copilot CLI.

    Supports:
    - Session management via --resume flag
    - Model selection via --model flag
    - Tool access via --allow-all-tools and --allow-all-urls

    Note: Copilot uses different model naming conventions than Claude.
    This adapter provides a mapping for convenient aliasing.

    Example:
        ```python
        adapter = CopilotAdapter()
        cmd = adapter.build_command(
            prompt="Explain this code",
            model="balanced",
            session_flags=["--resume", "session-id"],
        )
        ```
    """

    provider_name: str = "copilot"

    # Copilot-specific model name mappings
    MODEL_MAPPING: dict[str, str] = {
        "haiku": "claude-haiku-4.5",
        "sonnet": "claude-sonnet-4-5",
        "opus": "claude-sonnet-4",  # No direct Opus equivalent in Copilot
        "fast": "claude-haiku-4.5",
        "balanced": "claude-sonnet-4-5",
        "powerful": "gpt-5",
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
            session_flags: Session management flags (--resume or empty).
            allow_web: Enable web access via --allow-all-urls.
            tools: Additional tools (Copilot uses --allow-all-tools).
            sandbox: Unused (Copilot doesn't support sandbox mode).

        Returns:
            Command array for subprocess execution.

        Examples:
            First call:  ["copilot", "-p", "prompt"]
            Resume:      ["copilot", "-p", "prompt", "--resume", "uuid"]
            With web:    ["copilot", "-p", "prompt", "--allow-all-tools", "--allow-all-urls"]
        """
        cmd = ["copilot", "-p", prompt]

        # Add session flags
        cmd.extend(session_flags)

        # Map model name to Copilot-specific name
        copilot_model = self.MODEL_MAPPING.get(model, model)
        if copilot_model:
            cmd.extend(["--model", copilot_model])

        # Copilot uses --allow-all-tools for extended access
        if allow_web or tools:
            cmd.append("--allow-all-tools")
            if allow_web:
                cmd.append("--allow-all-urls")

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
                "Copilot CLI not installed. Install with: gh extension install github/copilot-cli",
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
                "Copilot authentication failed. Run 'gh auth login' to authenticate.",
                provider=self.provider_name,
            )
        elif "github copilot" in err_lower and "access" in err_lower:
            return ProviderAuthError(
                "GitHub Copilot access required. Ensure you have an active Copilot subscription.",
                provider=self.provider_name,
            )
        else:
            return ExecutionError(
                f"Copilot CLI error (code {returncode}): {stderr}",
                provider=self.provider_name,
                returncode=returncode,
                stderr=stderr,
            )
