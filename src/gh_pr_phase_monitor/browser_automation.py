"""Browser automation module for automated button clicking

This module provides functionality to automate clicking buttons in a browser
using Selenium WebDriver. It's designed to work on Windows PCs and can be
optionally enabled through configuration.
"""

import time
from typing import Any, Dict, Optional

# Selenium imports are optional - will be imported only if automation is enabled
try:
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


def is_selenium_available() -> bool:
    """Check if Selenium is available for use

    Returns:
        True if Selenium is installed and available, False otherwise
    """
    return SELENIUM_AVAILABLE


def assign_issue_to_copilot_automated(
    issue_url: str,
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """Automatically assign an issue to Copilot by clicking buttons in browser

    This function uses Selenium WebDriver to:
    1. Open the issue in a browser
    2. Wait for the configured time (default 10 seconds)
    3. Click the "Assign to Copilot" button
    4. Click the "Assign" button

    Args:
        issue_url: The URL of the GitHub issue
        config: Optional configuration dict with automation settings

    Returns:
        True if automation was successful, False otherwise
    """
    if not SELENIUM_AVAILABLE:
        print("  ✗ Selenium is not installed. Install with: pip install selenium webdriver-manager")
        return False

    # Get configuration settings
    if config is None:
        config = {}

    assign_config = config.get("assign_to_copilot", {})

    # Validate and get wait_seconds
    try:
        wait_seconds = int(assign_config.get("wait_seconds", 10))
        if wait_seconds < 0:
            print("  ⚠ wait_seconds must be positive, using default: 10")
            wait_seconds = 10
    except (ValueError, TypeError):
        print("  ⚠ Invalid wait_seconds value in config, using default: 10")
        wait_seconds = 10

    browser_type = assign_config.get("browser", "edge").lower()
    headless = assign_config.get("headless", False)

    driver = None

    try:
        # Initialize the browser driver
        driver = _create_browser_driver(browser_type, headless)
        if driver is None:
            return False

        print(f"  → Opening issue in {browser_type} browser...")
        driver.get(issue_url)

        # Wait for the configured time
        print(f"  → Waiting {wait_seconds} seconds for page to load...")
        time.sleep(wait_seconds)

        # Click "Assign to Copilot" button
        print("  → Looking for 'Assign to Copilot' button...")
        if not _click_button(driver, "Assign to Copilot"):
            print("  ✗ Could not find or click 'Assign to Copilot' button")
            return False

        print("  ✓ Clicked 'Assign to Copilot' button")

        # Wait a bit for the assignment UI to appear
        time.sleep(2)

        # Click "Assign" button
        print("  → Looking for 'Assign' button...")
        if not _click_button(driver, "Assign"):
            print("  ✗ Could not find or click 'Assign' button")
            return False

        print("  ✓ Clicked 'Assign' button")
        print("  ✓ Successfully automated issue assignment to Copilot")

        # Wait a bit before closing
        time.sleep(2)

        return True

    except WebDriverException as e:
        print(f"  ✗ Browser automation error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Failed to automate button clicks: {e}")
        return False
    finally:
        # Clean up - close the browser
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass  # Ignore errors when closing


def _create_browser_driver(browser_type: str, headless: bool) -> Optional["webdriver.Remote"]:
    """Create and configure a browser driver

    Args:
        browser_type: Type of browser (edge, chrome, firefox)
        headless: Whether to run in headless mode

    Returns:
        WebDriver instance or None if failed
    """
    try:
        if browser_type == "edge":
            options = webdriver.EdgeOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--disable-blink-features=AutomationControlled")
            return webdriver.Edge(options=options)

        elif browser_type == "chrome":
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--disable-blink-features=AutomationControlled")
            return webdriver.Chrome(options=options)

        elif browser_type == "firefox":
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            return webdriver.Firefox(options=options)

        else:
            print(f"  ✗ Unsupported browser type: {browser_type}")
            return None

    except WebDriverException as e:
        print(f"  ✗ Failed to create {browser_type} browser driver: {e}")
        print(f"  → Make sure {browser_type} driver is installed")
        return None


def _click_button(driver: "webdriver.Remote", button_text: str, timeout: int = 10) -> bool:
    """Find and click a button by its text

    Args:
        driver: Selenium WebDriver instance
        button_text: Text content of the button to click (should be safe, predefined text)
        timeout: Maximum time to wait for button (seconds)

    Returns:
        True if button was found and clicked, False otherwise

    Note:
        This function expects predefined button text like "Assign to Copilot"
        and is not designed to handle arbitrary user input.
    """
    try:
        wait = WebDriverWait(driver, timeout)

        # Try multiple strategies to find the button
        # Using double quotes for XPath to avoid issues with single quotes in text
        selectors = [
            (By.XPATH, f'//button[contains(text(), "{button_text}")]'),
            (By.XPATH, f'//button[@aria-label="{button_text}"]'),
            (By.XPATH, f'//a[contains(text(), "{button_text}")]'),
        ]

        for by, selector in selectors:
            try:
                button = wait.until(
                    EC.element_to_be_clickable((by, selector))
                )
                button.click()
                return True
            except TimeoutException:
                continue

        # If none of the selectors worked
        return False

    except Exception as e:
        print(f"  ✗ Error clicking button '{button_text}': {e}")
        return False
