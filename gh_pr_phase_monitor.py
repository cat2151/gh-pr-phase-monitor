#!/usr/bin/env python3
"""
GitHub PR Phase Monitor
Monitors PR phases and opens browser for actionable phases
"""

import json
import re
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Any, Dict, List

import tomli

# Cache for current user to avoid repeated subprocess calls
_current_user_cache = None


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


def parse_interval(interval_str: str) -> int:
    """Parse interval string like '1m', '30s', '2h' to seconds

    Args:
        interval_str: String like '1m', '30s', '2h', '1d'

    Returns:
        Number of seconds

    Raises:
        ValueError: If the interval string format is invalid
    """
    # Type validation for common misconfiguration
    if not isinstance(interval_str, str):
        raise ValueError(
            f"Interval must be a string (e.g., '1m', '30s'), got {type(interval_str).__name__}: {interval_str}"
        )

    interval_str = interval_str.strip().lower()

    # Match pattern like "30s", "1m", "2h", "1d"
    match = re.match(r"^(\d+)([smhd])$", interval_str)

    if not match:
        raise ValueError(
            f"Invalid interval format: '{interval_str}'. "
            "Expected format: <number><unit> (e.g., '30s', '1m', '2h', '1d')"
        )

    value = int(match.group(1))
    unit = match.group(2)

    # Convert to seconds
    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    else:  # unit == "d"
        return value * 86400


def load_config(config_path: str = "config.toml") -> Dict[str, Any]:
    """Load configuration from TOML file"""
    with open(config_path, "rb") as f:
        return tomli.load(f)


def get_current_user() -> str:
    """Get the current authenticated GitHub user's login

    Returns:
        The login name of the current authenticated user

    Raises:
        RuntimeError: If unable to retrieve the current user (authentication failure)
    """
    global _current_user_cache

    # Return cached value if available (only cache successful authentication)
    if _current_user_cache is not None and _current_user_cache != "":
        return _current_user_cache

    cmd = ["gh", "api", "user", "--jq", ".login"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        _current_user_cache = result.stdout.strip()
        return _current_user_cache
    except subprocess.CalledProcessError as e:
        error_msg = (
            "Failed to retrieve current GitHub user via `gh api user`. "
            "GitHub CLI authentication is required for phase3 comments. "
            "Please run `gh auth login` or `gh auth status` to check your authentication."
        )
        print(f"\n[ERROR] {error_msg}")
        if e.stderr:
            print(f"Details: {e.stderr}")
        raise RuntimeError(error_msg) from e


def get_repositories_with_open_prs() -> List[Dict[str, Any]]:
    """Get all repositories with open PR counts using GraphQL (Phase 1)

    Returns:
        List of repositories with name and open PR count
        Example: [{"name": "repo1", "owner": "user", "openPRCount": 2}, ...]
    """
    current_user = get_current_user()

    # GraphQL query to get all repositories with open PR counts
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(first: 100, ownerAffiliations: OWNER) {
          nodes {
            name
            owner {
              login
            }
            pullRequests(states: OPEN) {
              totalCount
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
    """

    repos_with_prs = []
    has_next_page = True
    end_cursor = None

    while has_next_page:
        if end_cursor:
            # Add pagination support
            query_with_pagination = query.replace(
                "repositories(first: 100, ownerAffiliations: OWNER)",
                f'repositories(first: 100, ownerAffiliations: OWNER, after: "{end_cursor}")'
            )
        else:
            query_with_pagination = query

        # Execute GraphQL query using gh CLI
        cmd = ["gh", "api", "graphql", "-f", f"query={query_with_pagination}", "-F", f"login={current_user}"]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
            )
            data = json.loads(result.stdout)

            repositories = data.get("data", {}).get("user", {}).get("repositories", {})
            nodes = repositories.get("nodes", [])
            page_info = repositories.get("pageInfo", {})

            # Filter repositories with open PRs
            for repo in nodes:
                pr_count = repo.get("pullRequests", {}).get("totalCount", 0)
                if pr_count > 0:
                    repos_with_prs.append({
                        "name": repo.get("name"),
                        "owner": repo.get("owner", {}).get("login"),
                        "openPRCount": pr_count
                    })

            has_next_page = page_info.get("hasNextPage", False)
            end_cursor = page_info.get("endCursor")

        except subprocess.CalledProcessError as e:
            print(f"Error fetching repositories: {e}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            break

    return repos_with_prs


def get_pr_details_batch(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get PR details for multiple repositories in a single GraphQL query (Phase 2)

    Args:
        repos: List of repository dicts with 'name' and 'owner' keys

    Returns:
        List of PR data matching the format expected by determine_phase()
    """
    if not repos:
        return []

    # Build GraphQL query with aliases for multiple repositories
    # Limit to 10 repos per query to avoid overly complex queries
    batch_size = 10
    all_prs = []

    for i in range(0, len(repos), batch_size):
        batch = repos[i:i+batch_size]

        # Build query fragments for each repository
        repo_queries = []
        for idx, repo in enumerate(batch):
            alias = f"repo{idx}"
            repo_name = repo["name"]
            owner = repo["owner"]

            repo_query = f"""
            {alias}: repository(owner: "{owner}", name: "{repo_name}") {{
              name
              owner {{
                login
              }}
              pullRequests(first: 50, states: OPEN, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
                nodes {{
                  title
                  url
                  isDraft
                  author {{
                    login
                  }}
                  reviews(last: 50) {{
                    nodes {{
                      author {{
                        login
                      }}
                      state
                      body
                    }}
                  }}
                  latestReviews(first: 50) {{
                    nodes {{
                      author {{
                        login
                      }}
                      state
                    }}
                  }}
                  reviewRequests(first: 10) {{
                    nodes {{
                      requestedReviewer {{
                        ... on User {{
                          login
                        }}
                        ... on Team {{
                          name
                        }}
                      }}
                    }}
                  }}
                  comments(last: 10) {{
                    totalCount
                  }}
                  commits(last: 1) {{
                    totalCount
                  }}
                  autoMergeRequest {{
                    enabledAt
                  }}
                  mergeable
                  reviewDecision
                  state
                }}
              }}
            }}
            """
            repo_queries.append(repo_query)

        # Combine all repository queries
        full_query = f"""
        query {{
          {' '.join(repo_queries)}
          rateLimit {{
            cost
            remaining
            resetAt
          }}
        }}
        """

        # Execute GraphQL query
        cmd = ["gh", "api", "graphql", "-f", f"query={full_query}"]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
            )
            data = json.loads(result.stdout)

            # Extract PR data from response
            for idx, repo in enumerate(batch):
                alias = f"repo{idx}"
                repo_data = data.get("data", {}).get(alias, {})

                if repo_data:
                    prs = repo_data.get("pullRequests", {}).get("nodes", [])
                    repo_name = repo_data.get("name", repo["name"])
                    owner = repo_data.get("owner", {}).get("login", repo["owner"])

                    # Transform GraphQL data to match expected format
                    for pr in prs:
                        # Transform reviews
                        reviews = []
                        for review in pr.get("reviews", {}).get("nodes", []):
                            reviews.append({
                                "author": {"login": review.get("author", {}).get("login", "")},
                                "state": review.get("state", ""),
                                "body": review.get("body", "")
                            })

                        # Transform latestReviews
                        latest_reviews = []
                        for review in pr.get("latestReviews", {}).get("nodes", []):
                            latest_reviews.append({
                                "author": {"login": review.get("author", {}).get("login", "")},
                                "state": review.get("state", "")
                            })

                        # Transform reviewRequests
                        review_requests = []
                        for req in pr.get("reviewRequests", {}).get("nodes", []):
                            reviewer = req.get("requestedReviewer", {})
                            login = reviewer.get("login") or reviewer.get("name", "")
                            if login:
                                review_requests.append({"login": login})

                        # Add repository info to PR
                        pr_with_repo = {
                            "title": pr.get("title", ""),
                            "url": pr.get("url", ""),
                            "isDraft": pr.get("isDraft", False),
                            "author": pr.get("author", {}),
                            "reviews": reviews,
                            "latestReviews": latest_reviews,
                            "reviewRequests": review_requests,
                            "comments": pr.get("comments", {}).get("totalCount", 0),
                            "commits": pr.get("commits", {}).get("totalCount", 0),
                            "autoMergeRequest": pr.get("autoMergeRequest"),
                            "mergeable": pr.get("mergeable", ""),
                            "reviewDecision": pr.get("reviewDecision"),
                            "state": pr.get("state", ""),
                            "repository": {
                                "name": repo_name,
                                "owner": owner
                            }
                        }
                        all_prs.append(pr_with_repo)

            # Print rate limit info
            rate_limit = data.get("data", {}).get("rateLimit", {})
            if rate_limit:
                print(f"  GraphQL API - Cost: {rate_limit.get('cost')}, Remaining: {rate_limit.get('remaining')}")

        except subprocess.CalledProcessError as e:
            print(f"Error fetching PR details: {e}")
            if e.stderr:
                print(f"stderr: {e.stderr}")

    return all_prs


def get_pr_data(repo_dir: Path) -> List[Dict[str, Any]]:
    """Get PR data from GitHub CLI (Legacy function - kept for compatibility)

    This function is no longer used in the main flow but kept for potential
    backwards compatibility or testing purposes.
    """
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
    """Determine which phase the PR is in

    Args:
        pr: PR data dictionary

    Returns:
        Phase string: "phase1", "phase2", "phase3", or "LLM working"
    """
    is_draft = pr.get("isDraft", False)
    reviews = pr.get("reviews", [])
    latest_reviews = pr.get("latestReviews", [])
    review_requests = pr.get("reviewRequests", [])

    # Phase 1: Draft状態 (ただし、reviewRequestsが空の場合はLLM working)
    if is_draft:
        # reviewRequestsが空なら、LLM workingと判定
        if not review_requests:
            return "LLM working"
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

        # CHANGES_REQUESTEDの場合は確実にphase2
        if review_state == "CHANGES_REQUESTED":
            return "phase2"

        # COMMENTEDの場合、レビュー本文にインラインコメントの存在を示すパターンがあるかチェック
        # レビューコメントがある場合はphase2（修正が必要）、ない場合はphase3（レビュー待ち）
        if review_state == "COMMENTED":
            review_body = latest_review.get("body", "")
            if has_inline_review_comments(review_body):
                return "phase2"
            # レビューコメントがない場合はphase3
            return "phase3"

        # それ以外(APPROVED, DISMISSED, PENDING等)はphase3
        return "phase3"

    # Phase 3: copilot-swe-agent の修正後
    if author_login == "copilot-swe-agent":
        return "phase3"

    return "LLM working"


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
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
        )
        data = json.loads(result.stdout)
        return data.get("comments", [])
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []


def has_inline_review_comments(review_body: str) -> bool:
    """Check if review body indicates inline code comments were generated

    Copilot's review body contains text like:
    "Copilot reviewed X out of Y changed files in this pull request and generated N comment(s)."
    when inline comments are present.

    Args:
        review_body: The body text of the review

    Returns:
        True if the review body indicates inline comments exist, False otherwise
    """
    if not review_body:
        return False

    # Check for the pattern indicating inline comments were generated
    # Pattern matches: "generated 1 comment" or "generated 2 comments" etc.
    pattern = r"generated\s+\d+\s+comments?"
    return bool(re.search(pattern, review_body, re.IGNORECASE))


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
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
        )
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
        subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error posting comment: {e}")
        stderr = getattr(e, "stderr", "No stderr available")
        print(f"    stderr: {stderr}")
        return False


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
        subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error marking PR as ready: {e}")
        stderr = getattr(e, "stderr", "No stderr available")
        print(f"    stderr: {stderr}")
        return False


def open_browser(url: str) -> None:
    """Open URL in browser"""
    webbrowser.open(url)


def process_pr(pr: Dict[str, Any], config: Dict[str, Any] = None) -> None:
    """Process a single PR

    Args:
        pr: PR data dictionary (with repository info)
        config: Configuration dictionary (optional)
    """
    repo_info = pr.get("repository", {})
    repo_name = repo_info.get("name", "Unknown")
    repo_owner = repo_info.get("owner", "Unknown")
    title = pr.get("title", "Unknown")
    url = pr.get("url", "")
    phase = determine_phase(pr)

    # Phase表示をカラフルに
    phase_display = colorize_phase(phase)
    print(f"  [{repo_owner}/{repo_name}] {phase_display} {title}")
    print(f"    URL: {url}")

    # Phase 1, 2, 3 の場合はブラウザで開く
    if phase in ["phase1", "phase2", "phase3"]:
        print("    Opening browser...")
        open_browser(url)

        # Mark PR as ready for review when in phase 1
        if phase == "phase1":
            print("    Marking PR as ready for review...")
            if mark_pr_ready(url, None):
                print("    PR marked as ready successfully")
            else:
                print("    Failed to mark PR as ready")

        # Post comment when in phase 2
        if phase == "phase2":
            print("    Posting comment for phase2...")
            if post_phase2_comment(pr, None):
                print("    Comment posted successfully")
            else:
                print("    Failed to post comment")

        # Post comment when in phase 3
        if phase == "phase3":
            print("    Posting comment for phase3...")
            # phase3_comment_message is required and validated in main()
            phase3_text = config["phase3_comment_message"]
            if post_phase3_comment(pr, None, phase3_text):
                print("    Comment posted successfully")
            else:
                print("    Failed to post comment")


def process_repository(repo_dir: Path, config: Dict[str, Any] = None) -> None:
    """Process a single repository (Legacy function - kept for compatibility)

    Args:
        repo_dir: Repository directory
        config: Configuration dictionary (optional)
    """
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

                # Mark PR as ready for review when in phase 1
                if phase == "phase1":
                    print("    Marking PR as ready for review...")
                    if mark_pr_ready(url, repo_dir):
                        print("    PR marked as ready successfully")
                    else:
                        print("    Failed to mark PR as ready")

                # Post comment when in phase 2
                if phase == "phase2":
                    print("    Posting comment for phase2...")
                    if post_phase2_comment(pr, repo_dir):
                        print("    Comment posted successfully")
                    else:
                        print("    Failed to post comment")

                # Post comment when in phase 3
                if phase == "phase3":
                    print("    Posting comment for phase3...")
                    # phase3_comment_message is required and validated in main()
                    phase3_text = config["phase3_comment_message"]
                    if post_phase3_comment(pr, repo_dir, phase3_text):
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

        except RuntimeError as e:
            print(f"\nError: {e}")
            print("Please ensure you are authenticated with gh CLI")
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            import traceback
            traceback.print_exc()

        print(f"\n{'=' * 50}")
        print(f"Waiting {interval_str} until next check...")
        print(f"{'=' * 50}")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
