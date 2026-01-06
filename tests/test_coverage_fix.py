import pytest

from determinagent.adapters.codex import CodexAdapter
from determinagent.adapters.copilot import CopilotAdapter
from determinagent.agent import UnifiedAgent
from determinagent.exceptions import (
    ExecutionError,
    ParseError,
    ProviderAuthError,
    SessionError,
)
from determinagent.sessions import SessionManager


class TestCoverageFix:
    def test_copilot_access_error(self):
        adapter = CopilotAdapter()
        stderr = "Error: GitHub Copilot access required."
        error = adapter.handle_error(1, stderr)
        assert isinstance(error, ProviderAuthError)
        assert "access required" in str(error)

    def test_codex_auth_error(self):
        adapter = CodexAdapter()
        stderr = "Authentication failed: Please login."
        error = adapter.handle_error(1, stderr)
        assert isinstance(error, ProviderAuthError)

    def test_codex_execution_error(self):
        adapter = CodexAdapter()
        stderr = "Unknown internal error"
        error = adapter.handle_error(1, stderr)
        assert isinstance(error, ExecutionError)
        assert "Unknown internal error" in str(error)

    def test_extract_nested_json(self):
        session = SessionManager("claude")
        agent = UnifiedAgent("claude", "balanced", "tester", "inst", session)

        # Nested JSON structure embedded in text (matches \{.*\} regex)
        response = """
        Here is the analysis:
        {
            "category": "nested",
            "data": {
                "value": 123,
                "list": [1, 2]
            }
        }
        End of report.
        """
        data = agent._extract_json(response)
        assert data["category"] == "nested"
        assert data["data"]["value"] == 123

    def test_extract_nested_json_failure(self):
        # Case where regex matches but json is invalid
        session = SessionManager("claude")
        agent = UnifiedAgent("claude", "balanced", "tester", "inst", session)

        response = "text { invalid json } text"
        # Since _extract_json raises ParseError if all attempts fail
        with pytest.raises(ParseError):
            agent._extract_json(response)

    def test_copilot_session_corrupted_error(self):
        """Test that corrupted session errors are properly detected."""
        adapter = CopilotAdapter()
        stderr = "Error: Session file is corrupted or incompatible"
        error = adapter.handle_error(1, stderr)
        assert isinstance(error, SessionError)
        assert "corrupted" in str(error).lower()
        assert "rm -rf ~/.copilot/sessions" in str(error)

    def test_agent_session_error_recovery(self):
        """Test that UnifiedAgent resets session on SessionError and retries."""
        from unittest.mock import patch

        session = SessionManager("copilot")
        agent = UnifiedAgent("copilot", "balanced", "tester", "instructions", session)

        # Track session ID before and after
        original_session_id = session.session_id
        session.call_count = 1  # Simulate a resumed session

        # First call raises SessionError, second succeeds
        call_count = 0

        def mock_execute(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise SessionError(
                    "Session file is corrupted",
                    provider="copilot",
                )
            return "success response"

        with patch.object(agent.adapter, "execute", side_effect=mock_execute):
            response = agent.send("test prompt", max_retries=2)

        assert response == "success response"
        assert call_count == 2  # First failed, second succeeded
        # Session should have been reset (new ID)
        assert session.session_id != original_session_id
        assert session.call_count == 0 or session.call_count == 1  # Reset to 0, then incremented
