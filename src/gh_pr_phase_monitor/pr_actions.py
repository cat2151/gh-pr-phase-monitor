"""
PR actions such as marking ready and opening browser
"""

import subprocess
import webbrowser
from pathlib import Path
from typing import Any, Dict

from .colors import colorize_phase
from .comment_manager import post_phase2_comment, post_phase3_comment
from .phase_detector import PHASE_1, PHASE_2, PHASE_3, determine_phase


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
        print("    Marking PR as ready for review...")
        if mark_pr_ready(url, None):
            print("    PR marked as ready successfully")
        else:
            print("    Failed to mark PR as ready")

    # Post comment when in phase 2
    if phase == PHASE_2:
        print("    Posting comment for phase2...")
        if post_phase2_comment(pr, None):
            print("    Comment posted successfully")
        else:
            print("    Failed to post comment")

    # Open browser and post comment when in phase 3
    if phase == PHASE_3:
        print("    Opening browser...")
        open_browser(url)

        print("    Posting comment for phase3...")
        # phase3_comment_message is required and validated in main()
        if config and "phase3_comment_message" in config:
            phase3_text = config["phase3_comment_message"]
            if post_phase3_comment(pr, None, phase3_text):
                print("    Comment posted successfully")
            else:
                print("    Failed to post comment")
        else:
            print("    Warning: phase3_comment_message not configured, skipping comment")


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
