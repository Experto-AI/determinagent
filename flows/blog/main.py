"""
Blog Workflow

Demonstrates the DeterminAgent library with provider interchangeability.

Usage:
    python blog-flow.py "AI Agents" --writer claude --editor claude --reviewer claude
    python blog-flow.py "Topic" --provider claude  # Use same provider for all
"""

import argparse
import re
import sys
import uuid
from datetime import datetime
from typing import Any, TypedDict, cast

from langgraph.graph import END, StateGraph

from determinagent import cli_utils, ui, utils
from determinagent.adapters import Provider
from determinagent.agent import UnifiedAgent
from determinagent.constants import resolve_model_alias
from determinagent.exceptions import DeterminAgentError, ProviderNotAvailable
from determinagent.parsers import format_text_stats, parse_review
from determinagent.sessions import SessionManager
from determinagent.validation import validate_providers

# ============================================================================
# Default Prompts (if not provided in config)
# ============================================================================

DEFAULT_WRITER_SYSTEM = "You are a professional blog writer."
DEFAULT_WRITER_TASK = "Write a blog post about {topic}."
DEFAULT_EDITOR_INSTRUCTIONS = "Edit the following blog post for clarity and style."
DEFAULT_REVIEWER_CATEGORIES = "Evaluate the blog post quality."
DEFAULT_REVISION_PROMPT = "Revise the blog post based on: {review}"

DEFAULT_WRITER_HUMAN_REVISION = """HUMAN REVIEWER FEEDBACK:
{user_feedback}

PREVIOUS VERSION:
{draft}

INSTRUCTIONS:
1. Address the human feedback above by REVISING your previous draft.
2. PRESERVE the existing content, structure, and key points.
3. DO NOT rewrite from scratch - make targeted improvements only.
4. If asked to shorten: TRIM content while keeping the best parts.
5. If asked to expand: ADD detail to existing sections.
6. Maintain word count between {min_words} and {max_words} words.

COPYWRITING RULES:
- Title: Use power words, create curiosity, promise clear benefit
- Introduction: Hook immediately, identify pain points, follow AIDA principles

CRITICAL OUTPUT RULES:
- Start DIRECTLY with the blog post title (e.g., "# Title Here").
- Do NOT include ANY introductory text.
- Do NOT include ANY closing remarks.
- Output ONLY the raw blog post Markdown.
"""

DEFAULT_EDITOR_INITIAL = """{editor_instructions}

WORD COUNT REQUIREMENT: Between {min_words} and {max_words} words.
IMPORTANT: DO NOT expand content beyond {max_words} words. Trim if necessary.

DRAFT TO EDIT:
{draft}"""

DEFAULT_EDITOR_SUBSEQUENT = """NEW VERSION TO EDIT:
{draft}

EDITING TASKS:
1. Apply consistent style based on your previous edits (in session memory).
2. Fix any new grammar, spelling, and style issues.
3. Improve clarity while PRESERVING the writer's key points.
4. Ensure title and introduction follow copywriting best practices.
5. MAINTAIN word count between {min_words} and {max_words} words.
6. DO NOT expand beyond {max_words} words - trim if necessary.

CRITICAL OUTPUT RULES:
- Start DIRECTLY with the blog post title (e.g., "# Title Here").
- Do NOT include ANY introductory text or meta-commentary.
- Do NOT include ANY closing remarks.
- Do NOT add separators like "---" before or after the content.
- Output ONLY the raw blog post Markdown. Nothing else."""

DEFAULT_REVIEWER_INITIAL = """YOUR ROLE: Strict Blog Post Reviewer

TASK: Evaluate the blog post quality.
WORD COUNT REQUIREMENT: Between {min_words} and {max_words} words.
ACTUAL CONTENT WORD COUNT: {content_words} words (measured, not estimated)

IMPORTANT: You are a STRICT reviewer. Only give scores of 8+ if the content truly excels.
The blog will ONLY pass to human review if ALL categories score 8 or higher.

BLOG POST TO REVIEW:
---
{content}
---

{reviewer_categories}

CRITICAL: Respond in EXACTLY this format (no markdown headers, no /10 suffixes):
STRUCTURE: [score] - [brief feedback]
GRAMMAR: [score] - [brief feedback]
TECHNICAL_ACCURACY: [score] - [brief feedback]
ENGAGEMENT: [score] - [brief feedback]
ACTIONABILITY: [score] - [brief feedback]
SEO: [score] - [brief feedback]
FORMATTING: [score] - [brief feedback]
DEPTH: [score] - [brief feedback]
ORIGINALITY: [score] - [brief feedback]
WORD_COUNT: [score] - [brief feedback with exact word count and analysis]
TITLE: [score] - [brief feedback]
INTRO: [score] - [brief feedback]

OVERALL_FEEDBACK: [2-3 sentence summary with specific improvement suggestions or "Ready for publication"]

APPROVAL_STATUS: [APPROVED if all categories >= 8, else NEEDS_REVISION]"""

DEFAULT_REVIEWER_SUBSEQUENT = """NEW VERSION TO REVIEW (iteration {iteration}):
---
{content}
---

ACTUAL CONTENT WORD COUNT: {content_words} words (measured, not estimated)
WORD COUNT REQUIREMENT: Between {min_words} and {max_words} words.

Compare this to the previous version you reviewed (in your session memory).

IMPORTANT: You are a STRICT reviewer. Only give scores of 8+ if content truly excels.
The blog will ONLY pass if ALL categories score 8 or higher.

{reviewer_categories}

CRITICAL: Respond in EXACTLY this format (no markdown headers, no /10 suffixes):
STRUCTURE: [score] - [brief feedback]
GRAMMAR: [score] - [brief feedback]
TECHNICAL_ACCURACY: [score] - [brief feedback]
ENGAGEMENT: [score] - [brief feedback]
ACTIONABILITY: [score] - [brief feedback]
SEO: [score] - [brief feedback]
FORMATTING: [score] - [brief feedback]
DEPTH: [score] - [brief feedback]
ORIGINALITY: [score] - [brief feedback]
WORD_COUNT: [score] - [brief feedback with exact word count and analysis]
TITLE: [score] - [brief feedback]
INTRO: [score] - [brief feedback]

OVERALL_FEEDBACK: [2-3 sentence summary]

APPROVAL_STATUS: [APPROVED if all >= 8, else NEEDS_REVISION]"""

# ============================================================================
# State Definition
# ============================================================================

TITLE_LINE_PATTERN = re.compile(r"^\s*#\s*\S")


def normalize_blog_markdown(text: str) -> str:
    """Normalize blog output to ensure it starts at the title line."""
    if not text:
        return text

    cleaned = text.lstrip("\ufeff").strip()
    fenced = re.match(r"^```(?:markdown|md)?\s*\n(.*)\n```$", cleaned, re.DOTALL)
    if fenced:
        cleaned = fenced.group(1).strip()

    lines = cleaned.splitlines()
    for idx, line in enumerate(lines):
        if TITLE_LINE_PATTERN.match(line):
            return "\n".join(lines[idx:]).strip()

    return cleaned


def format_session_label(session: SessionManager, is_first: bool) -> str:
    """Format session info for display, accounting for stateless providers."""
    if session.supports_resume():
        status = "NEW" if is_first else "RESUMED"
        return f"{utils.truncate_id(session.session_id)} ({status})"
    return "stateless (no resume)"


class BlogState(TypedDict):
    """LangGraph state for blog workflow."""

    topic: str
    min_words: int
    max_words: int

    draft: str
    edited: str
    review: str
    revision_count: int

    # AI approval
    is_approved: bool
    max_revisions: int

    # Human review phase
    user_approved: bool
    user_feedback: str
    in_human_phase: bool

    final_output: str


# ============================================================================
# Workflow Creation
# ============================================================================


def create_blog_workflow(
    writer_provider: Provider = "claude",
    editor_provider: Provider = "claude",
    reviewer_provider: Provider = "claude",
    writer_model: str = "balanced",
    editor_model: str = "fast",
    reviewer_model: str = "balanced",
    prompts: dict | None = None,
) -> Any:
    """
    Create blog post workflow with configurable providers.

    Args:
        writer_provider: Provider for writer agent
        editor_provider: Provider for editor agent
        reviewer_provider: Provider for reviewer agent
        *_model: Model aliases (fast/balanced/powerful)
        prompts: Dictionary of prompt templates

    Returns:
        Compiled LangGraph workflow
    """
    prompts = prompts or {}
    writer_system = prompts.get("writer_system", DEFAULT_WRITER_SYSTEM)
    writer_task_template = prompts.get("writer_task", DEFAULT_WRITER_TASK)
    editor_instructions = prompts.get("editor_instructions", DEFAULT_EDITOR_INSTRUCTIONS)
    reviewer_categories = prompts.get("reviewer_categories", DEFAULT_REVIEWER_CATEGORIES)
    revision_prompt_template = prompts.get("revision_prompt", DEFAULT_REVISION_PROMPT)
    writer_human_revision = prompts.get("writer_human_revision", DEFAULT_WRITER_HUMAN_REVISION)
    editor_initial_task = prompts.get("editor_initial", DEFAULT_EDITOR_INITIAL)
    editor_subsequent_task = prompts.get("editor_subsequent", DEFAULT_EDITOR_SUBSEQUENT)
    reviewer_initial_task = prompts.get("reviewer_initial", DEFAULT_REVIEWER_INITIAL)
    reviewer_subsequent_task = prompts.get("reviewer_subsequent", DEFAULT_REVIEWER_SUBSEQUENT)

    # Create agent instances
    writer = UnifiedAgent(
        provider=writer_provider,
        model=writer_model,
        role="writer",
        instructions=writer_system,
        session=SessionManager(writer_provider, str(uuid.uuid4())),
    )

    editor = UnifiedAgent(
        provider=editor_provider,
        model=editor_model,
        role="editor",
        instructions=editor_instructions,
        session=SessionManager(editor_provider, str(uuid.uuid4())),
    )

    reviewer = UnifiedAgent(
        provider=reviewer_provider,
        model=reviewer_model,
        role="reviewer",
        instructions=reviewer_categories,
        session=SessionManager(reviewer_provider, str(uuid.uuid4())),
    )

    # ========================================================================
    # Node Definitions
    # ========================================================================

    def writer_node(state: BlogState) -> dict:
        """Generate initial draft or revise based on human feedback."""
        is_first = state.get("revision_count", 0) == 0 and not state.get("in_human_phase", False)
        user_feedback = state.get("user_feedback", "")
        in_human_phase = state.get("in_human_phase", False)

        if in_human_phase and user_feedback:
            status = "Revising based on human feedback"
        elif is_first:
            status = "Generating initial"
        else:
            status = "Revising"

        session_label = format_session_label(writer.session, is_first)
        ui.print_header(
            f"WRITER - {status} blog post draft",
            f"📋 Session: {session_label}",
            icon="🖊️ ",
        )
        print(f"Topic: '{state['topic']}'")
        print(f"Word count target: {state['min_words']}-{state['max_words']} words")
        if user_feedback:
            print(f"User feedback: {user_feedback[:80]}...")
        ui.print_separator("-")

        # If we have user feedback, create a revision prompt with it
        if user_feedback:
            prompt = writer_human_revision.format(
                user_feedback=user_feedback,
                min_words=state["min_words"],
                max_words=state["max_words"],
                draft=state.get("edited") or state["draft"],
            )
        else:
            prompt = writer_task_template.format(
                topic=state["topic"], min_words=state["min_words"], max_words=state["max_words"]
            )

        draft = writer.send(prompt, allow_web=True)
        draft = normalize_blog_markdown(draft)

        # Calculate stats
        stats = format_text_stats(draft)
        print(f"✅ Draft created ({stats})")

        ui.display_content("WRITER OUTPUT", draft)

        return {
            "draft": draft,
            "revision_count": 0,
            "user_feedback": "",  # Clear user feedback after addressing it
        }

    def editor_node(state: BlogState) -> dict:
        """Edit the draft."""
        supports_resume = editor.session.supports_resume()
        is_first = editor.session.call_count == 0 or not supports_resume

        session_label = format_session_label(editor.session, is_first)
        ui.print_header(
            "EDITOR - Polishing the draft",
            f"📋 Session: {session_label}",
            icon="✏️ ",
        )

        min_words = state.get("min_words", 800)
        max_words = state.get("max_words", 1200)

        if supports_resume and not is_first:
            # On subsequent calls, reference the session memory
            prompt = editor_subsequent_task.format(
                draft=state["draft"], min_words=min_words, max_words=max_words
            )
        else:
            prompt = editor_initial_task.format(
                editor_instructions=editor_instructions,
                min_words=min_words,
                max_words=max_words,
                draft=state["draft"],
            )

        edited = editor.send(prompt)
        edited = normalize_blog_markdown(edited)

        # Calculate stats
        stats = format_text_stats(edited)
        print(f"✅ Edit complete ({stats})")

        ui.display_content("EDITOR OUTPUT", edited)

        return {"edited": edited}

    def reviewer_node(state: BlogState) -> dict:
        """Review and score the draft."""
        iteration = state.get("revision_count", 0)
        supports_resume = reviewer.session.supports_resume()
        is_first = reviewer.session.call_count == 0 or not supports_resume

        max_revs = state.get("max_revisions", 3)
        session_label = format_session_label(reviewer.session, is_first)
        ui.print_header(
            f"REVIEWER - Evaluating quality (Revision: {iteration + 1}/{max_revs})",
            f"📋 Session: {session_label}",
            icon="🤖",
        )

        content = state.get("edited") or state["draft"]
        min_words = state.get("min_words", 800)
        max_words = state.get("max_words", 1200)

        # Calculate and display stats
        stats = format_text_stats(content)
        print(f"Content to review: {stats}")

        # Calculate actual content word count for accurate feedback
        from determinagent.parsers import count_text_stats, strip_markdown

        raw_chars, raw_words, raw_lines = count_text_stats(content)
        plain_text = strip_markdown(content)
        _, content_words, _ = count_text_stats(plain_text)

        # Build the detailed reviewer prompt
        if supports_resume and not is_first:
            prompt = reviewer_subsequent_task.format(
                iteration=iteration + 1,
                content=content,
                content_words=content_words,
                min_words=min_words,
                max_words=max_words,
                reviewer_categories=reviewer_categories,
            )
        else:
            prompt = reviewer_initial_task.format(
                min_words=min_words,
                max_words=max_words,
                content_words=content_words,
                content=content,
                reviewer_categories=reviewer_categories,
            )

        # Include iteration number in prompt to ensure fresh evaluation
        review_response = reviewer.send(prompt)

        # Parse review
        review_result = parse_review(review_response, min_score=8)

        print("-" * 60)
        print("📝 REVIEWER FEEDBACK:")
        for cat in review_result.scores.values():
            status = "✅" if cat.score >= 8 else "❌"
            print(f"  {status} {cat.name}: {cat.score}/10 - {cat.feedback}")
        ui.print_separator("-")
        print(f"⭐ Min score: {review_result.min_score}/10")
        print(f"{'✅ APPROVED' if review_result.is_approved else '❌ NEEDS IMPROVEMENT'}")
        if review_result.overall_feedback:
            print(f"\nOVERALL FEEDBACK:\n{review_result.overall_feedback}")
        ui.print_separator("-")

        return {"review": review_response, "is_approved": review_result.is_approved}

    def revision_node(state: BlogState) -> dict:
        """Revise draft based on feedback."""
        session_label = format_session_label(writer.session, False)
        ui.print_header(
            "WRITER - Applying revisions",
            f"📋 Session: {session_label}",
            icon="🖊️ ",
        )

        # Extract low-scoring categories
        review_result = parse_review(state["review"])
        focus_areas = [
            f"- {cat.name}: {cat.score}/10 - {cat.feedback}"
            for cat in review_result.scores.values()
            if cat.score < 8
        ]
        focus_text = "\n".join(focus_areas)

        # Use the edited version (after editor polishing) as the base for revision
        current_version = state.get("edited") or state["draft"]

        prompt = revision_prompt_template.format(
            draft=current_version,
            review=state["review"],
            focus_areas=focus_text,
            min_words=state["min_words"],
            max_words=state["max_words"],
        )

        revised_draft = writer.send(prompt)
        revised_draft = normalize_blog_markdown(revised_draft)
        revision_count = state.get("revision_count", 0) + 1

        # Calculate stats
        stats = format_text_stats(revised_draft)
        print(f"✅ Revision {revision_count} complete ({stats})")

        ui.display_content("REVISED DRAFT", revised_draft)

        return {"draft": revised_draft, "revision_count": revision_count}

    def human_review_node(state: BlogState) -> dict:
        """Human review: shows blog to user and asks for approval."""
        ui.print_header("HUMAN REVIEW", icon="👤")

        # Display the blog post
        content = normalize_blog_markdown(state.get("edited") or state["draft"])
        ui.display_content("BLOG POST FOR YOUR REVIEW", content)

        # Show review summary
        review_result = parse_review(state.get("review", ""), min_score=8)
        print(f"AI Minimum Score: {review_result.min_score}/10")
        print(
            f"AI Review: {'✅ APPROVED' if review_result.is_approved else '❌ NEEDS IMPROVEMENT'}"
        )
        print(f"AI Iterations used: {state.get('revision_count', 0)}")
        print("")

        while True:
            choice = input("Do you approve this blog post? [y/n]: ").strip().lower()

            if choice == "y":
                print("\n✅ User APPROVED blog post")
                return {
                    "user_approved": True,
                    "in_human_phase": True,
                    "final_output": content,
                }
            elif choice == "n":
                feedback = input(
                    "\nWhat would you like to improve?\n(e.g., 'Add code examples', 'Make more technical', 'Shorten intro')\n> "
                ).strip()

                if not feedback:
                    print("⚠️  Please provide feedback to continue")
                    continue

                print(f"\n🔄 Sending back to writer with feedback: {feedback[:50]}...")
                return {
                    "user_approved": False,
                    "user_feedback": feedback,
                    "in_human_phase": True,
                    "is_approved": False,  # Reset AI approval for new loop
                    "revision_count": 0,  # Reset revision counter for new loop
                }
            else:
                print("❌ Invalid input. Please enter 'y' or 'n'")

    def finalize_node(state: BlogState) -> dict:
        """Finalize approved draft with cleanup."""
        ui.print_header("SUCCESS - Workflow complete", icon="🎉")

        final = state.get("final_output") or state.get("edited") or state["draft"]
        final = normalize_blog_markdown(final)

        # Clean up any HTML comments that may have been added by the editor
        final_clean = re.sub(r"<!--.*?-->", "", final, flags=re.DOTALL)
        # Clean up any double line breaks that remain after removing comments
        final_clean = re.sub(r"\n\s*\n\s*\n", "\n\n", final_clean)

        return {"final_output": final_clean.strip()}

    # ========================================================================
    # Conditional Routing
    # ========================================================================

    def route_after_review(state: BlogState) -> str:
        """Route based on AI approval status."""
        max_revs = state.get("max_revisions", 3)
        if state.get("is_approved"):
            print("\n🎉 AI approved! Moving to human review...")
            return "human_review"
        elif state.get("revision_count", 0) >= max_revs:
            print(f"\n⚠️  Max revisions ({max_revs}) reached. Moving to human review...")
            return "human_review"
        else:
            return "revise"

    def route_after_human(state: BlogState) -> str:
        """Route based on human approval status."""
        if state.get("user_approved"):
            return "finalize"
        else:
            print("\n🔄 User requested changes. Restarting Writer → Editor → Reviewer loop...")
            return "revise_from_human"

    # ========================================================================
    # Build Graph
    # ========================================================================

    workflow = StateGraph(BlogState)

    # Add nodes
    workflow.add_node("writer", writer_node)
    workflow.add_node("editor", editor_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("revise", revision_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("finalize", finalize_node)

    # Add edges
    workflow.set_entry_point("writer")
    workflow.add_edge("writer", "editor")
    workflow.add_edge("editor", "reviewer")

    # After AI reviewer: either continue revision loop or go to human review
    workflow.add_conditional_edges(
        "reviewer", route_after_review, {"human_review": "human_review", "revise": "revise"}
    )
    # After revision, send back to editor before re-review
    workflow.add_edge("revise", "editor")

    # After human review: either finalize or loop back to writer
    workflow.add_conditional_edges(
        "human_review",
        route_after_human,
        {
            "finalize": "finalize",
            "revise_from_human": "writer",  # Full restart with human feedback
        },
    )

    workflow.add_edge("finalize", END)

    return workflow.compile()


# ============================================================================
# CLI Interface
# ============================================================================

# ============================================================================
# CLI Interface
# ============================================================================


def main() -> None:
    # Load configuration
    from determinagent.config import load_config

    config = load_config()

    defaults_cfg = config.get("defaults", {})
    writer_def = defaults_cfg.get("writer", {}).get("provider", "claude")
    editor_def = defaults_cfg.get("editor", {}).get("provider", "claude")
    reviewer_def = defaults_cfg.get("reviewer", {}).get("provider", "claude")
    writer_model_def = defaults_cfg.get("writer", {}).get("model", "balanced")
    editor_model_def = defaults_cfg.get("editor", {}).get("model", "fast")
    reviewer_model_def = defaults_cfg.get("reviewer", {}).get("model", "balanced")

    word_count_cfg = config.get("word_count", {})
    min_words_def = word_count_cfg.get("min", 800)
    max_words_def = word_count_cfg.get("max", 1200)

    review_cfg = config.get("review", {})
    max_revs_def = review_cfg.get("max_revisions", 3)

    parser = argparse.ArgumentParser(description="Blog post generator using multiple CLI providers")

    parser.add_argument("topic", help="Blog post topic")

    # Add standardized provider arguments
    roles = ["writer", "editor", "reviewer"]
    defaults_map = {"writer": writer_def, "editor": editor_def, "reviewer": reviewer_def}
    cli_utils.add_provider_args(parser, roles, defaults_map)

    parser.add_argument(
        "--min-words",
        type=int,
        default=min_words_def,
        help=f"Minimum word count (default: {min_words_def})",
    )

    parser.add_argument(
        "--max-words",
        type=int,
        default=max_words_def,
        help=f"Maximum word count (default: {max_words_def})",
    )

    parser.add_argument(
        "--max-revisions",
        type=int,
        default=max_revs_def,
        help=f"Maximum number of revisions (default: {max_revs_def})",
    )

    args = parser.parse_args()

    # Resolve providers
    providers = cli_utils.resolve_provider_args(args, roles)
    writer_provider = cast(Provider, providers["writer"])
    editor_provider = cast(Provider, providers["editor"])
    reviewer_provider = cast(Provider, providers["reviewer"])

    # Validate providers are installed and accessible
    print()
    all_valid, validation_results = validate_providers(
        writer_provider, editor_provider, reviewer_provider, verbose=True
    )

    if not all_valid:
        print()
        print("❌ Provider validation failed. Some providers are not available.")
        print()
        print("Options:")
        print("  1. Install the missing provider(s)")
        print("  2. Switch to a different provider using --writer, --editor, or --reviewer")
        print()
        for result in validation_results:
            if result["status"] != "✅ available":
                print(f"  {result['role'].upper()}: {result['error']}")
        print()
        sys.exit(1)

    # Resolve model aliases to actual model names
    writer_model_resolved = resolve_model_alias(writer_model_def, writer_provider)
    editor_model_resolved = resolve_model_alias(editor_model_def, editor_provider)
    reviewer_model_resolved = resolve_model_alias(reviewer_model_def, reviewer_provider)

    # Display provider and model configuration
    print()
    ui.print_header("CONFIGURATION", icon="⚙️")
    print(f"  WRITER:   {writer_provider} ({writer_model_def} → {writer_model_resolved})")
    print(f"  EDITOR:   {editor_provider} ({editor_model_def} → {editor_model_resolved})")
    print(f"  REVIEWER: {reviewer_provider} ({reviewer_model_def} → {reviewer_model_resolved})")
    ui.print_separator("-")

    ui.print_header(
        "BLOG WORKFLOW",
        f"Topic: {args.topic}",
        icon="🚀",
    )

    print(f"Workflow: Writer → Editor → Reviewer (loop max {args.max_revisions})")
    print("          ↓ (if approved or max reached)")
    print("        Human Review")
    print("          ↓ (if rejected, restart loop)")
    print("        Save to file")
    ui.print_separator("=")

    # Create workflow
    workflow = create_blog_workflow(
        writer_provider=writer_provider,
        editor_provider=editor_provider,
        reviewer_provider=reviewer_provider,
        writer_model=writer_model_def,
        editor_model=editor_model_def,
        reviewer_model=reviewer_model_def,
        prompts=config.get("prompts"),
    )

    # Note: Session details are displayed within the workflow nodes during execution

    # Execute workflow
    initial_state = {
        "topic": args.topic,
        "min_words": args.min_words,
        "max_words": args.max_words,
        "max_revisions": args.max_revisions,
    }

    try:
        result = workflow.invoke(initial_state)

        # Save output
        output_cfg = config.get("output", {})
        filename_template = output_cfg.get("filename_template", "{date}-blog-{topic}.md")

        date_str = datetime.now().strftime("%Y-%m-%d")
        description = utils.sanitize_filename(args.topic)

        # Build filename from template
        output_file = filename_template.format(
            date=date_str,
            topic=description,
        )

        with open(output_file, "w") as f:
            f.write(result["final_output"])

        # Calculate final stats
        final_stats = format_text_stats(result["final_output"])

        ui.print_header(
            f"SUCCESS! Blog post saved to: {output_file}",
            f"📊 Final Stats: {final_stats}\n🔄 Revisions: {result.get('revision_count', 0)}",
            icon="✅",
        )

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        # Check if the error is one of ours (even if wrapped)
        def find_base_exception(exc: BaseException) -> BaseException:
            while exc.__cause__:
                exc = exc.__cause__
            return exc

        base_exc = find_base_exception(e)

        if isinstance(base_exc, ProviderNotAvailable):
            ui.print_header("PROVIDER ERROR", f"{base_exc}", icon="❌")
            print("Tip: Ensure the CLI tool is installed and authenticated.")
            sys.exit(1)

        if isinstance(base_exc, DeterminAgentError):
            ui.print_header("EXECUTION ERROR", f"{base_exc}", icon="❌")
            sys.exit(1)

        ui.print_header(f"UNEXPECTED ERROR: {e}", icon="❌")
        raise


if __name__ == "__main__":
    main()
