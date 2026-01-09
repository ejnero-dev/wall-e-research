"""
Scraper principal de Wallapop con capacidades avanzadas de automatización
Implementa navegación robusta, manejo de conversaciones y anti-detección
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)
import json
from pathlib import Path

from .config import scraper_config, ScraperUrls, WallapopSelectors
from .session_manager import SessionManager, SessionStatus, AuthMethod
from .anti_detection import anti_detection
from .error_handler import error_handler, ErrorSeverity
from .utils import (
    ElementFinder,
    TextCleaner,
    TimeUtils,
    screenshot_manager,
    rate_limiter,
    ConversationAnalyzer,
    BehaviorSimulator,
)

logger = logging.getLogger(__name__)


class ScraperStatus(Enum):
    """Estados del scraper"""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class MessageData:
    """Datos de un mensaje de chat"""

    id: str
    conversation_id: str
    sender_id: str
    sender_name: str
    content: str
    timestamp: datetime
    is_read: bool
    is_from_me: bool


@dataclass
class ConversationData:
    """Datos de una conversación"""

    id: str
    buyer_id: str
    buyer_name: str
    product_id: str
    product_title: str
    last_message: Optional[MessageData]
    unread_count: int
    last_activity: datetime
    status: str


@dataclass
class ProductData:
    """Datos de un producto"""

    id: str
    title: str
    price: float
    description: str
    condition: str
    location: str
    images: List[str]
    views: int
    favorites: int
    is_active: bool


class WallapopScraper:
    """Scraper principal de Wallapop"""

    def __init__(self, auth_method: AuthMethod = AuthMethod.AUTO):
        self.status = ScraperStatus.STOPPED
        self.session_manager = SessionManager(auth_method)
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.main_page: Optional[Page] = None

        # Estados internos
        self.start_time: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
        self.total_messages_processed = 0
        self.total_conversations_handled = 0
        self.errors_count = 0

        # Control de flujo
        self.is_running = False
        self.pause_requested = False
        self.stop_requested = False

        # Callbacks para integración
        self.message_callback: Optional[callable] = None
        self.conversation_callback: Optional[callable] = None
        self.error_callback: Optional[callable] = None

    async def start(self) -> bool:
        """Inicia el scraper"""
        logger.info("Starting Wallapop scraper")
        self.status = ScraperStatus.STARTING

        try:
            # Verificar horario de actividad
            if not TimeUtils.is_within_business_hours():
                logger.info("Outside business hours, waiting...")
                await self._wait_for_business_hours()

            # Inicializar Playwright
            self.playwright = await async_playwright().start()

            # Configurar navegador con anti-detección
            await self._setup_browser()

            # Autenticarse
            session_info = await self.session_manager.authenticate(self.context)

            if session_info.status != SessionStatus.AUTHENTICATED:
                raise Exception(f"Authentication failed: {session_info.status}")

            logger.info(f"Successfully authenticated as {session_info.username}")

            # Crear página principal
            self.main_page = await self.context.new_page()

            # Navegar a página principal
            await self._navigate_to_main_page()

            # Configurar estado
            self.status = ScraperStatus.RUNNING
            self.is_running = True
            self.start_time = datetime.now()
            self.last_activity = datetime.now()

            logger.info("Scraper started successfully")
            return True

        except Exception as e:
            logger.error(f"Error starting scraper: {e}")
            error_handler.record_error(
                e, {"context": "scraper_start"}, ErrorSeverity.CRITICAL
            )
            self.status = ScraperStatus.ERROR
            await self.cleanup()
            return False

    async def stop(self):
        """Detiene el scraper de forma limpia"""
        logger.info("Stopping scraper")
        self.stop_requested = True
        self.is_running = False
        self.status = ScraperStatus.STOPPED

        await self.cleanup()
        logger.info("Scraper stopped")

    async def pause(self):
        """Pausa el scraper temporalmente"""
        logger.info("Pausing scraper")
        self.pause_requested = True
        self.status = ScraperStatus.PAUSED

    async def resume(self):
        """Reanuda el scraper"""
        logger.info("Resuming scraper")
        self.pause_requested = False
        self.status = ScraperStatus.RUNNING

    async def cleanup(self):
        """Limpia recursos del scraper"""
        try:
            if self.main_page:
                await self.main_page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    @error_handler.with_retry("page_load")
    @error_handler.with_circuit_breaker("page_load")
    async def _setup_browser(self):
        """Configura el navegador con anti-detección"""
        logger.info("Setting up browser with anti-detection")

        # Configuración del navegador
        browser_args = [
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-hang-monitor",
            "--disable-sync",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--disable-extensions-except=/path/to/extension",
            "--disable-plugins-discovery",
            "--disable-preconnect",
        ]

        # Configurar proxy si está habilitado
        proxy_config = None
        if scraper_config.should_use_proxy():
            proxy_url = scraper_config.get_random_proxy()
            if proxy_url:
                proxy_config = {"server": proxy_url}
                logger.info(f"Using proxy: {proxy_url}")

        # Lanzar navegador
        self.browser = await self.playwright.chromium.launch(
            headless=scraper_config.HEADLESS, args=browser_args, proxy=proxy_config
        )

        # Configurar contexto con anti-detección
        self.context = await anti_detection.setup_browser_context(self.browser)

        logger.info("Browser setup completed")

    async def _navigate_to_main_page(self):
        """Navega a la página principal"""
        logger.info("Navigating to main page")

        await self.main_page.goto(ScraperUrls.BASE_URL)
        await self.main_page.wait_for_load_state("networkidle")

        # Tomar screenshot si está habilitado
        if scraper_config.SCREENSHOT_ON_ERROR:
            await screenshot_manager.take_screenshot(
                self.main_page, "main_page_loaded", "navigation"
            )

    async def _wait_for_business_hours(self):
        """Espera hasta el horario comercial"""
        while not TimeUtils.is_within_business_hours():
            logger.info("Waiting for business hours...")
            await asyncio.sleep(300)  # Verificar cada 5 minutos

    # ===== FUNCIONALIDADES PRINCIPALES =====

    async def get_conversations(self) -> List[ConversationData]:
        """Obtiene lista de conversaciones activas"""
        logger.info("Getting conversations list")

        try:
            await rate_limiter.acquire()

            # Navegar a página de chat
            await self.main_page.goto(ScraperUrls.CHAT_URL)
            await self.main_page.wait_for_load_state("networkidle")

            # Buscar lista de conversaciones
            conversations_list = await ElementFinder.find_element_with_fallback(
                self.main_page, WallapopSelectors.CHAT_LIST
            )

            if not conversations_list:
                logger.warning("No conversations list found")
                return []

            # Obtener elementos de conversaciones
            conversation_elements = await ElementFinder.find_elements_with_fallback(
                self.main_page, WallapopSelectors.CHAT_ITEM
            )

            conversations = []
            for element_info in conversation_elements:
                try:
                    conv_data = await self._extract_conversation_data(element_info)
                    if conv_data:
                        conversations.append(conv_data)
                except Exception as e:
                    logger.error(f"Error extracting conversation data: {e}")
                    continue

            logger.info(f"Found {len(conversations)} conversations")
            return conversations

        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            error_handler.record_error(
                e, {"context": "get_conversations"}, ErrorSeverity.HIGH
            )
            return []

    async def _extract_conversation_data(
        self, element_info
    ) -> Optional[ConversationData]:
        """Extrae datos de una conversación"""
        try:
            element = element_info.element

            # Extraer información básica
            conversation_id = (
                await element.get_attribute("data-conversation-id")
                or await element.get_attribute("id")
                or f"conv_{int(time.time())}"
            )

            # Nombre del comprador
            buyer_name_selectors = [
                ".buyer-name",
                ".username",
                ".contact-name",
                '[data-testid="buyer-name"]',
            ]
            buyer_name_element = await ElementFinder.find_element_with_fallback(
                element, buyer_name_selectors
            )
            buyer_name = buyer_name_element.text if buyer_name_element else "Unknown"

            # Último mensaje
            last_message_selectors = [
                ".last-message",
                ".message-preview",
                '[data-testid="last-message"]',
            ]
            last_message_element = await ElementFinder.find_element_with_fallback(
                element, last_message_selectors
            )
            last_message_text = (
                last_message_element.text if last_message_element else ""
            )

            # Contador de mensajes no leídos
            unread_badge = await ElementFinder.find_element_with_fallback(
                element, WallapopSelectors.UNREAD_BADGE
            )
            unread_count = 0
            if unread_badge and unread_badge.text:
                try:
                    unread_count = int(unread_badge.text)
                except ValueError:
                    unread_count = 1 if unread_badge.text else 0

            # Producto asociado
            product_title_selectors = [
                ".product-title",
                ".item-title",
                '[data-testid="product-title"]',
            ]
            product_title_element = await ElementFinder.find_element_with_fallback(
                element, product_title_selectors
            )
            product_title = (
                product_title_element.text
                if product_title_element
                else "Unknown Product"
            )

            return ConversationData(
                id=conversation_id,
                buyer_id=f"buyer_{conversation_id}",
                buyer_name=TextCleaner.normalize_username(buyer_name),
                product_id=f"product_{conversation_id}",
                product_title=product_title,
                last_message=(
                    MessageData(
                        id=f"msg_{int(time.time())}",
                        conversation_id=conversation_id,
                        sender_id=f"buyer_{conversation_id}",
                        sender_name=buyer_name,
                        content=TextCleaner.clean_message_text(last_message_text),
                        timestamp=datetime.now(),
                        is_read=unread_count == 0,
                        is_from_me=False,
                    )
                    if last_message_text
                    else None
                ),
                unread_count=unread_count,
                last_activity=datetime.now(),
                status="active",
            )

        except Exception as e:
            logger.error(f"Error extracting conversation data: {e}")
            return None

    async def get_messages(self, conversation_id: str) -> List[MessageData]:
        """Obtiene mensajes de una conversación específica"""
        logger.info(f"Getting messages for conversation {conversation_id}")

        try:
            await rate_limiter.acquire()

            # Abrir conversación específica
            await self._open_conversation(conversation_id)

            # Buscar contenedor de mensajes
            messages_container = await ElementFinder.find_element_with_fallback(
                self.main_page, WallapopSelectors.MESSAGE_LIST
            )

            if not messages_container:
                logger.warning(
                    f"No messages container found for conversation {conversation_id}"
                )
                return []

            # Obtener elementos de mensajes
            message_elements = await ElementFinder.find_elements_with_fallback(
                self.main_page, WallapopSelectors.MESSAGE_ITEM
            )

            messages = []
            for element_info in message_elements:
                try:
                    msg_data = await self._extract_message_data(
                        element_info, conversation_id
                    )
                    if msg_data:
                        messages.append(msg_data)
                except Exception as e:
                    logger.error(f"Error extracting message data: {e}")
                    continue

            logger.info(
                f"Found {len(messages)} messages in conversation {conversation_id}"
            )
            return messages

        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            error_handler.record_error(
                e,
                {"context": "get_messages", "conversation_id": conversation_id},
                ErrorSeverity.HIGH,
            )
            return []

    async def _open_conversation(self, conversation_id: str):
        """Abre una conversación específica"""
        try:
            # Buscar y hacer click en la conversación
            conversation_selector = f'[data-conversation-id="{conversation_id}"]'
            conversation_element = await self.main_page.wait_for_selector(
                conversation_selector, timeout=5000
            )

            if conversation_element:
                await conversation_element.click()
                await self.main_page.wait_for_load_state("networkidle")
            else:
                # Fallback: buscar por posición en lista
                conversations = await self.main_page.query_selector_all(
                    WallapopSelectors.CHAT_ITEM[0]
                )
                if conversations:
                    await conversations[0].click()  # Abrir primera conversación
                    await self.main_page.wait_for_load_state("networkidle")

        except Exception as e:
            logger.error(f"Error opening conversation {conversation_id}: {e}")
            raise

    async def _extract_message_data(
        self, element_info, conversation_id: str
    ) -> Optional[MessageData]:
        """Extrae datos de un mensaje"""
        try:
            element = element_info.element

            # Contenido del mensaje
            message_content_selectors = [
                ".message-content",
                ".message-text",
                '[data-testid="message-content"]',
            ]
            content_element = await ElementFinder.find_element_with_fallback(
                element, message_content_selectors
            )
            content = content_element.text if content_element else ""

            if not content:
                return None

            # Determinar si es mensaje propio
            is_from_me = await element.evaluate(
                "el => el.classList.contains('own-message') || el.classList.contains('sent')"
            )

            # Información del remitente
            sender_name = "Me" if is_from_me else "Buyer"
            sender_id = "me" if is_from_me else f"buyer_{conversation_id}"

            # Timestamp (si está disponible)
            timestamp_selectors = [
                ".message-time",
                ".timestamp",
                '[data-testid="message-time"]',
            ]
            await ElementFinder.find_element_with_fallback(element, timestamp_selectors)
            timestamp = datetime.now()  # Por defecto, usar tiempo actual

            # Estado de lectura
            is_read = not await element.evaluate(
                "el => el.classList.contains('unread')"
            )

            return MessageData(
                id=f"msg_{conversation_id}_{int(time.time())}",
                conversation_id=conversation_id,
                sender_id=sender_id,
                sender_name=sender_name,
                content=TextCleaner.clean_message_text(content),
                timestamp=timestamp,
                is_read=is_read,
                is_from_me=is_from_me,
            )

        except Exception as e:
            logger.error(f"Error extracting message data: {e}")
            return None

    @error_handler.with_retry("message_send")
    @error_handler.with_circuit_breaker("message_send")
    async def send_message(self, conversation_id: str, message: str) -> bool:
        """Envía un mensaje a una conversación"""
        logger.info(f"Sending message to conversation {conversation_id}")

        try:
            await rate_limiter.acquire()

            # Abrir conversación
            await self._open_conversation(conversation_id)

            # Simular tiempo de lectura antes de responder
            reading_time = await BehaviorSimulator.simulate_reading_time(len(message))
            await asyncio.sleep(min(reading_time, 5.0))  # Máximo 5 segundos

            # Simular tiempo de reflexión
            thinking_time = await BehaviorSimulator.simulate_thinking_time()
            await asyncio.sleep(min(thinking_time, 3.0))  # Máximo 3 segundos

            # Buscar campo de entrada de mensaje
            message_input = await ElementFinder.find_element_with_fallback(
                self.main_page, WallapopSelectors.MESSAGE_INPUT
            )

            if not message_input:
                raise Exception("Message input field not found")

            # Escribir mensaje con comportamiento humano
            await anti_detection.human_like_typing(
                self.main_page, WallapopSelectors.MESSAGE_INPUT[0], message
            )

            # Esperar un momento antes de enviar
            await asyncio.sleep(scraper_config.get_human_delay())

            # Buscar y hacer click en botón de envío
            send_button = await ElementFinder.find_element_with_fallback(
                self.main_page, WallapopSelectors.SEND_BUTTON
            )

            if not send_button:
                # Alternativa: usar Enter
                await self.main_page.keyboard.press("Enter")
            else:
                await send_button.element.click()

            # Esperar confirmación de envío
            await asyncio.sleep(2.0)

            # Verificar que el mensaje se envió
            success = await self._verify_message_sent(message)

            if success:
                self.total_messages_processed += 1
                self.last_activity = datetime.now()
                logger.info(
                    f"Message sent successfully to conversation {conversation_id}"
                )
            else:
                raise Exception("Message sending verification failed")

            return success

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            error_handler.record_error(
                e,
                {
                    "context": "send_message",
                    "conversation_id": conversation_id,
                    "message_length": len(message),
                },
                ErrorSeverity.HIGH,
            )
            return False

    async def _verify_message_sent(self, message: str) -> bool:
        """Verifica que el mensaje se envió correctamente"""
        try:
            # Buscar el mensaje recién enviado en la conversación
            message_elements = await self.main_page.query_selector_all(
                WallapopSelectors.MESSAGE_ITEM[0]
            )

            # Verificar los últimos mensajes
            for element in message_elements[-3:]:  # Revisar últimos 3 mensajes
                try:
                    content = await element.text_content()
                    is_own = await element.evaluate(
                        "el => el.classList.contains('own-message') || el.classList.contains('sent')"
                    )

                    if is_own and message in content:
                        return True
                except Exception:
                    continue

            return False

        except Exception as e:
            logger.error(f"Error verifying message sent: {e}")
            return False

    async def get_product_details(self, product_id: str) -> Optional[ProductData]:
        """Obtiene detalles de un producto específico"""
        logger.info(f"Getting product details for {product_id}")

        try:
            await rate_limiter.acquire()

            # Navegar a página del producto
            product_url = ScraperUrls.product_url(product_id)
            await self.main_page.goto(product_url)
            await self.main_page.wait_for_load_state("networkidle")

            # Extraer información del producto
            title = await self._extract_product_title()
            price = await self._extract_product_price()
            description = await self._extract_product_description()
            condition = await self._extract_product_condition()
            location = await self._extract_product_location()
            images = await self._extract_product_images()

            return ProductData(
                id=product_id,
                title=title or "Unknown Product",
                price=price or 0.0,
                description=description or "",
                condition=condition or "unknown",
                location=location or "",
                images=images,
                views=0,  # Estos datos requerirían scraping adicional
                favorites=0,
                is_active=True,
            )

        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            error_handler.record_error(
                e,
                {"context": "get_product_details", "product_id": product_id},
                ErrorSeverity.MEDIUM,
            )
            return None

    async def _extract_product_title(self) -> Optional[str]:
        """Extrae título del producto"""
        title_element = await ElementFinder.find_element_with_fallback(
            self.main_page, WallapopSelectors.PRODUCT_TITLE
        )
        return title_element.text if title_element else None

    async def _extract_product_price(self) -> Optional[float]:
        """Extrae precio del producto"""
        price_element = await ElementFinder.find_element_with_fallback(
            self.main_page, WallapopSelectors.PRODUCT_PRICE
        )
        if price_element and price_element.text:
            return TextCleaner.extract_price(price_element.text)
        return None

    async def _extract_product_description(self) -> Optional[str]:
        """Extrae descripción del producto"""
        desc_element = await ElementFinder.find_element_with_fallback(
            self.main_page, WallapopSelectors.PRODUCT_DESCRIPTION
        )
        return desc_element.text if desc_element else None

    async def _extract_product_condition(self) -> Optional[str]:
        """Extrae condición del producto"""
        condition_selectors = [
            ".product-condition",
            ".item-condition",
            '[data-testid="condition"]',
        ]
        condition_element = await ElementFinder.find_element_with_fallback(
            self.main_page, condition_selectors
        )
        return condition_element.text if condition_element else None

    async def _extract_product_location(self) -> Optional[str]:
        """Extrae ubicación del producto"""
        location_selectors = [
            ".product-location",
            ".item-location",
            '[data-testid="location"]',
        ]
        location_element = await ElementFinder.find_element_with_fallback(
            self.main_page, location_selectors
        )
        return location_element.text if location_element else None

    async def _extract_product_images(self) -> List[str]:
        """Extrae URLs de imágenes del producto"""
        try:
            image_selectors = [
                ".product-images img",
                ".item-gallery img",
                '[data-testid="product-image"]',
            ]

            images = []
            for selector in image_selectors:
                try:
                    img_elements = await self.main_page.query_selector_all(selector)
                    for img in img_elements:
                        src = await img.get_attribute("src")
                        if src and src.startswith("http"):
                            images.append(src)
                    if images:
                        break
                except Exception:
                    continue

            return images[:5]  # Máximo 5 imágenes

        except Exception as e:
            logger.error(f"Error extracting product images: {e}")
            return []

    # ===== CALLBACKS Y EVENTOS =====

    def set_message_callback(self, callback: callable):
        """Establece callback para nuevos mensajes"""
        self.message_callback = callback

    def set_conversation_callback(self, callback: callable):
        """Establece callback para nuevas conversaciones"""
        self.conversation_callback = callback

    def set_error_callback(self, callback: callable):
        """Establece callback para errores"""
        self.error_callback = callback

    # ===== MONITOREO Y ESTADÍSTICAS =====

    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado actual del scraper"""
        uptime = None
        if self.start_time:
            uptime = str(datetime.now() - self.start_time)

        return {
            "status": self.status.value,
            "is_running": self.is_running,
            "uptime": uptime,
            "total_messages_processed": self.total_messages_processed,
            "total_conversations_handled": self.total_conversations_handled,
            "errors_count": self.errors_count,
            "last_activity": (
                self.last_activity.isoformat() if self.last_activity else None
            ),
            "session_info": self.session_manager.get_session_stats(),
        }

    async def health_check(self) -> Dict[str, Any]:
        """Realiza health check del scraper"""
        health = {
            "healthy": True,
            "timestamp": datetime.now().isoformat(),
            "checks": {},
        }

        # Verificar estado del navegador
        try:
            if self.browser and self.context and self.main_page:
                await self.main_page.evaluate("document.title")
                health["checks"]["browser"] = "ok"
            else:
                health["checks"]["browser"] = "down"
                health["healthy"] = False
        except Exception as e:
            health["checks"]["browser"] = f"error: {str(e)}"
            health["healthy"] = False

        # Verificar sesión
        session_info = self.session_manager.get_session_info()
        if session_info and session_info.status == SessionStatus.AUTHENTICATED:
            health["checks"]["session"] = "authenticated"
        else:
            health["checks"]["session"] = "not_authenticated"
            health["healthy"] = False

        # Verificar conectividad
        try:
            await self.main_page.goto(ScraperUrls.BASE_URL, timeout=10000)
            health["checks"]["connectivity"] = "ok"
        except Exception as e:
            health["checks"]["connectivity"] = f"error: {str(e)}"
            health["healthy"] = False

        return health
