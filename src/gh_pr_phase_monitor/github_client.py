"""
GitHub API client for interacting with repositories, PRs, and comments
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

# Cache for current user to avoid repeated subprocess calls
_current_user_cache = None

# GraphQL pagination constants
REPOSITORIES_PER_PAGE = 100
REPOSITORIES_BATCH_SIZE = 10
ISSUES_PER_REPO = 50


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
    # Includes both user-owned repos and organization repos where user is a member
    query = """
    query($login: String!) {{
      user(login: $login) {{
        repositories(first: {repositories_per_page}, ownerAffiliations: [OWNER, ORGANIZATION_MEMBER]) {{
          nodes {{
            name
            owner {{
              login
            }}
            pullRequests(states: OPEN) {{
              totalCount
            }}
          }}
          pageInfo {{
            hasNextPage
            endCursor
          }}
        }}
      }}
    }}
    """.format(repositories_per_page=REPOSITORIES_PER_PAGE)

    repos_with_prs = []
    has_next_page = True
    end_cursor = None

    while has_next_page:
        # Build query with pagination
        if end_cursor:
            query_with_pagination = query.replace(
                f"repositories(first: {REPOSITORIES_PER_PAGE}, ownerAffiliations: [OWNER, ORGANIZATION_MEMBER])",
                f'repositories(first: {REPOSITORIES_PER_PAGE}, ownerAffiliations: [OWNER, ORGANIZATION_MEMBER], after: "{end_cursor}")',
            )
        else:
            query_with_pagination = query

        # Execute GraphQL query using gh CLI
        cmd = ["gh", "api", "graphql", "-f", f"query={query_with_pagination}", "-F", f"login={current_user}"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                error_message = f"Error parsing JSON response from gh CLI: {e}\nRaw output from gh:\n{result.stdout}"
                print(error_message)
                raise RuntimeError(error_message) from e

            repositories = data.get("data", {}).get("user", {}).get("repositories", {})
            nodes = repositories.get("nodes", [])
            page_info = repositories.get("pageInfo", {})

            # Filter repositories with open PRs
            for repo in nodes:
                pr_count = repo.get("pullRequests", {}).get("totalCount", 0)
                if pr_count > 0:
                    repos_with_prs.append(
                        {"name": repo.get("name"), "owner": repo.get("owner", {}).get("login"), "openPRCount": pr_count}
                    )

            has_next_page = page_info.get("hasNextPage", False)
            end_cursor = page_info.get("endCursor")

        except subprocess.CalledProcessError as e:
            error_message = f"Error fetching repositories: {e}"
            print(error_message)
            if e.stderr:
                print(f"stderr: {e.stderr}")
            raise RuntimeError(error_message) from e

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
    # Limit to REPOSITORIES_BATCH_SIZE repos per query to avoid overly complex queries
    all_prs = []

    for i in range(0, len(repos), REPOSITORIES_BATCH_SIZE):
        batch = repos[i : i + REPOSITORIES_BATCH_SIZE]

        # Build query fragments for each repository
        repo_queries = []
        for idx, repo in enumerate(batch):
            alias = f"repo{idx}"
            repo_name = repo["name"]
            owner = repo["owner"]

            # Escape values to prevent GraphQL injection
            owner_literal = json.dumps(owner)
            repo_name_literal = json.dumps(repo_name)

            # Note: We intentionally fetch a single page of open PRs and rely on GitHub's
            # maximum page size (first: 100). Repositories with >100 open PRs will be
            # truncated; add pagination here if full coverage is required.
            repo_query = f"""
            {alias}: repository(owner: {owner_literal}, name: {repo_name_literal}) {{
              name
              owner {{
                login
              }}
              pullRequests(first: 100, states: OPEN, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
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
                    nodes {{
                      reactionGroups {{
                        content
                        users {{
                          totalCount
                        }}
                      }}
                    }}
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
          {" ".join(repo_queries)}
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
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Failed to parse JSON from 'gh api graphql' output. Raw output was:\n{result.stdout}"
                ) from e

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
                        # Transform reviews - handle null authors
                        reviews = []
                        for review in pr.get("reviews", {}).get("nodes", []):
                            author_data = review.get("author")
                            if author_data is None:
                                # Deleted account - use placeholder
                                author = {"login": "[deleted]"}
                            else:
                                author = {"login": author_data.get("login", "")}
                            reviews.append(
                                {"author": author, "state": review.get("state", ""), "body": review.get("body", "")}
                            )

                        # Transform latestReviews - handle null authors
                        latest_reviews = []
                        for review in pr.get("latestReviews", {}).get("nodes", []):
                            author_data = review.get("author")
                            if author_data is None:
                                # Deleted account - use placeholder
                                author = {"login": "[deleted]"}
                            else:
                                author = {"login": author_data.get("login", "")}
                            latest_reviews.append({"author": author, "state": review.get("state", "")})

                        # Transform reviewRequests
                        review_requests = []
                        for req in pr.get("reviewRequests", {}).get("nodes", []):
                            reviewer = req.get("requestedReviewer", {})
                            login = reviewer.get("login") or reviewer.get("name", "")
                            if login:
                                review_requests.append({"login": login})

                        # Handle null PR author
                        author_data = pr.get("author")
                        if author_data is None:
                            # Deleted account - use placeholder
                            author = {"login": "[deleted]"}
                        else:
                            author = {"login": author_data.get("login", "")}

                        # Extract comment nodes with reactionGroups
                        comments_data = pr.get("comments", {})
                        comment_nodes = comments_data.get("nodes", [])

                        # Add repository info to PR
                        pr_with_repo = {
                            "title": pr.get("title", ""),
                            "url": pr.get("url", ""),
                            "isDraft": pr.get("isDraft", False),
                            "author": author,
                            "reviews": reviews,
                            "latestReviews": latest_reviews,
                            "reviewRequests": review_requests,
                            "comments": comments_data.get("totalCount", 0),
                            "commentNodes": comment_nodes,
                            "commits": pr.get("commits", {}).get("totalCount", 0),
                            "autoMergeRequest": pr.get("autoMergeRequest"),
                            "mergeable": pr.get("mergeable", ""),
                            "reviewDecision": pr.get("reviewDecision"),
                            "state": pr.get("state", ""),
                            "repository": {"name": repo_name, "owner": owner},
                        }
                        all_prs.append(pr_with_repo)

            # Print rate limit info
            rate_limit = data.get("data", {}).get("rateLimit", {})
            if rate_limit:
                print(f"  GraphQL API - Cost: {rate_limit.get('cost')}, Remaining: {rate_limit.get('remaining')}")

        except subprocess.CalledProcessError as e:
            error_message = f"Error fetching PR details: {e}"
            print(error_message)
            if e.stderr:
                print(f"stderr: {e.stderr}")
            # Re-raise to avoid silently skipping batches and to inform the caller of incomplete data
            raise RuntimeError(error_message) from e

    return all_prs


def get_pr_data(repo_dir: Path) -> List[Dict[str, Any]]:
    """Get PR data from GitHub CLI (Legacy function - kept for compatibility)

    This function is no longer used in the main flow but kept for potential
    backwards compatibility or testing purposes.

    Args:
        repo_dir: Repository directory path

    Returns:
        List of PR data dictionaries
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


def get_all_repositories() -> List[Dict[str, Any]]:
    """Get all repositories for the authenticated user using GraphQL

    Returns:
        List of repositories with name, owner, open PR count, and open issue count
        Example: [{"name": "repo1", "owner": "user", "openPRCount": 2, "openIssueCount": 5}, ...]
    """
    current_user = get_current_user()

    # GraphQL query to get all repositories with open PR and issue counts
    query = """
    query($login: String!) {{
      user(login: $login) {{
        repositories(first: {repositories_per_page}, ownerAffiliations: [OWNER, ORGANIZATION_MEMBER]) {{
          nodes {{
            name
            owner {{
              login
            }}
            pullRequests(states: OPEN) {{
              totalCount
            }}
            issues(states: OPEN) {{
              totalCount
            }}
          }}
          pageInfo {{
            hasNextPage
            endCursor
          }}
        }}
      }}
    }}
    """.format(repositories_per_page=REPOSITORIES_PER_PAGE)

    all_repos = []
    has_next_page = True
    end_cursor = None

    while has_next_page:
        # Build query with pagination
        if end_cursor:
            query_with_pagination = query.replace(
                f"repositories(first: {REPOSITORIES_PER_PAGE}, ownerAffiliations: [OWNER, ORGANIZATION_MEMBER])",
                f'repositories(first: {REPOSITORIES_PER_PAGE}, ownerAffiliations: [OWNER, ORGANIZATION_MEMBER], after: "{end_cursor}")',
            )
        else:
            query_with_pagination = query

        # Execute GraphQL query using gh CLI
        cmd = ["gh", "api", "graphql", "-f", f"query={query_with_pagination}", "-F", f"login={current_user}"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                error_message = f"Error parsing JSON response from gh CLI: {e}\nRaw output from gh:\n{result.stdout}"
                print(error_message)
                raise RuntimeError(error_message) from e

            repositories = data.get("data", {}).get("user", {}).get("repositories", {})
            nodes = repositories.get("nodes", [])
            page_info = repositories.get("pageInfo", {})

            # Collect all repositories with their counts
            for repo in nodes:
                pr_count = repo.get("pullRequests", {}).get("totalCount", 0)
                issue_count = repo.get("issues", {}).get("totalCount", 0)
                all_repos.append({
                    "name": repo.get("name"),
                    "owner": repo.get("owner", {}).get("login"),
                    "openPRCount": pr_count,
                    "openIssueCount": issue_count
                })

            has_next_page = page_info.get("hasNextPage", False)
            end_cursor = page_info.get("endCursor")

        except subprocess.CalledProcessError as e:
            error_message = f"Error fetching repositories: {e}"
            print(error_message)
            if e.stderr:
                print(f"stderr: {e.stderr}")
            raise RuntimeError(error_message) from e

    return all_repos


def get_repositories_with_no_prs_and_open_issues() -> List[Dict[str, Any]]:
    """Get repositories that have no open PRs but have open issues

    Returns:
        List of repositories with name, owner, and open issue count
        Example: [{"name": "repo1", "owner": "user", "openIssueCount": 5}, ...]
    """
    all_repos = get_all_repositories()

    # Filter repositories: no open PRs AND has open issues
    filtered_repos = [
        repo for repo in all_repos
        if repo["openPRCount"] == 0 and repo["openIssueCount"] > 0
    ]

    return filtered_repos


def get_issues_from_repositories(repos: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """Get issues from multiple repositories, sorted by timestamp descending

    Args:
        repos: List of repository dicts with 'name' and 'owner' keys
        limit: Maximum number of issues to return (default: 10)

    Returns:
        List of issue data sorted by updatedAt timestamp in descending order
    """
    if not repos:
        return []

    # Build GraphQL query to fetch issues from all repositories
    # We'll batch repositories to avoid overly complex queries
    all_issues = []

    for i in range(0, len(repos), REPOSITORIES_BATCH_SIZE):
        batch = repos[i : i + REPOSITORIES_BATCH_SIZE]

        # Build query fragments for each repository
        repo_queries = []
        for idx, repo in enumerate(batch):
            alias = f"repo{idx}"
            repo_name = repo["name"]
            owner = repo["owner"]

            # Escape values to prevent GraphQL injection
            owner_literal = json.dumps(owner)
            repo_name_literal = json.dumps(repo_name)

            # Fetch up to ISSUES_PER_REPO issues per repository (sorted by updated time)
            repo_query = f"""
            {alias}: repository(owner: {owner_literal}, name: {repo_name_literal}) {{
              name
              owner {{
                login
              }}
              issues(first: {ISSUES_PER_REPO}, states: OPEN, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
                nodes {{
                  title
                  url
                  number
                  createdAt
                  updatedAt
                  author {{
                    login
                  }}
                }}
              }}
            }}
            """
            repo_queries.append(repo_query)

        # Combine all repository queries
        full_query = f"""
        query {{
          {" ".join(repo_queries)}
        }}
        """

        # Execute GraphQL query
        cmd = ["gh", "api", "graphql", "-f", f"query={full_query}"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Failed to parse JSON from 'gh api graphql' output. Raw output was:\n{result.stdout}"
                ) from e

            # Extract issue data from response
            for idx, repo in enumerate(batch):
                alias = f"repo{idx}"
                repo_data = data.get("data", {}).get(alias, {})

                if repo_data:
                    issues = repo_data.get("issues", {}).get("nodes", [])
                    repo_name = repo_data.get("name", repo["name"])
                    owner = repo_data.get("owner", {}).get("login", repo["owner"])

                    # Add repository info to each issue
                    for issue in issues:
                        # Handle null author
                        author_data = issue.get("author")
                        if author_data is None:
                            author = {"login": "[deleted]"}
                        else:
                            author = {"login": author_data.get("login", "")}

                        issue_with_repo = {
                            "title": issue.get("title", ""),
                            "url": issue.get("url", ""),
                            "number": issue.get("number", 0),
                            "createdAt": issue.get("createdAt", ""),
                            "updatedAt": issue.get("updatedAt", ""),
                            "author": author,
                            "repository": {"name": repo_name, "owner": owner},
                        }
                        all_issues.append(issue_with_repo)

        except subprocess.CalledProcessError as e:
            error_message = f"Error fetching issues: {e}"
            print(error_message)
            if e.stderr:
                print(f"stderr: {e.stderr}")
            raise RuntimeError(error_message) from e

    # Sort all issues by updatedAt timestamp in descending order
    all_issues.sort(key=lambda x: x["updatedAt"], reverse=True)

    # Return top N issues
    return all_issues[:limit]
