#!/usr/bin/env python3
"""
Comparison demo script for Selenium vs Playwright

This script provides a side-by-side comparison of both automation backends
to help determine which is more suitable for the automated issue assignment feature.
"""

import sys
import time
from src.gh_pr_phase_monitor.browser_automation import (
    is_selenium_available,
    is_playwright_available,
    assign_issue_to_copilot_automated
)


def print_header(title):
    """Print a formatted section header"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def print_section(title):
    """Print a formatted subsection"""
    print()
    print(f"--- {title} " + "-" * (70 - len(title) - 5))
    print()


def check_availability():
    """Check which automation backends are available"""
    print_header("Checking Automation Backend Availability")
    
    selenium_available = is_selenium_available()
    playwright_available = is_playwright_available()
    
    print(f"Selenium:   {'✓ Available' if selenium_available else '✗ Not installed'}")
    print(f"Playwright: {'✓ Available' if playwright_available else '✗ Not installed'}")
    
    return selenium_available, playwright_available


def compare_features():
    """Display feature comparison table"""
    print_header("Feature Comparison: Selenium vs Playwright")
    
    print("┌" + "─" * 68 + "┐")
    print("│ Feature                    │ Selenium      │ Playwright        │")
    print("├" + "─" * 68 + "┤")
    
    features = [
        ("Maturity", "High (2004)", "Medium (2020)"),
        ("Browser Support", "Chrome/Edge/FF", "Chromium/FF/WebKit"),
        ("Installation", "Separate drivers", "Built-in browsers"),
        ("Auto-wait", "Manual", "Automatic"),
        ("Speed", "Moderate", "Fast"),
        ("Stability", "High", "Very High"),
        ("API Design", "Traditional", "Modern"),
        ("Community", "Large", "Growing"),
        ("Documentation", "Extensive", "Good"),
        ("Windows Support", "Excellent", "Excellent"),
    ]
    
    for feature, selenium, playwright in features:
        print(f"│ {feature:<26} │ {selenium:<13} │ {playwright:<17} │")
    
    print("└" + "─" * 68 + "┘")


def print_comparison_summary():
    """Print summary of which backend might be more suitable"""
    print_header("Summary & Recommendations")
    
    print("Choose Selenium if:")
    print("  ✓ You need maximum stability and community support")
    print("  ✓ You prefer using real browser installations")
    print("  ✓ You want proven technology with extensive documentation")
    print("  ✓ Your team is already familiar with Selenium")
    print()
    print("Choose Playwright if:")
    print("  ✓ You want faster execution and better performance")
    print("  ✓ You prefer automatic browser management")
    print("  ✓ You value modern API design and auto-waiting")
    print("  ✓ You want built-in support for multiple browser engines")
    print()
    print("For this project (GitHub issue automation):")
    print("  → Both backends are suitable and work well")
    print("  → Playwright may be slightly easier to set up (built-in browsers)")
    print("  → Selenium has more troubleshooting resources available")
    print("  → Consider testing both with your actual workflow to decide")


def run_performance_test(test_url):
    """Run a simple performance comparison (if URL provided)"""
    print_header("Performance Test")
    
    selenium_available = is_selenium_available()
    playwright_available = is_playwright_available()
    
    if not selenium_available and not playwright_available:
        print("⚠ No automation backends available for testing.")
        return
    
    if not test_url:
        print("ℹ No test URL provided. Skipping performance test.")
        print("  To run performance test, provide a GitHub issue URL:")
        print("  python demo_comparison.py https://github.com/owner/repo/issues/123")
        return
    
    results = {}
    
    # Test Selenium
    if selenium_available:
        print_section("Testing Selenium")
        config = {
            "assign_to_copilot": {
                "automation_backend": "selenium",
                "browser": "edge",
                "headless": True,
                "wait_seconds": 5
            }
        }
        
        start_time = time.time()
        success = assign_issue_to_copilot_automated(test_url, config)
        elapsed = time.time() - start_time
        
        results["selenium"] = {
            "success": success,
            "time": elapsed
        }
        
        print(f"Result: {'✓ Success' if success else '✗ Failed'}")
        print(f"Time: {elapsed:.2f} seconds")
    
    # Test Playwright
    if playwright_available:
        print_section("Testing Playwright")
        config = {
            "assign_to_copilot": {
                "automation_backend": "playwright",
                "browser": "chromium",
                "headless": True,
                "wait_seconds": 5
            }
        }
        
        start_time = time.time()
        success = assign_issue_to_copilot_automated(test_url, config)
        elapsed = time.time() - start_time
        
        results["playwright"] = {
            "success": success,
            "time": elapsed
        }
        
        print(f"Result: {'✓ Success' if success else '✗ Failed'}")
        print(f"Time: {elapsed:.2f} seconds")
    
    # Print comparison
    if len(results) > 1:
        print_section("Performance Comparison")
        selenium_time = results.get("selenium", {}).get("time", 0)
        playwright_time = results.get("playwright", {}).get("time", 0)
        
        if selenium_time > 0 and playwright_time > 0:
            diff = abs(selenium_time - playwright_time)
            faster = "Playwright" if playwright_time < selenium_time else "Selenium"
            percent = (diff / max(selenium_time, playwright_time)) * 100
            
            print(f"Selenium:   {selenium_time:.2f}s")
            print(f"Playwright: {playwright_time:.2f}s")
            print(f"→ {faster} was {diff:.2f}s ({percent:.1f}%) faster")


def main():
    """Main comparison demo"""
    print_header("Selenium vs Playwright Comparison Demo")
    
    # Check availability
    selenium_available, playwright_available = check_availability()
    
    if not selenium_available and not playwright_available:
        print()
        print("⚠ Neither Selenium nor Playwright is installed.")
        print()
        print("To install:")
        print("  Selenium:   pip install selenium webdriver-manager")
        print("  Playwright: pip install playwright && playwright install")
        print()
        return 1
    
    # Show feature comparison
    compare_features()
    
    # Run performance test if URL provided
    test_url = sys.argv[1] if len(sys.argv) > 1 else None
    run_performance_test(test_url)
    
    # Print summary
    print_comparison_summary()
    
    print_header("Comparison Complete")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
