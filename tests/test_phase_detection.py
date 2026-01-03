"""
Tests for PR phase detection logic

Tests cover the following scenarios:
- Phase 1: Draft PRs
- Phase 2: Copilot reviewer with comments/changes requested
- Phase 3: Copilot reviewer approved or no comments, copilot-swe-agent modifications
- LLM working: No reviews or unknown reviewers
"""

from pathlib import Path

from gh_pr_phase_monitor import determine_phase


class TestDeterminePhase:
    """Test the determine_phase function"""

    def test_phase1_draft_pr(self):
        """Draft PRs with reviewRequests should be phase1"""
        pr = {"isDraft": True, "reviews": [], "latestReviews": [], "reviewRequests": [{"login": "user1"}]}
        assert determine_phase(pr) == "phase1"

    def test_llm_working_draft_pr_no_review_requests(self):
        """Draft PRs with no reviewRequests should be 'LLM working'"""
        pr = {"isDraft": True, "reviews": [], "latestReviews": [], "reviewRequests": []}
        assert determine_phase(pr) == "LLM working"

    def test_llm_working_no_reviews(self):
        """PRs with no reviews should be 'LLM working'"""
        pr = {"isDraft": False, "reviews": [], "latestReviews": []}
        assert determine_phase(pr) == "LLM working"

    def test_phase3_copilot_reviewer_commented_with_summary(self):
        """Copilot reviewer with COMMENTED state and summary body should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nThis PR adds comprehensive documentation.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_reviewer_approved(self):
        """Copilot reviewer with APPROVED state should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED", "body": "Looks good!"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_reviewer_no_body(self):
        """Copilot reviewer with no review body should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED", "body": ""}],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_reviewer_whitespace_only_body(self):
        """Copilot reviewer with only whitespace in body should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED", "body": "   \n  \t  "}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_swe_agent(self):
        """Copilot SWE agent as latest reviewer should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "Please fix issues",
                },
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": "Fixed the issues"},
            ],
            "latestReviews": [{"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED"}],
        }
        assert determine_phase(pr) == "phase3"

    def test_llm_working_unknown_reviewer(self):
        """Unknown reviewer should be 'LLM working'"""
        pr = {
            "isDraft": False,
            "reviews": [{"author": {"login": "some-other-bot"}, "state": "COMMENTED", "body": "Some comment"}],
            "latestReviews": [{"author": {"login": "some-other-bot"}, "state": "COMMENTED"}],
        }
        assert determine_phase(pr) == "LLM working"

    def test_phase2_changes_requested(self):
        """Copilot reviewer with CHANGES_REQUESTED should be phase2"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "CHANGES_REQUESTED",
                    "body": "Please address these issues",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "CHANGES_REQUESTED"}],
        }
        assert determine_phase(pr) == "phase2"

    def test_phase3_copilot_reviewer_dismissed(self):
        """Copilot reviewer with DISMISSED state should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "DISMISSED", "body": "Review dismissed"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "DISMISSED"}],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_reviewer_pending(self):
        """Copilot reviewer with PENDING state should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "PENDING", "body": "Review pending"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "PENDING"}],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase2_copilot_reviewer_commented_with_review_comments(self, mocker):
        """Copilot reviewer with COMMENTED state and inline review comments should be phase2"""
        # Mock the has_review_comments_from_author function to return True
        mock_has_review_comments = mocker.patch(
            "gh_pr_phase_monitor.has_review_comments_from_author", return_value=True
        )

        pr = {
            "isDraft": False,
            "url": "https://github.com/owner/repo/pull/123",
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Review comments\n\nPlease see inline comments.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
        }
        repo_dir = Path("/tmp/test-repo")

        assert determine_phase(pr, repo_dir) == "phase2"
        mock_has_review_comments.assert_called_once_with(
            "https://github.com/owner/repo/pull/123", repo_dir, "copilot-pull-request-reviewer"
        )

    def test_phase3_copilot_reviewer_commented_without_review_comments(self, mocker):
        """Copilot reviewer with COMMENTED state but no inline review comments should be phase3"""
        # Mock the has_review_comments_from_author function to return False
        mock_has_review_comments = mocker.patch(
            "gh_pr_phase_monitor.has_review_comments_from_author", return_value=False
        )

        pr = {
            "isDraft": False,
            "url": "https://github.com/owner/repo/pull/123",
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nThis PR looks good overall.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
        }
        repo_dir = Path("/tmp/test-repo")

        assert determine_phase(pr, repo_dir) == "phase3"
        mock_has_review_comments.assert_called_once_with(
            "https://github.com/owner/repo/pull/123", repo_dir, "copilot-pull-request-reviewer"
        )
