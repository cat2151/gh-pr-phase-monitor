"""
Tests for posting comments to PRs when phase2 or phase3 is detected
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gh_pr_phase_monitor import (
    get_current_user,
    get_existing_comments,
    has_copilot_apply_comment,
    has_phase3_review_comment,
    mark_pr_ready,
    post_phase2_comment,
    post_phase3_comment,
)


class TestGetExistingComments:
    """Test the get_existing_comments function"""

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_get_comments_success(self, mock_run):
        """Test successful retrieval of comments"""
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps({"comments": [{"body": "Test comment"}]}))

        pr_url = "https://github.com/user/repo/pull/123"
        repo_dir = Path("/tmp/test-repo")

        result = get_existing_comments(pr_url, repo_dir)

        assert len(result) == 1
        assert result[0]["body"] == "Test comment"

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_get_comments_failure(self, mock_run):
        """Test handling of failure to retrieve comments"""
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "view"])

        pr_url = "https://github.com/user/repo/pull/999"
        repo_dir = Path("/tmp/test-repo")

        result = get_existing_comments(pr_url, repo_dir)

        assert result == []


class TestHasCopilotApplyComment:
    """Test the has_copilot_apply_comment function"""

    def test_comment_exists(self):
        """Test detection when comment exists"""
        comments = [
            {"body": "Some other comment"},
            {"body": "@copilot apply changes based on the comments"},
            {"body": "Another comment"},
        ]

        assert has_copilot_apply_comment(comments) is True

    def test_comment_does_not_exist(self):
        """Test detection when comment does not exist"""
        comments = [{"body": "Some other comment"}, {"body": "Another comment"}]

        assert has_copilot_apply_comment(comments) is False

    def test_empty_comments(self):
        """Test with empty comment list"""
        assert has_copilot_apply_comment([]) is False


class TestGetCurrentUser:
    """Test the get_current_user function"""

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_get_current_user_success(self, mock_run):
        """Test successful retrieval of current user"""
        # Reset cache before test
        import gh_pr_phase_monitor

        gh_pr_phase_monitor._current_user_cache = None

        mock_run.return_value = MagicMock(returncode=0, stdout="testuser\n")

        result = get_current_user()

        assert result == "testuser"
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd == ["gh", "api", "user", "--jq", ".login"]

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_get_current_user_failure(self, mock_run):
        """Test handling of failure to retrieve current user"""
        # Reset cache before test
        import gh_pr_phase_monitor

        gh_pr_phase_monitor._current_user_cache = None

        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["gh", "api", "user"])

        with pytest.raises(RuntimeError, match="Failed to retrieve current GitHub user"):
            get_current_user()

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_get_current_user_uses_cache(self, mock_run):
        """Test that get_current_user uses cached value on subsequent calls"""
        # Reset cache before test
        import gh_pr_phase_monitor

        gh_pr_phase_monitor._current_user_cache = None

        mock_run.return_value = MagicMock(returncode=0, stdout="testuser\n")

        # First call should execute subprocess
        result1 = get_current_user()
        assert result1 == "testuser"
        assert mock_run.call_count == 1

        # Second call should use cache, no additional subprocess call
        result2 = get_current_user()
        assert result2 == "testuser"
        assert mock_run.call_count == 1  # Still only called once

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_get_current_user_does_not_cache_failures(self, mock_run):
        """Test that authentication failures are not cached, allowing retries"""
        # Reset cache before test
        import gh_pr_phase_monitor

        gh_pr_phase_monitor._current_user_cache = None

        # First call fails
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["gh", "api", "user"])
        with pytest.raises(RuntimeError):
            get_current_user()
        assert mock_run.call_count == 1

        # Second call should retry (not use cached failure)
        mock_run.side_effect = None
        mock_run.return_value = MagicMock(returncode=0, stdout="testuser\n")
        result2 = get_current_user()
        assert result2 == "testuser"
        assert mock_run.call_count == 2  # Called twice, allowing retry


class TestPostPhase2Comment:
    """Test the post_phase2_comment function"""

    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_success(self, mock_run, mock_get_comments):
        """Test successful comment posting"""
        mock_get_comments.return_value = []
        mock_run.return_value = MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123", "reviews": [{"author": {"login": "copilot"}}]}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr, repo_dir)

        assert result is True
        assert mock_run.call_count == 1

        # Verify command arguments
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[0] == "gh"
        assert cmd[1] == "pr"
        assert cmd[2] == "comment"
        assert cmd[3] == "https://github.com/user/repo/pull/123"
        assert cmd[4] == "--body"
        assert "@copilot apply changes" in cmd[5]
        assert "this pull request" in cmd[5]

    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_skips_if_exists(self, mock_run, mock_get_comments):
        """Test that comment posting is skipped if comment already exists"""
        mock_get_comments.return_value = [{"body": "@copilot apply changes based on the comments"}]

        pr = {"url": "https://github.com/user/repo/pull/123", "reviews": []}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr, repo_dir)

        assert result is True
        mock_run.assert_not_called()

    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_failure(self, mock_run, mock_get_comments):
        """Test failed comment posting"""
        mock_get_comments.return_value = []
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "comment"])
        error.stderr = "Error: PR not found"
        mock_run.side_effect = error

        pr = {"url": "https://github.com/user/repo/pull/999", "reviews": []}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr, repo_dir)

        assert result is False

    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_with_correct_cwd(self, mock_run, mock_get_comments):
        """Test that comment posting uses correct working directory"""
        mock_get_comments.return_value = []
        mock_run.return_value = MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123", "reviews": []}
        repo_dir = Path("/custom/repo/path")

        post_phase2_comment(pr, repo_dir)

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cwd"] == repo_dir

    @patch("gh_pr_phase_monitor.get_existing_comments")
    def test_post_comment_no_url(self, mock_get_comments):
        """Test handling of PR without URL"""
        mock_get_comments.return_value = []

        pr = {"reviews": []}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr, repo_dir)

        assert result is False

    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_handles_missing_stderr(self, mock_run, mock_get_comments):
        """Test that missing stderr is handled gracefully"""
        mock_get_comments.return_value = []
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "comment"])
        # Don't set stderr attribute
        mock_run.side_effect = error

        pr = {"url": "https://github.com/user/repo/pull/999", "reviews": []}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr, repo_dir)

        assert result is False


class TestHasPhase3ReviewComment:
    """Test the has_phase3_review_comment function"""

    def test_comment_exists_japanese(self):
        """Test detection when Japanese review comment exists"""
        comments = [
            {"body": "Some other comment"},
            {
                "body": "@user 🎁レビューお願いします🎁 : Copilot has finished applying the changes. Please review the updates."
            },
            {"body": "Another comment"},
        ]

        assert has_phase3_review_comment(comments) is True

    def test_comment_exists_english(self):
        """Test detection when English review comment exists"""
        comments = [
            {"body": "Some other comment"},
            {"body": "Please review the updates."},
            {"body": "Another comment"},
        ]

        assert has_phase3_review_comment(comments) is True

    def test_comment_does_not_exist(self):
        """Test detection when comment does not exist"""
        comments = [{"body": "Some other comment"}, {"body": "Another comment"}]

        assert has_phase3_review_comment(comments) is False

    def test_empty_comments(self):
        """Test with empty comment list"""
        assert has_phase3_review_comment([]) is False


class TestPostPhase3Comment:
    """Test the post_phase3_comment function"""

    @patch("gh_pr_phase_monitor.get_current_user")
    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_success_with_user(self, mock_run, mock_get_comments, mock_get_user):
        """Test successful comment posting with current user"""
        mock_get_comments.return_value = []
        mock_get_user.return_value = "currentuser"
        mock_run.return_value = MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123"}
        repo_dir = Path("/tmp/test-repo")
        custom_text = "🎁レビューお願いします🎁 : Copilot has finished applying the changes. Please review the updates."

        result = post_phase3_comment(pr, repo_dir, custom_text)

        assert result is True
        assert mock_run.call_count == 1

        # Verify command arguments
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[0] == "gh"
        assert cmd[1] == "pr"
        assert cmd[2] == "comment"
        assert cmd[3] == "https://github.com/user/repo/pull/123"
        assert cmd[4] == "--body"
        # Should be "@currentuser " + custom_text
        assert (
            cmd[5]
            == "@currentuser 🎁レビューお願いします🎁 : Copilot has finished applying the changes. Please review the updates."
        )

    @patch("gh_pr_phase_monitor.get_current_user")
    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_without_current_user_raises_error(self, mock_run, mock_get_comments, mock_get_user):
        """Test comment posting fails when current user cannot be determined"""
        mock_get_comments.return_value = []
        mock_get_user.side_effect = RuntimeError("Failed to retrieve current GitHub user")
        mock_run.return_value = MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123"}
        repo_dir = Path("/tmp/test-repo")
        custom_text = "🎁レビューお願いします🎁 : Copilot has finished applying the changes. Please review the updates."

        with pytest.raises(RuntimeError, match="Failed to retrieve current GitHub user"):
            post_phase3_comment(pr, repo_dir, custom_text)

        # Should not have attempted to post comment
        mock_run.assert_not_called()

    @patch("gh_pr_phase_monitor.get_current_user")
    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_with_custom_text(self, mock_run, mock_get_comments, mock_get_user):
        """Test comment posting with custom text"""
        mock_get_comments.return_value = []
        mock_get_user.return_value = "testuser"
        mock_run.return_value = MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123"}
        repo_dir = Path("/tmp/test-repo")
        custom_text = "Please review this PR!"

        result = post_phase3_comment(pr, repo_dir, custom_text)

        assert result is True
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[5] == "@testuser Please review this PR!"

    @patch("gh_pr_phase_monitor.get_current_user")
    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_skips_if_exists(self, mock_run, mock_get_comments, mock_get_user):
        """Test that comment posting is skipped if comment already exists"""
        mock_get_comments.return_value = [
            {
                "body": "@currentuser 🎁レビューお願いします🎁 : Copilot has finished applying the changes. Please review the updates."
            }
        ]
        mock_get_user.return_value = "currentuser"

        pr = {"url": "https://github.com/user/repo/pull/123"}
        repo_dir = Path("/tmp/test-repo")
        custom_text = "🎁レビューお願いします🎁 : Copilot has finished applying the changes. Please review the updates."

        result = post_phase3_comment(pr, repo_dir, custom_text)

        assert result is True
        mock_run.assert_not_called()

    @patch("gh_pr_phase_monitor.get_current_user")
    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_failure(self, mock_run, mock_get_comments, mock_get_user):
        """Test failed comment posting"""
        mock_get_comments.return_value = []
        mock_get_user.return_value = "currentuser"
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "comment"])
        error.stderr = "Error: PR not found"
        mock_run.side_effect = error

        pr = {"url": "https://github.com/user/repo/pull/999"}
        repo_dir = Path("/tmp/test-repo")
        custom_text = "Please review!"

        result = post_phase3_comment(pr, repo_dir, custom_text)

        assert result is False

    @patch("gh_pr_phase_monitor.get_current_user")
    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_with_correct_cwd(self, mock_run, mock_get_comments, mock_get_user):
        """Test that comment posting uses correct working directory"""
        mock_get_comments.return_value = []
        mock_get_user.return_value = "currentuser"
        mock_run.return_value = MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123"}
        repo_dir = Path("/custom/repo/path")
        custom_text = "Please review!"

        post_phase3_comment(pr, repo_dir, custom_text)

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cwd"] == repo_dir

    @patch("gh_pr_phase_monitor.get_current_user")
    @patch("gh_pr_phase_monitor.get_existing_comments")
    def test_post_comment_no_url(self, mock_get_comments, mock_get_user):
        """Test handling of PR without URL"""
        mock_get_comments.return_value = []
        mock_get_user.return_value = "currentuser"

        pr = {}
        repo_dir = Path("/tmp/test-repo")
        custom_text = "Please review!"

        result = post_phase3_comment(pr, repo_dir, custom_text)

        assert result is False

    @patch("gh_pr_phase_monitor.get_current_user")
    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_handles_missing_stderr(self, mock_run, mock_get_comments, mock_get_user):
        """Test that missing stderr is handled gracefully"""
        mock_get_comments.return_value = []
        mock_get_user.return_value = "currentuser"
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "comment"])
        # Don't set stderr attribute
        mock_run.side_effect = error

        pr = {"url": "https://github.com/user/repo/pull/999"}
        repo_dir = Path("/tmp/test-repo")
        custom_text = "Please review!"

        result = post_phase3_comment(pr, repo_dir, custom_text)

        assert result is False


class TestMarkPRReady:
    """Test the mark_pr_ready function"""

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_mark_pr_ready_success(self, mock_run):
        """Test successful marking of PR as ready for review"""
        mock_run.return_value = MagicMock(returncode=0)

        pr_url = "https://github.com/user/repo/pull/123"
        repo_dir = Path("/tmp/test-repo")

        result = mark_pr_ready(pr_url, repo_dir)

        assert result is True
        assert mock_run.call_count == 1

        # Verify command arguments
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd == ["gh", "pr", "ready", "https://github.com/user/repo/pull/123"]

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_mark_pr_ready_failure(self, mock_run):
        """Test failed marking of PR as ready"""
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "ready"])
        error.stderr = "Error: PR not found or not a draft"
        mock_run.side_effect = error

        pr_url = "https://github.com/user/repo/pull/999"
        repo_dir = Path("/tmp/test-repo")

        result = mark_pr_ready(pr_url, repo_dir)

        assert result is False

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_mark_pr_ready_with_correct_cwd(self, mock_run):
        """Test that PR ready marking uses correct working directory"""
        mock_run.return_value = MagicMock(returncode=0)

        pr_url = "https://github.com/user/repo/pull/123"
        repo_dir = Path("/custom/repo/path")

        mark_pr_ready(pr_url, repo_dir)

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cwd"] == repo_dir

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_mark_pr_ready_handles_missing_stderr(self, mock_run):
        """Test that missing stderr is handled gracefully"""
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "ready"])
        # Don't set stderr attribute
        mock_run.side_effect = error

        pr_url = "https://github.com/user/repo/pull/999"
        repo_dir = Path("/tmp/test-repo")

        result = mark_pr_ready(pr_url, repo_dir)

        assert result is False
