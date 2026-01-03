#!/usr/bin/env python3
"""
GitHub PR Phase Monitor
Monitors PR phases and opens browser for actionable phases
"""

import json
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Any, Dict, List

import tomli


# ANSI Color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    RED = "\033[91m"
    BLUE = "\033[94m"


def colorize_phase(phase: str) -> str:
    """Add color to phase string"""
    if phase == "phase1":
        return f"{Colors.BOLD}{Colors.YELLOW}[{phase}]{Colors.RESET}"
    elif phase == "phase2":
        return f"{Colors.BOLD}{Colors.CYAN}[{phase}]{Colors.RESET}"
    elif phase == "phase3":
        return f"{Colors.BOLD}{Colors.GREEN}[{phase}]{Colors.RESET}"
    else:  # LLM working
        return f"{Colors.BOLD}{Colors.MAGENTA}[{phase}]{Colors.RESET}"


def load_config(config_path: str = "config.toml") -> Dict[str, Any]:
    """Load configuration from TOML file"""
    with open(config_path, "rb") as f:
        return tomli.load(f)


def get_pr_data(repo_dir: Path) -> List[Dict[str, Any]]:
    """Get PR data from GitHub CLI"""
    cmd = [
        "gh",
        "pr",
        "list",
        "--json",
        "author,autoMergeRequest,comments,commits,isDraft,latestReviews,mergeable,reviewDecision,reviewRequests,reviews,state,statusCheckRollup,title,url",
    ]

    result = subprocess.run(
        cmd, cwd=repo_dir, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
    )

    return json.loads(result.stdout)


def determine_phase(pr: Dict[str, Any]) -> str:
    """Determine which phase the PR is in"""
    is_draft = pr.get("isDraft", False)
    reviews = pr.get("reviews", [])
    latest_reviews = pr.get("latestReviews", [])

    # Phase 1: Draft状態
    if is_draft:
        return "phase1"

    # Phase 2 と Phase 3 の判定には reviews が必要
    if not reviews or not latest_reviews:
        return "LLM working"

    # 最新のレビューを取得
    latest_review = reviews[-1]
    author_login = latest_review.get("author", {}).get("login", "")

    # Phase 2/3: copilot-pull-request-reviewer のレビュー後
    if author_login == "copilot-pull-request-reviewer":
        # レビューの状態を確認
        review_state = latest_review.get("state", "")

        # CHANGES_REQUESTEDの場合のみphase2 (copilot-swe-agentの対応待ち)
        # それ以外(APPROVED, COMMENTED, DISMISSED, PENDING等)はphase3
        # 本文の有無に関わらず、CHANGES_REQUESTEDでなければphase3と判定
        if review_state == "CHANGES_REQUESTED":
            return "phase2"

        return "phase3"

    # Phase 3: copilot-swe-agent の修正後
    if author_login == "copilot-swe-agent":
        return "phase3"

    return "LLM working"


def get_existing_comments(pr_url: str, repo_dir: Path) -> List[Dict[str, Any]]:
    """Get existing comments on a PR

    Args:
        pr_url: URL of the PR
        repo_dir: Repository directory

    Returns:
        List of comment dictionaries
    """
    cmd = ["gh", "pr", "view", pr_url, "--json", "comments"]

    try:
        result = subprocess.run(
            cmd, cwd=repo_dir, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
        )
        data = json.loads(result.stdout)
        return data.get("comments", [])
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []


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


def post_phase2_comment(pr: Dict[str, Any], repo_dir: Path) -> bool:
    """Post a comment to PR when phase2 is detected

    Args:
        pr: PR data dictionary containing url and reviews
        repo_dir: Repository directory

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

    # Get the latest review to include its URL in the comment
    reviews = pr.get("reviews", [])
    if reviews:
        reviews[-1]
        # Try to construct review URL from PR URL and review info
        # Reviews don't have direct URLs in the JSON, but we can link to the PR
        comment_body = f"@copilot apply changes based on the comments in [this pull request]({pr_url})"
    else:
        comment_body = f"@copilot apply changes based on the comments in [this pull request]({pr_url})"

    cmd = ["gh", "pr", "comment", pr_url, "--body", comment_body]

    try:
        subprocess.run(
            cmd, cwd=repo_dir, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error posting comment: {e}")
        stderr = getattr(e, "stderr", "No stderr available")
        print(f"    stderr: {stderr}")
        return False


def open_browser(url: str) -> None:
    """Open URL in browser"""
    webbrowser.open(url)


def process_repository(repo_dir: Path) -> None:
    """Process a single repository"""
    print(f"\n=== Processing: {repo_dir} ===")

    try:
        pr_list = get_pr_data(repo_dir)

        if not pr_list:
            print("  No open PRs found")
            return

        for pr in pr_list:
            title = pr.get("title", "Unknown")
            url = pr.get("url", "")
            phase = determine_phase(pr)

            # Phase表示をカラフルに
            phase_display = colorize_phase(phase)
            print(f"  {phase_display} {title}")
            print(f"    URL: {url}")

            # Phase 1, 2, 3 の場合はブラウザで開く
            if phase in ["phase1", "phase2", "phase3"]:
                print("    Opening browser...")
                open_browser(url)

                # Post comment when in phase 2
                if phase == "phase2":
                    print("    Posting comment for phase2...")
                    if post_phase2_comment(pr, repo_dir):
                        print("    Comment posted successfully")
                    else:
                        print("    Failed to post comment")

    except subprocess.CalledProcessError as e:
        print(f"  Error running gh command: {e}")
        print(f"  stderr: {e.stderr}")
    except Exception as e:
        print(f"  Error: {e}")


def main():
    """Main execution function"""
    config_path = "config.toml"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    try:
        config = load_config(config_path)
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found")
        print("\nExpected format:")
        print('dirs = ["/path/to/repo1", "/path/to/repo2"]')
        sys.exit(1)

    dirs = config.get("dirs", [])

    if not dirs:
        print("Error: No directories specified in config")
        sys.exit(1)

    print("GitHub PR Phase Monitor")
    print("=" * 50)

    for dir_path in dirs:
        repo_dir = Path(dir_path).expanduser()

        if not repo_dir.exists():
            print(f"\nWarning: Directory does not exist: {repo_dir}")
            continue

        process_repository(repo_dir)

    print("\n" + "=" * 50)
    print("Monitoring complete")


if __name__ == "__main__":
    main()
