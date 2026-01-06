"""
Tests for provider validation module.

Tests provider validation, error handling, and result reporting.
"""

from unittest.mock import MagicMock, patch

import pytest

from determinagent.exceptions import ProviderAuthError, ProviderNotAvailable
from determinagent.validation import (
    validate_provider,
    validate_providers,
    validate_providers_by_list,
    ValidationResult,
)


class TestValidateProvider:
    """Tests for validate_provider function."""

    def test_validate_provider_available_returns_success(self) -> None:
        """Test that a valid provider returns success status."""
        # Arrange & Act
        result = validate_provider("claude", role="test_writer")

        # Assert
        assert isinstance(result, dict)
        assert result["role"] == "test_writer"
        assert result["provider"] == "claude"
        assert result["status"] == "✅ available"
        assert result["error"] is None

    def test_validate_provider_returns_validation_result_type(self) -> None:
        """Test that result matches ValidationResult TypedDict structure."""
        # Arrange & Act
        result = validate_provider("claude", role="writer")

        # Assert
        assert "role" in result
        assert "provider" in result
        assert "status" in result
        assert "error" in result

    @patch("determinagent.agent.get_adapter")
    def test_validate_provider_not_installed_returns_error(
        self, mock_get_adapter: MagicMock
    ) -> None:
        """Test that missing provider returns not installed status."""
        # Arrange
        mock_get_adapter.side_effect = ProviderNotAvailable(
            "CLI not found", provider="missing"
        )

        # Act
        result = validate_provider("missing", role="editor")

        # Assert
        assert result["status"] == "❌ not installed"
        assert result["error"] is not None
        assert "not found" in result["error"].lower() or "not installed" in result["error"].lower()

    @patch("determinagent.agent.get_adapter")
    def test_validate_provider_auth_error_returns_auth_failed(
        self, mock_get_adapter: MagicMock
    ) -> None:
        """Test that auth error returns auth failed status."""
        # Arrange
        mock_get_adapter.side_effect = ProviderAuthError(
            "Authentication failed", provider="claude"
        )

        # Act
        result = validate_provider("claude", role="reviewer")

        # Assert
        assert result["status"] == "⚠️  auth failed"
        assert result["error"] is not None

    @patch("determinagent.agent.get_adapter")
    def test_validate_provider_generic_error_returns_error_status(
        self, mock_get_adapter: MagicMock
    ) -> None:
        """Test that generic error returns error status."""
        # Arrange
        mock_get_adapter.side_effect = RuntimeError("Unexpected error")

        # Act
        result = validate_provider("claude", role="test")

        # Assert
        assert result["status"] == "⚠️  error"
        assert result["error"] is not None
        assert "Unexpected error" in result["error"]


class TestValidateProviders:
    """Tests for validate_providers function."""

    def test_validate_providers_all_valid_returns_true(self) -> None:
        """Test that validation returns True when all providers are valid."""
        # Act
        all_valid, results = validate_providers(
            "claude", "claude", "claude", verbose=False
        )

        # Assert
        assert all_valid is True
        assert len(results) == 3
        for result in results:
            assert result["status"] == "✅ available"

    def test_validate_providers_returns_list_with_three_results(self) -> None:
        """Test that validation returns results for all three providers."""
        # Act
        all_valid, results = validate_providers(
            "claude", "claude", "claude", verbose=False
        )

        # Assert
        assert len(results) == 3
        roles = {result["role"] for result in results}
        assert roles == {"writer", "editor", "reviewer"}

    @patch("determinagent.validation.validate_provider")
    def test_validate_providers_returns_false_if_any_invalid(
        self, mock_validate: MagicMock
    ) -> None:
        """Test that validation returns False if any provider is invalid."""
        # Arrange
        mock_validate.side_effect = [
            {"role": "writer", "provider": "claude", "status": "✅ available", "error": None},
            {"role": "editor", "provider": "gemini", "status": "❌ not installed", "error": "Not found"},
            {"role": "reviewer", "provider": "claude", "status": "✅ available", "error": None},
        ]

        # Act
        all_valid, results = validate_providers(
            "claude", "gemini", "claude", verbose=False
        )

        # Assert
        assert all_valid is False

    @patch("determinagent.validation.validate_provider")
    def test_validate_providers_with_three_failures_returns_false(
        self, mock_validate: MagicMock
    ) -> None:
        """Test that validation returns False with multiple failures."""
        # Arrange
        mock_validate.side_effect = [
            {"role": "writer", "provider": "missing1", "status": "❌ not installed", "error": "Not found"},
            {"role": "editor", "provider": "missing2", "status": "❌ not installed", "error": "Not found"},
            {"role": "reviewer", "provider": "missing3", "status": "❌ not installed", "error": "Not found"},
        ]

        # Act
        all_valid, results = validate_providers(
            "missing1", "missing2", "missing3", verbose=False
        )

        # Assert
        assert all_valid is False
        assert all(result["status"] == "❌ not installed" for result in results)

    def test_validate_providers_maps_providers_to_roles(self) -> None:
        """Test that providers are mapped to correct roles."""
        # Act
        all_valid, results = validate_providers(
            "claude", "copilot", "gemini", verbose=False
        )

        # Assert
        role_provider_map = {result["role"]: result["provider"] for result in results}
        assert role_provider_map["writer"] == "claude"
        assert role_provider_map["editor"] == "copilot"
        assert role_provider_map["reviewer"] == "gemini"

    def test_validate_providers_verbose_false_no_output(self, capsys) -> None:
        """Test that verbose=False produces no output."""
        # Act
        validate_providers("claude", "claude", "claude", verbose=False)

        # Assert
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_validate_providers_verbose_true_produces_output(self, capsys) -> None:
        """Test that verbose=True produces output."""
        # Act
        validate_providers("claude", "claude", "claude", verbose=True)

        # Assert
        captured = capsys.readouterr()
        assert "PROVIDER VALIDATION" in captured.out or len(captured.out) > 0


class TestValidateProvidersByList:
    """Tests for validate_providers_by_list function."""

    def test_validate_providers_by_list_with_single_provider(self) -> None:
        """Test validation with custom list of providers."""
        # Act
        all_valid, results = validate_providers_by_list(
            {"tool": "claude"}, verbose=False
        )

        # Assert
        assert all_valid is True
        assert len(results) == 1
        assert results[0]["role"] == "tool"
        assert results[0]["provider"] == "claude"

    def test_validate_providers_by_list_with_multiple_providers(self) -> None:
        """Test validation with multiple custom providers."""
        # Act
        all_valid, results = validate_providers_by_list(
            {
                "primary": "claude",
                "fallback": "copilot",
                "research": "gemini",
            },
            verbose=False,
        )

        # Assert
        assert len(results) == 3
        roles = {result["role"] for result in results}
        assert roles == {"primary", "fallback", "research"}

    def test_validate_providers_by_list_returns_all_valid_true_if_all_available(
        self,
    ) -> None:
        """Test that all_valid=True when all providers are available."""
        # Act
        all_valid, results = validate_providers_by_list(
            {"primary": "claude", "secondary": "copilot"},
            verbose=False,
        )

        # Assert
        assert all_valid is True
        assert all(result["status"] == "✅ available" for result in results)

    @patch("determinagent.validation.validate_provider")
    def test_validate_providers_by_list_returns_false_if_any_invalid(
        self, mock_validate: MagicMock
    ) -> None:
        """Test that validation fails if any provider is invalid."""
        # Arrange
        mock_validate.side_effect = [
            {"role": "primary", "provider": "claude", "status": "✅ available", "error": None},
            {"role": "secondary", "provider": "missing", "status": "❌ not installed", "error": "Not found"},
        ]

        # Act
        all_valid, results = validate_providers_by_list(
            {"primary": "claude", "secondary": "missing"},
            verbose=False,
        )

        # Assert
        assert all_valid is False

    def test_validate_providers_by_list_empty_dict_returns_true(self) -> None:
        """Test that empty provider dict returns True."""
        # Act
        all_valid, results = validate_providers_by_list({}, verbose=False)

        # Assert
        assert all_valid is True
        assert len(results) == 0


class TestValidationResultType:
    """Tests for ValidationResult TypedDict."""

    def test_validation_result_has_required_fields(self) -> None:
        """Test that ValidationResult has all required fields."""
        # Arrange
        result: ValidationResult = {
            "role": "writer",
            "provider": "claude",
            "status": "✅ available",
            "error": None,
        }

        # Assert
        assert result["role"] == "writer"
        assert result["provider"] == "claude"
        assert result["status"] == "✅ available"
        assert result["error"] is None

    def test_validation_result_with_error_message(self) -> None:
        """Test that ValidationResult can contain error messages."""
        # Arrange
        result: ValidationResult = {
            "role": "editor",
            "provider": "gemini",
            "status": "❌ not installed",
            "error": "CLI not found",
        }

        # Assert
        assert result["error"] == "CLI not found"
        assert result["status"] == "❌ not installed"
