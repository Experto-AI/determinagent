"""
CLI utilities for building agent arguments.
"""

import argparse


def add_provider_args(
    parser: argparse.ArgumentParser,
    roles: list[str],
    defaults: dict[str, str] | None = None,
) -> None:
    """
    Add standard provider selection arguments to an argparse parser.

    Adds:
    - --provider: Global override
    - --{role}-provider: Role-specific provider

    Args:
        parser: The ArgumentParser instance
        roles: List of role names (e.g., ['writer', 'editor'])
        defaults: Dictionary mapping role names to default provider names
    """
    defaults = defaults or {}
    choices = ["claude", "copilot", "gemini", "codex"]

    # Global provider override
    parser.add_argument(
        "--provider",
        choices=choices,
        help="Use same provider for all agents (overrides specific settings)",
    )

    # Role-specific providers
    for role in roles:
        default_val = defaults.get(role, "claude")
        parser.add_argument(
            f"--{role}-provider",
            dest=f"{role}_provider",
            default=default_val,
            choices=choices,
            help=f"Provider for {role} agent (default: {default_val})",
        )


def resolve_provider_args(args: argparse.Namespace, roles: list[str]) -> dict[str, str]:
    """
    Resolve provider selections handling variable precedence.

    Logic:
    1. If args.provider is set, it overrides everything.
    2. Otherwise, use the specific args.{role}_provider value.

    Args:
        args: Parsed arguments
        roles: List of role names

    Returns:
        Dictionary mapping role -> provider_name
    """
    providers = {}

    if hasattr(args, "provider") and args.provider:
        # Global override
        for role in roles:
            providers[role] = args.provider
    else:
        # Specific assignments
        for role in roles:
            providers[role] = getattr(args, f"{role}_provider")

    return providers
