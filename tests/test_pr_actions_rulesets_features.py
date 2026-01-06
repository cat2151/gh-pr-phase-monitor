"""
Tests for PR actions with ruleset-based phase3_merge and assign_to_copilot configuration
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor import pr_actions
from src.gh_pr_phase_monitor.pr_actions import process_pr


class TestProcessPRWithRulesetPhase3Merge:
    """Test process_pr function with ruleset-based phase3_merge configuration"""

    def setup_method(self):
        """Clear tracking before each test"""
        pr_actions._browser_opened.clear()
        pr_actions._notifications_sent.clear()
        pr_actions._merged_prs.clear()

    def test_ruleset_phase3_merge_for_specific_repo(self):
        """Ruleset should apply specific phase3_merge settings for a repository"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "phase3_merge": {
                "enabled": False,
                "comment": "Global comment",
            },
            "enable_execution_phase3_to_merge": False,
            "rulesets": [
                {
                    "name": "Enable merge for test-repo",
                    "repositories": ["test-owner/test-repo"],
                    "enable_execution_phase3_to_merge": True,
                    "phase3_merge": {
                        "enabled": True,
                        "comment": "Ruleset merge comment",
                        "automated": False,
                    }
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_merge.return_value = True
            mock_comment.return_value = True
            process_pr(pr, config)
            
            # Comment should use ruleset comment
            mock_comment.assert_called_once_with(pr, "Ruleset merge comment", None)
            # Merge should be attempted
            mock_merge.assert_called_once()

    def test_different_repos_different_merge_configs(self):
        """Different repositories should get different phase3_merge configurations"""
        pr1 = {
            "isDraft": False,
            "reviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "repo1", "owner": "owner"},
            "title": "PR 1",
            "url": "https://github.com/owner/repo1/pull/1",
        }
        pr2 = {
            "isDraft": False,
            "reviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "repo2", "owner": "owner"},
            "title": "PR 2",
            "url": "https://github.com/owner/repo2/pull/2",
        }
        config = {
            "phase3_merge": {"enabled": False},
            "enable_execution_phase3_to_merge": False,
            "rulesets": [
                {
                    "repositories": ["owner/repo1"],
                    "enable_execution_phase3_to_merge": True,
                    "phase3_merge": {
                        "enabled": True,
                        "comment": "Comment for repo1",
                    }
                },
                {
                    "repositories": ["owner/repo2"],
                    "enable_execution_phase3_to_merge": True,
                    "phase3_merge": {
                        "enabled": True,
                        "comment": "Comment for repo2",
                    }
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_merge.return_value = True
            mock_comment.return_value = True
            
            # Process PR 1
            process_pr(pr1, config)
            assert mock_comment.call_count == 1
            assert mock_comment.call_args[0][1] == "Comment for repo1"
            
            # Reset mocks
            mock_comment.reset_mock()
            mock_merge.reset_mock()
            
            # Process PR 2
            process_pr(pr2, config)
            assert mock_comment.call_count == 1
            assert mock_comment.call_args[0][1] == "Comment for repo2"

    def test_ruleset_automated_merge_setting(self):
        """Ruleset should apply automated merge setting per repository"""
        pr = {
            "isDraft": False,
            "reviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "phase3_merge": {
                "enabled": False,
                "automated": False,
            },
            "enable_execution_phase3_to_merge": False,
            "rulesets": [
                {
                    "repositories": ["test-owner/test-repo"],
                    "enable_execution_phase3_to_merge": True,
                    "phase3_merge": {
                        "enabled": True,
                        "comment": "Automated merge",
                        "automated": True,
                    }
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr_automated"
        ) as mock_merge_auto, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_merge_auto.return_value = True
            mock_comment.return_value = True
            process_pr(pr, config)
            
            # Should use automated merge
            mock_merge_auto.assert_called_once()
            # The config passed should contain the resolved phase3_merge settings
            call_args = mock_merge_auto.call_args
            assert call_args[0][0] == "https://github.com/test-owner/test-repo/pull/1"
            passed_config = call_args[0][1]
            assert passed_config["phase3_merge"]["automated"] is True

    def test_no_merge_when_ruleset_disables_execution(self):
        """Merge should not happen when ruleset disables execution flag"""
        pr = {
            "isDraft": False,
            "reviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "phase3_merge": {"enabled": True},
            "enable_execution_phase3_to_merge": True,
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_execution_phase3_to_merge": True,
                    "phase3_merge": {"enabled": True},
                },
                {
                    "repositories": ["test-owner/test-repo"],
                    "enable_execution_phase3_to_merge": False,  # Disable for this repo
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            process_pr(pr, config)
            # Merge should not be attempted
            mock_merge.assert_not_called()
            mock_comment.assert_not_called()

    def test_partial_phase3_merge_override_in_ruleset(self):
        """Ruleset can partially override phase3_merge settings"""
        pr = {
            "isDraft": False,
            "reviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "phase3_merge": {
                "enabled": True,
                "comment": "Global comment",
                "automated": False,
                "wait_seconds": 10,
                "browser": "edge",
            },
            "enable_execution_phase3_to_merge": True,
            "rulesets": [
                {
                    "repositories": ["test-owner/test-repo"],
                    "phase3_merge": {
                        "comment": "Overridden comment",
                    }
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_merge.return_value = True
            mock_comment.return_value = True
            process_pr(pr, config)
            
            # Should use overridden comment
            mock_comment.assert_called_once_with(pr, "Overridden comment", None)
            # Other settings preserved from global
            mock_merge.assert_called_once()
