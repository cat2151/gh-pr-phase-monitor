"""
Tests for issue fetching functionality
"""

import json
import subprocess
from unittest.mock import MagicMock, patch

from src.gh_pr_phase_monitor.github_client import (
    assign_issue_to_copilot,
    get_all_repositories,
    get_issues_from_repositories,
    get_repositories_with_no_prs_and_open_issues,
)


class TestGetAllRepositories:
    """Tests for get_all_repositories function"""

    @patch("src.gh_pr_phase_monitor.repository_fetcher.get_current_user")
    @patch("subprocess.run")
    def test_get_all_repositories_success(self, mock_run, mock_get_user):
        """Test successful retrieval of all repositories"""
        mock_get_user.return_value = "testuser"

        # Mock the GraphQL response
        mock_response = {
            "data": {
                "user": {
                    "repositories": {
                        "nodes": [
                            {
                                "name": "repo1",
                                "owner": {"login": "testuser"},
                                "pullRequests": {"totalCount": 2},
                                "issues": {"totalCount": 5},
                            },
                            {
                                "name": "repo2",
                                "owner": {"login": "testuser"},
                                "pullRequests": {"totalCount": 0},
                                "issues": {"totalCount": 3},
                            },
                        ],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        }

        mock_result = MagicMock()
        mock_result.stdout = json.dumps(mock_response)
        mock_run.return_value = mock_result

        repos = get_all_repositories()

        assert len(repos) == 2
        assert repos[0]["name"] == "repo1"
        assert repos[0]["openPRCount"] == 2
        assert repos[0]["openIssueCount"] == 5
        assert repos[1]["name"] == "repo2"
        assert repos[1]["openPRCount"] == 0
        assert repos[1]["openIssueCount"] == 3

    @patch("src.gh_pr_phase_monitor.repository_fetcher.get_current_user")
    @patch("subprocess.run")
    def test_get_all_repositories_empty(self, mock_run, mock_get_user):
        """Test retrieval when no repositories exist"""
        mock_get_user.return_value = "testuser"

        mock_response = {
            "data": {
                "user": {
                    "repositories": {
                        "nodes": [],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        }

        mock_result = MagicMock()
        mock_result.stdout = json.dumps(mock_response)
        mock_run.return_value = mock_result

        repos = get_all_repositories()

        assert len(repos) == 0


class TestGetRepositoriesWithNoPrsAndOpenIssues:
    """Tests for get_repositories_with_no_prs_and_open_issues function"""

    @patch("src.gh_pr_phase_monitor.repository_fetcher.get_all_repositories")
    def test_filter_repos_with_no_prs_and_issues(self, mock_get_all):
        """Test filtering repositories with no PRs but with issues"""
        mock_get_all.return_value = [
            {"name": "repo1", "owner": "user", "openPRCount": 2, "openIssueCount": 5},
            {"name": "repo2", "owner": "user", "openPRCount": 0, "openIssueCount": 3},
            {"name": "repo3", "owner": "user", "openPRCount": 0, "openIssueCount": 0},
            {"name": "repo4", "owner": "user", "openPRCount": 1, "openIssueCount": 0},
        ]

        filtered = get_repositories_with_no_prs_and_open_issues()

        assert len(filtered) == 1
        assert filtered[0]["name"] == "repo2"
        assert filtered[0]["openPRCount"] == 0
        assert filtered[0]["openIssueCount"] == 3

    @patch("src.gh_pr_phase_monitor.repository_fetcher.get_all_repositories")
    def test_filter_repos_empty_result(self, mock_get_all):
        """Test filtering when no repositories match criteria"""
        mock_get_all.return_value = [
            {"name": "repo1", "owner": "user", "openPRCount": 2, "openIssueCount": 5},
            {"name": "repo2", "owner": "user", "openPRCount": 1, "openIssueCount": 3},
        ]

        filtered = get_repositories_with_no_prs_and_open_issues()

        assert len(filtered) == 0


class TestGetIssuesFromRepositories:
    """Tests for get_issues_from_repositories function"""

    @patch("subprocess.run")
    def test_get_issues_success(self, mock_run):
        """Test successful retrieval of issues from repositories"""
        repos = [
            {"name": "repo1", "owner": "user1"},
            {"name": "repo2", "owner": "user2"},
        ]

        mock_response = {
            "data": {
                "repo0": {
                    "name": "repo1",
                    "owner": {"login": "user1"},
                    "issues": {
                        "nodes": [
                            {
                                "title": "Issue 1",
                                "url": "https://github.com/user1/repo1/issues/1",
                                "number": 1,
                                "createdAt": "2024-01-01T00:00:00Z",
                                "updatedAt": "2024-01-03T00:00:00Z",
                                "author": {"login": "author1"},
                                "labels": {"nodes": [{"name": "bug"}]},
                            },
                            {
                                "title": "Issue 2",
                                "url": "https://github.com/user1/repo1/issues/2",
                                "number": 2,
                                "createdAt": "2024-01-02T00:00:00Z",
                                "updatedAt": "2024-01-02T00:00:00Z",
                                "author": {"login": "author2"},
                                "labels": {"nodes": []},
                            },
                        ]
                    },
                },
                "repo1": {
                    "name": "repo2",
                    "owner": {"login": "user2"},
                    "issues": {
                        "nodes": [
                            {
                                "title": "Issue 3",
                                "url": "https://github.com/user2/repo2/issues/1",
                                "number": 1,
                                "createdAt": "2024-01-01T00:00:00Z",
                                "updatedAt": "2024-01-04T00:00:00Z",
                                "author": {"login": "author3"},
                                "labels": {"nodes": [{"name": "enhancement"}]},
                            }
                        ]
                    },
                },
            }
        }

        mock_result = MagicMock()
        mock_result.stdout = json.dumps(mock_response)
        mock_run.return_value = mock_result

        issues = get_issues_from_repositories(repos, limit=10)

        assert len(issues) == 3
        # Check sorting by updatedAt descending
        assert issues[0]["title"] == "Issue 3"
        assert issues[0]["updatedAt"] == "2024-01-04T00:00:00Z"
        assert issues[1]["title"] == "Issue 1"
        assert issues[1]["updatedAt"] == "2024-01-03T00:00:00Z"
        assert issues[2]["title"] == "Issue 2"
        assert issues[2]["updatedAt"] == "2024-01-02T00:00:00Z"

    @patch("subprocess.run")
    def test_get_issues_with_limit(self, mock_run):
        """Test that limit is respected when fetching issues"""
        repos = [{"name": "repo1", "owner": "user1"}]

        # Create 15 issues with valid timestamps (incrementing minutes)
        issues_nodes = [
            {
                "title": f"Issue {i}",
                "url": f"https://github.com/user1/repo1/issues/{i}",
                "number": i,
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": f"2024-01-01T00:{str(i).zfill(2)}:00Z",
                "author": {"login": "author"},
                "labels": {"nodes": []},
            }
            for i in range(1, 16)
        ]

        mock_response = {
            "data": {
                "repo0": {
                    "name": "repo1",
                    "owner": {"login": "user1"},
                    "issues": {"nodes": issues_nodes},
                }
            }
        }

        mock_result = MagicMock()
        mock_result.stdout = json.dumps(mock_response)
        mock_run.return_value = mock_result

        issues = get_issues_from_repositories(repos, limit=10)

        assert len(issues) == 10

    def test_get_issues_empty_repos(self):
        """Test behavior when no repositories are provided"""
        issues = get_issues_from_repositories([], limit=10)
        assert len(issues) == 0

    @patch("subprocess.run")
    def test_get_issues_with_deleted_author(self, mock_run):
        """Test handling of issues with deleted author"""
        repos = [{"name": "repo1", "owner": "user1"}]

        mock_response = {
            "data": {
                "repo0": {
                    "name": "repo1",
                    "owner": {"login": "user1"},
                    "issues": {
                        "nodes": [
                            {
                                "title": "Issue with deleted author",
                                "url": "https://github.com/user1/repo1/issues/1",
                                "number": 1,
                                "createdAt": "2024-01-01T00:00:00Z",
                                "updatedAt": "2024-01-03T00:00:00Z",
                                "author": None,  # Deleted account
                                "labels": {"nodes": []},
                            }
                        ]
                    },
                }
            }
        }

        mock_result = MagicMock()
        mock_result.stdout = json.dumps(mock_response)
        mock_run.return_value = mock_result

        issues = get_issues_from_repositories(repos, limit=10)

        assert len(issues) == 1
        assert issues[0]["author"]["login"] == "[deleted]"

    @patch("subprocess.run")
    def test_get_issues_with_labels_filter(self, mock_run):
        """Test filtering issues by labels"""
        repos = [{"name": "repo1", "owner": "user1"}]

        mock_response = {
            "data": {
                "repo0": {
                    "name": "repo1",
                    "owner": {"login": "user1"},
                    "issues": {
                        "nodes": [
                            {
                                "title": "Good First Issue",
                                "url": "https://github.com/user1/repo1/issues/1",
                                "number": 1,
                                "createdAt": "2024-01-01T00:00:00Z",
                                "updatedAt": "2024-01-03T00:00:00Z",
                                "author": {"login": "author1"},
                                "labels": {"nodes": [{"name": "good first issue"}]},
                            }
                        ]
                    },
                }
            }
        }

        mock_result = MagicMock()
        mock_result.stdout = json.dumps(mock_response)
        mock_run.return_value = mock_result

        issues = get_issues_from_repositories(repos, limit=10, labels=["good first issue"])

        assert len(issues) == 1
        assert issues[0]["title"] == "Good First Issue"
        assert "good first issue" in issues[0]["labels"]


class TestAssignIssueToCopilot:
    """Tests for assign_issue_to_copilot function"""

    @patch("webbrowser.open")
    def test_successful_assignment(self, mock_browser_open):
        """Test successful issue browser opening"""
        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
            "url": "https://github.com/test-owner/test-repo/issues/123",
        }

        result = assign_issue_to_copilot(issue)

        assert result is True
        mock_browser_open.assert_called_once_with("https://github.com/test-owner/test-repo/issues/123")

    @patch("webbrowser.open")
    def test_failed_assignment(self, mock_browser_open):
        """Test failed assignment (browser open exception)"""
        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
            "url": "https://github.com/test-owner/test-repo/issues/123",
        }

        mock_browser_open.side_effect = Exception("Browser error")

        result = assign_issue_to_copilot(issue)

        assert result is False

    def test_missing_url_field(self):
        """Test validation of missing URL field"""
        # Missing 'url' field
        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
        }
        assert assign_issue_to_copilot(issue) is False
