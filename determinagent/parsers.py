import re
from dataclasses import dataclass

import markdown
from bs4 import BeautifulSoup


@dataclass
class CategoryScore:
    """Individual category evaluation."""

    name: str
    score: int
    feedback: str


@dataclass
class ReviewResult:
    """Complete review with scores and approval status."""

    scores: dict[str, CategoryScore]
    overall_feedback: str
    is_approved: bool
    min_score: int


# Evaluation categories
REVIEW_CATEGORIES_LIST = [
    "STRUCTURE",
    "GRAMMAR",
    "TECHNICAL_ACCURACY",
    "ENGAGEMENT",
    "ACTIONABILITY",
    "SEO",
    "FORMATTING",
    "DEPTH",
    "ORIGINALITY",
    "WORD_COUNT",
    "TITLE",
    "INTRO",
]

# ============================================================================
# Text Statistics Helpers
# ============================================================================


def count_text_stats(text: str) -> tuple[int, int, int]:
    """
    Count characters, words, and lines in text.

    Returns:
        Tuple of (characters, words, lines)
    """
    chars = len(text)
    words = len(text.split())
    lines = text.count("\n") + 1 if text else 0
    return chars, words, lines


def strip_markdown(text: str) -> str:
    """
    Strip markdown formatting from text to get plain text.
    """
    # Convert markdown to HTML
    html = markdown.markdown(text)
    # Parse HTML and extract text
    soup = BeautifulSoup(html, "html.parser")
    plain_text = soup.get_text(separator=" ")
    # Clean up extra whitespace
    return re.sub(r"\s+", " ", plain_text).strip()


def format_text_stats(text: str) -> str:
    """
    Format text statistics as a readable string.

    Example: "1234 chars, 200 words, 50 lines (content: 180 words)"
    """
    raw_chars, raw_words, raw_lines = count_text_stats(text)
    plain_text = strip_markdown(text)
    _, plain_words, _ = count_text_stats(plain_text)
    return f"{raw_chars} chars, {raw_words} words, {raw_lines} lines (content: {plain_words} words)"


# ============================================================================
# Review Parser
# ============================================================================


def parse_review(response: str, min_score: int = 8) -> ReviewResult:
    """
    Parse reviewer response with multiple fallback patterns.

    This implements battle-tested regex logic with multiple fallback patterns
    to handle various AI response formats.

    Args:
        response: Raw reviewer response
        min_score: Minimum acceptable score (default: 8)

    Returns:
        ReviewResult with parsed scores and approval status
    """
    scores = {}

    # Try multiple patterns in order of likelihood
    for cat_key in REVIEW_CATEGORIES_LIST:
        score_val = None
        feedback_text = None

        # Pattern 1: Standard format (CATEGORY: 8 - feedback)
        pattern1 = rf"{cat_key}:\s*(\d+)\s*-\s*(.+?)(?=\n[A-Z_]+:|OVERALL_FEEDBACK:|APPROVAL|$)"
        match1 = re.search(pattern1, response, re.DOTALL | re.IGNORECASE)
        if match1:
            score_val = int(match1.group(1))
            feedback_text = match1.group(2).strip()

        # Pattern 2: With /10 (CATEGORY: 8/10 - feedback)
        if not score_val:
            pattern2 = (
                rf"{cat_key}:\s*(\d+)/10\s*-\s*(.+?)(?=\n[A-Z_]+:|OVERALL_FEEDBACK:|APPROVAL|$)"
            )
            match2 = re.search(pattern2, response, re.DOTALL | re.IGNORECASE)
            if match2:
                score_val = int(match2.group(1))
                feedback_text = match2.group(2).strip()

        # Pattern 3: Parentheses (CATEGORY (8/10): feedback)
        if not score_val:
            pattern3 = (
                rf"{cat_key}\s*\((\d+)/10\):\s*(.+?)(?=\n[A-Z_]+\s*\(|OVERALL_FEEDBACK:|APPROVAL|$)"
            )
            match3 = re.search(pattern3, response, re.DOTALL | re.IGNORECASE)
            if match3:
                score_val = int(match3.group(1))
                feedback_text = match3.group(2).strip()

        # Pattern 4: Markdown headers (## CATEGORY: 8 - feedback)
        if not score_val:
            pattern4 = rf"#{1, 3}\s*{cat_key}:\s*(\d+)(?:/10)?\s*-\s*(.+?)(?=\n#{1, 3}\s*[A-Z]|OVERALL_FEEDBACK:|APPROVAL|$)"
            match4 = re.search(pattern4, response, re.DOTALL | re.IGNORECASE)
            if match4:
                score_val = int(match4.group(1))
                feedback_text = match4.group(2).strip()

        # Pattern 5: Bold markdown (**CATEGORY**: 8 - feedback)
        if not score_val:
            pattern5 = rf"\*\*{cat_key}\*\*:\s*(\d+)(?:/10)?\s*-\s*(.+?)(?=\n\*\*[A-Z]|OVERALL_FEEDBACK:|APPROVAL|$)"
            match5 = re.search(pattern5, response, re.DOTALL | re.IGNORECASE)
            if match5:
                score_val = int(match5.group(1))
                feedback_text = match5.group(2).strip()

        # Pattern 5b: Bold markdown with score inside (**CATEGORY: 8** - feedback)
        if not score_val:
            pattern5b = rf"\*\*{cat_key}:\s*(\d+)(?:/10)?\*\*\s*-\s*(.+?)(?=\n\*\*[A-Z]|OVERALL_FEEDBACK:|APPROVAL|$)"
            match5b = re.search(pattern5b, response, re.DOTALL | re.IGNORECASE)
            if match5b:
                score_val = int(match5b.group(1))
                feedback_text = match5b.group(2).strip()

        # Pattern 6: Emoji checkmark format (✅ CATEGORY: 8/10 - feedback)
        if not score_val:
            pattern6 = rf"[✅❌]\s*{cat_key}:\s*(\d+)(?:/10)?\s*-\s*(.+?)(?=\n[✅❌]|OVERALL_FEEDBACK:|APPROVAL|$)"
            match6 = re.search(pattern6, response, re.DOTALL | re.IGNORECASE)
            if match6:
                score_val = int(match6.group(1))
                feedback_text = match6.group(2).strip()

        # Pattern 7: Simple format without dash (CATEGORY: 8 feedback...)
        if not score_val:
            pattern7 = rf"{cat_key}:\s*(\d+)(?:/10)?[:\s]+(.+?)(?=\n[A-Z_]+:|OVERALL|APPROVAL|$)"
            match7 = re.search(pattern7, response, re.DOTALL | re.IGNORECASE)
            if match7:
                score_val = int(match7.group(1))
                feedback_text = match7.group(2).strip()

        # If no pattern matched, use defaults
        if score_val is None:
            # We default to 1 to force improvement if parsing fails
            score_val = 1
            feedback_text = (
                "Parsing failed for this category. Ensure the output follows the required format."
            )

        # Clamp score to valid range
        score_val = min(10, max(1, score_val))

        scores[cat_key] = CategoryScore(name=cat_key, score=score_val, feedback=feedback_text or "")

    # Extract overall feedback - try multiple patterns
    overall_feedback = ""

    # Try with colon
    overall_match = re.search(
        r"OVERALL_FEEDBACK:\s*(.+?)(?=\nAPPROVAL|\n[A-Z_]+:|$)", response, re.DOTALL | re.IGNORECASE
    )
    if overall_match:
        overall_feedback = overall_match.group(1).strip()

    # Try markdown header format
    if not overall_feedback:
        overall_match2 = re.search(
            r"#{1,3}\s*OVERALL[_\s]?FEEDBACK[:\s]*(.+?)(?=\nAPPROVAL|\n#{1,3}|$)",
            response,
            re.DOTALL | re.IGNORECASE,
        )
        if overall_match2:
            overall_feedback = overall_match2.group(1).strip()

    # Check approval (all scores >= min_score)
    is_approved = all(cat.score >= min_score for cat in scores.values())
    min_score_actual = min(cat.score for cat in scores.values())

    return ReviewResult(
        scores=scores,
        overall_feedback=overall_feedback,
        is_approved=is_approved,
        min_score=min_score_actual,
    )
