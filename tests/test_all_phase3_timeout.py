"""
Test to verify that the application exits when all PRs remain in phase3 for too long
"""

import time
from unittest.mock import patch

import pytest

from src.gh_pr_phase_monitor import main
from src.gh_pr_phase_monitor.main import check_all_phase3_timeout
from src.gh_pr_phase_monitor.phase_detector import PHASE_3, PHASE_2, PHASE_LLM_WORKING


class TestAllPhase3Timeout:
    """Test the check_all_phase3_timeout function"""
    
    def setup_method(self):
        """Reset global state before each test"""
        main._all_phase3_start_time = None

    def test_default_timeout_when_config_not_set(self):
        """Test that default 30m timeout is used when all_phase3_timeout is not configured"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_3]
        config = {}
        
        # Should not exit immediately (30m default timeout)
        # First call initializes the timer
        check_all_phase3_timeout(all_prs, pr_phases, config)
        
        # Verify timer was started (not None)
        assert main._all_phase3_start_time is not None

    def test_no_timeout_when_config_is_empty_string(self):
        """Test that no timeout occurs when all_phase3_timeout is empty string"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_3]
        config = {"all_phase3_timeout": ""}
        
        # Should not exit
        check_all_phase3_timeout(all_prs, pr_phases, config)

    def test_no_timeout_when_not_all_phase3(self):
        """Test that no timeout occurs when not all PRs are in phase3"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_2]
        config = {"all_phase3_timeout": "30m"}
        
        # Should not exit
        check_all_phase3_timeout(all_prs, pr_phases, config)

    def test_no_timeout_when_mixed_phases(self):
        """Test that no timeout occurs when PRs are in mixed phases"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 3", "url": "https://github.com/owner/repo1/pulls/3", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_2, PHASE_LLM_WORKING]
        config = {"all_phase3_timeout": "30m"}
        
        # Should not exit
        check_all_phase3_timeout(all_prs, pr_phases, config)

    def test_timeout_exit_when_all_phase3_too_long(self):
        """Test that application exits when all PRs are in phase3 for too long"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_3]
        config = {"all_phase3_timeout": "1s"}  # Very short timeout for testing
        
        # First call: initialize the timer
        check_all_phase3_timeout(all_prs, pr_phases, config)
        
        # Wait for timeout to elapse
        time.sleep(1.5)
        
        # Second call: should exit
        with pytest.raises(SystemExit) as exc_info:
            check_all_phase3_timeout(all_prs, pr_phases, config)
        
        assert exc_info.value.code == 0

    def test_timer_reset_when_phase_changes(self):
        """Test that timer resets when not all PRs are in phase3"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        config = {"all_phase3_timeout": "2s"}
        
        # First call: all phase3, start timer
        pr_phases = [PHASE_3, PHASE_3]
        check_all_phase3_timeout(all_prs, pr_phases, config)
        
        # Wait for some time but not full timeout
        time.sleep(1)
        
        # Second call: not all phase3, should reset timer
        pr_phases = [PHASE_3, PHASE_2]
        check_all_phase3_timeout(all_prs, pr_phases, config)
        
        # Third call: all phase3 again, timer should restart
        pr_phases = [PHASE_3, PHASE_3]
        check_all_phase3_timeout(all_prs, pr_phases, config)
        
        # Wait less than timeout
        time.sleep(1)
        
        # Should not exit because timer was reset
        check_all_phase3_timeout(all_prs, pr_phases, config)

    def test_invalid_timeout_format(self):
        """Test that invalid timeout format is handled gracefully"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3]
        config = {"all_phase3_timeout": "invalid"}
        
        # Should print warning and not exit
        with patch("builtins.print") as mock_print:
            check_all_phase3_timeout(all_prs, pr_phases, config)
            
            # Check that warning was printed
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Warning" in str(call) and "invalid" in str(call).lower() for call in calls)

    def test_empty_pr_list(self):
        """Test that empty PR list doesn't cause issues"""
        all_prs = []
        pr_phases = []
        config = {"all_phase3_timeout": "30m"}
        
        # Should not exit
        check_all_phase3_timeout(all_prs, pr_phases, config)

    def test_timeout_message_in_japanese(self):
        """Test that exit message is displayed in Japanese"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3]
        config = {"all_phase3_timeout": "1s"}
        
        # First call: initialize the timer
        check_all_phase3_timeout(all_prs, pr_phases, config)
        
        # Wait for timeout to elapse
        time.sleep(1.5)
        
        # Second call: should exit with Japanese message
        with patch("builtins.print") as mock_print:
            with pytest.raises(SystemExit):
                check_all_phase3_timeout(all_prs, pr_phases, config)
            
            # Check that Japanese message was printed
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "phase3" in output
            assert "レビュー待ち" in output
            assert "API利用の浪費を防止" in output

    def test_mismatched_list_lengths(self):
        """Test that mismatched all_prs and pr_phases lengths are handled correctly"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3]  # Only one phase for two PRs - mismatched!
        config = {"all_phase3_timeout": "1s"}
        
        # Should not exit or crash, just reset timer due to mismatch
        check_all_phase3_timeout(all_prs, pr_phases, config)

    @patch("src.gh_pr_phase_monitor.main.send_all_phase3_notification")
    def test_all_phase3_notification_sent_on_first_detection(self, mock_send):
        """Test that notification is sent when all PRs first become phase3"""
        mock_send.return_value = True
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_3]
        config = {
            "all_phase3_timeout": "30m",
            "ntfy": {"enabled": True, "topic": "test-topic"}
        }
        
        # First call: should send notification
        check_all_phase3_timeout(all_prs, pr_phases, config)
        
        # Verify notification was sent
        mock_send.assert_called_once_with(config)

    @patch("src.gh_pr_phase_monitor.main.send_all_phase3_notification")
    def test_all_phase3_notification_not_sent_when_ntfy_disabled(self, mock_send):
        """Test that notification is not sent when ntfy is disabled"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3]
        config = {
            "all_phase3_timeout": "30m",
            "ntfy": {"enabled": False, "topic": "test-topic"}
        }
        
        # Should not send notification
        check_all_phase3_timeout(all_prs, pr_phases, config)
        
        # Verify notification was not sent
        mock_send.assert_not_called()

    @patch("src.gh_pr_phase_monitor.main.send_all_phase3_notification")
    def test_all_phase3_notification_sent_only_once(self, mock_send):
        """Test that notification is sent only once per all-phase3 period"""
        mock_send.return_value = True
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3]
        config = {
            "all_phase3_timeout": "30m",
            "ntfy": {"enabled": True, "topic": "test-topic"}
        }
        
        # First call: should send notification
        check_all_phase3_timeout(all_prs, pr_phases, config)
        assert mock_send.call_count == 1
        
        # Second call: should not send notification again
        check_all_phase3_timeout(all_prs, pr_phases, config)
        assert mock_send.call_count == 1

    @patch("src.gh_pr_phase_monitor.main.send_all_phase3_notification")
    def test_all_phase3_notification_resent_after_phase_change(self, mock_send):
        """Test that notification is sent again if PRs leave phase3 and return"""
        mock_send.return_value = True
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        config = {
            "all_phase3_timeout": "30m",
            "ntfy": {"enabled": True, "topic": "test-topic"}
        }
        
        # First call: all phase3, should send notification
        pr_phases = [PHASE_3]
        check_all_phase3_timeout(all_prs, pr_phases, config)
        assert mock_send.call_count == 1
        
        # Second call: not all phase3, should reset
        pr_phases = [PHASE_2]
        check_all_phase3_timeout(all_prs, pr_phases, config)
        
        # Third call: all phase3 again, should send notification again
        pr_phases = [PHASE_3]
        check_all_phase3_timeout(all_prs, pr_phases, config)
        assert mock_send.call_count == 2
