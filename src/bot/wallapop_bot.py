# wallapop_bot.py
"""
Bot principal de automatización para Wallapop
Coordina todas las funcionalidades del sistema
"""

import asyncio
import logging
import os
import yaml
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

# Importaciones locales (se implementarán)
# from conversation_engine.engine import ConversationEngine
# from scraper.wallapop_scraper import WallapopScraper
# from database.db_manager import DatabaseManager

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/wallapop_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WallapopBot:
    """Clase principal del bot de Wallapop"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Inicializa el bot con la configuración"""
        self.config = self._load_config(config_path)
        self.is_running = False
        
        # Inicializar componentes
        logger.info("Inicializando WallapopBot...")
        # self.conversation_engine = ConversationEngine()
        # self.scraper = WallapopScraper(self.config)
        # self.db = DatabaseManager(self.config['database'])
        
        # Estado del bot
        self.active_conversations = {}
        self.pending_responses = []
        self.stats = {
            "messages_processed": 0,
            "responses_sent": 0,
            "sales_completed": 0,
            "fraud_attempts_blocked": 0
        }
    
    def _load_config(self, path: str) -> Dict:
        """Carga la configuración desde archivo YAML"""
        if not os.path.exists(path):
            logger.warning(f"Config file not found at {path}, using defaults")
            return self._get_default_config()
        
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict:
        """Retorna configuración por defecto"""
        return {
            "wallapop": {
                "behavior": {
                    "min_delay_between_messages": 30,
                    "max_delay_between_messages": 120,
                    "active_hours": {
                        "start": "09:00",
                        "end": "22:00",
                        "timezone": "Europe/Madrid"
                    },
                    "max_concurrent_conversations": 5,
                    "max_messages_per_conversation": 20
                }
            },
            "security": {
                "fraud_detection": {
                    "enabled": True,
                    "auto_block_suspicious": False
                }
            },
            "notifications": {
                "desktop_notifications": True
            }
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
            self._check_abandoned_conversations()
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
    
    async def _monitor_messages(self):
        """Monitorea mensajes nuevos"""
        while self.is_running:
            try:
                # Simular obtención de mensajes
                # messages = await self.scraper.get_new_messages()
                
                # for message in messages:
                #     await self._process_message(message)
                
                await asyncio.sleep(10)  # Check cada 10 segundos
                
            except Exception as e:
                logger.error(f"Error monitoring messages: {e}")
                await asyncio.sleep(30)
    
    async def _process_message(self, message: Dict):
        """Procesa un mensaje individual"""
        try:
            logger.info(f"Processing message from {message.get('buyer_id')}")
            self.stats["messages_processed"] += 1
            
            # Analizar mensaje
            # analysis = self.conversation_engine.analyze_message(
            #     message['text'],
            #     message['buyer'],
            #     message['product']
            # )
            
            # Si es fraude, manejar apropiadamente
            # if analysis['fraud_risk'] > 70:
            #     self.stats["fraud_attempts_blocked"] += 1
            #     logger.warning(f"Fraud attempt detected from {message['buyer_id']}")
            
            # Generar respuesta
            # response = self.conversation_engine.generate_response(
            #     analysis,
            #     message['text'],
            #     message['buyer'],
            #     message['product']
            # )
            
            # if response:
            #     await self._queue_response(message['buyer_id'], response)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _queue_response(self, buyer_id: str, response: str):
        """Añade respuesta a la cola con delay apropiado"""
        delay = self._calculate_response_delay()
        
        self.pending_responses.append({
            "buyer_id": buyer_id,
            "response": response,
            "send_after": datetime.now().timestamp() + delay
        })
    
    def _calculate_response_delay(self) -> int:
        """Calcula delay para parecer humano"""
        import random
        config = self.config['wallapop']['behavior']
        return random.randint(
            config['min_delay_between_messages'],
            config['max_delay_between_messages']
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
                    if current_time >= response['send_after']:
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
        
        config = self.config['wallapop']['behavior']['active_hours']
        tz = pytz.timezone(config['timezone'])
        now = datetime.now(tz)
        
        start_hour = int(config['start'].split(':')[0])
        end_hour = int(config['end'].split(':')[0])
        
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
    
    def _save_state(self):
        """Guarda el estado actual del bot"""
        state = {
            "stats": self.stats,
            "active_conversations": len(self.active_conversations),
            "pending_responses": len(self.pending_responses),
            "timestamp": datetime.now().isoformat()
        }
        
        with open('logs/bot_state.json', 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info("Bot state saved")

# Función principal
async def main():
    """Función principal de ejecución"""
    bot = WallapopBot()
    
    try:
        await bot.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    # Crear directorios necesarios
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Ejecutar bot
    asyncio.run(main())
