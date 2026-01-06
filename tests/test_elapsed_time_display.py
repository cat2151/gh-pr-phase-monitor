"""
Test to verify that elapsed time is displayed correctly for unchanged PR states

This test ensures the new behavior requested in the issue:
"If the display content is exactly the same as before, change the display content 
to show something like '現在、検知してから3分20秒経過' (Currently, 3 minutes 20 seconds have elapsed since detection)"
"""

import time
from unittest.mock import patch, MagicMock

from src.gh_pr_phase_monitor.main import (
    display_status_summary,
    format_elapsed_time,
    wait_with_countdown,
    _pr_state_times,
)
from src.gh_pr_phase_monitor.phase_detector import PHASE_LLM_WORKING, PHASE_1


class TestElapsedTimeDisplay:
    """Test the elapsed time display functionality"""

    def setup_method(self):
        """Reset PR state times before each test"""
        _pr_state_times.clear()

    def test_format_elapsed_time_seconds_only(self):
        """Test formatting elapsed time when less than a minute"""
        assert format_elapsed_time(0) == "0秒"
        assert format_elapsed_time(30) == "30秒"
        assert format_elapsed_time(59) == "59秒"

    def test_format_elapsed_time_minutes_and_seconds(self):
        """Test formatting elapsed time with minutes and seconds"""
        assert format_elapsed_time(60) == "1分0秒"
        assert format_elapsed_time(90) == "1分30秒"
        assert format_elapsed_time(200) == "3分20秒"
        assert format_elapsed_time(3661) == "61分1秒"

    def test_elapsed_time_not_shown_for_new_prs(self):
        """Test that elapsed time is not shown for PRs detected for less than 60 seconds"""
        # Create mock PR data
        all_prs = [
            {
                "title": "New PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        with patch("builtins.print") as mock_print:
            display_status_summary(all_prs, pr_phases, repos_with_prs)

            # Extract all printed messages
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)

            # Verify that elapsed time is NOT displayed (PR is new)
            assert "経過" not in output
            assert "New PR" in output

    def test_elapsed_time_shown_after_60_seconds(self):
        """Test that elapsed time is shown for PRs in same state for more than 60 seconds"""
        # Create mock PR data
        all_prs = [
            {
                "title": "Old PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        # First call to set the initial detection time
        with patch("builtins.print"):
            display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Manually adjust the detection time to simulate 200 seconds elapsed
        state_key = ("https://github.com/owner/repo1/pulls/1", PHASE_LLM_WORKING)
        _pr_state_times[state_key] = time.time() - 200

        # Second call should show elapsed time
        with patch("builtins.print") as mock_print:
            display_status_summary(all_prs, pr_phases, repos_with_prs)

            # Extract all printed messages
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)

            # Verify that elapsed time IS displayed
            assert "現在、検知してから" in output
            assert "経過" in output
            assert "3分" in output  # Should be around 3 minutes

    def test_elapsed_time_resets_when_phase_changes(self):
        """Test that elapsed time tracking resets when PR phase changes"""
        # Create mock PR data
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            }
        ]

        # First call with PHASE_LLM_WORKING
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        with patch("builtins.print"):
            display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Verify that state was tracked
        state_key_1 = ("https://github.com/owner/repo1/pulls/1", PHASE_LLM_WORKING)
        assert state_key_1 in _pr_state_times

        # Simulate phase change by calling with a different phase
        pr_phases = [PHASE_1]
        with patch("builtins.print"):
            display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Verify that old state was cleaned up and new state was tracked
        state_key_2 = ("https://github.com/owner/repo1/pulls/1", PHASE_1)
        assert state_key_1 not in _pr_state_times
        assert state_key_2 in _pr_state_times

    def test_cleanup_removes_old_pr_states(self):
        """Test that cleanup removes states for PRs that no longer exist"""
        # Create mock PR data
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            },
            {
                "title": "PR 2",
                "url": "https://github.com/owner/repo1/pulls/2",
                "repository": {"name": "repo1", "owner": "owner"},
            },
        ]
        pr_phases = [PHASE_LLM_WORKING, PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 2}]

        # First call to track both PRs
        with patch("builtins.print"):
            display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Verify both PRs are tracked
        assert len(_pr_state_times) == 2

        # Second call with only one PR
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]

        with patch("builtins.print"):
            display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Verify only one PR is now tracked (cleanup removed the other)
        assert len(_pr_state_times) == 1
        assert ("https://github.com/owner/repo1/pulls/1", PHASE_LLM_WORKING) in _pr_state_times

    def test_elapsed_time_shown_at_exactly_60_seconds(self):
        """Test that elapsed time is shown when exactly 60 seconds have elapsed (boundary condition)"""
        # Create mock PR data
        all_prs = [
            {
                "title": "PR at boundary",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        # First call to set the initial detection time
        with patch("builtins.print"):
            display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Manually adjust the detection time to simulate exactly 60 seconds elapsed
        state_key = ("https://github.com/owner/repo1/pulls/1", PHASE_LLM_WORKING)
        _pr_state_times[state_key] = time.time() - 60

        # Second call should show elapsed time since it's >= 60
        with patch("builtins.print") as mock_print:
            display_status_summary(all_prs, pr_phases, repos_with_prs)

            # Extract all printed messages
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)

            # Verify that elapsed time IS displayed at the boundary
            assert "現在、検知してから" in output
            assert "経過" in output
            assert "1分0秒" in output  # Should be exactly 1 minute


class TestWaitWithCountdown:
    """Test the wait_with_countdown functionality"""

    def test_countdown_displays_elapsed_time(self):
        """Test that countdown displays correctly with elapsed time formatting"""
        with patch("builtins.print") as mock_print, \
             patch("time.sleep") as mock_sleep, \
             patch("time.time") as mock_time:
            # Mock time.time to simulate passage of time
            mock_time.side_effect = [0, 0, 1, 2, 3, 3]  # start, loop checks
            wait_with_countdown(3, "3s")

            # Verify print was called with header
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "Waiting 3s until next check" in output

            # Verify countdown messages were printed
            assert "待機中... 経過時間: 0秒" in output
            assert "待機中... 経過時間: 1秒" in output
            assert "待機中... 経過時間: 2秒" in output
            assert "待機中... 経過時間: 3秒" in output

            # Verify sleep was called correct number of times
            assert mock_sleep.call_count == 3

    def test_countdown_uses_carriage_return_for_updates(self):
        """Test that countdown uses ANSI escape sequences (carriage return) for in-place updates"""
        with patch("builtins.print") as mock_print, \
             patch("time.sleep") as mock_sleep, \
             patch("time.time") as mock_time:
            # Mock time.time to simulate passage of time
            mock_time.side_effect = [0, 0, 1, 2, 2]
            wait_with_countdown(2, "2s")

            # Check that carriage return is used in countdown lines
            countdown_calls = [
                call for call in mock_print.call_args_list
                if "待機中" in str(call)
            ]

            # Verify carriage return usage
            for call in countdown_calls[:-1]:  # All except the last one
                call_str = str(call)
                assert "\\r" in call_str or call_str.startswith("call('\\r")

    def test_countdown_handles_different_intervals(self):
        """Test that countdown properly handles different time intervals"""
        with patch("builtins.print") as mock_print, \
             patch("time.sleep") as mock_sleep, \
             patch("time.time") as mock_time:
            # Mock time.time to simulate passage of time
            mock_time.side_effect = [0, 0, 1, 2, 3, 4, 5, 5]
            wait_with_countdown(5, "5s")

            # Verify sleep was called 5 times (once per second)
            assert mock_sleep.call_count == 5

            # Verify final elapsed time
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "待機中... 経過時間: 5秒" in output

    def test_countdown_formats_time_correctly(self):
        """Test that countdown formats time with minutes and seconds"""
        with patch("builtins.print") as mock_print, \
             patch("time.sleep") as mock_sleep, \
             patch("time.time") as mock_time:
            # Mock time.time to simulate 90 seconds of elapsed time
            # We need enough values for 90 iterations + extra for checks
            times = [0] + [i for i in range(91) for _ in range(2)]  # start + pairs for each iteration
            mock_time.side_effect = times
            wait_with_countdown(90, "90s")

            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)

            # Verify that minutes are displayed correctly
            assert "待機中... 経過時間: 1分29秒" in output
            assert "待機中... 経過時間: 1分30秒" in output
