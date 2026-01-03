"""
Tests for posting comments to PRs when phase2 or phase3 is detected
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from gh_pr_phase_monitor import (
    get_current_user,
    get_existing_comments,
    has_copilot_apply_comment,
    has_phase3_review_comment,
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
        mock_run.return_value = MagicMock(returncode=0, stdout="testuser\n")

        result = get_current_user()

        assert result == "testuser"
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd == ["gh", "api", "user", "--jq", ".login"]

    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_get_current_user_failure(self, mock_run):
        """Test handling of failure to retrieve current user"""
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["gh", "api", "user"])

        result = get_current_user()

        assert result == ""


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
            {"body": "@user 🎁レビューお願いします🎁 : Copilot has finished applying the changes. Please review the updates."},
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
    def test_post_comment_success(self, mock_run, mock_get_comments, mock_get_user):
        """Test successful comment posting"""
        mock_get_comments.return_value = []
        mock_get_user.return_value = "currentuser"
        mock_run.return_value = MagicMock(returncode=0)

        pr = {
            "url": "https://github.com/user/repo/pull/123",
        }
        repo_dir = Path("/tmp/test-repo")

        result = post_phase3_comment(pr, repo_dir)

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
        assert "@currentuser" in cmd[5]
        assert "🎁レビューお願いします🎁" in cmd[5]
        assert "Please review the updates" in cmd[5]

    @patch("gh_pr_phase_monitor.get_current_user")
    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_without_current_user(self, mock_run, mock_get_comments, mock_get_user):
        """Test comment posting without current user"""
        mock_get_comments.return_value = []
        mock_get_user.return_value = ""
        mock_run.return_value = MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123"}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase3_comment(pr, repo_dir)

        assert result is True
        assert mock_run.call_count == 1

        # Verify command arguments
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[5].startswith("🎁レビューお願いします🎁")
        assert "@" not in cmd[5] or "@" == cmd[5][0]  # No @ or at start

    @patch("gh_pr_phase_monitor.get_current_user")
    @patch("gh_pr_phase_monitor.get_existing_comments")
    @patch("gh_pr_phase_monitor.subprocess.run")
    def test_post_comment_skips_if_exists(self, mock_run, mock_get_comments, mock_get_user):
        """Test that comment posting is skipped if comment already exists"""
        mock_get_comments.return_value = [
            {"body": "@currentuser 🎁レビューお願いします🎁 : Copilot has finished applying the changes. Please review the updates."}
        ]
        mock_get_user.return_value = "currentuser"

        pr = {"url": "https://github.com/user/repo/pull/123"}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase3_comment(pr, repo_dir)

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

        result = post_phase3_comment(pr, repo_dir)

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

        post_phase3_comment(pr, repo_dir)

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

        result = post_phase3_comment(pr, repo_dir)

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

        result = post_phase3_comment(pr, repo_dir)

        assert result is False

