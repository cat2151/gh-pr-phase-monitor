"""
PR fetching module for GitHub pull requests
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from .graphql_client import execute_graphql_query

# GraphQL pagination constants
REPOSITORIES_BATCH_SIZE = 10


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
        data = execute_graphql_query(full_query)

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
