"""
ANSI color codes and colorization functions for terminal output
"""


class Colors:
    """ANSI color codes for terminal output"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    RED = "\033[91m"
    BLUE = "\033[94m"


def colorize_phase(phase: str) -> str:
    """Add color to phase string

    Args:
        phase: Phase string (phase1, phase2, phase3, or LLM working)

    Returns:
        Colorized phase string with ANSI codes
    """
    if phase == "phase1":
        return f"{Colors.BOLD}{Colors.YELLOW}[{phase}]{Colors.RESET}"
    elif phase == "phase2":
        return f"{Colors.BOLD}{Colors.CYAN}[{phase}]{Colors.RESET}"
    elif phase == "phase3":
        return f"{Colors.BOLD}{Colors.GREEN}[{phase}]{Colors.RESET}"
    else:  # LLM working
        return f"{Colors.BOLD}{Colors.MAGENTA}[{phase}]{Colors.RESET}"
