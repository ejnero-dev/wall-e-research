"""
Integración del scraper con el ConversationEngine existente
Orquesta la comunicación entre scraping y análisis de conversaciones
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Importaciones del proyecto existente
from ..conversation_engine.engine import ConversationEngine, Buyer, Product
from ..database.models import (
    Conversation,
    Message,
    BotSession,
    ConversationStatus,
    MessageType,
    ProductStatus,
)
from ..database.db_manager import DatabaseManager

# Importaciones del scraper
from .wallapop_scraper import (
    WallapopScraper,
    MessageData,
    ConversationData,
    ProductData,
)
from .session_manager import AuthMethod
from .error_handler import error_handler, ErrorSeverity
from .config import scraper_config

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Resultado del procesamiento de un mensaje"""

    success: bool
    response_sent: bool
    response_text: Optional[str] = None
    error_message: Optional[str] = None
    requires_human: bool = False


class ScraperIntegration:
    """Integrador principal entre scraper y motor de conversaciones"""

    def __init__(self, auth_method: AuthMethod = AuthMethod.AUTO):
        self.scraper = WallapopScraper(auth_method)
        self.conversation_engine = ConversationEngine()
        self.db_manager = DatabaseManager()

        # Estado interno
        self.is_running = False
        self.last_scan_time: Optional[datetime] = None
        self.processed_messages: set = set()
        self.active_conversations: Dict[str, datetime] = {}

        # Configuración de procesamiento
        self.scan_interval = 30  # Segundos entre escaneos
        self.max_concurrent_conversations = scraper_config.MAX_CONCURRENT_CONVERSATIONS
        self.message_processing_delay = scraper_config.get_human_delay()

        # Configurar callbacks del scraper
        self.scraper.set_message_callback(self._on_new_message)
        self.scraper.set_conversation_callback(self._on_new_conversation)
        self.scraper.set_error_callback(self._on_scraper_error)

    async def start(self) -> bool:
        """Inicia el sistema integrado"""
        logger.info("Starting scraper integration")

        try:
            # Inicializar base de datos
            await self.db_manager.init_db()

            # Iniciar scraper
            success = await self.scraper.start()
            if not success:
                raise Exception("Failed to start scraper")

            # Iniciar bucle principal
            self.is_running = True
            asyncio.create_task(self._main_processing_loop())

            logger.info("Scraper integration started successfully")
            return True

        except Exception as e:
            logger.error(f"Error starting scraper integration: {e}")
            error_handler.record_error(
                e, {"context": "integration_start"}, ErrorSeverity.CRITICAL
            )
            return False

    async def stop(self):
        """Detiene el sistema integrado"""
        logger.info("Stopping scraper integration")

        self.is_running = False
        await self.scraper.stop()
        await self.db_manager.close_connections()

        logger.info("Scraper integration stopped")

    async def _main_processing_loop(self):
        """Bucle principal de procesamiento"""
        logger.info("Starting main processing loop")

        while self.is_running:
            try:
                # Verificar si estamos en horario activo
                if not scraper_config.is_within_active_hours():
                    logger.info("Outside active hours, sleeping...")
                    await asyncio.sleep(300)  # 5 minutos
                    continue

                # Escanear conversaciones
                await self._scan_conversations()

                # Procesar mensajes nuevos
                await self._process_new_messages()

                # Gestionar conversaciones activas
                await self._manage_active_conversations()

                # Actualizar estadísticas
                await self._update_session_stats()

                # Esperar antes del siguiente ciclo
                await asyncio.sleep(self.scan_interval)

            except Exception as e:
                logger.error(f"Error in main processing loop: {e}")
                error_handler.record_error(
                    e, {"context": "main_loop"}, ErrorSeverity.HIGH
                )
                await asyncio.sleep(60)  # Esperar más tiempo en caso de error

    async def _scan_conversations(self):
        """Escanea conversaciones en Wallapop"""
        logger.debug("Scanning conversations")

        try:
            # Obtener conversaciones del scraper
            conversations = await self.scraper.get_conversations()

            for conv_data in conversations:
                # Verificar si ya tenemos esta conversación en BD
                await self._get_or_create_conversation(conv_data)

                # Actualizar tiempo de última actividad
                if conv_data.unread_count > 0:
                    self.active_conversations[conv_data.id] = datetime.now()

            self.last_scan_time = datetime.now()
            logger.debug(f"Scanned {len(conversations)} conversations")

        except Exception as e:
            logger.error(f"Error scanning conversations: {e}")
            error_handler.record_error(
                e, {"context": "scan_conversations"}, ErrorSeverity.MEDIUM
            )

    async def _process_new_messages(self):
        """Procesa mensajes nuevos"""
        logger.debug("Processing new messages")

        try:
            # Obtener conversaciones con mensajes no leídos
            active_conversations = list(self.active_conversations.keys())[
                : self.max_concurrent_conversations
            ]

            for conv_id in active_conversations:
                try:
                    await self._process_conversation_messages(conv_id)
                except Exception as e:
                    logger.error(f"Error processing conversation {conv_id}: {e}")
                    continue

                # Delay entre conversaciones
                await asyncio.sleep(scraper_config.get_human_delay())

        except Exception as e:
            logger.error(f"Error processing new messages: {e}")
            error_handler.record_error(
                e, {"context": "process_messages"}, ErrorSeverity.MEDIUM
            )

    async def _process_conversation_messages(self, conversation_id: str):
        """Procesa mensajes de una conversación específica"""
        logger.debug(f"Processing messages for conversation {conversation_id}")

        try:
            # Obtener mensajes del scraper
            messages = await self.scraper.get_messages(conversation_id)

            # Filtrar mensajes no procesados que no sean nuestros
            new_messages = [
                msg
                for msg in messages
                if not msg.is_from_me and msg.id not in self.processed_messages
            ]

            if not new_messages:
                return

            logger.info(
                f"Found {len(new_messages)} new messages in conversation {conversation_id}"
            )

            # Obtener datos de la conversación desde BD
            conversation = await self._get_conversation_by_external_id(conversation_id)
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found in database")
                return

            # Procesar cada mensaje nuevo
            for message_data in new_messages:
                try:
                    result = await self._process_single_message(
                        message_data, conversation
                    )

                    # Marcar mensaje como procesado
                    self.processed_messages.add(message_data.id)

                    # Si se requiere intervención humana, pausar procesamiento automático
                    if result.requires_human:
                        logger.warning(
                            f"Human intervention required for conversation {conversation_id}"
                        )
                        await self._flag_for_human_review(
                            conversation, message_data, result.error_message
                        )

                    # Delay entre mensajes
                    await asyncio.sleep(scraper_config.get_human_delay())

                except Exception as e:
                    logger.error(f"Error processing message {message_data.id}: {e}")
                    error_handler.record_error(
                        e,
                        {
                            "context": "process_single_message",
                            "message_id": message_data.id,
                            "conversation_id": conversation_id,
                        },
                        ErrorSeverity.HIGH,
                    )
                    continue

            # Actualizar timestamp de conversación
            if conversation_id in self.active_conversations:
                self.active_conversations[conversation_id] = datetime.now()

        except Exception as e:
            logger.error(f"Error processing conversation messages: {e}")
            raise

    async def _process_single_message(
        self, message_data: MessageData, conversation: Conversation
    ) -> ProcessingResult:
        """Procesa un mensaje individual"""
        logger.debug(f"Processing message: {message_data.content[:50]}...")

        try:
            # Guardar mensaje en BD
            await self._save_message_to_db(message_data, conversation)

            # Crear objetos para el motor de conversaciones
            buyer = await self._create_buyer_object(conversation)
            product = await self._create_product_object(conversation)

            # Analizar mensaje con el motor de conversaciones
            analysis = self.conversation_engine.analyze_message(
                message_data.content, buyer, product
            )

            logger.info(f"Message analysis: {analysis}")

            # Verificar si requiere intervención humana
            if analysis.get("requires_human", False):
                return ProcessingResult(
                    success=True,
                    response_sent=False,
                    requires_human=True,
                    error_message=f"High fraud risk: {analysis.get('fraud_risk', 0)}",
                )

            # Generar respuesta
            response = self.conversation_engine.generate_response(
                analysis, message_data.content, buyer, product
            )

            if not response:
                logger.warning("No response generated by conversation engine")
                return ProcessingResult(
                    success=True,
                    response_sent=False,
                    error_message="No response generated",
                )

            # Verificar si debemos responder según timing
            should_respond = self.conversation_engine.should_respond(
                buyer, message_data.timestamp
            )

            if not should_respond:
                logger.info("Delaying response based on timing rules")
                return ProcessingResult(
                    success=True,
                    response_sent=False,
                    response_text=response,
                    error_message="Response delayed by timing rules",
                )

            # Enviar respuesta
            success = await self.scraper.send_message(
                conversation.wallapop_chat_id, response
            )

            if success:
                # Guardar respuesta en BD
                await self._save_response_to_db(response, conversation)

                logger.info(f"Response sent successfully: {response[:50]}...")
                return ProcessingResult(
                    success=True, response_sent=True, response_text=response
                )
            else:
                return ProcessingResult(
                    success=False,
                    response_sent=False,
                    response_text=response,
                    error_message="Failed to send response",
                )

        except Exception as e:
            logger.error(f"Error processing single message: {e}")
            return ProcessingResult(
                success=False,
                response_sent=False,
                error_message=str(e),
                requires_human=True,
            )

    async def _get_or_create_conversation(
        self, conv_data: ConversationData
    ) -> Conversation:
        """Obtiene o crea conversación en la base de datos"""
        try:
            # Buscar conversación existente
            existing_conv = await self.db_manager.get_conversation_by_external_id(
                conv_data.id
            )

            if existing_conv:
                return existing_conv

            # Crear nueva conversación
            # Primero obtener o crear buyer
            buyer = await self._get_or_create_buyer(conv_data)

            # Obtener o crear producto
            product = await self._get_or_create_product(conv_data)

            # Crear conversación
            conversation = Conversation(
                wallapop_chat_id=conv_data.id,
                product_id=product.id,
                buyer_id=buyer.id,
                status=ConversationStatus.ACTIVE,
                last_message_at=conv_data.last_activity,
                message_count=0,
            )

            await self.db_manager.save_conversation(conversation)
            logger.info(f"Created new conversation: {conv_data.id}")

            return conversation

        except Exception as e:
            logger.error(f"Error getting/creating conversation: {e}")
            raise

    async def _get_or_create_buyer(self, conv_data: ConversationData):
        """Obtiene o crea comprador en la base de datos"""
        # Implementación simplificada - en producción sería más compleja
        from ..database.models import Buyer

        existing_buyer = await self.db_manager.get_buyer_by_external_id(
            conv_data.buyer_id
        )

        if existing_buyer:
            return existing_buyer

        buyer = Buyer(
            wallapop_user_id=conv_data.buyer_id,
            username=conv_data.buyer_name,
            display_name=conv_data.buyer_name,
            is_verified=False,
            trust_score=0.5,
        )

        await self.db_manager.save_buyer(buyer)
        return buyer

    async def _get_or_create_product(self, conv_data: ConversationData):
        """Obtiene o crea producto en la base de datos"""
        from ..database.models import Product

        existing_product = await self.db_manager.get_product_by_external_id(
            conv_data.product_id
        )

        if existing_product:
            return existing_product

        product = Product(
            wallapop_id=conv_data.product_id,
            title=conv_data.product_title,
            price=0.0,  # Se actualizará con scraping detallado
            status=ProductStatus.AVAILABLE,
        )

        await self.db_manager.save_product(product)
        return product

    async def _create_buyer_object(self, conversation: Conversation) -> Buyer:
        """Crea objeto Buyer para el motor de conversaciones"""
        db_buyer = await self.db_manager.get_buyer_by_id(conversation.buyer_id)

        return Buyer(
            id=db_buyer.wallapop_user_id,
            username=db_buyer.username,
            valoraciones=0,  # Requeriría scraping adicional
            num_compras=db_buyer.completed_purchases,
            distancia_km=50.0,  # Valor por defecto
            ultima_actividad=db_buyer.last_active_at or datetime.now(),
            perfil_verificado=db_buyer.is_verified,
            tiene_foto=True,  # Valor por defecto
        )

    async def _create_product_object(self, conversation: Conversation) -> Product:
        """Crea objeto Product para el motor de conversaciones"""
        db_product = await self.db_manager.get_product_by_id(conversation.product_id)

        return Product(
            id=db_product.wallapop_id,
            titulo=db_product.title,
            precio=db_product.price,
            precio_minimo=db_product.price * 0.9,  # 10% menos como mínimo
            descripcion=db_product.description or "",
            estado=db_product.condition or "good",
            categoria=db_product.category or "general",
            permite_envio=True,  # Valor por defecto
            zona=db_product.location or "Madrid",
        )

    async def _save_message_to_db(
        self, message_data: MessageData, conversation: Conversation
    ) -> Message:
        """Guarda mensaje en la base de datos"""
        db_message = Message(
            wallapop_message_id=message_data.id,
            conversation_id=conversation.id,
            buyer_id=conversation.buyer_id,
            content=message_data.content,
            message_type=MessageType.USER_MESSAGE,
            is_read=message_data.is_read,
            is_processed=True,
        )

        await self.db_manager.save_message(db_message)
        return db_message

    async def _save_response_to_db(self, response: str, conversation: Conversation):
        """Guarda respuesta del bot en la base de datos"""
        response_message = Message(
            wallapop_message_id=f"bot_{int(datetime.now().timestamp())}",
            conversation_id=conversation.id,
            buyer_id=None,  # Es respuesta del bot
            content=response,
            message_type=MessageType.BOT_MESSAGE,
            is_read=True,
            is_processed=True,
        )

        await self.db_manager.save_message(response_message)

    async def _flag_for_human_review(
        self, conversation: Conversation, message_data: MessageData, reason: str
    ):
        """Marca conversación para revisión humana"""
        # Actualizar estado de conversación
        conversation.status = ConversationStatus.BLOCKED
        conversation.bot_confidence = 0.0

        await self.db_manager.update_conversation(conversation)

        # Enviar alerta
        if error_handler.alert_manager:
            await error_handler.alert_manager.send_alert(
                title="Human Review Required",
                message=f"Conversation {conversation.id} flagged for review. Reason: {reason}",
                severity=ErrorSeverity.HIGH,
                context={
                    "conversation_id": conversation.id,
                    "buyer_id": conversation.buyer_id,
                    "message_content": message_data.content,
                    "reason": reason,
                },
            )

    async def _manage_active_conversations(self):
        """Gestiona conversaciones activas y timeouts"""
        current_time = datetime.now()
        timeout_threshold = timedelta(hours=2)  # 2 horas sin actividad

        expired_conversations = []

        for conv_id, last_activity in self.active_conversations.items():
            if current_time - last_activity > timeout_threshold:
                expired_conversations.append(conv_id)

        # Remover conversaciones expiradas
        for conv_id in expired_conversations:
            del self.active_conversations[conv_id]
            logger.debug(f"Removed expired conversation: {conv_id}")

    async def _update_session_stats(self):
        """Actualiza estadísticas de la sesión"""
        try:
            session_stats = {
                "active_conversations_count": len(self.active_conversations),
                "messages_sent_today": self.scraper.total_messages_processed,
                "last_activity_at": datetime.now(),
                "is_rate_limited": False,
            }

            # Guardar en BD si tenemos BotSession
            # Implementación simplificada
            logger.debug(f"Session stats: {session_stats}")

        except Exception as e:
            logger.error(f"Error updating session stats: {e}")

    # ===== CALLBACKS DEL SCRAPER =====

    async def _on_new_message(self, message_data: MessageData):
        """Callback para nuevos mensajes"""
        logger.info(f"New message received: {message_data.id}")
        # El procesamiento se maneja en el bucle principal

    async def _on_new_conversation(self, conversation_data: ConversationData):
        """Callback para nuevas conversaciones"""
        logger.info(f"New conversation detected: {conversation_data.id}")
        self.active_conversations[conversation_data.id] = datetime.now()

    async def _on_scraper_error(self, error: Exception, context: Dict[str, Any]):
        """Callback para errores del scraper"""
        logger.error(f"Scraper error: {error}")
        error_handler.record_error(error, context, ErrorSeverity.HIGH)

    # ===== MÉTODOS AUXILIARES =====

    async def _get_conversation_by_external_id(
        self, external_id: str
    ) -> Optional[Conversation]:
        """Obtiene conversación por ID externo"""
        return await self.db_manager.get_conversation_by_external_id(external_id)

    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado del integrador"""
        return {
            "is_running": self.is_running,
            "last_scan_time": (
                self.last_scan_time.isoformat() if self.last_scan_time else None
            ),
            "active_conversations": len(self.active_conversations),
            "processed_messages": len(self.processed_messages),
            "scraper_status": self.scraper.get_status(),
        }
