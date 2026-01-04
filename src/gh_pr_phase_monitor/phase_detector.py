"""
PR phase detection logic based on reviews and PR state
"""

import re
from typing import Any, Dict, List, Union

# Phase constants
PHASE_LLM_WORKING = "LLM working"
PHASE_1 = "phase1"
PHASE_2 = "phase2"
PHASE_3 = "phase3"


def has_comments_with_reactions(comments: Union[List[Dict[str, Any]], int, None]) -> bool:
    """Check if any comments have non-empty reactionGroups

    When the LLM (coding agent) is working on addressing PR comments
    (general pull request comments fetched via the `comments` field),
    those comments may have reactions (GitHub reactions like 👍, 👎, 😄, 🎉,
    😕, ❤️, 🚀, 👀, etc.) indicating the bot is processing them.
    This indicates the LLM is actively working.

    Args:
        comments: List of comment dictionaries with reactionGroups, or None/integer for backward compatibility

    Returns:
        True if any comment has non-empty reactionGroups, False otherwise
    """
    # Handle backward compatibility: comments might be an integer or None from legacy API
    if not comments or not isinstance(comments, list):
        return False

    for comment in comments:
        reaction_groups = comment.get("reactionGroups", [])
        if reaction_groups:
            # Check if any reaction group has users
            for group in reaction_groups:
                users = group.get("users", {})
                total_count = users.get("totalCount", 0)
                if total_count > 0:
                    return True

    return False


def has_inline_review_comments(review_body: str) -> bool:
    """Check if review body indicates inline code comments were generated

    Copilot's review body contains text like:
    "Copilot reviewed X out of Y changed files in this pull request and generated N comment(s)."
    when inline comments are present.

    Args:
        review_body: The body text of the review

    Returns:
        True if the review body indicates inline comments exist, False otherwise
    """
    if not review_body:
        return False

    # Check for the pattern indicating inline comments were generated
    # Pattern matches: "generated 1 comment" or "generated 2 comments" etc.
    pattern = r"generated\s+\d+\s+comments?"
    return bool(re.search(pattern, review_body, re.IGNORECASE))


def determine_phase(pr: Dict[str, Any]) -> str:
    """Determine which phase the PR is in

    Args:
        pr: PR data dictionary

    Returns:
        Phase string: PHASE_1, PHASE_2, PHASE_3, or PHASE_LLM_WORKING
    """
    is_draft = pr.get("isDraft", False)
    reviews = pr.get("reviews", [])
    latest_reviews = pr.get("latestReviews", [])
    review_requests = pr.get("reviewRequests", [])
    # Use commentNodes if available (new API), fall back to comments for legacy compatibility
    comment_nodes = pr.get("commentNodes", pr.get("comments", []))

    # Check if any comments have reactions - this indicates LLM is working
    # When the coding agent is responding to PR comments, those comments
    # may have reactions indicating the bot is processing them
    if has_comments_with_reactions(comment_nodes):
        return PHASE_LLM_WORKING

    # Phase 1: Draft状態 (ただし、reviewRequestsが空の場合はLLM working)
    if is_draft:
        # reviewRequestsが空なら、LLM workingと判定
        if not review_requests:
            return PHASE_LLM_WORKING
        return PHASE_1

    # Phase 2 と Phase 3 の判定には reviews が必要
    if not reviews or not latest_reviews:
        return PHASE_LLM_WORKING

    # 最新のレビューを取得
    latest_review = reviews[-1]
    author_login = latest_review.get("author", {}).get("login", "")

    # Phase 2/3: copilot-pull-request-reviewer のレビュー後
    if author_login == "copilot-pull-request-reviewer":
        # レビューの状態を確認
        review_state = latest_review.get("state", "")

        # CHANGES_REQUESTEDの場合は確実にphase2
        if review_state == "CHANGES_REQUESTED":
            return PHASE_2

        # COMMENTEDの場合、レビュー本文にインラインコメントの存在を示すパターンがあるかチェック
        # レビューコメントがある場合はphase2（修正が必要）、ない場合はphase3（レビュー待ち）
        if review_state == "COMMENTED":
            review_body = latest_review.get("body", "")
            if has_inline_review_comments(review_body):
                return PHASE_2
            # レビューコメントがない場合はphase3
            return PHASE_3

        # それ以外(APPROVED, DISMISSED, PENDING等)はphase3
        return PHASE_3

    # Phase 3: copilot-swe-agent の修正後
    # ただし、copilot-pull-request-reviewerの未解決レビューがある場合はphase2
    if author_login == "copilot-swe-agent":
        # copilot-pull-request-reviewerのレビューを探す（最新から逆順で）
        for review in reversed(reviews):
            reviewer_login = review.get("author", {}).get("login", "")
            if reviewer_login == "copilot-pull-request-reviewer":
                review_state = review.get("state", "")
                review_body = review.get("body", "")

                # CHANGES_REQUESTEDの場合はphase2
                if review_state == "CHANGES_REQUESTED":
                    return PHASE_2

                # インラインレビューコメントがある場合はphase2
                if review_state == "COMMENTED" and has_inline_review_comments(review_body):
                    return PHASE_2

        # 未解決のレビューコメントがない場合はphase3
        return PHASE_3

    return PHASE_LLM_WORKING
