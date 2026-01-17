"""
Display and UI functions for status summary and issues
"""

import time
import traceback
from typing import Any, Dict, List, Optional

from .colors import colorize_phase
from .config import (
    DEFAULT_MAX_LLM_WORKING_PARALLEL,
    get_assign_to_copilot_config,
    resolve_execution_config_for_repo,
)
from .github_client import (
    assign_issue_to_copilot,
    get_issues_from_repositories,
    get_repositories_with_no_prs_and_open_issues,
)
from .state_tracker import cleanup_old_pr_states, get_pr_state_time, set_pr_state_time
from .time_utils import format_elapsed_time


def display_status_summary(
    all_prs: List[Dict[str, Any]], pr_phases: List[str], repos_with_prs: List[Dict[str, Any]]
) -> None:
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
        title = pr.get("title", "Unknown")
        url = pr.get("url", "")

        # Track state for elapsed time
        state_key = (url, phase)
        current_states.append(state_key)
        if get_pr_state_time(url, phase) is None:
            set_pr_state_time(url, phase, current_time)

        # Calculate elapsed time
        elapsed = current_time - get_pr_state_time(url, phase)

        # Display phase with colors using the same format
        phase_display = colorize_phase(phase)

        # Show elapsed time if state has persisted for more than 60 seconds
        if elapsed >= 60:
            elapsed_str = format_elapsed_time(elapsed)
            print(f"  [{repo_name}] {phase_display} {title} (現在、検知してから{elapsed_str}経過)")
        else:
            print(f"  [{repo_name}] {phase_display} {title}")

    # Clean up old PR states that are no longer present
    cleanup_old_pr_states(current_states)


def _resolve_assign_to_copilot_config(issue: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve assign_to_copilot configuration for a specific issue's repository

    Args:
        issue: Issue dictionary with repository information
        config: Global configuration dictionary (can be None)

    Returns:
        Configuration dictionary with assign_to_copilot settings
    """
    # Handle None config
    if config is None:
        return {"assign_to_copilot": {}}

    # Get repository-specific configuration
    repo_info = issue.get("repository", {})
    repo_owner = repo_info.get("owner", "")
    repo_name = repo_info.get("name", "")

    if repo_owner and repo_name:
        exec_config = resolve_execution_config_for_repo(config, repo_owner, repo_name)
        # Check if any assignment flag is enabled for this repo
        if exec_config.get("assign_good_first_old", False) or exec_config.get("assign_old", False):
            # Assignment enabled for this repo, use global assign_to_copilot settings with defaults
            return {"assign_to_copilot": get_assign_to_copilot_config(config)}
        else:
            # No assignment flags enabled
            return {"assign_to_copilot": {}}
    else:
        return {"assign_to_copilot": {}}


def display_issues_from_repos_without_prs(config: Optional[Dict[str, Any]] = None, llm_working_count: int = 0):
    """Display issues from repositories with no open PRs

    Args:
        config: Configuration dictionary (optional)
        llm_working_count: Number of PRs currently in "LLM working" state (default: 0)
    """
    print("Checking for repositories with no open PRs but with open issues...")

    try:
        repos_with_issues = get_repositories_with_no_prs_and_open_issues()

        if not repos_with_issues:
            print("  No repositories found with open issues and no open PRs")
        else:
            print(f"  Found {len(repos_with_issues)} repositories with open issues (no open PRs):")
            for repo in repos_with_issues:
                print(f"    - {repo['name']}: {repo['openIssueCount']} open issue(s)")

            # Check if auto-assign feature is enabled in config
            # With the new design:
            # - Rulesets can specify "assign_good_first_old" to assign one old "good first issue" (oldest by issue number)
            # - Rulesets can specify "assign_old" to assign one old issue (oldest by issue number, any issue)
            # - Both default to false
            # - When both are true, prioritize "good first issue"

            # Check if any repository has auto-assign enabled
            # We need to check all repos to determine which mode to use
            # Also filter repos to only those with assignment properly enabled
            any_good_first = False
            any_old = False
            repos_with_good_first_enabled = []
            repos_with_old_enabled = []

            # Only check for assign flags if config is not None
            if config:
                for repo in repos_with_issues:
                    repo_owner = repo.get("owner", "")
                    repo_name = repo.get("name", "")
                    if repo_owner and repo_name:
                        exec_config = resolve_execution_config_for_repo(config, repo_owner, repo_name)
                        # Check if any assignment flag is enabled
                        if exec_config.get("assign_good_first_old", False):
                            any_good_first = True
                            repos_with_good_first_enabled.append(repo)
                        if exec_config.get("assign_old", False):
                            any_old = True
                            repos_with_old_enabled.append(repo)

            # Check if we should pause auto-assignment due to too many LLM working PRs
            # Get max_llm_working_parallel setting from config (default: 3)
            max_llm_working = DEFAULT_MAX_LLM_WORKING_PARALLEL
            if config:
                max_llm_working = config.get("max_llm_working_parallel", DEFAULT_MAX_LLM_WORKING_PARALLEL)

            # Check if we should pause auto-assignment
            should_pause_assignment = llm_working_count >= max_llm_working

            if should_pause_assignment:
                print(f"\n{'=' * 50}")
                print(f"LLM workingのPR数が最大並列数（{max_llm_working}）に達しています。")
                print(f"現在のLLM working PR数: {llm_working_count}")
                print("レートリミット回避のため、新しいissueの自動assignを保留します。")
                print(f"{'=' * 50}")
                # Skip assignment but continue to display issues
            else:
                # Always try to check for issues to assign (batteries-included)
                # Individual repositories must explicitly enable via rulesets for actual assignment
                # Priority: good first issue > old issue (both sorted by issue number ascending)
                if any_good_first:
                    # Fetch and auto-assign the oldest "good first issue" (oldest by issue number)
                    # Only from repos with assign_good_first_old enabled
                    print(f"\n{'=' * 50}")
                    print("Checking for the oldest 'good first issue' to auto-assign to Copilot...")
                    print(f"{'=' * 50}")

                    good_first_issues = get_issues_from_repositories(
                        repos_with_good_first_enabled, limit=1, labels=["good first issue"], sort_by_number=True
                    )

                    if good_first_issues:
                        issue = good_first_issues[0]
                        print("\n  Found oldest 'good first issue' (sorted by issue number, ascending):")
                        print(f"  #{issue['number']}: {issue['title']}")
                        print(f"     URL: {issue['url']}")
                        # Safely join labels, ensuring they are all strings
                        labels = issue.get("labels", [])
                        label_str = ", ".join(str(label) for label in labels)
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
                elif any_old:
                    # Fetch and auto-assign the oldest issue (any issue)
                    # Only from repos with assign_old enabled
                    print(f"\n{'=' * 50}")
                    print("Checking for the oldest issue to auto-assign to Copilot...")
                    print(f"{'=' * 50}")

                    oldest_issues = get_issues_from_repositories(repos_with_old_enabled, limit=1, sort_by_number=True)

                    if oldest_issues:
                        issue = oldest_issues[0]
                        print("\n  Found oldest issue (sorted by issue number, ascending):")
                        print(f"  #{issue['number']}: {issue['title']}")
                        print(f"     URL: {issue['url']}")
                        # Safely join labels, ensuring they are all strings
                        labels = issue.get("labels", [])
                        label_str = ", ".join(str(label) for label in labels)
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
