"""
Tests for PR actions including browser opening behavior
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor import pr_actions
from src.gh_pr_phase_monitor.pr_actions import process_pr


class TestProcessPR:
    """Test the process_pr function"""

    def setup_method(self):
        """Clear the browser opened and notification tracking before each test"""
        pr_actions._browser_opened.clear()
        pr_actions._notifications_sent.clear()

    def test_browser_not_opened_for_phase1(self):
        """Browser should not open for phase1"""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {"enable_execution_phase1_to_phase2": True}

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser,
            patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready,
        ):
            mock_ready.return_value = True
            process_pr(pr, config)
            # Browser should not be called for phase1
            mock_browser.assert_not_called()

    def test_browser_not_opened_for_phase2(self):
        """Browser should not open for phase2"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "CHANGES_REQUESTED",
                    "body": "Please address these issues",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "CHANGES_REQUESTED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {"enable_execution_phase2_to_phase3": True}

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser,
            patch("src.gh_pr_phase_monitor.pr_actions.post_phase2_comment") as mock_comment,
        ):
            mock_comment.return_value = True
            process_pr(pr, config)
            # Browser should not be called for phase2
            mock_browser.assert_not_called()

    def test_browser_opened_for_phase3(self):
        """Browser should open for phase3"""
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

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser:
            process_pr(pr, {})
            # Browser should be called for phase3
            mock_browser.assert_called_once_with("https://github.com/test-owner/test-repo/pull/1")

    def test_browser_not_opened_for_llm_working(self):
        """Browser should not open for 'LLM working' phase"""
        pr = {
            "isDraft": False,
            "reviews": [],
            "latestReviews": [],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser:
            process_pr(pr, {})
            # Browser should not be called for LLM working
            mock_browser.assert_not_called()

    def test_browser_opened_only_once_for_phase3(self):
        """Browser should open only once for phase3, even if called multiple times"""
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

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser:
            # First call should open browser
            process_pr(pr, {})
            assert mock_browser.call_count == 1

            # Second call should not open browser again
            process_pr(pr, {})
            assert mock_browser.call_count == 1

            # Third call should still not open browser
            process_pr(pr, {})
            assert mock_browser.call_count == 1


class TestPhase3Notifications:
    """Test notification behavior for phase3"""

    def setup_method(self):
        """Clear tracking before each test"""
        pr_actions._browser_opened.clear()
        pr_actions._notifications_sent.clear()

    def test_notification_sent_when_enabled(self):
        """Notification should be sent when enabled in config"""
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
            "ntfy": {"enabled": True, "topic": "test-topic", "message": "PR ready: {url}"},
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_send_ntfy": True,
                }
            ],
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            mock_notify.return_value = True
            process_pr(pr, config)
            # Notification should be sent
            mock_notify.assert_called_once_with(config, "https://github.com/test-owner/test-repo/pull/1", "Test PR")

    def test_notification_not_sent_when_disabled(self):
        """Notification should not be sent when disabled in config"""
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
        config = {"ntfy": {"enabled": False, "topic": "test-topic"}}

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            process_pr(pr, config)
            # Notification should not be sent
            mock_notify.assert_not_called()

    def test_notification_not_sent_when_no_config(self):
        """Notification should not be sent when ntfy not in config"""
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
        config = {}

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            process_pr(pr, config)
            # Notification should not be sent
            mock_notify.assert_not_called()

    def test_notification_sent_only_once(self):
        """Notification should be sent only once per PR"""
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
            "ntfy": {"enabled": True, "topic": "test-topic", "message": "PR ready: {url}"},
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_send_ntfy": True,
                }
            ],
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            mock_notify.return_value = True
            # First call should send notification
            process_pr(pr, config)
            assert mock_notify.call_count == 1

            # Second call should not send notification again
            process_pr(pr, config)
            assert mock_notify.call_count == 1

            # Third call should still not send notification
            process_pr(pr, config)
            assert mock_notify.call_count == 1

    def test_notification_not_sent_for_phase1(self):
        """Notification should not be sent for phase1"""
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
            "ntfy": {"enabled": True, "topic": "test-topic"},
            "enable_execution_phase1_to_phase2": True,
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
            patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready,
        ):
            mock_ready.return_value = True
            process_pr(pr, config)
            # Notification should not be sent for phase1
            mock_notify.assert_not_called()

    def test_notification_not_sent_for_phase2(self):
        """Notification should not be sent for phase2"""
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
            "ntfy": {"enabled": True, "topic": "test-topic"},
            "enable_execution_phase2_to_phase3": True,
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
            patch("src.gh_pr_phase_monitor.pr_actions.post_phase2_comment") as mock_comment,
        ):
            mock_comment.return_value = True
            process_pr(pr, config)
            # Notification should not be sent for phase2
            mock_notify.assert_not_called()


class TestDryRunMode:
    """Test dry-run behavior when execution flags are false (default)"""

    def setup_method(self):
        """Clear tracking before each test"""
        pr_actions._browser_opened.clear()
        pr_actions._notifications_sent.clear()

    def test_phase1_dry_run_by_default(self):
        """Phase1 should not mark PR ready when flag is false (default)"""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {}  # No execution flag means default (false)

        with patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready:
            process_pr(pr, config)
            # mark_pr_ready should not be called in dry-run mode
            mock_ready.assert_not_called()

    def test_phase1_executes_when_enabled(self):
        """Phase1 should mark PR ready when flag is true"""
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
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase1_to_phase2": True,
                }
            ]
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready:
            mock_ready.return_value = True
            process_pr(pr, config)
            # mark_pr_ready should be called when execution is enabled
            mock_ready.assert_called_once_with("https://github.com/test-owner/test-repo/pull/1", None)

    def test_phase2_dry_run_by_default(self):
        """Phase2 should not post comment when flag is false (default)"""
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
        config = {}  # No execution flag means default (false)

        with patch("src.gh_pr_phase_monitor.pr_actions.post_phase2_comment") as mock_comment:
            process_pr(pr, config)
            # post_phase2_comment should not be called in dry-run mode
            mock_comment.assert_not_called()

    def test_phase2_executes_when_enabled(self):
        """Phase2 should post comment when flag is true"""
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
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase2_to_phase3": True,
                }
            ]
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.post_phase2_comment") as mock_comment:
            mock_comment.return_value = True
            process_pr(pr, config)
            # post_phase2_comment should be called when execution is enabled
            mock_comment.assert_called_once_with(pr, None)

    def test_phase3_dry_run_ntfy_by_default(self):
        """Phase3 should not send ntfy when flag is false (default)"""
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
            # enable_execution_phase3_send_ntfy is not set, so defaults to false
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            process_pr(pr, config)
            # send_phase3_notification should not be called in dry-run mode
            mock_notify.assert_not_called()

    def test_phase3_executes_ntfy_when_enabled(self):
        """Phase3 should send ntfy when flag is true"""
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
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_send_ntfy": True,
                }
            ],
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            mock_notify.return_value = True
            process_pr(pr, config)
            # send_phase3_notification should be called when execution is enabled
            mock_notify.assert_called_once_with(config, "https://github.com/test-owner/test-repo/pull/1", "Test PR")

    def test_phase3_notification_can_be_sent_after_dry_run(self):
        """Notification should be sent when execution is enabled, even after processing in dry-run mode"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED", "body": "Looks good!"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/2",
        }

        # First process in dry-run mode
        config_dry = {
            "ntfy": {"enabled": True, "topic": "test-topic"},
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_send_ntfy": False,
                }
            ],
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            process_pr(pr, config_dry)
            # Notification should not be sent in dry-run mode
            mock_notify.assert_not_called()

        # Then process with execution enabled
        config_exec = {
            "ntfy": {"enabled": True, "topic": "test-topic"},
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_send_ntfy": True,
                }
            ],
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            mock_notify.return_value = True
            process_pr(pr, config_exec)
            # Notification should be sent when execution is enabled, even after dry-run
            mock_notify.assert_called_once_with(
                config_exec, "https://github.com/test-owner/test-repo/pull/2", "Test PR"
            )


class TestOpenBrowserCooldown:
    """Test open_browser cooldown functionality"""

    def setup_method(self):
        """Reset cooldown state before each test"""
        import src.gh_pr_phase_monitor.browser_automation as ba

        ba._last_browser_open_time = None

    @patch("src.gh_pr_phase_monitor.pr_actions.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_open_browser_returns_true_on_success(self, mock_time, mock_webbrowser):
        """Test that open_browser returns True when browser is opened"""
        from src.gh_pr_phase_monitor.pr_actions import open_browser

        mock_time.return_value = 0.0

        result = open_browser("https://github.com/test/repo/pull/1")

        assert result is True
        mock_webbrowser.open.assert_called_once()

    @patch("src.gh_pr_phase_monitor.pr_actions.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_open_browser_respects_cooldown(self, mock_time, mock_webbrowser):
        """Test that open_browser respects the 60-second cooldown"""
        from src.gh_pr_phase_monitor.pr_actions import open_browser

        # First call - should succeed
        mock_time.return_value = 0.0
        result1 = open_browser("https://github.com/test/repo/pull/1")
        assert result1 is True

        # Second call immediately after - should fail
        mock_time.return_value = 1.0
        result2 = open_browser("https://github.com/test/repo/pull/2")
        assert result2 is False

        # Third call after cooldown - should succeed
        mock_time.return_value = 61.0
        result3 = open_browser("https://github.com/test/repo/pull/3")
        assert result3 is True

        # Verify browser was only opened twice
        assert mock_webbrowser.open.call_count == 2

    @patch("src.gh_pr_phase_monitor.pr_actions.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_process_pr_phase3_respects_cooldown(self, mock_time, mock_webbrowser):
        """Test that process_pr respects cooldown when opening browser for phase3"""
        pr_actions._browser_opened.clear()

        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "APPROVED",
                    "body": "LGTM",
                }
            ],
            "latestReviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "APPROVED",
                }
            ],
            "reviewRequests": [],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }

        # First PR - should open browser
        mock_time.return_value = 0.0
        process_pr(pr, None)
        assert mock_webbrowser.open.call_count == 1

        # Clear the tracking but keep the cooldown
        pr_actions._browser_opened.clear()

        # Second PR immediately after - should not open browser due to cooldown
        pr2 = pr.copy()
        pr2["url"] = "https://github.com/test-owner/test-repo/pull/2"
        mock_time.return_value = 1.0
        process_pr(pr2, None)
        # Still only 1 call because cooldown prevented the second open
        assert mock_webbrowser.open.call_count == 1

        # Third PR after cooldown - should open browser
        pr3 = pr.copy()
        pr3["url"] = "https://github.com/test-owner/test-repo/pull/3"
        mock_time.return_value = 61.0
        process_pr(pr3, None)
        assert mock_webbrowser.open.call_count == 2
