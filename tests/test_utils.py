"""
Tests for determinagent.utils.
"""

from determinagent import utils


class TestTruncateId:
    """Tests for truncate_id."""

    def test_truncate_id_short_input_returns_unchanged(self) -> None:
        """Z: Test short input."""
        # Arrange
        input_id = "short"
        # Act
        result = utils.truncate_id(input_id)
        # Assert
        assert result == "short"

    def test_truncate_id_empty_input_returns_empty(self) -> None:
        """Z: Test empty input."""
        # Arrange
        input_id = ""
        # Act
        result = utils.truncate_id(input_id)
        # Assert
        assert result == ""

    def test_truncate_id_exact_length_returns_unchanged(self) -> None:
        """B: Test input of exact default length (8)."""
        # Arrange
        input_id = "12345678"
        # Act
        result = utils.truncate_id(input_id)
        # Assert
        assert result == "12345678"

    def test_truncate_id_long_input_returns_truncated(self) -> None:
        """M: Test input longer than default length."""
        # Arrange
        input_id = "1234567890"
        # Act
        result = utils.truncate_id(input_id)
        # Assert
        assert result == "12345678..."

    def test_truncate_id_custom_length_respects_length(self) -> None:
        """M: Test input longer than custom length."""
        # Arrange
        input_id = "1234567890"
        length = 4
        # Act
        result = utils.truncate_id(input_id, length)
        # Assert
        assert result == "1234..."


class TestSanitizeFilename:
    """Tests for sanitize_filename."""

    def test_sanitize_filename_simple_alphanumeric_returns_lowercase(self) -> None:
        """S: Test simple alphanumeric name."""
        # Arrange
        name = "MyTopic"
        # Act
        result = utils.sanitize_filename(name)
        # Assert
        assert result == "mytopic"

    def test_sanitize_filename_spaces_returns_hyphens(self) -> None:
        """O: Test spaces replaced by hyphens."""
        # Arrange
        name = "My New Topic"
        # Act
        result = utils.sanitize_filename(name)
        # Assert
        assert result == "my-new-topic"

    def test_sanitize_filename_special_chars_returns_hyphens(self) -> None:
        """I: Test special characters removed or replaced."""
        # Arrange
        name = "Topic & Stuff!"
        # Act
        result = utils.sanitize_filename(name)
        # Assert
        assert result == "topic-stuff"

    def test_sanitize_filename_multiple_hyphens_collapsed(self) -> None:
        """O: Test multiple hyphens collapsing."""
        # Arrange
        name = "Topic--Name"
        # Act
        result = utils.sanitize_filename(name)
        # Assert
        assert result == "topic-name"

    def test_sanitize_filename_leading_trailing_hyphens_removed(self) -> None:
        """B: Test leading/trailing hyphens."""
        # Arrange
        name = "-Topic-"
        # Act
        result = utils.sanitize_filename(name)
        # Assert
        assert result == "topic"

    def test_sanitize_filename_truncates_long_names(self) -> None:
        """M: Test truncation of long names."""
        # Arrange
        name = "a" * 60
        # Act
        result = utils.sanitize_filename(name, max_length=50)
        # Assert
        assert len(result) == 50

    def test_sanitize_filename_truncates_at_hyphen_if_possible(self) -> None:
        """M: Test smart truncation at hyphen."""
        # Arrange
        # 45 chars + hyphen + 10 chars = 56 chars
        part1 = "a" * 45
        part2 = "b" * 10
        name = f"{part1}-{part2}"
        # Act
        result = utils.sanitize_filename(name, max_length=50)
        # Assert
        # Should truncate at the hyphen, so length 45
        assert len(result) == 45
        assert result == part1.lower()

    def test_sanitize_filename_hard_truncates_if_no_hyphen(self) -> None:
        """M: Test hard truncation if no hyphen found."""
        # Arrange
        name = "a" * 55
        # Act
        result = utils.sanitize_filename(name, max_length=50)
        # Assert
        assert len(result) == 50
        assert result == ("a" * 50).lower()
