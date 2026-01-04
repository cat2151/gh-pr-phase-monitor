"""
GitHub API client for interacting with repositories, PRs, and comments

This module now serves as a compatibility layer, re-exporting functions from specialized modules.
The original functionality has been split into focused modules following the Single Responsibility Principle:
- github_auth: Authentication management
- graphql_client: GraphQL query execution
- repository_fetcher: Repository operations
- pr_fetcher: PR operations
- issue_fetcher: Issue operations
- comment_fetcher: Comment operations
"""

# Re-export authentication functions
from .github_auth import get_current_user

# Re-export repository functions
from .repository_fetcher import (
    get_all_repositories,
    get_repositories_with_no_prs_and_open_issues,
    get_repositories_with_open_prs,
)

# Re-export PR functions
from .pr_fetcher import get_pr_data, get_pr_details_batch

# Re-export issue functions
from .issue_fetcher import get_issues_from_repositories

# Re-export comment functions
from .comment_fetcher import get_existing_comments

__all__ = [
    "get_current_user",
    "get_repositories_with_open_prs",
    "get_all_repositories",
    "get_repositories_with_no_prs_and_open_issues",
    "get_pr_details_batch",
    "get_pr_data",
    "get_issues_from_repositories",
    "get_existing_comments",
]
