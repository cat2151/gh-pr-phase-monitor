"""
Tests for notification functionality
"""

from unittest.mock import MagicMock, patch

from src.gh_pr_phase_monitor.notifier import (
    format_notification_message,
    send_ntfy_notification,
    send_phase3_notification,
)


class TestFormatNotificationMessage:
    """Test the format_notification_message function"""

    def test_simple_url_replacement(self):
        """Test basic URL placeholder replacement"""
        template = "PR is ready: {url}"
        url = "https://github.com/owner/repo/pull/123"
        result = format_notification_message(template, url)
        assert result == "PR is ready: https://github.com/owner/repo/pull/123"

    def test_multiple_url_placeholders(self):
        """Test multiple URL placeholders in template"""
        template = "Check {url} or visit {url} again"
        url = "https://github.com/owner/repo/pull/456"
        result = format_notification_message(template, url)
        assert result == "Check https://github.com/owner/repo/pull/456 or visit https://github.com/owner/repo/pull/456 again"

    def test_no_placeholder(self):
        """Test template without placeholder"""
        template = "PR is ready for review"
        url = "https://github.com/owner/repo/pull/789"
        result = format_notification_message(template, url)
        assert result == "PR is ready for review"

    def test_empty_template(self):
        """Test empty template"""
        template = ""
        url = "https://github.com/owner/repo/pull/111"
        result = format_notification_message(template, url)
        assert result == ""


class TestSendNtfyNotification:
    """Test the send_ntfy_notification function"""

    @patch("urllib.request.urlopen")
    def test_successful_notification(self, mock_urlopen):
        """Test successful notification sending"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = send_ntfy_notification("test-topic", "Test message")
        assert result is True

    @patch("urllib.request.urlopen")
    def test_notification_with_title(self, mock_urlopen):
        """Test notification with title"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = send_ntfy_notification("test-topic", "Test message", title="Test Title")
        assert result is True

    @patch("urllib.request.urlopen")
    def test_notification_with_priority(self, mock_urlopen):
        """Test notification with priority"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = send_ntfy_notification("test-topic", "Test message", priority=5)
        assert result is True

    @patch("urllib.request.urlopen")
    def test_failed_notification(self, mock_urlopen):
        """Test failed notification sending"""
        # Mock exception
        mock_urlopen.side_effect = Exception("Network error")

        result = send_ntfy_notification("test-topic", "Test message")
        assert result is False

    def test_empty_topic(self):
        """Test with empty topic"""
        result = send_ntfy_notification("", "Test message")
        assert result is False

    def test_empty_message(self):
        """Test with empty message"""
        result = send_ntfy_notification("test-topic", "")
        assert result is False


class TestSendPhase3Notification:
    """Test the send_phase3_notification function"""

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_notification_disabled(self, mock_send):
        """Test when notifications are disabled"""
        config = {"ntfy": {"enabled": False, "topic": "test-topic"}}
        result = send_phase3_notification(config, "https://github.com/owner/repo/pull/1", "Test PR")
        assert result is False
        mock_send.assert_not_called()

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_notification_enabled_no_topic(self, mock_send):
        """Test when notifications are enabled but no topic configured"""
        config = {"ntfy": {"enabled": True}}
        result = send_phase3_notification(config, "https://github.com/owner/repo/pull/1", "Test PR")
        assert result is False
        mock_send.assert_not_called()

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_successful_notification(self, mock_send):
        """Test successful phase3 notification"""
        mock_send.return_value = True
        config = {
            "ntfy": {
                "enabled": True,
                "topic": "test-topic",
                "message": "PR ready: {url}",
            }
        }
        result = send_phase3_notification(
            config, "https://github.com/owner/repo/pull/1", "Test PR"
        )
        assert result is True
        mock_send.assert_called_once()

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_default_message_template(self, mock_send):
        """Test with default message template"""
        mock_send.return_value = True
        config = {"ntfy": {"enabled": True, "topic": "test-topic"}}
        result = send_phase3_notification(
            config, "https://github.com/owner/repo/pull/1", "Test PR"
        )
        assert result is True
        # Verify the default template was used
        call_args = mock_send.call_args
        assert "PR is ready for review:" in call_args[0][1]
        assert "https://github.com/owner/repo/pull/1" in call_args[0][1]

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_no_ntfy_config(self, mock_send):
        """Test when ntfy config is not present"""
        config = {}
        result = send_phase3_notification(config, "https://github.com/owner/repo/pull/1", "Test PR")
        assert result is False
        mock_send.assert_not_called()
