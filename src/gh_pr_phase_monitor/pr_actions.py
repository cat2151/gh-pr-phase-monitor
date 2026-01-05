"""
PR actions such as marking ready and opening browser
"""

import subprocess
import webbrowser
from pathlib import Path
from typing import Any, Dict, Set, Tuple

from .colors import colorize_phase
from .comment_manager import (
    post_phase2_comment,
)
from .notifier import send_phase3_notification
from .phase_detector import PHASE_1, PHASE_2, PHASE_3, determine_phase

# Track which PRs have had their browser opened: set of (url, phase) tuples
_browser_opened: Set[Tuple[str, str]] = set()

# Track which PRs have had notifications sent: set of (url, phase) tuples
_notifications_sent: Set[Tuple[str, str]] = set()


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

    # Mark PR as ready for review when in phase 1
    if phase == PHASE_1:
        # Check if execution is enabled
        execution_enabled = config.get("enable_execution_phase1_to_phase2", False) if config else False
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
        execution_enabled = config.get("enable_execution_phase2_to_phase3", False) if config else False
        if execution_enabled:
            print("    Posting comment for phase2...")
            if post_phase2_comment(pr, None):
                print("    Comment posted successfully")
            else:
                print("    Failed to post comment")
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
        execution_enabled = config.get("enable_execution_phase3_send_ntfy", False) if config else False
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
