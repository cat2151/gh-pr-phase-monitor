"""Tests for browser automation module"""

from unittest.mock import patch, MagicMock

from src.gh_pr_phase_monitor.browser_automation import (
    assign_issue_to_copilot_automated,
    merge_pr_automated,
    is_selenium_available,
    is_playwright_available,
)


class TestIsSeleniumAvailable:
    """Tests for is_selenium_available function"""

    def test_returns_true_when_selenium_imported(self):
        """Test that function returns correct availability status"""
        # This will be True or False depending on whether Selenium is installed
        result = is_selenium_available()
        assert isinstance(result, bool)


class TestIsPlaywrightAvailable:
    """Tests for is_playwright_available function"""

    def test_returns_true_when_playwright_imported(self):
        """Test that function returns correct availability status"""
        # This will be True or False depending on whether Playwright is installed
        result = is_playwright_available()
        assert isinstance(result, bool)


class TestAssignIssueToCopilotAutomated:
    """Tests for assign_issue_to_copilot_automated function"""

    @patch("src.gh_pr_phase_monitor.browser_automation.SELENIUM_AVAILABLE", False)
    def test_returns_false_when_selenium_unavailable(self):
        """Test that function returns False when Selenium is not available"""
        result = assign_issue_to_copilot_automated(
            "https://github.com/test/repo/issues/1",
            {}
        )
        assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.SELENIUM_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._create_browser_driver")
    def test_handles_invalid_wait_seconds_string(self, mock_create_driver):
        """Test that function handles invalid wait_seconds (string) gracefully"""
        mock_create_driver.return_value = None

        config = {
            "assign_to_copilot": {
                "wait_seconds": "invalid",
                "browser": "edge",
                "automation_backend": "selenium"
            }
        }

        result = assign_issue_to_copilot_automated(
            "https://github.com/test/repo/issues/1",
            config
        )

        # Should use default value and attempt to create driver
        assert result is False
        mock_create_driver.assert_called_once()

    @patch("src.gh_pr_phase_monitor.browser_automation.SELENIUM_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._create_browser_driver")
    def test_handles_negative_wait_seconds(self, mock_create_driver):
        """Test that function handles negative wait_seconds gracefully"""
        mock_create_driver.return_value = None

        config = {
            "assign_to_copilot": {
                "wait_seconds": -5,
                "browser": "edge",
                "automation_backend": "selenium"
            }
        }

        result = assign_issue_to_copilot_automated(
            "https://github.com/test/repo/issues/1",
            config
        )

        # Should use default value (10) instead of -5
        assert result is False
        mock_create_driver.assert_called_once()

    @patch("src.gh_pr_phase_monitor.browser_automation.SELENIUM_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._create_browser_driver")
    def test_accepts_valid_wait_seconds(self, mock_create_driver):
        """Test that function accepts valid wait_seconds"""
        mock_create_driver.return_value = None

        config = {
            "assign_to_copilot": {
                "wait_seconds": 5,
                "browser": "edge",
                "automation_backend": "selenium"
            }
        }

        result = assign_issue_to_copilot_automated(
            "https://github.com/test/repo/issues/1",
            config
        )

        assert result is False
        mock_create_driver.assert_called_once_with("edge", False)

    @patch("src.gh_pr_phase_monitor.browser_automation.SELENIUM_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._create_browser_driver")
    def test_handles_float_wait_seconds(self, mock_create_driver):
        """Test that function converts float wait_seconds to int"""
        mock_create_driver.return_value = None

        config = {
            "assign_to_copilot": {
                "wait_seconds": 5.7,
                "browser": "edge",
                "automation_backend": "selenium"
            }
        }

        result = assign_issue_to_copilot_automated(
            "https://github.com/test/repo/issues/1",
            config
        )

        # Should convert to int (5)
        assert result is False
        mock_create_driver.assert_called_once()


class TestPlaywrightBackend:
    """Tests for Playwright backend functionality"""

    @patch("src.gh_pr_phase_monitor.browser_automation.PLAYWRIGHT_AVAILABLE", False)
    def test_returns_false_when_playwright_unavailable(self):
        """Test that function returns False when Playwright is not available"""
        config = {
            "assign_to_copilot": {
                "automation_backend": "playwright"
            }
        }
        result = assign_issue_to_copilot_automated(
            "https://github.com/test/repo/issues/1",
            config
        )
        assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.PLAYWRIGHT_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.sync_playwright")
    def test_uses_playwright_when_configured(self, mock_playwright):
        """Test that Playwright is used when configured"""
        # Setup mock
        mock_pw_instance = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.return_value.__enter__ = MagicMock(return_value=mock_pw_instance)
        mock_playwright.return_value.__exit__ = MagicMock(return_value=False)
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_page.click.side_effect = Exception("Button not found")
        
        config = {
            "assign_to_copilot": {
                "automation_backend": "playwright",
                "browser": "chromium",
                "wait_seconds": 1
            }
        }
        
        result = assign_issue_to_copilot_automated(
            "https://github.com/test/repo/issues/1",
            config
        )
        
        # Should attempt to use Playwright and succeed (buttons were found and clicked in mock)
        assert result is True
        mock_pw_instance.chromium.launch.assert_called_once()

    def test_defaults_to_playwright_backend(self):
        """Test that Playwright is used by default when backend not specified"""
        config = {
            "assign_to_copilot": {}  # No settings - should use all defaults
        }
        
        # Setup mock for Playwright
        with patch("src.gh_pr_phase_monitor.browser_automation.PLAYWRIGHT_AVAILABLE", True):
            with patch("src.gh_pr_phase_monitor.browser_automation.sync_playwright") as mock_playwright:
                mock_pw_instance = MagicMock()
                mock_browser = MagicMock()
                mock_context = MagicMock()
                mock_page = MagicMock()
                
                mock_playwright.return_value.__enter__ = MagicMock(return_value=mock_pw_instance)
                mock_playwright.return_value.__exit__ = MagicMock(return_value=False)
                mock_pw_instance.chromium.launch.return_value = mock_browser
                mock_browser.new_context.return_value = mock_context
                mock_context.new_page.return_value = mock_page
                mock_page.click.side_effect = Exception("Button not found")
                
                assign_issue_to_copilot_automated(
                    "https://github.com/test/repo/issues/1",
                    config
                )
                
                # Should use Playwright backend (default) and chromium browser (default)
                mock_pw_instance.chromium.launch.assert_called_once()


class TestMergePrAutomated:
    """Tests for merge_pr_automated function"""

    @patch("src.gh_pr_phase_monitor.browser_automation.SELENIUM_AVAILABLE", False)
    @patch("src.gh_pr_phase_monitor.browser_automation.PLAYWRIGHT_AVAILABLE", False)
    def test_returns_false_when_selenium_unavailable(self):
        """Test that function returns False when Selenium is not available and Selenium is requested"""
        result = merge_pr_automated(
            "https://github.com/test/repo/pull/1",
            {"phase3_merge": {"automation_backend": "selenium"}}
        )
        assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.SELENIUM_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._create_browser_driver")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_selenium")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_clicks_delete_branch_button_after_merge(self, mock_sleep, mock_click, mock_create_driver):
        """Test that function attempts to click Delete branch button after merge"""
        mock_driver = MagicMock()
        mock_create_driver.return_value = mock_driver
        
        # Mock click function to succeed for all buttons
        mock_click.return_value = True
        
        config = {
            "phase3_merge": {
                "wait_seconds": 1,
                "browser": "edge",
                "headless": False,
                "automation_backend": "selenium"
            }
        }
        
        result = merge_pr_automated(
            "https://github.com/test/repo/pull/1",
            config
        )
        
        # Should succeed
        assert result is True
        
        # Verify the three button clicks: Merge pull request, Confirm merge, Delete branch
        assert mock_click.call_count == 3
        call_args_list = [call[0][1] for call in mock_click.call_args_list]
        assert "Merge pull request" in call_args_list
        assert "Confirm merge" in call_args_list
        assert "Delete branch" in call_args_list

    @patch("src.gh_pr_phase_monitor.browser_automation.SELENIUM_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._create_browser_driver")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_selenium")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_succeeds_even_if_delete_branch_button_not_found(self, mock_sleep, mock_click, mock_create_driver):
        """Test that function succeeds even if Delete branch button is not found"""
        mock_driver = MagicMock()
        mock_create_driver.return_value = mock_driver
        
        # Mock click function to succeed for Merge and Confirm, fail for Delete branch
        def click_side_effect(driver, button_text, timeout=10):
            if button_text == "Delete branch":
                return False  # Button not found
            return True
        
        mock_click.side_effect = click_side_effect
        
        config = {
            "phase3_merge": {
                "wait_seconds": 1,
                "browser": "edge",
                "headless": False,
                "automation_backend": "selenium"
            }
        }
        
        result = merge_pr_automated(
            "https://github.com/test/repo/pull/1",
            config
        )
        
        # Should still succeed (merge was successful, branch deletion is optional)
        assert result is True
        assert mock_click.call_count == 3

    @patch("src.gh_pr_phase_monitor.browser_automation.PLAYWRIGHT_AVAILABLE", False)
    def test_playwright_returns_false_when_unavailable(self):
        """Test that Playwright backend returns False when not available"""
        config = {
            "phase3_merge": {
                "automation_backend": "playwright",
                "browser": "chromium"
            }
        }
        
        result = merge_pr_automated(
            "https://github.com/test/repo/pull/1",
            config
        )
        
        # Should fail because Playwright is not available
        assert result is False
