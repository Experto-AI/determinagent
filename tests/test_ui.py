"""
Tests for determinagent.ui.
"""

from unittest.mock import call, patch

from determinagent import ui


class TestPrintSeparator:
    """Tests for print_separator."""

    @patch("builtins.print")
    def test_print_separator_defaults(self, mock_print) -> None:
        """S: Test default separator."""
        ui.print_separator()
        mock_print.assert_called_once_with("=" * 60)

    @patch("builtins.print")
    def test_print_separator_custom(self, mock_print) -> None:
        """O: Test custom char and length."""
        ui.print_separator("-", 10)
        mock_print.assert_called_once_with("-" * 10)


class TestPrintHeader:
    """Tests for print_header."""

    @patch("builtins.print")
    def test_print_header_basic(self, mock_print) -> None:
        """S: Test basic header."""
        ui.print_header("Title")
        # Verify sequence of calls
        mock_print.assert_has_calls([call("\n" + "=" * 60), call("Title"), call("=" * 60)])

    @patch("builtins.print")
    def test_print_header_with_icon(self, mock_print) -> None:
        """O: Test header with icon."""
        ui.print_header("Title", icon="🚀")
        mock_print.assert_any_call("🚀 Title")

    @patch("builtins.print")
    def test_print_header_with_subtitle(self, mock_print) -> None:
        """O: Test header with subtitle."""
        ui.print_header("Title", subtitle="Sub")
        mock_print.assert_any_call("Sub")


class TestDisplayContent:
    """Tests for display_content."""

    @patch("builtins.print")
    def test_display_content_basic(self, mock_print) -> None:
        """S: Test display content."""
        ui.display_content("Title", "Content")

        sep = "=" * 60
        mock_print.assert_has_calls(
            [call("\n" + sep), call("📄 Title"), call(sep), call("Content"), call(sep + "\n")]
        )
