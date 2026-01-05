"""Browser automation module for automated button clicking

This module provides functionality to automate clicking buttons in a browser
using Selenium WebDriver or Playwright. It's designed to work on Windows PCs
and can be optionally enabled through configuration.
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

# Playwright imports are optional
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    # Define a placeholder exception class when Playwright is not available
    class PlaywrightTimeoutError(Exception):  # type: ignore
        """Placeholder for when Playwright is not installed"""
        pass


def is_selenium_available() -> bool:
    """Check if Selenium is available for use

    Returns:
        True if Selenium is installed and available, False otherwise
    """
    return SELENIUM_AVAILABLE


def is_playwright_available() -> bool:
    """Check if Playwright is available for use

    Returns:
        True if Playwright is installed and available, False otherwise
    """
    return PLAYWRIGHT_AVAILABLE


def assign_issue_to_copilot_automated(
    issue_url: str,
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """Automatically assign an issue to Copilot by clicking buttons in browser

    This function uses Selenium WebDriver or Playwright to:
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
    # Get configuration settings
    if config is None:
        config = {}

    assign_config = config.get("assign_to_copilot", {})
    
    # Get automation backend (selenium or playwright)
    backend = assign_config.get("automation_backend", "selenium").lower()
    
    if backend == "playwright":
        return _assign_with_playwright(issue_url, assign_config)
    else:
        return _assign_with_selenium(issue_url, assign_config)


def _assign_with_selenium(
    issue_url: str,
    assign_config: Dict[str, Any]
) -> bool:
    """Assign issue to Copilot using Selenium WebDriver

    Args:
        issue_url: The URL of the GitHub issue
        assign_config: Configuration dict with automation settings

    Returns:
        True if automation was successful, False otherwise
    """
    if not SELENIUM_AVAILABLE:
        print("  ✗ Selenium is not installed. Install with: pip install selenium webdriver-manager")
        return False

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

        print(f"  → [Selenium] Opening issue in {browser_type} browser...")
        driver.get(issue_url)

        # Wait for the configured time
        print(f"  → Waiting {wait_seconds} seconds for page to load...")
        time.sleep(wait_seconds)

        # Click "Assign to Copilot" button
        print("  → Looking for 'Assign to Copilot' button...")
        if not _click_button_selenium(driver, "Assign to Copilot"):
            print("  ✗ Could not find or click 'Assign to Copilot' button")
            return False

        print("  ✓ Clicked 'Assign to Copilot' button")

        # Wait a bit for the assignment UI to appear
        time.sleep(2)

        # Click "Assign" button
        print("  → Looking for 'Assign' button...")
        if not _click_button_selenium(driver, "Assign"):
            print("  ✗ Could not find or click 'Assign' button")
            return False

        print("  ✓ Clicked 'Assign' button")
        print("  ✓ [Selenium] Successfully automated issue assignment to Copilot")

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


def _assign_with_playwright(
    issue_url: str,
    assign_config: Dict[str, Any]
) -> bool:
    """Assign issue to Copilot using Playwright

    Args:
        issue_url: The URL of the GitHub issue
        assign_config: Configuration dict with automation settings

    Returns:
        True if automation was successful, False otherwise
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("  ✗ Playwright is not installed. Install with: pip install playwright && playwright install")
        return False

    # Validate and get wait_seconds
    try:
        wait_seconds = int(assign_config.get("wait_seconds", 10))
        if wait_seconds < 0:
            print("  ⚠ wait_seconds must be positive, using default: 10")
            wait_seconds = 10
    except (ValueError, TypeError):
        print("  ⚠ Invalid wait_seconds value in config, using default: 10")
        wait_seconds = 10

    browser_type = assign_config.get("browser", "chromium").lower()
    headless = assign_config.get("headless", False)

    try:
        with sync_playwright() as p:
            # Initialize the browser
            print(f"  → [Playwright] Opening issue in {browser_type} browser...")
            
            if browser_type == "firefox":
                browser = p.firefox.launch(headless=headless)
            elif browser_type == "webkit":
                browser = p.webkit.launch(headless=headless)
            else:  # default to chromium (includes chrome and edge)
                browser = p.chromium.launch(headless=headless)

            context = browser.new_context()
            page = context.new_page()

            # Navigate to the issue
            page.goto(issue_url)

            # Wait for the configured time
            print(f"  → Waiting {wait_seconds} seconds for page to load...")
            time.sleep(wait_seconds)

            # Click "Assign to Copilot" button
            print("  → Looking for 'Assign to Copilot' button...")
            if not _click_button_playwright(page, "Assign to Copilot"):
                browser.close()
                print("  ✗ Could not find or click 'Assign to Copilot' button")
                return False

            print("  ✓ Clicked 'Assign to Copilot' button")

            # Wait a bit for the assignment UI to appear
            time.sleep(2)

            # Click "Assign" button
            print("  → Looking for 'Assign' button...")
            if not _click_button_playwright(page, "Assign"):
                browser.close()
                print("  ✗ Could not find or click 'Assign' button")
                return False

            print("  ✓ Clicked 'Assign' button")
            print("  ✓ [Playwright] Successfully automated issue assignment to Copilot")

            # Wait a bit before closing
            time.sleep(2)

            browser.close()
            return True

    except PlaywrightTimeoutError as e:
        print(f"  ✗ Playwright timeout error: Page elements not found within timeout period")
        print(f"     Details: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Failed to automate button clicks with Playwright: {e}")
        return False


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


def _click_button_selenium(driver: "webdriver.Remote", button_text: str, timeout: int = 10) -> bool:
    """Find and click a button by its text using Selenium

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


def _click_button_playwright(page, button_text: str, timeout: int = 10000) -> bool:
    """Find and click a button by its text using Playwright

    Args:
        page: Playwright page instance
        button_text: Text content of the button to click (should be safe, predefined text)
        timeout: Maximum time to wait for button (milliseconds)

    Returns:
        True if button was found and clicked, False otherwise

    Note:
        This function expects predefined button text like "Assign to Copilot"
        and is not designed to handle arbitrary user input.
    """
    try:
        # Try multiple strategies to find and click the button using Playwright locators
        locators = [
            page.get_by_role("button", name=button_text),
            page.get_by_role("button", name=button_text, exact=True),
            page.get_by_role("link", name=button_text),
            page.get_by_text(button_text),
        ]

        for locator in locators:
            try:
                locator.click(timeout=timeout)
                return True
            except PlaywrightTimeoutError:
                continue
            except Exception:
                continue

        # If none of the locators worked
        return False

    except Exception as e:
        print(f"  ✗ Error clicking button '{button_text}': {e}")
        return False
