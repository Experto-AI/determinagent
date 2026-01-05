"""
Session management for CLI providers.

This module handles session continuity across CLI calls, using each
provider's native session capabilities for optimal performance.
"""

from __future__ import annotations

import uuid
from typing import Literal

# Type alias for supported providers
Provider = Literal["claude", "gemini", "copilot", "codex"]


class SessionManager:
    """
    Manages CLI sessions using native provider capabilities.

    All four supported CLIs have native session support:
    - Claude:  `--session-id <uuid>`, `-r <uuid>` for resume
    - Gemini:  `--resume <uuid>` for resume
    - Copilot: `--resume <sessionId>` for resume
    - Codex:   `exec resume <id>` subcommand

    Using native sessions provides optimal performance as the provider
    handles context storage and management.

    Example:
        ```python
        session = SessionManager("claude")

        # First call - creates new session
        flags = session.get_session_flags()
        # Returns: ["--session-id", "uuid-here"]

        session.call_count = 1

        # Subsequent calls - resume session
        flags = session.get_session_flags()
        # Returns: ["-r", "uuid-here"]
        ```

    Attributes:
        provider: The CLI provider being used.
        session_id: Unique identifier for this session.
        call_count: Number of calls made in this session.
    """

    def __init__(
        self,
        provider: Provider,
        session_id: str | None = None,
    ) -> None:
        """
        Initialize a session manager.

        Args:
            provider: CLI provider (claude, gemini, copilot, codex).
            session_id: Optional explicit session ID. If not provided,
                       a new UUID will be generated.
        """
        self.provider: Provider = provider
        self.session_id: str = session_id or str(uuid.uuid4())
        self.call_count: int = 0

    def get_session_flags(
        self,
        is_first_call: bool | None = None,
    ) -> list[str]:
        """
        Return provider-specific session flags.

        Each provider has its own syntax for session management:
        - Claude: `--session-id <uuid>` for first call, `-r <uuid>` for resume
        - Gemini: (none) for first call, `--resume <uuid>` for resume
        - Copilot: (none) for first call, `--resume <id>` for resume
        - Codex: Returns `["resume", "<id>"]` which the adapter handles

        Args:
            is_first_call: Override for first-call detection. If None,
                          uses `call_count == 0` to determine.

        Returns:
            List of CLI flags for session management.

        Note:
            For Codex, the adapter (not session manager) handles the
            subcommand structure (`exec` vs `exec resume <id>`).
        """
        if is_first_call is None:
            is_first_call = self.call_count == 0

        if self.provider == "claude":
            if is_first_call:
                return ["--session-id", self.session_id]
            else:
                return ["-r", self.session_id]

        elif self.provider == "gemini":
            if is_first_call:
                return []  # Gemini auto-creates session
            else:
                return ["--resume", self.session_id]

        elif self.provider == "copilot":
            if is_first_call:
                return []  # Copilot auto-creates session
            else:
                return ["--resume", self.session_id]

        elif self.provider == "codex":
            # Codex uses subcommands, not flags
            # The adapter handles "exec" vs "exec resume <id>"
            if is_first_call:
                return []
            else:
                return ["resume", self.session_id]

        return []

    def build_prompt(self, prompt: str) -> str:
        """
        Build the prompt with any session-specific modifications.

        For native sessions, no modification is needed as the provider
        handles context persistence.

        Args:
            prompt: The original prompt text.

        Returns:
            The prompt (unmodified for native sessions).
        """
        # Native sessions don't need prompt modification
        return prompt

    def save_exchange(self, prompt: str, response: str) -> None:
        """
        Save an exchange to session history.

        For native sessions, this just increments the call count
        as the provider handles actual storage.

        Args:
            prompt: The prompt that was sent.
            response: The response that was received.

        Note:
            For file-based sessions (not yet implemented), this would
            save the exchange to the session file.
        """
        self.call_count += 1

    def reset_session(self) -> None:
        """
        Reset to a new session.

        Generates a new session ID and resets the call count,
        effectively starting a fresh conversation.
        """
        self.session_id = str(uuid.uuid4())
        self.call_count = 0

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"SessionManager(provider={self.provider!r}, "
            f"session_id={self.session_id!r}, "
            f"call_count={self.call_count})"
        )
