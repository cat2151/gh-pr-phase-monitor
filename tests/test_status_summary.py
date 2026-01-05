"""
Test to verify that status summary is displayed correctly before waiting state

This test ensures the new behavior requested in the issue:
"To help users easily understand LLM working information even on terminals with few lines,
display a summary of LLM working status at the end before entering the waiting state"
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor.main import display_status_summary
from src.gh_pr_phase_monitor.phase_detector import PHASE_1, PHASE_2, PHASE_3, PHASE_LLM_WORKING


class TestDisplayStatusSummary:
    """Test the display_status_summary function"""

    def test_display_status_summary_with_no_prs(self):
        """Test that display_status_summary correctly handles empty PR list"""
        with patch("builtins.print") as mock_print:
            display_status_summary([], [], [])
            
            # Verify that a "No open PRs" message is displayed
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("No open PRs to monitor" in str(call) for call in calls)

    def test_display_status_summary_with_mixed_phases(self):
        """Test that display_status_summary correctly displays PRs by phase"""
        # Create mock PR data with repository info
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 3", "url": "https://github.com/owner/repo2/pulls/3", "repository": {"name": "repo2", "owner": "owner"}},
            {"title": "PR 4", "url": "https://github.com/owner/repo2/pulls/4", "repository": {"name": "repo2", "owner": "owner"}},
            {"title": "PR 5", "url": "https://github.com/owner/repo3/pulls/5", "repository": {"name": "repo3", "owner": "owner"}},
        ]
        
        # Mixed phases: 1 phase1, 2 phase2, 1 phase3, 1 LLM working
        pr_phases = [PHASE_1, PHASE_2, PHASE_2, PHASE_3, PHASE_LLM_WORKING]
        
        repos_with_prs = [
            {"name": "repo1", "owner": "owner", "openPRCount": 2},
            {"name": "repo2", "owner": "owner", "openPRCount": 2},
            {"name": "repo3", "owner": "owner", "openPRCount": 1},
        ]
        
        with patch("builtins.print") as mock_print:
            display_status_summary(all_prs, pr_phases, repos_with_prs)
            
            # Extract all printed messages
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            
            # Verify that PRs are displayed in the format [owner/repo] [phase] title
            assert "[owner/repo1]" in output
            assert "[owner/repo2]" in output
            assert "[owner/repo3]" in output
            assert "PR 1" in output
            assert "PR 2" in output
            assert "PR 3" in output
            assert "PR 4" in output
            assert "PR 5" in output

    def test_display_status_summary_with_all_llm_working(self):
        """Test that display_status_summary correctly handles all PRs in LLM working state"""
        # Create mock PR data with repository info
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        
        # All PRs are in LLM working state
        pr_phases = [PHASE_LLM_WORKING, PHASE_LLM_WORKING]
        
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 2}]
        
        with patch("builtins.print") as mock_print:
            display_status_summary(all_prs, pr_phases, repos_with_prs)
            
            # Extract all printed messages
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            
            # Verify that PRs are displayed
            assert "[owner/repo1]" in output
            assert "PR 1" in output
            assert "PR 2" in output

    def test_display_status_summary_with_single_phase(self):
        """Test that display_status_summary correctly handles PRs in single phase"""
        # Create mock PR data with repository info
        all_prs = [
            {"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 2", "url": "https://github.com/owner/repo1/pulls/2", "repository": {"name": "repo1", "owner": "owner"}},
            {"title": "PR 3", "url": "https://github.com/owner/repo1/pulls/3", "repository": {"name": "repo1", "owner": "owner"}},
        ]
        
        # All PRs are in phase 3
        pr_phases = [PHASE_3, PHASE_3, PHASE_3]
        
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 3}]
        
        with patch("builtins.print") as mock_print:
            display_status_summary(all_prs, pr_phases, repos_with_prs)
            
            # Extract all printed messages
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            
            # Verify that PRs are displayed
            assert "[owner/repo1]" in output
            assert "PR 1" in output
            assert "PR 2" in output
            assert "PR 3" in output

    def test_display_status_summary_displays_summary_header(self):
        """Test that display_status_summary displays a clear summary header"""
        all_prs = [{"title": "PR 1", "url": "https://github.com/owner/repo1/pulls/1", "repository": {"name": "repo1", "owner": "owner"}}]
        pr_phases = [PHASE_1]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]
        
        with patch("builtins.print") as mock_print:
            display_status_summary(all_prs, pr_phases, repos_with_prs)
            
            # Extract all printed messages
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            
            # Verify that "Status Summary" header is displayed
            assert "Status Summary:" in output
