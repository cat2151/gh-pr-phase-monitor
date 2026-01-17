"""
Time formatting utilities
"""


def format_elapsed_time(seconds: float) -> str:
    """Format elapsed time in Japanese style

    Args:
        seconds: Elapsed time in seconds

    Returns:
        Formatted string like "3分20秒"
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)

    if minutes > 0:
        return f"{minutes}分{secs}秒"
    else:
        return f"{secs}秒"
