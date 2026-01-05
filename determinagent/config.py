"""
Configuration loading utilities.

This module provides functions for loading configuration from YAML files,
with automatic discovery based on the running script name.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import yaml

from .exceptions import ConfigurationError


def load_config(
    path: str | Path | None = None,
    required: bool = False,
) -> dict[str, Any]:
    """
    Load configuration from a YAML file.

    If path is provided, it is used directly. Otherwise, attempts to find
    a config file with the same name as the running script but with a
    `.yaml` extension.

    Args:
        path: Optional explicit path to the configuration file.
              Can be a string or Path object.
        required: If True, raise ConfigurationError if file not found.
                 If False (default), return empty dict.

    Returns:
        Dictionary containing the configuration, or empty dict if not found
        and `required` is False.

    Raises:
        ConfigurationError: If required=True and config file not found,
                           or if YAML parsing fails.

    Example:
        ```python
        # Auto-discover config (e.g., script.yaml for script.py)
        config = load_config()

        # Explicit path
        config = load_config("my-config.yaml")

        # Required config
        config = load_config("settings.yaml", required=True)
        ```
    """
    config_path: Path

    if path is None:
        # Auto-discover: Use script name with .yaml extension
        main_script = sys.argv[0]
        base, _ = os.path.splitext(main_script)
        config_path = Path(f"{base}.yaml")
    else:
        config_path = Path(path) if isinstance(path, str) else path

    if not config_path.exists():
        if required:
            raise ConfigurationError(f"Required configuration file not found: {config_path}")
        return {}

    try:
        with open(config_path, encoding="utf-8") as f:
            content = yaml.safe_load(f)
            return content if content is not None else {}
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in configuration file {config_path}: {e}") from e
    except OSError as e:
        if required:
            raise ConfigurationError(f"Error reading configuration file {config_path}: {e}") from e
        return {}


def load_config_from_string(content: str) -> dict[str, Any]:
    """
    Load configuration from a YAML string.

    Args:
        content: YAML content as a string.

    Returns:
        Dictionary containing the configuration.

    Raises:
        ConfigurationError: If YAML parsing fails.

    Example:
        ```python
        config = load_config_from_string('''
        name: my-workflow
        agents:
          writer:
            provider: claude
            model: balanced
        ''')
        ```
    """
    try:
        result = yaml.safe_load(content)
        return result if result is not None else {}
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML content: {e}") from e


def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    """
    Merge multiple configuration dictionaries.

    Later configs override earlier ones. Nested dictionaries are merged
    recursively.

    Args:
        *configs: Configuration dictionaries to merge.

    Returns:
        Merged configuration dictionary.

    Example:
        ```python
        base = {"debug": False, "agent": {"model": "fast"}}
        override = {"agent": {"model": "balanced"}}
        merged = merge_configs(base, override)
        # Result: {"debug": False, "agent": {"model": "balanced"}}
        ```
    """
    result: dict[str, Any] = {}

    for config in configs:
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = merge_configs(result[key], value)
            else:
                result[key] = value

    return result
