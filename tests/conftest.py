"""
Test configuration for pytest.

This conftest.py provides shared fixtures for all tests.
"""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_subprocess() -> Generator[MagicMock, None, None]:
    """Mock subprocess.run for testing CLI adapters."""
    with patch("subprocess.run") as mock:
        mock.return_value = MagicMock(
            returncode=0,
            stdout="Test response from CLI",
            stderr="",
        )
        yield mock


@pytest.fixture
def sample_claude_response() -> str:
    """Sample response from Claude CLI."""
    return "This is a sample response from Claude."


@pytest.fixture
def sample_json_response() -> str:
    """Sample JSON response for structured output testing."""
    return '{"score": 8, "feedback": "Good work!"}'


@pytest.fixture
def sample_review_response() -> str:
    """Sample review response for parser testing."""
    return """
STRUCTURE: 9 - Well organized with clear sections.
GRAMMAR: 8 - Minor typos but overall good.
TECHNICAL_ACCURACY: 9 - All facts are correct.
ENGAGEMENT: 7 - Could use more examples.
ACTIONABILITY: 8 - Clear takeaways provided.
SEO: 7 - Could improve keyword density.
FORMATTING: 9 - Clean and readable.
DEPTH: 8 - Good coverage of the topic.
ORIGINALITY: 7 - Some unique insights.
WORD_COUNT: 9 - Meets requirements.
TITLE: 8 - Catchy and descriptive.
INTRO: 8 - Hooks the reader well.

OVERALL_FEEDBACK: Solid article that needs minor improvements in engagement and SEO.

APPROVAL: YES
"""
