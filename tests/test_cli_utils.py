"""
Tests for determinagent.cli_utils.
"""

import argparse
from unittest.mock import MagicMock

from determinagent import cli_utils


class TestAddProviderArgs:
    """Tests for add_provider_args."""

    def test_add_provider_args_adds_global_and_role_args(self) -> None:
        """S: Test basic argument addition."""
        # Arrange
        parser = MagicMock(spec=argparse.ArgumentParser)
        roles = ["writer", "editor"]

        # Act
        cli_utils.add_provider_args(parser, roles)

        # Assert
        # Check that add_argument was called at least 3 times (provider + writer + editor)
        assert parser.add_argument.call_count >= 3

        # Verify specific calls
        calls = [args[0] for args, _ in parser.add_argument.call_args_list]
        assert "--provider" in calls
        assert "--writer-provider" in calls
        assert "--editor-provider" in calls

    def test_add_provider_args_uses_defaults(self) -> None:
        """O: Test that defaults are correctly passed."""
        # Arrange
        parser = MagicMock(spec=argparse.ArgumentParser)
        roles = ["writer"]
        defaults = {"writer": "gemini"}

        # Act
        cli_utils.add_provider_args(parser, roles, defaults)

        # Assert
        # Find call for writer-provider
        writer_call = None
        for args, kwargs in parser.add_argument.call_args_list:
            if args[0] == "--writer-provider":
                writer_call = kwargs
                break

        assert writer_call is not None
        assert writer_call["default"] == "gemini"

    def test_add_provider_args_uses_fallback_default(self) -> None:
        """Z: Test fallback default when not provided."""
        # Arrange
        parser = MagicMock(spec=argparse.ArgumentParser)
        roles = ["writer"]

        # Act
        cli_utils.add_provider_args(parser, roles)

        # Assert
        writer_call = None
        for args, kwargs in parser.add_argument.call_args_list:
            if args[0] == "--writer-provider":
                writer_call = kwargs
                break

        assert writer_call["default"] == "claude"


class TestResolveProviderArgs:
    """Tests for resolve_provider_args."""

    def test_resolve_provider_args_global_override(self) -> None:
        """S: Test that --provider overrides everything."""
        # Arrange
        args = argparse.Namespace(
            provider="gemini", writer_provider="claude", editor_provider="copilot"
        )
        roles = ["writer", "editor"]

        # Act
        result = cli_utils.resolve_provider_args(args, roles)

        # Assert
        assert result["writer"] == "gemini"
        assert result["editor"] == "gemini"

    def test_resolve_provider_args_specific_providers(self) -> None:
        """S: Test individual provider settings."""
        # Arrange
        args = argparse.Namespace(
            provider=None, writer_provider="claude", editor_provider="copilot"
        )
        roles = ["writer", "editor"]

        # Act
        result = cli_utils.resolve_provider_args(args, roles)

        # Assert
        assert result["writer"] == "claude"
        assert result["editor"] == "copilot"

    def test_resolve_provider_args_partial_override(self) -> None:
        """B: Test precedence with None global provider."""
        # Arrange
        args = argparse.Namespace(
            provider=None, writer_provider="claude", editor_provider="copilot"
        )
        roles = ["writer", "editor"]

        # Act
        result = cli_utils.resolve_provider_args(args, roles)

        # Assert
        assert result["writer"] == "claude"
        assert result["editor"] == "copilot"
