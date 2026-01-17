"""
Main execution module for GitHub PR Phase Monitor
"""

import signal
import sys
import time
import traceback

from .config import (
    get_config_mtime,
    load_config,
    parse_interval,
    print_config,
    validate_phase3_merge_config_required,
)
from .display import display_issues_from_repos_without_prs, display_status_summary
from .github_client import get_pr_details_batch, get_repositories_with_open_prs
from .monitor import check_no_state_change_timeout
from .phase_detector import PHASE_LLM_WORKING, determine_phase
from .pr_actions import process_pr
from .wait_handler import wait_with_countdown


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
    # Keep the normal interval separate from the current interval to prevent the normal
    # interval from being overwritten by reduced frequency interval values during mode switches
    normal_interval_str = config.get("interval", "1m")
    try:
        normal_interval_seconds = parse_interval(normal_interval_str)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("GitHub PR Phase Monitor")
    print("=" * 50)
    print(f"Monitoring interval: {normal_interval_str} ({normal_interval_seconds} seconds)")
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
                # No PRs means llm_working_count = 0
                display_issues_from_repos_without_prs(config, llm_working_count=0)
            else:
                print(f"  Found {len(repos_with_prs)} repositories with open PRs:")
                for repo in repos_with_prs:
                    print(f"    - {repo['name']}: {repo['openPRCount']} open PR(s)")

                # Validate phase3_merge configuration for all repositories
                # This must be done before processing PRs to fail fast
                print("\nValidating phase3_merge configuration...")
                for repo in repos_with_prs:
                    repo_owner = repo.get("owner", "")
                    repo_name = repo.get("name", "")
                    if repo_owner and repo_name:
                        validate_phase3_merge_config_required(config, repo_owner, repo_name)

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

                    # Count how many PRs are in "LLM working" phase
                    # This count is used for rate limit protection - when too many PRs are being
                    # worked on simultaneously, we pause auto-assignment to prevent API rate limits
                    llm_working_count = sum(1 for phase in pr_phases if phase == PHASE_LLM_WORKING)

                    # Look for new issues to assign only when all PRs are in "LLM working" phase
                    # This means all existing work is in progress (not waiting for review or action)
                    # The llm_working_count throttles assignment when parallel work is too high
                    if pr_phases and all(phase == PHASE_LLM_WORKING for phase in pr_phases):
                        print(f"\n{'=' * 50}")
                        print("All PRs are in 'LLM working' phase")
                        print(f"{'=' * 50}")
                        # Display issues and potentially auto-assign new work
                        # Throttling is applied inside the function based on llm_working_count
                        display_issues_from_repos_without_prs(config, llm_working_count=llm_working_count)

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
            # Use normal interval (preserved separately to avoid contamination)
            current_interval_seconds = normal_interval_seconds
            current_interval_str = normal_interval_str

        # Wait with countdown display and check for config changes
        new_config, new_interval_seconds, new_interval_str, new_config_mtime = wait_with_countdown(
            current_interval_seconds, current_interval_str, config_path, config_mtime
        )

        # Update config and interval based on what was returned from wait
        # Config will be non-empty only if successfully reloaded during wait
        config_reloaded = new_config_mtime != config_mtime
        if config_reloaded and new_config:
            config = new_config
            # Update normal interval only on hot reload (config change).
            # This prevents the normal interval from being contaminated by reduced frequency
            # interval values that may be returned from wait_with_countdown().
            normal_interval_seconds = new_interval_seconds
            normal_interval_str = new_interval_str
        # Always update mtime
        config_mtime = new_config_mtime


if __name__ == "__main__":
    main()
