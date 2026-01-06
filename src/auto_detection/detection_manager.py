"""
Auto-Detection Manager for Wall-E
Manages automatic product detection and dashboard integration
"""
import asyncio
import json
import logging
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

import sys
from pathlib import Path

# Ensure src is in path for imports
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from scraper.account_scanner import AccountScanner, DetectedProduct, ScanResults, ScanStatus
from scraper.session_manager import AuthMethod
from auto_detection.notifications import notification_manager, NotificationType, NotificationPriority

logger = logging.getLogger(__name__)


class DetectionManager:
    """Gestor principal del sistema de auto-detección"""
    
    def __init__(self, dashboard_api_url: str = "http://localhost:8000/api/dashboard"):
        self.dashboard_api_url = dashboard_api_url
        self.scanner = AccountScanner(AuthMethod.AUTO)
        
        # Estado del manager
        self.is_running = False
        self.auto_add_enabled = True
        self.notification_enabled = True
        
        # Configuración
        self.config = {
            "scan_interval_minutes": 10,
            "auto_respond_new_products": True,
            "ai_personality": "professional",
            "response_delay_min": 15,
            "response_delay_max": 60,
            "max_products_per_scan": 50,
            "enable_notifications": True
        }
        
        # Estadísticas
        self.stats = {
            "products_detected": 0,
            "products_auto_added": 0,
            "api_calls_made": 0,
            "api_errors": 0,
            "last_detection_time": None,
            "uptime_start": None
        }
        
        # Cola de productos para procesar
        self.product_queue = asyncio.Queue()
        
        # Configurar callbacks del scanner
        self._setup_scanner_callbacks()
        
        logger.info("DetectionManager initialized")
    
    def _setup_scanner_callbacks(self):
        """Configura callbacks del scanner"""
        self.scanner.set_new_product_callback(self._on_new_product_detected)
        self.scanner.set_product_changed_callback(self._on_product_changed)
        self.scanner.set_product_removed_callback(self._on_product_removed)
        self.scanner.set_error_callback(self._on_scanner_error)
    
    async def start(self) -> bool:
        """Inicia el sistema de auto-detección"""
        if self.is_running:
            logger.warning("Detection manager is already running")
            return True
        
        logger.info("Starting auto-detection system")
        
        try:
            # Inicializar estadísticas
            self.stats["uptime_start"] = datetime.now()
            
            # Configurar intervalo de escaneo
            scan_interval_seconds = self.config["scan_interval_minutes"] * 60
            
            # Iniciar scanner
            success = await self.scanner.start_scanning(scan_interval_seconds)
            if not success:
                logger.error("Failed to start scanner")
                return False
            
            # Iniciar procesamiento de cola
            asyncio.create_task(self._process_product_queue())
            
            self.is_running = True
            logger.info(f"Auto-detection system started with {self.config['scan_interval_minutes']}min intervals")
            return True
            
        except Exception as e:
            logger.error(f"Error starting detection manager: {e}")
            return False
    
    async def stop(self):
        """Detiene el sistema de auto-detección"""
        logger.info("Stopping auto-detection system")
        self.is_running = False
        
        await self.scanner.stop_scanning()
        
        # Procesar productos restantes en la cola
        while not self.product_queue.empty():
            try:
                await asyncio.wait_for(self._process_product_queue(), timeout=5.0)
            except asyncio.TimeoutError:
                break
        
        logger.info("Auto-detection system stopped")
    
    async def _on_new_product_detected(self, product: DetectedProduct):
        """Callback para cuando se detecta un producto nuevo"""
        logger.info(f"New product detected: {product.title} - €{product.price}")
        
        self.stats["products_detected"] += 1
        self.stats["last_detection_time"] = datetime.now()
        
        if self.auto_add_enabled:
            # Añadir a la cola para procesamiento
            await self.product_queue.put(('new', product))
            logger.debug(f"Added new product to queue: {product.title}")
        
        if self.notification_enabled:
            await self._send_notification("new_product", {
                "title": product.title,
                "price": product.price,
                "url": product.wallapop_url,
                "status": "detected"
            })
    
    async def _on_product_changed(self, old_product: DetectedProduct, new_product: DetectedProduct):
        """Callback para cuando un producto ha cambiado"""
        logger.info(f"Product changed: {new_product.title}")
        
        # Determinar qué cambió
        changes = []
        if old_product.price != new_product.price:
            changes.append(f"price: €{old_product.price} → €{new_product.price}")
        if old_product.status != new_product.status:
            changes.append(f"status: {old_product.status.value} → {new_product.status.value}")
        if old_product.title != new_product.title:
            changes.append(f"title: '{old_product.title}' → '{new_product.title}'")
        
        logger.debug(f"Changes detected: {', '.join(changes)}")
        
        # Añadir a la cola para actualizar en dashboard
        await self.product_queue.put(('changed', new_product, changes))
        
        if self.notification_enabled:
            await self._send_notification("product_changed", {
                "title": new_product.title,
                "changes": changes,
                "url": new_product.wallapop_url
            })
    
    async def _on_product_removed(self, product: DetectedProduct):
        """Callback para cuando un producto ha sido eliminado"""
        logger.info(f"Product removed: {product.title}")
        
        # Añadir a la cola para actualizar estado
        await self.product_queue.put(('removed', product))
        
        if self.notification_enabled:
            await self._send_notification("product_removed", {
                "title": product.title,
                "url": product.wallapop_url,
                "last_seen": product.last_seen.isoformat()
            })
    
    async def _on_scanner_error(self, error: Exception):
        """Callback para errores del scanner"""
        logger.error(f"Scanner error: {error}")
        
        if self.notification_enabled:
            await self._send_notification("scanner_error", {
                "error": str(error),
                "timestamp": datetime.now().isoformat()
            })
    
    async def _process_product_queue(self):
        """Procesa la cola de productos detectados"""
        while self.is_running or not self.product_queue.empty():
            try:
                # Esperar por producto en la cola
                item = await asyncio.wait_for(self.product_queue.get(), timeout=1.0)
                
                action = item[0]
                product = item[1]
                
                try:
                    if action == 'new':
                        await self._add_product_to_dashboard(product)
                    elif action == 'changed':
                        changes = item[2] if len(item) > 2 else []
                        await self._update_product_in_dashboard(product, changes)
                    elif action == 'removed':
                        await self._mark_product_removed_in_dashboard(product)
                    
                    # Marcar tarea como completada
                    self.product_queue.task_done()
                    
                except Exception as e:
                    logger.error(f"Error processing product {action}: {e}")
                    self.stats["api_errors"] += 1
                
            except asyncio.TimeoutError:
                # Timeout normal, continúa el bucle
                continue
            except Exception as e:
                logger.error(f"Error in product queue processing: {e}")
                await asyncio.sleep(5)  # Esperar antes de reintentar
    
    async def _add_product_to_dashboard(self, product: DetectedProduct):
        """Añade un producto nuevo al dashboard"""
        logger.info(f"Adding product to dashboard: {product.title}")
        
        try:
            # Preparar datos para la API del dashboard
            product_data = {
                "wallapop_url": product.wallapop_url,
                "auto_respond": self.config["auto_respond_new_products"],
                "ai_personality": self.config["ai_personality"],
                "response_delay_min": self.config["response_delay_min"],
                "response_delay_max": self.config["response_delay_max"],
                # Datos extraídos para información adicional
                "_auto_detected": True,
                "_detected_data": {
                    "title": product.title,
                    "description": product.description,
                    "price": product.price,
                    "condition": product.condition,
                    "location": product.location,
                    "status": product.status.value,
                    "image_urls": product.image_urls,
                    "views": product.views,
                    "favorites": product.favorites,
                    "messages_count": product.messages_count,
                    "detected_at": datetime.now().isoformat()
                }
            }
            
            # Hacer llamada a la API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.dashboard_api_url}/products",
                    json=product_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    self.stats["api_calls_made"] += 1
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Successfully added product to dashboard: {result.get('id', 'unknown')}")
                        self.stats["products_auto_added"] += 1
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to add product to dashboard: {response.status} - {error_text}")
                        self.stats["api_errors"] += 1
            
        except Exception as e:
            logger.error(f"Error adding product to dashboard: {e}")
            self.stats["api_errors"] += 1
    
    async def _update_product_in_dashboard(self, product: DetectedProduct, changes: List[str]):
        """Actualiza un producto en el dashboard"""
        logger.info(f"Updating product in dashboard: {product.title}")
        
        try:
            # Buscar el producto en el dashboard por URL
            dashboard_product_id = await self._find_product_id_by_url(product.wallapop_url)
            
            if not dashboard_product_id:
                logger.warning(f"Product not found in dashboard, adding as new: {product.title}")
                await self._add_product_to_dashboard(product)
                return
            
            # Preparar datos de actualización
            update_data = {
                "price": product.price,
                "status": product.status.value,
                "views": product.views,
                "favorites": product.favorites,
                "messages_received": product.messages_count,
                "updated_at": datetime.now().isoformat(),
                "_last_changes": changes,
                "_last_scan": datetime.now().isoformat()
            }
            
            # Actualizar en dashboard
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.dashboard_api_url}/products/{dashboard_product_id}",
                    json=update_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    self.stats["api_calls_made"] += 1
                    
                    if response.status == 200:
                        logger.info(f"Successfully updated product in dashboard: {dashboard_product_id}")
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to update product in dashboard: {response.status} - {error_text}")
                        self.stats["api_errors"] += 1
            
        except Exception as e:
            logger.error(f"Error updating product in dashboard: {e}")
            self.stats["api_errors"] += 1
    
    async def _mark_product_removed_in_dashboard(self, product: DetectedProduct):
        """Marca un producto como eliminado en el dashboard"""
        logger.info(f"Marking product as removed in dashboard: {product.title}")
        
        try:
            dashboard_product_id = await self._find_product_id_by_url(product.wallapop_url)
            
            if not dashboard_product_id:
                logger.warning(f"Product not found in dashboard: {product.title}")
                return
            
            # Actualizar estado a removido
            update_data = {
                "status": "removed",
                "updated_at": datetime.now().isoformat(),
                "_removed_at": datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.dashboard_api_url}/products/{dashboard_product_id}",
                    json=update_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    self.stats["api_calls_made"] += 1
                    
                    if response.status == 200:
                        logger.info(f"Successfully marked product as removed: {dashboard_product_id}")
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to mark product as removed: {response.status} - {error_text}")
                        self.stats["api_errors"] += 1
            
        except Exception as e:
            logger.error(f"Error marking product as removed: {e}")
            self.stats["api_errors"] += 1
    
    async def _find_product_id_by_url(self, wallapop_url: str) -> Optional[str]:
        """Busca el ID de un producto en el dashboard por su URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.dashboard_api_url}/products",
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    self.stats["api_calls_made"] += 1
                    
                    if response.status == 200:
                        products = await response.json()
                        
                        # Buscar producto por URL
                        for product in products:
                            if product.get("wallapop_url") == wallapop_url:
                                return product.get("id")
                    else:
                        logger.error(f"Failed to get products from dashboard: {response.status}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding product by URL: {e}")
            return None
    
    async def _send_notification(self, notification_type: str, data: Dict[str, Any]):
        """Envía notificación sobre evento detectado"""
        try:
            # Use the integrated notification system
            if notification_type == "new_product":
                await notification_manager.notify_new_product(data)
            elif notification_type == "product_changed":
                changes = data.get("changes", [])
                await notification_manager.notify_product_changed(data, changes)
            elif notification_type == "product_removed":
                await notification_manager.notify_product_removed(data)
            elif notification_type == "scanner_error":
                await notification_manager.notify_scanner_error(data.get("error", "Unknown error"))
            else:
                # Generic notification
                await notification_manager.send_notification(
                    NotificationType.SYSTEM_STATUS,
                    f"Auto-Detection Event: {notification_type}",
                    f"System event occurred: {notification_type}",
                    data=data,
                    priority=NotificationPriority.NORMAL
                )
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    # ===== MÉTODOS DE CONFIGURACIÓN =====
    
    def update_config(self, config_updates: Dict[str, Any]):
        """Actualiza configuración del sistema"""
        for key, value in config_updates.items():
            if key in self.config:
                old_value = self.config[key]
                self.config[key] = value
                logger.info(f"Config updated: {key} = {value} (was {old_value})")
                
                # Aplicar cambios inmediatamente si es necesario
                if key == "scan_interval_minutes" and self.is_running:
                    new_interval = value * 60
                    self.scanner.set_scan_interval(new_interval)
    
    def set_auto_add_enabled(self, enabled: bool):
        """Habilita/deshabilita la adición automática de productos"""
        self.auto_add_enabled = enabled
        logger.info(f"Auto-add {'enabled' if enabled else 'disabled'}")
    
    def set_notification_enabled(self, enabled: bool):
        """Habilita/deshabilita las notificaciones"""
        self.notification_enabled = enabled
        logger.info(f"Notifications {'enabled' if enabled else 'disabled'}")
    
    # ===== MÉTODOS DE INFORMACIÓN =====
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado completo del sistema"""
        scanner_status = self.scanner.get_status()
        
        uptime = None
        if self.stats["uptime_start"]:
            uptime = str(datetime.now() - self.stats["uptime_start"])
        
        return {
            "detection_manager": {
                "is_running": self.is_running,
                "auto_add_enabled": self.auto_add_enabled,
                "notification_enabled": self.notification_enabled,
                "uptime": uptime,
                "queue_size": self.product_queue.qsize()
            },
            "scanner": scanner_status,
            "stats": self.stats,
            "config": self.config
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas detalladas"""
        return {
            **self.stats,
            "success_rate": (
                (self.stats["products_auto_added"] / max(self.stats["products_detected"], 1)) * 100
                if self.stats["products_detected"] > 0 else 0
            ),
            "api_success_rate": (
                ((self.stats["api_calls_made"] - self.stats["api_errors"]) / 
                 max(self.stats["api_calls_made"], 1)) * 100
                if self.stats["api_calls_made"] > 0 else 0
            )
        }
    
    async def manual_scan(self) -> Dict[str, Any]:
        """Ejecuta un escaneo manual"""
        logger.info("Starting manual scan")
        
        try:
            scan_results = await self.scanner.manual_scan()
            
            return {
                "success": True,
                "timestamp": scan_results.timestamp.isoformat(),
                "total_products": scan_results.total_products,
                "new_products": len(scan_results.new_products),
                "changed_products": len(scan_results.changed_products),
                "removed_products": len(scan_results.removed_products),
                "errors": scan_results.errors,
                "duration_seconds": scan_results.scan_duration
            }
            
        except Exception as e:
            logger.error(f"Error in manual scan: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }