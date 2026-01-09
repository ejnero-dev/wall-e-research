"""
Notification System for Wall-E Auto-Detection
Handles real-time notifications for detected products and system events
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications"""

    NEW_PRODUCT = "new_product"
    PRODUCT_CHANGED = "product_changed"
    PRODUCT_REMOVED = "product_removed"
    SCANNER_ERROR = "scanner_error"
    SYSTEM_STATUS = "system_status"
    DAILY_SUMMARY = "daily_summary"


class NotificationPriority(Enum):
    """Notification priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Available notification channels"""

    WEBSOCKET = "websocket"
    EMAIL = "email"
    SLACK = "slack"
    CONSOLE = "console"
    FILE = "file"


class NotificationManager:
    """Manages all notification channels and delivery"""

    def __init__(self):
        self.channels = {}
        self.enabled = True
        self.subscribers = {}  # Channel -> list of subscribers

        # Default configuration
        self.config = {
            "email": {
                "enabled": False,
                "smtp_host": "localhost",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "wall-e@localhost",
                "to_emails": [],
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#wall-e",
                "username": "Wall-E Bot",
            },
            "websocket": {"enabled": True, "broadcast_to_dashboard": True},
            "file": {"enabled": True, "log_file": "logs/notifications.log"},
        }

        # Initialize notification log
        self.notification_log_file = Path(self.config["file"]["log_file"])
        self.notification_log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info("NotificationManager initialized")

    def configure(self, config: Dict[str, Any]):
        """Update notification configuration"""
        for channel, settings in config.items():
            if channel in self.config:
                self.config[channel].update(settings)
                logger.info(f"Updated {channel} notification settings")

    def enable_channel(self, channel: NotificationChannel, enabled: bool = True):
        """Enable/disable specific notification channel"""
        channel_name = channel.value
        if channel_name in self.config:
            self.config[channel_name]["enabled"] = enabled
            logger.info(
                f"{'Enabled' if enabled else 'Disabled'} {channel_name} notifications"
            )

    def subscribe(self, channel: NotificationChannel, callback: Callable):
        """Subscribe to notifications on a specific channel"""
        channel_name = channel.value
        if channel_name not in self.subscribers:
            self.subscribers[channel_name] = []

        self.subscribers[channel_name].append(callback)
        logger.info(f"Added subscriber to {channel_name} notifications")

    async def send_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channels: Optional[List[NotificationChannel]] = None,
    ):
        """Send notification through specified channels"""

        if not self.enabled:
            return

        notification = {
            "id": f"notif_{int(datetime.now().timestamp())}",
            "type": notification_type.value,
            "title": title,
            "message": message,
            "data": data or {},
            "priority": priority.value,
            "timestamp": datetime.now().isoformat(),
            "channels": [ch.value for ch in channels] if channels else ["all"],
        }

        # Log notification
        await self._log_notification(notification)

        # Send through all enabled channels if none specified
        if not channels:
            channels = [
                NotificationChannel.WEBSOCKET,
                NotificationChannel.CONSOLE,
                NotificationChannel.FILE,
            ]

            # Add email for high/critical priority
            if priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL]:
                if self.config["email"]["enabled"]:
                    channels.append(NotificationChannel.EMAIL)

        # Send through each channel
        tasks = []
        for channel in channels:
            if self._is_channel_enabled(channel):
                task = asyncio.create_task(
                    self._send_through_channel(channel, notification)
                )
                tasks.append(task)

        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"Error sending notifications: {e}")

    def _is_channel_enabled(self, channel: NotificationChannel) -> bool:
        """Check if notification channel is enabled"""
        channel_name = channel.value
        return self.config.get(channel_name, {}).get("enabled", False)

    async def _send_through_channel(  # noqa: C901
        self, channel: NotificationChannel, notification: Dict[str, Any]
    ):
        """Send notification through specific channel"""
        try:
            if channel == NotificationChannel.WEBSOCKET:
                await self._send_websocket(notification)
            elif channel == NotificationChannel.EMAIL:
                await self._send_email(notification)
            elif channel == NotificationChannel.SLACK:
                await self._send_slack(notification)
            elif channel == NotificationChannel.CONSOLE:
                await self._send_console(notification)
            elif channel == NotificationChannel.FILE:
                await self._send_file(notification)

            # Call custom subscribers
            channel_name = channel.value
            if channel_name in self.subscribers:
                for callback in self.subscribers[channel_name]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(notification)
                        else:
                            callback(notification)
                    except Exception as e:
                        logger.error(f"Error in notification callback: {e}")

        except Exception as e:
            logger.error(f"Error sending {channel.value} notification: {e}")

    async def _send_websocket(self, notification: Dict[str, Any]):
        """Send notification via WebSocket to dashboard"""
        try:
            # Import here to avoid circular imports
            import sys
            from pathlib import Path

            # Ensure src is in path
            src_path = str(Path(__file__).parent.parent)
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            from api.dashboard_routes import connection_manager

            websocket_message = {"type": "notification", "data": notification}

            await connection_manager.broadcast(websocket_message)
            logger.debug(f"Sent WebSocket notification: {notification['title']}")

        except Exception as e:
            logger.error(f"WebSocket notification error: {e}")

    async def _send_email(self, notification: Dict[str, Any]):
        """Send notification via email"""
        try:
            email_config = self.config["email"]

            if not email_config["to_emails"]:
                return

            subject = f"[Wall-E] {notification['title']}"

            # Create HTML email
            html_body = self._format_email_html(notification)
            text_body = self._format_email_text(notification)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = email_config["from_email"]
            msg["To"] = ", ".join(email_config["to_emails"])

            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Send email
            with smtplib.SMTP(
                email_config["smtp_host"], email_config["smtp_port"]
            ) as server:
                if email_config["username"] and email_config["password"]:
                    server.starttls()
                    server.login(email_config["username"], email_config["password"])

                server.send_message(msg)

            logger.info(f"Sent email notification: {notification['title']}")

        except Exception as e:
            logger.error(f"Email notification error: {e}")

    async def _send_slack(self, notification: Dict[str, Any]):
        """Send notification via Slack webhook"""
        try:
            import aiohttp

            slack_config = self.config["slack"]
            webhook_url = slack_config["webhook_url"]

            if not webhook_url:
                return

            # Format Slack message
            slack_message = {
                "channel": slack_config["channel"],
                "username": slack_config["username"],
                "text": f"*{notification['title']}*\n{notification['message']}",
                "attachments": [],
            }

            # Add data as attachment for detailed notifications
            if notification.get("data") and notification["type"] == "new_product":
                data = notification["data"]
                attachment = {
                    "color": (
                        "good" if notification["priority"] == "normal" else "warning"
                    ),
                    "fields": [
                        {
                            "title": "Price",
                            "value": f"€{data.get('price', 'N/A')}",
                            "short": True,
                        },
                        {
                            "title": "URL",
                            "value": data.get("url", "N/A"),
                            "short": False,
                        },
                    ],
                }
                slack_message["attachments"].append(attachment)

            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=slack_message) as response:
                    if response.status == 200:
                        logger.debug(
                            f"Sent Slack notification: {notification['title']}"
                        )
                    else:
                        logger.error(f"Slack notification failed: {response.status}")

        except Exception as e:
            logger.error(f"Slack notification error: {e}")

    async def _send_console(self, notification: Dict[str, Any]):
        """Send notification to console/stdout"""
        try:
            priority_emoji = {"low": "ℹ️", "normal": "📢", "high": "⚠️", "critical": "🚨"}

            emoji = priority_emoji.get(notification["priority"], "📢")

            print(f"\n{emoji} [{notification['type'].upper()}] {notification['title']}")
            print(f"   {notification['message']}")
            print(f"   Time: {notification['timestamp']}")

            # Print additional data for product notifications
            if notification.get("data") and notification["type"] in [
                "new_product",
                "product_changed",
            ]:
                data = notification["data"]
                if "price" in data:
                    print(f"   Price: €{data['price']}")
                if "url" in data:
                    print(f"   URL: {data['url']}")

            print()  # Empty line for readability

        except Exception as e:
            logger.error(f"Console notification error: {e}")

    async def _send_file(self, notification: Dict[str, Any]):
        """Send notification to log file"""
        try:
            log_entry = {
                "timestamp": notification["timestamp"],
                "type": notification["type"],
                "priority": notification["priority"],
                "title": notification["title"],
                "message": notification["message"],
                "data": notification.get("data", {}),
            }

            with open(self.notification_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        except Exception as e:
            logger.error(f"File notification error: {e}")

    def _format_email_html(self, notification: Dict[str, Any]) -> str:
        """Format notification as HTML email"""
        priority_colors = {
            "low": "#17a2b8",
            "normal": "#28a745",
            "high": "#ffc107",
            "critical": "#dc3545",
        }

        color = priority_colors.get(notification["priority"], "#28a745")

        html = f"""
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0;">
                    <h2 style="margin: 0;">{notification['title']}</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Priority: {notification['priority'].upper()}</p>
                </div>
                <div style="background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-top: 0; border-radius: 0 0 5px 5px;">
                    <p style="margin-top: 0;">{notification['message']}</p>
        """

        # Add product details for product notifications
        if notification.get("data") and notification["type"] in [
            "new_product",
            "product_changed",
        ]:
            data = notification["data"]
            html += "<hr><h3>Product Details:</h3><ul>"

            if "title" in data:
                html += f"<li><strong>Title:</strong> {data['title']}</li>"
            if "price" in data:
                html += f"<li><strong>Price:</strong> €{data['price']}</li>"
            if "url" in data:
                html += f"<li><strong>URL:</strong> <a href='{data['url']}'>View on Wallapop</a></li>"

            html += "</ul>"

        html += f"""
                    <hr>
                    <p style="color: #6c757d; font-size: 12px; margin-bottom: 0;">
                        Sent at: {notification['timestamp']}<br>
                        Type: {notification['type']}<br>
                        From: Wall-E Auto-Detection System
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _format_email_text(self, notification: Dict[str, Any]) -> str:
        """Format notification as plain text email"""
        text = f"""
{notification['title']}
Priority: {notification['priority'].upper()}

{notification['message']}
"""

        # Add product details
        if notification.get("data") and notification["type"] in [
            "new_product",
            "product_changed",
        ]:
            data = notification["data"]
            text += "\nProduct Details:\n"

            if "title" in data:
                text += f"- Title: {data['title']}\n"
            if "price" in data:
                text += f"- Price: €{data['price']}\n"
            if "url" in data:
                text += f"- URL: {data['url']}\n"

        text += f"""
---
Sent at: {notification['timestamp']}
Type: {notification['type']}
From: Wall-E Auto-Detection System
"""

        return text

    async def _log_notification(self, notification: Dict[str, Any]):
        """Log notification to internal log"""
        logger.info(
            f"Notification sent - Type: {notification['type']}, "
            f"Priority: {notification['priority']}, "
            f"Title: {notification['title']}"
        )

    # ===== CONVENIENCE METHODS =====

    async def notify_new_product(self, product_data: Dict[str, Any]):
        """Send new product notification"""
        await self.send_notification(
            NotificationType.NEW_PRODUCT,
            f"New Product Detected: {product_data.get('title', 'Unknown')}",
            "A new product has been automatically detected and added to your dashboard.",
            data=product_data,
            priority=NotificationPriority.NORMAL,
        )

    async def notify_product_changed(
        self, product_data: Dict[str, Any], changes: List[str]
    ):
        """Send product changed notification"""
        changes_text = ", ".join(changes) if changes else "unknown changes"

        await self.send_notification(
            NotificationType.PRODUCT_CHANGED,
            f"Product Updated: {product_data.get('title', 'Unknown')}",
            f"Product has been updated: {changes_text}",
            data={**product_data, "changes": changes},
            priority=NotificationPriority.NORMAL,
        )

    async def notify_product_removed(self, product_data: Dict[str, Any]):
        """Send product removed notification"""
        await self.send_notification(
            NotificationType.PRODUCT_REMOVED,
            f"Product Removed: {product_data.get('title', 'Unknown')}",
            "Product is no longer available on Wallapop.",
            data=product_data,
            priority=NotificationPriority.NORMAL,
        )

    async def notify_scanner_error(self, error: str):
        """Send scanner error notification"""
        await self.send_notification(
            NotificationType.SCANNER_ERROR,
            "Scanner Error Detected",
            f"Auto-detection scanner encountered an error: {error}",
            data={"error": error},
            priority=NotificationPriority.HIGH,
        )

    async def notify_system_status(self, status: str, details: Dict[str, Any]):
        """Send system status notification"""
        priority = (
            NotificationPriority.HIGH
            if status in ["error", "critical"]
            else NotificationPriority.NORMAL
        )

        await self.send_notification(
            NotificationType.SYSTEM_STATUS,
            f"System Status: {status.title()}",
            "Auto-detection system status update.",
            data=details,
            priority=priority,
        )

    async def send_daily_summary(self, summary_data: Dict[str, Any]):
        """Send daily summary notification"""
        await self.send_notification(
            NotificationType.DAILY_SUMMARY,
            "Daily Auto-Detection Summary",
            f"Daily summary: {summary_data.get('products_detected', 0)} products detected, "
            f"{summary_data.get('products_added', 0)} added to dashboard.",
            data=summary_data,
            priority=NotificationPriority.LOW,
            channels=[NotificationChannel.EMAIL, NotificationChannel.FILE],
        )


# Global notification manager instance
notification_manager = NotificationManager()
