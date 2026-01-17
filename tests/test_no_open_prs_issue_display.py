"""
Test to verify that issues are displayed when no repositories with open PRs are found

This test ensures the new behavior requested in the issue:
"Add the condition 'No repositories with open PRs found' to the conditions for displaying the latest issue."
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor.display import display_issues_from_repos_without_prs


def test_display_issues_when_no_repos_with_prs():
    """
    Test that display_issues_from_repos_without_prs correctly displays issues
    when there are no repositories with open PRs
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
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

                # Create config with assign_to_copilot enabled via rulesets
                config = {
                    "assign_to_copilot": {},  # Empty section provides defaults
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_good_first_old": True,  # Enable good first issue assignment
                        }
                    ],
                }

                # Call the function with config
                display_issues_from_repos_without_prs(config)

                # Verify that the function fetched repos without PRs
                mock_get_repos.assert_called_once()

                # Verify that issues were fetched twice (good first issue + top 10)
                assert mock_get_issues.call_count == 2

                # Verify first call was for good first issue (with sort_by_number=True)
                first_call = mock_get_issues.call_args_list[0]
                assert first_call[1]["limit"] == 1
                assert first_call[1]["labels"] == ["good first issue"]
                assert first_call[1]["sort_by_number"] is True

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
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
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
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
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
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
                # Mock response: repos with no PRs but with issues
                mock_get_repos.return_value = [
                    {
                        "name": "test-repo",
                        "owner": "testuser",
                        "openIssueCount": 2,
                    }
                ]

                # Mock issue responses - only one call now for displaying issues
                mock_get_issues.side_effect = [
                    # Only call for top 10 issues
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

                # Create config without rulesets enabling assign flags
                config = {"assign_to_copilot": {}}  # Defaults available, but no ruleset enables it

                # Call the function with config
                display_issues_from_repos_without_prs(config)

                # Verify that the function fetched repos without PRs
                mock_get_repos.assert_called_once()

                # Verify that issues were fetched only once (top 10), no assign attempt
                assert mock_get_issues.call_count == 1

                # Verify assignment was NOT attempted (no ruleset enabling it)
                mock_assign.assert_not_called()


def test_display_issues_with_custom_limit():
    """
    Test that display_issues_from_repos_without_prs respects the issue_display_limit config
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            # Mock response: repos with no PRs but with issues
            mock_get_repos.return_value = [
                {
                    "name": "test-repo",
                    "owner": "testuser",
                    "openIssueCount": 10,
                }
            ]

            # Mock issue response - only display issues call
            mock_get_issues.side_effect = [
                # Only call: top N issues with custom limit
                [
                    {
                        "title": f"Issue {i}",
                        "url": f"https://github.com/testuser/test-repo/issues/{i}",
                        "number": i,
                        "updatedAt": f"2024-01-{i:02d}T00:00:00Z",
                        "author": {"login": "contributor1"},
                        "repository": {"owner": "testuser", "name": "test-repo"},
                    }
                    for i in range(1, 6)
                ],
            ]

            # Create config with custom issue_display_limit, no assign flags
            config = {"assign_to_copilot": {}, "issue_display_limit": 5}

            # Call the function with config
            display_issues_from_repos_without_prs(config)

            # Verify that the function fetched repos without PRs
            mock_get_repos.assert_called_once()

            # Verify that issues were fetched once (top N only, no auto-assign)
            assert mock_get_issues.call_count == 1
            # Check the call used the custom limit
            call = mock_get_issues.call_args_list[0]
            assert call[1]["limit"] == 5


def test_display_issues_with_none_config():
    """
    Test that display_issues_from_repos_without_prs handles None config gracefully
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            # Mock response: repos with no PRs but with issues
            mock_get_repos.return_value = [
                {
                    "name": "test-repo",
                    "owner": "testuser",
                    "openIssueCount": 10,
                }
            ]

            # Mock issue response - only display issues
            mock_get_issues.side_effect = [
                # Only call: top 10 issues
                [
                    {
                        "title": f"Issue {i}",
                        "url": f"https://github.com/testuser/test-repo/issues/{i}",
                        "number": i,
                        "updatedAt": f"2024-01-{i:02d}T00:00:00Z",
                        "author": {"login": "contributor1"},
                        "repository": {"owner": "testuser", "name": "test-repo"},
                    }
                    for i in range(1, 11)
                ],
            ]

            # Call the function with None config - should use default limit of 10
            display_issues_from_repos_without_prs(None)

            # Verify that the function fetched repos without PRs
            mock_get_repos.assert_called_once()

            # Verify that issues were fetched once (top 10 only, no assign)
            assert mock_get_issues.call_count == 1
            # Check the call used the default limit of 10
            call = mock_get_issues.call_args_list[0]
            assert call[1]["limit"] == 10


def test_display_issues_with_assign_lowest_number():
    """
    Test that display_issues_from_repos_without_prs correctly assigns the oldest issue
    when assign_old is enabled (replaces assign_lowest_number_issue)
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
                # Mock response: repos with no PRs but with issues
                mock_get_repos.return_value = [
                    {
                        "name": "test-repo",
                        "owner": "testuser",
                        "openIssueCount": 3,
                    }
                ]

                # Mock lowest number issue response
                mock_get_issues.side_effect = [
                    # First call: oldest issue
                    [
                        {
                            "title": "Issue with lowest number",
                            "url": "https://github.com/testuser/test-repo/issues/5",
                            "number": 5,
                            "updatedAt": "2024-01-05T00:00:00Z",
                            "author": {"login": "contributor1"},
                            "repository": {"owner": "testuser", "name": "test-repo"},
                            "labels": ["bug"],
                        }
                    ],
                    # Second call: top 10 issues
                    [
                        {
                            "title": "Issue 1",
                            "url": "https://github.com/testuser/test-repo/issues/5",
                            "number": 5,
                            "updatedAt": "2024-01-05T00:00:00Z",
                            "author": {"login": "contributor1"},
                            "repository": {"owner": "testuser", "name": "test-repo"},
                        },
                        {
                            "title": "Issue 2",
                            "url": "https://github.com/testuser/test-repo/issues/10",
                            "number": 10,
                            "updatedAt": "2024-01-10T00:00:00Z",
                            "author": {"login": "contributor2"},
                            "repository": {"owner": "testuser", "name": "test-repo"},
                        },
                    ],
                ]

                mock_assign.return_value = True

                # Create config with assign_old enabled in rulesets
                config = {
                    "assign_to_copilot": {},
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_old": True,  # Enable old issue assignment
                        }
                    ],
                }

                # Call the function with config
                display_issues_from_repos_without_prs(config)

                # Verify that the function fetched repos without PRs
                mock_get_repos.assert_called_once()

                # Verify that issues were fetched twice (oldest issue + top 10)
                assert mock_get_issues.call_count == 2

                # Verify first call was for oldest issue (with sort_by_number=True, no labels)
                first_call = mock_get_issues.call_args_list[0]
                assert first_call[1]["limit"] == 1
                assert first_call[1]["sort_by_number"] is True
                # Should not have labels filter for oldest issue mode
                assert "labels" not in first_call[1] or first_call[1]["labels"] is None

                # Verify second call was for top 10 issues
                second_call = mock_get_issues.call_args_list[1]
                assert second_call[1]["limit"] == 10

                # Verify assignment was attempted
                mock_assign.assert_called_once()


def test_assign_only_fetches_from_enabled_repos():
    """
    Test that assignment only fetches issues from repos where
    assign_good_first_old or assign_old is enabled.
    This prevents fetching issues from repos that don't have assignment enabled.
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
                # Mock response: two repos without PRs but with issues
                mock_get_repos.return_value = [
                    {"name": "repo-with-assign", "owner": "testuser", "openIssueCount": 2},
                    {"name": "repo-without-assign", "owner": "testuser", "openIssueCount": 3},
                ]

                # Mock issue response
                mock_get_issues.side_effect = [
                    # First call: good first issue (should only fetch from repo-with-assign)
                    [
                        {
                            "title": "Good first issue from enabled repo",
                            "url": "https://github.com/testuser/repo-with-assign/issues/1",
                            "number": 1,
                            "updatedAt": "2024-01-01T00:00:00Z",
                            "author": {"login": "contributor1"},
                            "repository": {"owner": "testuser", "name": "repo-with-assign"},
                            "labels": ["good first issue"],
                        }
                    ],
                    # Second call: top 10 issues
                    [],
                ]

                mock_assign.return_value = True

                # Create config where only repo-with-assign has the assignment flag enabled
                config = {
                    "assign_to_copilot": {},
                    "rulesets": [
                        {
                            "repositories": ["repo-with-assign"],
                            "assign_good_first_old": True,
                        },
                        {
                            "repositories": ["repo-without-assign"],
                            # No assignment flags enabled
                        },
                    ],
                }

                # Call the function
                display_issues_from_repos_without_prs(config)

                # Verify that get_issues_from_repositories was called
                assert mock_get_issues.call_count == 2

                # Verify first call only included repo-with-assign
                first_call = mock_get_issues.call_args_list[0]
                repos_arg = first_call[0][0]  # First positional argument
                assert len(repos_arg) == 1
                assert repos_arg[0]["name"] == "repo-with-assign"

                # Verify assignment was attempted
                mock_assign.assert_called_once()


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

    test_display_issues_with_assign_lowest_number()
    print("✓ Test 7 passed: display_issues_with_assign_lowest_number")

    test_assign_only_fetches_from_enabled_repos()
    print("✓ Test 8 passed: test_assign_only_fetches_from_enabled_repos")

    print("\n✅ All tests passed!")
