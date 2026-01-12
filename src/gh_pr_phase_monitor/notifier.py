"""
Notification module for sending alerts via ntfy.sh

This module provides utilities for sending pull request notifications via the
public ntfy.sh HTTP API. It is primarily used by the GH PR phase monitor to
send notifications when a pull request reaches a specific phase (e.g., ready
for review).

Typical usage
-------------

The high-level entry point is :func:`send_phase3_notification`, which expects
a configuration mapping and PR metadata::

    from gh_pr_phase_monitor import notifier

    config = {
        "ntfy": {
            "enabled": True,
            "topic": "my-topic",
            "message": "PR ready: {url}",
        }
    }

    result = notifier.send_phase3_notification(
        config,
        "https://github.com/org/repo/pull/123",
        "Fix notification bug"
    )

You can also call :func:`send_ntfy_notification` directly::

    notifier.send_ntfy_notification(
        topic="my-topic",
        message="Build finished",
        title="CI status",
        priority=3,
        actions="view,Open Details,https://example.com/details"
    )

Requirements
------------

* Internet connectivity to reach https://ntfy.sh
* Topics must satisfy :func:`is_valid_topic` (alphanumeric, underscore,
  hyphen, dot; 1-100 chars; no leading/trailing/consecutive dots)

Features
--------

* **Action buttons**: Notifications include clickable action buttons that open
  the PR URL in a browser. This uses ntfy's actions feature with the format
  "action_type,label,url" (e.g., "view,Open PR,https://github.com/...")

Limitations
-----------

* Uses public ntfy.sh service with HTTPS; no authentication configured
* ntfy.sh may apply rate limiting or message size limits
* Network errors return False and print error messages; no exceptions raised
* 10 second timeout on HTTP requests
* Notifications track per (URL, phase) to prevent duplicates
* Action buttons are supported by ntfy mobile app and some clients
"""

import base64
import re
import urllib.request
from typing import Any, Dict, Optional


def encode_header_value(value: str) -> str:
    """Encode a header value for use in HTTP headers.

    If the value contains non-ASCII characters, encode it using RFC 2047
    MIME encoded-word syntax (=?UTF-8?B?...?=) which ntfy.sh supports.

    Args:
        value: The header value to encode

    Returns:
        Encoded header value safe for HTTP headers
    """
    try:
        # Try to encode as latin-1 (ASCII-compatible)
        value.encode("latin-1")
        return value
    except UnicodeEncodeError:
        # Contains non-ASCII, use RFC 2047 Base64 encoding
        encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
        return f"=?UTF-8?B?{encoded}?="


def is_valid_topic(topic: str) -> bool:
    """Validate ntfy.sh topic name

    Topics should only contain alphanumeric characters, underscores, hyphens, and dots.
    Topics must not start or end with a dot, and must not contain consecutive dots.
    This prevents potential URL injection issues and invalid topic names.

    Args:
        topic: Topic name to validate

    Returns:
        True if valid, False otherwise
    """
    # Check length constraints first
    if not (1 <= len(topic) <= 100):
        return False

    # Check for leading or trailing dots
    if topic.startswith(".") or topic.endswith("."):
        return False

    # Check for consecutive dots
    if ".." in topic:
        return False

    # Check allowed characters: alphanumeric, underscore, hyphen, and dot
    return bool(re.match(r"^[a-zA-Z0-9_.-]+$", topic))


def send_ntfy_notification(
    topic: str, message: str, title: Optional[str] = None, priority: Optional[int] = None, actions: Optional[str] = None
) -> bool:
    """Send a notification via ntfy.sh

    Args:
        topic: The ntfy.sh topic to send to
        message: The notification message
        title: Optional title for the notification
        priority: Optional priority (1=min, 3=default, 5=max)
        actions: Optional actions header for clickable buttons (e.g., "view,Open PR,https://github.com/...")

    Returns:
        True if notification was sent successfully, False otherwise
    """
    if not topic or not message:
        return False

    # Validate topic to prevent URL injection
    if not is_valid_topic(topic):
        print(f"    Error: Invalid ntfy topic name: {topic}")
        return False

    url = f"https://ntfy.sh/{topic}"

    # Prepare headers
    headers = {}
    if title:
        # Sanitize title to prevent header injection via newline/control characters
        sanitized_title = re.sub(r"[\r\n]+", " ", title)
        # Encode non-ASCII characters for HTTP headers
        headers["Title"] = encode_header_value(sanitized_title)
    if priority is not None:
        headers["Priority"] = str(priority)
    if actions:
        # Sanitize actions to prevent header injection via newline/control characters
        sanitized_actions = re.sub(r"[\r\n]+", " ", actions)
        headers["Actions"] = sanitized_actions

    try:
        # Create request with message as body
        req = urllib.request.Request(url, data=message.encode("utf-8"), headers=headers, method="POST")

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
    priority = ntfy_config.get("priority", 4)  # Default to 4 (high), configurable

    if not topic:
        print("    Warning: ntfy.topic not configured")
        return False

    # Format message with PR URL
    message = format_notification_message(message_template, pr_url)

    # Create action button for opening PR
    # Format: action_type,label,url
    actions = f"view,Open PR,{pr_url}"

    # Send notification with PR title as the notification title and action button
    return send_ntfy_notification(topic, message, title=pr_title, priority=priority, actions=actions)


def send_all_phase3_notification(config: Dict[str, Any]) -> bool:
    """Send notification when all PRs become phase3

    Args:
        config: Configuration dictionary

    Returns:
        True if notification was sent successfully, False otherwise
    """
    # Check if ntfy is configured and enabled
    ntfy_config = config.get("ntfy", {})
    if not ntfy_config.get("enabled", False):
        return False

    topic = ntfy_config.get("topic")
    message = ntfy_config.get("all_phase3_message", "All PRs are now in phase3 (ready for review)")
    priority = ntfy_config.get("priority", 4)  # Default to 4 (high), configurable

    if not topic:
        print("    Warning: ntfy.topic not configured")
        return False

    # Send notification with default title
    title = "All PRs Ready for Review"
    return send_ntfy_notification(topic, message, title=title, priority=priority)
