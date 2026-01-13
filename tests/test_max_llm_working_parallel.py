"""
Test to verify the max_llm_working_parallel feature

This test ensures that auto-assignment of issues is paused when the number
of PRs in "LLM working" state reaches the configured maximum parallel limit.
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor.main import display_issues_from_repos_without_prs


def test_assignment_paused_when_limit_reached():
    """
    Test that assignment is paused when LLM working count reaches the limit
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

                # Mock issue response - only for displaying issues
                mock_get_issues.side_effect = [
                    # Only call: top 10 issues (no assignment call should happen)
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

                # Create config with assign_to_copilot enabled via rulesets
                # and max_llm_working_parallel set to 3
                config = {
                    "assign_to_copilot": {},
                    "max_llm_working_parallel": 3,
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_good_first_old": True,
                        }
                    ],
                }

                # Call with llm_working_count = 3 (at the limit)
                display_issues_from_repos_without_prs(config, llm_working_count=3)

                # Verify that assignment was NOT attempted (limit reached)
                mock_assign.assert_not_called()

                # Verify that issues were only fetched once (for display, not for assignment)
                assert mock_get_issues.call_count == 1


def test_assignment_proceeds_when_below_limit():
    """
    Test that assignment proceeds when LLM working count is below the limit
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

                # Mock issue response
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
                    ],
                ]

                mock_assign.return_value = True

                # Create config with assign_to_copilot enabled via rulesets
                # and max_llm_working_parallel set to 3
                config = {
                    "assign_to_copilot": {},
                    "max_llm_working_parallel": 3,
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_good_first_old": True,
                        }
                    ],
                }

                # Call with llm_working_count = 2 (below the limit)
                display_issues_from_repos_without_prs(config, llm_working_count=2)

                # Verify that assignment WAS attempted (below limit)
                mock_assign.assert_called_once()

                # Verify that issues were fetched twice (assignment + display)
                assert mock_get_issues.call_count == 2


def test_default_limit_when_not_configured():
    """
    Test that the default limit (3) is used when not configured
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

                # Mock issue response - only for displaying issues
                mock_get_issues.side_effect = [
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

                # Create config WITHOUT max_llm_working_parallel (should use default of 3)
                config = {
                    "assign_to_copilot": {},
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_good_first_old": True,
                        }
                    ],
                }

                # Call with llm_working_count = 3 (at the default limit)
                display_issues_from_repos_without_prs(config, llm_working_count=3)

                # Verify that assignment was NOT attempted (default limit reached)
                mock_assign.assert_not_called()


def test_custom_limit():
    """
    Test that custom max_llm_working_parallel values are respected
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

                # Mock issue response
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
                    ],
                ]

                mock_assign.return_value = True

                # Create config with custom max_llm_working_parallel of 5
                config = {
                    "assign_to_copilot": {},
                    "max_llm_working_parallel": 5,
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_good_first_old": True,
                        }
                    ],
                }

                # Call with llm_working_count = 4 (below custom limit of 5)
                display_issues_from_repos_without_prs(config, llm_working_count=4)

                # Verify that assignment WAS attempted (below custom limit)
                mock_assign.assert_called_once()


def test_invalid_limit_uses_default():
    """
    Test that invalid max_llm_working_parallel values fall back to default
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

                # Mock issue response - only for displaying issues
                mock_get_issues.side_effect = [
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

                # Create config with INVALID max_llm_working_parallel (string instead of int)
                config = {
                    "assign_to_copilot": {},
                    "max_llm_working_parallel": "invalid",  # Invalid type
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_good_first_old": True,
                        }
                    ],
                }

                # Call with llm_working_count = 3 (at the default limit)
                display_issues_from_repos_without_prs(config, llm_working_count=3)

                # Verify that assignment was NOT attempted (default limit used)
                mock_assign.assert_not_called()


def test_zero_llm_working_count():
    """
    Test that assignment proceeds when llm_working_count is 0
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

                # Mock issue response
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
                    ],
                ]

                mock_assign.return_value = True

                # Create config
                config = {
                    "assign_to_copilot": {},
                    "max_llm_working_parallel": 3,
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_good_first_old": True,
                        }
                    ],
                }

                # Call with llm_working_count = 0 (well below limit)
                display_issues_from_repos_without_prs(config, llm_working_count=0)

                # Verify that assignment WAS attempted
                mock_assign.assert_called_once()


def test_config_validation_at_load_time():
    """
    Test that invalid max_llm_working_parallel values are validated when config is loaded
    """
    import tempfile
    import os
    from src.gh_pr_phase_monitor.config import load_config, DEFAULT_MAX_LLM_WORKING_PARALLEL

    # Test invalid string value
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write('max_llm_working_parallel = "invalid"\n')
        f.flush()
        config = load_config(f.name)
        assert config['max_llm_working_parallel'] == DEFAULT_MAX_LLM_WORKING_PARALLEL
        os.unlink(f.name)

    # Test zero value
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write('max_llm_working_parallel = 0\n')
        f.flush()
        config = load_config(f.name)
        assert config['max_llm_working_parallel'] == DEFAULT_MAX_LLM_WORKING_PARALLEL
        os.unlink(f.name)

    # Test negative value
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write('max_llm_working_parallel = -1\n')
        f.flush()
        config = load_config(f.name)
        assert config['max_llm_working_parallel'] == DEFAULT_MAX_LLM_WORKING_PARALLEL
        os.unlink(f.name)

    # Test valid value is preserved
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write('max_llm_working_parallel = 5\n')
        f.flush()
        config = load_config(f.name)
        assert config['max_llm_working_parallel'] == 5
        os.unlink(f.name)


if __name__ == "__main__":
    test_assignment_paused_when_limit_reached()
    print("✓ Test 1 passed: assignment_paused_when_limit_reached")

    test_assignment_proceeds_when_below_limit()
    print("✓ Test 2 passed: assignment_proceeds_when_below_limit")

    test_default_limit_when_not_configured()
    print("✓ Test 3 passed: default_limit_when_not_configured")

    test_custom_limit()
    print("✓ Test 4 passed: custom_limit")

    test_invalid_limit_uses_default()
    print("✓ Test 5 passed: invalid_limit_uses_default")

    test_zero_llm_working_count()
    print("✓ Test 6 passed: zero_llm_working_count")

    test_config_validation_at_load_time()
    print("✓ Test 7 passed: config_validation_at_load_time")

    print("\n✅ All tests passed!")
