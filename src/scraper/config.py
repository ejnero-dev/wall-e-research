"""
Configuración específica del scraper de Wallapop
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random
import time


@dataclass
class ScraperConfig:
    """Configuración del scraper con valores optimizados para anti-detección"""

    # Anti-detección básica
    MIN_DELAY: int = 30  # Segundos entre acciones
    MAX_DELAY: int = 120
    PAGE_LOAD_TIMEOUT: int = 30
    ELEMENT_TIMEOUT: int = 10

    # Configuración de navegador
    HEADLESS: bool = True
    VIEWPORT_WIDTH: int = 1366
    VIEWPORT_HEIGHT: int = 768

    # User agents rotativos realistas
    USER_AGENTS: List[str] = None

    # Headers HTTP realistas
    DEFAULT_HEADERS: Dict[str, str] = None

    # Proxies (opcional)
    PROXY_LIST: List[str] = None
    ROTATE_PROXY: bool = False

    # Configuración de sesión
    COOKIES_FILE: str = "wallapop_cookies.json"
    SESSION_TIMEOUT_HOURS: int = 24
    MAX_LOGIN_ATTEMPTS: int = 3

    # Límites de seguridad
    MAX_CONCURRENT_CONVERSATIONS: int = 5
    MAX_MESSAGES_PER_HOUR: int = 50
    MAX_ACTIONS_PER_MINUTE: int = 2

    # Horario de actividad
    ACTIVE_HOURS_START: int = 9
    ACTIVE_HOURS_END: int = 22
    TIMEZONE: str = "Europe/Madrid"

    # Rate limiting
    RATE_LIMIT_RESET_INTERVAL: int = 3600  # 1 hora
    CIRCUIT_BREAKER_THRESHOLD: int = 5
    CIRCUIT_BREAKER_TIMEOUT: int = 300  # 5 minutos

    # Alertas y monitoreo
    SLACK_WEBHOOK_URL: Optional[str] = None
    EMAIL_ALERTS: bool = False
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    EMAIL_FROM: str = ""
    EMAIL_TO: str = ""

    # Configuración de logs
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "wallapop_scraper.log"
    SCREENSHOT_ON_ERROR: bool = True
    SCREENSHOT_DIR: str = "debug/screenshots"

    def __post_init__(self):
        """Inicializar valores por defecto después de la creación"""
        if self.USER_AGENTS is None:
            self.USER_AGENTS = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
            ]

        if self.DEFAULT_HEADERS is None:
            self.DEFAULT_HEADERS = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            }

        if self.PROXY_LIST is None:
            self.PROXY_LIST = []

    def get_random_user_agent(self) -> str:
        """Obtiene un User-Agent aleatorio"""
        return random.choice(self.USER_AGENTS)

    def get_human_delay(self) -> float:
        """Genera un delay humanizado con distribución realista"""
        # Usar distribución beta para simular comportamiento humano más realista
        base_delay = random.uniform(self.MIN_DELAY, self.MAX_DELAY)

        # Añadir micro-variaciones para hacer más realista
        micro_variation = random.uniform(-2, 5)

        return max(base_delay + micro_variation, self.MIN_DELAY)

    def get_typing_delay(self, text_length: int) -> float:
        """Calcula delay realista para escribir texto"""
        # Simular velocidad de escritura humana (40-70 WPM)
        chars_per_second = random.uniform(1.5, 3.0)  # Aproximadamente 45-65 WPM
        base_time = text_length / chars_per_second

        # Añadir pausas realistas para palabras largas
        thinking_pauses = random.uniform(0.5, 2.0)

        return base_time + thinking_pauses

    def should_use_proxy(self) -> bool:
        """Determina si usar proxy en esta sesión"""
        return self.ROTATE_PROXY and len(self.PROXY_LIST) > 0

    def get_random_proxy(self) -> Optional[str]:
        """Obtiene un proxy aleatorio si está configurado"""
        if self.should_use_proxy():
            return random.choice(self.PROXY_LIST)
        return None

    def is_within_active_hours(self) -> bool:
        """Verifica si estamos dentro del horario de actividad"""
        import datetime
        import pytz

        try:
            tz = pytz.timezone(self.TIMEZONE)
            current_time = datetime.datetime.now(tz)
            current_hour = current_time.hour

            return self.ACTIVE_HOURS_START <= current_hour <= self.ACTIVE_HOURS_END
        except Exception:
            # Si hay error con timezone, asumir que está en horario activo
            return True


class WallapopSelectors:
    """Selectores CSS para elementos de Wallapop con múltiples estrategias"""

    # Login
    LOGIN_BUTTON = [
        'button[data-testid="login-button"]',
        'a[href*="login"]',
        'button:has-text("Iniciar sesión")',
        ".login-button",
        "#login-btn",
    ]

    EMAIL_INPUT = [
        'input[data-testid="email-input"]',
        'input[type="email"]',
        'input[name="email"]',
        "#email",
        ".email-input",
    ]

    PASSWORD_INPUT = [
        'input[data-testid="password-input"]',
        'input[type="password"]',
        'input[name="password"]',
        "#password",
        ".password-input",
    ]

    LOGIN_SUBMIT = [
        'button[data-testid="login-submit"]',
        'button[type="submit"]',
        'button:has-text("Entrar")',
        ".login-submit",
        "#login-submit",
    ]

    # Chat y mensajes
    CHAT_LIST = [
        '[data-testid="chat-list"]',
        ".chat-list",
        ".conversations-list",
        "#chat-container ul",
    ]

    CHAT_ITEM = [
        '[data-testid="chat-item"]',
        ".chat-item",
        ".conversation-item",
        ".chat-list li",
    ]

    UNREAD_BADGE = [
        '[data-testid="unread-badge"]',
        ".unread-badge",
        ".notification-badge",
        ".badge-unread",
    ]

    MESSAGE_INPUT = [
        '[data-testid="message-input"]',
        'textarea[placeholder*="Escribe"]',
        ".message-input textarea",
        "#message-textarea",
    ]

    SEND_BUTTON = [
        '[data-testid="send-button"]',
        'button[aria-label*="Enviar"]',
        ".send-button",
        "#send-btn",
    ]

    MESSAGE_LIST = [
        '[data-testid="messages-list"]',
        ".messages-container",
        ".chat-messages",
        "#messages",
    ]

    MESSAGE_ITEM = [
        '[data-testid="message"]',
        ".message-item",
        ".chat-message",
        ".message",
    ]

    # Navegación
    NOTIFICATIONS_ICON = [
        '[data-testid="notifications"]',
        ".notifications-icon",
        'button[aria-label*="Notificaciones"]',
        "#notifications-btn",
    ]

    PROFILE_MENU = [
        '[data-testid="profile-menu"]',
        ".profile-menu",
        ".user-menu",
        "#profile-dropdown",
    ]

    # Productos
    PRODUCT_TITLE = [
        '[data-testid="product-title"]',
        ".product-title",
        "h1.title",
        ".item-title",
    ]

    PRODUCT_PRICE = [
        '[data-testid="product-price"]',
        ".product-price",
        ".price",
        ".item-price",
    ]

    PRODUCT_DESCRIPTION = [
        '[data-testid="product-description"]',
        ".product-description",
        ".description",
        ".item-description",
    ]


class ScraperUrls:
    """URLs importantes de Wallapop"""

    BASE_URL = "https://es.wallapop.com"
    LOGIN_URL = f"{BASE_URL}/app/login"
    CHAT_URL = f"{BASE_URL}/app/chat"
    NOTIFICATIONS_URL = f"{BASE_URL}/app/notifications"
    PROFILE_URL = f"{BASE_URL}/app/profile"

    @staticmethod
    def product_url(product_id: str) -> str:
        return f"{ScraperUrls.BASE_URL}/item/{product_id}"

    @staticmethod
    def chat_url(chat_id: str) -> str:
        return f"{ScraperUrls.CHAT_URL}/{chat_id}"


# Instancia global de configuración
scraper_config = ScraperConfig()
