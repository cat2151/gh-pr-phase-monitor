"""
Issue fetching module for GitHub issues
"""

import json
from typing import Any, Dict, List

from .graphql_client import execute_graphql_query

# GraphQL pagination constants
REPOSITORIES_BATCH_SIZE = 10
ISSUES_PER_REPO = 50


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
        data = execute_graphql_query(full_query)

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

    # Sort all issues by updatedAt timestamp in descending order
    all_issues.sort(key=lambda x: x["updatedAt"], reverse=True)

    # Return top N issues
    return all_issues[:limit]
