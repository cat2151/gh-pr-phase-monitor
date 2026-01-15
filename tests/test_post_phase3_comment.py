"""
Tests for post_phase3_comment function
"""

import subprocess
from unittest.mock import patch

from src.gh_pr_phase_monitor.comment_manager import post_phase3_comment


class TestPostPhase3Comment:
    """Test the post_phase3_comment function"""

    def test_post_comment_success(self):
        """Should post comment successfully"""
        pr = {"url": "https://github.com/owner/repo/pull/1"}
        comment_text = "agentによって、レビュー指摘対応が完了したと判断します。userの責任のもと、userレビューは省略します。PRをMergeします。"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = post_phase3_comment(pr, comment_text, None)

            assert result is True
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args == [
                "gh",
                "pr",
                "comment",
                "https://github.com/owner/repo/pull/1",
                "--body",
                "agentによって、レビュー指摘対応が完了したと判断します。userの責任のもと、userレビューは省略します。PRをMergeします。",
            ]

    def test_post_comment_failure(self):
        """Should handle comment posting failure"""
        pr = {"url": "https://github.com/owner/repo/pull/1"}
        comment_text = "Merge comment"

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="Error: Failed to post comment")
            result = post_phase3_comment(pr, comment_text, None)

            assert result is False

    def test_post_comment_no_url(self):
        """Should return False when PR has no URL"""
        pr = {}
        comment_text = "Merge comment"

        with patch("subprocess.run") as mock_run:
            result = post_phase3_comment(pr, comment_text, None)

            assert result is False
            mock_run.assert_not_called()

    def test_post_comment_with_custom_text(self):
        """Should post comment with custom text"""
        pr = {"url": "https://github.com/owner/repo/pull/2"}
        comment_text = "Custom merge message from config"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = post_phase3_comment(pr, comment_text, None)

            assert result is True
            args = mock_run.call_args[0][0]
            assert args[-1] == "Custom merge message from config"

    def test_post_comment_handles_missing_stderr(self):
        """Should handle missing stderr gracefully"""
        pr = {"url": "https://github.com/owner/repo/pull/1"}
        comment_text = "Merge comment"

        with patch("subprocess.run") as mock_run:
            # Create exception without stderr attribute
            error = subprocess.CalledProcessError(1, "gh")
            if hasattr(error, "stderr"):
                delattr(error, "stderr")
            mock_run.side_effect = error

            result = post_phase3_comment(pr, comment_text, None)

            assert result is False
