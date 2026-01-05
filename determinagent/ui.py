"""
UI utilities for DeterminAgent flows.

This module provides standardized console output formatting to ensure a consistent
look and feel across different agent workflows.
"""


def print_separator(char: str = "=", length: int = 60) -> None:
    """Print a separator line."""
    print(char * length)


def print_header(title: str, subtitle: str = "", icon: str = "", length: int = 60) -> None:
    """
    Print a standardized header block.

    Args:
        title: Main title text
        subtitle: Optional subtitle text (e.g., session ID)
        icon: Optional icon or emoji prefix for the title
        length: Length of separator lines
    """
    print("\n" + "=" * length)
    if icon:
        print(f"{icon} {title}")
    else:
        print(title)

    if subtitle:
        print(subtitle)
    print("=" * length)


def display_content(title: str, content: str, char: str = "=", length: int = 60) -> None:
    """
    Display a block of content with a titled header.

    Args:
        title: Title for the content block
        content: The content to display
        char: Separator character
        length: Length of separator lines
    """
    print("\n" + char * length)
    print(f"📄 {title}")
    print(char * length)
    print(content)
    print(char * length + "\n")
