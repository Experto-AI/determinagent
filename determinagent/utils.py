"""
General utility functions for DeterminAgent.
"""

import re


def truncate_id(full_id: str, length: int = 8) -> str:
    """
    Truncate a UUID or long ID string for display.

    Args:
        full_id: The full ID string
        length: Number of characters to keep (default: 8)

    Returns:
        Truncated ID string ending in '...' if truncated
    """
    if len(full_id) <= length:
        return full_id
    return full_id[:length] + "..."


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """
    Sanitize a string for use as a filename.

    Args:
        name: Input string (e.g., blog topic)
        max_length: Maximum length of the result

    Returns:
        Safe filename string (lowercase, alphanumeric + hyphens)
    """
    # Replace non-alphanumeric characters with hyphens
    sanitized = re.sub(r"[^a-zA-Z0-9\-_]", "-", name)
    # Replace multiple hyphens with a single one
    sanitized = re.sub(r"-+", "-", sanitized)
    # Strip leading/trailing hyphens
    sanitized = sanitized.strip("-")

    # Limit length and try to avoid cutting in the middle of a word
    if len(sanitized) > max_length:
        truncated = sanitized[:max_length]
        sanitized = truncated.rsplit("-", 1)[0] if "-" in truncated else truncated

    return sanitized.lower()
