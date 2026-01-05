from unittest.mock import MagicMock, patch

import pytest

from flows.blog.main import create_blog_workflow


class TestBlogFlow:
    """Tests for the blog post generation workflow."""

    @pytest.fixture
    def mock_agents(self):
        with (
            patch("flows.blog.main.UnifiedAgent") as mock_agent_cls,
            patch("flows.blog.main.SessionManager"),
        ):
            # Create mock instances for each role
            mock_writer = MagicMock()
            mock_editor = MagicMock()
            mock_reviewer = MagicMock()

            # Setup default behavior
            mock_writer.session.session_id = "writer-session"
            mock_editor.session.session_id = "editor-session"
            mock_reviewer.session.session_id = "reviewer-session"

            # Agent instantiation order: Writer, Editor, Reviewer
            mock_agent_cls.side_effect = [mock_writer, mock_editor, mock_reviewer]

            yield mock_writer, mock_editor, mock_reviewer

    def test_happy_path_workflow(self, mock_agents):
        """Test the ideal flow: Writer -> Editor -> Reviewer (Approved) -> Human (Approved)."""
        mock_writer, mock_editor, mock_reviewer = mock_agents

        # 1. Writer creates draft
        mock_writer.send.return_value = "# Draft Title\n\nInitial draft content."

        # 2. Editor polishes
        mock_editor.send.return_value = "# Draft Title\n\nPolished content."

        # 3. Reviewer approves
        mock_reviewer.send.return_value = """
        STRUCTURE: 9 - Excellent flow
        GRAMMAR: 10 - Perfect
        TECHNICAL_ACCURACY: 9 - Accurate
        ENGAGEMENT: 8 - Good hook
        ACTIONABILITY: 9 - Clear steps
        SEO: 8 - Optimized
        FORMATTING: 9 - Clean markdown
        DEPTH: 8 - Sufficient detail
        ORIGINALITY: 8 - Fresh perspective
        WORD_COUNT: 10 - 1000 words (perfect)
        TITLE: 9 - Catchy
        INTRO: 9 - Strong

        OVERALL_FEEDBACK: excellent work!
        APPROVAL_STATUS: APPROVED
        """

        # Create workflow
        app = create_blog_workflow()

        # Initial state
        state = {"topic": "Unit Testing", "min_words": 500, "max_words": 1500, "max_revisions": 3}

        # Mock user input to 'y' (approve)
        with (
            patch("builtins.input", return_value="y"),
            patch("builtins.print"),
        ):  # Silence print output
            result = app.invoke(state)

        # Assertions
        assert result["final_output"] == "# Draft Title\n\nPolished content."
        assert result["user_approved"] is True

        # Verify call counts
        assert mock_writer.send.call_count == 1
        assert mock_editor.send.call_count == 1
        assert mock_reviewer.send.call_count == 1

    def test_revision_loop(self, mock_agents):
        """Test flow with one revision: Writer -> Editor -> Reviewer (Reject) -> Writer -> Editor -> Reviewer (Approve)."""
        mock_writer, mock_editor, mock_reviewer = mock_agents

        # 1. Writer creates draft
        mock_writer.send.side_effect = [
            "# Bad Draft",  # Initial
            "# Improved Draft",  # Revision
        ]

        # 2. Editor polishes
        mock_editor.send.side_effect = [
            "# Polished Bad Draft",  # Initial
            "# Polished Improved Draft",  # After revision
        ]

        # 3. Reviewer rejects first, approves second
        mock_reviewer.send.side_effect = [
            # First review: Fail
            """
            STRUCTURE: 4 - Messy
            GRAMMAR: 5 - Typos
            TECHNICAL_ACCURACY: 8 - OK
            ENGAGEMENT: 4 - Boring
            ACTIONABILITY: 5 - Vague
            SEO: 5 - Weak
            FORMATTING: 6 - Issues
            DEPTH: 4 - Shallow
            ORIGINALITY: 5 - Generic
            WORD_COUNT: 10 - 1000 words
            TITLE: 5 - Boring
            INTRO: 4 - Weak

            OVERALL_FEEDBACK: Needs work.
            APPROVAL_STATUS: NEEDS_REVISION
            """,
            # Second review: Pass
            """
            STRUCTURE: 9 - Excellent
            GRAMMAR: 9 - Good
            TECHNICAL_ACCURACY: 9 - Good
            ENGAGEMENT: 9 - Good
            ACTIONABILITY: 9 - Good
            SEO: 9 - Good
            FORMATTING: 9 - Good
            DEPTH: 9 - Good
            ORIGINALITY: 9 - Good
            WORD_COUNT: 10 - 1000 words
            TITLE: 9 - Good
            INTRO: 9 - Good

            OVERALL_FEEDBACK: Much better.
            APPROVAL_STATUS: APPROVED
            """,
        ]

        app = create_blog_workflow()

        state = {"topic": "Refactoring", "min_words": 500, "max_words": 1500, "max_revisions": 3}

        with patch("builtins.input", return_value="y"), patch("builtins.print"):
            result = app.invoke(state)

        assert result["final_output"] == "# Polished Improved Draft"
        assert result["revision_count"] == 1

        # Writer called twice (initial + revision)
        assert mock_writer.send.call_count == 2
        # Editor called twice
        assert mock_editor.send.call_count == 2
        # Reviewer called twice
        assert mock_reviewer.send.call_count == 2

    def test_human_rejection_loop(self, mock_agents):
        """Test flow where human rejects first draft."""
        mock_writer, mock_editor, mock_reviewer = mock_agents

        # Mock responses (simplified for brevity)
        mock_writer.send.return_value = "Draft"
        mock_editor.send.return_value = "Polished"
        mock_reviewer.send.return_value = """
        STRUCTURE: 8 - Good
        GRAMMAR: 8 - Good
        TECHNICAL_ACCURACY: 8 - Good
        ENGAGEMENT: 8 - Good
        ACTIONABILITY: 8 - Good
        SEO: 8 - Good
        FORMATTING: 8 - Good
        DEPTH: 8 - Good
        ORIGINALITY: 8 - Good
        WORD_COUNT: 8 - Good
        TITLE: 8 - Good
        INTRO: 8 - Good
        APPROVAL_STATUS: APPROVED
        """

        app = create_blog_workflow()

        state = {"topic": "Human Loop", "min_words": 500, "max_words": 1500, "max_revisions": 3}

        # User rejects first ('n'), gives feedback, then approves second ('y')
        with (
            patch("builtins.input", side_effect=["n", "Make it punchier", "y"]),
            patch("builtins.print"),
        ):
            result = app.invoke(state)

        # Verify feedback was cleared in final state (consumed by writer)
        assert result["user_feedback"] == ""
        assert result["user_approved"] is True

        # Verify feedback was passed to writer in the revision call
        # 1st call: Initial draft (no feedback)
        # 2nd call: Revision with feedback
        call_args = mock_writer.send.call_args_list
        assert len(call_args) == 2
        revision_prompt = call_args[1][0][0]
        assert "Make it punchier" in revision_prompt
