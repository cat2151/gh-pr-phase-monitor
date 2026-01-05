"""
Test to verify that issues are displayed when no repositories with open PRs are found

This test ensures the new behavior requested in the issue:
"Add the condition 'No repositories with open PRs found' to the conditions for displaying the latest issue."
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor.main import display_issues_from_repos_without_prs


def test_display_issues_when_no_repos_with_prs():
    """
    Test that display_issues_from_repos_without_prs correctly displays issues
    when there are no repositories with open PRs
    """
    with patch("src.gh_pr_phase_monitor.main.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.main.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.main.assign_issue_to_copilot") as mock_assign:
                # Mock response: repos with no PRs but with issues
                mock_get_repos.return_value = [
                    {
                        "name": "test-repo",
                        "owner": "testuser",
                        "openIssueCount": 2,
                    }
                ]

                # Mock good first issue response
                mock_get_issues.side_effect = [
                    # First call: good first issue
                    [
                        {
                            "title": "Good first issue",
                            "url": "https://github.com/testuser/test-repo/issues/1",
                            "number": 1,
                            "updatedAt": "2024-01-01T00:00:00Z",
                            "author": {"login": "contributor1"},
                            "repository": {"owner": "testuser", "name": "test-repo"},
                            "labels": ["good first issue"],
                        }
                    ],
                    # Second call: top 10 issues
                    [
                        {
                            "title": "Issue 1",
                            "url": "https://github.com/testuser/test-repo/issues/1",
                            "number": 1,
                            "updatedAt": "2024-01-01T00:00:00Z",
                            "author": {"login": "contributor1"},
                            "repository": {"owner": "testuser", "name": "test-repo"},
                        },
                        {
                            "title": "Issue 2",
                            "url": "https://github.com/testuser/test-repo/issues/2",
                            "number": 2,
                            "updatedAt": "2024-01-02T00:00:00Z",
                            "author": {"login": "contributor2"},
                            "repository": {"owner": "testuser", "name": "test-repo"},
                        },
                    ],
                ]

                mock_assign.return_value = True

                # Create config with assign_to_copilot enabled
                config = {"assign_to_copilot": {"enabled": True}}

                # Call the function with config
                display_issues_from_repos_without_prs(config)

                # Verify that the function fetched repos without PRs
                mock_get_repos.assert_called_once()

                # Verify that issues were fetched twice (good first issue + top 10)
                assert mock_get_issues.call_count == 2

                # Verify first call was for good first issue
                first_call = mock_get_issues.call_args_list[0]
                assert first_call[1]["limit"] == 1
                assert first_call[1]["labels"] == ["good first issue"]

                # Verify second call was for top 10 issues
                second_call = mock_get_issues.call_args_list[1]
                assert second_call[1]["limit"] == 10

                # Verify assignment was attempted
                mock_assign.assert_called_once()


def test_display_issues_when_no_repos_with_issues():
    """
    Test that display_issues_from_repos_without_prs handles the case
    when there are no repositories with issues
    """
    with patch("src.gh_pr_phase_monitor.main.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        # Mock response: no repos with issues
        mock_get_repos.return_value = []

        # Call the function with empty config - should not raise an error
        display_issues_from_repos_without_prs({})

        # Verify that the function fetched repos without PRs
        mock_get_repos.assert_called_once()


def test_display_issues_handles_exceptions():
    """
    Test that display_issues_from_repos_without_prs handles exceptions gracefully
    """
    with patch("src.gh_pr_phase_monitor.main.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        # Mock an exception
        mock_get_repos.side_effect = Exception("API Error")

        # Call the function with empty config - should not raise an error
        display_issues_from_repos_without_prs({})

        # Verify that the function attempted to fetch repos
        mock_get_repos.assert_called_once()


def test_display_issues_with_assign_disabled():
    """
    Test that display_issues_from_repos_without_prs does NOT attempt assignment
    when the feature is disabled
    """
    with patch("src.gh_pr_phase_monitor.main.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.main.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.main.assign_issue_to_copilot") as mock_assign:
                # Mock response: repos with no PRs but with issues
                mock_get_repos.return_value = [
                    {
                        "name": "test-repo",
                        "owner": "testuser",
                        "openIssueCount": 2,
                    }
                ]

                # Mock good first issue response - but it should never be called
                mock_get_issues.side_effect = [
                    # Only the second call (top 10 issues) should be made
                    [
                        {
                            "title": "Issue 1",
                            "url": "https://github.com/testuser/test-repo/issues/1",
                            "number": 1,
                            "updatedAt": "2024-01-01T00:00:00Z",
                            "author": {"login": "contributor1"},
                            "repository": {"owner": "testuser", "name": "test-repo"},
                        },
                    ],
                ]

                # Create config with assign_to_copilot disabled (or missing)
                config = {"assign_to_copilot": {"enabled": False}}

                # Call the function with config
                display_issues_from_repos_without_prs(config)

                # Verify that the function fetched repos without PRs
                mock_get_repos.assert_called_once()

                # Verify that only one issue fetch was made (top 10, not good first issue)
                assert mock_get_issues.call_count == 1

                # Verify assignment was NOT attempted
                mock_assign.assert_not_called()


def test_display_issues_with_custom_limit():
    """
    Test that display_issues_from_repos_without_prs respects the issue_display_limit config
    """
    with patch("src.gh_pr_phase_monitor.main.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.main.get_issues_from_repositories") as mock_get_issues:
            # Mock response: repos with no PRs but with issues
            mock_get_repos.return_value = [
                {
                    "name": "test-repo",
                    "owner": "testuser",
                    "openIssueCount": 10,
                }
            ]

            # Mock issue response
            mock_get_issues.return_value = [
                {
                    "title": f"Issue {i}",
                    "url": f"https://github.com/testuser/test-repo/issues/{i}",
                    "number": i,
                    "updatedAt": f"2024-01-{i:02d}T00:00:00Z",
                    "author": {"login": "contributor1"},
                    "repository": {"owner": "testuser", "name": "test-repo"},
                }
                for i in range(1, 6)
            ]

            # Create config with custom issue_display_limit
            config = {"assign_to_copilot": {"enabled": False}, "issue_display_limit": 5}

            # Call the function with config
            display_issues_from_repos_without_prs(config)

            # Verify that the function fetched repos without PRs
            mock_get_repos.assert_called_once()

            # Verify that issues were fetched with the custom limit
            mock_get_issues.assert_called_once()
            call_args = mock_get_issues.call_args
            assert call_args[1]["limit"] == 5


def test_display_issues_with_none_config():
    """
    Test that display_issues_from_repos_without_prs handles None config gracefully
    """
    with patch("src.gh_pr_phase_monitor.main.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.main.get_issues_from_repositories") as mock_get_issues:
            # Mock response: repos with no PRs but with issues
            mock_get_repos.return_value = [
                {
                    "name": "test-repo",
                    "owner": "testuser",
                    "openIssueCount": 10,
                }
            ]

            # Mock issue response
            mock_get_issues.return_value = [
                {
                    "title": f"Issue {i}",
                    "url": f"https://github.com/testuser/test-repo/issues/{i}",
                    "number": i,
                    "updatedAt": f"2024-01-{i:02d}T00:00:00Z",
                    "author": {"login": "contributor1"},
                    "repository": {"owner": "testuser", "name": "test-repo"},
                }
                for i in range(1, 11)
            ]

            # Call the function with None config - should use default limit of 10
            display_issues_from_repos_without_prs(None)

            # Verify that the function fetched repos without PRs
            mock_get_repos.assert_called_once()

            # Verify that issues were fetched with the default limit of 10
            mock_get_issues.assert_called_once()
            call_args = mock_get_issues.call_args
            assert call_args[1]["limit"] == 10


if __name__ == "__main__":
    test_display_issues_when_no_repos_with_prs()
    print("✓ Test 1 passed: display_issues_when_no_repos_with_prs")

    test_display_issues_when_no_repos_with_issues()
    print("✓ Test 2 passed: display_issues_when_no_repos_with_issues")

    test_display_issues_handles_exceptions()
    print("✓ Test 3 passed: display_issues_handles_exceptions")

    test_display_issues_with_assign_disabled()
    print("✓ Test 4 passed: display_issues_with_assign_disabled")

    test_display_issues_with_custom_limit()
    print("✓ Test 5 passed: display_issues_with_custom_limit")

    test_display_issues_with_none_config()
    print("✓ Test 6 passed: display_issues_with_none_config")

    print("\n✅ All tests passed!")
