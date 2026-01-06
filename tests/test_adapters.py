"""
Tests for provider adapters.

Tests command building, output parsing, and error handling for all adapters.
"""

from unittest.mock import MagicMock

import pytest

from determinagent.adapters import (
    ClaudeAdapter,
    CodexAdapter,
    CopilotAdapter,
    GeminiAdapter,
)
from determinagent.exceptions import (
    ExecutionError,
    ProviderAuthError,
    ProviderNotAvailable,
    RateLimitExceeded,
    SandboxViolation,
)


class TestClaudeAdapter:
    """Tests for the Claude Code CLI adapter."""

    def test_build_command_first_call_returns_correct_args(self) -> None:
        """Test command building for first session call."""
        # Arrange
        adapter = ClaudeAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Write a poem",
            model="sonnet",
            session_flags=["--session-id", "test-uuid-123"],
        )
        # Assert
        assert "claude" in cmd
        assert "--model" in cmd
        assert "sonnet" in cmd
        assert "--session-id" in cmd
        assert "test-uuid-123" in cmd
        assert "-p" in cmd
        assert "Write a poem" in cmd

    def test_build_command_resume_returns_correct_args(self) -> None:
        """Test command building for session resume."""
        # Arrange
        adapter = ClaudeAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Continue the poem",
            model="sonnet",
            session_flags=["-r", "test-uuid-123"],
        )
        # Assert
        assert "-r" in cmd
        assert "test-uuid-123" in cmd
        assert "-p" in cmd

    def test_build_command_with_web_returns_web_tools(self) -> None:
        """Test command building with web tools enabled."""
        # Arrange
        adapter = ClaudeAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Search for info",
            model="haiku",
            session_flags=["--session-id", "test-123"],
            allow_web=True,
        )
        # Assert
        assert "--allowedTools" in cmd
        tools_idx = cmd.index("--allowedTools")
        tools_value = cmd[tools_idx + 1]
        assert "WebSearch" in tools_value
        assert "WebFetch" in tools_value

    def test_build_command_with_custom_tools_returns_tools(self) -> None:
        """Test command building with custom tools."""
        # Arrange
        adapter = ClaudeAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Test",
            model="sonnet",
            session_flags=[],
            tools=["CustomTool1", "CustomTool2"],
        )
        # Assert
        assert "--allowedTools" in cmd
        tools_idx = cmd.index("--allowedTools")
        tools_value = cmd[tools_idx + 1]
        assert "CustomTool1" in tools_value
        assert "CustomTool2" in tools_value

    def test_build_command_with_web_and_custom_tools_returns_all_tools(self) -> None:
        """Test command building with both web and custom tools."""
        # Arrange
        adapter = ClaudeAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Test",
            model="sonnet",
            session_flags=[],
            allow_web=True,
            tools=["CustomTool"],
        )
        # Assert
        assert "--allowedTools" in cmd
        tools_idx = cmd.index("--allowedTools")
        tools_value = cmd[tools_idx + 1]
        assert "WebSearch" in tools_value
        assert "WebFetch" in tools_value
        assert "CustomTool" in tools_value

    def test_parse_output_with_whitespace_strips_it(self) -> None:
        """Test that output parsing strips whitespace."""
        # Arrange
        adapter = ClaudeAdapter()
        # Act
        result = adapter.parse_output("  Hello World  \n\n")
        # Assert
        assert result == "Hello World"

    def test_parse_output_with_empty_string_returns_empty(self) -> None:
        """Test parsing empty output."""
        # Arrange
        adapter = ClaudeAdapter()
        # Act
        result = adapter.parse_output("")
        # Assert
        assert result == ""

    def test_handle_error_command_not_found_raises_provider_not_available(self) -> None:
        """Test error handling for missing CLI."""
        # Arrange
        adapter = ClaudeAdapter()
        # Act
        error = adapter.handle_error(127, "claude: command not found")
        # Assert
        assert isinstance(error, ProviderNotAvailable)
        assert "not installed" in str(error).lower()

    def test_handle_error_rate_limit_raises_rate_limit_exceeded(self) -> None:
        """Test error handling for rate limiting."""
        # Arrange
        adapter = ClaudeAdapter()
        # Act
        error = adapter.handle_error(1, "Rate limit exceeded. Please wait.")
        # Assert
        assert isinstance(error, RateLimitExceeded)
        assert "rate limit" in str(error).lower()

    def test_handle_error_auth_raises_provider_auth_error(self) -> None:
        """Test error handling for authentication failure."""
        # Arrange
        adapter = ClaudeAdapter()
        # Act
        error = adapter.handle_error(1, "API key not configured")
        # Assert
        assert isinstance(error, ProviderAuthError)
        assert "auth" in str(error).lower()

    def test_handle_error_generic_raises_execution_error(self) -> None:
        """Test error handling for generic errors."""
        # Arrange
        adapter = ClaudeAdapter()
        # Act
        error = adapter.handle_error(1, "Something went wrong")
        # Assert
        assert isinstance(error, ExecutionError)
        assert error.returncode == 1
        assert "Something went wrong" in error.stderr

    def test_execute_success_returns_parsed_output(self, mock_subprocess: MagicMock) -> None:
        """Test successful command execution."""
        # Arrange
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Hello from Claude",
            stderr="",
        )
        adapter = ClaudeAdapter()
        # Act
        result = adapter.execute(
            prompt="Say hello",
            model="sonnet",
            session_flags=["--session-id", "test"],
        )
        # Assert
        assert result == "Hello from Claude"
        mock_subprocess.assert_called_once()

    def test_execute_failure_raises_execution_error(self, mock_subprocess: MagicMock) -> None:
        """Test command execution failure."""
        # Arrange
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error occurred",
        )
        adapter = ClaudeAdapter()
        # Act & Assert
        with pytest.raises(ExecutionError):
            adapter.execute(
                prompt="Test",
                model="sonnet",
                session_flags=[],
            )


class TestCopilotAdapter:
    """Tests for the GitHub Copilot CLI adapter."""

    def test_build_command_basic_returns_correct_args(self) -> None:
        """Test basic command building."""
        # Arrange
        adapter = CopilotAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Explain this code",
            model="balanced",
            session_flags=[],
        )
        # Assert
        assert "copilot" in cmd
        assert "-p" in cmd
        assert "Explain this code" in cmd
        assert "--model" in cmd

    def test_build_command_resume_returns_resume_flag(self) -> None:
        """Test command building with session resume."""
        # Arrange
        adapter = CopilotAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Continue",
            model="fast",
            session_flags=["--resume", "session-123"],
        )
        # Assert
        assert "--resume" in cmd
        assert "session-123" in cmd

    def test_build_command_with_web_returns_tool_flags(self) -> None:
        """Test command building with tool access."""
        # Arrange
        adapter = CopilotAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Search",
            model="balanced",
            session_flags=[],
            allow_web=True,
        )
        # Assert
        assert "--allow-all-tools" in cmd

    def test_model_mapping_resolves_aliases(self) -> None:
        """Test that model aliases are correctly mapped."""
        # Arrange
        adapter = CopilotAdapter()

        # Act & Assert
        cmd_fast = adapter.build_command("test", "fast", [])
        assert "claude-haiku-4.5" in cmd_fast

        cmd_balanced = adapter.build_command("test", "balanced", [])
        assert "claude-sonnet-4.5" in cmd_balanced

        cmd_powerful = adapter.build_command("test", "powerful", [])
        assert "gpt-5" in cmd_powerful

    def test_model_passthrough_keeps_unknown_names(self) -> None:
        """Test that unknown model names pass through unchanged."""
        # Arrange
        adapter = CopilotAdapter()
        # Act
        cmd = adapter.build_command("test", "custom-model-name", [])
        # Assert
        assert "custom-model-name" in cmd

    def test_parse_output_strips_whitespace(self) -> None:
        """Test output parsing."""
        # Arrange
        adapter = CopilotAdapter()
        # Act
        result = adapter.parse_output("  Response text  \n")
        # Assert
        assert result == "Response text"

    def test_handle_error_not_found_raises_provider_not_available(self) -> None:
        """Test error handling for missing CLI."""
        # Arrange
        adapter = CopilotAdapter()
        # Act
        error = adapter.handle_error(127, "copilot: command not found")
        # Assert
        assert isinstance(error, ProviderNotAvailable)

    def test_handle_error_auth_raises_provider_auth_error(self) -> None:
        """Test error handling for auth failure."""
        # Arrange
        adapter = CopilotAdapter()
        # Act
        error = adapter.handle_error(1, "Not logged in to GitHub")
        # Assert
        assert isinstance(error, ProviderAuthError)

    def test_handle_error_rate_limit_raises_rate_limit_exceeded(self) -> None:
        """Test error handling for rate limiting."""
        # Arrange
        adapter = CopilotAdapter()
        # Act
        error = adapter.handle_error(1, "Too many requests")
        # Assert
        assert isinstance(error, RateLimitExceeded)


class TestAdapterProviderName:
    """Test that adapters have correct provider names."""

    def test_claude_provider_name_returns_claude(self) -> None:
        """Test Claude adapter has correct provider name."""
        adapter = ClaudeAdapter()
        assert adapter.provider_name == "claude"

    def test_copilot_provider_name_returns_copilot(self) -> None:
        """Test Copilot adapter has correct provider name."""
        adapter = CopilotAdapter()
        assert adapter.provider_name == "copilot"

    def test_gemini_provider_name_returns_gemini(self) -> None:
        """Test Gemini adapter has correct provider name."""
        adapter = GeminiAdapter()
        assert adapter.provider_name == "gemini"

    def test_codex_provider_name_returns_codex(self) -> None:
        """Test Codex adapter has correct provider name."""
        adapter = CodexAdapter()
        assert adapter.provider_name == "codex"


class TestGeminiAdapter:
    """Tests for the Google Gemini CLI adapter."""

    def test_build_command_basic_returns_correct_args(self) -> None:
        """Test basic command building."""
        # Arrange
        adapter = GeminiAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Explain this",
            model="gemini-1.5-pro",
            session_flags=[],
        )
        # Assert
        assert "gemini" in cmd
        assert "Explain this" in cmd
        assert "--model" in cmd
        assert "gemini-1.5-pro" in cmd
        assert "--output-format" in cmd
        assert "json" in cmd

    def test_build_command_resume_returns_resume_flag(self) -> None:
        """Test command building with session resume."""
        # Arrange
        adapter = GeminiAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Continue",
            model="gemini-1.5-flash",
            session_flags=["--resume", "abc-123"],
        )
        # Assert
        assert "--resume" in cmd
        assert "abc-123" in cmd

    def test_parse_output_json_returns_content(self) -> None:
        """Test parsing valid JSON output."""
        # Arrange
        adapter = GeminiAdapter()
        # Act
        result = adapter.parse_output('{"response": "Hello World"}')
        # Assert
        assert result == "Hello World"

    def test_parse_output_missing_key_returns_raw_json(self) -> None:
        """Test parsing JSON output without 'response' key."""
        # Arrange
        adapter = GeminiAdapter()
        # Act
        result = adapter.parse_output('{"text": "Some text"}')
        # Assert
        assert result == '{"text": "Some text"}'

    def test_parse_output_malformed_json_returns_raw_text(self) -> None:
        """Test parsing malformed JSON (fallback to text)."""
        # Arrange
        adapter = GeminiAdapter()
        # Act
        result = adapter.parse_output("Not JSON at all")
        # Assert
        assert result == "Not JSON at all"

    def test_handle_error_not_found_raises_provider_not_available(self) -> None:
        """Test error handling for missing CLI."""
        # Arrange
        adapter = GeminiAdapter()
        # Act
        error = adapter.handle_error(127, "gemini: command not found")
        # Assert
        assert isinstance(error, ProviderNotAvailable)

    def test_handle_error_rate_limit_raises_rate_limit_exceeded(self) -> None:
        """Test error handling for rate limiting."""
        # Arrange
        adapter = GeminiAdapter()
        # Act
        error = adapter.handle_error(1, "Quota exceeded")
        # Assert
        assert isinstance(error, RateLimitExceeded)

    def test_handle_error_auth_raises_provider_auth_error(self) -> None:
        """Test error handling for auth failure."""
        # Arrange
        adapter = GeminiAdapter()
        # Act
        error = adapter.handle_error(1, "Invalid credentials")
        # Assert
        assert isinstance(error, ProviderAuthError)


class TestCodexAdapter:
    """Tests for the Codex CLI adapter."""

    def test_build_command_basic_returns_correct_args(self) -> None:
        """Test basic command building."""
        # Arrange
        adapter = CodexAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Refactor this",
            model="default",
            session_flags=[],
        )
        # Assert
        assert "codex" in cmd
        assert "exec" in cmd
        assert "Refactor this" in cmd
        assert "--full-auto" in cmd

    def test_build_command_resume_returns_resume_subcommand(self) -> None:
        """Test command building with resume subcommand."""
        # Arrange
        adapter = CodexAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Continue",
            model="default",
            session_flags=["resume", "session-123"],
        )
        # Assert
        assert "exec" in cmd
        assert "resume" in cmd
        assert "session-123" in cmd
        assert "Continue" in cmd
        # Ensure order: exec resume <id> <prompt>
        idx_resume = cmd.index("resume")
        idx_prompt = cmd.index("Continue")
        assert idx_resume < idx_prompt

    def test_build_command_sandbox_returns_sandbox_flag(self) -> None:
        """Test command building with sandbox."""
        # Arrange
        adapter = CodexAdapter()
        # Act
        cmd = adapter.build_command(
            prompt="Test",
            model="default",
            session_flags=[],
            sandbox="workspace-write",
        )
        # Assert
        assert "--sandbox" in cmd
        assert "workspace-write" in cmd

    def test_parse_output_jsonl_returns_completed_turn_content(self) -> None:
        """Test parsing JSONL with turn.completed event."""
        # Arrange
        adapter = CodexAdapter()
        raw_output = """
{"type": "turn.start", "data": {}}
{"type": "turn.completed", "data": {"content": "Final Code"}}
"""
        # Act
        result = adapter.parse_output(raw_output)
        # Assert
        assert result == "Final Code"

    def test_parse_output_no_event_returns_raw_text(self) -> None:
        """Test parsing output when no event is found."""
        # Arrange
        adapter = CodexAdapter()
        # Act
        result = adapter.parse_output("Standard Text Output")
        # Assert
        assert result == "Standard Text Output"

    def test_handle_error_sandbox_raises_sandbox_violation(self) -> None:
        """Test error handling for sandbox violation."""
        # Arrange
        adapter = CodexAdapter()
        # Act
        error = adapter.handle_error(1, "Sandbox violation: Access denied")
        # Assert
        assert isinstance(error, SandboxViolation)

    def test_handle_error_not_found_raises_provider_not_available(self) -> None:
        """Test error handling for missing CLI."""
        # Arrange
        adapter = CodexAdapter()
        # Act
        error = adapter.handle_error(127, "codex: command not found")
        # Assert
        assert isinstance(error, ProviderNotAvailable)
