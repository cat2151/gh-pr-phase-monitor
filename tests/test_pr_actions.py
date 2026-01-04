"""
Tests for PR actions including browser opening behavior
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor import pr_actions
from src.gh_pr_phase_monitor.pr_actions import process_pr


class TestProcessPR:
    """Test the process_pr function"""

    def setup_method(self):
        """Clear the browser opened tracking before each test"""
        pr_actions._browser_opened.clear()

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

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser, patch(
            "src.gh_pr_phase_monitor.pr_actions.mark_pr_ready"
        ) as mock_ready:
            mock_ready.return_value = True
            process_pr(pr, {})
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

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser, patch(
            "src.gh_pr_phase_monitor.pr_actions.post_phase2_comment"
        ) as mock_comment:
            mock_comment.return_value = True
            process_pr(pr, {})
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
