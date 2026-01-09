"""
Tests for PR actions with ruleset-based phase3_merge on/off flags
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor import pr_actions
from src.gh_pr_phase_monitor.pr_actions import process_pr


class TestProcessPRWithRulesetPhase3MergeFlag:
    """Test process_pr function with ruleset-based phase3_merge on/off flag"""

    def setup_method(self):
        """Clear tracking before each test"""
        pr_actions._browser_opened.clear()
        pr_actions._notifications_sent.clear()
        pr_actions._merged_prs.clear()

    def test_ruleset_enables_phase3_merge_for_specific_repo(self):
        """Ruleset should enable phase3_merge using global settings for specific repository"""
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
                "enabled": True,
                "comment": "Global merge comment",
                "automated": False,
            },
            "enable_execution_phase3_to_merge": False,
            "rulesets": [
                {
                    "name": "Enable merge for test-repo",
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": True,
                    "enable_phase3_merge": True,  # Enable using global settings
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_merge.return_value = True
            mock_comment.return_value = True
            process_pr(pr, config)
            
            # Comment should use global comment
            mock_comment.assert_called_once_with(pr, "Global merge comment", None)
            # Merge should be attempted
            mock_merge.assert_called_once()

    def test_different_repos_different_merge_enabled(self):
        """Different repositories should have different enable states"""
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
            "phase3_merge": {
                "enabled": True,
                "comment": "Global comment",
            },
            "enable_execution_phase3_to_merge": False,
            "rulesets": [
                {
                    "repositories": ["repo1"],
                    "enable_execution_phase3_to_merge": True,
                    "enable_phase3_merge": True,
                },
                {
                    "repositories": ["repo2"],
                    "enable_execution_phase3_to_merge": True,
                    "enable_phase3_merge": False,  # Disabled for repo2
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_merge.return_value = True
            mock_comment.return_value = True
            
            # Process PR 1 - should merge
            process_pr(pr1, config)
            assert mock_comment.call_count == 1
            assert mock_merge.call_count == 1
            
            # Reset mocks
            mock_comment.reset_mock()
            mock_merge.reset_mock()
            
            # Process PR 2 - should not merge (enable_phase3_merge is False)
            process_pr(pr2, config)
            assert mock_comment.call_count == 0
            assert mock_merge.call_count == 0

    def test_automated_merge_uses_global_settings(self):
        """Automated merge should use global automated settings"""
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
                "comment": "Automated merge",
                "automated": True,  # Global setting for automation
            },
            "enable_execution_phase3_to_merge": False,
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": True,
                    "enable_phase3_merge": True,
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr_automated"
        ) as mock_merge_auto, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_merge_auto.return_value = True
            mock_comment.return_value = True
            process_pr(pr, config)
            
            # Should use automated merge based on global setting
            mock_merge_auto.assert_called_once()

    def test_no_merge_when_enable_phase3_merge_false(self):
        """Merge should not happen when enable_phase3_merge is false"""
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
                "comment": "Merge comment",
            },
            "enable_execution_phase3_to_merge": False,
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": True,
                    "enable_phase3_merge": False,  # Disabled for this repo
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

    def test_no_merge_when_global_phase3_merge_disabled(self):
        """Merge should not happen when global phase3_merge.enabled is false"""
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
                "enabled": False,  # Globally disabled
                "comment": "Merge comment",
            },
            "enable_execution_phase3_to_merge": False,
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": True,
                    "enable_phase3_merge": True,  # Enabled for repo, but global is disabled
                }
            ],
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            process_pr(pr, config)
            # Merge should not be attempted because global enabled is False
            mock_merge.assert_not_called()
            mock_comment.assert_not_called()
