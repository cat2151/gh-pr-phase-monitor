"""
Tests for PR actions with ruleset-based configuration
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor import pr_actions
from src.gh_pr_phase_monitor.pr_actions import process_pr


class TestProcessPRWithRulesets:
    """Test process_pr function with ruleset-based configuration"""

    def setup_method(self):
        """Clear tracking before each test"""
        pr_actions._browser_opened.clear()
        pr_actions._notifications_sent.clear()

    def test_ruleset_enables_phase1_for_specific_repo(self):
        """Ruleset should enable phase1 execution for specific repository"""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "enable_execution_phase1_to_phase2": False,  # Global is disabled
            "rulesets": [
                {
                    "name": "Enable for test-repo",
                    "repositories": ["test-repo"],
                    "enable_execution_phase1_to_phase2": True,
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready:
            mock_ready.return_value = True
            process_pr(pr, config)
            # Should be called because ruleset enables it for this repo
            mock_ready.assert_called_once_with("https://github.com/test-owner/test-repo/pull/1", None)

    def test_ruleset_disables_phase1_for_specific_repo(self):
        """Ruleset should disable phase1 execution for specific repository"""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "enable_execution_phase1_to_phase2": True,  # Global is enabled
            "rulesets": [
                {
                    "name": "Enable for all",
                    "repositories": ["all"],
                    "enable_execution_phase1_to_phase2": True,
                },
                {
                    "name": "Disable for test-repo",
                    "repositories": ["test-repo"],
                    "enable_execution_phase1_to_phase2": False,
                },
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready:
            process_pr(pr, config)
            # Should not be called because ruleset disables it for this repo
            mock_ready.assert_not_called()

    def test_all_ruleset_applies_to_all_repositories(self):
        """Ruleset with 'all' should apply to any repository"""
        pr1 = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "repo1", "owner": "owner1"},
            "title": "Test PR 1",
            "url": "https://github.com/owner1/repo1/pull/1",
        }
        pr2 = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "repo2", "owner": "owner2"},
            "title": "Test PR 2",
            "url": "https://github.com/owner2/repo2/pull/1",
        }
        config = {
            "enable_execution_phase1_to_phase2": False,
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_execution_phase1_to_phase2": True,
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready:
            mock_ready.return_value = True
            
            process_pr(pr1, config)
            assert mock_ready.call_count == 1
            
            process_pr(pr2, config)
            assert mock_ready.call_count == 2

    def test_repository_name_only_matching(self):
        """Ruleset should match by repository name only"""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "test-repo", "owner": "any-owner"},
            "title": "Test PR",
            "url": "https://github.com/any-owner/test-repo/pull/1",
        }
        config = {
            "enable_execution_phase1_to_phase2": False,
            "rulesets": [
                {
                    "repositories": ["test-repo"],  # Just repo name, no owner
                    "enable_execution_phase1_to_phase2": True,
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready:
            mock_ready.return_value = True
            process_pr(pr, config)
            mock_ready.assert_called_once()

    def test_ruleset_applies_to_phase2(self):
        """Ruleset should control phase2 execution"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "CHANGES_REQUESTED",
                    "body": "Please fix",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "CHANGES_REQUESTED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "enable_execution_phase2_to_phase3": False,
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase2_to_phase3": True,
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.post_phase2_comment") as mock_comment:
            mock_comment.return_value = True
            process_pr(pr, config)
            mock_comment.assert_called_once()

    def test_ruleset_applies_to_phase3(self):
        """Ruleset should control phase3 notification execution"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED", "body": "Looks good!"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "ntfy": {"enabled": True, "topic": "test-topic"},
            "enable_execution_phase3_send_ntfy": False,
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_send_ntfy": True,
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.send_phase3_notification"
        ) as mock_notify:
            mock_notify.return_value = True
            process_pr(pr, config)
            mock_notify.assert_called_once()

    def test_multiple_rulesets_with_override(self):
        """Later rulesets should override earlier ones"""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "special-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/special-repo/pull/1",
        }
        config = {
            "enable_execution_phase1_to_phase2": False,
            "rulesets": [
                {
                    "name": "Enable for all",
                    "repositories": ["all"],
                    "enable_execution_phase1_to_phase2": True,
                },
                {
                    "name": "Disable for special-repo",
                    "repositories": ["special-repo"],
                    "enable_execution_phase1_to_phase2": False,
                },
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready:
            process_pr(pr, config)
            # Should not be called because second ruleset overrides first
            mock_ready.assert_not_called()

    def test_different_repos_get_different_config(self):
        """Different repositories should get different configurations from rulesets"""
        pr_enabled = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "enabled-repo", "owner": "test-owner"},
            "title": "Test PR Enabled",
            "url": "https://github.com/test-owner/enabled-repo/pull/1",
        }
        pr_disabled = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "disabled-repo", "owner": "test-owner"},
            "title": "Test PR Disabled",
            "url": "https://github.com/test-owner/disabled-repo/pull/1",
        }
        config = {
            "enable_execution_phase1_to_phase2": False,
            "rulesets": [
                {
                    "repositories": ["enabled-repo"],
                    "enable_execution_phase1_to_phase2": True,
                },
                # disabled-repo not in any ruleset, uses global config (False)
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready:
            mock_ready.return_value = True
            
            # enabled-repo should execute
            process_pr(pr_enabled, config)
            assert mock_ready.call_count == 1
            
            # disabled-repo should not execute
            process_pr(pr_disabled, config)
            assert mock_ready.call_count == 1  # Still 1, not incremented

    def test_partial_config_in_ruleset(self):
        """Ruleset can specify only some execution flags"""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "enable_execution_phase1_to_phase2": True,
            "enable_execution_phase2_to_phase3": True,
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_execution_phase1_to_phase2": False,
                    # Note: enable_execution_phase2_to_phase3 not specified, should use global
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready:
            process_pr(pr, config)
            # phase1 should be disabled by ruleset
            mock_ready.assert_not_called()
