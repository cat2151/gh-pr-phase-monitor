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

# PyAutoGUI imports are optional - will be imported only if automation is enabled
try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


def is_pyautogui_available() -> bool:
    """Check if PyAutoGUI is available for use

    Returns:
        True if PyAutoGUI is installed and available, False otherwise
    """
    return PYAUTOGUI_AVAILABLE


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


def _get_screenshot_path(button_name: str, config: Dict[str, Any]) -> Optional[Path]:
    """Get the path to the button screenshot image

    Args:
        button_name: Name of the button (e.g., "assign_to_copilot", "assign", "merge_pull_request")
        config: Configuration dict with screenshot_dir setting

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


def _click_button_with_image(button_name: str, config: Dict[str, Any], confidence: float = 0.8) -> bool:
    """Find and click a button using image recognition

    Args:
        button_name: Name of the button screenshot file (without extension)
        config: Configuration dict with screenshot settings
        confidence: Confidence level for image matching (0.0 to 1.0)

    Returns:
        True if button was found and clicked, False otherwise
    """
    if not PYAUTOGUI_AVAILABLE:
        print("  ✗ PyAutoGUI is not available")
        return False

    screenshot_path = _get_screenshot_path(button_name, config)
    if screenshot_path is None:
        print(f"  ✗ Screenshot not found for button '{button_name}'")
        print(f"     Please save a screenshot as '{button_name}.png' in the screenshots directory")
        print(f"     See README.ja.md for instructions")
        return False

    try:
        print(f"  → Looking for button using screenshot: {screenshot_path}")
        location = pyautogui.locateOnScreen(str(screenshot_path), confidence=confidence)

        if location is None:
            print(f"  ✗ Could not find button '{button_name}' on screen")
            return False

        # Click in the center of the found button
        center = pyautogui.center(location)
        pyautogui.click(center)
        print(f"  ✓ Clicked button '{button_name}' at position {center}")
        return True

    except Exception as e:
        print(f"  ✗ Error clicking button '{button_name}': {e}")
        return False


def assign_issue_to_copilot_automated(issue_url: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """Automatically assign an issue to Copilot by clicking buttons in browser

    This function uses PyAutoGUI with image recognition to:
    1. Open the issue in a browser
    2. Wait for the configured time (default 10 seconds)
    3. Click the "Assign to Copilot" button (using screenshot)
    4. Click the "Assign" button (using screenshot)

    Required screenshots (must be provided by user):
    - assign_to_copilot.png: Screenshot of "Assign to Copilot" button
    - assign.png: Screenshot of "Assign" button

    Args:
        issue_url: The URL of the GitHub issue
        config: Optional configuration dict with automation settings

    Returns:
        True if automation was successful, False otherwise
    """
    if not PYAUTOGUI_AVAILABLE:
        print("  ✗ PyAutoGUI is not installed. Install with: pip install pyautogui pillow")
        return False

    # Get configuration settings
    if config is None:
        config = {}

    assign_config = config.get("assign_to_copilot", {})

    # Validate and get wait_seconds
    wait_seconds = _validate_wait_seconds(assign_config)

    print(f"  → [PyAutoGUI] Opening issue in browser...")
    webbrowser.open(issue_url)

    # Wait for the configured time
    print(f"  → Waiting {wait_seconds} seconds for page to load...")
    time.sleep(wait_seconds)

    # Click "Assign to Copilot" button
    print("  → Looking for 'Assign to Copilot' button...")
    if not _click_button_with_image("assign_to_copilot", assign_config):
        print("  ✗ Could not find or click 'Assign to Copilot' button")
        return False

    print("  ✓ Clicked 'Assign to Copilot' button")

    # Wait a bit for the assignment UI to appear
    time.sleep(2)

    # Click "Assign" button
    print("  → Looking for 'Assign' button...")
    if not _click_button_with_image("assign", assign_config):
        print("  ✗ Could not find or click 'Assign' button")
        return False

    print("  ✓ Clicked 'Assign' button")
    print("  ✓ [PyAutoGUI] Successfully automated issue assignment to Copilot")

    # Wait a bit before finishing
    time.sleep(2)

    return True


def merge_pr_automated(pr_url: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """Automatically merge a PR by clicking the merge button in browser

    This function uses PyAutoGUI with image recognition to:
    1. Open the PR in a browser
    2. Wait for the configured time (default 10 seconds)
    3. Click the "Merge pull request" button (using screenshot)
    4. Click the "Confirm merge" button (using screenshot)
    5. Click the "Delete branch" button (using screenshot)

    Required screenshots (must be provided by user):
    - merge_pull_request.png: Screenshot of "Merge pull request" button
    - confirm_merge.png: Screenshot of "Confirm merge" button
    - delete_branch.png: Screenshot of "Delete branch" button (optional)

    Args:
        pr_url: The URL of the GitHub PR
        config: Optional configuration dict with automation settings

    Returns:
        True if automation was successful, False otherwise
    """
    if not PYAUTOGUI_AVAILABLE:
        print("  ✗ PyAutoGUI is not installed. Install with: pip install pyautogui pillow")
        return False

    # Get configuration settings
    if config is None:
        config = {}

    merge_config = config.get("phase3_merge", {})

    # Validate and get wait_seconds
    wait_seconds = _validate_wait_seconds(merge_config)

    print(f"  → [PyAutoGUI] Opening PR in browser...")
    webbrowser.open(pr_url)

    # Wait for the configured time
    print(f"  → Waiting {wait_seconds} seconds for page to load...")
    time.sleep(wait_seconds)

    # Click "Merge pull request" button
    print("  → Looking for 'Merge pull request' button...")
    if not _click_button_with_image("merge_pull_request", merge_config):
        print("  ✗ Could not find or click 'Merge pull request' button")
        return False

    print("  ✓ Clicked 'Merge pull request' button")

    # Wait a bit for the confirmation UI to appear
    time.sleep(2)

    # Click "Confirm merge" button
    print("  → Looking for 'Confirm merge' button...")
    if not _click_button_with_image("confirm_merge", merge_config):
        print("  ✗ Could not find or click 'Confirm merge' button")
        return False

    print("  ✓ Clicked 'Confirm merge' button")

    # Wait for merge to complete and delete branch button to appear
    time.sleep(3)

    # Click "Delete branch" button (optional - don't fail if not found)
    print("  → Looking for 'Delete branch' button...")
    if not _click_button_with_image("delete_branch", merge_config):
        print("  ⚠ Could not find or click 'Delete branch' button (may have already been deleted)")
    else:
        print("  ✓ Clicked 'Delete branch' button")

    print("  ✓ [PyAutoGUI] Successfully automated PR merge")

    # Wait a bit before finishing
    time.sleep(2)

    return True
