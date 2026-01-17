"""
Monitoring logic for state changes and frequency adjustment
"""

import time
from typing import Any, Dict, List, Optional

from .config import parse_interval
from .state_tracker import get_last_state, is_reduced_frequency_mode, set_last_state, set_reduced_frequency_mode
from .time_utils import format_elapsed_time


def check_no_state_change_timeout(
    all_prs: List[Dict[str, Any]], pr_phases: List[str], config: Optional[Dict[str, Any]] = None
) -> bool:
    """Check if the overall PR state has not changed for too long and switch to reduced frequency mode

    This tracks when ANY change happens in the PR state (phase changes, PRs added/removed).
    Timer starts when the state first becomes stable and resets on any state change.
    When timeout is reached, monitoring switches to reduced frequency mode (using the configured reduced_frequency_interval).
    When changes are detected, monitoring returns to normal frequency mode.

    Args:
        all_prs: List of all PRs
        pr_phases: List of phase strings corresponding to all_prs
        config: Configuration dictionary (optional)

    Returns:
        True if monitoring should switch to reduced frequency mode, False otherwise
    """
    # Get timeout setting from config with default of "30m"
    timeout_str = (config or {}).get("no_change_timeout", "30m")

    # Get reduced frequency interval setting from config with default of "1h"
    reduced_interval_str = (config or {}).get("reduced_frequency_interval", "1h")

    # If timeout is explicitly set to empty string (disabled), don't check
    if not timeout_str:
        set_last_state(None)
        set_reduced_frequency_mode(False)
        return False

    # Parse timeout to seconds
    try:
        timeout_seconds = parse_interval(timeout_str)
    except ValueError as e:
        print(f"Warning: Invalid no_change_timeout format: {e}")
        set_last_state(None)
        set_reduced_frequency_mode(False)
        return False

    current_time = time.time()

    # Create a snapshot of current state
    # Validate that all_prs and pr_phases have the same length
    if all_prs and pr_phases and len(all_prs) == len(pr_phases):
        # Create frozenset of (url, phase) tuples to represent current state
        current_state = frozenset((pr.get("url", ""), phase) for pr, phase in zip(all_prs, pr_phases))
    else:
        # Invalid or empty state
        current_state = frozenset()

    # Check if state has changed
    last_state = get_last_state()
    if last_state is None:
        # First check - initialize the state
        set_last_state((current_state, current_time))
        set_reduced_frequency_mode(False)
    elif last_state[0] != current_state:
        # State has changed - reset timer and return to normal mode
        set_last_state((current_state, current_time))
        if is_reduced_frequency_mode():
            # Switching back to normal monitoring
            print(f"\n{'=' * 50}")
            print("PRの状態に変化を検知しました。")
            print("通常の監視間隔に戻ります。")
            print(f"{'=' * 50}")
        set_reduced_frequency_mode(False)
    else:
        # State is unchanged - check if timeout has been reached
        state_start_time = last_state[1]
        elapsed = current_time - state_start_time
        if elapsed >= timeout_seconds and not is_reduced_frequency_mode():
            # Timeout reached - switch to reduced frequency mode
            elapsed_str = format_elapsed_time(elapsed)
            print(f"\n{'=' * 50}")
            print(f"PRの状態に変化がない状態が{timeout_str}（{elapsed_str}）続きました。")
            print(f"API利用の浪費を防止するため、監視間隔を{reduced_interval_str}に変更します。")
            print("変化があったら元の監視間隔に戻ります。")
            print(f"{'=' * 50}")
            set_reduced_frequency_mode(True)

    return is_reduced_frequency_mode()
