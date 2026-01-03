"""
Main execution module for GitHub PR Phase Monitor
"""

import signal
import sys
import time
import traceback

from .config import load_config, parse_interval
from .github_client import (
    get_issues_from_repositories,
    get_pr_details_batch,
    get_repositories_with_no_prs_and_open_issues,
    get_repositories_with_open_prs,
)
from .phase_detector import PHASE_LLM_WORKING, determine_phase
from .pr_actions import process_pr


def main():
    """Main execution function"""
    config_path = "config.toml"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    # Load config if it exists, otherwise use defaults
    config = {}
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        print(f"Warning: Config file '{config_path}' not found, using defaults")
        print("You can create a config.toml file to customize settings")
        print("Expected format:")
        print('interval = "1m"  # Check interval (e.g., "30s", "1m", "5m")')
        print(
            'phase3_comment_message = "🎁レビューお願いします🎁 : Copilot has finished applying the changes. Please review the updates."'
        )
        print()

    # Validate required phase3_comment_message field
    if "phase3_comment_message" not in config:
        print("Error: 'phase3_comment_message' is required in config file")
        print("\nExpected format:")
        print(
            'phase3_comment_message = "🎁レビューお願いします🎁 : Copilot has finished applying the changes. Please review the updates."'
        )
        sys.exit(1)

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

        try:
            # Phase 1: Get all repositories with open PRs (lightweight query)
            print("\nPhase 1: Fetching repositories with open PRs...")
            repos_with_prs = get_repositories_with_open_prs()

            if not repos_with_prs:
                print("  No repositories with open PRs found")
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
                    pr_phases = []
                    for pr in all_prs:
                        phase = determine_phase(pr)
                        pr_phases.append(phase)
                        process_pr(pr, config, phase)

                    # Check if all PRs are in "LLM working" phase
                    if pr_phases and all(phase == PHASE_LLM_WORKING for phase in pr_phases):
                        print(f"\n{'=' * 50}")
                        print("All PRs are in 'LLM working' phase")
                        print("Checking for repositories with no open PRs but with open issues...")
                        print(f"{'=' * 50}")

                        try:
                            repos_with_issues = get_repositories_with_no_prs_and_open_issues()

                            if not repos_with_issues:
                                print("  No repositories found with open issues and no open PRs")
                            else:
                                print(f"  Found {len(repos_with_issues)} repositories with open issues (no open PRs):")
                                for repo in repos_with_issues:
                                    print(f"    - {repo['owner']}/{repo['name']}: {repo['openIssueCount']} open issue(s)")

                                print(f"\n{'=' * 50}")
                                print("Fetching top 10 issues from these repositories...")
                                print(f"{'=' * 50}")

                                top_issues = get_issues_from_repositories(repos_with_issues, limit=10)

                                if not top_issues:
                                    print("  No issues found")
                                else:
                                    print(f"\n  Top {len(top_issues)} issues (sorted by last update, descending):\n")
                                    for idx, issue in enumerate(top_issues, 1):
                                        repo_info = issue["repository"]
                                        print(f"  {idx}. [{repo_info['owner']}/{repo_info['name']}] #{issue['number']}: {issue['title']}")
                                        print(f"     URL: {issue['url']}")
                                        print(f"     Author: {issue['author']['login']}")
                                        print(f"     Updated: {issue['updatedAt']}")
                                        print()
                        except Exception as e:
                            print(f"  Error fetching issues: {e}")
                            traceback.print_exc()

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

        print(f"\n{'=' * 50}")
        print(f"Waiting {interval_str} until next check...")
        print(f"{'=' * 50}")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
