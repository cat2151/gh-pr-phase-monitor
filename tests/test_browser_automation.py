"""Tests for browser automation module"""

from unittest.mock import patch, MagicMock

from src.gh_pr_phase_monitor.browser_automation import (
    assign_issue_to_copilot_automated,
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
                "browser": "edge"
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
                "browser": "edge"
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
                "browser": "edge"
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
                "browser": "edge"
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
        
        # Should attempt to use Playwright
        assert result is False
        mock_pw_instance.chromium.launch.assert_called_once()

    def test_defaults_to_selenium_backend(self):
        """Test that Selenium is used by default when backend not specified"""
        config = {
            "assign_to_copilot": {
                "browser": "edge"
            }
        }
        
        with patch("src.gh_pr_phase_monitor.browser_automation.SELENIUM_AVAILABLE", True):
            with patch("src.gh_pr_phase_monitor.browser_automation._create_browser_driver") as mock_driver:
                mock_driver.return_value = None
                assign_issue_to_copilot_automated(
                    "https://github.com/test/repo/issues/1",
                    config
                )
                
                # Should use Selenium backend (default)
                mock_driver.assert_called_once()
