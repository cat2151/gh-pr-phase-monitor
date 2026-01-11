"""
Main execution module for GitHub PR Phase Monitor
"""

import signal
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import tomli

from .colors import colorize_phase
from .config import get_config_mtime, load_config, parse_interval, print_config, resolve_execution_config_for_repo
from .github_client import (
    assign_issue_to_copilot,
    get_issues_from_repositories,
    get_pr_details_batch,
    get_repositories_with_no_prs_and_open_issues,
    get_repositories_with_open_prs,
)
from .phase_detector import PHASE_3, PHASE_LLM_WORKING, determine_phase
from .pr_actions import process_pr

# Track PR states and detection times
# Key: (pr_url, phase), Value: timestamp when first detected
_pr_state_times: Dict[Tuple[str, str], float] = {}

# Track when the overall PR state last changed
# This includes: (last_state_snapshot, timestamp when state started)
# State snapshot is a frozenset of (pr_url, phase) tuples
_last_state: Optional[Tuple[frozenset, float]] = None

# Track the current monitoring mode
# True = reduced frequency mode (uses the configured reduced_frequency_interval), False = normal mode
_reduced_frequency_mode: bool = False


def format_elapsed_time(seconds: float) -> str:
    """Format elapsed time in Japanese style
    
    Args:
        seconds: Elapsed time in seconds
        
    Returns:
        Formatted string like "3分20秒"
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)

    if minutes > 0:
        return f"{minutes}分{secs}秒"
    else:
        return f"{secs}秒"


def wait_with_countdown(
    interval_seconds: int,
    interval_str: str,
    config_path: str = "",
    last_config_mtime: float = 0.0
) -> Tuple[Dict[str, Any], int, str, float]:
    """Wait for the specified interval with a live countdown display and hot reload support
    
    This function checks the config file's modification timestamp every second during the wait.
    If the config file has been modified, it reloads the configuration and updates the interval.
    
    Note: The filesystem check every second is intentional per the issue requirements for
    hot reload functionality during the wait state.
    
    Args:
        interval_seconds: Number of seconds to wait
        interval_str: Human-readable interval string (e.g., "1m", "30s")
        config_path: Path to the configuration file (empty string disables hot reload)
        last_config_mtime: Last known modification time of the config file
    
    Returns:
        Tuple of (config, interval_seconds, interval_str, new_config_mtime)
    """
    print(f"\n{'=' * 50}")
    print(f"Waiting {interval_str} until next check...")
    print(f"{'=' * 50}")

    # Current config values (may be updated during wait)
    current_config = {}
    current_interval_seconds = interval_seconds
    current_interval_str = interval_str
    current_mtime = last_config_mtime

    # Track actual elapsed time from the start of wait
    wait_start_time = time.time()

    # Display countdown with updates every second using ANSI escape sequences
    while True:
        # Calculate actual elapsed time
        actual_elapsed = time.time() - wait_start_time

        # Check if we've waited long enough
        if actual_elapsed >= interval_seconds:
            break

        elapsed_str = format_elapsed_time(actual_elapsed)
        # Print countdown on same line using carriage return
        print(f"\r待機中... 経過時間: {elapsed_str}     ", end="", flush=True)

        # Calculate remaining time
        remaining = interval_seconds - actual_elapsed
        sleep_duration = min(1, remaining)
        time.sleep(sleep_duration)

        # Check if config file has been modified (only if config_path is provided)
        # Note: This check happens every second as per hot reload requirements
        if config_path:
            try:
                new_mtime = get_config_mtime(config_path)
                if new_mtime != current_mtime:
                    # Config file has been modified, reload it
                    print(f"\n\n{'=' * 50}")
                    print("設定ファイルの変更を検知しました。再読み込みします...")
                    print(f"{'=' * 50}")

                    try:
                        new_config = load_config(config_path)
                        new_interval_str = new_config.get("interval", "1m")
                        new_interval_seconds = parse_interval(new_interval_str)

                        # Update current values
                        current_config = new_config
                        current_interval_seconds = new_interval_seconds
                        current_interval_str = new_interval_str
                        current_mtime = new_mtime

                        print("設定を再読み込みしました。")
                        print(f"新しい監視間隔: {new_interval_str} ({new_interval_seconds}秒)")

                        # Print config if verbose mode is enabled
                        if new_config.get("verbose", False):
                            print_config(new_config)

                        print(f"{'=' * 50}")
                        print(f"Waiting {current_interval_str} until next check...")
                        print(f"{'=' * 50}")

                    except (ValueError, tomli.TOMLDecodeError) as e:
                        # Config file has invalid format (TOML parsing error or invalid interval)
                        # Update mtime to avoid repeatedly trying to reload the same broken config
                        current_mtime = new_mtime
                        print(f"設定ファイルの再読み込みに失敗しました: {e}")
                        print("前の設定を使い続けます。")
                        print(f"{'=' * 50}")
                        print(f"Waiting {current_interval_str} until next check...")
                        print(f"{'=' * 50}")

            except FileNotFoundError:
                # Config file was deleted, continue with current config
                pass
            except (OSError, PermissionError):
                # File system errors (e.g., permission issues), ignore and continue
                pass

    # Final update - show actual elapsed time
    actual_elapsed = time.time() - wait_start_time
    elapsed_str = format_elapsed_time(actual_elapsed)
    print(f"\r待機中... 経過時間: {elapsed_str}     ", flush=True)
    print()  # New line after countdown completes

    return current_config, current_interval_seconds, current_interval_str, current_mtime


def cleanup_old_pr_states(current_prs_with_phases: List[Tuple[str, str]]) -> None:
    """Clean up PR state tracking for PRs that no longer exist or changed phase
    
    Args:
        current_prs_with_phases: List of tuples (pr_url, phase) for current PRs
    """
    current_keys = set(current_prs_with_phases)
    # Filter the existing state dict in place to keep only current keys
    filtered_states = {
        key: value
        for key, value in _pr_state_times.items()
        if key in current_keys
    }
    _pr_state_times.clear()
    _pr_state_times.update(filtered_states)


def display_status_summary(all_prs: List[Dict[str, Any]], pr_phases: List[str], repos_with_prs: List[Dict[str, Any]]) -> None:
    """Display a concise summary of current PR status
    
    This summary helps users understand the overall status at a glance,
    especially useful on terminals with limited display lines.
    Uses the same format as process_pr() for consistency.
    
    Args:
        all_prs: List of all PRs
        pr_phases: List of phase strings corresponding to all_prs
        repos_with_prs: List of repositories with open PRs
    """
    print(f"\n{'=' * 50}")
    print("Status Summary:")
    print(f"{'=' * 50}")

    if not all_prs:
        print("  No open PRs to monitor")
        cleanup_old_pr_states([])
        return

    current_time = time.time()
    current_states = []

    # Display each PR using the same format as process_pr()
    for pr, phase in zip(all_prs, pr_phases):
        repo_info = pr.get("repository", {})
        repo_name = repo_info.get("name", "Unknown")
        repo_owner = repo_info.get("owner", "Unknown")
        title = pr.get("title", "Unknown")
        url = pr.get("url", "")

        # Track state for elapsed time
        state_key = (url, phase)
        current_states.append(state_key)
        if state_key not in _pr_state_times:
            _pr_state_times[state_key] = current_time

        # Calculate elapsed time
        elapsed = current_time - _pr_state_times[state_key]

        # Display phase with colors using the same format
        phase_display = colorize_phase(phase)

        # Show elapsed time if state has persisted for more than 60 seconds
        if elapsed >= 60:
            elapsed_str = format_elapsed_time(elapsed)
            print(f"  [{repo_owner}/{repo_name}] {phase_display} {title} (現在、検知してから{elapsed_str}経過)")
        else:
            print(f"  [{repo_owner}/{repo_name}] {phase_display} {title}")

    # Clean up old PR states that are no longer present
    cleanup_old_pr_states(current_states)


def check_no_state_change_timeout(
    all_prs: List[Dict[str, Any]],
    pr_phases: List[str],
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """Check if the overall PR state has not changed for too long and switch to reduced frequency mode
    
    This tracks when ANY change happens in the PR state (phase changes, PRs added/removed).
    Timer starts when the state first becomes stable and resets on any state change.
    When timeout is reached, monitoring switches to reduced frequency mode (using the configured reduced_frequency_interval).
    When changes are detected, monitoring returns to normal frequency mode.
    
    Args:
        all_prs: List of all PRs
        pr_phases: List of phase strings corresponding to all_prs
        config: Configuration dictionary (optional)
        
    Returns:
        True if monitoring should switch to reduced frequency mode, False otherwise
    """
    global _last_state, _reduced_frequency_mode

    # Get timeout setting from config with default of "30m"
    timeout_str = (config or {}).get("no_change_timeout", "30m")
    
    # Get reduced frequency interval setting from config with default of "1h"
    reduced_interval_str = (config or {}).get("reduced_frequency_interval", "1h")

    # If timeout is explicitly set to empty string (disabled), don't check
    if not timeout_str:
        _last_state = None
        _reduced_frequency_mode = False
        return False

    # Parse timeout to seconds
    try:
        timeout_seconds = parse_interval(timeout_str)
    except ValueError as e:
        print(f"Warning: Invalid no_change_timeout format: {e}")
        _last_state = None
        _reduced_frequency_mode = False
        return False

    current_time = time.time()

    # Create a snapshot of current state
    # Validate that all_prs and pr_phases have the same length
    if all_prs and pr_phases and len(all_prs) == len(pr_phases):
        # Create frozenset of (url, phase) tuples to represent current state
        current_state = frozenset(
            (pr.get("url", ""), phase)
            for pr, phase in zip(all_prs, pr_phases)
        )
    else:
        # Invalid or empty state
        current_state = frozenset()

    # Check if state has changed
    if _last_state is None:
        # First check - initialize the state
        _last_state = (current_state, current_time)
        _reduced_frequency_mode = False
    elif _last_state[0] != current_state:
        # State has changed - reset timer and return to normal mode
        _last_state = (current_state, current_time)
        if _reduced_frequency_mode:
            # Switching back to normal monitoring
            print(f"\n{'=' * 50}")
            print("PRの状態に変化を検知しました。")
            print("通常の監視間隔に戻ります。")
            print(f"{'=' * 50}")
        _reduced_frequency_mode = False
    else:
        # State is unchanged - check if timeout has been reached
        state_start_time = _last_state[1]
        elapsed = current_time - state_start_time
        if elapsed >= timeout_seconds and not _reduced_frequency_mode:
            # Timeout reached - switch to reduced frequency mode
            elapsed_str = format_elapsed_time(elapsed)
            print(f"\n{'=' * 50}")
            print(f"PRの状態に変化がない状態が{timeout_str}（{elapsed_str}）続きました。")
            print(f"API利用の浪費を防止するため、監視間隔を{reduced_interval_str}に変更します。")
            print("変化があったら元の監視間隔に戻ります。")
            print(f"{'=' * 50}")
            _reduced_frequency_mode = True
    
    return _reduced_frequency_mode


def _resolve_assign_to_copilot_config(issue: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve assign_to_copilot configuration for a specific issue's repository
    
    Args:
        issue: Issue dictionary with repository information
        config: Global configuration dictionary
        
    Returns:
        Configuration dictionary with assign_to_copilot settings if enabled for this repo
    """
    # Get repository-specific configuration
    repo_info = issue.get("repository", {})
    repo_owner = repo_info.get("owner", "")
    repo_name = repo_info.get("name", "")
    
    if repo_owner and repo_name:
        exec_config = resolve_execution_config_for_repo(config, repo_owner, repo_name)
        # Check if assign_to_copilot is enabled for this repo
        enable_assign_flag = exec_config.get("enable_assign_to_copilot")
        if enable_assign_flag is None:
            # Not set by rulesets, use global config for backward compatibility
            return config
        elif enable_assign_flag:
            # Enabled for this repo, use global assign_to_copilot settings
            return {"assign_to_copilot": config.get("assign_to_copilot", {})}
        else:
            # Disabled for this repo
            return {"assign_to_copilot": {"enabled": False}}
    else:
        return config


def display_issues_from_repos_without_prs(config: Optional[Dict[str, Any]] = None):
    """Display issues from repositories with no open PRs

    Args:
        config: Configuration dictionary (optional)
    """
    print("Checking for repositories with no open PRs but with open issues...")

    try:
        repos_with_issues = get_repositories_with_no_prs_and_open_issues()

        if not repos_with_issues:
            print("  No repositories found with open issues and no open PRs")
        else:
            print(f"  Found {len(repos_with_issues)} repositories with open issues (no open PRs):")
            for repo in repos_with_issues:
                print(f"    - {repo['owner']}/{repo['name']}: {repo['openIssueCount']} open issue(s)")

            # Check if auto-assign feature is enabled in config
            # We need to check per repository since it can be configured per ruleset
            # For the global check, we use the global config settings
            assign_enabled = False
            assign_lowest_number = False
            if config:
                assign_config = config.get("assign_to_copilot", {})
                assign_enabled = assign_config.get("enabled", False)
                assign_lowest_number = assign_config.get("assign_lowest_number_issue", False)

            # Only try to auto-assign if the feature is enabled
            if assign_enabled:
                # Check which mode to use: lowest number or good first issue
                if assign_lowest_number:
                    # Fetch and auto-assign the issue with the lowest number
                    print(f"\n{'=' * 50}")
                    print("Checking for the issue with the lowest number to auto-assign to Copilot...")
                    print(f"{'=' * 50}")

                    lowest_number_issues = get_issues_from_repositories(
                        repos_with_issues, limit=1, sort_by_number=True
                    )

                    if lowest_number_issues:
                        issue = lowest_number_issues[0]
                        print("\n  Found issue with lowest number:")
                        print(f"  #{issue['number']}: {issue['title']}")
                        print(f"     URL: {issue['url']}")
                        # Safely join labels, ensuring they are all strings
                        labels = issue.get('labels', [])
                        label_str = ', '.join(str(label) for label in labels)
                        print(f"     Labels: {label_str}")
                        print("\n  Attempting to assign to Copilot...")

                        # Get repository-specific configuration
                        temp_config = _resolve_assign_to_copilot_config(issue, config)
                        
                        # Assign the issue to Copilot and check the result
                        success = assign_issue_to_copilot(issue, temp_config)
                        if not success:
                            print("  Assignment failed - will retry on next iteration")
                    else:
                        print("  No issues found in repositories without open PRs")
                else:
                    # Original behavior: try to fetch and auto-assign "good first issue" issues
                    print(f"\n{'=' * 50}")
                    print("Checking for 'good first issue' issues to auto-assign to Copilot...")
                    print(f"{'=' * 50}")

                    good_first_issues = get_issues_from_repositories(
                        repos_with_issues, limit=1, labels=["good first issue"]
                    )

                    if good_first_issues:
                        issue = good_first_issues[0]
                        print("\n  Found top 'good first issue' (sorted by last update, descending):")
                        print(f"  #{issue['number']}: {issue['title']}")
                        print(f"     URL: {issue['url']}")
                        # Safely join labels, ensuring they are all strings
                        labels = issue.get('labels', [])
                        label_str = ', '.join(str(label) for label in labels)
                        print(f"     Labels: {label_str}")
                        print("\n  Attempting to assign to Copilot...")

                        # Get repository-specific configuration
                        temp_config = _resolve_assign_to_copilot_config(issue, config)
                        
                        # Assign the issue to Copilot and check the result
                        success = assign_issue_to_copilot(issue, temp_config)
                        if not success:
                            print("  Assignment failed - will retry on next iteration")
                    else:
                        print("  No 'good first issue' issues found in repositories without open PRs")
            else:
                print(f"\n{'=' * 50}")
                print("Auto-assign to Copilot feature is disabled")
                print("To enable, set 'assign_to_copilot.enabled = true' in config.toml")
                print(f"{'=' * 50}")

            # Get the issue display limit from config (default: 10)
            issue_limit = config.get("issue_display_limit", 10) if config else 10

            # Then, show top N issues from these repositories
            print(f"\n{'=' * 50}")
            print(f"Fetching top {issue_limit} issues from these repositories...")
            print(f"{'=' * 50}")

            top_issues = get_issues_from_repositories(repos_with_issues, limit=issue_limit)

            if not top_issues:
                print("  No issues found")
            else:
                print(f"\n  Top {len(top_issues)} issues (sorted by last update, descending):\n")
                for idx, issue in enumerate(top_issues, 1):
                    print(f"  {idx}. #{issue['number']}: {issue['title']}")
                    print(f"     URL: {issue['url']}")
                    print()
    except Exception as e:
        print(f"  Error fetching issues: {e}")
        traceback.print_exc()


def main():
    """Main execution function"""
    config_path = "config.toml"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    # Load config if it exists, otherwise use defaults
    config = {}
    config_mtime = 0.0
    try:
        config = load_config(config_path)
        config_mtime = get_config_mtime(config_path)
    except FileNotFoundError:
        print(f"Warning: Config file '{config_path}' not found, using defaults")
        print("You can create a config.toml file to customize settings")
        print("Expected format:")
        print('interval = "1m"  # Check interval (e.g., "30s", "1m", "5m")')
        print()

    # Get interval setting (default to 1 minute if not specified)
    interval_str = config.get("interval", "1m")
    try:
        interval_seconds = parse_interval(interval_str)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("GitHub PR Phase Monitor")
    print("=" * 50)
    print(f"Monitoring interval: {interval_str} ({interval_seconds} seconds)")
    print("Monitoring all repositories for the current GitHub user")
    print("Press CTRL+C to stop monitoring")
    print("=" * 50)

    # Print configuration if verbose mode is enabled
    if config.get("verbose", False):
        print_config(config)

    # Set up signal handler for graceful interruption
    def signal_handler(_signum, _frame):
        print("\n\nMonitoring interrupted by user (CTRL+C)")
        print("Exiting...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Infinite monitoring loop
    iteration = 0
    consecutive_failures = 0
    while True:
        iteration += 1
        print(f"\n{'=' * 50}")
        print(f"Check #{iteration} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 50}")

        # Initialize variables to track status for summary
        all_prs = []
        pr_phases = []
        repos_with_prs = []

        try:
            # Phase 1: Get all repositories with open PRs (lightweight query)
            print("\nPhase 1: Fetching repositories with open PRs...")
            repos_with_prs = get_repositories_with_open_prs()

            if not repos_with_prs:
                print("  No repositories with open PRs found")
                # Display issues when no repositories with open PRs are found
                display_issues_from_repos_without_prs(config)
            else:
                print(f"  Found {len(repos_with_prs)} repositories with open PRs:")
                for repo in repos_with_prs:
                    print(f"    - {repo['owner']}/{repo['name']}: {repo['openPRCount']} open PR(s)")

                # Phase 2: Get PR details for repositories with open PRs (detailed query)
                print(f"\nPhase 2: Fetching PR details for {len(repos_with_prs)} repositories...")
                all_prs = get_pr_details_batch(repos_with_prs)

                if not all_prs:
                    print("  No PRs found")
                else:
                    print(f"\n  Found {len(all_prs)} open PR(s) total")
                    print(f"\n{'=' * 50}")
                    print("Processing PRs:")
                    print(f"{'=' * 50}")

                    # Track phases to detect if all PRs are in "LLM working"
                    for pr in all_prs:
                        phase = determine_phase(pr)
                        pr_phases.append(phase)
                        process_pr(pr, config, phase)

                    # Check if all PRs are in "LLM working" phase
                    if pr_phases and all(phase == PHASE_LLM_WORKING for phase in pr_phases):
                        print(f"\n{'=' * 50}")
                        print("All PRs are in 'LLM working' phase")
                        print(f"{'=' * 50}")
                        # Display issues when all PRs are in "LLM working" phase
                        display_issues_from_repos_without_prs(config)

            # Reset consecutive-failure counter on a successful iteration
            consecutive_failures = 0

        except RuntimeError as e:
            print(f"\nError: {e}")
            print("Please ensure you are authenticated with gh CLI")
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            traceback.print_exc()

            # Track consecutive unexpected failures to avoid infinite error loops
            consecutive_failures += 1

            if consecutive_failures >= 3:
                print("\nEncountered 3 consecutive unexpected errors; exiting to avoid an infinite error loop.")
                sys.exit(1)

        # Display status summary before waiting
        # This helps users understand the current state at a glance,
        # especially on terminals with limited display lines.
        # Note: If an error occurred during data collection, the summary will show
        # incomplete or empty data, which is acceptable as it reflects the actual
        # state that was successfully retrieved before the error.
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Check if PR state has not changed for too long and switch to reduced frequency mode
        use_reduced_frequency = check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Determine which interval to use
        if use_reduced_frequency:
            # Use reduced frequency interval (default: 1h)
            reduced_interval_str = (config or {}).get("reduced_frequency_interval", "1h")
            try:
                reduced_interval_seconds = parse_interval(reduced_interval_str)
                current_interval_seconds = reduced_interval_seconds
                current_interval_str = reduced_interval_str
            except ValueError as e:
                print(f"Error: Invalid reduced_frequency_interval format: {e}")
                sys.exit(1)
        else:
            # Use normal interval
            current_interval_seconds = interval_seconds
            current_interval_str = interval_str

        # Wait with countdown display and check for config changes
        new_config, new_interval_seconds, new_interval_str, new_config_mtime = wait_with_countdown(
            current_interval_seconds, current_interval_str, config_path, config_mtime
        )

        # Update config and interval based on what was returned from wait
        # Config will be non-empty only if successfully reloaded during wait
        config_reloaded = new_config_mtime != config_mtime
        if config_reloaded and new_config:
            config = new_config
        # Always update interval and mtime as they may have changed during reload
        interval_seconds = new_interval_seconds
        interval_str = new_interval_str
        config_mtime = new_config_mtime


if __name__ == "__main__":
    main()
