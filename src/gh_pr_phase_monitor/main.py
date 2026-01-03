"""
Main execution module for GitHub PR Phase Monitor
"""

import signal
import sys
import time
import traceback

from .config import load_config, parse_interval
from .github_client import get_pr_details_batch, get_repositories_with_open_prs
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

                    for pr in all_prs:
                        process_pr(pr, config)

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
