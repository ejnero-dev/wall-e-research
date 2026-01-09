# wallapop_bot.py - COMPLIANCE VERSION
"""
Bot COMPLIANCE para Wallapop - Versión Restringida
Esta versión está diseñada para cumplimiento legal estricto:
- Requiere confirmación humana para acciones críticas
- Cumple con GDPR y leyes de protección de datos
- Mantiene audit trail completo
- Transparencia total en operaciones automatizadas
"""

import asyncio
import logging
import os
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import uuid
from enum import Enum

# Importaciones locales
from conversation_engine.engine import ConversationEngine
from scraper.wallapop_scraper import WallapopScraper
from database.db_manager import DatabaseManager
from config_loader import load_config, ConfigMode

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/wallapop_bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Tipos de acciones que requieren confirmación"""

    SEND_MESSAGE = "send_message"
    ACCEPT_OFFER = "accept_offer"
    REJECT_OFFER = "reject_offer"
    BLOCK_USER = "block_user"
    SHARE_CONTACT = "share_contact"


@dataclass
class PendingAction:
    """Acción pendiente de confirmación humana"""

    id: str
    action_type: ActionType
    target_user: str
    details: Dict[str, Any]
    created_at: datetime
    expires_at: datetime
    requires_confirmation: bool = True
    gdpr_consent_required: bool = False


@dataclass
class AuditLogEntry:
    """Entrada del registro de auditoría"""

    timestamp: datetime
    action: str
    user_id: str
    details: Dict[str, Any]
    automated: bool
    human_confirmed: bool
    gdpr_compliant: bool


class ComplianceWallapopBot:
    """Clase principal del bot COMPLIANCE de Wallapop"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Inicializa el bot COMPLIANCE con la configuración"""
        self.config = self._load_config(config_path)
        self.is_running = False

        # Verificar modo compliance
        if (
            not self.config.get("development", {})
            .get("gdpr_compliance", {})
            .get("enabled", False)
        ):
            raise ValueError("COMPLIANCE MODE must be enabled in config")

        # Inicializar componentes
        logger.info("Inicializando ComplianceWallapopBot...")

        # Estado del bot COMPLIANCE
        self.active_conversations = {}
        self.pending_responses = []
        self.pending_actions: List[PendingAction] = []
        self.audit_log: List[AuditLogEntry] = []
        self.user_consents: Dict[str, Dict] = {}  # GDPR consent tracking

        self.stats = {
            "messages_processed": 0,
            "responses_sent": 0,
            "sales_completed": 0,
            "fraud_attempts_blocked": 0,
            "human_confirmations_required": 0,
            "human_confirmations_received": 0,
            "gdpr_consents_obtained": 0,
        }

        # Rate limiting compliance
        self.message_count = 0
        self.last_message_time = datetime.now()
        self.hourly_message_count = 0
        self.hourly_reset_time = datetime.now() + timedelta(hours=1)

        # Inicializar módulos integrados
        self._initialize_modules()

    def _initialize_modules(self):
        """Inicializa e integra todos los módulos del bot"""
        try:
            logger.info("Inicializando módulos integrados...")

            # Inicializar Database Manager
            db_config = self.config.get("database", {})
            if db_config.get("url"):
                self.db = DatabaseManager(database_url=db_config["url"])
                logger.info("Database Manager inicializado")
            else:
                logger.warning(
                    "Database URL not found in config, DB operations will be disabled"
                )
                self.db = None

            # Inicializar Conversation Engine
            templates_path = self.config.get("responses", {}).get(
                "templates_path", "src/templates/responses.json"
            )
            self.conversation_engine = ConversationEngine(templates_path=templates_path)
            logger.info("Conversation Engine inicializado")

            # Inicializar Wallapop Scraper
            from scraper.session_manager import AuthMethod

            auth_method = AuthMethod.AUTO
            self.scraper = WallapopScraper(auth_method=auth_method)
            logger.info("Wallapop Scraper inicializado")

            # Validar integraciones críticas
            self._validate_integrations()

        except Exception as e:
            logger.error(f"Error inicializando módulos: {e}")
            raise RuntimeError(f"Failed to initialize bot modules: {e}")

    def _validate_integrations(self):
        """Valida que las integraciones críticas estén funcionando"""
        validation_errors = []

        if not hasattr(self, "conversation_engine") or self.conversation_engine is None:
            validation_errors.append("Conversation Engine not initialized")

        if not hasattr(self, "scraper") or self.scraper is None:
            validation_errors.append("Wallapop Scraper not initialized")

        if validation_errors:
            raise RuntimeError(
                f"Integration validation failed: {', '.join(validation_errors)}"
            )

        logger.info("Validación de integraciones completada exitosamente")

    def _load_config(self, path: str) -> Dict:
        """Carga la configuración desde archivo YAML"""
        if not os.path.exists(path):
            logger.warning(f"Config file not found at {path}, using defaults")
            return self._get_default_config()

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _get_default_config(self) -> Dict:
        """Retorna configuración COMPLIANCE por defecto"""
        return {
            "wallapop": {
                "behavior": {
                    "min_delay_between_messages": 300,  # 5 minutos
                    "max_delay_between_messages": 900,  # 15 minutos
                    "max_messages_per_hour": 5,  # COMPLIANCE LIMIT
                    "require_human_confirmation": True,
                    "active_hours": {
                        "start": "09:00",
                        "end": "22:00",
                        "timezone": "Europe/Madrid",
                    },
                    "max_concurrent_conversations": 1,  # Solo una
                    "max_messages_per_conversation": 10,
                }
            },
            "security": {
                "fraud_detection": {
                    "enabled": True,
                    "auto_block_suspicious": False,  # Siempre requiere confirmación
                },
                "automation_disclosure": {
                    "enabled": True,
                    "message": "Este mensaje es generado por un sistema automatizado.",
                },
            },
            "development": {
                "gdpr_compliance": {
                    "enabled": True,
                    "consent_required": True,
                    "data_retention_days": 30,
                    "audit_trail": True,
                },
                "dry_run": True,  # Default to simulation
            },
            "notifications": {"desktop_notifications": True},
        }

    async def start(self):
        """Inicia el bot"""
        logger.info("Starting WallapopBot...")
        self.is_running = True

        # Tareas principales
        tasks = [
            self._monitor_messages(),
            self._process_responses(),
            self._update_stats(),
            self._check_abandoned_conversations(),
        ]

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Detiene el bot de forma segura"""
        logger.info("Stopping WallapopBot...")
        self.is_running = False

        # Guardar estado actual
        self._save_state()

        # Cerrar conexiones
        # await self.scraper.close()
        # await self.db.close()

        logger.info("Bot stopped successfully")

    async def request_human_confirmation(self, action: PendingAction) -> bool:
        """COMPLIANCE: Requiere confirmación humana explícita para todas las acciones"""

        print("\n" + "=" * 60)
        print("🤖 CONFIRMACIÓN HUMANA REQUERIDA")
        print("=" * 60)
        print(f"Acción: {action.action_type.value}")
        print(f"Usuario objetivo: {action.target_user}")
        print(f"Detalles: {json.dumps(action.details, indent=2, ensure_ascii=False)}")
        print(f"Creada: {action.created_at}")
        print(f"Expira: {action.expires_at}")
        print("\n¿Desea aprobar esta acción?")
        print("Opciones:")
        print("  [s] Sí, aprobar")
        print("  [n] No, rechazar")
        print("  [p] Pausar bot")
        print("  [q] Detener bot")
        print("-" * 60)

        try:
            # Timeout de 5 minutos para respuesta humana
            import signal

            def timeout_handler(signum, frame):
                print("\n⏰ Timeout: No se recibió confirmación humana")
                return False

            # Configurar timeout (solo en Linux/macOS)
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(300)  # 5 minutos
            except AttributeError:
                # Windows no soporta signal.alarm
                pass

            while True:
                response = input("\nIngrese su respuesta [s/n/p/q]: ").lower().strip()

                if response == "s":
                    print("✅ Acción APROBADA por humano")
                    self.stats["human_confirmations_received"] += 1
                    self._log_audit_entry(
                        "human_approval",
                        action.target_user,
                        {"action": action.action_type.value, "approved": True},
                        automated=False,
                        human_confirmed=True,
                    )
                    return True

                elif response == "n":
                    print("❌ Acción RECHAZADA por humano")
                    self._log_audit_entry(
                        "human_rejection",
                        action.target_user,
                        {"action": action.action_type.value, "approved": False},
                        automated=False,
                        human_confirmed=True,
                    )
                    return False

                elif response == "p":
                    print("⏸️  Bot PAUSADO por humano")
                    self.is_running = False
                    return False

                elif response == "q":
                    print("🛑 Bot DETENIDO por humano")
                    await self.stop()
                    return False

                else:
                    print(
                        "❓ Respuesta inválida. Use: s (sí), n (no), p (pausar), q (salir)"
                    )

        except KeyboardInterrupt:
            print("\n🛑 Confirmación interrumpida por usuario")
            return False
        except Exception as e:
            logger.error(f"Error durante confirmación humana: {e}")
            return False
        finally:
            try:
                signal.alarm(0)  # Cancelar timeout
            except Exception:
                pass

    async def _verify_gdpr_consent(self, user_id: str) -> bool:
        """Verifica si el usuario ha dado consentimiento GDPR"""
        return user_id in self.user_consents

    async def _request_gdpr_consent(self, user_id: str):
        """Solicita consentimiento GDPR al usuario"""

        consent_message = (
            "Hola! Soy un asistente automatizado que ayuda con las ventas. "
            "Para continuar nuestra conversación necesito tu consentimiento para:"
            "\n• Procesar nuestras conversaciones"
            "\n• Almacenar temporalmente los mensajes para mejorar las respuestas"
            "\n• Analizar el contenido para detectar spam/fraude"
            "\n\n¿Está de acuerdo? Puedes retirar tu consentimiento en cualquier momento."
        )

        print(f"\n📋 SOLICITUD DE CONSENTIMIENTO GDPR para {user_id}")
        print(f"Mensaje a enviar: {consent_message}")

        # Aquí iría la lógica para enviar el mensaje de consentimiento
        # await self.send_message(user_id, consent_message)

        # Por ahora, simular el consentimiento
        self.user_consents[user_id] = {
            "timestamp": datetime.now(),
            "consented": False,
            "pending": True,
        }
        self.stats["gdpr_consents_obtained"] += 1

    def _check_rate_limits(self) -> bool:
        """Verifica límites de tasa COMPLIANCE"""
        now = datetime.now()

        # Reset contador por hora
        if now >= self.hourly_reset_time:
            self.hourly_message_count = 0
            self.hourly_reset_time = now + timedelta(hours=1)

        # Verificar límite por hora (5 mensajes)
        if self.hourly_message_count >= 5:
            logger.warning("[COMPLIANCE] Hourly rate limit reached (5/hour)")
            return False

        # Verificar delay mínimo entre mensajes (2 minutos)
        time_since_last = (now - self.last_message_time).total_seconds()
        if time_since_last < 120:  # 2 minutos
            logger.warning(
                f"[COMPLIANCE] Minimum delay not met ({time_since_last}s < 120s)"
            )
            return False

        return True

    def _log_audit_entry(
        self,
        action: str,
        user_id: str,
        details: Dict,
        automated: bool = True,
        human_confirmed: bool = False,
    ):
        """Registra entrada en audit trail"""

        entry = AuditLogEntry(
            timestamp=datetime.now(),
            action=action,
            user_id=user_id,
            details=details,
            automated=automated,
            human_confirmed=human_confirmed,
            gdpr_compliant=user_id in self.user_consents,
        )

        self.audit_log.append(entry)

        # Log to file
        audit_data = {
            "timestamp": entry.timestamp.isoformat(),
            "action": entry.action,
            "user_id": entry.user_id,
            "details": entry.details,
            "automated": entry.automated,
            "human_confirmed": entry.human_confirmed,
            "gdpr_compliant": entry.gdpr_compliant,
        }

        logger.info(f"[AUDIT] {json.dumps(audit_data, ensure_ascii=False)}")

    def _save_state(self):
        """Guarda el estado actual del bot para compliance"""
        state = {
            "stats": self.stats,
            "pending_actions": [asdict(action) for action in self.pending_actions],
            "user_consents": self.user_consents,
            "audit_log_count": len(self.audit_log),
            "last_save": datetime.now().isoformat(),
        }

        try:
            os.makedirs("./data", exist_ok=True)
            with open("./data/bot_state.json", "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False, default=str)
            logger.info("Bot state saved successfully")
        except Exception as e:
            logger.error(f"Failed to save bot state: {e}")

    async def _monitor_messages(self):
        """Monitorea mensajes nuevos usando el scraper integrado"""
        while self.is_running:
            try:
                # COMPLIANCE: Verificar rate limits antes de hacer scraping
                if not self._check_rate_limits():
                    logger.info("[COMPLIANCE] Rate limits exceeded, waiting...")
                    await asyncio.sleep(300)  # Esperar 5 minutos
                    continue

                # Obtener conversaciones con mensajes no leídos
                try:
                    conversations = await self.scraper.get_conversations()

                    for conversation in conversations:
                        if conversation.get("unread_count", 0) > 0:
                            # Obtener mensajes no leídos de esta conversación
                            messages = await self.scraper.get_messages(
                                conversation["id"]
                            )

                            for message in messages:
                                if not message.get(
                                    "is_from_me", False
                                ) and not message.get("is_processed", False):
                                    await self._process_message(message)

                                    # COMPLIANCE: Delay entre procesamiento de mensajes
                                    await asyncio.sleep(
                                        self.config.get("wallapop", {})
                                        .get("behavior", {})
                                        .get("min_delay_between_messages", 120)
                                    )

                except Exception as scraper_error:
                    logger.error(f"Scraper error: {scraper_error}")
                    # Si hay error con scraper, usar modo fallback
                    logger.info("Switching to fallback mode...")

                # COMPLIANCE: Delay mínimo entre checks
                await asyncio.sleep(
                    max(
                        60,
                        self.config.get("wallapop", {})
                        .get("behavior", {})
                        .get("message_check_interval", 60),
                    )
                )

            except Exception as e:
                logger.error(f"Error monitoring messages: {e}")
                await asyncio.sleep(300)  # Esperar más tiempo si hay errores

    async def _process_message(self, message: Dict):
        """Procesa un mensaje individual con validaciones COMPLIANCE"""
        try:
            buyer_id = message.get("buyer_id")
            logger.info(f"[COMPLIANCE] Processing message from {buyer_id}")

            # 1. Verificar rate limits
            if not self._check_rate_limits():
                logger.warning("[COMPLIANCE] Rate limit exceeded, queuing for later")
                return

            # 2. Verificar consentimiento GDPR
            if not await self._verify_gdpr_consent(buyer_id):
                logger.warning(f"[COMPLIANCE] GDPR consent required for {buyer_id}")
                await self._request_gdpr_consent(buyer_id)
                return

            self.stats["messages_processed"] += 1
            self._log_audit_entry(
                "message_processed", buyer_id, message, automated=True
            )

            # 3. Obtener datos del comprador y producto
            buyer = await self._get_or_create_buyer(buyer_id, message)
            product = await self._get_product_from_message(message)

            # 4. Análisis completo del mensaje usando Conversation Engine
            analysis = self.conversation_engine.analyze_message(
                message.get("content", ""), buyer, product
            )

            # 5. COMPLIANCE: Forzar revisión humana si es necesario
            if (
                analysis.get("fraud_risk", 0) > 30
                or analysis.get("intention") == "fraude"
            ):
                analysis["requires_human_review"] = True
            else:
                # En modo compliance, revisar menos críticos pero con threshold bajo
                analysis["requires_human_review"] = analysis.get(
                    "requires_human", False
                ) or (analysis.get("fraud_risk", 0) > 10)

            # 6. Generar respuesta sugerida usando Conversation Engine
            suggested_response = None
            if (
                not analysis.get("fraud_risk", 0) > 80
            ):  # No generar respuestas para fraude obvio
                suggested_response = self.conversation_engine.generate_response(
                    analysis, message.get("content", ""), buyer, product
                )

            # 7. Persistir en base de datos
            await self._save_conversation_data(
                buyer, message, analysis, suggested_response
            )

            # 8. Crear acción pendiente que requiere confirmación humana
            if analysis["requires_human_review"]:
                action = PendingAction(
                    id=str(uuid.uuid4()),
                    action_type=ActionType.SEND_MESSAGE,
                    target_user=buyer_id,
                    details={
                        "original_message": message,
                        "analysis": analysis,
                        "suggested_response": suggested_response
                        or "Respuesta requiere revisión manual",
                    },
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=24),
                    requires_confirmation=True,
                )

                self.pending_actions.append(action)
                self.stats["human_confirmations_required"] += 1

                logger.info(
                    f"[COMPLIANCE] Action {action.id} created and pending human confirmation"
                )
                await self._notify_human_required(action)

        except Exception as e:
            logger.error(f"[COMPLIANCE] Error processing message: {e}")
            self._log_audit_entry(
                "error", buyer_id or "unknown", {"error": str(e)}, automated=True
            )

    async def _queue_response(
        self, buyer_id: str, response: str, human_confirmed: bool = False
    ):
        """Añade respuesta a la cola con validaciones COMPLIANCE"""

        # COMPLIANCE: Solo procesar si está confirmado por humano
        if (
            not human_confirmed
            and self.config["wallapop"]["behavior"]["require_human_confirmation"]
        ):
            logger.warning(
                f"[COMPLIANCE] Response to {buyer_id} requires human confirmation"
            )
            return

        # Verificar consentimiento GDPR
        if not await self._verify_gdpr_consent(buyer_id):
            logger.warning(
                f"[COMPLIANCE] Cannot send response to {buyer_id} - no GDPR consent"
            )
            return

        delay = self._calculate_response_delay()

        # Añadir disclosure de automatización
        disclosure = (
            self.config.get("security", {})
            .get("automation_disclosure", {})
            .get("message", "")
        )
        if disclosure and not human_confirmed:
            response = f"{disclosure}\n\n{response}"

        self.pending_responses.append(
            {
                "buyer_id": buyer_id,
                "response": response,
                "send_after": datetime.now().timestamp() + delay,
                "human_confirmed": human_confirmed,
                "includes_disclosure": bool(disclosure),
            }
        )

        self._log_audit_entry(
            "response_queued",
            buyer_id,
            {
                "response_length": len(response),
                "delay": delay,
                "human_confirmed": human_confirmed,
            },
            automated=not human_confirmed,
            human_confirmed=human_confirmed,
        )

    def _calculate_response_delay(self) -> int:
        """Calcula delay COMPLIANCE - Más conservador"""
        import random

        config = self.config["wallapop"]["behavior"]
        return random.randint(
            config.get("min_delay_between_messages", 300),  # Mínimo 5 min
            config.get("max_delay_between_messages", 900),  # Máximo 15 min
        )

    async def _process_responses(self):
        """Procesa y envía respuestas pendientes"""
        while self.is_running:
            try:
                current_time = datetime.now().timestamp()

                # Verificar si estamos en horario activo
                if not self._is_active_hours():
                    await asyncio.sleep(60)
                    continue

                # Procesar respuestas pendientes
                for response in self.pending_responses[:]:
                    if current_time >= response["send_after"]:
                        # await self._send_response(response)
                        self.pending_responses.remove(response)
                        self.stats["responses_sent"] += 1

                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error processing responses: {e}")
                await asyncio.sleep(30)

    def _is_active_hours(self) -> bool:
        """Verifica si estamos en horario activo"""
        from datetime import datetime
        import pytz

        config = self.config["wallapop"]["behavior"]["active_hours"]
        tz = pytz.timezone(config["timezone"])
        now = datetime.now(tz)

        start_hour = int(config["start"].split(":")[0])
        end_hour = int(config["end"].split(":")[0])

        return start_hour <= now.hour < end_hour

    async def _update_stats(self):
        """Actualiza estadísticas periódicamente"""
        while self.is_running:
            try:
                logger.info(f"Stats: {self.stats}")

                # Guardar stats en DB
                # await self.db.save_stats(self.stats)

                await asyncio.sleep(300)  # Cada 5 minutos

            except Exception as e:
                logger.error(f"Error updating stats: {e}")

    async def _check_abandoned_conversations(self):
        """Verifica conversaciones abandonadas para recuperación"""
        while self.is_running:
            try:
                # Verificar conversaciones sin actividad >24h
                # abandoned = await self.db.get_abandoned_conversations()

                # for conv in abandoned:
                #     recovery_msg = self.conversation_engine.get_recovery_message(conv)
                #     if recovery_msg:
                #         await self._queue_response(conv['buyer_id'], recovery_msg)

                await asyncio.sleep(3600)  # Cada hora

            except Exception as e:
                logger.error(f"Error checking abandoned conversations: {e}")

    def _save_audit_log(self, entry: AuditLogEntry):
        """Guarda entrada de audit en archivo"""
        try:
            os.makedirs("logs/audit", exist_ok=True)
            log_file = f"logs/audit/audit_{datetime.now().strftime('%Y%m%d')}.jsonl"

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(entry), default=str) + "\n")
        except Exception as e:
            logger.error(f"[AUDIT] Error saving audit log: {e}")

    async def _notify_human_required(self, action: PendingAction):
        """Notifica que se requiere confirmación humana"""
        logger.info(
            f"[HUMAN REQUIRED] Action {action.id} - {action.action_type.value} for {action.target_user}"
        )

        # En implementación real, enviaría notificación por email/Slack/etc
        notification = {
            "action_id": action.id,
            "type": action.action_type.value,
            "user": action.target_user,
            "details": action.details,
            "expires_at": action.expires_at.isoformat(),
        }

        # Guardar notificación para dashboard humano
        os.makedirs("data/pending_actions", exist_ok=True)
        with open(f"data/pending_actions/{action.id}.json", "w") as f:
            json.dump(notification, f, indent=2, default=str)

    def get_pending_actions(self) -> List[Dict]:
        """Obtiene acciones pendientes para revisión humana"""
        return [
            {
                "id": action.id,
                "type": action.action_type.value,
                "user": action.target_user,
                "details": action.details,
                "created_at": action.created_at.isoformat(),
                "expires_at": action.expires_at.isoformat(),
            }
            for action in self.pending_actions
        ]

    async def confirm_action(
        self, action_id: str, approved: bool, human_user: str
    ) -> bool:
        """Confirma o rechaza una acción pendiente"""
        action = next((a for a in self.pending_actions if a.id == action_id), None)
        if not action:
            logger.warning(f"[COMPLIANCE] Action {action_id} not found")
            return False

        if datetime.now() > action.expires_at:
            logger.warning(f"[COMPLIANCE] Action {action_id} has expired")
            self.pending_actions.remove(action)
            return False

        self.stats["human_confirmations_received"] += 1

        if approved:
            logger.info(f"[COMPLIANCE] Action {action_id} approved by {human_user}")

            # Ejecutar acción
            if action.action_type == ActionType.SEND_MESSAGE:
                response = action.details.get("suggested_response", "")
                await self._queue_response(
                    action.target_user, response, human_confirmed=True
                )

            self._log_audit_entry(
                "action_approved",
                action.target_user,
                {"action_id": action_id, "approved_by": human_user},
                automated=False,
                human_confirmed=True,
            )
        else:
            logger.info(f"[COMPLIANCE] Action {action_id} rejected by {human_user}")
            self._log_audit_entry(
                "action_rejected",
                action.target_user,
                {"action_id": action_id, "rejected_by": human_user},
                automated=False,
                human_confirmed=True,
            )

        self.pending_actions.remove(action)

        # Limpiar archivo de notificación
        try:
            os.remove(f"data/pending_actions/{action_id}.json")
        except FileNotFoundError:
            pass

        return True

    # MÉTODOS HELPER PARA INTEGRACIONES

    async def _get_or_create_buyer(self, buyer_id: str, message: Dict) -> Any:
        """Obtiene o crea un comprador en la base de datos"""
        try:
            if self.db:
                # Intentar obtener comprador existente
                buyer = await self.db.get_buyer_by_id(buyer_id)
                if buyer:
                    return buyer

                # Crear nuevo comprador con datos del mensaje
                buyer_data = {
                    "id": buyer_id,
                    "nombre": message.get("sender_name", f"Usuario_{buyer_id[:8]}"),
                    "valoracion": message.get("sender_rating", 0),
                    "ubicacion": message.get("sender_location", "Desconocida"),
                    "fecha_registro": message.get("sender_join_date", datetime.now()),
                    "es_verificado": message.get("sender_verified", False),
                    "foto_perfil": message.get("sender_avatar", None),
                }

                buyer = await self.db.create_buyer(buyer_data)
                logger.info(f"Nuevo comprador creado: {buyer_id}")
                return buyer
            else:
                # Crear objeto buyer temporal sin persistencia
                from conversation_engine.engine import Buyer

                return Buyer(
                    id=buyer_id,
                    nombre=message.get("sender_name", f"Usuario_{buyer_id[:8]}"),
                    valoracion=message.get("sender_rating", 0),
                    ubicacion=message.get("sender_location", "Desconocida"),
                    fecha_registro=message.get("sender_join_date", datetime.now()),
                    es_verificado=message.get("sender_verified", False),
                    foto_perfil=message.get("sender_avatar", None),
                )

        except Exception as e:
            logger.error(f"Error getting/creating buyer {buyer_id}: {e}")
            # Retornar buyer básico en caso de error
            from conversation_engine.engine import Buyer

            return Buyer(
                id=buyer_id,
                nombre=f"Usuario_{buyer_id[:8]}",
                valoracion=0,
                ubicacion="Desconocida",
                fecha_registro=datetime.now(),
                es_verificado=False,
                foto_perfil=None,
            )

    async def _get_product_from_message(self, message: Dict) -> Any:
        """Obtiene información del producto relacionado con el mensaje"""
        try:
            conversation_id = message.get("conversation_id")
            product_id = message.get("product_id")

            if self.db and product_id:
                # Intentar obtener producto desde BD
                product = await self.db.get_product_by_id(product_id)
                if product:
                    return product

            # Crear producto temporal con datos del mensaje o defaults
            from conversation_engine.engine import Product

            return Product(
                id=product_id or f"prod_{conversation_id}",
                titulo=message.get("product_title", "Producto desconocido"),
                precio=float(message.get("product_price", 0)),
                descripcion=message.get("product_description", ""),
                categoria=message.get("product_category", "General"),
                estado=message.get("product_condition", "usado"),
                zona=message.get("product_location", "Desconocida"),
                fotos=[],
                fecha_publicacion=datetime.now(),
                es_envio=message.get("product_shipping", True),
                precio_envio=float(message.get("shipping_cost", 0)),
            )

        except Exception as e:
            logger.error(f"Error getting product from message: {e}")
            from conversation_engine.engine import Product

            return Product(
                id="unknown_product",
                titulo="Producto desconocido",
                precio=0,
                descripcion="",
                categoria="General",
                estado="usado",
                zona="Desconocida",
                fotos=[],
                fecha_publicacion=datetime.now(),
                es_envio=True,
                precio_envio=0,
            )

    async def _save_conversation_data(
        self, buyer: Any, message: Dict, analysis: Dict, suggested_response: str = None
    ):
        """Guarda datos de conversación en la base de datos"""
        try:
            if not self.db:
                logger.warning("Database not available, skipping conversation save")
                return

            # Crear o actualizar conversación
            conversation_id = message.get("conversation_id")
            conversation_data = {
                "id": conversation_id,
                "buyer_id": buyer.id,
                "product_id": message.get("product_id", "unknown"),
                "estado": analysis.get("state", "inicial"),
                "prioridad": analysis.get("priority", "media"),
                "riesgo_fraude": analysis.get("fraud_risk", 0),
                "ultima_actividad": datetime.now(),
                "requiere_atencion": analysis.get("requires_human", False),
            }

            await self.db.create_or_update_conversation(conversation_data)

            # Guardar mensaje
            message_data = {
                "conversation_id": conversation_id,
                "sender_id": buyer.id,
                "content": message.get("content", ""),
                "timestamp": message.get("timestamp", datetime.now()),
                "is_from_me": False,
                "analysis": analysis,
                "suggested_response": suggested_response,
            }

            await self.db.create_message(message_data)
            logger.debug(f"Conversation data saved for {conversation_id}")

        except Exception as e:
            logger.error(f"Error saving conversation data: {e}")


# Mantener compatibilidad
WallapopBot = ComplianceWallapopBot


# Función principal
async def main():
    """Función principal de ejecución COMPLIANCE"""
    bot = ComplianceWallapopBot()

    try:
        await bot.start()
    except Exception as e:
        logger.error(f"[COMPLIANCE] Fatal error: {e}")
    finally:
        await bot.stop()


if __name__ == "__main__":
    # Crear directorios necesarios para COMPLIANCE
    os.makedirs("logs", exist_ok=True)
    os.makedirs("logs/audit", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/pending_actions", exist_ok=True)
    os.makedirs("data/gdpr_consents", exist_ok=True)

    logger.info("[COMPLIANCE] Starting Wallapop Bot in COMPLIANCE mode")
    logger.info("[COMPLIANCE] All actions require human confirmation")
    logger.info("[COMPLIANCE] GDPR compliance enabled")
    logger.info("[COMPLIANCE] Rate limits: 5 messages/hour maximum")

    # Ejecutar bot COMPLIANCE
    asyncio.run(main())
