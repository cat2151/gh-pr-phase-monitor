"""
Test to verify that elapsed time is displayed correctly for unchanged PR states

This test ensures the new behavior requested in the issue:
"If the display content is exactly the same as before, change the display content 
to show something like '現在、検知してから3分20秒経過' (Currently, 3 minutes 20 seconds have elapsed since detection)"
"""

import time
from unittest.mock import patch

from src.gh_pr_phase_monitor.main import (
    display_status_summary,
    format_elapsed_time,
    _pr_state_times,
)
from src.gh_pr_phase_monitor.phase_detector import PHASE_LLM_WORKING


class TestElapsedTimeDisplay:
    """Test the elapsed time display functionality"""

    def setup_method(self):
        """Reset PR state times before each test"""
        _pr_state_times.clear()

    def test_format_elapsed_time_seconds_only(self):
        """Test formatting elapsed time when less than a minute"""
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
        from src.gh_pr_phase_monitor.phase_detector import PHASE_1

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
