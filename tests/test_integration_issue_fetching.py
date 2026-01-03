"""
Integration test to demonstrate the new issue fetching feature

This test simulates the scenario where all PRs are in "LLM working" phase
and shows how the tool will fetch and display issues from repositories
with no open PRs but with open issues.
"""

import json
from unittest.mock import MagicMock, patch

from src.gh_pr_phase_monitor.github_client import (
    get_all_repositories,
    get_issues_from_repositories,
    get_repositories_with_no_prs_and_open_issues,
)
from src.gh_pr_phase_monitor.phase_detector import PHASE_LLM_WORKING, determine_phase


def test_integration_all_prs_llm_working():
    """
    Integration test: When all PRs are in LLM working phase,
    the tool should fetch and display issues from repos without open PRs
    """

    # Step 1: Create sample PRs all in "LLM working" phase
    pr1 = {
        "isDraft": False,
        "reviews": [],
        "latestReviews": [],
        "reviewRequests": [],
        "commentNodes": [],
    }

    pr2 = {
        "isDraft": True,
        "reviews": [],
        "latestReviews": [],
        "reviewRequests": [],
        "commentNodes": [],
    }

    # Verify all PRs are in "LLM working" phase
    assert determine_phase(pr1) == PHASE_LLM_WORKING
    assert determine_phase(pr2) == PHASE_LLM_WORKING

    print("✓ All PRs are in 'LLM working' phase")

    # Step 2: Mock get_all_repositories to return repos with mixed states
    with patch("src.gh_pr_phase_monitor.github_client.get_current_user") as mock_user:
        mock_user.return_value = "testuser"

        with patch("subprocess.run") as mock_run:
            # Mock response for get_all_repositories
            all_repos_response = {
                "data": {
                    "user": {
                        "repositories": {
                            "nodes": [
                                {
                                    "name": "repo-with-prs-and-issues",
                                    "owner": {"login": "testuser"},
                                    "pullRequests": {"totalCount": 2},
                                    "issues": {"totalCount": 5},
                                },
                                {
                                    "name": "repo-no-prs-with-issues",
                                    "owner": {"login": "testuser"},
                                    "pullRequests": {"totalCount": 0},
                                    "issues": {"totalCount": 3},
                                },
                                {
                                    "name": "repo-no-prs-no-issues",
                                    "owner": {"login": "testuser"},
                                    "pullRequests": {"totalCount": 0},
                                    "issues": {"totalCount": 0},
                                },
                            ],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        }
                    }
                }
            }

            mock_result = MagicMock()
            mock_result.stdout = json.dumps(all_repos_response)
            mock_run.return_value = mock_result

            # Get all repositories
            all_repos = get_all_repositories()
            assert len(all_repos) == 3
            print(f"✓ Found {len(all_repos)} repositories total")

            # Step 3: Filter for repos with no PRs but with issues
            filtered_repos = get_repositories_with_no_prs_and_open_issues()
            assert len(filtered_repos) == 1
            assert filtered_repos[0]["name"] == "repo-no-prs-with-issues"
            print(f"✓ Found {len(filtered_repos)} repository with no open PRs but with open issues")

            # Step 4: Mock get_issues_from_repositories
            issues_response = {
                "data": {
                    "repo0": {
                        "name": "repo-no-prs-with-issues",
                        "owner": {"login": "testuser"},
                        "issues": {
                            "nodes": [
                                {
                                    "title": "Feature request: Add dark mode",
                                    "url": "https://github.com/testuser/repo-no-prs-with-issues/issues/1",
                                    "number": 1,
                                    "createdAt": "2024-01-01T00:00:00Z",
                                    "updatedAt": "2024-01-03T12:00:00Z",
                                    "author": {"login": "contributor1"},
                                },
                                {
                                    "title": "Bug: Login page crashes on mobile",
                                    "url": "https://github.com/testuser/repo-no-prs-with-issues/issues/2",
                                    "number": 2,
                                    "createdAt": "2024-01-02T00:00:00Z",
                                    "updatedAt": "2024-01-04T08:30:00Z",
                                    "author": {"login": "contributor2"},
                                },
                                {
                                    "title": "Documentation: Update README",
                                    "url": "https://github.com/testuser/repo-no-prs-with-issues/issues/3",
                                    "number": 3,
                                    "createdAt": "2024-01-03T00:00:00Z",
                                    "updatedAt": "2024-01-02T16:00:00Z",
                                    "author": {"login": "contributor3"},
                                },
                            ]
                        },
                    }
                }
            }

            mock_result.stdout = json.dumps(issues_response)

            # Get issues from filtered repositories
            issues = get_issues_from_repositories(filtered_repos, limit=10)
            assert len(issues) == 3

            # Verify issues are sorted by updatedAt descending
            assert issues[0]["title"] == "Bug: Login page crashes on mobile"
            assert issues[1]["title"] == "Feature request: Add dark mode"
            assert issues[2]["title"] == "Documentation: Update README"

            print(f"✓ Fetched {len(issues)} issues sorted by last update (descending)")
            print("\nTop issues:")
            for idx, issue in enumerate(issues, 1):
                print(f"  {idx}. [{issue['repository']['owner']}/{issue['repository']['name']}] #{issue['number']}: {issue['title']}")
                print(f"     Updated: {issue['updatedAt']}")

    print("\n✅ Integration test passed!")


if __name__ == "__main__":
    test_integration_all_prs_llm_working()
