"""
Tests for issue fetching functionality
"""

import json
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

    @patch("subprocess.run")
    def test_get_issues_sorted_by_number(self, mock_run):
        """Test sorting issues by issue number in ascending order"""
        repos = [{"name": "repo1", "owner": "user1"}]

        mock_response = {
            "data": {
                "repo0": {
                    "name": "repo1",
                    "owner": {"login": "user1"},
                    "issues": {
                        "nodes": [
                            {
                                "title": "Issue 10",
                                "url": "https://github.com/user1/repo1/issues/10",
                                "number": 10,
                                "createdAt": "2024-01-10T00:00:00Z",
                                "updatedAt": "2024-01-15T00:00:00Z",
                                "author": {"login": "author1"},
                                "labels": {"nodes": []},
                            },
                            {
                                "title": "Issue 5",
                                "url": "https://github.com/user1/repo1/issues/5",
                                "number": 5,
                                "createdAt": "2024-01-05T00:00:00Z",
                                "updatedAt": "2024-01-10T00:00:00Z",
                                "author": {"login": "author2"},
                                "labels": {"nodes": []},
                            },
                            {
                                "title": "Issue 20",
                                "url": "https://github.com/user1/repo1/issues/20",
                                "number": 20,
                                "createdAt": "2024-01-20T00:00:00Z",
                                "updatedAt": "2024-01-20T00:00:00Z",
                                "author": {"login": "author3"},
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

        # Test with sort_by_number=True - should return issue with lowest number first
        issues = get_issues_from_repositories(repos, limit=10, sort_by_number=True)

        assert len(issues) == 3
        # Issues should be sorted by number in ascending order
        assert issues[0]["number"] == 5
        assert issues[0]["title"] == "Issue 5"
        assert issues[1]["number"] == 10
        assert issues[1]["title"] == "Issue 10"
        assert issues[2]["number"] == 20
        assert issues[2]["title"] == "Issue 20"

    @patch("subprocess.run")
    def test_get_issues_default_sorting_by_updated_at(self, mock_run):
        """Test default sorting by updatedAt in descending order"""
        repos = [{"name": "repo1", "owner": "user1"}]

        mock_response = {
            "data": {
                "repo0": {
                    "name": "repo1",
                    "owner": {"login": "user1"},
                    "issues": {
                        "nodes": [
                            {
                                "title": "Issue 10",
                                "url": "https://github.com/user1/repo1/issues/10",
                                "number": 10,
                                "createdAt": "2024-01-10T00:00:00Z",
                                "updatedAt": "2024-01-15T00:00:00Z",
                                "author": {"login": "author1"},
                                "labels": {"nodes": []},
                            },
                            {
                                "title": "Issue 5",
                                "url": "https://github.com/user1/repo1/issues/5",
                                "number": 5,
                                "createdAt": "2024-01-05T00:00:00Z",
                                "updatedAt": "2024-01-10T00:00:00Z",
                                "author": {"login": "author2"},
                                "labels": {"nodes": []},
                            },
                            {
                                "title": "Issue 20",
                                "url": "https://github.com/user1/repo1/issues/20",
                                "number": 20,
                                "createdAt": "2024-01-20T00:00:00Z",
                                "updatedAt": "2024-01-20T00:00:00Z",
                                "author": {"login": "author3"},
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

        # Test with sort_by_number=False (default) - should return issue with latest update first
        issues = get_issues_from_repositories(repos, limit=10, sort_by_number=False)

        assert len(issues) == 3
        # Issues should be sorted by updatedAt in descending order
        assert issues[0]["number"] == 20
        assert issues[0]["title"] == "Issue 20"
        assert issues[1]["number"] == 10
        assert issues[1]["title"] == "Issue 10"
        assert issues[2]["number"] == 5
        assert issues[2]["title"] == "Issue 5"


class TestAssignIssueToCopilot:
    """Tests for assign_issue_to_copilot function"""

    @patch("webbrowser.open")
    def test_successful_assignment(self, mock_browser_open):
        """Test successful issue browser opening"""
        mock_browser_open.return_value = True
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

    @patch("webbrowser.open")
    def test_browser_open_returns_false(self, mock_browser_open):
        """Test when webbrowser.open returns False"""
        mock_browser_open.return_value = False
        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
            "url": "https://github.com/test-owner/test-repo/issues/123",
        }

        result = assign_issue_to_copilot(issue)

        assert result is False
        mock_browser_open.assert_called_once_with("https://github.com/test-owner/test-repo/issues/123")

    def test_missing_url_field(self):
        """Test validation of missing URL field"""
        # Missing 'url' field
        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
        }
        assert assign_issue_to_copilot(issue) is False

    @patch("src.gh_pr_phase_monitor.issue_fetcher.assign_issue_to_copilot_automated")
    @patch("src.gh_pr_phase_monitor.issue_fetcher.is_selenium_available")
    def test_automated_mode_when_selenium_available(self, mock_selenium_available, mock_automated_func):
        """Test automated mode when Selenium is available and config.automated=true"""
        mock_selenium_available.return_value = True
        mock_automated_func.return_value = True

        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
            "url": "https://github.com/test-owner/test-repo/issues/123",
        }
        config = {
            "assign_to_copilot": {
                "automated": True,
                "wait_seconds": 5,
                "browser": "edge"
            }
        }

        result = assign_issue_to_copilot(issue, config)

        assert result is True
        mock_selenium_available.assert_called_once()
        mock_automated_func.assert_called_once_with(
            "https://github.com/test-owner/test-repo/issues/123",
            config
        )

    @patch("webbrowser.open")
    @patch("src.gh_pr_phase_monitor.issue_fetcher.is_selenium_available")
    def test_fallback_to_manual_when_selenium_unavailable(self, mock_selenium_available, mock_browser_open):
        """Test fallback to manual mode when Selenium is unavailable despite config.automated=true"""
        mock_selenium_available.return_value = False
        mock_browser_open.return_value = True

        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
            "url": "https://github.com/test-owner/test-repo/issues/123",
        }
        config = {
            "assign_to_copilot": {
                "automated": True,
                "wait_seconds": 5,
            }
        }

        result = assign_issue_to_copilot(issue, config)

        assert result is True
        mock_selenium_available.assert_called_once()
        # Should fall back to manual mode (webbrowser.open)
        mock_browser_open.assert_called_once_with("https://github.com/test-owner/test-repo/issues/123")

    @patch("webbrowser.open")
    def test_behavior_when_config_is_none(self, mock_browser_open):
        """Test behavior when config parameter is None (uses manual mode)"""
        mock_browser_open.return_value = True

        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
            "url": "https://github.com/test-owner/test-repo/issues/123",
        }

        result = assign_issue_to_copilot(issue, None)

        assert result is True
        mock_browser_open.assert_called_once_with("https://github.com/test-owner/test-repo/issues/123")

    @patch("webbrowser.open")
    def test_manual_mode_when_automated_is_false(self, mock_browser_open):
        """Test manual mode when config.automated=false"""
        mock_browser_open.return_value = True

        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
            "url": "https://github.com/test-owner/test-repo/issues/123",
        }
        config = {
            "assign_to_copilot": {
                "automated": False,
            }
        }

        result = assign_issue_to_copilot(issue, config)

        assert result is True
        mock_browser_open.assert_called_once_with("https://github.com/test-owner/test-repo/issues/123")
