"""
Tests for PR phase detection logic

Tests cover the following scenarios:
- Phase 1: Draft PRs
- Phase 2: Copilot reviewer with comments/changes requested
- Phase 3: Copilot reviewer approved or no comments, copilot-swe-agent modifications
- LLM working: No reviews, unknown reviewers, or comments with reactions
"""

from src.gh_pr_phase_monitor import determine_phase, has_comments_with_reactions


class TestHasCommentsWithReactions:
    """Test the has_comments_with_reactions function"""

    def test_no_comments(self):
        """Empty comments list should return False"""
        assert has_comments_with_reactions([]) is False

    def test_comments_without_reactions(self):
        """Comments without reactionGroups should return False"""
        comments = [
            {"body": "Test comment 1"},
            {"body": "Test comment 2"},
        ]
        assert has_comments_with_reactions(comments) is False

    def test_comments_with_empty_reaction_groups(self):
        """Comments with empty reactionGroups should return False"""
        comments = [
            {"body": "Test comment", "reactionGroups": []},
        ]
        assert has_comments_with_reactions(comments) is False

    def test_comments_with_zero_count_reactions(self):
        """Comments with reactionGroups but zero users should return False"""
        comments = [
            {
                "body": "Test comment",
                "reactionGroups": [
                    {"content": "THUMBS_UP", "users": {"totalCount": 0}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is False

    def test_comments_with_reactions(self):
        """Comments with non-empty reactionGroups should return True"""
        comments = [
            {
                "body": "Test comment",
                "reactionGroups": [
                    {"content": "THUMBS_UP", "users": {"totalCount": 1}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is True

    def test_multiple_comments_with_reactions(self):
        """Multiple comments, one with reactions should return True"""
        comments = [
            {"body": "Test comment 1"},
            {
                "body": "Test comment 2",
                "reactionGroups": [
                    {"content": "EYES", "users": {"totalCount": 2}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is True

    def test_multiple_reaction_groups(self):
        """Comment with multiple reaction groups should return True"""
        comments = [
            {
                "body": "Test comment",
                "reactionGroups": [
                    {"content": "THUMBS_UP", "users": {"totalCount": 0}},
                    {"content": "EYES", "users": {"totalCount": 1}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is True

    def test_backward_compatibility_with_integer(self):
        """Integer comments (from legacy API) should return False"""
        assert has_comments_with_reactions(5) is False

    def test_backward_compatibility_with_none(self):
        """None comments should return False"""
        assert has_comments_with_reactions(None) is False


class TestDeterminePhase:
    """Test the determine_phase function"""

    def test_phase1_draft_pr(self):
        """Draft PRs with reviewRequests should be phase1"""
        pr = {"isDraft": True, "reviews": [], "latestReviews": [], "reviewRequests": [{"login": "user1"}], "comments": []}
        assert determine_phase(pr) == "phase1"

    def test_llm_working_draft_pr_no_review_requests(self):
        """Draft PRs with no reviewRequests should be 'LLM working'"""
        pr = {"isDraft": True, "reviews": [], "latestReviews": [], "reviewRequests": [], "comments": []}
        assert determine_phase(pr) == "LLM working"

    def test_llm_working_no_reviews(self):
        """PRs with no reviews should be 'LLM working'"""
        pr = {"isDraft": False, "reviews": [], "latestReviews": [], "comments": []}
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
            "comments": [],
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
            "comments": [],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_reviewer_no_body(self):
        """Copilot reviewer with no review body should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED", "body": ""}],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "comments": [],
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
            "comments": [],
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
            "comments": [],
        }
        assert determine_phase(pr) == "phase3"

    def test_llm_working_unknown_reviewer(self):
        """Unknown reviewer should be 'LLM working'"""
        pr = {
            "isDraft": False,
            "reviews": [{"author": {"login": "some-other-bot"}, "state": "COMMENTED", "body": "Some comment"}],
            "latestReviews": [{"author": {"login": "some-other-bot"}, "state": "COMMENTED"}],
            "comments": [],
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
            "comments": [],
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
            "comments": [],
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
            "comments": [],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase2_copilot_reviewer_commented_with_review_comments(self):
        """Copilot reviewer with COMMENTED state and inline review comments should be phase2"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "Copilot reviewed 2 out of 2 changed files in this pull request and generated 1 comment.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "comments": [],
        }

        assert determine_phase(pr) == "phase2"

    def test_phase3_copilot_reviewer_commented_without_review_comments(self):
        """Copilot reviewer with COMMENTED state but no inline review comments should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nThis PR looks good overall.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "comments": [],
        }

        assert determine_phase(pr) == "phase3"

    def test_llm_working_when_comments_have_reactions(self):
        """PR with comments that have reactions should be 'LLM working'"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "Copilot reviewed 2 out of 2 changed files in this pull request and generated 1 comment.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "commentNodes": [
                {
                    "body": "Please fix this issue",
                    "reactionGroups": [
                        {"content": "EYES", "users": {"totalCount": 1}},
                    ],
                }
            ],
        }

        assert determine_phase(pr) == "LLM working"

    def test_phase2_when_comments_without_reactions(self):
        """PR with review comments but no reactions should still be phase2"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "Copilot reviewed 2 out of 2 changed files in this pull request and generated 1 comment.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "commentNodes": [
                {"body": "Please fix this issue", "reactionGroups": []},
            ],
        }

        assert determine_phase(pr) == "phase2"

    def test_llm_working_phase3_scenario_with_reactions(self):
        """PR that would be phase3 but has comments with reactions should be 'LLM working'"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nThis PR looks good overall.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "commentNodes": [
                {
                    "body": "Some comment",
                    "reactionGroups": [
                        {"content": "ROCKET", "users": {"totalCount": 1}},
                    ],
                }
            ],
        }

        assert determine_phase(pr) == "LLM working"

    def test_backward_compatibility_with_integer_comments(self):
        """PR with integer comments (legacy API) should work correctly"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "Copilot reviewed 2 out of 2 changed files in this pull request and generated 1 comment.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "comments": 5,  # Legacy API returns integer
        }

        assert determine_phase(pr) == "phase2"
