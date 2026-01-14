"""Tests for check_process_before_autoraise configuration option

This module tests the process detection functionality and autoraise behavior
when cat-window-watcher process is running or not.
"""

import subprocess
from unittest.mock import MagicMock, patch

import src.gh_pr_phase_monitor.browser_automation as browser_automation
from src.gh_pr_phase_monitor.config import (
    DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE,
    is_process_running,
)


class TestProcessDetection:
    """Test process detection functionality"""

    def test_is_process_running_returns_true_when_process_exists(self):
        """Test that is_process_running returns True when process is found by pgrep"""
        with patch("subprocess.run") as mock_run:
            # Mock pgrep output with cat-window-watcher process PID
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "1234\n5678\n"
            mock_run.return_value = mock_result

            result = is_process_running("cat-window-watcher")
            assert result is True
            mock_run.assert_called_once()
            # Verify pgrep was called
            assert mock_run.call_args[0][0] == ["pgrep", "-f", "cat-window-watcher"]

    def test_is_process_running_returns_false_when_process_not_exists(self):
        """Test that is_process_running returns False when process is not found by pgrep"""
        with patch("subprocess.run") as mock_run:
            # Mock pgrep output without any processes
            mock_result = MagicMock()
            mock_result.returncode = 1  # pgrep returns 1 when no processes found
            mock_result.stdout = ""
            mock_run.return_value = mock_result

            result = is_process_running("cat-window-watcher")
            assert result is False
            mock_run.assert_called_once()

    def test_is_process_running_handles_subprocess_error(self):
        """Test that is_process_running handles subprocess errors gracefully"""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.SubprocessError("Command failed")

            result = is_process_running("cat-window-watcher")
            assert result is False

    def test_is_process_running_handles_file_not_found_error(self):
        """Test that is_process_running falls back to ps aux when pgrep is not available"""
        with patch("subprocess.run") as mock_run:
            # First call (pgrep) raises FileNotFoundError
            # Second call (ps aux fallback) succeeds
            def side_effect(cmd, **kwargs):
                if cmd[0] == "pgrep":
                    raise FileNotFoundError("pgrep command not found")
                else:  # ps aux
                    mock_result = MagicMock()
                    mock_result.returncode = 0
                    mock_result.stdout = (
                        "user  1234  0.0  0.1  12345  6789 ?  S  10:00  0:01 python cat-window-watcher.py"
                    )
                    return mock_result

            mock_run.side_effect = side_effect

            result = is_process_running("cat-window-watcher")
            assert result is True
            # Should have been called twice (pgrep then ps)
            assert mock_run.call_count == 2

    def test_is_process_running_handles_nonzero_return_code(self):
        """Test that is_process_running handles non-zero return codes from pgrep"""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1  # pgrep returns 1 when no matches
            mock_result.stdout = ""
            mock_run.return_value = mock_result

            result = is_process_running("cat-window-watcher")
            assert result is False

    def test_is_process_running_fallback_to_ps_when_pgrep_unavailable(self):
        """Test complete fallback path when pgrep is not available"""
        with patch("subprocess.run") as mock_run:
            # First call (pgrep) raises FileNotFoundError
            # Second call (ps aux) returns no matching process
            def side_effect(cmd, **kwargs):
                if cmd[0] == "pgrep":
                    raise FileNotFoundError("pgrep not found")
                else:  # ps aux
                    mock_result = MagicMock()
                    mock_result.returncode = 0
                    mock_result.stdout = "user  1234  0.0  0.1  12345  6789 ?  S  10:00  0:01 python other-script.py"
                    return mock_result

            mock_run.side_effect = side_effect

            result = is_process_running("cat-window-watcher")
            assert result is False
            assert mock_run.call_count == 2


class TestAutoraiseBehavior:
    """Test autoraise behavior in browser_automation module"""

    def test_should_autoraise_returns_true_when_config_disabled(self):
        """Test that _should_autoraise_window returns True when check is disabled"""
        from src.gh_pr_phase_monitor.browser_automation import _should_autoraise_window

        config = {"check_process_before_autoraise": False}

        with patch("src.gh_pr_phase_monitor.browser_automation.is_process_running") as mock_is_running:
            mock_is_running.return_value = True  # Process is running

            result = _should_autoraise_window(config)
            assert result is True
            # Should not check for process when disabled
            mock_is_running.assert_not_called()

    def test_should_autoraise_returns_false_when_process_running_and_config_enabled(self):
        """Test that _should_autoraise_window returns False when cat-window-watcher is running"""
        from src.gh_pr_phase_monitor.browser_automation import _should_autoraise_window

        config = {"check_process_before_autoraise": True}

        with patch("src.gh_pr_phase_monitor.browser_automation.is_process_running") as mock_is_running:
            mock_is_running.return_value = True  # Process is running

            result = _should_autoraise_window(config)
            assert result is False
            mock_is_running.assert_called_once_with("cat-window-watcher")

    def test_should_autoraise_returns_true_when_process_not_running_and_config_enabled(self):
        """Test that _should_autoraise_window returns True when cat-window-watcher is not running"""
        from src.gh_pr_phase_monitor.browser_automation import _should_autoraise_window

        config = {"check_process_before_autoraise": True}

        with patch("src.gh_pr_phase_monitor.browser_automation.is_process_running") as mock_is_running:
            mock_is_running.return_value = False  # Process is not running

            result = _should_autoraise_window(config)
            assert result is True
            mock_is_running.assert_called_once_with("cat-window-watcher")

    def test_should_autoraise_uses_default_when_config_not_provided(self):
        """Test that _should_autoraise_window uses default config when not provided"""
        from src.gh_pr_phase_monitor.browser_automation import _should_autoraise_window

        with patch("src.gh_pr_phase_monitor.browser_automation.is_process_running") as mock_is_running:
            mock_is_running.return_value = False

            result = _should_autoraise_window(None)
            # Default is True, so should check for process
            assert result is True
            mock_is_running.assert_called_once_with("cat-window-watcher")

    def test_should_autoraise_uses_default_when_key_not_in_config(self):
        """Test that _should_autoraise_window uses default when key is not in config"""
        from src.gh_pr_phase_monitor.browser_automation import _should_autoraise_window

        config = {}  # Empty config

        with patch("src.gh_pr_phase_monitor.browser_automation.is_process_running") as mock_is_running:
            mock_is_running.return_value = False

            result = _should_autoraise_window(config)
            # Default is True, so should check for process
            assert result is True
            mock_is_running.assert_called_once_with("cat-window-watcher")


class TestBrowserAutomationIntegration:
    """Test integration with browser automation functions"""

    def setup_method(self):
        """Reset browser cooldown state before each test"""
        browser_automation._last_browser_open_time = None
        browser_automation._issue_assign_attempted.clear()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation.is_process_running")
    @patch("time.sleep")
    def test_assign_issue_uses_autoraise_false_when_process_running(
        self, mock_sleep, mock_is_running, mock_webbrowser, mock_click
    ):
        """Test that assign_issue_to_copilot_automated uses autoraise=False when cat-window-watcher is running"""
        from src.gh_pr_phase_monitor.browser_automation import assign_issue_to_copilot_automated

        mock_is_running.return_value = True
        mock_webbrowser.open.return_value = True
        mock_click.return_value = True

        config = {"check_process_before_autoraise": True}
        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        assert result is True
        mock_webbrowser.open.assert_called_once()
        # Check that autoraise=False was used
        call_args = mock_webbrowser.open.call_args
        assert call_args[1]["autoraise"] is False

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation.is_process_running")
    @patch("time.sleep")
    def test_assign_issue_uses_autoraise_true_when_process_not_running(
        self, mock_sleep, mock_is_running, mock_webbrowser, mock_click
    ):
        """Test that assign_issue_to_copilot_automated uses autoraise=True when cat-window-watcher is not running"""
        from src.gh_pr_phase_monitor.browser_automation import assign_issue_to_copilot_automated

        mock_is_running.return_value = False
        mock_webbrowser.open.return_value = True
        mock_click.return_value = True

        config = {"check_process_before_autoraise": True}
        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        assert result is True
        mock_webbrowser.open.assert_called_once()
        # Check that autoraise=True was used
        call_args = mock_webbrowser.open.call_args
        assert call_args[1]["autoraise"] is True

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation.is_process_running")
    @patch("time.sleep")
    def test_merge_pr_uses_autoraise_false_when_process_running(
        self, mock_sleep, mock_is_running, mock_webbrowser, mock_click
    ):
        """Test that merge_pr_automated uses autoraise=False when cat-window-watcher is running"""
        from src.gh_pr_phase_monitor.browser_automation import merge_pr_automated

        mock_is_running.return_value = True
        mock_webbrowser.open.return_value = True
        mock_click.return_value = True

        config = {"check_process_before_autoraise": True}
        result = merge_pr_automated("https://github.com/test/repo/pull/1", config)

        assert result is True
        mock_webbrowser.open.assert_called_once()
        # Check that autoraise=False was used
        call_args = mock_webbrowser.open.call_args
        assert call_args[1]["autoraise"] is False


class TestOpenBrowserIntegration:
    """Test integration with open_browser function in pr_actions"""

    def setup_method(self):
        """Reset browser cooldown state before each test"""
        browser_automation._last_browser_open_time = None
        browser_automation._issue_assign_attempted.clear()

    @patch("src.gh_pr_phase_monitor.pr_actions.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation.is_process_running")
    def test_open_browser_uses_autoraise_false_when_process_running(self, mock_is_running, mock_webbrowser):
        """Test that open_browser uses autoraise=False when cat-window-watcher is running"""
        from src.gh_pr_phase_monitor.pr_actions import open_browser

        mock_is_running.return_value = True
        mock_webbrowser.open.return_value = True

        config = {"check_process_before_autoraise": True}
        result = open_browser("https://github.com/test/repo/pull/1", config)

        assert result is True
        mock_webbrowser.open.assert_called_once()
        # Check that autoraise=False was used
        call_args = mock_webbrowser.open.call_args
        assert call_args[1]["autoraise"] is False

    @patch("src.gh_pr_phase_monitor.pr_actions.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation.is_process_running")
    def test_open_browser_uses_autoraise_true_when_process_not_running(self, mock_is_running, mock_webbrowser):
        """Test that open_browser uses autoraise=True when cat-window-watcher is not running"""
        from src.gh_pr_phase_monitor.pr_actions import open_browser

        mock_is_running.return_value = False
        mock_webbrowser.open.return_value = True

        config = {"check_process_before_autoraise": True}
        result = open_browser("https://github.com/test/repo/pull/1", config)

        assert result is True
        mock_webbrowser.open.assert_called_once()
        # Check that autoraise=True was used
        call_args = mock_webbrowser.open.call_args
        assert call_args[1]["autoraise"] is True


class TestConfigDefault:
    """Test that the default value is correct"""

    def test_default_check_process_before_autoraise_is_true(self):
        """Test that DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE is True"""
        assert DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE is True
