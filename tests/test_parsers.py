"""
Tests for review parsing.

Tests edge case handling for regex patterns in the review parser.
"""


from determinagent.parsers import (
    REVIEW_CATEGORIES_LIST,
    CategoryScore,
    ReviewResult,
    count_text_stats,
    format_text_stats,
    parse_review,
    strip_markdown,
)


class TestCountTextStats:
    """Tests for text statistics counting."""

    def test_basic_counting(self) -> None:
        """Test basic character, word, and line counting."""
        text = "Hello World"
        chars, words, lines = count_text_stats(text)

        assert chars == 11
        assert words == 2
        assert lines == 1

    def test_multiline(self) -> None:
        """Test multiline text counting."""
        text = "Line 1\nLine 2\nLine 3"
        chars, words, lines = count_text_stats(text)

        assert lines == 3
        assert words == 6

    def test_empty_string(self) -> None:
        """Test empty string handling."""
        chars, words, lines = count_text_stats("")

        assert chars == 0
        assert words == 0
        assert lines == 0


class TestStripMarkdown:
    """Tests for markdown stripping."""

    def test_headers(self) -> None:
        """Test that headers are stripped."""
        text = "# Header\n\nSome content"
        result = strip_markdown(text)

        assert "Header" in result
        assert "#" not in result

    def test_bold_italic(self) -> None:
        """Test that bold and italic are stripped."""
        text = "This is **bold** and *italic* text"
        result = strip_markdown(text)

        assert "bold" in result
        assert "italic" in result
        assert "*" not in result

    def test_links(self) -> None:
        """Test that links are stripped."""
        text = "Check out [this link](https://example.com)"
        result = strip_markdown(text)

        assert "this link" in result
        assert "[" not in result
        assert "example.com" not in result


class TestFormatTextStats:
    """Tests for text statistics formatting."""

    def test_format_output(self) -> None:
        """Test formatted output structure."""
        text = "# Hello World\n\nThis is content"
        result = format_text_stats(text)

        assert "chars" in result
        assert "words" in result
        assert "lines" in result
        assert "content:" in result


class TestParseReviewStandardFormat:
    """Tests for parsing standard review format."""

    def test_parse_basic_review(self, sample_review_response: str) -> None:
        """Test parsing a well-formatted review."""
        result = parse_review(sample_review_response)

        assert isinstance(result, ReviewResult)
        assert len(result.scores) == len(REVIEW_CATEGORIES_LIST)

    def test_scores_extracted(self, sample_review_response: str) -> None:
        """Test that scores are correctly extracted."""
        result = parse_review(sample_review_response)

        assert result.scores["STRUCTURE"].score == 9
        assert result.scores["GRAMMAR"].score == 8
        assert result.scores["ENGAGEMENT"].score == 7

    def test_feedback_extracted(self, sample_review_response: str) -> None:
        """Test that feedback is correctly extracted."""
        result = parse_review(sample_review_response)

        assert "Well organized" in result.scores["STRUCTURE"].feedback
        assert "typos" in result.scores["GRAMMAR"].feedback.lower()

    def test_overall_feedback_extracted(self, sample_review_response: str) -> None:
        """Test that overall feedback is extracted."""
        result = parse_review(sample_review_response)

        assert result.overall_feedback != ""
        assert "minor improvements" in result.overall_feedback.lower()

    def test_approval_calculation(self, sample_review_response: str) -> None:
        """Test approval calculation based on min_score."""
        result = parse_review(sample_review_response, min_score=8)

        # Some scores are 7, so not approved at min_score=8
        assert result.is_approved is False

        result_lenient = parse_review(sample_review_response, min_score=7)
        assert result_lenient.is_approved is True


class TestParseReviewAlternativeFormats:
    """Tests for parsing alternative review formats."""

    def test_parse_with_slash_ten(self) -> None:
        """Test parsing CATEGORY: 8/10 format."""
        response = """
STRUCTURE: 8/10 - Good organization
GRAMMAR: 9/10 - Excellent writing
TECHNICAL_ACCURACY: 8/10 - Accurate
ENGAGEMENT: 7/10 - Could be better
ACTIONABILITY: 8/10 - Clear steps
SEO: 7/10 - Needs work
FORMATTING: 8/10 - Clean
DEPTH: 8/10 - Good coverage
ORIGINALITY: 7/10 - Some unique ideas
WORD_COUNT: 9/10 - Perfect length
TITLE: 8/10 - Good title
INTRO: 8/10 - Strong opening
"""
        result = parse_review(response)

        assert result.scores["STRUCTURE"].score == 8
        assert result.scores["GRAMMAR"].score == 9

    def test_parse_parentheses_format(self) -> None:
        """Test parsing CATEGORY (8/10): format."""
        response = """
STRUCTURE (8/10): Good organization throughout.
GRAMMAR (9/10): Excellent writing quality.
TECHNICAL_ACCURACY (8/10): All facts verified.
ENGAGEMENT (7/10): Could add more examples.
ACTIONABILITY (8/10): Clear action items.
SEO (7/10): Keyword optimization needed.
FORMATTING (8/10): Clean layout.
DEPTH (8/10): Good topic coverage.
ORIGINALITY (7/10): Some fresh perspectives.
WORD_COUNT (9/10): Meets requirements.
TITLE (8/10): Catchy and clear.
INTRO (8/10): Strong hook.
"""
        result = parse_review(response)

        assert result.scores["STRUCTURE"].score == 8
        assert result.scores["GRAMMAR"].score == 9

    def test_parse_markdown_headers(self) -> None:
        """Test parsing with markdown headers."""
        response = """
## STRUCTURE: 8 - Good organization
## GRAMMAR: 9 - Excellent writing
## TECHNICAL_ACCURACY: 8 - Accurate content
## ENGAGEMENT: 7 - Needs more examples
## ACTIONABILITY: 8 - Clear steps
## SEO: 7 - Work on keywords
## FORMATTING: 8 - Clean
## DEPTH: 8 - Good coverage
## ORIGINALITY: 7 - Some unique ideas
## WORD_COUNT: 9 - Good length
## TITLE: 8 - Catchy
## INTRO: 8 - Strong
"""
        result = parse_review(response)

        assert result.scores["STRUCTURE"].score == 8
        assert result.scores["GRAMMAR"].score == 9

    def test_parse_bold_format(self) -> None:
        """Test parsing with bold markdown."""
        response = """
**STRUCTURE**: 8 - Good organization.
**GRAMMAR**: 9 - Excellent.
**TECHNICAL_ACCURACY**: 8 - Accurate.
**ENGAGEMENT**: 7 - Needs work.
**ACTIONABILITY**: 8 - Clear.
**SEO**: 7 - Improve.
**FORMATTING**: 8 - Clean.
**DEPTH**: 8 - Good.
**ORIGINALITY**: 7 - OK.
**WORD_COUNT**: 9 - Good.
**TITLE**: 8 - Nice.
**INTRO**: 8 - Strong.
"""
        result = parse_review(response)

        assert result.scores["STRUCTURE"].score == 8

    def test_parse_emoji_format(self) -> None:
        """Test parsing with emoji prefixes."""
        response = """
✅ STRUCTURE: 8 - Good organization.
✅ GRAMMAR: 9 - Excellent.
✅ TECHNICAL_ACCURACY: 8 - Accurate.
❌ ENGAGEMENT: 7 - Needs work.
✅ ACTIONABILITY: 8 - Clear.
❌ SEO: 7 - Improve.
✅ FORMATTING: 8 - Clean.
✅ DEPTH: 8 - Good.
❌ ORIGINALITY: 7 - OK.
✅ WORD_COUNT: 9 - Good.
✅ TITLE: 8 - Nice.
✅ INTRO: 8 - Strong.
"""
        result = parse_review(response)

        assert result.scores["STRUCTURE"].score == 8
        assert result.scores["ENGAGEMENT"].score == 7


class TestParseReviewEdgeCases:
    """Tests for edge cases in review parsing."""

    def test_missing_category(self) -> None:
        """Test handling of missing categories (defaults to 1)."""
        response = """
STRUCTURE: 8 - Good
GRAMMAR: 9 - Good
"""
        result = parse_review(response)

        # Missing categories should default to 1
        assert result.scores["ENGAGEMENT"].score == 1
        assert "parsing failed" in result.scores["ENGAGEMENT"].feedback.lower()

    def test_score_clamping_high(self) -> None:
        """Test that scores above 10 are clamped."""
        response = "STRUCTURE: 15 - Amazing work!"
        result = parse_review(response)

        assert result.scores["STRUCTURE"].score == 10

    def test_score_clamping_low(self) -> None:
        """Test that scores below 1 are clamped."""
        response = "STRUCTURE: 0 - Terrible!"
        result = parse_review(response)

        assert result.scores["STRUCTURE"].score == 1

    def test_min_score_tracking(self) -> None:
        """Test that min_score is correctly calculated."""
        response = """
STRUCTURE: 9 - Good
GRAMMAR: 5 - Poor
TECHNICAL_ACCURACY: 8 - OK
ENGAGEMENT: 7 - Meh
ACTIONABILITY: 6 - Needs work
SEO: 8 - Fine
FORMATTING: 9 - Great
DEPTH: 7 - OK
ORIGINALITY: 8 - Nice
WORD_COUNT: 9 - Perfect
TITLE: 8 - Good
INTRO: 7 - OK
"""
        result = parse_review(response)

        assert result.min_score == 5

    def test_empty_response(self) -> None:
        """Test handling of empty response."""
        response = ""
        result = parse_review(response)

        # All categories should default to 1
        assert all(score.score == 1 for score in result.scores.values())
        assert result.is_approved is False

    def test_case_insensitive(self) -> None:
        """Test that parsing is case insensitive."""
        response = """
structure: 8 - Good
grammar: 9 - Excellent
technical_accuracy: 8 - Accurate
engagement: 7 - OK
actionability: 8 - Clear
seo: 7 - Needs work
formatting: 8 - Clean
depth: 8 - Good
originality: 7 - Some ideas
word_count: 9 - Perfect
title: 8 - Nice
intro: 8 - Strong
"""
        result = parse_review(response)

        # Should still parse correctly (case insensitive)
        assert result.scores["STRUCTURE"].score == 8


class TestReviewResult:
    """Tests for ReviewResult data class."""

    def test_review_result_structure(self, sample_review_response: str) -> None:
        """Test ReviewResult has correct structure."""
        result = parse_review(sample_review_response)

        assert hasattr(result, "scores")
        assert hasattr(result, "overall_feedback")
        assert hasattr(result, "is_approved")
        assert hasattr(result, "min_score")

    def test_category_score_structure(self, sample_review_response: str) -> None:
        """Test CategoryScore has correct structure."""
        result = parse_review(sample_review_response)
        score = result.scores["STRUCTURE"]

        assert isinstance(score, CategoryScore)
        assert hasattr(score, "name")
        assert hasattr(score, "score")
        assert hasattr(score, "feedback")
        assert score.name == "STRUCTURE"
