#!/usr/bin/env python3
"""
Provider validation utility for DeterminAgent.

This script validates that DeterminAgent provider CLIs are installed and accessible.

Usage:
    python scripts/validate_providers.py [--providers PROVIDER1,PROVIDER2,...]
    python scripts/validate_providers.py --help
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path so we can import determinagent
sys.path.insert(0, str(Path(__file__).parent.parent))

from determinagent import ui
from determinagent.validation import validate_providers_by_list


def main() -> int:
    """Main entry point for provider validation."""
    parser = argparse.ArgumentParser(
        description="Validate DeterminAgent provider CLIs are installed and accessible"
    )

    parser.add_argument(
        "--providers",
        type=str,
        default="writer:claude,editor:claude,reviewer:claude",
        help="Comma-separated list of role:provider pairs (default: writer:claude,editor:claude,reviewer:claude)",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only return exit code, no output",
    )

    args = parser.parse_args()

    # Parse providers from comma-separated list
    providers_list = {}
    try:
        for pair in args.providers.split(","):
            if ":" not in pair:
                print(f"Error: Invalid provider specification '{pair}'. Expected format: role:provider")
                return 1
            role, provider = pair.split(":", 1)
            providers_list[role.strip()] = provider.strip()
    except Exception as e:
        print(f"Error parsing providers: {e}")
        return 1

    if not providers_list:
        print("Error: No providers specified")
        return 1

    # Run validation
    verbose = not args.quiet
    all_valid, results = validate_providers_by_list(providers_list, verbose=verbose)

    if not all_valid:
        if not args.quiet:
            print()
            print("❌ Some providers are not available or not properly configured.")
        return 1

    if not args.quiet:
        print()
        print("✅ All providers validated successfully!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
