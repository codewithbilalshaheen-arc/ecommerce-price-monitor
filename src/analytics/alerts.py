import logging
import requests
from typing import Optional
from src.config import SLACK_WEBHOOK_URL, ALERT_EMAIL_RECIPIENT

logger = logging.getLogger(__name__)


def send_slack_notification(message: str, webhook_url: Optional[str] = None) -> bool:
    """Send alert message to Slack webhook."""
    url = webhook_url or SLACK_WEBHOOK_URL
    if not url:
        logger.info(f"[Slack Alert - No Webhook Configured]: {message}")
        return False

    try:
        response = requests.post(url, json={"text": message}, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")
        return False


def send_email_notification(subject: str, message: str, recipient: Optional[str] = None) -> bool:
    """Send alert email (simulated/logged if no SMTP server configured)."""
    to = recipient or ALERT_EMAIL_RECIPIENT
    logger.info(f"[Email Alert to {to or 'configured recipient'}]: {subject}\n{message}")
    return True
