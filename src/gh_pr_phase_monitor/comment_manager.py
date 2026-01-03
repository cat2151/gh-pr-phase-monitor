"""
Comment management for posting and checking PR comments
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List

from .github_client import get_current_user, get_existing_comments


def has_copilot_apply_comment(comments: List[Dict[str, Any]]) -> bool:
    """Check if a '@copilot apply changes' comment already exists

    Args:
        comments: List of comment dictionaries

    Returns:
        True if comment exists, False otherwise
    """
    for comment in comments:
        body = comment.get("body", "")
        if "@copilot apply changes" in body:
            return True
    return False


def has_phase3_review_comment(comments: List[Dict[str, Any]]) -> bool:
    """Check if a phase3 review request comment already exists

    Args:
        comments: List of comment dictionaries

    Returns:
        True if comment exists, False otherwise
    """
    for comment in comments:
        body = comment.get("body", "")
        if "🎁レビューお願いします🎁" in body or "Please review the updates" in body:
            return True
    return False


def post_phase2_comment(pr: Dict[str, Any], repo_dir: Path = None) -> bool:
    """Post a comment to PR when phase2 is detected

    Args:
        pr: PR data dictionary containing url and reviews
        repo_dir: Repository directory (optional, not used when working with URLs)

    Returns:
        True if comment was posted successfully, False otherwise
    """
    pr_url = pr.get("url", "")
    if not pr_url:
        return False

    # Check if we already posted a comment
    existing_comments = get_existing_comments(pr_url, repo_dir)
    if has_copilot_apply_comment(existing_comments):
        print("    Comment already exists, skipping")
        return True

    # Construct comment body linking to the PR
    # Reviews don't have direct URLs in the JSON, but we can link to the PR
    comment_body = f"@copilot apply changes based on the comments in [this pull request]({pr_url})"

    cmd = ["gh", "pr", "comment", pr_url, "--body", comment_body]

    try:
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error posting comment: {e}")
        stderr = getattr(e, "stderr", "No stderr available")
        print(f"    stderr: {stderr}")
        return False


def post_phase3_comment(pr: Dict[str, Any], repo_dir: Path = None, custom_text: str = "") -> bool:
    """Post a comment to PR when phase3 is detected

    Args:
        pr: PR data dictionary containing url
        repo_dir: Repository directory (optional, not used when working with URLs)
        custom_text: Custom text to append after "@{user} " prefix.
                     Required parameter from config.

    Returns:
        True if comment was posted successfully, False otherwise

    Raises:
        RuntimeError: If unable to get current GitHub user (authentication failure)
    """
    pr_url = pr.get("url", "")
    if not pr_url:
        return False

    # Check if we already posted a comment
    existing_comments = get_existing_comments(pr_url, repo_dir)
    if has_phase3_review_comment(existing_comments):
        print("    Comment already exists, skipping")
        return True

    # Get the current authenticated user (will raise RuntimeError if unavailable)
    current_user = get_current_user()

    # Build comment body with hardcoded "@{user} " prefix
    comment_body = f"@{current_user} {custom_text}"

    cmd = ["gh", "pr", "comment", pr_url, "--body", comment_body]

    try:
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error posting comment: {e}")
        stderr = getattr(e, "stderr", "No stderr available")
        print(f"    stderr: {stderr}")
        return False
