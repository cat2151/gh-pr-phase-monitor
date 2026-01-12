"""
GitHub PR Phase Monitor

Monitors PR phases and opens browser for actionable phases
"""

from .colors import Colors, colorize_phase
from .comment_manager import (
    has_copilot_apply_comment,
    post_phase2_comment,
)
from .config import get_config_mtime, load_config, parse_interval, get_phase3_merge_config, get_assign_to_copilot_config
from .github_client import (
    get_current_user,
    get_existing_comments,
    get_pr_data,
    get_pr_details_batch,
    get_repositories_with_open_prs,
)
from .phase_detector import (
    determine_phase,
    has_comments_with_reactions,
    has_inline_review_comments,
    has_unresolved_review_threads,
)
from .pr_actions import mark_pr_ready, open_browser, process_pr, process_repository

__all__ = [
    # Colors
    "Colors",
    "colorize_phase",
    # Config
    "get_config_mtime",
    "load_config",
    "parse_interval",
    "get_phase3_merge_config",
    "get_assign_to_copilot_config",
    # GitHub Client
    "get_current_user",
    "get_repositories_with_open_prs",
    "get_pr_details_batch",
    "get_pr_data",
    "get_existing_comments",
    # Phase Detector
    "determine_phase",
    "has_comments_with_reactions",
    "has_inline_review_comments",
    "has_unresolved_review_threads",
    # Comment Manager
    "has_copilot_apply_comment",
    "post_phase2_comment",
    # PR Actions
    "mark_pr_ready",
    "open_browser",
    "process_pr",
    "process_repository",
]
