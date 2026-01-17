"""
Test to verify that normal interval is not contaminated by reduced frequency interval
when returning from reduced frequency mode.

This test reproduces the bug where:
1. System enters reduced frequency mode (e.g., 1h interval)
2. State change is detected
3. Message "通常の監視間隔に戻ります" is displayed
4. But the wait time is still 1h instead of normal interval
"""

import time
from unittest.mock import patch

from src.gh_pr_phase_monitor import state_tracker
from src.gh_pr_phase_monitor.monitor import check_no_state_change_timeout
from src.gh_pr_phase_monitor.phase_detector import PHASE_2, PHASE_3


class TestIntervalContaminationBug:
    """Test that normal interval is not contaminated by reduced frequency mode"""

    def setup_method(self):
        """Reset global state before each test"""
        state_tracker.set_last_state(None)
        state_tracker.set_reduced_frequency_mode(False)

    def test_interval_not_contaminated_after_returning_from_reduced_mode(self):
        """
        Test that when returning from reduced frequency mode to normal mode,
        the normal interval is used, not the reduced frequency interval.

        This test simulates the scenario:
        1. Start with normal mode
        2. Enter reduced frequency mode after timeout
        3. Detect state change and return to normal mode
        4. Verify that normal interval is used in the next iteration

        The bug was: interval_seconds and interval_str variables were being
        overwritten by wait_with_countdown return values which included
        the reduced frequency interval, causing the normal interval to be
        contaminated.
        """
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            }
        ]

        # Shortened timeout for testing
        config = {
            "no_change_timeout": "1s",
            "reduced_frequency_interval": "1h",
            "interval": "1m",  # Normal interval
        }

        # First call: initialize state with phase3
        pr_phases = [PHASE_3]
        result = check_no_state_change_timeout(all_prs, pr_phases, config)
        assert result is False  # Normal mode initially

        # Wait for timeout to elapse
        time.sleep(1.5)

        # Second call: should enter reduced frequency mode
        result = check_no_state_change_timeout(all_prs, pr_phases, config)
        assert result is True  # Now in reduced frequency mode

        # Third call: change phase to trigger state change
        pr_phases = [PHASE_2]
        with patch("builtins.print") as mock_print:
            result = check_no_state_change_timeout(all_prs, pr_phases, config)
            assert result is False  # Should return to normal mode

            # Verify that return-to-normal message was printed
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "変化を検知" in output
            assert "通常の監視間隔に戻ります" in output
