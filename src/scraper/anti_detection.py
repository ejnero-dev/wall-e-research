"""
Sistema avanzado anti-detección para Wallapop scraper
Implementa técnicas sofisticadas para evitar detección automatizada
"""
import asyncio
import random
import time
import json
import base64
from typing import Dict, List, Optional, Tuple, Any
from playwright.async_api import Page, Browser, BrowserContext
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BrowserFingerprint:
    """Configuración de fingerprint del navegador"""
    user_agent: str
    viewport: Tuple[int, int]
    screen_resolution: Tuple[int, int]
    timezone: str
    language: str
    platform: str
    webgl_vendor: str
    webgl_renderer: str
    canvas_fingerprint: str


class AntiDetectionManager:
    """Gestor principal de medidas anti-detección"""
    
    def __init__(self):
        self.current_fingerprint: Optional[BrowserFingerprint] = None
        self.mouse_positions: List[Tuple[int, int]] = []
        self.last_action_time = time.time()
        self.action_patterns = []
        
    async def setup_browser_context(self, browser: Browser) -> BrowserContext:
        """Configura un contexto de navegador con anti-detección completa"""
        
        # Generar fingerprint único
        fingerprint = self._generate_realistic_fingerprint()
        self.current_fingerprint = fingerprint
        
        # Configurar contexto con fingerprint
        context_options = {
            "user_agent": fingerprint.user_agent,
            "viewport": {"width": fingerprint.viewport[0], "height": fingerprint.viewport[1]},
            "screen": {"width": fingerprint.screen_resolution[0], "height": fingerprint.screen_resolution[1]},
            "timezone_id": fingerprint.timezone,
            "locale": fingerprint.language,
            "geolocation": await self._get_realistic_location(),
            "permissions": ["geolocation"],
            "extra_http_headers": self._get_realistic_headers(fingerprint.user_agent),
            "java_script_enabled": True,
            "bypass_csp": True,
            "ignore_https_errors": True
        }
        
        context = await browser.new_context(**context_options)
        
        # Aplicar scripts anti-detección
        await self._inject_anti_detection_scripts(context)
        
        logger.info(f"Browser context configured with fingerprint: {fingerprint.user_agent[:50]}...")
        return context
    
    def _generate_realistic_fingerprint(self) -> BrowserFingerprint:
        """Genera un fingerprint realista y consistente"""
        
        # Seleccionar configuración realista
        configs = [
            {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "viewport": (1366, 768),
                "screen": (1920, 1080),
                "platform": "Win64",
                "webgl_vendor": "Google Inc. (Intel)",
                "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)"
            },
            {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "viewport": (1440, 900),
                "screen": (2560, 1440),
                "platform": "MacIntel",
                "webgl_vendor": "Apple Inc.",
                "webgl_renderer": "Apple M1"
            },
            {
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "viewport": (1920, 1080),
                "screen": (1920, 1080),
                "platform": "Linux x86_64",
                "webgl_vendor": "Mesa",
                "webgl_renderer": "llvmpipe (LLVM 12.0.0, 256 bits)"
            }
        ]
        
        config = random.choice(configs)
        
        return BrowserFingerprint(
            user_agent=config["user_agent"],
            viewport=config["viewport"],
            screen_resolution=config["screen"],
            timezone=random.choice(["Europe/Madrid", "Europe/Barcelona", "Europe/Valencia"]),
            language=random.choice(["es-ES", "es-ES,es;q=0.9", "es-ES,es;q=0.9,en;q=0.8"]),
            platform=config["platform"],
            webgl_vendor=config["webgl_vendor"],
            webgl_renderer=config["webgl_renderer"],
            canvas_fingerprint=self._generate_canvas_fingerprint()
        )
    
    def _generate_canvas_fingerprint(self) -> str:
        """Genera un fingerprint de canvas único pero consistente"""
        # Simular un hash de canvas realista
        import hashlib
        random_data = f"{random.randint(1000000, 9999999)}-{time.time()}"
        return hashlib.md5(random_data.encode()).hexdigest()[:16]
    
    async def _get_realistic_location(self) -> Dict[str, float]:
        """Obtiene coordenadas realistas de España"""
        # Coordenadas de ciudades principales españolas
        locations = [
            {"latitude": 40.4168, "longitude": -3.7038, "accuracy": 100},  # Madrid
            {"latitude": 41.3851, "longitude": 2.1734, "accuracy": 100},   # Barcelona
            {"latitude": 39.4699, "longitude": -0.3763, "accuracy": 100},  # Valencia
            {"latitude": 37.3891, "longitude": -5.9845, "accuracy": 100},  # Sevilla
            {"latitude": 43.2627, "longitude": -2.9253, "accuracy": 100},  # Bilbao
        ]
        
        location = random.choice(locations)
        # Añadir pequeña variación para hacer único
        location["latitude"] += random.uniform(-0.01, 0.01)
        location["longitude"] += random.uniform(-0.01, 0.01)
        
        return location
    
    def _get_realistic_headers(self, user_agent: str) -> Dict[str, str]:
        """Genera headers HTTP realistas"""
        return {
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
            "sec-ch-ua": self._generate_sec_ch_ua(user_agent),
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{self._extract_platform_from_ua(user_agent)}"'
        }
    
    def _generate_sec_ch_ua(self, user_agent: str) -> str:
        """Genera sec-ch-ua header consistente con el user agent"""
        if "Chrome/122" in user_agent:
            return '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"'
        elif "Chrome/121" in user_agent:
            return '"Chromium";v="121", "Not(A:Brand";v="24", "Google Chrome";v="121"'
        else:
            return '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"'
    
    def _extract_platform_from_ua(self, user_agent: str) -> str:
        """Extrae la plataforma del user agent"""
        if "Windows" in user_agent:
            return "Windows"
        elif "Macintosh" in user_agent:
            return "macOS"
        elif "Linux" in user_agent:
            return "Linux"
        else:
            return "Windows"
    
    async def _inject_anti_detection_scripts(self, context: BrowserContext):
        """Inyecta scripts JavaScript para evitar detección"""
        
        # Script principal anti-detección
        anti_detection_script = """
        // Ocultar automatización
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Simular propiedades de navegador real
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['es-ES', 'es', 'en'],
        });
        
        // Ocultar propiedades de Playwright
        delete window.__playwright;
        delete window.__pw_manual;
        delete window.__PW_inspect;
        
        // Simular comportamiento de mouse realista
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        EventTarget.prototype.addEventListener = function(type, listener, options) {
            if (type === 'click' || type === 'mousedown' || type === 'mouseup') {
                const wrappedListener = function(e) {
                    // Simular timing humano
                    setTimeout(() => listener.call(this, e), Math.random() * 10);
                };
                return originalAddEventListener.call(this, type, wrappedListener, options);
            }
            return originalAddEventListener.call(this, type, listener, options);
        };
        
        // WebGL spoofing
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return '%s';
            }
            if (parameter === 37446) {
                return '%s';
            }
            return getParameter(parameter);
        };
        
        // Canvas fingerprinting protection
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function() {
            // Añadir ruido mínimo consistente
            const context = this.getContext('2d');
            const originalData = context.getImageData(0, 0, this.width, this.height);
            // Modificar ligeramente algunos píxeles
            for (let i = 0; i < 10; i++) {
                const randomIndex = Math.floor(Math.random() * originalData.data.length);
                originalData.data[randomIndex] = originalData.data[randomIndex] ^ 1;
            }
            context.putImageData(originalData, 0, 0);
            return originalData.call(this);
        };
        
        console.log('Anti-detection measures activated');
        """ % (self.current_fingerprint.webgl_vendor, self.current_fingerprint.webgl_renderer)
        
        await context.add_init_script(anti_detection_script)
        
        # Script adicional para timing
        timing_script = """
        // Modificar timing de eventos para parecer más humano
        const originalSetTimeout = window.setTimeout;
        window.setTimeout = function(callback, delay, ...args) {
            const humanDelay = delay + (Math.random() * 50 - 25);
            return originalSetTimeout(callback, Math.max(humanDelay, 0), ...args);
        };
        """
        
        await context.add_init_script(timing_script)
    
    async def human_like_mouse_movement(self, page: Page, target_x: int, target_y: int):
        """Simula movimento de mouse humano con curvas realistas"""
        
        # Obtener posición actual del mouse
        current_pos = await page.evaluate("() => ({ x: window.mouseX || 0, y: window.mouseY || 0 })")
        start_x = current_pos.get("x", 0)
        start_y = current_pos.get("y", 0)
        
        # Calcular ruta curva
        control_points = self._calculate_bezier_curve(start_x, start_y, target_x, target_y)
        
        # Mover el mouse siguiendo la curva
        for i, (x, y) in enumerate(control_points):
            await page.mouse.move(x, y)
            # Delay variable para simular aceleración/desaceleración humana
            delay = self._calculate_mouse_delay(i, len(control_points))
            await asyncio.sleep(delay)
        
        # Actualizar posición para próximo movimiento
        await page.evaluate(f"window.mouseX = {target_x}; window.mouseY = {target_y}")
        self.mouse_positions.append((target_x, target_y))
    
    def _calculate_bezier_curve(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """Calcula puntos de una curva Bézier para movimento natural"""
        
        # Añadir punto de control aleatorio para curva natural
        mid_x = (start_x + end_x) / 2 + random.randint(-50, 50)
        mid_y = (start_y + end_y) / 2 + random.randint(-50, 50)
        
        points = []
        steps = random.randint(10, 20)  # Número variable de pasos
        
        for i in range(steps + 1):
            t = i / steps
            # Curva Bézier cuadrática
            x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * mid_x + t ** 2 * end_x
            y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * mid_y + t ** 2 * end_y
            points.append((int(x), int(y)))
        
        return points
    
    def _calculate_mouse_delay(self, step: int, total_steps: int) -> float:
        """Calcula delay realista para movimento de mouse"""
        # Simular aceleración al inicio y desaceleración al final
        progress = step / total_steps
        
        if progress < 0.3:  # Aceleración
            delay = 0.05 - (progress * 0.03)
        elif progress > 0.7:  # Desaceleración
            delay = 0.02 + ((progress - 0.7) * 0.03)
        else:  # Velocidad constante
            delay = 0.02
        
        # Añadir variación aleatoria
        delay += random.uniform(-0.01, 0.01)
        return max(delay, 0.001)
    
    async def human_like_typing(self, page: Page, element_selector: str, text: str):
        """Simula escritura humana con timing realista"""
        
        element = await page.wait_for_selector(element_selector)
        await element.click()
        
        # Limpiar campo
        await element.fill("")
        
        # Escribir caracter por caracter con delays humanos
        for i, char in enumerate(text):
            await element.type(char)
            
            # Calcular delay basado en el tipo de caracter
            if char == ' ':
                delay = random.uniform(0.1, 0.3)  # Pausas en espacios
            elif char in '.,;:!?':
                delay = random.uniform(0.2, 0.4)  # Pausas en puntuación
            elif i > 0 and text[i-1] == ' ':
                delay = random.uniform(0.05, 0.15)  # Inicio de palabra
            else:
                delay = random.uniform(0.05, 0.2)  # Caracter normal
            
            # Simular errores ocasionales de tipeo
            if random.random() < 0.02:  # 2% de probabilidad de error
                # Escribir caracter incorrecto
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                await element.type(wrong_char)
                await asyncio.sleep(random.uniform(0.1, 0.3))
                # Corregir con backspace
                await element.press('Backspace')
                await asyncio.sleep(random.uniform(0.1, 0.2))
                # Escribir el caracter correcto
                await element.type(char)
                delay = random.uniform(0.1, 0.3)
            
            await asyncio.sleep(delay)
    
    async def random_mouse_movements(self, page: Page, duration: float = 2.0):
        """Realiza movimientos aleatorios de mouse para simular actividad humana"""
        
        viewport = page.viewport_size
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Generar posición aleatoria dentro del viewport
            x = random.randint(50, viewport["width"] - 50)
            y = random.randint(50, viewport["height"] - 50)
            
            await self.human_like_mouse_movement(page, x, y)
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def simulate_scroll_behavior(self, page: Page):
        """Simula comportamiento de scroll realista"""
        
        # Scroll aleatorio hacia abajo
        scroll_distance = random.randint(100, 500)
        await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Ocasionalmente scroll hacia arriba
        if random.random() < 0.3:
            back_scroll = random.randint(50, scroll_distance // 2)
            await page.evaluate(f"window.scrollBy(0, -{back_scroll})")
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def add_random_delays(self):
        """Añade delays aleatorios entre acciones"""
        delay = random.uniform(1.0, 3.0)
        logger.debug(f"Adding random delay: {delay:.2f}s")
        await asyncio.sleep(delay)
    
    def record_action_pattern(self, action_type: str, duration: float):
        """Registra patrones de acción para análisis"""
        self.action_patterns.append({
            "action": action_type,
            "duration": duration,
            "timestamp": time.time()
        })
        
        # Mantener solo los últimos 50 patrones
        if len(self.action_patterns) > 50:
            self.action_patterns = self.action_patterns[-50:]
    
    def get_behavioral_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de comportamiento para análisis"""
        if not self.action_patterns:
            return {}
        
        durations = [p["duration"] for p in self.action_patterns]
        intervals = []
        
        for i in range(1, len(self.action_patterns)):
            interval = self.action_patterns[i]["timestamp"] - self.action_patterns[i-1]["timestamp"]
            intervals.append(interval)
        
        return {
            "avg_action_duration": sum(durations) / len(durations),
            "avg_interval": sum(intervals) / len(intervals) if intervals else 0,
            "total_actions": len(self.action_patterns),
            "action_types": list(set(p["action"] for p in self.action_patterns))
        }


# Instancia global del gestor anti-detección
anti_detection = AntiDetectionManager()