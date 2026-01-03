"""
Tests for posting comments to PRs when phase2 is detected
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from gh_pr_phase_monitor import post_phase2_comment


class TestPostPhase2Comment:
    """Test the post_phase2_comment function"""

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_success(self, mock_run):
        """Test successful comment posting"""
        mock_run.return_value = MagicMock(returncode=0)

        pr_url = "https://github.com/user/repo/pull/123"
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr_url, repo_dir)

        assert result is True
        mock_run.assert_called_once()

        # Verify command arguments
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[0] == "gh"
        assert cmd[1] == "pr"
        assert cmd[2] == "comment"
        assert cmd[3] == pr_url
        assert cmd[4] == "--body"
        assert "@copilot apply changes based on the review comments" in cmd[5]

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_failure(self, mock_run):
        """Test failed comment posting"""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["gh", "pr", "comment"], stderr="Error: PR not found"
        )

        pr_url = "https://github.com/user/repo/pull/999"
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr_url, repo_dir)

        assert result is False

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_with_correct_cwd(self, mock_run):
        """Test that comment posting uses correct working directory"""
        mock_run.return_value = MagicMock(returncode=0)

        pr_url = "https://github.com/user/repo/pull/123"
        repo_dir = Path("/custom/repo/path")

        post_phase2_comment(pr_url, repo_dir)

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cwd"] == repo_dir
