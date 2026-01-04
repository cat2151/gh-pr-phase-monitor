"""
Repository fetching module for GitHub repositories
"""

from typing import Any, Dict, List

from .github_auth import get_current_user
from .graphql_client import execute_graphql_query

# GraphQL pagination constants
REPOSITORIES_PER_PAGE = 100


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

        # Execute GraphQL query
        data = execute_graphql_query(query_with_pagination, {"login": current_user})

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

    return repos_with_prs


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

        # Execute GraphQL query
        data = execute_graphql_query(query_with_pagination, {"login": current_user})

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
