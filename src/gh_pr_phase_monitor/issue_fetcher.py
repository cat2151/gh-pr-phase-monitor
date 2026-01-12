"""
Issue fetching module for GitHub issues
"""

import json
from typing import Any, Dict, List, Optional

from .browser_automation import assign_issue_to_copilot_automated, is_pyautogui_available
from .graphql_client import execute_graphql_query

# GraphQL pagination constants
REPOSITORIES_BATCH_SIZE = 10
ISSUES_PER_REPO = 50


def get_issues_from_repositories(
    repos: List[Dict[str, Any]], limit: int = 10, labels: Optional[List[str]] = None, sort_by_number: bool = False
) -> List[Dict[str, Any]]:
    """Get issues from multiple repositories, sorted by timestamp descending or by issue number ascending

    Args:
        repos: List of repository dicts with 'name' and 'owner' keys
        limit: Maximum number of issues to return (default: 10)
        labels: Optional list of label names to filter by (e.g., ["good first issue"])
        sort_by_number: If True, sort by issue number ascending; otherwise sort by updatedAt descending (default: False)

    Returns:
        List of issue data sorted by updatedAt timestamp in descending order or by issue number in ascending order
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

            # Determine ordering based on sort_by_number parameter
            # When sorting by number, we need to fetch issues ordered by CREATED_AT ascending
            # (since issue numbers are assigned sequentially at creation time)
            if sort_by_number:
                order_clause = "orderBy: {field: CREATED_AT, direction: ASC}"
            else:
                order_clause = "orderBy: {field: UPDATED_AT, direction: DESC}"

            # Fetch up to ISSUES_PER_REPO issues per repository
            repo_query = f"""
            {alias}: repository(owner: {owner_literal}, name: {repo_name_literal}) {{
              name
              owner {{
                login
              }}
              issues(first: {ISSUES_PER_REPO}, states: OPEN, {order_clause}{labels_filter}) {{
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

    # Sort all issues after combining results from multiple repositories
    # Note: Issues from each repository are already pre-sorted by the GraphQL API,
    # but we need to re-sort the combined results across all repositories
    if sort_by_number:
        all_issues.sort(key=lambda x: x["number"])
    else:
        all_issues.sort(key=lambda x: x["updatedAt"], reverse=True)

    # Return top N issues
    return all_issues[:limit]


def assign_issue_to_copilot(issue: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> bool:
    """Assign an issue to GitHub Copilot using browser automation

    This function uses Selenium or Playwright to automatically:
    1. Open the issue in a browser
    2. Wait for the configured time (default 10 seconds)
    3. Click the "Assign to Copilot" button
    4. Click the "Assign" button

    This function no longer posts a comment, as that approach was found to
    increase assignee count without actually assigning Copilot, which polluted
    the issue information.

    Args:
        issue: Issue dictionary with 'url' field
        config: Optional configuration dict with automation settings

    Returns:
        True if the assignment was successful, False otherwise
    """
    # Validate that the issue dictionary contains the required fields
    if "url" not in issue:
        print("  ✗ Invalid issue data: missing 'url' field")
        return False

    issue_url = issue["url"]

    # Get issue details for logging
    repo_info = issue.get("repository", {})
    repo_name = repo_info.get("name", "unknown")
    owner = repo_info.get("owner", "unknown")
    issue_number = issue.get("number", "unknown")

    # Always use automated assignment
    print(f"  → Attempting automated assignment for issue #{issue_number}: {owner}/{repo_name}")

    if not is_pyautogui_available():
        print("  ✗ PyAutoGUI is not available")
        print("  → To enable automation, install PyAutoGUI:")
        print("     pip install pyautogui pillow")
        return False

    # Use automated browser automation
    return assign_issue_to_copilot_automated(issue_url, config)
