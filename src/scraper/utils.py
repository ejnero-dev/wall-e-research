"""
Utilidades compartidas para el scraper de Wallapop
"""
import asyncio
import re
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import hashlib
import json
from playwright.async_api import Page, ElementHandle
from dataclasses import dataclass
import pytz

logger = logging.getLogger(__name__)


@dataclass
class ElementInfo:
    """Información sobre un elemento encontrado"""
    element: ElementHandle
    selector: str
    text: Optional[str] = None
    attributes: Dict[str, str] = None


class TextCleaner:
    """Utilidades para limpiar y normalizar texto"""
    
    @staticmethod
    def clean_message_text(text: str) -> str:
        """Limpia texto de mensajes"""
        if not text:
            return ""
        
        # Remover espacios extra y saltos de línea
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remover caracteres especiales problemáticos
        text = re.sub(r'[^\w\s.,;:!?¿¡áéíóúÁÉÍÓÚñÑ()-]', '', text)
        
        return text
    
    @staticmethod
    def extract_price(text: str) -> Optional[float]:
        """Extrae precio de texto"""
        if not text:
            return None
        
        # Buscar patrones de precio
        price_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*€',  # 1.500,50 €
            r'€\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # € 1.500,50
            r'(\d+(?:\.\d{3})*(?:,\d{2})?)\s*euros?',  # 1.500,50 euros
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*eur',  # 1.500,50 eur
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1)
                # Convertir formato español a float
                price_str = price_str.replace('.', '').replace(',', '.')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def normalize_username(username: str) -> str:
        """Normaliza nombre de usuario"""
        if not username:
            return ""
        
        return username.strip().lower()
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extrae URLs de texto"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)


class ElementFinder:
    """Utilidades para encontrar elementos de forma robusta"""
    
    @staticmethod
    async def find_element_with_fallback(page: Page, selectors: List[str], timeout: int = 5000) -> Optional[ElementInfo]:
        """Busca elemento probando múltiples selectores"""
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=timeout)
                if element:
                    text = await element.text_content()
                    attributes = await element.evaluate("el => Object.fromEntries(Array.from(el.attributes).map(attr => [attr.name, attr.value]))")
                    
                    return ElementInfo(
                        element=element,
                        selector=selector,
                        text=text,
                        attributes=attributes
                    )
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        return None
    
    @staticmethod
    async def find_elements_with_fallback(page: Page, selectors: List[str]) -> List[ElementInfo]:
        """Busca múltiples elementos probando selectores"""
        elements = []
        
        for selector in selectors:
            try:
                element_handles = await page.query_selector_all(selector)
                for element in element_handles:
                    text = await element.text_content()
                    attributes = await element.evaluate("el => Object.fromEntries(Array.from(el.attributes).map(attr => [attr.name, attr.value]))")
                    
                    elements.append(ElementInfo(
                        element=element,
                        selector=selector,
                        text=text,
                        attributes=attributes
                    ))
                
                if elements:
                    break  # Si encontramos elementos, no probar más selectores
                    
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        return elements
    
    @staticmethod
    async def wait_for_any_selector(page: Page, selectors: List[str], timeout: int = 10000) -> Optional[str]:
        """Espera a que aparezca cualquiera de los selectores"""
        start_time = time.time()
        
        while (time.time() - start_time) * 1000 < timeout:
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        return selector
                except Exception:
                    pass
            
            await asyncio.sleep(0.1)
        
        return None


class RateLimiter:
    """Control de velocidad de requests"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """Espera hasta que se pueda hacer otro request"""
        current_time = time.time()
        
        # Limpiar requests antiguos
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.time_window]
        
        # Si hemos alcanzado el límite, esperar
        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.time_window - (current_time - oldest_request)
            
            if wait_time > 0:
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
        
        # Registrar este request
        self.requests.append(current_time)


class TimeUtils:
    """Utilidades de tiempo y zona horaria"""
    
    @staticmethod
    def is_within_business_hours(timezone: str = "Europe/Madrid") -> bool:
        """Verifica si estamos en horario comercial"""
        try:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            
            # Horario comercial: 9 AM - 10 PM
            return 9 <= current_time.hour <= 22
        except Exception:
            return True  # Por defecto, asumir que sí
    
    @staticmethod
    def get_human_delay(min_seconds: float = 1.0, max_seconds: float = 5.0) -> float:
        """Genera delay humanizado"""
        # Usar distribución beta para comportamiento más realista
        import numpy as np
        
        try:
            # Distribución beta que favorece delays medios
            beta_sample = np.random.beta(2, 2)  # Forma de campana
            delay = min_seconds + (max_seconds - min_seconds) * beta_sample
            
            # Añadir micro-variaciones
            micro_jitter = random.uniform(-0.1, 0.1)
            delay += micro_jitter
            
            return max(delay, min_seconds)
            
        except ImportError:
            # Fallback si numpy no está disponible
            return random.uniform(min_seconds, max_seconds)
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Formatea duración en formato legible"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


class ScreenshotManager:
    """Gestor de capturas de pantalla para debugging"""
    
    def __init__(self, screenshots_dir: str = "debug/screenshots"):
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    async def take_screenshot(self, page: Page, name: str, context: str = "") -> str:
        """Toma captura de pantalla con nombre descriptivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.png"
        
        if context:
            filename = f"{timestamp}_{context}_{name}.png"
        
        filepath = self.screenshots_dir / filename
        
        try:
            await page.screenshot(path=str(filepath), full_page=True)
            logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return ""
    
    async def take_element_screenshot(self, element: ElementHandle, name: str) -> str:
        """Toma captura de un elemento específico"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_element_{name}.png"
        filepath = self.screenshots_dir / filename
        
        try:
            await element.screenshot(path=str(filepath))
            logger.info(f"Element screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error taking element screenshot: {e}")
            return ""


class DataValidator:
    """Validadores de datos"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Valida formato de teléfono español"""
        # Formatos: +34 xxx xxx xxx, 6xx xxx xxx, 7xx xxx xxx, 9xx xxx xxx
        pattern = r'^(\+34\s?)?[679]\d{8}$'
        clean_phone = re.sub(r'[\s-]', '', phone)
        return bool(re.match(pattern, clean_phone))
    
    @staticmethod
    def is_suspicious_message(message: str) -> bool:
        """Detecta mensajes sospechosos"""
        suspicious_patterns = [
            r'western\s+union',
            r'paypal\s+familia',
            r'mi\s+transportista',
            r'adelantado',
            r'verificar\s+tarjeta',
            r'whatsapp',
            r'telegram',
            r'https?://bit\.ly',
            r'https?://tinyurl'
        ]
        
        message_lower = message.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False


class HashUtils:
    """Utilidades de hash para identificadores únicos"""
    
    @staticmethod
    def generate_conversation_id(buyer_id: str, product_id: str) -> str:
        """Genera ID único para conversación"""
        content = f"{buyer_id}_{product_id}_{int(time.time())}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    @staticmethod
    def generate_message_id(conversation_id: str, timestamp: float, content: str) -> str:
        """Genera ID único para mensaje"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        return f"{conversation_id}_{int(timestamp)}_{content_hash}"
    
    @staticmethod
    def hash_sensitive_data(data: str) -> str:
        """Hash para datos sensibles"""
        return hashlib.sha256(data.encode()).hexdigest()


class UrlUtils:
    """Utilidades para manejo de URLs"""
    
    @staticmethod
    def extract_product_id(url: str) -> Optional[str]:
        """Extrae ID de producto de URL de Wallapop"""
        patterns = [
            r'/item/([a-zA-Z0-9-]+)',
            r'/products/([a-zA-Z0-9-]+)',
            r'wallapop\.com/.*?([a-fA-F0-9]{24})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def extract_user_id(url: str) -> Optional[str]:
        """Extrae ID de usuario de URL"""
        patterns = [
            r'/user/([a-zA-Z0-9-]+)',
            r'/users/([a-zA-Z0-9-]+)',
            r'/profile/([a-zA-Z0-9-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def is_wallapop_url(url: str) -> bool:
        """Verifica si es URL de Wallapop"""
        return 'wallapop.com' in url.lower()


class BehaviorSimulator:
    """Simula comportamiento humano realista"""
    
    @staticmethod
    async def simulate_reading_time(text_length: int) -> float:
        """Calcula tiempo de lectura realista"""
        # Velocidad de lectura promedio: 200-250 palabras por minuto
        words = text_length / 5  # Aproximadamente 5 caracteres por palabra
        reading_speed = random.uniform(200, 250)  # WPM
        
        base_time = (words / reading_speed) * 60  # Segundos
        
        # Añadir factor de comprensión/atención
        attention_factor = random.uniform(1.2, 2.0)
        
        return base_time * attention_factor
    
    @staticmethod
    async def simulate_thinking_time() -> float:
        """Simula tiempo de reflexión antes de responder"""
        # Tiempo de reflexión humano típico
        return random.uniform(2.0, 8.0)
    
    @staticmethod
    async def simulate_typing_breaks(text: str) -> List[float]:
        """Genera pausas realistas durante la escritura"""
        breaks = []
        words = text.split()
        
        for i, word in enumerate(words):
            if i > 0:
                # Pausa entre palabras
                breaks.append(random.uniform(0.1, 0.4))
            
            # Pausa después de puntuación
            if word.endswith(('.', '!', '?', ':')):
                breaks.append(random.uniform(0.3, 1.0))
            elif word.endswith(','):
                breaks.append(random.uniform(0.2, 0.6))
        
        return breaks


class ConversationAnalyzer:
    """Analizador de patrones de conversación"""
    
    @staticmethod
    def detect_urgency(message: str) -> float:
        """Detecta nivel de urgencia en mensaje (0-1)"""
        urgency_keywords = [
            ('urgente', 0.9),
            ('rápido', 0.7),
            ('ahora', 0.8),
            ('ya', 0.6),
            ('inmediato', 0.9),
            ('hoy', 0.7),
            ('prisa', 0.8)
        ]
        
        message_lower = message.lower()
        max_urgency = 0.0
        
        for keyword, score in urgency_keywords:
            if keyword in message_lower:
                max_urgency = max(max_urgency, score)
        
        # Detectar signos de exclamación múltiples
        exclamation_count = message.count('!')
        if exclamation_count > 1:
            max_urgency = max(max_urgency, min(0.6 + (exclamation_count * 0.1), 1.0))
        
        return max_urgency
    
    @staticmethod
    def detect_purchase_intent(message: str) -> float:
        """Detecta intención de compra (0-1)"""
        purchase_keywords = [
            ('lo quiero', 0.9),
            ('me lo llevo', 0.9),
            ('lo compro', 0.9),
            ('interesado', 0.7),
            ('me interesa', 0.7),
            ('reservar', 0.8),
            ('apartar', 0.6),
            ('cuando puedo', 0.8),
            ('donde quedamos', 0.9),
            ('efectivo', 0.7),
            ('bizum', 0.8)
        ]
        
        message_lower = message.lower()
        max_intent = 0.0
        
        for keyword, score in purchase_keywords:
            if keyword in message_lower:
                max_intent = max(max_intent, score)
        
        return max_intent


# Instancias globales de utilidades
screenshot_manager = ScreenshotManager()
rate_limiter = RateLimiter(max_requests=30, time_window=60)  # 30 requests por minuto