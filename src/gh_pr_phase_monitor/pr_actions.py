"""
PR actions such as marking ready and opening browser
"""

import subprocess
import webbrowser
from pathlib import Path
from typing import Any, Dict, Set, Tuple

from .browser_automation import merge_pr_automated
from .colors import colorize_phase
from .comment_manager import (
    post_phase2_comment,
    post_phase3_comment,
)
from .config import resolve_execution_config_for_repo, print_repo_execution_config
from .notifier import send_phase3_notification
from .phase_detector import PHASE_1, PHASE_2, PHASE_3, determine_phase

# Track which PRs have had their browser opened: set of (url, phase) tuples
_browser_opened: Set[Tuple[str, str]] = set()

# Track which PRs have had notifications sent: set of (url, phase) tuples
_notifications_sent: Set[Tuple[str, str]] = set()

# Track which PRs have been merged: set of PR URLs
_merged_prs: Set[str] = set()


def mark_pr_ready(pr_url: str, repo_dir: Path = None) -> bool:
    """Mark a draft PR as ready for review using gh command

    Args:
        pr_url: URL of the PR
        repo_dir: Repository directory (optional, not used when working with URLs)

    Returns:
        True if PR was successfully marked as ready, False otherwise
    """
    cmd = ["gh", "pr", "ready", pr_url]

    try:
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error marking PR as ready: {e}")
        stderr = getattr(e, "stderr", "No stderr available")
        print(f"    stderr: {stderr}")
        return False


def merge_pr(pr_url: str, repo_dir: Path = None) -> bool:
    """Merge a PR using gh command

    Args:
        pr_url: URL of the PR
        repo_dir: Repository directory (optional, not used when working with URLs)

    Returns:
        True if PR was successfully merged, False otherwise

    Note:
        Uses --squash for a clean commit history and --delete-branch to
        automatically delete the feature branch after merge. Does not use --auto flag
        because phase3 detection already implies all required checks have passed.
    """
    cmd = ["gh", "pr", "merge", pr_url, "--squash", "--delete-branch"]

    try:
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error merging PR: {e}")
        stderr = getattr(e, "stderr", "No stderr available")
        print(f"    stderr: {stderr}")
        return False


def open_browser(url: str) -> None:
    """Open URL in browser

    Args:
        url: URL to open in browser
    """
    webbrowser.open(url)


def process_pr(pr: Dict[str, Any], config: Dict[str, Any] = None, phase: str = None) -> None:
    """Process a single PR

    Args:
        pr: PR data dictionary (with repository info)
        config: Configuration dictionary (optional)
        phase: Pre-computed phase (optional, will be computed if not provided)
    """
    repo_info = pr.get("repository", {})
    repo_name = repo_info.get("name", "Unknown")
    repo_owner = repo_info.get("owner", "Unknown")
    title = pr.get("title", "Unknown")
    url = pr.get("url", "")

    # Use pre-computed phase if provided, otherwise compute it
    if phase is None:
        phase = determine_phase(pr)

    # Display phase with colors
    phase_display = colorize_phase(phase)
    print(f"  [{repo_owner}/{repo_name}] {phase_display} {title}")
    print(f"    URL: {url}")

    # Resolve execution config for this repository
    if config:
        exec_config = resolve_execution_config_for_repo(config, repo_owner, repo_name)
        
        # Print execution config if verbose mode is enabled
        if config.get("verbose", False):
            print_repo_execution_config(repo_owner, repo_name, exec_config)
    else:
        exec_config = {
            "enable_execution_phase1_to_phase2": False,
            "enable_execution_phase2_to_phase3": False,
            "enable_execution_phase3_send_ntfy": False,
            "enable_execution_phase3_to_merge": False,
            "enable_phase3_merge": None,
            "enable_assign_to_copilot": None,
        }

    # Mark PR as ready for review when in phase 1
    if phase == PHASE_1:
        # Check if execution is enabled
        execution_enabled = exec_config["enable_execution_phase1_to_phase2"]
        if execution_enabled:
            print("    Marking PR as ready for review...")
            if mark_pr_ready(url, None):
                print("    PR marked as ready successfully")
            else:
                print("    Failed to mark PR as ready")
        else:
            print("    [DRY-RUN] Would mark PR as ready for review (enable_execution_phase1_to_phase2=false)")

    # Post comment when in phase 2
    if phase == PHASE_2:
        # Check if execution is enabled
        execution_enabled = exec_config["enable_execution_phase2_to_phase3"]
        if execution_enabled:
            print("    Posting comment for phase2...")
            result = post_phase2_comment(pr, None)
            if result is True:
                print("    Comment posted successfully")
            elif result is False:
                print("    Failed to post comment")
            # If result is None, post_phase2_comment already printed "Comment already exists, skipping"
            # (see implementation in comment_manager.py)
        else:
            print("    [DRY-RUN] Would post comment for phase2 (enable_execution_phase2_to_phase3=false)")

    # Open browser and send notification when in phase 3
    if phase == PHASE_3:
        # Check if browser was already opened for this PR in this phase
        browser_key = (url, phase)
        if browser_key not in _browser_opened:
            print("    Opening browser...")
            open_browser(url)
            _browser_opened.add(browser_key)
        else:
            print("    Browser already opened for this PR, skipping")

        # Send notification if configured and not already attempted
        # Note: Notifications are tracked per (url, phase) tuple, meaning if a PR
        # transitions from phase3 to another phase and back to phase3, a new
        # notification will NOT be sent. This prevents duplicate notifications for
        # the same phase of the same PR across monitoring iterations.
        notification_key = (url, phase)

        # Check if ntfy execution is enabled
        execution_enabled = exec_config["enable_execution_phase3_send_ntfy"]
        ntfy_configured = config and config.get("ntfy", {}).get("enabled", False)

        # Only track notifications when execution is enabled (not in dry-run mode)
        if ntfy_configured and execution_enabled:
            if notification_key not in _notifications_sent:
                # Mark as attempted to avoid repeated sends
                _notifications_sent.add(notification_key)
                print("    Sending ntfy notification...")
                if send_phase3_notification(config, url, title):
                    print("    Notification sent successfully")
                else:
                    print("    Failed to send notification")
        elif ntfy_configured and not execution_enabled:
            print("    [DRY-RUN] Would send ntfy notification (enable_execution_phase3_send_ntfy=false)")

        # Merge PR if configured and not already merged
        merge_key = url
        merge_execution_enabled = exec_config["enable_execution_phase3_to_merge"]
        # Use global phase3_merge configuration
        phase3_merge_config = config.get("phase3_merge", {}) if config else {}
        # Check if phase3_merge is enabled:
        # - If enable_phase3_merge is None (not set by rulesets), use global phase3_merge.enabled for backward compatibility
        # - If enable_phase3_merge is explicitly True/False from rulesets, respect that
        enable_phase3_merge_flag = exec_config.get("enable_phase3_merge")
        if enable_phase3_merge_flag is None:
            # No ruleset override, use global setting for backward compatibility
            merge_configured = phase3_merge_config.get("enabled", False)
        elif enable_phase3_merge_flag:
            # Ruleset enables it, check global enabled flag too
            merge_configured = phase3_merge_config.get("enabled", False)
        else:
            # Ruleset explicitly disables it
            merge_configured = False

        if merge_configured and merge_execution_enabled:
            if merge_key not in _merged_prs:
                # Post comment before merging
                merge_comment = phase3_merge_config.get("comment", "All checks passed. Merging PR.")
                print(f"    Posting pre-merge comment: '{merge_comment}'...")
                comment_posted = post_phase3_comment(pr, merge_comment, None)

                if not comment_posted:
                    print("    Failed to post pre-merge comment")
                    print("    Skipping merge because pre-merge comment could not be posted")
                    return  # Early return - do not add to merged_prs, allow retry

                print("    Pre-merge comment posted successfully")

                # Check if automated merge is enabled
                merge_automated = phase3_merge_config.get("automated", False)

                merge_success = False
                if merge_automated:
                    print("    Merging PR using browser automation...")
                    # Create a temporary config dict with the global phase3_merge settings
                    temp_config = {"phase3_merge": phase3_merge_config}
                    if merge_pr_automated(url, temp_config):
                        print("    PR merged successfully via browser automation")
                        merge_success = True
                    else:
                        print("    Failed to merge PR via browser automation")
                else:
                    print("    Merging PR using gh CLI...")
                    if merge_pr(url, None):
                        print("    PR merged successfully via gh CLI")
                        merge_success = True
                    else:
                        print("    Failed to merge PR via gh CLI")

                # Only mark as merged if the merge was successful
                if merge_success:
                    _merged_prs.add(merge_key)
        elif merge_configured and not merge_execution_enabled:
            print("    [DRY-RUN] Would merge PR (enable_execution_phase3_to_merge=false)")


def process_repository(repo_dir: Path, config: Dict[str, Any] = None) -> None:
    """Process a single repository (Legacy function - kept for compatibility)

    Args:
        repo_dir: Repository directory
        config: Configuration dictionary (optional)
    """
    from .github_client import get_pr_data

    print(f"\n=== Processing: {repo_dir} ===")

    try:
        pr_list = get_pr_data(repo_dir)

        if not pr_list:
            print("  No open PRs found")
            return

        for pr in pr_list:
            # Add repository info to PR for compatibility with process_pr
            # Legacy get_pr_data doesn't include repository info
            pr["repository"] = {"name": str(repo_dir.name), "owner": "Unknown"}
            # Delegate per-PR processing to the shared helper to avoid duplication
            process_pr(pr, config)

    except subprocess.CalledProcessError as e:
        print(f"  Error running gh command: {e}")
        print(f"  stderr: {e.stderr}")
    except Exception as e:
        print(f"  Error: {e}")
