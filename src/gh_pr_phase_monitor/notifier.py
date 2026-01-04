"""
Notification module for sending alerts via ntfy.sh
"""

import urllib.request
from typing import Any, Dict, Optional


def send_ntfy_notification(
    topic: str, message: str, title: Optional[str] = None, priority: Optional[int] = None
) -> bool:
    """Send a notification via ntfy.sh

    Args:
        topic: The ntfy.sh topic to send to
        message: The notification message
        title: Optional title for the notification
        priority: Optional priority (1=min, 3=default, 5=max)

    Returns:
        True if notification was sent successfully, False otherwise
    """
    if not topic or not message:
        return False

    url = f"https://ntfy.sh/{topic}"

    # Prepare headers
    headers = {}
    if title:
        headers["Title"] = title
    if priority is not None:
        headers["Priority"] = str(priority)

    try:
        # Create request with message as body
        req = urllib.request.Request(
            url, data=message.encode("utf-8"), headers=headers, method="POST"
        )

        # Send request
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200

    except Exception as e:
        print(f"    Error sending ntfy notification: {e}")
        return False


def format_notification_message(template: str, pr_url: str) -> str:
    """Format notification message by replacing placeholders

    Args:
        template: Message template with {url} placeholder
        pr_url: PR URL to substitute

    Returns:
        Formatted message
    """
    return template.replace("{url}", pr_url)


def send_phase3_notification(config: Dict[str, Any], pr_url: str, pr_title: str) -> bool:
    """Send notification for phase3 detection

    Args:
        config: Configuration dictionary
        pr_url: PR URL
        pr_title: PR title

    Returns:
        True if notification was sent successfully, False otherwise
    """
    # Check if ntfy is configured and enabled
    ntfy_config = config.get("ntfy", {})
    if not ntfy_config.get("enabled", False):
        return False

    topic = ntfy_config.get("topic")
    message_template = ntfy_config.get("message", "PR is ready for review: {url}")

    if not topic:
        print("    Warning: ntfy.topic not configured")
        return False

    # Format message with PR URL
    message = format_notification_message(message_template, pr_url)

    # Send notification with PR title as the notification title
    return send_ntfy_notification(topic, message, title=pr_title, priority=4)
