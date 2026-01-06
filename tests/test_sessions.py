"""
Tests for session management.

Tests session flag generation for all providers.
"""

from determinagent.sessions import SessionManager


class TestSessionManager:
    """Tests for the SessionManager class."""

    def test_init_with_auto_uuid_generates_valid_id(self) -> None:
        """Test initialization with auto-generated UUID."""
        # Arrange & Act
        manager = SessionManager("claude")

        # Assert
        assert manager.provider == "claude"
        assert manager.session_id is not None
        assert len(manager.session_id) == 36  # UUID format
        assert manager.call_count == 0

    def test_init_with_custom_id_uses_provided_id(self) -> None:
        """Test initialization with custom session ID."""
        # Arrange
        custom_id = "my-custom-session-id"
        # Act
        manager = SessionManager("claude", session_id=custom_id)

        # Assert
        assert manager.session_id == custom_id

    def test_repr_returns_descriptive_string(self) -> None:
        """Test string representation."""
        # Arrange
        manager = SessionManager("claude", session_id="test-123")
        # Act
        repr_str = repr(manager)

        # Assert
        assert "SessionManager" in repr_str
        assert "claude" in repr_str
        assert "test-123" in repr_str


class TestClaudeSessionFlags:
    """Tests for Claude session flag generation."""

    def test_get_session_flags_first_call_returns_session_id_flag(self) -> None:
        """Test session flags for first call."""
        # Arrange
        manager = SessionManager("claude", session_id="test-uuid")
        # Act
        flags = manager.get_session_flags()

        # Assert
        assert flags == ["--session-id", "test-uuid"]

    def test_get_session_flags_resume_returns_r_flag(self) -> None:
        """Test session flags for resume call."""
        # Arrange
        manager = SessionManager("claude", session_id="test-uuid")
        manager.call_count = 1
        # Act
        flags = manager.get_session_flags()

        # Assert
        assert flags == ["-r", "test-uuid"]

    def test_get_session_flags_explicit_first_call_overrides_count(self) -> None:
        """Test explicit first call override."""
        # Arrange
        manager = SessionManager("claude", session_id="test-uuid")
        manager.call_count = 5  # Normally would trigger resume

        # Act
        flags = manager.get_session_flags(is_first_call=True)
        # Assert
        assert flags == ["--session-id", "test-uuid"]

    def test_get_session_flags_explicit_resume_overrides_count(self) -> None:
        """Test explicit resume override."""
        # Arrange
        manager = SessionManager("claude", session_id="test-uuid")
        manager.call_count = 0  # Normally would trigger first call

        # Act
        flags = manager.get_session_flags(is_first_call=False)
        # Assert
        assert flags == ["-r", "test-uuid"]


class TestGeminiSessionFlags:
    """Tests for Gemini session flag generation."""

    def test_get_session_flags_first_call_returns_empty(self) -> None:
        """Test that first call has no flags (auto-create)."""
        # Arrange
        manager = SessionManager("gemini", session_id="test-uuid")
        # Act
        flags = manager.get_session_flags()

        # Assert
        assert flags == []

    def test_get_session_flags_resume_returns_resume_flag(self) -> None:
        """Test resume flags (Not supported for Gemini)."""
        # Arrange
        manager = SessionManager("gemini", session_id="test-uuid")
        manager.call_count = 1
        # Act
        flags = manager.get_session_flags()

        # Assert
        assert flags == []


class TestCopilotSessionFlags:
    """Tests for Copilot session flag generation."""

    def test_get_session_flags_first_call_returns_empty(self) -> None:
        """Test that first call has no flags."""
        # Arrange
        manager = SessionManager("copilot", session_id="test-uuid")
        # Act
        flags = manager.get_session_flags()

        # Assert
        assert flags == []

    def test_get_session_flags_resume_returns_resume_flag(self) -> None:
        """Test resume flags (Not supported for Copilot)."""
        # Arrange
        manager = SessionManager("copilot", session_id="test-uuid")
        manager.call_count = 1
        # Act
        flags = manager.get_session_flags()

        # Assert
        assert flags == []


class TestCodexSessionFlags:
    """Tests for Codex session flag generation."""

    def test_get_session_flags_first_call_returns_empty(self) -> None:
        """Test that first call has no flags."""
        # Arrange
        manager = SessionManager("codex", session_id="test-uuid")
        # Act
        flags = manager.get_session_flags()

        # Assert
        assert flags == []

    def test_get_session_flags_resume_returns_resume_subcommand(self) -> None:
        """Test resume flags (Not supported for Codex)."""
        # Arrange
        manager = SessionManager("codex", session_id="test-uuid")
        manager.call_count = 1
        # Act
        flags = manager.get_session_flags()

        # Assert
        # Codex returns empty flags as session resume is not supported
        assert flags == []


class TestSessionLifecycle:
    """Tests for session lifecycle management."""

    def test_save_exchange_increments_call_count(self) -> None:
        """Test that save_exchange increments call count."""
        # Arrange
        manager = SessionManager("claude")
        assert manager.call_count == 0

        # Act
        manager.save_exchange("prompt", "response")
        # Assert
        assert manager.call_count == 1

        # Act
        manager.save_exchange("prompt2", "response2")
        # Assert
        assert manager.call_count == 2

    def test_reset_session_generates_new_id_and_resets_count(self) -> None:
        """Test session reset."""
        # Arrange
        manager = SessionManager("claude", session_id="original-id")
        manager.call_count = 5
        original_id = manager.session_id

        # Act
        manager.reset_session()

        # Assert
        assert manager.session_id != original_id
        assert manager.call_count == 0
        assert len(manager.session_id) == 36

    def test_build_prompt_returns_prompt_unchanged(self) -> None:
        """Test that build_prompt returns prompt unchanged (native sessions)."""
        # Arrange
        manager = SessionManager("claude")
        prompt = "This is my prompt"

        # Act
        result = manager.build_prompt(prompt)
        # Assert
        assert result == prompt


class TestUnknownProvider:
    """Tests for unknown provider handling."""

    def test_get_session_flags_unknown_provider_returns_empty(self) -> None:
        """Test that unknown providers return empty flags."""
        # Arrange
        manager = SessionManager("unknown")  # type: ignore
        # Act
        flags = manager.get_session_flags()

        # Assert
        assert flags == []
