"""
Test to verify that the application exits when PR state does not change for too long
"""

import time
from unittest.mock import patch

import pytest

from src.gh_pr_phase_monitor import main
from src.gh_pr_phase_monitor.main import check_no_state_change_timeout
from src.gh_pr_phase_monitor.phase_detector import PHASE_3, PHASE_2, PHASE_1, PHASE_LLM_WORKING


class TestNoChangeTimeout:
    """Test the check_no_state_change_timeout function"""
    
    def setup_method(self):
        """Reset global state before each test"""
        main._last_state = None

    def test_default_timeout_when_config_not_set(self):
        """Test that default 30m timeout is used when no_change_timeout is not configured"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_3]
        config = {}
        
        # Should not exit immediately (30m default timeout)
        # First call initializes the state
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Verify state was initialized (not None)
        assert main._last_state is not None

    def test_no_timeout_when_config_is_empty_string(self):
        """Test that no timeout occurs when no_change_timeout is empty string"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_3]
        config = {"no_change_timeout": ""}
        
        # Should not exit
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # State should remain None when disabled
        assert main._last_state is None

    def test_timeout_when_state_unchanged(self):
        """Test that application exits when state does not change for timeout duration"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_2]
        config = {"no_change_timeout": "1s"}  # Very short timeout for testing
        
        # First call: initialize the state
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Wait for timeout to elapse
        time.sleep(1.5)
        
        # Second call with same state: should exit
        with pytest.raises(SystemExit) as exc_info:
            check_no_state_change_timeout(all_prs, pr_phases, config)
        
        assert exc_info.value.code == 0

    def test_timer_reset_when_phase_changes(self):
        """Test that timer resets when any PR phase changes"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        config = {"no_change_timeout": "2s"}
        
        # First call: start with phase3 and phase2
        pr_phases = [PHASE_3, PHASE_2]
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Wait for some time but not full timeout
        time.sleep(1)
        
        # Second call: change phase of one PR, should reset timer
        pr_phases = [PHASE_3, PHASE_3]
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Wait less than timeout
        time.sleep(1)
        
        # Should not exit because timer was reset
        check_no_state_change_timeout(all_prs, pr_phases, config)

    def test_timer_reset_when_pr_added(self):
        """Test that timer resets when a PR is added"""
        config = {"no_change_timeout": "2s"}
        
        # First call: two PRs
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_2]
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Wait for some time but not full timeout
        time.sleep(1)
        
        # Second call: add a new PR, should reset timer
        all_prs.append({"title": "PR 3", "url": "https://github.com/owner/repo1/pulls/3", "repository": {"name": "repo1", "owner": "owner"}})
        pr_phases = [PHASE_3, PHASE_2, PHASE_1]
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Wait less than timeout
        time.sleep(1)
        
        # Should not exit because timer was reset
        check_no_state_change_timeout(all_prs, pr_phases, config)

    def test_timer_reset_when_pr_removed(self):
        """Test that timer resets when a PR is removed"""
        config = {"no_change_timeout": "2s"}
        
        # First call: three PRs
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 3", "url": "https://github.com/owner/repo1/pulls/3", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_2, PHASE_1]
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Wait for some time but not full timeout
        time.sleep(1)
        
        # Second call: remove a PR, should reset timer
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_2]
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Wait less than timeout
        time.sleep(1)
        
        # Should not exit because timer was reset
        check_no_state_change_timeout(all_prs, pr_phases, config)

    def test_invalid_timeout_format(self):
        """Test that invalid timeout format is handled gracefully"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3]
        config = {"no_change_timeout": "invalid"}
        
        # Should print warning and not exit
        with patch("builtins.print") as mock_print:
            check_no_state_change_timeout(all_prs, pr_phases, config)
            
            # Check that warning was printed
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Warning" in str(call) and "invalid" in str(call).lower() for call in calls)

    def test_empty_pr_list(self):
        """Test that empty PR list doesn't cause issues"""
        all_prs = []
        pr_phases = []
        config = {"no_change_timeout": "30m"}
        
        # Should not exit
        check_no_state_change_timeout(all_prs, pr_phases, config)

    def test_timeout_message_in_japanese(self):
        """Test that exit message is displayed in Japanese"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3]
        config = {"no_change_timeout": "1s"}
        
        # First call: initialize the state
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Wait for timeout to elapse
        time.sleep(1.5)
        
        # Second call: should exit with Japanese message
        with patch("builtins.print") as mock_print:
            with pytest.raises(SystemExit):
                check_no_state_change_timeout(all_prs, pr_phases, config)
            
            # Check that Japanese message was printed
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "変化がない" in output
            assert "API利用の浪費を防止" in output

    def test_mismatched_list_lengths(self):
        """Test that mismatched all_prs and pr_phases lengths are handled correctly"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3]  # Only one phase for two PRs - mismatched!
        config = {"no_change_timeout": "1s"}
        
        # Should not exit or crash, just handle gracefully
        check_no_state_change_timeout(all_prs, pr_phases, config)

    def test_same_phases_different_prs_triggers_reset(self):
        """Test that changing PR URLs (even with same phases) resets the timer"""
        config = {"no_change_timeout": "2s"}
        
        # First call: PR 1 and 2
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_2]
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Wait for some time but not full timeout
        time.sleep(1)
        
        # Second call: PR 1 and 3 (different PR, same phases), should reset timer
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 3", "url": "https://github.com/owner/repo1/pulls/3", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        pr_phases = [PHASE_3, PHASE_2]
        check_no_state_change_timeout(all_prs, pr_phases, config)
        
        # Wait less than timeout
        time.sleep(1)
        
        # Should not exit because timer was reset
        check_no_state_change_timeout(all_prs, pr_phases, config)

    def test_no_timeout_with_frequent_phase_changes(self):
        """Test that timeout doesn't occur if state keeps changing"""
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        config = {"no_change_timeout": "2s"}
        
        # Multiple calls with different phases
        phases_sequence = [PHASE_1, PHASE_2, PHASE_3, PHASE_LLM_WORKING, PHASE_2]
        
        for phase in phases_sequence:
            pr_phases = [phase]
            check_no_state_change_timeout(all_prs, pr_phases, config)
            time.sleep(0.5)  # Wait between changes but not enough to timeout
        
        # Should not have exited because state kept changing
        assert True  # If we get here, test passed
