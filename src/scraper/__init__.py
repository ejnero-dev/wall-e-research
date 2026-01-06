"""
Módulo scraper de Wallapop - Sistema completo de automatización
"""

from .wallapop_scraper import (
    WallapopScraper,
    ScraperStatus,
    MessageData,
    ConversationData,
    ProductData,
)
from .session_manager import SessionManager, SessionStatus, SessionInfo, AuthMethod
from .anti_detection import AntiDetectionManager, BrowserFingerprint
from .error_handler import ErrorHandler, ErrorSeverity, CircuitBreakerState
from .config import scraper_config, ScraperConfig, WallapopSelectors, ScraperUrls
from .utils import (
    ElementFinder,
    TextCleaner,
    TimeUtils,
    ScreenshotManager,
    RateLimiter,
    DataValidator,
    ConversationAnalyzer,
    BehaviorSimulator,
)

__version__ = "1.0.0"
__author__ = "Wallapop Bot Team"

# Instancias principales para importación fácil
__all__ = [
    # Clases principales
    "WallapopScraper",
    "SessionManager",
    "AntiDetectionManager",
    "ErrorHandler",
    # Enums
    "ScraperStatus",
    "SessionStatus",
    "AuthMethod",
    "ErrorSeverity",
    "CircuitBreakerState",
    # Dataclasses
    "MessageData",
    "ConversationData",
    "ProductData",
    "SessionInfo",
    "BrowserFingerprint",
    # Configuración
    "scraper_config",
    "ScraperConfig",
    "WallapopSelectors",
    "ScraperUrls",
    # Utilidades
    "ElementFinder",
    "TextCleaner",
    "TimeUtils",
    "ScreenshotManager",
    "RateLimiter",
    "DataValidator",
    "ConversationAnalyzer",
    "BehaviorSimulator",
]
