"""
Configuration loading and parsing utilities
"""

import os
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


def get_config_mtime(config_path: str = "config.toml") -> float:
    """Get the modification time of the configuration file

    Args:
        config_path: Path to the TOML configuration file

    Returns:
        Modification time as a timestamp (seconds since epoch)

    Raises:
        FileNotFoundError: If the configuration file is not found
    """
    return os.path.getmtime(config_path)


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


def print_config(config: Dict[str, Any]) -> None:
    """Print all configuration settings in a readable format

    Args:
        config: Configuration dictionary loaded from TOML
    """
    print("\n" + "=" * 50)
    print("Configuration Settings:")
    print("=" * 50)

    # Print main settings
    print("\n[Main Settings]")
    print(f"  interval: {config.get('interval', '1m')}")
    print(f"  issue_display_limit: {config.get('issue_display_limit', 10)}")
    print(f"  no_change_timeout: {config.get('no_change_timeout', '30m')}")
    print(f"  reduced_frequency_interval: {config.get('reduced_frequency_interval', '1h')}")
    print(f"  verbose: {config.get('verbose', False)}")

    # Print rulesets
    rulesets = config.get("rulesets", [])
    if rulesets and isinstance(rulesets, list):
        print("\n[Rulesets]")
        for i, ruleset in enumerate(rulesets, 1):
            if isinstance(ruleset, dict):
                print(f"\n  Ruleset #{i}:")
                print(f"    name: {ruleset.get('name', 'N/A')}")
                print(f"    repositories: {ruleset.get('repositories', [])}")
                print(f"    enable_execution_phase1_to_phase2: {ruleset.get('enable_execution_phase1_to_phase2', 'not set')}")
                print(f"    enable_execution_phase2_to_phase3: {ruleset.get('enable_execution_phase2_to_phase3', 'not set')}")
                print(f"    enable_execution_phase3_send_ntfy: {ruleset.get('enable_execution_phase3_send_ntfy', 'not set')}")
                print(f"    enable_execution_phase3_to_merge: {ruleset.get('enable_execution_phase3_to_merge', 'not set')}")
    else:
        print("\n[Rulesets]")
        print("  No rulesets configured")

    # Print ntfy settings
    ntfy = config.get("ntfy")
    if ntfy and isinstance(ntfy, dict):
        print("\n[ntfy.sh Notification Settings]")
        print(f"  enabled: {ntfy.get('enabled', False)}")
        if ntfy.get('enabled', False):
            print(f"  topic: {ntfy.get('topic', 'N/A')}")
            print(f"  message: {ntfy.get('message', 'N/A')}")
            print(f"  priority: {ntfy.get('priority', 4)}")

    # Print phase3_merge settings
    phase3_merge = config.get("phase3_merge")
    if phase3_merge and isinstance(phase3_merge, dict):
        print("\n[Phase3 Merge Settings]")
        print(f"  enabled: {phase3_merge.get('enabled', False)}")
        if phase3_merge.get('enabled', False):
            print(f"  comment: {phase3_merge.get('comment', 'N/A')}")
            print(f"  automated: {phase3_merge.get('automated', False)}")
            if phase3_merge.get('automated', False):
                print(f"  automation_backend: {phase3_merge.get('automation_backend', 'selenium')}")
                print(f"  wait_seconds: {phase3_merge.get('wait_seconds', 10)}")
                print(f"  browser: {phase3_merge.get('browser', 'edge')}")
                print(f"  headless: {phase3_merge.get('headless', False)}")

    # Print assign_to_copilot settings
    assign_to_copilot = config.get("assign_to_copilot")
    if assign_to_copilot and isinstance(assign_to_copilot, dict):
        print("\n[Auto-assign to Copilot Settings]")
        print(f"  enabled: {assign_to_copilot.get('enabled', False)}")
        if assign_to_copilot.get('enabled', False):
            print(f"  assign_lowest_number_issue: {assign_to_copilot.get('assign_lowest_number_issue', False)}")
            print(f"  automated: {assign_to_copilot.get('automated', False)}")
            if assign_to_copilot.get('automated', False):
                print(f"  automation_backend: {assign_to_copilot.get('automation_backend', 'selenium')}")
                print(f"  wait_seconds: {assign_to_copilot.get('wait_seconds', 10)}")
                print(f"  browser: {assign_to_copilot.get('browser', 'edge')}")
                print(f"  headless: {assign_to_copilot.get('headless', False)}")

    print("\n" + "=" * 50)


def resolve_execution_config_for_repo(
    config: Dict[str, Any], repo_owner: str, repo_name: str
) -> Dict[str, Any]:
    """Resolve execution configuration for a specific repository using rulesets

    This function applies rulesets in order, with later rulesets overriding earlier ones.
    Global execution flags are no longer supported - all settings must be in rulesets.

    Args:
        config: Configuration dictionary loaded from TOML
        repo_owner: Repository owner (kept for compatibility, but not used in matching)
        repo_name: Repository name

    Returns:
        Dictionary with execution flags and feature settings:
        - enable_execution_phase1_to_phase2
        - enable_execution_phase2_to_phase3
        - enable_execution_phase3_send_ntfy
        - enable_execution_phase3_to_merge
        - phase3_merge: dict with phase3_merge settings
        - assign_to_copilot: dict with assign_to_copilot settings
    """
    # Start with all flags disabled (no global defaults)
    result = {
        "enable_execution_phase1_to_phase2": False,
        "enable_execution_phase2_to_phase3": False,
        "enable_execution_phase3_send_ntfy": False,
        "enable_execution_phase3_to_merge": False,
        "enable_phase3_merge": None,  # None means not set by rulesets, use global
        "enable_assign_to_copilot": None,  # None means not set by rulesets, use global
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
            # Match by repository name only
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
            if "enable_execution_phase3_to_merge" in ruleset:
                result["enable_execution_phase3_to_merge"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase3_to_merge"], "enable_execution_phase3_to_merge"
                )
            
            # Apply simple on/off flags for phase3_merge and assign_to_copilot
            if "enable_phase3_merge" in ruleset:
                result["enable_phase3_merge"] = _validate_boolean_flag(
                    ruleset["enable_phase3_merge"], "enable_phase3_merge"
                )
            if "enable_assign_to_copilot" in ruleset:
                result["enable_assign_to_copilot"] = _validate_boolean_flag(
                    ruleset["enable_assign_to_copilot"], "enable_assign_to_copilot"
                )

    return result


def print_repo_execution_config(
    repo_owner: str, repo_name: str, exec_config: Dict[str, Any]
) -> None:
    """Print execution configuration for a specific repository

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        exec_config: Execution configuration dictionary
    """
    print(f"    [Execution Config for {repo_name}]")
    print(f"      enable_execution_phase1_to_phase2: {exec_config.get('enable_execution_phase1_to_phase2', False)}")
    print(f"      enable_execution_phase2_to_phase3: {exec_config.get('enable_execution_phase2_to_phase3', False)}")
    print(f"      enable_execution_phase3_send_ntfy: {exec_config.get('enable_execution_phase3_send_ntfy', False)}")
    print(f"      enable_execution_phase3_to_merge: {exec_config.get('enable_execution_phase3_to_merge', False)}")
    print(f"      enable_phase3_merge: {exec_config.get('enable_phase3_merge', False)}")
    print(f"      enable_assign_to_copilot: {exec_config.get('enable_assign_to_copilot', False)}")
