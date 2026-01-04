#!/usr/bin/env python3
"""
Demo script to test browser automation feature

This script demonstrates the browser automation functionality
without requiring a full GitHub environment setup.
"""

from src.gh_pr_phase_monitor.browser_automation import is_selenium_available


def main():
    print("=" * 60)
    print("Browser Automation Demo for cat-github-watcher")
    print("=" * 60)
    print()

    # Check if Selenium is available
    print("1. Checking if Selenium is available...")
    if is_selenium_available():
        print("   ✓ Selenium is installed and available")
    else:
        print("   ✗ Selenium is NOT installed")
        print("   → Install with: pip install selenium webdriver-manager")
        return

    print()
    print("2. Browser automation is ready!")
    print()
    print("Configuration options (add to config.toml):")
    print("-" * 60)
    print("""
[assign_to_copilot]
enabled = true          # Enable the feature
automated = true        # Enable browser automation
wait_seconds = 10       # Wait time before clicking buttons
browser = "edge"        # Browser: "edge", "chrome", or "firefox"
headless = false        # Run in headless mode (no visible window)
    """)
    print("-" * 60)
    print()
    print("3. How it works:")
    print("   → Opens the GitHub issue URL in a browser")
    print("   → Waits for the configured time (default: 10 seconds)")
    print("   → Automatically clicks 'Assign to Copilot' button")
    print("   → Automatically clicks 'Assign' button")
    print()
    print("4. Requirements:")
    print("   → Selenium: pip install selenium webdriver-manager")
    print("   → Browser driver (automatically downloaded):")
    print("     - Edge: Pre-installed on Windows 10/11")
    print("     - Chrome: ChromeDriver (auto-downloaded)")
    print("     - Firefox: GeckoDriver (auto-downloaded)")
    print()
    print("5. Usage:")
    print("   When the tool finds a 'good first issue', it will:")
    print("   - In manual mode: Open browser and wait for you to click")
    print("   - In automated mode: Open browser and click automatically")
    print()
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
