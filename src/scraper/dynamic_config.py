"""
Dynamic Configuration for Wallapop Scraper
Eliminates hardcoded values by using centralized configuration system
"""

import os
import random
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path

# Import configuration system
try:
    from enhanced_config_loader import (
        get_config_loader,
        get_config_value,
        ConfigChangeEvent,
    )

    CONFIG_LOADER_AVAILABLE = True
except ImportError:
    try:
        from src.enhanced_config_loader import (
            get_config_loader,
            get_config_value,
            ConfigChangeEvent,
        )

        CONFIG_LOADER_AVAILABLE = True
    except ImportError:
        CONFIG_LOADER_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class DynamicScraperConfig:
    """
    Dynamic configuration for the scraper that reads from centralized config
    Replaces hardcoded values with configuration-driven approach
    """

    # Configuration loader reference
    _config_loader = None
    _current_config: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize configuration after creation"""
        if CONFIG_LOADER_AVAILABLE:
            try:
                self._config_loader = get_config_loader()
                self._current_config = self._config_loader._current_config

                # Register for configuration changes
                self._config_loader.add_change_callback(self._on_config_changed)
                logger.info("Dynamic scraper configuration initialized with hot-reload")
            except Exception as e:
                logger.warning(f"Could not initialize config loader: {e}")
        else:
            logger.warning(
                "Enhanced config loader not available, using fallback values"
            )

    def _on_config_changed(self, config: Dict[str, Any], event: ConfigChangeEvent):
        """Handle configuration change events"""
        self._current_config = config
        logger.info(f"Scraper configuration updated due to: {event}")

    def _get_config_value(self, key_path: str, default_value: Any = None) -> Any:
        """Get configuration value with fallback to default"""
        if CONFIG_LOADER_AVAILABLE and self._current_config:
            try:
                keys = key_path.split(".")
                value = self._current_config

                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        return default_value
                return value
            except Exception as e:
                logger.error(f"Error getting config value '{key_path}': {e}")
                return default_value
        else:
            return default_value

    # Dynamic properties that read from configuration

    @property
    def min_delay_seconds(self) -> int:
        """Minimum delay between actions"""
        return self._get_config_value("scraper.timing.min_delay_seconds", 30)

    @property
    def max_delay_seconds(self) -> int:
        """Maximum delay between actions"""
        return self._get_config_value("scraper.timing.max_delay_seconds", 120)

    @property
    def page_load_timeout(self) -> int:
        """Page load timeout in seconds"""
        return self._get_config_value("scraper.timing.page_load_timeout", 30)

    @property
    def element_timeout(self) -> int:
        """Element wait timeout in seconds"""
        return self._get_config_value("scraper.timing.element_timeout", 10)

    @property
    def headless(self) -> bool:
        """Run browser in headless mode"""
        return self._get_config_value("scraper.browser.headless", True)

    @property
    def viewport_width(self) -> int:
        """Browser viewport width"""
        return self._get_config_value("scraper.browser.viewport.width", 1366)

    @property
    def viewport_height(self) -> int:
        """Browser viewport height"""
        return self._get_config_value("scraper.browser.viewport.height", 768)

    @property
    def user_agents(self) -> List[str]:
        """List of user agents for rotation"""
        default_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        ]
        return self._get_config_value("scraper.user_agents", default_agents)

    @property
    def default_headers(self) -> Dict[str, str]:
        """Default HTTP headers"""
        default_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
        }
        return self._get_config_value("scraper.headers", default_headers)

    @property
    def proxy_list(self) -> List[str]:
        """List of proxy servers"""
        return self._get_config_value("scraper.proxy.proxy_list", [])

    @property
    def rotate_proxy(self) -> bool:
        """Whether to rotate proxy servers"""
        return self._get_config_value("scraper.proxy.rotation_enabled", False)

    @property
    def cookies_file(self) -> str:
        """Path to cookies file"""
        data_dir = self._get_config_value("file_paths.data_dir", "data")
        cookies_file = self._get_config_value(
            "file_paths.files.cookies_file", "wallapop_cookies.json"
        )
        return str(Path(data_dir) / cookies_file)

    @property
    def session_timeout_hours(self) -> int:
        """Session timeout in hours"""
        return self._get_config_value("scraper.session.timeout_hours", 24)

    @property
    def max_login_attempts(self) -> int:
        """Maximum login attempts"""
        return self._get_config_value("scraper.session.max_login_attempts", 3)

    @property
    def max_concurrent_conversations(self) -> int:
        """Maximum concurrent conversations"""
        return self._get_config_value("scraper.limits.max_concurrent_conversations", 5)

    @property
    def max_messages_per_hour(self) -> int:
        """Maximum messages per hour"""
        return self._get_config_value("scraper.limits.max_messages_per_hour", 50)

    @property
    def max_actions_per_minute(self) -> int:
        """Maximum actions per minute"""
        return self._get_config_value("scraper.limits.max_actions_per_minute", 2)

    @property
    def active_hours_start(self) -> int:
        """Active hours start (hour of day)"""
        time_str = self._get_config_value(
            "scraper.schedule.active_hours.start", "09:00"
        )
        return int(time_str.split(":")[0])

    @property
    def active_hours_end(self) -> int:
        """Active hours end (hour of day)"""
        time_str = self._get_config_value("scraper.schedule.active_hours.end", "22:00")
        return int(time_str.split(":")[0])

    @property
    def timezone(self) -> str:
        """Timezone for active hours"""
        return self._get_config_value(
            "scraper.schedule.active_hours.timezone", "Europe/Madrid"
        )

    @property
    def rate_limit_reset_interval(self) -> int:
        """Rate limit reset interval in seconds"""
        return self._get_config_value(
            "scraper.rate_limiting.reset_interval_seconds", 3600
        )

    @property
    def circuit_breaker_threshold(self) -> int:
        """Circuit breaker error threshold"""
        return self._get_config_value(
            "scraper.rate_limiting.circuit_breaker.threshold", 5
        )

    @property
    def circuit_breaker_timeout(self) -> int:
        """Circuit breaker timeout in seconds"""
        return self._get_config_value(
            "scraper.rate_limiting.circuit_breaker.timeout_seconds", 300
        )

    # Notification settings
    @property
    def slack_webhook_url(self) -> Optional[str]:
        """Slack webhook URL for notifications"""
        return self._get_config_value("notifications.slack.webhook_url")

    @property
    def email_alerts(self) -> bool:
        """Whether email alerts are enabled"""
        return self._get_config_value("notifications.email.enabled", False)

    @property
    def smtp_host(self) -> str:
        """SMTP server host"""
        return self._get_config_value("notifications.email.smtp.host", "localhost")

    @property
    def smtp_port(self) -> int:
        """SMTP server port"""
        return self._get_config_value("notifications.email.smtp.port", 587)

    @property
    def email_from(self) -> str:
        """From email address"""
        return self._get_config_value("notifications.email.addresses.from", "")

    @property
    def email_to(self) -> str:
        """To email address"""
        return self._get_config_value("notifications.email.addresses.to", "")

    # Logging settings
    @property
    def log_level(self) -> str:
        """Logging level"""
        return self._get_config_value("logging.level", "INFO")

    @property
    def log_file(self) -> str:
        """Log file path"""
        logs_dir = self._get_config_value("file_paths.logs_dir", "logs")
        scraper_log = self._get_config_value(
            "file_paths.files.scraper_log", "wallapop_scraper.log"
        )
        return str(Path(logs_dir) / scraper_log)

    @property
    def screenshot_on_error(self) -> bool:
        """Whether to take screenshots on error"""
        return self._get_config_value("development.debugging.save_screenshots", True)

    @property
    def screenshot_dir(self) -> str:
        """Screenshot directory path"""
        return self._get_config_value("file_paths.screenshots_dir", "debug/screenshots")

    # Helper methods with configuration-aware logic
    def get_random_user_agent(self) -> str:
        """Get a random User-Agent from the configured list"""
        agents = self.user_agents
        return (
            random.choice(agents) if agents else "Mozilla/5.0 (compatible; Wall-E Bot)"
        )

    def get_human_delay(self) -> float:
        """Generate a humanized delay with configurable parameters"""
        min_delay = self.min_delay_seconds
        max_delay = self.max_delay_seconds

        # Use distribution beta for realistic human behavior
        base_delay = random.uniform(min_delay, max_delay)

        # Add micro-variations
        micro_variation = random.uniform(-2, 5)

        return max(base_delay + micro_variation, min_delay)

    def get_typing_delay(self, text_length: int) -> float:
        """Calculate realistic typing delay for text"""
        # Configurable typing speed (characters per second)
        chars_per_second = random.uniform(1.5, 3.0)  # 45-65 WPM approximately
        base_time = text_length / chars_per_second

        # Add thinking pauses
        thinking_pauses = random.uniform(0.5, 2.0)

        return base_time + thinking_pauses

    def should_use_proxy(self) -> bool:
        """Determine if proxy should be used"""
        return self.rotate_proxy and len(self.proxy_list) > 0

    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy if configured"""
        if self.should_use_proxy():
            return random.choice(self.proxy_list)
        return None

    def is_within_active_hours(self) -> bool:
        """Check if current time is within active hours"""
        import datetime
        import pytz

        try:
            tz = pytz.timezone(self.timezone)
            current_time = datetime.datetime.now(tz)
            current_hour = current_time.hour

            return self.active_hours_start <= current_hour <= self.active_hours_end
        except Exception:
            # If timezone error, assume active
            return True


class DynamicWallapopSelectors:
    """
    Dynamic selectors that read from configuration
    Allows for easy updates without code changes
    """

    def __init__(self, config: Optional[DynamicScraperConfig] = None):
        self.config = config or DynamicScraperConfig()

    def _get_selectors(self, selector_path: str) -> List[str]:
        """Get selector list from configuration"""
        default_selectors = ["[data-testid]", ".default-selector"]
        if self.config._current_config:
            return self.config._get_config_value(
                f"wallapop.selectors.{selector_path}", default_selectors
            )
        return default_selectors

    @property
    def login_button(self) -> List[str]:
        return self._get_selectors("login.login_button")

    @property
    def email_input(self) -> List[str]:
        return self._get_selectors("login.email_input")

    @property
    def password_input(self) -> List[str]:
        return self._get_selectors("login.password_input")

    @property
    def login_submit(self) -> List[str]:
        return self._get_selectors("login.submit_button")

    @property
    def chat_list(self) -> List[str]:
        return self._get_selectors("chat.chat_list")

    @property
    def chat_item(self) -> List[str]:
        return self._get_selectors("chat.chat_item")

    @property
    def unread_badge(self) -> List[str]:
        return self._get_selectors("chat.unread_badge")

    @property
    def message_input(self) -> List[str]:
        return self._get_selectors("chat.message_input")

    @property
    def send_button(self) -> List[str]:
        return self._get_selectors("chat.send_button")

    @property
    def message_list(self) -> List[str]:
        return self._get_selectors("chat.message_list")

    @property
    def message_item(self) -> List[str]:
        return self._get_selectors("chat.message_item")

    @property
    def notifications_icon(self) -> List[str]:
        return self._get_selectors("navigation.notifications_icon")

    @property
    def profile_menu(self) -> List[str]:
        return self._get_selectors("navigation.profile_menu")

    @property
    def product_title(self) -> List[str]:
        return self._get_selectors("products.title")

    @property
    def product_price(self) -> List[str]:
        return self._get_selectors("products.price")

    @property
    def product_description(self) -> List[str]:
        return self._get_selectors("products.description")


class DynamicScraperUrls:
    """
    Dynamic URLs that read from configuration
    """

    def __init__(self, config: Optional[DynamicScraperConfig] = None):
        self.config = config or DynamicScraperConfig()

    @property
    def base_url(self) -> str:
        return self.config._get_config_value(
            "wallapop.urls.base_url", "https://es.wallapop.com"
        )

    @property
    def login_url(self) -> str:
        base = self.base_url
        path = self.config._get_config_value("wallapop.urls.login_url", "/app/login")
        return f"{base}{path}"

    @property
    def chat_url(self) -> str:
        base = self.base_url
        path = self.config._get_config_value("wallapop.urls.chat_url", "/app/chat")
        return f"{base}{path}"

    @property
    def notifications_url(self) -> str:
        base = self.base_url
        path = self.config._get_config_value(
            "wallapop.urls.notifications_url", "/app/notifications"
        )
        return f"{base}{path}"

    @property
    def profile_url(self) -> str:
        base = self.base_url
        path = self.config._get_config_value(
            "wallapop.urls.profile_url", "/app/profile"
        )
        return f"{base}{path}"

    def product_url(self, product_id: str) -> str:
        return f"{self.base_url}/item/{product_id}"

    def chat_url_with_id(self, chat_id: str) -> str:
        return f"{self.chat_url}/{chat_id}"


# Global instances for easy access
dynamic_scraper_config = DynamicScraperConfig()
dynamic_selectors = DynamicWallapopSelectors(dynamic_scraper_config)
dynamic_urls = DynamicScraperUrls(dynamic_scraper_config)


def get_scraper_config() -> DynamicScraperConfig:
    """Get the global dynamic scraper configuration"""
    return dynamic_scraper_config


def get_wallapop_selectors() -> DynamicWallapopSelectors:
    """Get the global dynamic selectors"""
    return dynamic_selectors


def get_wallapop_urls() -> DynamicScraperUrls:
    """Get the global dynamic URLs"""
    return dynamic_urls


# Migration helper to update existing code
def migrate_from_static_config():
    """
    Helper function to demonstrate how to migrate from static to dynamic config
    This shows the mapping between old hardcoded values and new config paths
    """
    migration_map = {
        "ScraperConfig.MIN_DELAY": "scraper.timing.min_delay_seconds",
        "ScraperConfig.MAX_DELAY": "scraper.timing.max_delay_seconds",
        "ScraperConfig.HEADLESS": "scraper.browser.headless",
        "ScraperConfig.VIEWPORT_WIDTH": "scraper.browser.viewport.width",
        "ScraperConfig.VIEWPORT_HEIGHT": "scraper.browser.viewport.height",
        "ScraperConfig.USER_AGENTS": "scraper.user_agents",
        "ScraperConfig.DEFAULT_HEADERS": "scraper.headers",
        "ScraperConfig.COOKIES_FILE": "file_paths.files.cookies_file (+ data_dir)",
        "ScraperConfig.SMTP_HOST": "notifications.email.smtp.host",
        "ScraperConfig.SMTP_PORT": "notifications.email.smtp.port",
        "ScraperUrls.BASE_URL": "wallapop.urls.base_url",
        "WallapopSelectors.LOGIN_BUTTON": "wallapop.selectors.login.login_button",
        # ... etc
    }

    print("Migration map from static to dynamic configuration:")
    for old_path, new_path in migration_map.items():
        print(f"  {old_path} → {new_path}")


if __name__ == "__main__":
    # Test the dynamic configuration
    logging.basicConfig(level=logging.INFO)

    config = get_scraper_config()
    selectors = get_wallapop_selectors()
    urls = get_wallapop_urls()

    print("Dynamic Scraper Configuration Test:")
    print(f"  Min delay: {config.min_delay_seconds}s")
    print(f"  Max delay: {config.max_delay_seconds}s")
    print(f"  Headless: {config.headless}")
    print(f"  Viewport: {config.viewport_width}x{config.viewport_height}")
    print(f"  Base URL: {urls.base_url}")
    print(f"  Login selectors: {selectors.login_button}")
    print(f"  Random User-Agent: {config.get_random_user_agent()}")
    print(f"  Human delay: {config.get_human_delay():.2f}s")
    print(
        f"  Active hours: {config.active_hours_start}:00 - {config.active_hours_end}:00"
    )
    print(f"  Within active hours: {config.is_within_active_hours()}")

    # Show migration information
    print("\n" + "=" * 50)
    migrate_from_static_config()
