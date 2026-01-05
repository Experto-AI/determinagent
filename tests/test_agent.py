"""
Tests for UnifiedAgent.

Tests retry logic, structured output, and session management.
"""

from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from determinagent import SessionManager, UnifiedAgent
from determinagent.agent import get_adapter
from determinagent.exceptions import (
    ConfigurationError,
    ExecutionError,
    ParseError,
    ValidationError,
)


class SimpleReview(BaseModel):
    """Simple schema for testing structured output."""

    score: int
    feedback: str


class ComplexResult(BaseModel):
    """Complex schema for testing nested structured output."""

    title: str
    sections: list[str]
    metadata: dict[str, str]


class TestGetAdapter:
    """Tests for adapter factory function."""

    def test_get_adapter_claude_returns_claude_adapter(self) -> None:
        """Test getting Claude adapter."""
        from determinagent.adapters import ClaudeAdapter

        adapter = get_adapter("claude")
        assert isinstance(adapter, ClaudeAdapter)

    def test_get_adapter_copilot_returns_copilot_adapter(self) -> None:
        """Test getting Copilot adapter."""
        from determinagent.adapters import CopilotAdapter

        adapter = get_adapter("copilot")
        assert isinstance(adapter, CopilotAdapter)

    def test_get_adapter_gemini_returns_gemini_adapter(self) -> None:
        """Test getting Gemini adapter."""
        from determinagent.adapters import GeminiAdapter

        adapter = get_adapter("gemini")
        assert isinstance(adapter, GeminiAdapter)

    def test_get_adapter_codex_returns_codex_adapter(self) -> None:
        """Test getting Codex adapter."""
        from determinagent.adapters import CodexAdapter

        adapter = get_adapter("codex")
        assert isinstance(adapter, CodexAdapter)

    def test_get_adapter_unknown_provider_raises_configuration_error(self) -> None:
        """Test that unknown provider raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            get_adapter("unknown")  # type: ignore

        assert "Unknown provider" in str(exc_info.value)
        assert "unknown" in str(exc_info.value)


class TestUnifiedAgentInit:
    """Tests for UnifiedAgent initialization."""

    def test_init_basic_sets_attributes_correctly(self) -> None:
        """Test basic agent initialization."""
        # Arrange
        session = SessionManager("claude")
        # Act
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="tester",
            instructions="You are a test agent.",
            session=session,
        )
        # Assert
        assert agent.provider == "claude"
        assert agent.role == "tester"
        assert agent.instructions == "You are a test agent."
        assert agent.session is session

    def test_init_model_alias_resolves_to_actual_name(self) -> None:
        """Test that model aliases are resolved."""
        # Arrange
        session = SessionManager("claude")
        # Act
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="tester",
            instructions="Test",
            session=session,
        )
        # Assert
        # "balanced" should resolve to "sonnet" for Claude
        assert agent.model == "sonnet"


class TestUnifiedAgentSend:
    """Tests for UnifiedAgent.send method."""

    def test_send_success_returns_parsed_response(self, mock_subprocess: MagicMock) -> None:
        """Test successful send."""
        # Arrange
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Hello, world!",
            stderr="",
        )
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="greeter",
            instructions="Say hello.",
            session=session,
        )
        # Act
        result = agent.send("Greet me")
        # Assert
        assert result == "Hello, world!"
        assert session.call_count == 1

    def test_send_includes_system_instructions_in_prompt(self, mock_subprocess: MagicMock) -> None:
        """Test that instructions are included in prompt."""
        # Arrange
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Response",
            stderr="",
        )
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="test",
            instructions="SYSTEM: Be helpful",
            session=session,
        )
        # Act
        agent.send("User prompt")
        # Assert
        call_args = mock_subprocess.call_args[0][0]
        p_idx = call_args.index("-p")
        prompt = call_args[p_idx + 1]
        assert "SYSTEM: Be helpful" in prompt
        assert "User prompt" in prompt

    def test_send_empty_response_triggers_retry(self, mock_subprocess: MagicMock) -> None:
        """Test retry on empty response."""
        # Arrange
        # First call returns empty, second returns content
        mock_subprocess.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),
            MagicMock(returncode=0, stdout="Actual response", stderr=""),
        ]
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="test",
            instructions="Test",
            session=session,
        )
        # Act
        result = agent.send("Test", max_retries=2)
        # Assert
        assert result == "Actual response"
        assert mock_subprocess.call_count == 2

    def test_send_keyboard_interrupt_exits_gracefully(self, mock_subprocess: MagicMock) -> None:
        """Test that KeyboardInterrupt is handled gracefully."""
        # Arrange
        mock_subprocess.side_effect = KeyboardInterrupt()
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="test",
            instructions="Test",
            session=session,
        )
        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            agent.send("Test")
        assert exc_info.value.code == 0

    def test_send_unexpected_error_raises_execution_error(self, mock_subprocess: MagicMock) -> None:
        """Test that unexpected errors raise ExecutionError."""
        # Arrange
        mock_subprocess.side_effect = Exception("Crash!")
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="test",
            instructions="Test",
            session=session,
        )
        # Act & Assert
        with pytest.raises(ExecutionError, match="Unexpected error after 3 attempts"):
            agent.send("Test", max_retries=2)

    def test_send_determinagent_error_retries_and_raises(self, mock_subprocess: MagicMock) -> None:
        """Test that DeterminAgentErrors are caught and retried."""
        # Arrange
        mock_subprocess.side_effect = ExecutionError("Execution failed", provider="claude")
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="test",
            instructions="Test",
            session=session,
        )
        # Act & Assert
        with pytest.raises(ExecutionError, match="Execution failed"):
            agent.send("Test", max_retries=1)
        assert mock_subprocess.call_count == 2

    def test_send_retry_with_explicit_format(self, mock_subprocess: MagicMock) -> None:
        """Test that explicit format is used on last retry."""
        # Arrange
        mock_subprocess.side_effect = [
            ExecutionError("Fail 1", provider="claude"),
            MagicMock(returncode=0, stdout="Success", stderr=""),
        ]
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="test",
            instructions="Test",
            session=session,
        )
        # Act
        result = agent.send("Original prompt", max_retries=1, retry_with_explicit_format=True)
        # Assert
        assert result == "Success"
        # Second call should have used the explicit format
        call_args = mock_subprocess.call_args[0][0]
        prompt = call_args[call_args.index("-p") + 1]
        assert "CRITICAL FORMAT REQUIREMENT" in prompt


class TestUnifiedAgentSendStructured:
    """Tests for structured output enforcement."""

    def test_send_structured_success_returns_validated_model(
        self, mock_subprocess: MagicMock
    ) -> None:
        """Test successful structured output."""
        # Arrange
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout='{"score": 8, "feedback": "Good work!"}',
            stderr="",
        )
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="reviewer",
            instructions="Review code.",
            session=session,
        )
        # Act
        result = agent.send_structured("Review this", schema=SimpleReview)
        # Assert
        assert isinstance(result, SimpleReview)
        assert result.score == 8
        assert result.feedback == "Good work!"

    def test_send_structured_invalid_json_raises_validation_error(
        self, mock_subprocess: MagicMock
    ) -> None:
        """Test that ValidationError is raised after max retries."""
        # Arrange
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Always invalid",
            stderr="",
        )
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="test",
            instructions="Test",
            session=session,
        )
        # Act & Assert
        with pytest.raises(ValidationError):
            agent.send_structured("Test", schema=SimpleReview, max_retries=1)

    def test_send_structured_unexpected_error_retries(self, mock_subprocess: MagicMock) -> None:
        """Test that unexpected errors in structured output are retried."""
        # Arrange
        mock_subprocess.side_effect = [
            Exception("Unexpected!"),
            MagicMock(returncode=0, stdout='{"score": 10, "feedback": "fixed"}', stderr=""),
        ]
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude",
            model="balanced",
            role="test",
            instructions="Test",
            session=session,
        )
        # Act
        result = agent.send_structured("Test", schema=SimpleReview, max_retries=1)
        # Assert
        assert result.score == 10
        assert mock_subprocess.call_count == 2


class TestExtractJson:
    """Tests for JSON extraction from responses."""

    def test_extract_json_direct_returns_dict(self) -> None:
        """Test extraction of direct JSON."""
        # Arrange
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude", model="balanced", role="test", instructions="T", session=session
        )
        # Act
        result = agent._extract_json('{"key": "value"}')
        # Assert
        assert result == {"key": "value"}

    def test_extract_json_from_markdown_returns_correct_data(self) -> None:
        """Test extraction from markdown code block."""
        # Arrange
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude", model="balanced", role="test", instructions="T", session=session
        )
        # Act
        result = agent._extract_json('```json\n{"key": "value"}\n```')
        # Assert
        assert result == {"key": "value"}

    def test_extract_json_no_valid_json_raises_parse_error(self) -> None:
        """Test that ParseError is raised when no JSON found."""
        # Arrange
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude", model="balanced", role="test", instructions="T", session=session
        )
        # Act & Assert
        with pytest.raises(ParseError):
            agent._extract_json("No JSON here at all")

    def test_extract_json_various_formats(self) -> None:
        """Test extraction from various tricky formats."""
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude", model="balanced", role="test", instructions="T", session=session
        )

        # Markdown without lang tag
        assert agent._extract_json('```\n{"a":1}\n```') == {"a": 1}
        # Random text around JSON
        assert agent._extract_json('Here is the result: {"a":1} hope you like it') == {"a": 1}
        # Nested JSON extraction - returns full object due to corrected regex order
        assert agent._extract_json('Result: {"a": {"b": 1}}') == {"a": {"b": 1}}


class TestUnifiedAgentHistory:
    """Tests for history and session management."""

    def test_get_history_empty_by_default(self) -> None:
        """Test getting history for native session (should be empty)."""
        session = SessionManager("claude")
        agent = UnifiedAgent(
            provider="claude", model="balanced", role="test", instructions="T", session=session
        )
        assert agent.get_history() == []

    def test_clear_session_resets_session(self) -> None:
        """Test clearing session."""
        session = SessionManager("claude")
        session.call_count = 5
        agent = UnifiedAgent(
            provider="claude", model="balanced", role="test", instructions="T", session=session
        )

        old_id = session.session_id
        agent.clear_session()

        assert session.call_count == 0
        assert session.session_id != old_id
