#!/usr/bin/env python3
"""
Version Bump Script for DeterminAgent

Synchronizes version numbers across pyproject.toml and determinagent/__init__.py.
Ensures consistent versioning before releases.

Usage:
    python scripts/bump_version.py <new_version>
    python scripts/bump_version.py 0.11.0
    python scripts/bump_version.py --check  # Verify versions are in sync

Examples:
    # Bump to new version
    python scripts/bump_version.py 1.0.0

    # Check current version sync status
    python scripts/bump_version.py --check
"""

import argparse
import re
import sys
from pathlib import Path

# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
INIT_PATH = PROJECT_ROOT / "determinagent" / "__init__.py"

# Regex patterns for version matching
PYPROJECT_VERSION_PATTERN = re.compile(r'^version = "([^"]+)"', re.MULTILINE)
INIT_VERSION_PATTERN = re.compile(r'^__version__ = "([^"]+)"', re.MULTILINE)

# Semantic versioning pattern (with optional pre-release and build metadata)
SEMVER_PATTERN = re.compile(
    r"^(\d+)\.(\d+)\.(\d+)"  # Major.Minor.Patch
    r"(-(?:alpha|beta|rc)\.?\d*)?"  # Optional pre-release
    r"(\+[\w.]+)?$"  # Optional build metadata
)


def get_pyproject_version() -> str:
    """Extract version from pyproject.toml."""
    content = PYPROJECT_PATH.read_text()
    match = PYPROJECT_VERSION_PATTERN.search(content)
    if not match:
        raise ValueError(f"Could not find version in {PYPROJECT_PATH}")
    return match.group(1)


def get_init_version() -> str:
    """Extract version from __init__.py."""
    content = INIT_PATH.read_text()
    match = INIT_VERSION_PATTERN.search(content)
    if not match:
        raise ValueError(f"Could not find __version__ in {INIT_PATH}")
    return match.group(1)


def validate_semver(version: str) -> bool:
    """Validate that version follows semantic versioning."""
    return bool(SEMVER_PATTERN.match(version))


def set_pyproject_version(new_version: str) -> None:
    """Update version in pyproject.toml."""
    content = PYPROJECT_PATH.read_text()
    new_content = PYPROJECT_VERSION_PATTERN.sub(f'version = "{new_version}"', content)
    PYPROJECT_PATH.write_text(new_content)
    print(f"✅ Updated pyproject.toml to version {new_version}")


def set_init_version(new_version: str) -> None:
    """Update version in __init__.py."""
    content = INIT_PATH.read_text()
    new_content = INIT_VERSION_PATTERN.sub(f'__version__ = "{new_version}"', content)
    INIT_PATH.write_text(new_content)
    print(f"✅ Updated __init__.py to version {new_version}")


def check_versions() -> bool:
    """Check if versions are in sync across files."""
    try:
        pyproject_ver = get_pyproject_version()
        init_ver = get_init_version()

        print(f"📦 pyproject.toml:           {pyproject_ver}")
        print(f"📦 determinagent/__init__.py: {init_ver}")

        if pyproject_ver == init_ver:
            print(f"\n✅ Versions are in sync: {pyproject_ver}")
            return True
        else:
            print("\n❌ Version mismatch detected!")
            print("   Run: python scripts/bump_version.py <version>")
            return False
    except ValueError as e:
        print(f"❌ Error: {e}")
        return False


def bump_version(new_version: str) -> bool:
    """Bump version in all files."""
    # Validate semantic versioning
    if not validate_semver(new_version):
        print(f"❌ Invalid version format: {new_version}")
        print("   Expected: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]")
        print("   Examples: 1.0.0, 0.11.0-alpha.1, 2.0.0-rc.1")
        return False

    # Get current versions for display
    try:
        current_pyproject = get_pyproject_version()
        current_init = get_init_version()
    except ValueError as e:
        print(f"❌ Error reading current version: {e}")
        return False

    print(f"📦 Current versions:")
    print(f"   pyproject.toml:           {current_pyproject}")
    print(f"   determinagent/__init__.py: {current_init}")
    print(f"\n🔄 Bumping to: {new_version}")

    # Update both files
    try:
        set_pyproject_version(new_version)
        set_init_version(new_version)
    except Exception as e:
        print(f"❌ Error updating version: {e}")
        return False

    print(f"\n🎉 Successfully bumped version to {new_version}")
    print("\n📋 Next steps:")
    print(f"   1. git add pyproject.toml determinagent/__init__.py")
    print(f"   2. git commit -m 'chore: bump version to {new_version}'")
    print(f"   3. git tag v{new_version}")
    print(f"   4. git push origin main --tags")
    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bump version across all DeterminAgent files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 1.0.0           Bump to version 1.0.0
  %(prog)s 0.11.0-alpha.1  Bump to pre-release version
  %(prog)s --check         Verify versions are in sync
        """,
    )
    parser.add_argument(
        "version",
        nargs="?",
        help="New version number (e.g., 1.0.0, 0.11.0-beta.1)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if versions are in sync (no changes made)",
    )

    args = parser.parse_args()

    # Handle --check mode
    if args.check:
        return 0 if check_versions() else 1

    # Require version argument if not checking
    if not args.version:
        parser.print_help()
        return 1

    # Bump version
    return 0 if bump_version(args.version) else 1


if __name__ == "__main__":
    sys.exit(main())
