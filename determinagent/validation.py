"""
Provider validation utilities for DeterminAgent.

Provides functions to validate that CLI providers are installed and accessible.
"""

from typing import TypedDict

from determinagent.adapters import Provider
from determinagent.exceptions import ProviderAuthError, ProviderNotAvailable
from determinagent.sessions import SessionManager


class ValidationResult(TypedDict):
    """Result of a single provider validation."""

    role: str
    provider: Provider
    status: str  # "✅ available", "❌ not installed", "⚠️  auth failed", "⚠️  error"
    error: str | None


def validate_provider(provider: Provider, role: str = "test") -> ValidationResult:
    """
    Validate a single provider is installed and accessible.

    Args:
        provider: The provider to validate (claude, copilot, gemini, codex)
        role: Role name for error messages (default: "test")

    Returns:
        ValidationResult dict with status and error information
    """
    # Import here to avoid circular dependency
    from determinagent.agent import get_adapter

    result: ValidationResult = {
        "role": role,
        "provider": provider,
        "status": "unknown",
        "error": None,
    }

    try:
        # Attempt to get adapter to verify provider exists
        _ = get_adapter(provider)

        # Try a simple version-like check by creating a test session
        # This will cause the adapter to be invoked minimally
        _ = SessionManager(provider, "validation-test")

        # Mark as valid
        result["status"] = "✅ available"

    except ProviderNotAvailable as e:
        result["status"] = "❌ not installed"
        result["error"] = str(e)

    except ProviderAuthError as e:
        result["status"] = "⚠️  auth failed"
        result["error"] = str(e)

    except Exception as e:
        result["status"] = "⚠️  error"
        result["error"] = str(e)

    return result


def validate_providers(
    writer_provider: Provider,
    editor_provider: Provider,
    reviewer_provider: Provider,
    verbose: bool = True,
) -> tuple[bool, list[ValidationResult]]:
    """
    Validate that all selected providers are installed and accessible.

    Args:
        writer_provider: Provider for writer role
        editor_provider: Provider for editor role
        reviewer_provider: Provider for reviewer role
        verbose: If True, print validation results (default: True)

    Returns:
        (all_valid, results) tuple where:
        - all_valid: True if all providers are available
        - results: List of ValidationResult dicts for each provider
    """
    from determinagent import ui  # Import here to avoid circular dependency

    providers = {
        "writer": writer_provider,
        "editor": editor_provider,
        "reviewer": reviewer_provider,
    }
    results = []
    all_valid = True

    if verbose:
        ui.print_header("PROVIDER VALIDATION", icon="🔍")

    for role, provider in providers.items():
        result = validate_provider(provider, role)
        results.append(result)
        all_valid = all_valid and result["status"] == "✅ available"

        if verbose:
            print(f"  {result['status']} {role.upper():8} ({provider})")
            if result["error"]:
                print(f"       Error: {result['error']}")

    if verbose:
        ui.print_separator("-")

    return all_valid, results


def validate_providers_by_list(
    providers: dict[str, Provider], verbose: bool = True
) -> tuple[bool, list[ValidationResult]]:
    """
    Validate a custom list of providers.

    Args:
        providers: Dict of role -> provider (e.g., {"writer": "claude", "tool": "gemini"})
        verbose: If True, print validation results (default: True)

    Returns:
        (all_valid, results) tuple where:
        - all_valid: True if all providers are available
        - results: List of ValidationResult dicts for each provider
    """
    from determinagent import ui  # Import here to avoid circular dependency

    results = []
    all_valid = True

    if verbose:
        ui.print_header("PROVIDER VALIDATION", icon="🔍")

    for role, provider in providers.items():
        result = validate_provider(provider, role)
        results.append(result)
        all_valid = all_valid and result["status"] == "✅ available"

        if verbose:
            print(f"  {result['status']} {role.upper():8} ({provider})")
            if result["error"]:
                print(f"       Error: {result['error']}")

    if verbose:
        ui.print_separator("-")

    return all_valid, results
