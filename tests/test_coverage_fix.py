import pytest

from determinagent.adapters.codex import CodexAdapter
from determinagent.adapters.copilot import CopilotAdapter
from determinagent.agent import UnifiedAgent
from determinagent.exceptions import (
    ExecutionError,
    ParseError,
    ProviderAuthError,
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
