#!/usr/bin/env python3
"""
Demo script to test browser automation feature

This script demonstrates the browser automation functionality
without requiring a full GitHub environment setup.
"""

from src.gh_pr_phase_monitor.browser_automation import is_pyautogui_available


def main():
    print("=" * 60)
    print("Browser Automation Demo for cat-github-watcher")
    print("=" * 60)
    print()

    # Check if PyAutoGUI is available
    print("1. Checking automation backend...")
    print()

    pyautogui_status = is_pyautogui_available()

    if pyautogui_status:
        print("   ✓ PyAutoGUI is installed and available")
    else:
        print("   ✗ PyAutoGUI is NOT installed")
        print("   → Install with: pip install pyautogui pillow")
        print()
        print("   ⚠ PyAutoGUI is required for browser automation.")
        return

    print()
    print("2. Browser automation is ready!")
    print()
    print("Configuration options (add to config.toml):")
    print("-" * 60)
    print("""
[assign_to_copilot]
wait_seconds = 10                 # Wait time before clicking buttons
screenshot_dir = "screenshots"    # Directory containing button screenshots

[phase3_merge]
automated = true                  # Enable browser automation for merge
wait_seconds = 10                 # Wait time before clicking buttons
screenshot_dir = "screenshots"    # Directory containing button screenshots
    """)
    print("-" * 60)
    print()
    print("3. How it works:")
    print("   → Opens the GitHub issue/PR URL in a browser")
    print("   → Waits for the configured time (default: 10 seconds)")
    print("   → Uses image recognition to find and click buttons")
    print("   → Requires you to provide screenshots of the buttons")
    print()
    print("4. Required screenshots:")
    print()
    print("   For issue assignment (assign_to_copilot):")
    print("   → assign_to_copilot.png - Screenshot of 'Assign to Copilot' button")
    print("   → assign.png - Screenshot of 'Assign' button")
    print()
    print("   For PR merge (phase3_merge):")
    print("   → merge_pull_request.png - Screenshot of 'Merge pull request' button")
    print("   → confirm_merge.png - Screenshot of 'Confirm merge' button")
    print("   → delete_branch.png - Screenshot of 'Delete branch' button (optional)")
    print()
    print("5. How to capture button screenshots:")
    print()
    print("   a. Open a GitHub issue or PR in your browser")
    print("   b. Find the button you want to automate")
    print("   c. Take a screenshot of JUST the button (not the whole screen)")
    print("   d. Save it as a PNG file in the screenshots directory")
    print("   e. Use the exact filenames listed above")
    print()
    print("   Tips:")
    print("   - Screenshot should include only the button with a small margin")
    print("   - Use your OS's screenshot tool (Windows: Snipping Tool, Mac: Cmd+Shift+4)")
    print("   - Make sure the button is clearly visible and not obscured")
    print()
    print("6. Installation:")
    print()
    print("   Install PyAutoGUI:")
    print("   → pip install -r requirements-automation.txt")
    print()
    print("   Or manually:")
    print("   → pip install pyautogui pillow")
    print()
    print("7. Usage:")
    print("   When the tool finds a 'good first issue' or a PR ready to merge:")
    print("   - Opens the URL in your browser")
    print("   - Waits for the configured time")
    print("   - Automatically clicks the buttons using image recognition")
    print()
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Create a 'screenshots' directory")
    print("2. Capture button screenshots as described above")
    print("3. Configure your config.toml")
    print("4. Run cat-github-watcher.py")
    print()


if __name__ == "__main__":
    main()
