"""
Gestor de sesiones y autenticación multi-método para Wallapop
Maneja cookies persistentes, credenciales fallback y rotación automática
"""

import asyncio
import json
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from playwright.async_api import Page, BrowserContext, Cookie
import base64
from cryptography.fernet import Fernet
import hashlib

from .config import scraper_config, ScraperUrls, WallapopSelectors
from .error_handler import error_handler, ErrorSeverity
from .anti_detection import anti_detection

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Métodos de autenticación disponibles"""

    COOKIES = "cookies"
    CREDENTIALS = "credentials"
    AUTO = "auto"


class SessionStatus(Enum):
    """Estados de la sesión"""

    NOT_AUTHENTICATED = "not_authenticated"
    AUTHENTICATED = "authenticated"
    EXPIRED = "expired"
    BLOCKED = "blocked"
    ERROR = "error"


@dataclass
class SessionInfo:
    """Información de la sesión actual"""

    status: SessionStatus
    auth_method: AuthMethod
    user_id: Optional[str] = None
    username: Optional[str] = None
    login_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    session_duration: Optional[timedelta] = None
    cookies_count: int = 0
    is_verified: bool = False


class CookieManager:
    """Gestor de cookies con persistencia y cifrado"""

    def __init__(self, cookies_file: str = "wallapop_cookies.json"):
        self.cookies_file = Path(cookies_file)
        self.encryption_key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)

    def _get_or_create_key(self) -> bytes:
        """Obtiene o crea una clave de cifrado"""
        key_file = Path("session.key")

        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            return key

    def save_cookies(self, cookies: List[Cookie], metadata: Dict[str, Any] = None):
        """Guarda cookies de forma segura con cifrado"""
        try:
            data = {
                "cookies": [self._cookie_to_dict(cookie) for cookie in cookies],
                "metadata": metadata or {},
                "saved_at": datetime.now().isoformat(),
                "version": "1.0",
            }

            json_data = json.dumps(data, indent=2)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())

            # Crear directorio si no existe
            self.cookies_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.cookies_file, "wb") as f:
                f.write(encrypted_data)

            logger.info(f"Saved {len(cookies)} cookies to {self.cookies_file}")

        except Exception as e:
            logger.error(f"Error saving cookies: {e}")
            raise

    def load_cookies(self) -> Tuple[List[Dict], Dict[str, Any]]:
        """Carga cookies del archivo cifrado"""
        try:
            if not self.cookies_file.exists():
                logger.info("No cookies file found")
                return [], {}

            with open(self.cookies_file, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())

            cookies = data.get("cookies", [])
            metadata = data.get("metadata", {})

            logger.info(f"Loaded {len(cookies)} cookies")
            return cookies, metadata

        except Exception as e:
            logger.error(f"Error loading cookies: {e}")
            return [], {}

    def _cookie_to_dict(self, cookie: Cookie) -> Dict:
        """Convierte objeto Cookie a diccionario"""
        return {
            "name": cookie.get("name"),
            "value": cookie.get("value"),
            "domain": cookie.get("domain"),
            "path": cookie.get("path", "/"),
            "expires": cookie.get("expires", -1),
            "httpOnly": cookie.get("httpOnly", False),
            "secure": cookie.get("secure", False),
            "sameSite": cookie.get("sameSite", "Lax"),
        }

    def are_cookies_valid(self, metadata: Dict[str, Any]) -> bool:
        """Verifica si las cookies siguen siendo válidas"""
        try:
            saved_at = datetime.fromisoformat(metadata.get("saved_at", ""))
            max_age = timedelta(hours=scraper_config.SESSION_TIMEOUT_HOURS)

            return datetime.now() - saved_at < max_age

        except Exception:
            return False

    def clear_cookies(self):
        """Elimina el archivo de cookies"""
        try:
            if self.cookies_file.exists():
                self.cookies_file.unlink()
                logger.info("Cookies cleared")
        except Exception as e:
            logger.error(f"Error clearing cookies: {e}")


class CredentialManager:
    """Gestor de credenciales cifradas"""

    def __init__(self):
        self.credentials_file = Path("credentials.enc")
        self.cipher_suite = Fernet(self._get_encryption_key())

    def _get_encryption_key(self) -> bytes:
        """Genera clave basada en el sistema"""
        # Usar información del sistema para generar clave consistente
        system_info = f"{os.getlogin()}-{os.path.basename(os.getcwd())}"
        key_material = hashlib.sha256(system_info.encode()).digest()
        return base64.urlsafe_b64encode(key_material)

    def save_credentials(self, username: str, password: str):
        """Guarda credenciales cifradas"""
        try:
            data = {
                "username": username,
                "password": password,
                "saved_at": datetime.now().isoformat(),
            }

            json_data = json.dumps(data)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())

            with open(self.credentials_file, "wb") as f:
                f.write(encrypted_data)

            logger.info("Credentials saved securely")

        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            raise

    def load_credentials(self) -> Optional[Tuple[str, str]]:
        """Carga credenciales cifradas"""
        try:
            if not self.credentials_file.exists():
                return None

            with open(self.credentials_file, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())

            return data["username"], data["password"]

        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return None


class SessionManager:
    """Gestor principal de sesiones y autenticación"""

    def __init__(self, auth_method: AuthMethod = AuthMethod.AUTO):
        self.auth_method = auth_method
        self.cookie_manager = CookieManager()
        self.credential_manager = CredentialManager()
        self.current_session: Optional[SessionInfo] = None
        self.login_attempts = 0
        self.last_login_attempt: Optional[datetime] = None

    async def authenticate(self, context: BrowserContext) -> SessionInfo:
        """Proceso principal de autenticación"""
        logger.info(f"Starting authentication with method: {self.auth_method.value}")

        # Verificar si ya hay una sesión válida
        if (
            self.current_session
            and self.current_session.status == SessionStatus.AUTHENTICATED
        ):
            if self._is_session_valid():
                logger.info("Using existing valid session")
                return self.current_session

        # Intentar autenticación según método configurado
        if self.auth_method == AuthMethod.COOKIES:
            session_info = await self._authenticate_with_cookies(context)
        elif self.auth_method == AuthMethod.CREDENTIALS:
            session_info = await self._authenticate_with_credentials(context)
        else:  # AUTO
            session_info = await self._authenticate_auto(context)

        self.current_session = session_info
        return session_info

    @error_handler.with_retry("login")
    @error_handler.with_circuit_breaker("login")
    async def _authenticate_with_cookies(self, context: BrowserContext) -> SessionInfo:
        """Autenticación usando cookies guardadas"""
        logger.info("Attempting authentication with cookies")

        try:
            # Cargar cookies
            cookies, metadata = self.cookie_manager.load_cookies()

            if not cookies:
                raise Exception("No cookies found")

            if not self.cookie_manager.are_cookies_valid(metadata):
                raise Exception("Cookies are expired")

            # Aplicar cookies al contexto
            await context.add_cookies(cookies)

            # Crear página y verificar autenticación
            page = await context.new_page()

            try:
                # Navegar a página principal
                await page.goto(ScraperUrls.BASE_URL)
                await page.wait_for_load_state("networkidle")

                # Verificar si estamos autenticados
                is_authenticated = await self._verify_authentication(page)

                if is_authenticated:
                    user_info = await self._extract_user_info(page)

                    session_info = SessionInfo(
                        status=SessionStatus.AUTHENTICATED,
                        auth_method=AuthMethod.COOKIES,
                        user_id=user_info.get("user_id"),
                        username=user_info.get("username"),
                        login_time=datetime.now(),
                        last_activity=datetime.now(),
                        cookies_count=len(cookies),
                        is_verified=user_info.get("is_verified", False),
                    )

                    logger.info(
                        f"Successfully authenticated with cookies as {user_info.get('username')}"
                    )
                    return session_info
                else:
                    raise Exception("Cookie authentication failed - not logged in")

            finally:
                await page.close()

        except Exception as e:
            logger.error(f"Cookie authentication failed: {e}")
            error_handler.record_error(e, {"method": "cookies"}, ErrorSeverity.MEDIUM)

            return SessionInfo(
                status=SessionStatus.NOT_AUTHENTICATED, auth_method=AuthMethod.COOKIES
            )

    @error_handler.with_retry("login")
    @error_handler.with_circuit_breaker("login")
    async def _authenticate_with_credentials(
        self, context: BrowserContext
    ) -> SessionInfo:
        """Autenticación usando credenciales"""
        logger.info("Attempting authentication with credentials")

        try:
            # Verificar límite de intentos de login
            if not self._can_attempt_login():
                raise Exception("Too many login attempts, waiting before retry")

            self.login_attempts += 1
            self.last_login_attempt = datetime.now()

            # Cargar credenciales
            credentials = self.credential_manager.load_credentials()
            if not credentials:
                raise Exception("No credentials found")

            username, password = credentials

            # Crear página y realizar login
            page = await context.new_page()

            try:
                # Navegar a página de login
                logger.info("Navigating to login page")
                await page.goto(ScraperUrls.LOGIN_URL)
                await page.wait_for_load_state("networkidle")

                # Buscar y llenar formulario de login
                await self._fill_login_form(page, username, password)

                # Esperar redirección o confirmación
                await page.wait_for_load_state("networkidle")

                # Verificar si el login fue exitoso
                is_authenticated = await self._verify_authentication(page)

                if is_authenticated:
                    # Extraer información del usuario
                    user_info = await self._extract_user_info(page)

                    # Guardar cookies para futuras sesiones
                    cookies = await context.cookies()
                    self.cookie_manager.save_cookies(
                        cookies,
                        {
                            "username": username,
                            "login_method": "credentials",
                            "user_info": user_info,
                        },
                    )

                    session_info = SessionInfo(
                        status=SessionStatus.AUTHENTICATED,
                        auth_method=AuthMethod.CREDENTIALS,
                        user_id=user_info.get("user_id"),
                        username=username,
                        login_time=datetime.now(),
                        last_activity=datetime.now(),
                        cookies_count=len(cookies),
                        is_verified=user_info.get("is_verified", False),
                    )

                    logger.info(
                        f"Successfully authenticated with credentials as {username}"
                    )
                    self.login_attempts = 0  # Reset contador
                    return session_info
                else:
                    raise Exception(
                        "Credential authentication failed - login unsuccessful"
                    )

            finally:
                await page.close()

        except Exception as e:
            logger.error(f"Credential authentication failed: {e}")
            error_handler.record_error(e, {"method": "credentials"}, ErrorSeverity.HIGH)

            return SessionInfo(
                status=SessionStatus.NOT_AUTHENTICATED,
                auth_method=AuthMethod.CREDENTIALS,
            )

    async def _authenticate_auto(self, context: BrowserContext) -> SessionInfo:
        """Autenticación automática - prueba cookies primero, luego credenciales"""
        logger.info("Attempting auto authentication")

        # Primero intentar con cookies
        session_info = await self._authenticate_with_cookies(context)

        if session_info.status == SessionStatus.AUTHENTICATED:
            return session_info

        # Si fallan las cookies, intentar con credenciales
        logger.info("Cookie authentication failed, trying credentials")
        session_info = await self._authenticate_with_credentials(context)

        return session_info

    async def _verify_authentication(self, page: Page) -> bool:
        """Verifica si estamos autenticados en la página"""
        try:
            # Buscar elementos que indican que estamos logueados
            selectors_to_check = [
                WallapopSelectors.PROFILE_MENU[0],
                WallapopSelectors.NOTIFICATIONS_ICON[0],
                '[data-testid="user-menu"]',
                ".user-avatar",
                "#user-dropdown",
            ]

            for selector in selectors_to_check:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000)
                    if element:
                        logger.debug(
                            f"Authentication verified with selector: {selector}"
                        )
                        return True
                except Exception:
                    continue

            # Verificar URL también
            current_url = page.url
            if "/login" not in current_url and "/auth" not in current_url:
                # Si no estamos en página de login, probablemente estamos autenticados
                logger.debug("Authentication verified by URL")
                return True

            return False

        except Exception as e:
            logger.error(f"Error verifying authentication: {e}")
            return False

    async def _extract_user_info(self, page: Page) -> Dict[str, Any]:
        """Extrae información del usuario autenticado"""
        user_info = {}

        try:
            # Intentar extraer información del perfil
            username_selectors = [
                '[data-testid="username"]',
                ".username",
                ".user-name",
                "#user-name",
            ]

            for selector in username_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=3000)
                    username = await element.text_content()
                    if username:
                        user_info["username"] = username.strip()
                        break
                except Exception:
                    continue

            # Intentar extraer user ID del DOM o URLs
            try:
                user_id = await page.evaluate(
                    """
                    () => {
                        // Buscar user ID en diferentes lugares
                        const userLinks = document.querySelectorAll('a[href*="/user/"]');
                        if (userLinks.length > 0) {
                            const href = userLinks[0].href;
                            const match = href.match(/\\/user\\/([^/]+)/);
                            return match ? match[1] : null;
                        }

                        // Buscar en metadatos
                        const metaUserId = document.querySelector('meta[name="user-id"]');
                        return metaUserId ? metaUserId.content : null;
                    }
                """
                )

                if user_id:
                    user_info["user_id"] = user_id

            except Exception as e:
                logger.debug(f"Could not extract user ID: {e}")

            # Verificar si la cuenta está verificada
            try:
                verified_element = await page.query_selector(
                    '.verified, .verified-badge, [data-testid="verified"]'
                )
                user_info["is_verified"] = verified_element is not None
            except Exception:
                user_info["is_verified"] = False

        except Exception as e:
            logger.error(f"Error extracting user info: {e}")

        return user_info

    async def _fill_login_form(
        self, page: Page, username: str, password: str
    ):  # noqa: C901
        """Llena el formulario de login de forma humana"""
        logger.info("Filling login form")

        # Buscar campo de email/username
        email_element = None
        for selector in WallapopSelectors.EMAIL_INPUT:
            try:
                email_element = await page.wait_for_selector(selector, timeout=5000)
                if email_element:
                    break
            except Exception:
                continue

        if not email_element:
            raise Exception("Could not find email input field")

        # Llenar email con typing humano
        await anti_detection.human_like_typing(
            page, WallapopSelectors.EMAIL_INPUT[0], username
        )
        await asyncio.sleep(0.5)

        # Buscar campo de password
        password_element = None
        for selector in WallapopSelectors.PASSWORD_INPUT:
            try:
                password_element = await page.wait_for_selector(selector, timeout=5000)
                if password_element:
                    break
            except Exception:
                continue

        if not password_element:
            raise Exception("Could not find password input field")

        # Llenar password con typing humano
        await anti_detection.human_like_typing(
            page, WallapopSelectors.PASSWORD_INPUT[0], password
        )
        await asyncio.sleep(0.5)

        # Buscar y hacer click en botón de submit
        submit_element = None
        for selector in WallapopSelectors.LOGIN_SUBMIT:
            try:
                submit_element = await page.wait_for_selector(selector, timeout=5000)
                if submit_element:
                    break
            except Exception:
                continue

        if not submit_element:
            raise Exception("Could not find login submit button")

        # Click con movimento de mouse humano
        bbox = await submit_element.bounding_box()
        if bbox:
            center_x = bbox["x"] + bbox["width"] / 2
            center_y = bbox["y"] + bbox["height"] / 2
            await anti_detection.human_like_mouse_movement(page, center_x, center_y)

        await submit_element.click()
        logger.info("Login form submitted")

    def _can_attempt_login(self) -> bool:
        """Verifica si podemos intentar hacer login"""
        if self.login_attempts >= scraper_config.MAX_LOGIN_ATTEMPTS:
            if self.last_login_attempt:
                time_since_last = datetime.now() - self.last_login_attempt
                # Esperar 10 minutos después del último intento fallido
                if time_since_last < timedelta(minutes=10):
                    return False
                else:
                    # Reset contador después del timeout
                    self.login_attempts = 0
        return True

    def _is_session_valid(self) -> bool:
        """Verifica si la sesión actual sigue siendo válida"""
        if not self.current_session or not self.current_session.login_time:
            return False

        session_age = datetime.now() - self.current_session.login_time
        max_age = timedelta(hours=scraper_config.SESSION_TIMEOUT_HOURS)

        return session_age < max_age

    async def refresh_session(self, context: BrowserContext) -> SessionInfo:
        """Refresca la sesión actual"""
        logger.info("Refreshing session")

        # Guardar cookies actuales
        cookies = await context.cookies()
        self.cookie_manager.save_cookies(
            cookies,
            {
                "refreshed_at": datetime.now().isoformat(),
                "session_info": (
                    self.current_session.__dict__ if self.current_session else None
                ),
            },
        )

        # Actualizar tiempo de última actividad
        if self.current_session:
            self.current_session.last_activity = datetime.now()

        return self.current_session

    async def logout(self, context: BrowserContext):
        """Cierra sesión y limpia cookies"""
        logger.info("Logging out")

        try:
            # Crear página para hacer logout
            page = await context.new_page()

            try:
                # Navegar a página principal
                await page.goto(ScraperUrls.BASE_URL)
                await page.wait_for_load_state("networkidle")

                # Buscar y hacer click en logout
                logout_selectors = [
                    'button:has-text("Cerrar sesión")',
                    'a:has-text("Logout")',
                    '[data-testid="logout"]',
                    ".logout-button",
                ]

                for selector in logout_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=3000)
                        if element:
                            await element.click()
                            break
                    except Exception:
                        continue

            finally:
                await page.close()

        except Exception as e:
            logger.error(f"Error during logout: {e}")

        # Limpiar cookies y sesión
        self.cookie_manager.clear_cookies()
        self.current_session = None
        logger.info("Session cleared")

    def get_session_info(self) -> Optional[SessionInfo]:
        """Obtiene información de la sesión actual"""
        return self.current_session

    def get_session_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la sesión"""
        if not self.current_session:
            return {"status": "no_session"}

        stats = {
            "status": self.current_session.status.value,
            "auth_method": self.current_session.auth_method.value,
            "username": self.current_session.username,
            "login_attempts": self.login_attempts,
            "is_valid": self._is_session_valid(),
        }

        if self.current_session.login_time:
            stats["session_duration"] = str(
                datetime.now() - self.current_session.login_time
            )

        if self.current_session.last_activity:
            stats["time_since_activity"] = str(
                datetime.now() - self.current_session.last_activity
            )

        return stats
