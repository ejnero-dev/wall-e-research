#!/usr/bin/env python3
"""
Test de integración Bot + AI Engine + Dashboard
Simula una conversación completa para validar el flujo end-to-end
"""
import asyncio
import logging
import sys
from datetime import datetime

# Configurar logging para ver el proceso
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_bot_ai_integration():
    """Test completo Bot + AI Engine"""
    try:
        logger.info("🚀 Iniciando test de integración Bot + AI Engine...")

        # Importar bot con AI Engine integrado
        from src.bot.wallapop_bot import ResearchWallapopBot

        # Crear instancia del bot (modo research)
        logger.info("🤖 Inicializando ResearchWallapopBot...")
        config_path = "config/research_overrides.yaml"
        bot = ResearchWallapopBot(config_path)

        logger.info(f"✅ Bot inicializado exitosamente")
        logger.info(f"   - AI Engine: {bot.ai_engine.status.value}")
        logger.info(
            f"   - Database: {'✅ Connected' if bot.db else '❌ Not available'}"
        )
        logger.info(
            f"   - Scraper: {'✅ Initialized' if bot.scraper else '❌ Not available'}"
        )

        # Simular mensaje de comprador
        test_message = {
            "id": "test_msg_001",
            "conversation_id": "conv_test_001",
            "buyer_id": "buyer_test_001",
            "product_id": "prod_test_001",
            "content": "¡Hola! ¿Está disponible el iPhone? ¿Cuál es el precio final?",
            "timestamp": datetime.now().isoformat(),
            "sender": "buyer",
        }

        logger.info("💬 Simulando procesamiento de mensaje...")
        logger.info(f"   Mensaje: '{test_message['content']}'")

        # Procesar mensaje con el bot (esto activará el AI Engine)
        await bot._process_message(test_message)

        logger.info("✅ Mensaje procesado exitosamente")

        # Mostrar estadísticas del bot
        logger.info("📊 Estadísticas del bot:")
        for key, value in bot.stats.items():
            logger.info(f"   - {key}: {value}")

        logger.info("🎉 Test de integración completado exitosamente!")
        return True

    except Exception as e:
        logger.error(f"❌ Error en test de integración: {e}")
        logger.error(f"   Tipo: {type(e).__name__}")
        import traceback

        logger.error(f"   Stack: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_bot_ai_integration())
        if result:
            print("\n🎯 SUCCESS: Bot + AI Engine integration working!")
            sys.exit(0)
        else:
            print("\n💥 FAILED: Integration test failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚡ Test cancelled by user")
        sys.exit(1)
