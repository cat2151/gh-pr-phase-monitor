"""
Comment fetching module for GitHub PRs
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def get_existing_comments(pr_url: str, repo_dir: Path = None) -> List[Dict[str, Any]]:
    """Get existing comments on a PR

    Args:
        pr_url: URL of the PR
        repo_dir: Repository directory (optional, not used when working with URLs)

    Returns:
        List of comment dictionaries
    """
    cmd = ["gh", "pr", "view", pr_url, "--json", "comments"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        data = json.loads(result.stdout)
        return data.get("comments", [])
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []
