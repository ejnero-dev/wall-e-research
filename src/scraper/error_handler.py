"""
Sistema robusto de manejo de errores con circuit breaker, retry y alertas
"""

import asyncio
import time
import logging
import json
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Type
from dataclasses import dataclass, field
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
from functools import wraps
import traceback

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Niveles de severidad de errores"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CircuitBreakerState(Enum):
    """Estados del circuit breaker"""

    CLOSED = "closed"  # Funcionando normalmente
    OPEN = "open"  # Bloqueado por errores
    HALF_OPEN = "half_open"  # Probando recuperación


@dataclass
class ErrorRecord:
    """Registro de error individual"""

    timestamp: datetime
    error_type: str
    message: str
    severity: ErrorSeverity
    context: Dict[str, Any] = field(default_factory=dict)
    traceback: Optional[str] = None
    retry_count: int = 0


@dataclass
class CircuitBreakerConfig:
    """Configuración del circuit breaker"""

    failure_threshold: int = 5  # Fallos antes de abrir
    timeout_seconds: int = 300  # Tiempo abierto (5 min)
    success_threshold: int = 3  # Éxitos para cerrar desde half-open
    monitoring_window: int = 600  # Ventana de monitoreo (10 min)


class CircuitBreaker:
    """Implementación de circuit breaker pattern"""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state_changed_time = datetime.now()

    def can_execute(self) -> bool:
        """Determina si se puede ejecutar una operación"""
        current_time = datetime.now()

        if self.state == CircuitBreakerState.CLOSED:
            return True

        elif self.state == CircuitBreakerState.OPEN:
            # Verificar si es hora de pasar a HALF_OPEN
            if (
                current_time - self.state_changed_time
            ).total_seconds() >= self.config.timeout_seconds:
                self._transition_to_half_open()
                return True
            return False

        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True

        return False

    def record_success(self):
        """Registra una operación exitosa"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0  # Reset contador de fallos

    def record_failure(self):
        """Registra una operación fallida"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self._transition_to_open()
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self._transition_to_open()

    def _transition_to_open(self):
        """Transición a estado OPEN"""
        self.state = CircuitBreakerState.OPEN
        self.state_changed_time = datetime.now()
        self.success_count = 0
        logger.warning(
            f"Circuit breaker '{self.name}' opened after {self.failure_count} failures"
        )

    def _transition_to_half_open(self):
        """Transición a estado HALF_OPEN"""
        self.state = CircuitBreakerState.HALF_OPEN
        self.state_changed_time = datetime.now()
        self.success_count = 0
        logger.info(f"Circuit breaker '{self.name}' transitioned to half-open")

    def _transition_to_closed(self):
        """Transición a estado CLOSED"""
        self.state = CircuitBreakerState.CLOSED
        self.state_changed_time = datetime.now()
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"Circuit breaker '{self.name}' closed after successful recovery")

    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del circuit breaker"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": (
                self.last_failure_time.isoformat() if self.last_failure_time else None
            ),
            "state_changed_time": self.state_changed_time.isoformat(),
        }


class RetryConfig:
    """Configuración para retry con backoff exponencial"""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calcula el delay para un intento específico"""
        import random

        delay = self.base_delay * (self.backoff_factor**attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Añadir jitter para evitar thundering herd
            delay *= 0.5 + random.random() * 0.5

        return delay


class AlertManager:
    """Gestor de alertas por email y Slack"""

    def __init__(
        self,
        slack_webhook_url: Optional[str] = None,
        email_config: Optional[Dict[str, Any]] = None,
    ):
        self.slack_webhook_url = slack_webhook_url
        self.email_config = email_config or {}
        self.alert_history: List[Dict] = []
        self.rate_limit_cache: Dict[str, datetime] = {}

    async def send_alert(
        self,
        title: str,
        message: str,
        severity: ErrorSeverity,
        context: Optional[Dict] = None,
    ):
        """Envía alerta por múltiples canales"""

        # Rate limiting - no más de 1 alerta del mismo tipo por 5 minutos
        alert_key = f"{title}_{severity.value}"
        current_time = datetime.now()

        if alert_key in self.rate_limit_cache:
            last_sent = self.rate_limit_cache[alert_key]
            if (current_time - last_sent).total_seconds() < 300:  # 5 minutos
                logger.debug(f"Alert rate limited: {alert_key}")
                return

        self.rate_limit_cache[alert_key] = current_time

        # Registrar en historial
        alert_record = {
            "timestamp": current_time.isoformat(),
            "title": title,
            "message": message,
            "severity": severity.value,
            "context": context or {},
        }
        self.alert_history.append(alert_record)

        # Mantener solo últimas 100 alertas
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]

        # Enviar por Slack si está configurado
        if self.slack_webhook_url and severity in [
            ErrorSeverity.HIGH,
            ErrorSeverity.CRITICAL,
        ]:
            await self._send_slack_alert(title, message, severity, context)

        # Enviar por email si está configurado
        if self.email_config and severity == ErrorSeverity.CRITICAL:
            await self._send_email_alert(title, message, severity, context)

        logger.error(f"ALERT [{severity.value.upper()}] {title}: {message}")

    async def _send_slack_alert(
        self, title: str, message: str, severity: ErrorSeverity, context: Optional[Dict]
    ):
        """Envía alerta a Slack"""
        try:
            color_map = {
                ErrorSeverity.LOW: "#36a64f",
                ErrorSeverity.MEDIUM: "#ff9900",
                ErrorSeverity.HIGH: "#ff6600",
                ErrorSeverity.CRITICAL: "#cc0000",
            }

            payload = {
                "attachments": [
                    {
                        "color": color_map.get(severity, "#cc0000"),
                        "title": f"🚨 Wallapop Scraper Alert - {title}",
                        "text": message,
                        "fields": [
                            {
                                "title": "Severity",
                                "value": severity.value.upper(),
                                "short": True,
                            },
                            {
                                "title": "Timestamp",
                                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True,
                            },
                        ],
                        "footer": "Wallapop Scraper",
                        "ts": int(time.time()),
                    }
                ]
            }

            if context:
                payload["attachments"][0]["fields"].append(
                    {
                        "title": "Context",
                        "value": json.dumps(context, indent=2),
                        "short": False,
                    }
                )

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.slack_webhook_url, json=payload
                ) as response:
                    if response.status == 200:
                        logger.info("Slack alert sent successfully")
                    else:
                        logger.error(f"Failed to send Slack alert: {response.status}")

        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")

    async def _send_email_alert(
        self, title: str, message: str, severity: ErrorSeverity, context: Optional[Dict]
    ):
        """Envía alerta por email"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_config.get("from_address", "")
            msg["To"] = self.email_config.get("to_address", "")
            msg["Subject"] = f"🚨 CRITICAL ALERT - Wallapop Scraper - {title}"

            body = f"""
            CRITICAL ALERT - Wallapop Scraper

            Title: {title}
            Severity: {severity.value.upper()}
            Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            Message:
            {message}

            Context:
            {json.dumps(context, indent=2) if context else 'No additional context'}

            Please investigate immediately.
            """

            msg.attach(MIMEText(body, "plain"))

            # Enviar usando asyncio para no bloquear
            await asyncio.get_event_loop().run_in_executor(
                None, self._send_email_sync, msg
            )

        except Exception as e:
            logger.error(f"Error sending email alert: {e}")

    def _send_email_sync(self, msg):
        """Envía email de forma síncrona"""
        try:
            server = smtplib.SMTP(
                self.email_config.get("smtp_host", "localhost"),
                self.email_config.get("smtp_port", 587),
            )

            if self.email_config.get("smtp_tls", True):
                server.starttls()

            if self.email_config.get("smtp_username"):
                server.login(
                    self.email_config["smtp_username"],
                    self.email_config["smtp_password"],
                )

            server.send_message(msg)
            server.quit()
            logger.info("Email alert sent successfully")

        except Exception as e:
            logger.error(f"Error in email sending: {e}")


class ErrorHandler:
    """Manejador centralizado de errores"""

    def __init__(self, alert_manager: Optional[AlertManager] = None):
        self.alert_manager = alert_manager
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_history: List[ErrorRecord] = []
        self.retry_configs: Dict[str, RetryConfig] = {}

        # Configuraciones por defecto
        self.setup_default_configs()

    def setup_default_configs(self):
        """Configura circuit breakers y retry por defecto"""

        # Circuit breakers para diferentes operaciones
        self.add_circuit_breaker(
            "login",
            CircuitBreakerConfig(
                failure_threshold=3,
                timeout_seconds=600,  # 10 minutos para login
                success_threshold=2,
            ),
        )

        self.add_circuit_breaker(
            "message_send",
            CircuitBreakerConfig(
                failure_threshold=5,
                timeout_seconds=300,  # 5 minutos para mensajes
                success_threshold=3,
            ),
        )

        self.add_circuit_breaker(
            "page_load",
            CircuitBreakerConfig(
                failure_threshold=10,
                timeout_seconds=120,  # 2 minutos para carga de páginas
                success_threshold=5,
            ),
        )

        # Configuraciones de retry
        self.retry_configs["login"] = RetryConfig(
            max_attempts=3, base_delay=5.0, max_delay=30.0
        )

        self.retry_configs["message_send"] = RetryConfig(
            max_attempts=5, base_delay=2.0, max_delay=15.0
        )

        self.retry_configs["page_load"] = RetryConfig(
            max_attempts=3, base_delay=1.0, max_delay=10.0
        )

    def add_circuit_breaker(self, name: str, config: CircuitBreakerConfig):
        """Añade un circuit breaker"""
        self.circuit_breakers[name] = CircuitBreaker(name, config)

    def record_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    ):
        """Registra un error en el sistema"""

        error_record = ErrorRecord(
            timestamp=datetime.now(),
            error_type=type(error).__name__,
            message=str(error),
            severity=severity,
            context=context,
            traceback=traceback.format_exc(),
        )

        self.error_history.append(error_record)

        # Mantener solo últimos 500 errores
        if len(self.error_history) > 500:
            self.error_history = self.error_history[-500:]

        # Enviar alerta si es necesario
        if self.alert_manager and severity in [
            ErrorSeverity.HIGH,
            ErrorSeverity.CRITICAL,
        ]:
            asyncio.create_task(
                self.alert_manager.send_alert(
                    title=f"{error_record.error_type} Error",
                    message=error_record.message,
                    severity=severity,
                    context=context,
                )
            )

        logger.error(
            f"Error recorded: {error_record.error_type} - {error_record.message}"
        )

    def with_circuit_breaker(self, breaker_name: str):
        """Decorator para aplicar circuit breaker a una función"""

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                breaker = self.circuit_breakers.get(breaker_name)
                if not breaker:
                    logger.warning(f"Circuit breaker '{breaker_name}' not found")
                    return await func(*args, **kwargs)

                if not breaker.can_execute():
                    raise Exception(f"Circuit breaker '{breaker_name}' is open")

                try:
                    result = await func(*args, **kwargs)
                    breaker.record_success()
                    return result
                except Exception:
                    breaker.record_failure()
                    raise

            return wrapper

        return decorator

    def with_retry(self, operation_name: str = "default"):
        """Decorator para aplicar retry con backoff exponencial"""

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                retry_config = self.retry_configs.get(operation_name, RetryConfig())
                last_exception = None

                for attempt in range(retry_config.max_attempts):
                    try:
                        result = await func(*args, **kwargs)

                        # Si llegamos aquí, la operación fue exitosa
                        if attempt > 0:
                            logger.info(f"Operation succeeded on attempt {attempt + 1}")

                        return result

                    except Exception as e:
                        last_exception = e

                        if attempt < retry_config.max_attempts - 1:
                            delay = retry_config.get_delay(attempt)
                            logger.warning(
                                f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}"
                            )
                            await asyncio.sleep(delay)
                        else:
                            logger.error(
                                f"All {retry_config.max_attempts} attempts failed"
                            )

                # Si llegamos aquí, todos los intentos fallaron
                self.record_error(
                    last_exception,
                    {
                        "operation": operation_name,
                        "attempts": retry_config.max_attempts,
                    },
                    ErrorSeverity.HIGH,
                )
                raise last_exception

            return wrapper

        return decorator

    def get_error_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de errores"""
        if not self.error_history:
            return {"total_errors": 0}

        # Contar errores por tipo
        error_types = {}
        severity_counts = {}
        recent_errors = []

        cutoff_time = datetime.now() - timedelta(hours=24)

        for error in self.error_history:
            # Contar por tipo
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1

            # Contar por severidad
            severity_counts[error.severity.value] = (
                severity_counts.get(error.severity.value, 0) + 1
            )

            # Errores recientes (últimas 24h)
            if error.timestamp >= cutoff_time:
                recent_errors.append(
                    {
                        "timestamp": error.timestamp.isoformat(),
                        "type": error.error_type,
                        "message": error.message,
                        "severity": error.severity.value,
                    }
                )

        return {
            "total_errors": len(self.error_history),
            "error_types": error_types,
            "severity_counts": severity_counts,
            "recent_errors_24h": len(recent_errors),
            "recent_errors": recent_errors[-10:],  # Últimos 10
            "circuit_breakers": {
                name: breaker.get_status()
                for name, breaker in self.circuit_breakers.items()
            },
        }

    async def health_check(self) -> Dict[str, Any]:
        """Realiza un health check del sistema"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "circuit_breakers": {},
            "error_rate_24h": 0,
            "critical_errors_24h": 0,
        }

        # Verificar circuit breakers
        all_breakers_healthy = True
        for name, breaker in self.circuit_breakers.items():
            breaker_status = breaker.get_status()
            health_status["circuit_breakers"][name] = breaker_status

            if breaker_status["state"] == "open":
                all_breakers_healthy = False

        # Calcular tasa de errores en 24h
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_errors = [e for e in self.error_history if e.timestamp >= cutoff_time]
        critical_errors = [
            e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL
        ]

        health_status["error_rate_24h"] = len(recent_errors)
        health_status["critical_errors_24h"] = len(critical_errors)

        # Determinar estado general
        if len(critical_errors) > 0:
            health_status["status"] = "critical"
        elif not all_breakers_healthy or len(recent_errors) > 50:
            health_status["status"] = "degraded"
        elif len(recent_errors) > 20:
            health_status["status"] = "warning"

        return health_status


# Instancia global del manejador de errores
error_handler = ErrorHandler()
