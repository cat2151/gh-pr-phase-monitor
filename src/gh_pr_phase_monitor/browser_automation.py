"""Browser automation module for automated button clicking

This module provides functionality to automate clicking buttons in a browser
using PyAutoGUI with image recognition. It's designed to work on Windows PCs
and can be optionally enabled through configuration.

Important: Users must provide screenshots of the buttons they want to click.
See README.ja.md for instructions on how to capture button screenshots.
"""

import time
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

from .config import DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE, is_process_running

# PyAutoGUI imports are optional - will be imported only if automation is enabled
try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None  # Set to None when not available

# Global state to track the last time a browser was opened
# This prevents opening multiple pages simultaneously which can cause issues
# with automated merge and assign operations
_last_browser_open_time: Optional[float] = None

# Minimum time (in seconds) to wait between opening browser pages
BROWSER_OPEN_COOLDOWN_SECONDS = 60

# Track which issue URLs have had assignment attempted with timestamp: dict of URL -> timestamp
# This prevents repeatedly trying to assign the same issue when automation fails
# URLs expire after 24 hours, allowing retries for temporary failures
_issue_assign_attempted: Dict[str, float] = {}

# Time (in seconds) before an issue URL can be retried (24 hours)
ISSUE_ASSIGN_RETRY_AFTER_SECONDS = 24 * 60 * 60


def is_pyautogui_available() -> bool:
    """Check if PyAutoGUI is available for use

    Returns:
        True if PyAutoGUI is installed and available, False otherwise
    """
    return PYAUTOGUI_AVAILABLE


def _can_open_browser() -> bool:
    """Check if enough time has passed since the last browser open

    Returns:
        True if a browser can be opened (cooldown period has passed), False otherwise
    """
    global _last_browser_open_time
    if _last_browser_open_time is None:
        return True
    elapsed = time.time() - _last_browser_open_time
    return elapsed >= BROWSER_OPEN_COOLDOWN_SECONDS


def _record_browser_open() -> None:
    """Record the current time as the last browser open time"""
    global _last_browser_open_time
    _last_browser_open_time = time.time()


def _get_remaining_cooldown() -> float:
    """Get the remaining cooldown time in seconds

    Returns:
        Remaining seconds until next browser can be opened, or 0 if ready
    """
    global _last_browser_open_time
    if _last_browser_open_time is None:
        return 0.0
    elapsed = time.time() - _last_browser_open_time
    remaining = BROWSER_OPEN_COOLDOWN_SECONDS - elapsed
    return max(0.0, remaining)


def _should_autoraise_window(config: Optional[Dict[str, Any]] = None) -> bool:
    """Determine if browser window should be raised to foreground

    Args:
        config: Configuration dictionary

    Returns:
        True if window should be raised, False otherwise
    """
    if config is None:
        config = {}

    # Get the check_process_before_autoraise setting (default: True)
    check_process = config.get("check_process_before_autoraise", DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE)

    # If the setting is disabled, always autoraise
    if not check_process:
        return True

    # If enabled, check if cat-window-watcher is running
    if is_process_running("cat-window-watcher"):
        print("  ℹ cat-window-watcher is running, browser window will not be raised to foreground")
        return False

    return True


def _validate_wait_seconds(config: Dict[str, Any]) -> int:
    """Validate and get wait_seconds from configuration

    Args:
        config: Configuration dict with wait_seconds setting

    Returns:
        Validated wait_seconds value (defaults to 10 if invalid)
    """
    try:
        wait_seconds = int(config.get("wait_seconds", 10))
        if wait_seconds < 0:
            print("  ⚠ wait_seconds must be positive, using default: 10")
            wait_seconds = 10
    except (ValueError, TypeError):
        print("  ⚠ Invalid wait_seconds value in config, using default: 10")
        wait_seconds = 10
    return wait_seconds


def _validate_confidence(config: Dict[str, Any]) -> float:
    """Validate and get confidence from configuration

    Args:
        config: Configuration dict with confidence setting

    Returns:
        Validated confidence value (defaults to 0.8 if invalid)
    """
    try:
        confidence = float(config.get("confidence", 0.8))
        if not 0.0 <= confidence <= 1.0:
            print("  ⚠ confidence must be between 0.0 and 1.0, using default: 0.8")
            confidence = 0.8
    except (ValueError, TypeError):
        print("  ⚠ Invalid confidence value in config, using default: 0.8")
        confidence = 0.8
    return confidence


def _validate_button_delay(config: Dict[str, Any]) -> float:
    """Validate and get button_delay from configuration

    Args:
        config: Configuration dict with button_delay setting

    Returns:
        Validated button_delay value in seconds (defaults to 2.0 if invalid)
    """
    try:
        button_delay = float(config.get("button_delay", 2.0))
        if button_delay < 0:
            print("  ⚠ button_delay must be positive, using default: 2.0")
            button_delay = 2.0
    except (ValueError, TypeError):
        print("  ⚠ Invalid button_delay value in config, using default: 2.0")
        button_delay = 2.0
    return button_delay


def _get_screenshot_path(button_name: str, config: Dict[str, Any]) -> Optional[Path]:
    """Get the path to the button screenshot image

    Args:
        button_name: Name of the button (e.g., "assign_to_copilot", "assign", "merge_pull_request")
        config: Configuration dict (assign_to_copilot or phase3_merge section) with screenshot_dir setting

    Returns:
        Path to the screenshot image, or None if not found
    """
    # Get screenshot directory from config, default to ./screenshots
    screenshot_dir_str = config.get("screenshot_dir", "screenshots")
    screenshot_dir = Path(screenshot_dir_str).expanduser().resolve()

    # Look for the screenshot with common image extensions
    for ext in [".png", ".jpg", ".jpeg"]:
        screenshot_path = screenshot_dir / f"{button_name}{ext}"
        if screenshot_path.exists():
            return screenshot_path

    return None


def _click_button_with_image(button_name: str, config: Dict[str, Any]) -> bool:
    """Find and click a button using image recognition

    Args:
        button_name: Name of the button screenshot file (without extension)
        config: Configuration dict with screenshot settings (including optional confidence)

    Returns:
        True if button was found and clicked, False otherwise

    Note:
        Uses image recognition to find and click buttons on screen. The first matching
        button found on the entire screen will be clicked. Ensure the correct GitHub
        browser window/tab is focused and visible before running this function.
    """
    if not PYAUTOGUI_AVAILABLE or pyautogui is None:
        print("  ✗ PyAutoGUI is not available")
        return False

    screenshot_path = _get_screenshot_path(button_name, config)
    if screenshot_path is None:
        print(f"  ✗ Screenshot not found for button '{button_name}'")
        print(f"     Please save a screenshot as '{button_name}.png' in the screenshots directory")
        print("     See README.ja.md for instructions")
        return False

    # Get confidence from config
    confidence = _validate_confidence(config)

    try:
        print(f"  → Looking for button using screenshot: {screenshot_path}")
        print(
            "  ⚠ Make sure the correct GitHub browser window/tab is focused "
            "because the first matching button on the entire screen will be clicked."
        )
        location = pyautogui.locateOnScreen(str(screenshot_path), confidence=confidence)

        if location is None:
            print(f"  ✗ Could not find button '{button_name}' on screen")
            print("     Ensure the button is visible and the screenshot matches the current display")
            return False

        # Click in the center of the found button
        center = pyautogui.center(location)
        time.sleep(0.5)  # Brief pause before clicking
        pyautogui.click(center)
        print(f"  ✓ Clicked button '{button_name}' at position {center}")
        return True

    except Exception as e:
        print(f"  ✗ Error clicking button '{button_name}': {e}")
        print("     This may occur if running in a headless environment, SSH session without display,")
        print("     or if the screen is locked. PyAutoGUI requires an active display.")
        return False


def assign_issue_to_copilot_automated(issue_url: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """Automatically assign an issue to Copilot by clicking buttons in browser

    This function uses PyAutoGUI with image recognition to:
    1. Open the issue in a browser (requires an already-authenticated browser session)
    2. Wait for the configured time (default 10 seconds)
    3. Click the "Assign to Copilot" button (using screenshot)
    4. Click the "Assign" button (using screenshot)

    Important: This function uses webbrowser.open() which opens the URL in your system's
    default browser. You must be already logged into GitHub in that browser for the
    automation to work. The function does not handle authentication.

    Note: To prevent issues with opening multiple pages simultaneously, this function
    will only open a browser if at least 60 seconds have passed since the last browser
    was opened. If the cooldown has not elapsed, the function returns False and the
    operation will be retried in the next monitoring iteration.

    Note: Once an assignment attempt has been made for a specific issue URL (whether
    successful or not), subsequent attempts for the same URL will be skipped for 24 hours
    to prevent repeatedly opening the same page when automation fails. After 24 hours,
    the issue URL can be retried automatically, allowing recovery from temporary failures
    (e.g., missing screenshots, UI changes). This prevents opening duplicate browser tabs
    while still allowing eventual retries.

    Required screenshots (must be provided by user):
    - assign_to_copilot.png: Screenshot of "Assign to Copilot" button
    - assign.png: Screenshot of "Assign" button

    Args:
        issue_url: The URL of the GitHub issue
        config: Optional configuration dict with automation settings
                Supported keys in assign_to_copilot section:
                - wait_seconds (int): Seconds to wait for page load (default: 10)
                - button_delay (float): Seconds to wait between button clicks (default: 2.0)
                - confidence (float): Image matching confidence 0.0-1.0 (default: 0.8)
                - screenshot_dir (str): Directory containing screenshots (default: "screenshots")

    Returns:
        True if automation was successful, False otherwise
    """
    if not PYAUTOGUI_AVAILABLE:
        print("  ✗ PyAutoGUI is not installed. Install with: pip install pyautogui pillow")
        return False

    # Check if assignment has already been attempted for this issue recently
    if issue_url in _issue_assign_attempted:
        last_attempt_time = _issue_assign_attempted[issue_url]
        elapsed = time.time() - last_attempt_time
        if elapsed < ISSUE_ASSIGN_RETRY_AFTER_SECONDS:
            remaining_hours = (ISSUE_ASSIGN_RETRY_AFTER_SECONDS - elapsed) / 3600
            print("  ℹ Assignment already attempted for this issue recently")
            print(f"     Will retry after {remaining_hours:.1f} hours (to prevent duplicate tabs)")
            return False
        else:
            # Enough time has passed, allow retry
            print(f"  ℹ Retrying assignment (last attempt was {elapsed / 3600:.1f} hours ago)")

    # Check if enough time has passed since the last browser open
    if not _can_open_browser():
        remaining = _get_remaining_cooldown()
        print(f"  ⏳ Browser cooldown in effect. Please wait {int(remaining)} more seconds before opening next page.")
        print("     This prevents issues with opening multiple pages simultaneously.")
        print("     Will retry in the next monitoring iteration.")
        return False

    # Get configuration settings
    if config is None:
        config = {}

    assign_config = config.get("assign_to_copilot", {})

    # Validate and get configuration values
    wait_seconds = _validate_wait_seconds(assign_config)
    button_delay = _validate_button_delay(assign_config)

    print("  → [PyAutoGUI] Opening issue in browser...")
    print("  ℹ Ensure you are already logged into GitHub in your default browser")

    # Determine if window should be raised to foreground
    autoraise = _should_autoraise_window(config)

    try:
        opened = webbrowser.open(issue_url, autoraise=autoraise)
        if not opened:
            print(f"  ✗ Browser did not open for issue URL '{issue_url}'")
            print("     Please check your default browser settings")
            return False
    except Exception as e:
        print(f"  ✗ Failed to open browser for issue URL '{issue_url}': {e}")
        return False

    # Record the browser open time to enforce cooldown
    _record_browser_open()

    # Mark this issue as having an assignment attempt with current timestamp
    # This is done immediately after browser opens to prevent repeated browser opens
    # even if the automation fails later (e.g., button not found). The goal is to
    # prevent opening 30+ tabs of the same URL, not to retry until successful.
    # The timestamp allows retries after 24 hours for temporary failures.
    _issue_assign_attempted[issue_url] = time.time()

    # Wait for the configured time
    print(f"  → Waiting {wait_seconds} seconds for page to load...")
    time.sleep(wait_seconds)

    # Click "Assign to Copilot" button
    print("  → Looking for 'Assign to Copilot' button...")
    if not _click_button_with_image("assign_to_copilot", assign_config):
        print("  ✗ Could not find or click 'Assign to Copilot' button")
        return False

    print("  ✓ Clicked 'Assign to Copilot' button")

    # Wait for the assignment UI to appear
    print(f"  → Waiting {button_delay} seconds for UI to respond...")
    time.sleep(button_delay)

    # Click "Assign" button
    print("  → Looking for 'Assign' button...")
    if not _click_button_with_image("assign", assign_config):
        print("  ✗ Could not find or click 'Assign' button")
        return False

    print("  ✓ Clicked 'Assign' button")
    print("  ✓ [PyAutoGUI] Successfully automated issue assignment to Copilot")

    # Wait before finishing
    time.sleep(button_delay)

    return True


def merge_pr_automated(pr_url: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """Automatically merge a PR by clicking the merge button in browser

    This function uses PyAutoGUI with image recognition to:
    1. Open the PR in a browser (requires an already-authenticated browser session)
    2. Wait for the configured time (default 10 seconds)
    3. Click the "Merge pull request" button (using screenshot)
    4. Click the "Confirm merge" button (using screenshot)
    5. Click the "Delete branch" button (using screenshot)

    Important: This function uses webbrowser.open() which opens the URL in your system's
    default browser. You must be already logged into GitHub in that browser for the
    automation to work. The function does not handle authentication.

    Note: To prevent issues with opening multiple pages simultaneously, this function
    will only open a browser if at least 60 seconds have passed since the last browser
    was opened. If the cooldown has not elapsed, the function returns False and the
    operation will be retried in the next monitoring iteration.

    Required screenshots (must be provided by user):
    - merge_pull_request.png: Screenshot of "Merge pull request" button
    - confirm_merge.png: Screenshot of "Confirm merge" button
    - delete_branch.png: Screenshot of "Delete branch" button (optional)

    Args:
        pr_url: The URL of the GitHub PR
        config: Optional configuration dict with automation settings
                Supported keys in phase3_merge section:
                - wait_seconds (int): Seconds to wait for page load (default: 10)
                - button_delay (float): Seconds to wait between button clicks (default: 2.0)
                - confidence (float): Image matching confidence 0.0-1.0 (default: 0.8)
                - screenshot_dir (str): Directory containing screenshots (default: "screenshots")

    Returns:
        True if automation was successful, False otherwise
    """
    if not PYAUTOGUI_AVAILABLE:
        print("  ✗ PyAutoGUI is not installed. Install with: pip install pyautogui pillow")
        return False

    # Check if enough time has passed since the last browser open
    if not _can_open_browser():
        remaining = _get_remaining_cooldown()
        print(f"  ⏳ Browser cooldown in effect. Please wait {int(remaining)} more seconds before opening next page.")
        print("     This prevents issues with opening multiple pages simultaneously.")
        print("     Will retry in the next monitoring iteration.")
        return False

    # Get configuration settings
    if config is None:
        config = {}

    merge_config = config.get("phase3_merge", {})

    # Validate and get configuration values
    wait_seconds = _validate_wait_seconds(merge_config)
    button_delay = _validate_button_delay(merge_config)

    print("  → [PyAutoGUI] Opening PR in browser...")
    print("  ℹ Ensure you are already logged into GitHub in your default browser")

    # Determine if window should be raised to foreground
    autoraise = _should_autoraise_window(config)

    try:
        opened = webbrowser.open(pr_url, autoraise=autoraise)
        if not opened:
            print(f"  ✗ Browser did not open for PR URL '{pr_url}'")
            print("     Please check your default browser settings")
            return False
    except Exception as e:
        print(f"  ✗ Failed to open browser for PR URL '{pr_url}': {e}")
        return False

    # Record the browser open time to enforce cooldown
    _record_browser_open()

    # Wait for the configured time
    print(f"  → Waiting {wait_seconds} seconds for page to load...")
    time.sleep(wait_seconds)

    # Click "Merge pull request" button
    print("  → Looking for 'Merge pull request' button...")
    if not _click_button_with_image("merge_pull_request", merge_config):
        print("  ✗ Could not find or click 'Merge pull request' button")
        return False

    print("  ✓ Clicked 'Merge pull request' button")

    # Wait for the confirmation UI to appear
    print(f"  → Waiting {button_delay} seconds for UI to respond...")
    time.sleep(button_delay)

    # Click "Confirm merge" button
    print("  → Looking for 'Confirm merge' button...")
    if not _click_button_with_image("confirm_merge", merge_config):
        print("  ✗ Could not find or click 'Confirm merge' button")
        return False

    print("  ✓ Clicked 'Confirm merge' button")

    # Wait for merge to complete and delete branch button to appear
    print(f"  → Waiting {button_delay + 1.0} seconds for merge to complete...")
    time.sleep(button_delay + 1.0)

    # Click "Delete branch" button (optional - don't fail if not found)
    print("  → Looking for 'Delete branch' button...")
    if not _click_button_with_image("delete_branch", merge_config):
        print("  ⚠ Could not find or click 'Delete branch' button (may have already been deleted)")
    else:
        print("  ✓ Clicked 'Delete branch' button")

    print("  ✓ [PyAutoGUI] Successfully automated PR merge")

    # Wait before finishing
    time.sleep(button_delay)

    return True
