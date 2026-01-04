"""
Issue fetching module for GitHub issues
"""

import json
import subprocess
from typing import Any, Dict, List

from .graphql_client import execute_graphql_query

# GraphQL pagination constants
REPOSITORIES_BATCH_SIZE = 10
ISSUES_PER_REPO = 50


def get_issues_from_repositories(repos: List[Dict[str, Any]], limit: int = 10, labels: List[str] = None) -> List[Dict[str, Any]]:
    """Get issues from multiple repositories, sorted by timestamp descending

    Args:
        repos: List of repository dicts with 'name' and 'owner' keys
        limit: Maximum number of issues to return (default: 10)
        labels: Optional list of label names to filter by (e.g., ["good first issue"])

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

            # Build labels filter if provided
            labels_filter = ""
            if labels:
                labels_json = json.dumps(labels)
                labels_filter = f", labels: {labels_json}"

            # Fetch up to ISSUES_PER_REPO issues per repository (sorted by updated time)
            repo_query = f"""
            {alias}: repository(owner: {owner_literal}, name: {repo_name_literal}) {{
              name
              owner {{
                login
              }}
              issues(first: {ISSUES_PER_REPO}, states: OPEN, orderBy: {{field: UPDATED_AT, direction: DESC}}{labels_filter}) {{
                nodes {{
                  title
                  url
                  number
                  createdAt
                  updatedAt
                  author {{
                    login
                  }}
                  labels(first: 10) {{
                    nodes {{
                      name
                    }}
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

                    # Extract label names
                    label_nodes = issue.get("labels", {}).get("nodes", [])
                    label_names = [label.get("name", "") for label in label_nodes]

                    issue_with_repo = {
                        "title": issue.get("title", ""),
                        "url": issue.get("url", ""),
                        "number": issue.get("number", 0),
                        "createdAt": issue.get("createdAt", ""),
                        "updatedAt": issue.get("updatedAt", ""),
                        "author": author,
                        "labels": label_names,
                        "repository": {"name": repo_name, "owner": owner},
                    }
                    all_issues.append(issue_with_repo)

    # Sort all issues by updatedAt timestamp in descending order
    all_issues.sort(key=lambda x: x["updatedAt"], reverse=True)

    # Return top N issues
    return all_issues[:limit]


def assign_issue_to_copilot(issue: Dict[str, Any]) -> bool:
    """Assign an issue to GitHub Copilot by posting an 'Assign to Copilot' comment

    Args:
        issue: Issue dictionary with 'repository' (name, owner), 'number' fields

    Returns:
        True if assignment was successful, False otherwise
    """
    repo_name = issue["repository"]["name"]
    owner = issue["repository"]["owner"]
    issue_number = issue["number"]

    # Post a comment "Assign to Copilot" which triggers GitHub's workflow for Copilot assignment
    try:
        cmd = [
            "gh",
            "issue",
            "comment",
            str(issue_number),
            "--repo",
            f"{owner}/{repo_name}",
            "--body",
            "Assign to Copilot",
        ]

        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            timeout=30,  # 30 second timeout for the gh command
        )

        print(f"  ✓ Assigned issue #{issue_number} to Copilot in {owner}/{repo_name}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to assign issue #{issue_number} to Copilot: {e}")
        if e.stderr:
            print(f"    stderr: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout while assigning issue #{issue_number} to Copilot")
        return False
