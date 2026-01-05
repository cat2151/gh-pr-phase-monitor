"""
Configuration loading and parsing utilities
"""

import re
from typing import Any, Dict

import tomli


def parse_interval(interval_str: str) -> int:
    """Parse interval string like '1m', '30s', '2h' to seconds

    Args:
        interval_str: String like '1m', '30s', '2h', '1d'

    Returns:
        Number of seconds

    Raises:
        ValueError: If the interval string format is invalid
    """
    # Type validation for common misconfiguration
    if not isinstance(interval_str, str):
        raise ValueError(
            f"Interval must be a string (e.g., '1m', '30s'), got {type(interval_str).__name__}: {interval_str}"
        )

    interval_str = interval_str.strip().lower()

    # Match pattern like "30s", "1m", "2h", "1d"
    match = re.match(r"^(\d+)([smhd])$", interval_str)

    if not match:
        raise ValueError(
            f"Invalid interval format: '{interval_str}'. "
            "Expected format: <number><unit> (e.g., '30s', '1m', '2h', '1d')"
        )

    value = int(match.group(1))
    unit = match.group(2)

    # Convert to seconds
    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    else:  # unit == "d"
        return value * 86400


def _validate_boolean_flag(value: Any, flag_name: str) -> bool:
    """Validate that a configuration flag is a boolean value

    Args:
        value: The value to validate
        flag_name: Name of the flag for error messages

    Returns:
        The boolean value

    Raises:
        ValueError: If the value is not a boolean
    """
    if not isinstance(value, bool):
        raise ValueError(
            f"Configuration flag '{flag_name}' must be a boolean (true/false), "
            f"got {type(value).__name__}: {value}"
        )
    return value


def load_config(config_path: str = "config.toml") -> Dict[str, Any]:
    """Load configuration from TOML file

    Args:
        config_path: Path to the TOML configuration file

    Returns:
        Dictionary containing configuration data

    Raises:
        FileNotFoundError: If the configuration file is not found
    """
    with open(config_path, "rb") as f:
        return tomli.load(f)


def resolve_execution_config_for_repo(
    config: Dict[str, Any], repo_owner: str, repo_name: str
) -> Dict[str, bool]:
    """Resolve execution configuration for a specific repository using rulesets

    This function applies rulesets in order, with later rulesets overriding earlier ones.
    First applies global settings, then applies matching rulesets.

    Args:
        config: Configuration dictionary loaded from TOML
        repo_owner: Repository owner
        repo_name: Repository name

    Returns:
        Dictionary with execution flags:
        - enable_execution_phase1_to_phase2
        - enable_execution_phase2_to_phase3
        - enable_execution_phase3_send_ntfy
    """
    # Full repository identifier
    repo_full_name = f"{repo_owner}/{repo_name}"

    # Start with global defaults (backward compatibility) with validation
    def get_validated_flag(flag_name: str, default: bool = False) -> bool:
        """Get and validate a global configuration flag"""
        value = config.get(flag_name, default)
        # Only validate if the value was actually provided in config (not using default)
        if flag_name in config:
            return _validate_boolean_flag(value, flag_name)
        return value

    result = {
        "enable_execution_phase1_to_phase2": get_validated_flag("enable_execution_phase1_to_phase2", False),
        "enable_execution_phase2_to_phase3": get_validated_flag("enable_execution_phase2_to_phase3", False),
        "enable_execution_phase3_send_ntfy": get_validated_flag("enable_execution_phase3_send_ntfy", False),
    }

    # Apply rulesets if they exist
    rulesets = config.get("rulesets", [])
    if not isinstance(rulesets, list):
        return result

    for ruleset in rulesets:
        if not isinstance(ruleset, dict):
            continue

        # Get target repositories for this ruleset
        repositories = ruleset.get("repositories", [])
        if not isinstance(repositories, list):
            continue

        # Check if this ruleset applies to the current repository
        applies = False
        for repo_pattern in repositories:
            if not isinstance(repo_pattern, str):
                continue
            # "all" matches all repositories
            if repo_pattern.lower() == "all":
                applies = True
                break
            # Exact match with full name (owner/repo)
            if repo_pattern == repo_full_name:
                applies = True
                break
            # Match just the repo name (for backward compatibility)
            if repo_pattern == repo_name:
                applies = True
                break

        # If this ruleset applies, override execution flags with validation
        if applies:
            if "enable_execution_phase1_to_phase2" in ruleset:
                result["enable_execution_phase1_to_phase2"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase1_to_phase2"], "enable_execution_phase1_to_phase2"
                )
            if "enable_execution_phase2_to_phase3" in ruleset:
                result["enable_execution_phase2_to_phase3"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase2_to_phase3"], "enable_execution_phase2_to_phase3"
                )
            if "enable_execution_phase3_send_ntfy" in ruleset:
                result["enable_execution_phase3_send_ntfy"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase3_send_ntfy"], "enable_execution_phase3_send_ntfy"
                )

    return result
