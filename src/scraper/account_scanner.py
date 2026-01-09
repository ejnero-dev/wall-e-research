"""
Account Scanner for Wall-E Auto-Detection System
Automatically discovers and monitors user products on Wallapop
"""

import asyncio
import time
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from .wallapop_scraper import WallapopScraper
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
    BehaviorSimulator,
)

logger = logging.getLogger(__name__)


class ProductStatus(Enum):
    """Estados del producto en Wallapop"""

    ACTIVE = "active"
    PAUSED = "paused"
    SOLD = "sold"
    EXPIRED = "expired"
    REMOVED = "removed"
    UNKNOWN = "unknown"


class ScanStatus(Enum):
    """Estados del scanner"""

    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class DetectedProduct:
    """Producto detectado en la cuenta del usuario"""

    id: str
    title: str
    price: float
    description: str
    condition: str
    location: str
    status: ProductStatus
    wallapop_url: str
    image_urls: List[str]
    views: int = 0
    favorites: int = 0
    messages_count: int = 0
    created_at: datetime = None
    last_seen: datetime = None
    last_modified: datetime = None
    hash: str = None  # Hash for change detection

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_seen is None:
            self.last_seen = datetime.now()
        if self.last_modified is None:
            self.last_modified = datetime.now()
        if self.hash is None:
            self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calcula hash del producto para detectar cambios"""
        content = (
            f"{self.title}:{self.price}:{self.status.value}:{self.description[:100]}"
        )
        return hashlib.md5(content.encode()).hexdigest()

    def has_changed(self, other: "DetectedProduct") -> bool:
        """Verifica si el producto ha cambiado"""
        return self.hash != other.hash

    def to_dashboard_format(self) -> Dict[str, Any]:
        """Convierte a formato compatible con dashboard API"""
        return {
            "wallapop_url": self.wallapop_url,
            "auto_respond": True,
            "ai_personality": "professional",
            "response_delay_min": 15,
            "response_delay_max": 60,
            # Datos adicionales para crear producto completo
            "_detected_data": {
                "title": self.title,
                "description": self.description,
                "price": self.price,
                "condition": self.condition,
                "location": self.location,
                "status": self.status.value,
                "image_urls": self.image_urls,
                "views": self.views,
                "favorites": self.favorites,
                "messages_count": self.messages_count,
            },
        }


@dataclass
class ScanResults:
    """Resultados de un escaneo"""

    timestamp: datetime
    total_products: int
    new_products: List[DetectedProduct]
    changed_products: List[Tuple[DetectedProduct, DetectedProduct]]  # (old, new)
    removed_products: List[DetectedProduct]
    errors: List[str]
    scan_duration: float


class AccountScanner:
    """Scanner automático de cuenta de Wallapop"""

    def __init__(self, auth_method: AuthMethod = AuthMethod.AUTO):
        self.status = ScanStatus.STOPPED
        self.scraper = WallapopScraper(auth_method)

        # Estados del scanner
        self.is_running = False
        self.pause_requested = False
        self.stop_requested = False
        self.scan_interval = 600  # 10 minutes default
        self.min_scan_interval = 600  # Minimum 10 minutes to avoid detection

        # Productos conocidos (en memoria)
        self.known_products: Dict[str, DetectedProduct] = {}
        self.last_scan_time: Optional[datetime] = None
        self.total_scans = 0
        self.successful_scans = 0

        # Callbacks para integración
        self.new_product_callback: Optional[callable] = None
        self.product_changed_callback: Optional[callable] = None
        self.product_removed_callback: Optional[callable] = None
        self.error_callback: Optional[callable] = None

        # Configuración de persistencia
        self.data_file = Path("data/detected_products.json")
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        # Cargar productos conocidos
        self._load_known_products()

        logger.info("AccountScanner initialized")

    async def start_scanning(self, scan_interval: int = None) -> bool:
        """Inicia el escáner automático"""
        if self.is_running:
            logger.warning("Scanner is already running")
            return True

        logger.info("Starting account scanner")
        self.status = ScanStatus.RUNNING

        if scan_interval:
            self.scan_interval = max(scan_interval, self.min_scan_interval)

        try:
            # Inicializar scraper
            success = await self.scraper.start()
            if not success:
                logger.error("Failed to start scraper for account scanning")
                self.status = ScanStatus.ERROR
                return False

            self.is_running = True
            self.stop_requested = False
            self.pause_requested = False

            # Iniciar bucle de escaneo
            asyncio.create_task(self._scanning_loop())

            logger.info(f"Account scanner started with {self.scan_interval}s interval")
            return True

        except Exception as e:
            logger.error(f"Error starting account scanner: {e}")
            error_handler.record_error(
                e, {"context": "scanner_start"}, ErrorSeverity.CRITICAL
            )
            self.status = ScanStatus.ERROR
            return False

    async def stop_scanning(self):
        """Detiene el escáner"""
        logger.info("Stopping account scanner")
        self.stop_requested = True
        self.is_running = False
        self.status = ScanStatus.STOPPED

        await self.scraper.stop()
        self._save_known_products()
        logger.info("Account scanner stopped")

    async def pause_scanning(self):
        """Pausa el escáner temporalmente"""
        logger.info("Pausing account scanner")
        self.pause_requested = True
        self.status = ScanStatus.PAUSED

    async def resume_scanning(self):
        """Reanuda el escáner"""
        logger.info("Resuming account scanner")
        self.pause_requested = False
        self.status = ScanStatus.RUNNING

    async def _scanning_loop(self):
        """Bucle principal de escaneo"""
        while not self.stop_requested:
            try:
                # Verificar si está pausado
                if self.pause_requested:
                    await asyncio.sleep(30)  # Wait 30s when paused
                    continue

                # Verificar horario de actividad
                if not TimeUtils.is_within_business_hours():
                    logger.info("Outside business hours, waiting...")
                    await asyncio.sleep(300)  # Wait 5 minutes
                    continue

                # Realizar escaneo
                start_time = time.time()
                scan_results = await self.scan_user_products()
                scan_duration = time.time() - start_time

                # Procesar resultados
                await self._process_scan_results(scan_results)

                # Actualizar estadísticas
                self.total_scans += 1
                if not scan_results.errors:
                    self.successful_scans += 1
                    self.last_scan_time = scan_results.timestamp

                logger.info(
                    f"Scan completed in {scan_duration:.1f}s. Found {len(scan_results.new_products)} new products"
                )

                # Esperar hasta próximo escaneo
                await asyncio.sleep(self.scan_interval)

            except Exception as e:
                logger.error(f"Error in scanning loop: {e}")
                error_handler.record_error(
                    e, {"context": "scanning_loop"}, ErrorSeverity.HIGH
                )

                if self.error_callback:
                    try:
                        await self.error_callback(e)
                    except Exception:
                        pass

                # Wait longer on error to avoid hammering the site
                await asyncio.sleep(min(self.scan_interval * 2, 1800))  # Max 30 minutes

        logger.info("Scanning loop ended")

    async def scan_user_products(self) -> ScanResults:
        """Escanea productos del usuario una vez"""
        start_time = time.time()
        logger.info("Starting user products scan")

        scan_results = ScanResults(
            timestamp=datetime.now(),
            total_products=0,
            new_products=[],
            changed_products=[],
            removed_products=[],
            errors=[],
            scan_duration=0,
        )

        try:
            await rate_limiter.acquire()

            # Navegar a "Mis productos"
            await self._navigate_to_my_products()

            # Obtener lista de productos
            detected_products = await self._extract_user_products()
            scan_results.total_products = len(detected_products)

            # Analizar cambios
            await self._analyze_product_changes(detected_products, scan_results)

            # Actualizar productos conocidos
            self._update_known_products(detected_products)

            # Guardar estado
            self._save_known_products()

        except Exception as e:
            error_msg = f"Error during product scan: {e}"
            logger.error(error_msg)
            scan_results.errors.append(error_msg)
            error_handler.record_error(
                e, {"context": "product_scan"}, ErrorSeverity.HIGH
            )

        scan_results.scan_duration = time.time() - start_time
        logger.info(f"Product scan completed in {scan_results.scan_duration:.1f}s")

        return scan_results

    async def _navigate_to_my_products(self):
        """Navega a la sección 'Mis productos'"""
        logger.info("Navigating to My Products section")

        try:
            # URLs posibles para "Mis productos"
            my_products_urls = [
                f"{ScraperUrls.BASE_URL}/app/profile/items",
                f"{ScraperUrls.BASE_URL}/app/my-items",
                f"{ScraperUrls.BASE_URL}/profile/products",
            ]

            # Intentar navegar a "Mis productos"
            for url in my_products_urls:
                try:
                    await self.scraper.main_page.goto(url)
                    await self.scraper.main_page.wait_for_load_state("networkidle")

                    # Verificar si estamos en la página correcta
                    if await self._verify_my_products_page():
                        logger.info(f"Successfully navigated to My Products: {url}")
                        return

                except Exception as e:
                    logger.debug(f"Failed to navigate to {url}: {e}")
                    continue

            # Si las URLs directas fallan, buscar enlace desde perfil
            await self._navigate_via_profile_menu()

        except Exception as e:
            logger.error(f"Failed to navigate to My Products: {e}")
            raise

    async def _verify_my_products_page(self) -> bool:
        """Verifica que estamos en la página de 'Mis productos'"""
        try:
            # Buscar indicadores de que estamos en "Mis productos"
            indicators = [
                "h1:has-text('Mis productos')",
                "h1:has-text('My items')",
                "[data-testid='my-products']",
                ".my-products-container",
                ".profile-products",
            ]

            for indicator in indicators:
                try:
                    element = await self.scraper.main_page.wait_for_selector(
                        indicator, timeout=3000
                    )
                    if element:
                        return True
                except Exception:
                    continue

            # Verificar URL
            current_url = self.scraper.main_page.url
            if any(
                path in current_url.lower() for path in ["profile", "items", "products"]
            ):
                return True

            return False

        except Exception as e:
            logger.debug(f"Error verifying My Products page: {e}")
            return False

    async def _navigate_via_profile_menu(self):
        """Navega a 'Mis productos' a través del menú de perfil"""
        try:
            # Ir al perfil primero
            await self.scraper.main_page.goto(ScraperUrls.PROFILE_URL)
            await self.scraper.main_page.wait_for_load_state("networkidle")

            # Buscar enlace a "Mis productos"
            product_links = [
                'a[href*="items"]',
                'a[href*="products"]',
                'a:has-text("Mis productos")',
                'a:has-text("My items")',
                '[data-testid="my-products-link"]',
            ]

            for selector in product_links:
                try:
                    link = await self.scraper.main_page.wait_for_selector(
                        selector, timeout=3000
                    )
                    if link:
                        await link.click()
                        await self.scraper.main_page.wait_for_load_state("networkidle")

                        if await self._verify_my_products_page():
                            logger.info(
                                "Successfully navigated to My Products via profile menu"
                            )
                            return
                except Exception:
                    continue

            raise Exception("Could not find link to My Products")

        except Exception as e:
            logger.error(f"Error navigating via profile menu: {e}")
            raise

    async def _extract_user_products(self) -> List[DetectedProduct]:
        """Extrae productos del usuario de la página"""
        logger.info("Extracting user products")

        detected_products = []

        try:
            # Esperar a que se carguen los productos
            await asyncio.sleep(2)

            # Selectores posibles para contenedor de productos
            container_selectors = [
                '[data-testid="products-list"]',
                ".products-grid",
                ".my-products-list",
                ".items-container",
                ".profile-items",
            ]

            products_container = await ElementFinder.find_element_with_fallback(
                self.scraper.main_page, container_selectors
            )

            if not products_container:
                logger.warning("Products container not found")
                return []

            # Selectores para elementos de productos individuales
            product_selectors = [
                '[data-testid="product-item"]',
                ".product-card",
                ".item-card",
                ".product-item",
                ".listing-item",
            ]

            product_elements = await ElementFinder.find_elements_with_fallback(
                self.scraper.main_page, product_selectors
            )

            if not product_elements:
                logger.warning("No product elements found")
                return []

            logger.info(f"Found {len(product_elements)} product elements")

            # Extraer datos de cada producto
            for i, element_info in enumerate(product_elements):
                try:
                    product = await self._extract_single_product(element_info, i)
                    if product:
                        detected_products.append(product)
                        logger.debug(f"Extracted product: {product.title}")
                except Exception as e:
                    logger.error(f"Error extracting product {i}: {e}")
                    continue

            logger.info(f"Successfully extracted {len(detected_products)} products")
            return detected_products

        except Exception as e:
            logger.error(f"Error extracting user products: {e}")
            return []

    async def _extract_single_product(  # noqa: C901
        self, element_info, index: int
    ) -> Optional[DetectedProduct]:
        """Extrae datos de un producto individual"""
        try:
            element = element_info.element

            # Título del producto
            title_selectors = [
                '[data-testid="product-title"]',
                ".product-title",
                ".item-title",
                "h3",
                "h2",
                ".title",
            ]
            title_element = await ElementFinder.find_element_with_fallback(
                element, title_selectors
            )
            title = (
                title_element.text.strip() if title_element else f"Product {index + 1}"
            )

            # Precio
            price_selectors = [
                '[data-testid="product-price"]',
                ".product-price",
                ".item-price",
                ".price",
            ]
            price_element = await ElementFinder.find_element_with_fallback(
                element, price_selectors
            )
            price = 0.0
            if price_element and price_element.text:
                price = TextCleaner.extract_price(price_element.text) or 0.0

            # URL del producto
            link_element = await element.query_selector("a[href]")
            product_url = ""
            product_id = f"detected_{int(time.time())}_{index}"

            if link_element:
                href = await link_element.get_attribute("href")
                if href:
                    if href.startswith("/"):
                        product_url = f"{ScraperUrls.BASE_URL}{href}"
                    else:
                        product_url = href

                    # Extraer ID del producto de la URL
                    if "/item/" in product_url:
                        try:
                            product_id = (
                                product_url.split("/item/")[-1]
                                .split("?")[0]
                                .split("#")[0]
                            )
                        except Exception:
                            pass

            # Estado del producto
            status = ProductStatus.ACTIVE  # Por defecto
            status_indicators = [
                ".status-sold",
                ".status-paused",
                ".status-expired",
                "[data-status]",
                ".product-status",
            ]

            for selector in status_indicators:
                try:
                    status_element = await element.query_selector(selector)
                    if status_element:
                        status_text = await status_element.text_content()
                        if status_text:
                            status_text = status_text.lower()
                            if "vendido" in status_text or "sold" in status_text:
                                status = ProductStatus.SOLD
                            elif "pausado" in status_text or "paused" in status_text:
                                status = ProductStatus.PAUSED
                            elif "expirado" in status_text or "expired" in status_text:
                                status = ProductStatus.EXPIRED
                        break
                except Exception:
                    continue

            # Descripción (si está visible)
            desc_selectors = [
                '[data-testid="product-description"]',
                ".product-description",
                ".item-description",
                ".description",
            ]
            desc_element = await ElementFinder.find_element_with_fallback(
                element, desc_selectors
            )
            description = (
                desc_element.text[:200] if desc_element and desc_element.text else ""
            )

            # Imágenes
            image_urls = []
            try:
                img_elements = await element.query_selector_all("img[src]")
                for img in img_elements[:3]:  # Máximo 3 imágenes
                    src = await img.get_attribute("src")
                    if src and src.startswith("http"):
                        image_urls.append(src)
            except Exception:
                pass

            # Estadísticas (si están disponibles)
            views = 0
            favorites = 0
            messages_count = 0

            try:
                stats_text = await element.text_content()
                if stats_text:
                    # Buscar números que podrían ser estadísticas
                    import re

                    numbers = re.findall(r"\d+", stats_text)
                    if len(numbers) >= 3:
                        views = int(numbers[-3]) if numbers[-3].isdigit() else 0
                        favorites = int(numbers[-2]) if numbers[-2].isdigit() else 0
                        messages_count = (
                            int(numbers[-1]) if numbers[-1].isdigit() else 0
                        )
            except Exception:
                pass

            return DetectedProduct(
                id=product_id,
                title=title,
                price=price,
                description=description,
                condition="unknown",  # Requeriría análisis más detallado
                location="",  # Requeriría análisis más detallado
                status=status,
                wallapop_url=product_url,
                image_urls=image_urls,
                views=views,
                favorites=favorites,
                messages_count=messages_count,
            )

        except Exception as e:
            logger.error(f"Error extracting single product: {e}")
            return None

    async def _analyze_product_changes(
        self, detected_products: List[DetectedProduct], scan_results: ScanResults
    ):
        """Analiza cambios en productos comparando con estado anterior"""
        logger.debug("Analyzing product changes")

        detected_ids = {p.id for p in detected_products}
        known_ids = set(self.known_products.keys())

        # Productos nuevos
        new_ids = detected_ids - known_ids
        scan_results.new_products = [p for p in detected_products if p.id in new_ids]

        # Productos que han cambiado
        for product in detected_products:
            if product.id in self.known_products:
                old_product = self.known_products[product.id]
                if product.has_changed(old_product):
                    scan_results.changed_products.append((old_product, product))

        # Productos eliminados/no encontrados
        removed_ids = known_ids - detected_ids
        scan_results.removed_products = [
            self.known_products[pid] for pid in removed_ids
        ]

        logger.info(
            f"Product changes: {len(scan_results.new_products)} new, "
            f"{len(scan_results.changed_products)} changed, "
            f"{len(scan_results.removed_products)} removed"
        )

    async def _process_scan_results(self, scan_results: ScanResults):  # noqa: C901
        """Procesa resultados del escaneo y ejecuta callbacks"""
        try:
            # Procesar productos nuevos
            for product in scan_results.new_products:
                logger.info(f"New product detected: {product.title} - €{product.price}")

                if self.new_product_callback:
                    try:
                        await self.new_product_callback(product)
                    except Exception as e:
                        logger.error(f"Error in new product callback: {e}")

            # Procesar productos cambiados
            for old_product, new_product in scan_results.changed_products:
                logger.info(f"Product changed: {new_product.title}")
                logger.debug(f"Changes: {old_product.hash} -> {new_product.hash}")

                if self.product_changed_callback:
                    try:
                        await self.product_changed_callback(old_product, new_product)
                    except Exception as e:
                        logger.error(f"Error in product changed callback: {e}")

            # Procesar productos eliminados
            for product in scan_results.removed_products:
                logger.info(f"Product removed: {product.title}")

                if self.product_removed_callback:
                    try:
                        await self.product_removed_callback(product)
                    except Exception as e:
                        logger.error(f"Error in product removed callback: {e}")

        except Exception as e:
            logger.error(f"Error processing scan results: {e}")

    def _update_known_products(self, detected_products: List[DetectedProduct]):
        """Actualiza la base de datos de productos conocidos"""
        # Actualizar productos existentes y añadir nuevos
        for product in detected_products:
            if product.id in self.known_products:
                # Mantener datos de creación del producto original
                original = self.known_products[product.id]
                product.created_at = original.created_at

            self.known_products[product.id] = product

        # Marcar productos no encontrados como removidos (no eliminar inmediatamente)
        detected_ids = {p.id for p in detected_products}
        for product_id in list(self.known_products.keys()):
            if product_id not in detected_ids:
                # Mantener por un tiempo por si fue un error temporal
                last_seen = self.known_products[product_id].last_seen
                if datetime.now() - last_seen > timedelta(hours=24):
                    # Eliminar después de 24h sin ver
                    del self.known_products[product_id]

    def _load_known_products(self):
        """Carga productos conocidos desde archivo"""
        try:
            if self.data_file.exists():
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for product_data in data:
                    # Convertir strings de fecha a datetime
                    for date_field in ["created_at", "last_seen", "last_modified"]:
                        if date_field in product_data and product_data[date_field]:
                            product_data[date_field] = datetime.fromisoformat(
                                product_data[date_field]
                            )

                    # Convertir status a enum
                    if "status" in product_data:
                        try:
                            product_data["status"] = ProductStatus(
                                product_data["status"]
                            )
                        except ValueError:
                            product_data["status"] = ProductStatus.UNKNOWN

                    product = DetectedProduct(**product_data)
                    self.known_products[product.id] = product

                logger.info(f"Loaded {len(self.known_products)} known products")
        except Exception as e:
            logger.error(f"Error loading known products: {e}")
            self.known_products = {}

    def _save_known_products(self):
        """Guarda productos conocidos en archivo"""
        try:
            data = []
            for product in self.known_products.values():
                product_dict = asdict(product)

                # Convertir datetime a string
                for date_field in ["created_at", "last_seen", "last_modified"]:
                    if date_field in product_dict and product_dict[date_field]:
                        product_dict[date_field] = product_dict[date_field].isoformat()

                # Convertir enum a string
                if "status" in product_dict:
                    product_dict["status"] = product_dict["status"].value

                data.append(product_dict)

            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved {len(data)} known products")

        except Exception as e:
            logger.error(f"Error saving known products: {e}")

    # ===== CALLBACKS Y CONFIGURACIÓN =====

    def set_new_product_callback(self, callback: callable):
        """Establece callback para productos nuevos detectados"""
        self.new_product_callback = callback

    def set_product_changed_callback(self, callback: callable):
        """Establece callback para productos que han cambiado"""
        self.product_changed_callback = callback

    def set_product_removed_callback(self, callback: callable):
        """Establece callback para productos eliminados"""
        self.product_removed_callback = callback

    def set_error_callback(self, callback: callable):
        """Establece callback para errores"""
        self.error_callback = callback

    def set_scan_interval(self, seconds: int):
        """Establece intervalo de escaneo (mínimo 10 minutos)"""
        self.scan_interval = max(seconds, self.min_scan_interval)
        logger.info(f"Scan interval set to {self.scan_interval}s")

    # ===== INFORMACIÓN Y ESTADÍSTICAS =====

    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado actual del scanner"""
        return {
            "status": self.status.value,
            "is_running": self.is_running,
            "is_paused": self.pause_requested,
            "scan_interval_seconds": self.scan_interval,
            "known_products_count": len(self.known_products),
            "total_scans": self.total_scans,
            "successful_scans": self.successful_scans,
            "success_rate": (self.successful_scans / max(self.total_scans, 1)) * 100,
            "last_scan_time": (
                self.last_scan_time.isoformat() if self.last_scan_time else None
            ),
            "scraper_status": self.scraper.get_status(),
        }

    def get_known_products(self) -> List[DetectedProduct]:
        """Obtiene lista de productos conocidos"""
        return list(self.known_products.values())

    def get_product_by_id(self, product_id: str) -> Optional[DetectedProduct]:
        """Obtiene un producto específico por ID"""
        return self.known_products.get(product_id)

    async def manual_scan(self) -> ScanResults:
        """Ejecuta un escaneo manual inmediato"""
        logger.info("Starting manual scan")

        if not self.scraper.is_running:
            # Inicializar scraper temporalmente para el escaneo manual
            success = await self.scraper.start()
            if not success:
                raise Exception("Failed to start scraper for manual scan")
            temp_scraper = True
        else:
            temp_scraper = False

        try:
            scan_results = await self.scan_user_products()
            await self._process_scan_results(scan_results)
            return scan_results
        finally:
            if temp_scraper:
                await self.scraper.stop()
