"""
Tests for notification functionality
"""

from unittest.mock import MagicMock, patch

from src.gh_pr_phase_monitor.notifier import (
    format_notification_message,
    is_valid_topic,
    send_all_phase3_notification,
    send_ntfy_notification,
    send_phase3_notification,
)


class TestIsValidTopic:
    """Test the is_valid_topic function"""

    def test_valid_simple_topic(self):
        """Test valid simple topic name"""
        assert is_valid_topic("test-topic") is True

    def test_valid_topic_with_underscores(self):
        """Test valid topic with underscores"""
        assert is_valid_topic("test_topic_123") is True

    def test_valid_topic_with_dots(self):
        """Test valid topic with dots"""
        assert is_valid_topic("test.topic.com") is True

    def test_valid_alphanumeric(self):
        """Test valid alphanumeric topic"""
        assert is_valid_topic("TestTopic123") is True

    def test_invalid_topic_with_slash(self):
        """Test invalid topic with slash"""
        assert is_valid_topic("test/topic") is False

    def test_invalid_topic_with_spaces(self):
        """Test invalid topic with spaces"""
        assert is_valid_topic("test topic") is False

    def test_invalid_topic_with_special_chars(self):
        """Test invalid topic with special characters"""
        assert is_valid_topic("test@topic") is False
        assert is_valid_topic("test#topic") is False
        assert is_valid_topic("test$topic") is False

    def test_invalid_empty_topic(self):
        """Test empty topic"""
        assert is_valid_topic("") is False

    def test_invalid_too_long_topic(self):
        """Test topic that is too long"""
        assert is_valid_topic("a" * 101) is False

    def test_valid_max_length_topic(self):
        """Test topic at maximum length"""
        assert is_valid_topic("a" * 100) is True

    def test_invalid_topic_starting_with_dot(self):
        """Test topic starting with dot"""
        assert is_valid_topic(".topic") is False

    def test_invalid_topic_ending_with_dot(self):
        """Test topic ending with dot"""
        assert is_valid_topic("topic.") is False

    def test_invalid_topic_with_consecutive_dots(self):
        """Test topic with consecutive dots"""
        assert is_valid_topic("test..topic") is False
        assert is_valid_topic("test...topic") is False


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
        assert (
            result
            == "Check https://github.com/owner/repo/pull/456 or visit https://github.com/owner/repo/pull/456 again"
        )

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

    def test_invalid_topic_name(self):
        """Test with invalid topic name"""
        result = send_ntfy_notification("test/invalid", "Test message")
        assert result is False

    @patch("urllib.request.urlopen")
    def test_non_200_response_code(self, mock_urlopen):
        """Test with non-200 response codes"""
        # Test 201 Created
        mock_response_201 = MagicMock()
        mock_response_201.status = 201
        mock_urlopen.return_value.__enter__.return_value = mock_response_201
        result = send_ntfy_notification("test-topic", "Test message")
        assert result is False

        # Test 400 Bad Request
        mock_response_400 = MagicMock()
        mock_response_400.status = 400
        mock_urlopen.return_value.__enter__.return_value = mock_response_400
        result = send_ntfy_notification("test-topic", "Test message")
        assert result is False

        # Test 404 Not Found
        mock_response_404 = MagicMock()
        mock_response_404.status = 404
        mock_urlopen.return_value.__enter__.return_value = mock_response_404
        result = send_ntfy_notification("test-topic", "Test message")
        assert result is False

        # Test 500 Internal Server Error
        mock_response_500 = MagicMock()
        mock_response_500.status = 500
        mock_urlopen.return_value.__enter__.return_value = mock_response_500
        result = send_ntfy_notification("test-topic", "Test message")
        assert result is False

    @patch("urllib.request.urlopen")
    def test_title_with_newline_characters(self, mock_urlopen):
        """Test that titles with newlines are sanitized"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test newline in title
        result = send_ntfy_notification("test-topic", "Test message", title="Test\nTitle")
        assert result is True

        # Verify the request was made with sanitized title
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        assert "\n" not in request.headers.get("Title", "")

    @patch("urllib.request.urlopen")
    def test_title_with_carriage_return(self, mock_urlopen):
        """Test that titles with carriage returns are sanitized"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = send_ntfy_notification("test-topic", "Test message", title="Test\r\nTitle")
        assert result is True

        # Verify the request was made with sanitized title
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        assert "\r" not in request.headers.get("Title", "")
        assert "\n" not in request.headers.get("Title", "")

    @patch("urllib.request.urlopen")
    def test_title_with_special_characters(self, mock_urlopen):
        """Test titles with various special characters"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test with emojis and unicode
        result = send_ntfy_notification("test-topic", "Test message", title="PR 🎉: Fix bug")
        assert result is True

        # Test with tabs
        result = send_ntfy_notification("test-topic", "Test message", title="Test\tTitle")
        assert result is True

    @patch("urllib.request.urlopen")
    def test_notification_with_actions(self, mock_urlopen):
        """Test notification with action buttons"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = send_ntfy_notification("test-topic", "Test message", actions="view,Open URL,https://example.com")
        assert result is True

        # Verify the request was made with Actions header
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        assert "Actions" in request.headers
        assert request.headers["Actions"] == "view,Open URL,https://example.com"

    @patch("urllib.request.urlopen")
    def test_actions_with_newline_characters(self, mock_urlopen):
        """Test that actions with newlines are sanitized"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test newline in actions
        result = send_ntfy_notification("test-topic", "Test message", actions="view,Open\nURL,https://example.com")
        assert result is True

        # Verify the request was made with sanitized actions
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        assert "\n" not in request.headers.get("Actions", "")
        assert "\r" not in request.headers.get("Actions", "")


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
        result = send_phase3_notification(config, "https://github.com/owner/repo/pull/1", "Test PR")
        assert result is True
        mock_send.assert_called_once()

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_default_message_template(self, mock_send):
        """Test with default message template"""
        mock_send.return_value = True
        config = {"ntfy": {"enabled": True, "topic": "test-topic"}}
        result = send_phase3_notification(config, "https://github.com/owner/repo/pull/1", "Test PR")
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

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_custom_priority(self, mock_send):
        """Test notification with custom priority from config"""
        mock_send.return_value = True
        config = {
            "ntfy": {
                "enabled": True,
                "topic": "test-topic",
                "message": "PR ready: {url}",
                "priority": 5,
            }
        }
        result = send_phase3_notification(config, "https://github.com/owner/repo/pull/1", "Test PR")
        assert result is True
        # Verify priority 5 was passed
        call_args = mock_send.call_args
        assert call_args[1]["priority"] == 5

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_default_priority_when_not_specified(self, mock_send):
        """Test that default priority is used when not in config"""
        mock_send.return_value = True
        config = {
            "ntfy": {
                "enabled": True,
                "topic": "test-topic",
                "message": "PR ready: {url}",
            }
        }
        result = send_phase3_notification(config, "https://github.com/owner/repo/pull/1", "Test PR")
        assert result is True
        # Verify default priority 4 was used
        call_args = mock_send.call_args
        assert call_args[1]["priority"] == 4

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_action_button_is_included(self, mock_send):
        """Test that action button is included in phase3 notification"""
        mock_send.return_value = True
        config = {
            "ntfy": {
                "enabled": True,
                "topic": "test-topic",
                "message": "PR ready: {url}",
            }
        }
        pr_url = "https://github.com/owner/repo/pull/1"
        result = send_phase3_notification(config, pr_url, "Test PR")
        assert result is True
        # Verify actions parameter was passed with correct format
        call_args = mock_send.call_args
        assert "actions" in call_args[1]
        actions = call_args[1]["actions"]
        assert actions == f"view,Open PR,{pr_url}"


class TestSendAllPhase3Notification:
    """Test the send_all_phase3_notification function"""

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_notification_disabled(self, mock_send):
        """Test when notifications are disabled"""
        config = {"ntfy": {"enabled": False, "topic": "test-topic"}}
        result = send_all_phase3_notification(config)
        assert result is False
        mock_send.assert_not_called()

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_notification_enabled_no_topic(self, mock_send):
        """Test when notifications are enabled but no topic configured"""
        config = {"ntfy": {"enabled": True}}
        result = send_all_phase3_notification(config)
        assert result is False
        mock_send.assert_not_called()

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_successful_notification(self, mock_send):
        """Test successful all-phase3 notification"""
        mock_send.return_value = True
        config = {
            "ntfy": {
                "enabled": True,
                "topic": "test-topic",
                "all_phase3_message": "All PRs are ready!",
            }
        }
        result = send_all_phase3_notification(config)
        assert result is True
        mock_send.assert_called_once()
        # Verify the message was used
        call_args = mock_send.call_args
        assert call_args[0][1] == "All PRs are ready!"

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_default_message(self, mock_send):
        """Test with default message when not configured"""
        mock_send.return_value = True
        config = {"ntfy": {"enabled": True, "topic": "test-topic"}}
        result = send_all_phase3_notification(config)
        assert result is True
        # Verify the default message was used
        call_args = mock_send.call_args
        assert "All PRs are now in phase3 (ready for review)" in call_args[0][1]

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_no_ntfy_config(self, mock_send):
        """Test when ntfy config is not present"""
        config = {}
        result = send_all_phase3_notification(config)
        assert result is False
        mock_send.assert_not_called()

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_custom_priority(self, mock_send):
        """Test notification with custom priority from config"""
        mock_send.return_value = True
        config = {
            "ntfy": {
                "enabled": True,
                "topic": "test-topic",
                "all_phase3_message": "All PRs ready",
                "priority": 5,
            }
        }
        result = send_all_phase3_notification(config)
        assert result is True
        # Verify priority 5 was passed
        call_args = mock_send.call_args
        assert call_args[1]["priority"] == 5

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_default_priority_when_not_specified(self, mock_send):
        """Test that default priority is used when not in config"""
        mock_send.return_value = True
        config = {
            "ntfy": {
                "enabled": True,
                "topic": "test-topic",
                "all_phase3_message": "All PRs ready",
            }
        }
        result = send_all_phase3_notification(config)
        assert result is True
        # Verify default priority 4 was used
        call_args = mock_send.call_args
        assert call_args[1]["priority"] == 4

    @patch("src.gh_pr_phase_monitor.notifier.send_ntfy_notification")
    def test_notification_title(self, mock_send):
        """Test that notification has correct title"""
        mock_send.return_value = True
        config = {
            "ntfy": {
                "enabled": True,
                "topic": "test-topic",
                "all_phase3_message": "All PRs ready",
            }
        }
        result = send_all_phase3_notification(config)
        assert result is True
        # Verify title was set correctly
        call_args = mock_send.call_args
        assert call_args[1]["title"] == "All PRs Ready for Review"
