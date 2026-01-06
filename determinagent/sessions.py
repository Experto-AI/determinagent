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

    Session support by provider:
    - **Claude**: Full support via `--session-id <uuid>` and `-r <uuid>`
    - **Gemini**: No session resume (always fresh sessions)
    - **Copilot**: No session resume (always fresh sessions)
    - **Codex**: No session resume (always fresh sessions)

    Note:
        Only Claude supports creating sessions with a custom ID on the first call.
        Other providers (Gemini, Copilot, Codex) generate session IDs internally
        and don't expose them for use in multi-agent workflows. For reliability,
        session resume is only enabled for Claude.

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
                       a new UUID will be generated (Gemini defaults to
                       "latest" since it resumes by latest or index).
        """
        self.provider: Provider = provider
        if session_id is None:
            session_id = "latest" if provider == "gemini" else str(uuid.uuid4())
        self.session_id: str = session_id
        self.call_count: int = 0

    def supports_resume(self) -> bool:
        """Return True if the provider supports session resume flags."""
        return self.provider == "claude"

    def get_session_flags(
        self,
        is_first_call: bool | None = None,
    ) -> list[str]:
        """
        Return provider-specific session flags.

        Session support:
        - Claude: `--session-id <uuid>` for first call, `-r <uuid>` for resume
        - Gemini: Always empty (no session resume support)
        - Copilot: Always empty (no session resume support)
        - Codex: Always empty (no session resume support)

        Args:
            is_first_call: Override for first-call detection. If None,
                          uses `call_count == 0` to determine.

        Returns:
            List of CLI flags for session management (only non-empty for Claude).

        Note:
            Only Claude supports creating sessions with custom IDs. Other providers
            generate session IDs internally, making them incompatible with
            multi-agent workflows where each agent needs its own persistent session.
        """
        if not self.supports_resume():
            return []

        if is_first_call is None:
            is_first_call = self.call_count == 0

        if is_first_call:
            return ["--session-id", self.session_id]
        return ["-r", self.session_id]

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
