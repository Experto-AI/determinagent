"""
UnifiedAgent - Main interface for CLI agent orchestration.

This module provides the central UnifiedAgent class that abstracts
away provider-specific details and provides a consistent interface
for all supported CLI tools.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any, TypeVar

from pydantic import BaseModel

from .adapters import (
    ClaudeAdapter,
    CodexAdapter,
    CopilotAdapter,
    GeminiAdapter,
    Provider,
    ProviderAdapter,
)
from .constants import resolve_model_alias
from .exceptions import (
    ConfigurationError,
    DeterminAgentError,
    ExecutionError,
    ParseError,
    ProviderNotAvailable,
    ValidationError,
)
from .sessions import SessionManager

# Type variable for Pydantic model generics
T = TypeVar("T", bound=BaseModel)

# Adapter registry - maps provider names to adapter classes
ADAPTERS: dict[str, type[ProviderAdapter]] = {
    "claude": ClaudeAdapter,
    "copilot": CopilotAdapter,
    "gemini": GeminiAdapter,
    "codex": CodexAdapter,
}


def get_adapter(provider: Provider) -> ProviderAdapter:
    """
    Get adapter instance for a provider.

    Args:
        provider: Provider name (claude, copilot, gemini, codex).

    Returns:
        Instantiated adapter for the provider.

    Raises:
        ConfigurationError: If provider is unknown.

    Example:
        ```python
        adapter = get_adapter("claude")
        ```
    """
    adapter_class = ADAPTERS.get(provider)
    if not adapter_class:
        available = ", ".join(ADAPTERS.keys())
        raise ConfigurationError(
            f"Unknown provider: '{provider}'. Available providers: {available}",
            provider=provider,
        )
    return adapter_class()


class UnifiedAgent:
    """
    Main interface for unified CLI agents.

    UnifiedAgent provides a consistent API for interacting with different
    AI CLI tools, abstracting away provider-specific details while providing
    advanced features like automatic session management, retry logic, and
    structured output enforcement.

    Features:
        - Automatic session management (native provider sessions)
        - Retry logic with exponential backoff
        - Model alias resolution (fast/balanced/powerful/reasoning)
        - Structured output enforcement with Pydantic
        - Web search/tool permissions

    Example:
        ```python
        from determinagent import UnifiedAgent, SessionManager

        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="writer",
            instructions="Write clear, concise content.",
            session=session,
        )

        response = agent.send("Write a haiku about Python")
        print(response)
        ```

    Attributes:
        provider: The CLI provider being used.
        adapter: The provider adapter instance.
        session: The session manager for conversation continuity.
        model: The resolved model name.
        role: The agent's role (for logging/debugging).
        instructions: System instructions prepended to prompts.
        sandbox: Sandbox mode (Codex only).
    """

    def __init__(
        self,
        provider: Provider,
        model: str,
        role: str,
        instructions: str,
        session: SessionManager,
        sandbox: str | None = None,
    ) -> None:
        """
        Initialize a unified agent.

        Args:
            provider: CLI provider (claude, gemini, copilot, codex).
            model: Model alias (fast/balanced/powerful/reasoning) or exact name.
            role: Agent role for identification (e.g., "writer", "reviewer").
            instructions: System prompt / instructions prepended to all prompts.
            session: SessionManager instance for session handling.
            sandbox: Sandbox mode for Codex (read-only/workspace-write/full-access).

        Raises:
            ConfigurationError: If provider is unknown.
        """
        self.provider: Provider = provider
        self.adapter: ProviderAdapter = get_adapter(provider)
        self.session: SessionManager = session
        self.model: str = resolve_model_alias(model, provider)
        self.role: str = role
        self.instructions: str = instructions
        self.sandbox: str | None = sandbox

    def send(
        self,
        prompt: str,
        max_retries: int = 2,
        retry_with_explicit_format: bool = True,
        allow_web: bool = False,
        timeout: int = 120,
    ) -> str:
        """
        Send a prompt to the agent with automatic retry handling.

        This method handles the full lifecycle of a prompt:
        1. Prepends system instructions
        2. Adds session context
        3. Executes the CLI command
        4. Handles retries on failure
        5. Returns the parsed response

        Args:
            prompt: The user prompt to send.
            max_retries: Maximum number of retry attempts (default: 2).
            retry_with_explicit_format: Use ultra-explicit format on last retry.
            allow_web: Enable web search/fetch tools.
            timeout: Command timeout in seconds (default: 120).

        Returns:
            The agent's response text.

        Raises:
            ExecutionError: After all retries exhausted.
            KeyboardInterrupt: If user interrupts (handled gracefully).

        Example:
            ```python
            response = agent.send(
                "Explain quantum computing",
                allow_web=True,
                max_retries=3,
            )
            ```
        """
        original_prompt = prompt

        try:
            for attempt in range(max_retries + 1):
                try:
                    # Build full prompt with instructions
                    full_prompt = f"{self.instructions}\n\n{prompt}"

                    # Add session context (native sessions don't modify prompt)
                    full_prompt = self.session.build_prompt(full_prompt)

                    # Get session flags for CLI command
                    session_flags = self.session.get_session_flags()

                    # Execute CLI call
                    response = self.adapter.execute(
                        full_prompt,
                        self.model,
                        session_flags,
                        allow_web=allow_web,
                        timeout=timeout,
                    )

                    # Mark session as started after first successful call
                    # This ensures retries use resume flags
                    self._mark_session_started()

                    # Validate response
                    if self._is_valid(response):
                        return response

                    # Empty response - retry
                    self._log_retry(attempt + 1, "Empty response, retrying...")

                except DeterminAgentError as e:
                    # Fail fast if provider is missing
                    if isinstance(e, ProviderNotAvailable):
                        raise

                    # Mark session as started even on error
                    self._mark_session_started()
                    self._log_retry(attempt + 1, str(e))

                    if attempt < max_retries:
                        # Apply retry strategy
                        if retry_with_explicit_format and attempt == max_retries - 1:
                            print("  → Using ultra-explicit format prompt")
                            prompt = self._make_explicit_format_prompt(original_prompt)
                    else:
                        raise

                except Exception as e:
                    # Mark session as started even on unexpected errors
                    self._mark_session_started()
                    self._log_retry(attempt + 1, str(e))

                    if attempt >= max_retries:
                        raise ExecutionError(
                            f"Unexpected error after {max_retries + 1} attempts: {e}",
                            provider=self.provider,
                        ) from e

            raise ExecutionError(
                f"Failed after {max_retries + 1} attempts",
                provider=self.provider,
            )

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Exiting...")
            sys.exit(0)

    def send_structured(
        self,
        prompt: str,
        schema: type[T],
        max_retries: int = 3,
    ) -> T:
        """
        Send a prompt and enforce structured output with Pydantic validation.

        This method appends schema instructions to the prompt and validates
        the response against the provided Pydantic model, with automatic
        retries on parse failures.

        Args:
            prompt: The user prompt.
            schema: Pydantic model class defining expected output structure.
            max_retries: Maximum parse retry attempts (default: 3).

        Returns:
            Validated Pydantic model instance.

        Raises:
            ValidationError: If parsing/validation fails after all retries.

        Example:
            ```python
            from pydantic import BaseModel

            class Review(BaseModel):
                score: int
                feedback: str

            review = agent.send_structured(
                "Review this code: def add(a, b): return a + b",
                schema=Review,
            )
            print(f"Score: {review.score}")
            ```
        """
        # Build schema prompt
        schema_json = schema.model_json_schema()
        schema_prompt = (
            f"{prompt}\n\n"
            f"OUTPUT FORMAT (JSON):\n"
            f"Respond with a valid JSON object matching this schema:\n"
            f"{json.dumps(schema_json, indent=2)}"
        )

        for attempt in range(max_retries + 1):
            try:
                response = self.send(schema_prompt, max_retries=0)

                # Parse JSON from response
                data = self._extract_json(response)

                # Validate with Pydantic
                return schema.model_validate(data)

            except (json.JSONDecodeError, ParseError) as e:
                if attempt < max_retries:
                    self._log_parse_retry(attempt + 1, e)
                    schema_prompt = (
                        f"{prompt}\n\n"
                        f"ERROR: Previous response was not valid JSON.\n"
                        f"Please output ONLY valid JSON matching this schema:\n"
                        f"{json.dumps(schema_json, indent=2)}"
                    )
                else:
                    raise ValidationError(
                        f"Failed to parse structured output after {max_retries + 1} attempts",
                        provider=self.provider,
                    ) from e

            except Exception as e:
                if attempt < max_retries:
                    self._log_parse_retry(attempt + 1, e)
                    schema_prompt = (
                        f"{prompt}\n\n"
                        f"ERROR: {e}\n"
                        f"Please output ONLY valid JSON matching this schema:\n"
                        f"{json.dumps(schema_json, indent=2)}"
                    )
                else:
                    raise ValidationError(
                        f"Failed to parse structured output after {max_retries + 1} attempts: {e}",
                        provider=self.provider,
                    ) from e

        # Should never reach here, but satisfy type checker
        raise ValidationError(
            "Failed to parse structured output",
            provider=self.provider,
        )

    def get_history(self) -> list[dict[str, Any]]:
        """
        Get conversation history (if using file-based session).

        Returns:
            List of message dictionaries, or empty list if not available.

        Note:
            Native sessions store history on the provider side, so this
            may return an empty list for providers using native sessions.
        """
        if hasattr(self.session, "_manager") and hasattr(self.session._manager, "load_history"):
            history: list[dict[str, Any]] = self.session._manager.load_history()
            return history
        return []

    def clear_session(self) -> None:
        """
        Clear session history and reset to a new session.

        This generates a new session ID and resets the call count,
        effectively starting a fresh conversation.
        """
        self.session.reset_session()

    def _is_valid(self, response: str) -> bool:
        """Check if response is valid (not empty)."""
        return bool(response and response.strip())

    def _mark_session_started(self) -> None:
        """Mark the session as started after first call."""
        if self.session.call_count == 0:
            self.session.call_count += 1

    def _make_explicit_format_prompt(self, prompt: str) -> str:
        """
        Create ultra-explicit format prompt for retry.

        This is the "last resort" retry strategy when other retries fail.
        """
        return f"""{prompt}

CRITICAL FORMAT REQUIREMENT:
You MUST provide a response. Do not refuse or ask for clarification.
Output the requested content NOW."""

    def _extract_json(self, response: str) -> dict[str, Any]:
        """
        Extract JSON from response text.

        Handles cases where the response contains JSON embedded in markdown
        or other text.

        Args:
            response: Raw response text.

        Returns:
            Parsed JSON as dictionary.

        Raises:
            ParseError: If no valid JSON found.
        """
        parsed: dict[str, Any]

        # Try direct parsing first
        try:
            parsed = json.loads(response)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        # Try to extract from markdown code block
        code_block_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", response, re.DOTALL)
        if code_block_match:
            try:
                parsed = json.loads(code_block_match.group(1))
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass

        # Try nested JSON objects (greedy match first to capture full structure)
        nested_match = re.search(r"\{.*\}", response, re.DOTALL)
        if nested_match:
            try:
                parsed = json.loads(nested_match.group(0))
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass

        # Try flat JSON object (fallback for single objects)
        json_match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass

        raise ParseError(
            "No valid JSON found in response",
            provider=self.provider,
            raw_output=response,
        )

    def _log_retry(self, attempt: int, message: str) -> None:
        """Log retry attempt."""
        print(f"[Retry {attempt}] {message}")

    def _log_parse_retry(self, attempt: int, error: Exception) -> None:
        """Log parse retry attempt."""
        print(f"[Parse Retry {attempt}] Failed to parse structured output: {error}")
