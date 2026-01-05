"""
Comment management for posting and checking PR comments
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List

from .github_client import get_existing_comments


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


def post_phase3_comment(pr: Dict[str, Any], comment_text: str, repo_dir: Path = None) -> bool:
    """Post a comment to PR when phase3 merge is about to happen

    Args:
        pr: PR data dictionary containing url
        comment_text: The comment text to post (from configuration)
        repo_dir: Repository directory (optional, not used when working with URLs)

    Returns:
        True if comment was posted successfully, False otherwise
    """
    pr_url = pr.get("url", "")
    if not pr_url:
        return False

    # No need to check for existing comment - we want to post this comment before merging

    cmd = ["gh", "pr", "comment", pr_url, "--body", comment_text]

    try:
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error posting comment: {e}")
        stderr = getattr(e, "stderr", "No stderr available")
        print(f"    stderr: {stderr}")
        return False
