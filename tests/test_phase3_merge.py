"""
Tests for Phase3 merge functionality
"""

from unittest.mock import MagicMock, patch

from src.gh_pr_phase_monitor import pr_actions
from src.gh_pr_phase_monitor.pr_actions import merge_pr, process_pr


class TestPhase3Merge:
    """Test the phase3 merge functionality"""

    def setup_method(self):
        """Clear the tracking before each test"""
        pr_actions._browser_opened.clear()
        pr_actions._notifications_sent.clear()
        pr_actions._merged_prs.clear()

    def test_merge_not_attempted_when_disabled(self):
        """Merge should not be attempted when disabled in config"""
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
            "phase3_merge": {"enabled": False},
            "enable_execution_phase3_to_merge": False,
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            process_pr(pr, config)
            # Merge should not be attempted
            mock_merge.assert_not_called()
            mock_comment.assert_not_called()

    def test_merge_attempted_when_enabled_with_gh_cli(self):
        """Merge should be attempted using gh CLI when enabled and automated=false"""
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
            "phase3_merge": {
                "enabled": True,
                "comment": "Test merge comment",
                "automated": False,
            },
            "enable_execution_phase3_to_merge": True,
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_merge.return_value = True
            mock_comment.return_value = True
            process_pr(pr, config)
            # Comment should be posted before merge
            mock_comment.assert_called_once_with(pr, "Test merge comment", None)
            # Merge should be attempted via gh CLI
            mock_merge.assert_called_once_with("https://github.com/test-owner/test-repo/pull/1", None)

    def test_merge_attempted_when_enabled_with_automation(self):
        """Merge should be attempted using browser automation when enabled and automated=true"""
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
            "phase3_merge": {
                "enabled": True,
                "comment": "Auto merge comment",
                "automated": True,
            },
            "enable_execution_phase3_to_merge": True,
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr_automated"
        ) as mock_merge_auto, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_merge_auto.return_value = True
            mock_comment.return_value = True
            process_pr(pr, config)
            # Comment should be posted before merge
            mock_comment.assert_called_once_with(pr, "Auto merge comment", None)
            # Merge should be attempted via browser automation with only phase3_merge config
            expected_config = {"phase3_merge": config["phase3_merge"]}
            mock_merge_auto.assert_called_once_with("https://github.com/test-owner/test-repo/pull/1", expected_config)

    def test_merge_only_once_per_pr(self):
        """Merge should only be attempted once per PR"""
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
            "phase3_merge": {
                "enabled": True,
                "comment": "Merging",
                "automated": False,
            },
            "enable_execution_phase3_to_merge": True,
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_merge.return_value = True
            mock_comment.return_value = True

            # First call should merge
            process_pr(pr, config)
            assert mock_merge.call_count == 1
            assert mock_comment.call_count == 1

            # Second call should not merge again
            process_pr(pr, config)
            assert mock_merge.call_count == 1
            assert mock_comment.call_count == 1

    def test_merge_not_attempted_for_phase1(self):
        """Merge should not be attempted for phase1"""
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
            "phase3_merge": {
                "enabled": True,
                "comment": "Merging",
            },
            "enable_execution_phase1_to_phase2": True,
            "enable_execution_phase3_to_merge": True,
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment, patch(
            "src.gh_pr_phase_monitor.pr_actions.mark_pr_ready"
        ) as mock_ready:
            mock_ready.return_value = True
            process_pr(pr, config)
            # Merge should not be attempted for phase1
            mock_merge.assert_not_called()
            mock_comment.assert_not_called()

    def test_merge_not_attempted_for_phase2(self):
        """Merge should not be attempted for phase2"""
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
            "phase3_merge": {
                "enabled": True,
                "comment": "Merging",
            },
            "enable_execution_phase2_to_phase3": True,
            "enable_execution_phase3_to_merge": True,
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment, patch(
            "src.gh_pr_phase_monitor.pr_actions.post_phase2_comment"
        ) as mock_phase2_comment:
            mock_phase2_comment.return_value = True
            process_pr(pr, config)
            # Merge should not be attempted for phase2
            mock_merge.assert_not_called()
            mock_comment.assert_not_called()

    def test_merge_dry_run_mode(self):
        """Merge should show dry-run message when execution flag is false"""
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
            "phase3_merge": {
                "enabled": True,
                "comment": "Merging",
            },
            "enable_execution_phase3_to_merge": False,  # Dry-run mode
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            process_pr(pr, config)
            # Merge should not be attempted in dry-run mode
            mock_merge.assert_not_called()
            mock_comment.assert_not_called()

    def test_merge_skipped_when_comment_fails(self):
        """Merge should be skipped when comment posting fails"""
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
            "phase3_merge": {
                "enabled": True,
                "comment": "Merging",
                "automated": False,
            },
            "enable_execution_phase3_to_merge": True,
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_comment.return_value = False  # Comment posting fails
            process_pr(pr, config)
            # Comment should be attempted
            mock_comment.assert_called_once()
            # Merge should NOT be attempted when comment fails
            mock_merge.assert_not_called()
            # PR should NOT be added to merged_prs set (allowing retry)
            assert "https://github.com/test-owner/test-repo/pull/1" not in pr_actions._merged_prs

    def test_merge_failure_allows_retry_cli(self):
        """When CLI merge fails, PR should not be marked as merged (allows retry)"""
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
            "phase3_merge": {
                "enabled": True,
                "comment": "Merging",
                "automated": False,
            },
            "enable_execution_phase3_to_merge": True,
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_comment.return_value = True
            mock_merge.return_value = False  # Merge fails
            process_pr(pr, config)
            # Comment and merge should be attempted
            mock_comment.assert_called_once()
            mock_merge.assert_called_once()
            # PR should NOT be in merged_prs set (allows retry)
            assert "https://github.com/test-owner/test-repo/pull/1" not in pr_actions._merged_prs

    def test_merge_failure_allows_retry_automation(self):
        """When browser automation merge fails, PR should not be marked as merged (allows retry)"""
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
            "phase3_merge": {
                "enabled": True,
                "comment": "Merging",
                "automated": True,
            },
            "enable_execution_phase3_to_merge": True,
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr_automated"
        ) as mock_merge_auto, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_comment.return_value = True
            mock_merge_auto.return_value = False  # Merge fails
            process_pr(pr, config)
            # Comment and merge should be attempted
            mock_comment.assert_called_once()
            mock_merge_auto.assert_called_once()
            # PR should NOT be in merged_prs set (allows retry)
            assert "https://github.com/test-owner/test-repo/pull/1" not in pr_actions._merged_prs

    def test_successful_merge_marks_pr_as_merged(self):
        """When merge succeeds, PR should be marked as merged (prevents duplicates)"""
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
            "phase3_merge": {
                "enabled": True,
                "comment": "Merging",
                "automated": False,
            },
            "enable_execution_phase3_to_merge": True,
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser"), patch(
            "src.gh_pr_phase_monitor.pr_actions.merge_pr"
        ) as mock_merge, patch("src.gh_pr_phase_monitor.pr_actions.post_phase3_comment") as mock_comment:
            mock_comment.return_value = True
            mock_merge.return_value = True  # Merge succeeds
            process_pr(pr, config)
            # Comment and merge should be attempted
            mock_comment.assert_called_once()
            mock_merge.assert_called_once()
            # PR SHOULD be in merged_prs set (prevents duplicate merges)
            assert "https://github.com/test-owner/test-repo/pull/1" in pr_actions._merged_prs

    def test_merge_includes_delete_branch_flag(self):
        """Merge command should include --delete-branch flag"""
        pr_url = "https://github.com/test-owner/test-repo/pull/123"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = merge_pr(pr_url)

            # Verify the command was called
            assert result is True
            mock_run.assert_called_once()

            # Get the actual command that was called
            call_args = mock_run.call_args
            cmd = call_args[0][0]

            # Verify the command includes --delete-branch flag
            assert "gh" in cmd
            assert "pr" in cmd
            assert "merge" in cmd
            assert pr_url in cmd
            assert "--squash" in cmd
            assert "--delete-branch" in cmd
