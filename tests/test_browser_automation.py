"""Tests for browser automation module"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.gh_pr_phase_monitor.browser_automation import (
    assign_issue_to_copilot_automated,
    is_pyautogui_available,
    merge_pr_automated,
)


class TestIsPyAutoGUIAvailable:
    """Tests for is_pyautogui_available function"""

    def test_returns_bool(self):
        """Test that function returns correct availability status"""
        # This will be True or False depending on whether PyAutoGUI is installed
        result = is_pyautogui_available()
        assert isinstance(result, bool)


class TestAssignIssueToCopilotAutomated:
    """Tests for assign_issue_to_copilot_automated function"""

    def setup_method(self):
        """Reset cooldown state before each test"""
        from src.gh_pr_phase_monitor import browser_automation as ba

        ba._last_browser_open_time = None
        ba._issue_assign_attempted.clear()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", False)
    def test_returns_false_when_pyautogui_unavailable(self):
        """Test that function returns False when PyAutoGUI is not available"""
        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", {})
        assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_successful_assignment(self, mock_sleep, mock_click, mock_webbrowser):
        """Test successful assignment flow"""
        # Mock successful button clicks
        mock_click.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 5}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        # Should succeed
        assert result is True

        # Verify browser was opened with autoraise parameter
        mock_webbrowser.open.assert_called_once()
        call_args = mock_webbrowser.open.call_args
        assert call_args[0][0] == "https://github.com/test/repo/issues/1"
        assert "autoraise" in call_args[1]  # autoraise parameter should be present

        # Verify two button clicks were attempted
        assert mock_click.call_count == 2
        call_args_list = [call[0][0] for call in mock_click.call_args_list]
        assert "assign_to_copilot" in call_args_list
        assert "assign" in call_args_list

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_handles_invalid_wait_seconds_string(self, mock_click, mock_webbrowser):
        """Test that function handles invalid wait_seconds (string) gracefully"""
        mock_click.return_value = False

        config = {"assign_to_copilot": {"wait_seconds": "invalid"}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        # Should use default value and fail (because buttons not found)
        assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_handles_negative_wait_seconds(self, mock_click, mock_webbrowser):
        """Test that function handles negative wait_seconds gracefully"""
        mock_click.return_value = False

        config = {"assign_to_copilot": {"wait_seconds": -5}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        # Should use default value (10) instead of -5
        assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_accepts_valid_wait_seconds(self, mock_click, mock_webbrowser):
        """Test that function accepts valid wait_seconds"""
        mock_click.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 5}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        assert result is True

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_handles_float_wait_seconds(self, mock_click, mock_webbrowser):
        """Test that function converts float wait_seconds to int"""
        mock_click.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 5.7}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        # Should convert to int (5)
        assert result is True

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_fails_if_first_button_not_found(self, mock_click, mock_webbrowser):
        """Test that function fails if first button is not found"""

        def click_side_effect(button_name, config, confidence=0.8):
            if button_name == "assign_to_copilot":
                return False  # First button not found
            return True

        mock_click.side_effect = click_side_effect

        config = {"assign_to_copilot": {"wait_seconds": 1}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        # Should fail
        assert result is False
        assert mock_click.call_count == 1  # Only tried first button

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_same_issue_url_not_attempted_twice(self, mock_click, mock_webbrowser):
        """Test that assignment is only attempted once per issue URL"""
        mock_click.return_value = False  # Simulate button not found
        mock_webbrowser.open.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 1}}
        issue_url = "https://github.com/test/repo/issues/123"

        # First attempt - should try to assign (and fail to find button)
        result1 = assign_issue_to_copilot_automated(issue_url, config)
        assert result1 is False
        assert mock_webbrowser.open.call_count == 1

        # Second attempt with same URL - should skip (already attempted)
        result2 = assign_issue_to_copilot_automated(issue_url, config)
        assert result2 is False
        # Browser should NOT be opened a second time
        assert mock_webbrowser.open.call_count == 1

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_issue_url_can_be_retried_after_24_hours(self, mock_time, mock_sleep, mock_click, mock_webbrowser):
        """Test that issue URL can be retried after 24 hours"""
        mock_click.return_value = False  # Simulate button not found
        mock_webbrowser.open.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 1}}
        issue_url = "https://github.com/test/repo/issues/123"

        # First attempt at time 0
        mock_time.return_value = 0.0
        result1 = assign_issue_to_copilot_automated(issue_url, config)
        assert result1 is False
        assert mock_webbrowser.open.call_count == 1

        # Second attempt after 12 hours - should skip (not enough time)
        mock_time.return_value = 12 * 3600  # 12 hours
        result2 = assign_issue_to_copilot_automated(issue_url, config)
        assert result2 is False
        assert mock_webbrowser.open.call_count == 1  # Still 1 (not opened again)

        # Third attempt after 25 hours - should retry (more than 24 hours)
        mock_time.return_value = 25 * 3600  # 25 hours
        result3 = assign_issue_to_copilot_automated(issue_url, config)
        assert result3 is False
        assert mock_webbrowser.open.call_count == 2  # Now 2 (opened again)

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_different_issue_urls_are_tracked_separately(self, mock_time, mock_sleep, mock_click, mock_webbrowser):
        """Test that different issue URLs can each be attempted once"""
        mock_click.return_value = True  # Simulate success
        mock_webbrowser.open.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 1}}
        issue_url_1 = "https://github.com/test/repo/issues/123"
        issue_url_2 = "https://github.com/test/repo/issues/456"

        # First issue - should succeed
        mock_time.return_value = 0.0
        result1 = assign_issue_to_copilot_automated(issue_url_1, config)
        assert result1 is True

        # Second issue - should also succeed (different URL)
        # Advance time past cooldown (61 seconds)
        mock_time.return_value = 61.0
        result2 = assign_issue_to_copilot_automated(issue_url_2, config)
        assert result2 is True

        # Browser should be opened twice (once for each URL)
        assert mock_webbrowser.open.call_count == 2


class TestMergePrAutomated:
    """Tests for merge_pr_automated function"""

    def setup_method(self):
        """Reset cooldown state before each test"""
        from src.gh_pr_phase_monitor import browser_automation as ba

        ba._last_browser_open_time = None
        ba._issue_assign_attempted.clear()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", False)
    def test_returns_false_when_pyautogui_unavailable(self):
        """Test that function returns False when PyAutoGUI is not available"""
        result = merge_pr_automated("https://github.com/test/repo/pull/1", {})
        assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_clicks_delete_branch_button_after_merge(self, mock_sleep, mock_click, mock_webbrowser):
        """Test that function attempts to click Delete branch button after merge"""
        # Mock click function to succeed for all buttons
        mock_click.return_value = True

        config = {"phase3_merge": {"wait_seconds": 1}}

        result = merge_pr_automated("https://github.com/test/repo/pull/1", config)

        # Should succeed
        assert result is True

        # Verify the three button clicks: merge_pull_request, confirm_merge, delete_branch
        assert mock_click.call_count == 3
        call_args_list = [call[0][0] for call in mock_click.call_args_list]
        assert "merge_pull_request" in call_args_list
        assert "confirm_merge" in call_args_list
        assert "delete_branch" in call_args_list

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_succeeds_even_if_delete_branch_button_not_found(self, mock_sleep, mock_click, mock_webbrowser):
        """Test that function succeeds even if Delete branch button is not found"""

        def click_side_effect(button_name, config, confidence=0.8):
            if button_name == "delete_branch":
                return False  # Button not found
            return True

        mock_click.side_effect = click_side_effect

        config = {"phase3_merge": {"wait_seconds": 1}}

        result = merge_pr_automated("https://github.com/test/repo/pull/1", config)

        # Should still succeed (merge was successful, branch deletion is optional)
        assert result is True
        assert mock_click.call_count == 3


class TestClickButtonWithImage:
    """Tests for _click_button_with_image helper function"""

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._get_screenshot_path")
    def test_returns_false_when_screenshot_not_found(self, mock_get_path):
        """Test that function returns False when screenshot is not found"""
        from src.gh_pr_phase_monitor.browser_automation import _click_button_with_image

        mock_get_path.return_value = None

        result = _click_button_with_image("test_button", {})

        assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._get_screenshot_path")
    def test_returns_false_when_button_not_on_screen(self, mock_get_path):
        """Test that function returns False when button is not found on screen"""
        from src.gh_pr_phase_monitor.browser_automation import _click_button_with_image

        # Need to mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser_automation.pyautogui") as mock_pyautogui:
            mock_get_path.return_value = Path("/tmp/test_button.png")
            mock_pyautogui.locateOnScreen.return_value = None  # Button not found

            result = _click_button_with_image("test_button", {})

            assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._get_screenshot_path")
    def test_clicks_button_when_found(self, mock_get_path):
        """Test that function clicks button when found on screen"""
        from src.gh_pr_phase_monitor.browser_automation import _click_button_with_image

        # Need to mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser_automation.pyautogui") as mock_pyautogui:
            mock_get_path.return_value = Path("/tmp/test_button.png")
            mock_location = MagicMock()
            mock_pyautogui.locateOnScreen.return_value = mock_location
            mock_pyautogui.center.return_value = (100, 200)

            result = _click_button_with_image("test_button", {})

            assert result is True
            mock_pyautogui.click.assert_called_once_with((100, 200))


class TestGetScreenshotPath:
    """Tests for _get_screenshot_path helper function"""

    def test_returns_none_when_file_not_exists(self, tmp_path):
        """Test that function returns None when screenshot file doesn't exist"""
        from src.gh_pr_phase_monitor.browser_automation import _get_screenshot_path

        config = {"screenshot_dir": str(tmp_path)}

        result = _get_screenshot_path("nonexistent_button", config)

        assert result is None

    def test_finds_png_file(self, tmp_path):
        """Test that function finds PNG file"""
        from src.gh_pr_phase_monitor.browser_automation import _get_screenshot_path

        # Create a dummy PNG file
        screenshot_file = tmp_path / "test_button.png"
        screenshot_file.touch()

        config = {"screenshot_dir": str(tmp_path)}

        result = _get_screenshot_path("test_button", config)

        assert result == screenshot_file

    def test_uses_default_screenshot_dir(self, tmp_path, monkeypatch):
        """Test that function uses default screenshots directory"""
        from src.gh_pr_phase_monitor.browser_automation import _get_screenshot_path

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # Create screenshots directory and file
        screenshots_dir = tmp_path / "screenshots"
        screenshots_dir.mkdir()
        screenshot_file = screenshots_dir / "test_button.png"
        screenshot_file.touch()

        config = {}  # No screenshot_dir specified, should use default "screenshots"

        result = _get_screenshot_path("test_button", config)

        assert result == screenshot_file


class TestSaveDebugInfo:
    """Tests for _save_debug_info helper function"""

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._get_screenshot_path")
    def test_saves_debug_screenshot_on_failure(self, mock_get_path, tmp_path):
        """Test that debug screenshot is saved when button is not found"""
        from src.gh_pr_phase_monitor.browser_automation import _save_debug_info

        # Mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser_automation.pyautogui") as mock_pyautogui:
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot
            mock_get_path.return_value = Path("/tmp/test_button.png")

            config = {"debug_dir": str(tmp_path)}
            _save_debug_info("test_button", 0.8, config)

            # Verify screenshot was taken and saved
            mock_pyautogui.screenshot.assert_called_once()
            mock_screenshot.save.assert_called_once()

            # Check that saved path is in the debug directory
            save_call_args = mock_screenshot.save.call_args[0][0]
            assert str(tmp_path) in save_call_args
            assert "test_button_fail" in save_call_args
            assert save_call_args.endswith(".png")

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._get_screenshot_path")
    def test_saves_debug_json_on_failure(self, mock_get_path, tmp_path):
        """Test that debug JSON is saved when button is not found"""
        from src.gh_pr_phase_monitor.browser_automation import _save_debug_info

        # Mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser_automation.pyautogui") as mock_pyautogui:
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot
            mock_get_path.return_value = Path("/tmp/test_button.png")

            config = {"debug_dir": str(tmp_path)}
            _save_debug_info("test_button", 0.8, config)

            # Check that JSON file was created
            json_files = list(tmp_path.glob("test_button_fail_*.json"))
            assert len(json_files) == 1

            # Verify JSON content
            with open(json_files[0], "r") as f:
                debug_info = json.load(f)

            assert debug_info["button_name"] == "test_button"
            assert debug_info["confidence"] == 0.8
            assert "timestamp" in debug_info
            assert "screenshot_path" in debug_info
            assert "template_screenshot" in debug_info

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._get_screenshot_path")
    def test_creates_debug_dir_if_not_exists(self, mock_get_path, tmp_path):
        """Test that debug directory is created if it doesn't exist"""
        from src.gh_pr_phase_monitor.browser_automation import _save_debug_info

        # Mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser_automation.pyautogui") as mock_pyautogui:
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot
            mock_get_path.return_value = Path("/tmp/test_button.png")

            # Use a non-existent subdirectory
            debug_dir = tmp_path / "new_debug_dir"
            assert not debug_dir.exists()

            config = {"debug_dir": str(debug_dir)}
            _save_debug_info("test_button", 0.8, config)

            # Verify directory was created
            assert debug_dir.exists()
            assert debug_dir.is_dir()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", False)
    def test_does_nothing_when_pyautogui_unavailable(self, tmp_path):
        """Test that function does nothing when PyAutoGUI is not available"""
        from src.gh_pr_phase_monitor.browser_automation import _save_debug_info

        config = {"debug_dir": str(tmp_path)}
        _save_debug_info("test_button", 0.8, config)

        # No files should be created
        assert len(list(tmp_path.glob("*"))) == 0

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._get_screenshot_path")
    def test_uses_default_debug_dir(self, mock_get_path, tmp_path, monkeypatch):
        """Test that function uses default debug_screenshots directory"""
        from src.gh_pr_phase_monitor.browser_automation import _save_debug_info

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # Mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser_automation.pyautogui") as mock_pyautogui:
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot
            mock_get_path.return_value = Path("/tmp/test_button.png")

            config = {}  # No debug_dir specified, should use default "debug_screenshots"
            _save_debug_info("test_button", 0.8, config)

            # Verify default directory was created
            default_debug_dir = tmp_path / "debug_screenshots"
            assert default_debug_dir.exists()
            assert default_debug_dir.is_dir()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._get_screenshot_path")
    def test_click_button_calls_save_debug_info_on_failure(self, mock_get_path, tmp_path):
        """Test that _click_button_with_image calls _save_debug_info when button not found"""
        from src.gh_pr_phase_monitor.browser_automation import _click_button_with_image

        # Mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser_automation.pyautogui") as mock_pyautogui:
            mock_get_path.return_value = Path("/tmp/test_button.png")
            mock_pyautogui.locateOnScreen.return_value = None  # Button not found
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot

            config = {"debug_dir": str(tmp_path)}
            result = _click_button_with_image("test_button", config)

            # Should return False
            assert result is False

            # Verify debug info was saved
            json_files = list(tmp_path.glob("test_button_fail_*.json"))
            assert len(json_files) == 1

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._get_screenshot_path")
    def test_click_button_saves_debug_info_on_exception(self, mock_get_path, tmp_path):
        """Test that _click_button_with_image saves debug info when exception occurs"""
        from src.gh_pr_phase_monitor.browser_automation import _click_button_with_image

        # Mock pyautogui module to raise exception
        with patch("src.gh_pr_phase_monitor.browser_automation.pyautogui") as mock_pyautogui:
            mock_get_path.return_value = Path("/tmp/test_button.png")
            mock_pyautogui.locateOnScreen.side_effect = Exception("Test exception")
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot

            config = {"debug_dir": str(tmp_path)}
            result = _click_button_with_image("test_button", config)

            # Should return False
            assert result is False

            # Verify that debug info is saved when exception occurs in locateOnScreen
            json_files = list(tmp_path.glob("test_button_fail_*.json"))
            assert len(json_files) == 1


class TestBrowserCooldown:
    """Tests for browser cooldown functionality"""

    def setup_method(self):
        """Reset cooldown state before each test"""
        from src.gh_pr_phase_monitor import browser_automation as ba

        ba._last_browser_open_time = None
        ba._issue_assign_attempted.clear()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_assign_respects_cooldown(self, mock_time, mock_sleep, mock_click, mock_webbrowser):
        """Test that assign_issue_to_copilot_automated respects cooldown"""
        # Mock click function to succeed
        mock_click.return_value = True

        # First call - should succeed
        mock_time.return_value = 0.0
        config = {"assign_to_copilot": {"wait_seconds": 1, "button_delay": 1}}

        result1 = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)
        assert result1 is True

        # Second call immediately after - should fail due to cooldown
        mock_time.return_value = 1.0  # Only 1 second passed
        result2 = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/2", config)
        assert result2 is False

        # Third call after cooldown - should succeed
        mock_time.return_value = 61.0  # 61 seconds passed since first call
        result3 = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/3", config)
        assert result3 is True

        # Verify browser was only opened twice (first and third calls)
        assert mock_webbrowser.open.call_count == 2

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_merge_respects_cooldown(self, mock_time, mock_sleep, mock_click, mock_webbrowser):
        """Test that merge_pr_automated respects cooldown"""
        # Mock click function to succeed
        mock_click.return_value = True

        # First call - should succeed
        mock_time.return_value = 0.0
        config = {"phase3_merge": {"wait_seconds": 1, "button_delay": 1}}

        result1 = merge_pr_automated("https://github.com/test/repo/pull/1", config)
        assert result1 is True

        # Second call immediately after - should fail due to cooldown
        mock_time.return_value = 1.0  # Only 1 second passed
        result2 = merge_pr_automated("https://github.com/test/repo/pull/2", config)
        assert result2 is False

        # Third call after cooldown - should succeed
        mock_time.return_value = 61.0  # 61 seconds passed since first call
        result3 = merge_pr_automated("https://github.com/test/repo/pull/3", config)
        assert result3 is True

        # Verify browser was only opened twice (first and third calls)
        assert mock_webbrowser.open.call_count == 2

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_cooldown_applies_across_assign_and_merge(self, mock_time, mock_sleep, mock_click, mock_webbrowser):
        """Test that cooldown is shared between assign and merge operations"""
        # Mock click function to succeed
        mock_click.return_value = True

        # First call - assign (should succeed)
        mock_time.return_value = 0.0
        config = {"assign_to_copilot": {"wait_seconds": 1}, "phase3_merge": {"wait_seconds": 1}}

        result1 = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)
        assert result1 is True

        # Second call - merge immediately after (should fail due to cooldown)
        mock_time.return_value = 1.0  # Only 1 second passed
        result2 = merge_pr_automated("https://github.com/test/repo/pull/1", config)
        assert result2 is False

        # Third call - merge after cooldown (should succeed)
        mock_time.return_value = 61.0  # 61 seconds passed since first call
        result3 = merge_pr_automated("https://github.com/test/repo/pull/2", config)
        assert result3 is True

        # Verify browser was only opened twice
        assert mock_webbrowser.open.call_count == 2

    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_can_open_browser_when_no_previous_open(self, mock_time):
        """Test that _can_open_browser returns True when no previous browser was opened"""
        from src.gh_pr_phase_monitor.browser_automation import _can_open_browser

        result = _can_open_browser()
        assert result is True

    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_can_open_browser_respects_cooldown(self, mock_time):
        """Test that _can_open_browser respects the 60-second cooldown"""
        from src.gh_pr_phase_monitor.browser_automation import _can_open_browser, _record_browser_open

        # Record a browser open at time 0
        mock_time.return_value = 0.0
        _record_browser_open()

        # Check at time 30 - should not be able to open
        mock_time.return_value = 30.0
        assert _can_open_browser() is False

        # Check at time 59 - still should not be able to open
        mock_time.return_value = 59.0
        assert _can_open_browser() is False

        # Check at time 60 - should be able to open
        mock_time.return_value = 60.0
        assert _can_open_browser() is True

        # Check at time 61 - should be able to open
        mock_time.return_value = 61.0
        assert _can_open_browser() is True

    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_get_remaining_cooldown(self, mock_time):
        """Test that _get_remaining_cooldown returns correct remaining time"""
        from src.gh_pr_phase_monitor.browser_automation import _get_remaining_cooldown, _record_browser_open

        # When no browser has been opened, remaining should be 0
        remaining = _get_remaining_cooldown()
        assert remaining == 0.0

        # Record a browser open at time 0
        mock_time.return_value = 0.0
        _record_browser_open()

        # At time 30, remaining should be 30
        mock_time.return_value = 30.0
        remaining = _get_remaining_cooldown()
        assert remaining == 30.0

        # At time 61, remaining should be 0
        mock_time.return_value = 61.0
        remaining = _get_remaining_cooldown()
        assert remaining == 0.0
