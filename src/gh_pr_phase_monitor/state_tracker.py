"""
State tracking for PRs and monitoring mode
"""

from typing import Dict, List, Optional, Tuple

# Track PR states and detection times
# Key: (pr_url, phase), Value: timestamp when first detected
_pr_state_times: Dict[Tuple[str, str], float] = {}

# Track when the overall PR state last changed
# This includes: (last_state_snapshot, timestamp when state started)
# State snapshot is a frozenset of (pr_url, phase) tuples
_last_state: Optional[Tuple[frozenset, float]] = None

# Track the current monitoring mode
# True = reduced frequency mode (uses the configured reduced_frequency_interval), False = normal mode
_reduced_frequency_mode: bool = False


def cleanup_old_pr_states(current_prs_with_phases: List[Tuple[str, str]]) -> None:
    """Clean up PR state tracking for PRs that no longer exist or changed phase

    Args:
        current_prs_with_phases: List of tuples (pr_url, phase) for current PRs
    """
    current_keys = set(current_prs_with_phases)
    # Filter the existing state dict in place to keep only current keys
    filtered_states = {key: value for key, value in _pr_state_times.items() if key in current_keys}
    _pr_state_times.clear()
    _pr_state_times.update(filtered_states)


def get_pr_state_time(pr_url: str, phase: str) -> Optional[float]:
    """Get the timestamp when a PR first entered a specific phase

    Args:
        pr_url: PR URL
        phase: Phase string

    Returns:
        Timestamp when first detected, or None if not tracked
    """
    return _pr_state_times.get((pr_url, phase))


def set_pr_state_time(pr_url: str, phase: str, timestamp: float) -> None:
    """Record the timestamp when a PR entered a specific phase

    Args:
        pr_url: PR URL
        phase: Phase string
        timestamp: Timestamp when detected
    """
    _pr_state_times[(pr_url, phase)] = timestamp


def get_last_state() -> Optional[Tuple[frozenset, float]]:
    """Get the last recorded overall PR state

    Returns:
        Tuple of (state_snapshot, timestamp) or None if not set
    """
    return _last_state


def set_last_state(state: Optional[Tuple[frozenset, float]]) -> None:
    """Set the last recorded overall PR state

    Args:
        state: Tuple of (state_snapshot, timestamp) or None to reset
    """
    global _last_state
    _last_state = state


def is_reduced_frequency_mode() -> bool:
    """Check if monitoring is in reduced frequency mode

    Returns:
        True if in reduced frequency mode, False otherwise
    """
    return _reduced_frequency_mode


def set_reduced_frequency_mode(enabled: bool) -> None:
    """Set the monitoring frequency mode

    Args:
        enabled: True to enable reduced frequency mode, False for normal mode
    """
    global _reduced_frequency_mode
    _reduced_frequency_mode = enabled
