#!/usr/bin/env python3
"""
🎯 DEMOSTRACIÓN COMPLETA DEL SISTEMA WALL-E
Muestra todas las capacidades integradas funcionando juntas:
- AI Engine con IA generativa
- Anti-detección de fraude
- Análisis de precios competitivos
- Dashboard en tiempo real
- Scraper avanzado
"""
import asyncio
import logging
import sys
import json
import os
from datetime import datetime
from typing import Dict, List

# Añadir el directorio padre al path para importar módulos src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configurar logging detallado
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WallESystemDemo:
    """Demostración completa del sistema integrado"""
    
    def __init__(self):
        self.product_demo = {
            "id": "demo_iphone12_001",
            "name": "iPhone 12 128GB Negro",
            "price": 420.0,
            "condition": "como nuevo",
            "description": "iPhone 12 en perfecto estado, sin arañazos, con caja original y cargador.",
            "location": "Madrid",
            "category": "smartphones",
            "seller_rating": 4.8
        }
        
        self.conversation_scenarios = [
            {
                "buyer_name": "María_García",
                "buyer_message": "¡Hola! ¿Está disponible el iPhone? ¿Cuál es el precio final?",
                "expected_outcome": "respuesta_normal"
            },
            {
                "buyer_name": "Estafador_Sospechoso", 
                "buyer_message": "Hola, te pago por PayPal familia y amigos, necesito que me envíes a Francia urgente",
                "expected_outcome": "deteccion_fraude"
            },
            {
                "buyer_name": "Cliente_Negociador",
                "buyer_message": "Me interesa mucho, pero he visto otros a 380€. ¿Puedes bajar algo el precio?",
                "expected_outcome": "negociacion"
            },
            {
                "buyer_name": "Comprador_Serio",
                "buyer_message": "Buenos días, ¿podemos quedar para verlo? Estoy interesado en comprarlo hoy mismo",
                "expected_outcome": "venta_probable"
            }
        ]
    
    async def demo_ai_engine_responses(self):
        """Demuestra respuestas del AI Engine con diferentes escenarios"""
        logger.info("🤖 === DEMO: AI ENGINE CON IA GENERATIVA ===")
        
        try:
            from src.ai_engine import AIEngine, AIEngineConfig
            from src.ai_engine.ai_engine import ConversationRequest
            
            # Inicializar AI Engine
            config = AIEngineConfig.for_research()
            ai_engine = AIEngine(config)
            logger.info(f"✅ AI Engine inicializado: {ai_engine.status.value}")
            
            # Procesar cada escenario
            for i, scenario in enumerate(self.conversation_scenarios, 1):
                logger.info(f"\n📱 ESCENARIO {i}: {scenario['expected_outcome'].upper()}")
                logger.info(f"👤 Comprador: {scenario['buyer_name']}")
                logger.info(f"💬 Mensaje: '{scenario['buyer_message']}'")
                
                # Crear request
                request = ConversationRequest(
                    buyer_message=scenario['buyer_message'],
                    buyer_name=scenario['buyer_name'],
                    product_name=self.product_demo['name'],
                    price=self.product_demo['price'],
                    personality="profesional_cordial"
                )
                
                # Generar respuesta con AI Engine
                response = ai_engine.generate_response(request)
                
                # Mostrar resultados
                logger.info(f"🎯 Fuente: {response.source}")
                logger.info(f"🧠 Respuesta IA: '{response.response_text}'")
                logger.info(f"⚡ Confianza: {response.confidence:.2f}")
                logger.info(f"🛡️ Risk Score: {response.risk_score}/100")
                
                if response.risk_score > 70:
                    logger.warning(f"🚨 FRAUDE DETECTADO - Score: {response.risk_score}")
                elif response.risk_score > 40:
                    logger.info(f"⚠️ Riesgo medio detectado")
                else:
                    logger.info(f"✅ Conversación segura")
                
                await asyncio.sleep(1)  # Pausa entre escenarios
                
        except Exception as e:
            logger.error(f"❌ Error en demo AI Engine: {e}")
            return False
            
        return True
    
    async def demo_price_analysis(self):
        """Demuestra análisis de precios competitivos"""
        logger.info("\n💰 === DEMO: ANÁLISIS DE PRECIOS COMPETITIVOS ===")
        
        try:
            from src.price_analyzer.analyzer import PriceAnalyzer, PriceData
            
            # Crear datos de ejemplo (simulando scraping real)
            sample_prices = [
                PriceData("wallapop", "iPhone 12 128GB", 380, "usado", True, "Barcelona", "", datetime.now()),
                PriceData("wallapop", "iPhone 12 128GB", 420, "como nuevo", True, "Madrid", "", datetime.now()),
                PriceData("wallapop", "iPhone 12 128GB", 450, "nuevo", True, "Valencia", "", datetime.now()),
                PriceData("amazon", "iPhone 12 128GB", 529, "nuevo", True, "Online", "", datetime.now()),
                PriceData("wallapop", "iPhone 12 128GB", 400, "buen estado", False, "Sevilla", "", datetime.now()),
            ]
            
            analyzer = PriceAnalyzer()
            
            # Simular análisis
            prices = [p.price for p in sample_prices]
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            logger.info(f"📊 Producto analizado: {self.product_demo['name']}")
            logger.info(f"📈 Precio promedio: {avg_price:.2f}€")
            logger.info(f"📉 Rango: {min_price}€ - {max_price}€")
            logger.info(f"🎯 Tu precio: {self.product_demo['price']}€")
            
            # Sugerencias de pricing
            competitive_price = avg_price * 0.95  # 5% below average
            premium_price = avg_price * 1.05     # 5% above average
            
            logger.info(f"💡 RECOMENDACIONES:")
            logger.info(f"   🏃 Venta rápida: {competitive_price:.2f}€")
            logger.info(f"   💰 Maximizar ganancia: {premium_price:.2f}€")
            
            if self.product_demo['price'] < competitive_price:
                logger.info(f"   ✅ Tu precio es MUY competitivo")
            elif self.product_demo['price'] <= premium_price:
                logger.info(f"   ⚖️ Tu precio está en rango óptimo")
            else:
                logger.info(f"   ⚠️ Tu precio podría ser alto")
                
        except Exception as e:
            logger.error(f"❌ Error en análisis de precios: {e}")
            return False
            
        return True
    
    async def demo_bot_integration(self):
        """Demuestra bot completo con integración"""
        logger.info("\n🤖 === DEMO: BOT INTEGRADO CON DASHBOARD ===")
        
        try:
            from src.bot.wallapop_bot import ResearchWallapopBot
            
            # Inicializar bot
            bot = ResearchWallapopBot("config/research_overrides.yaml")
            logger.info("✅ Bot inicializado con AI Engine integrado")
            
            # Simular mensajes llegando al bot
            for i, scenario in enumerate(self.conversation_scenarios[:2], 1):  # Solo 2 para demo
                test_message = {
                    'id': f'demo_msg_{i:03d}',
                    'conversation_id': f'conv_demo_{i:03d}',
                    'buyer_id': f'buyer_{scenario["buyer_name"]}',
                    'product_id': self.product_demo['id'],
                    'content': scenario['buyer_message'],
                    'timestamp': datetime.now().isoformat(),
                    'sender': 'buyer'
                }
                
                logger.info(f"\n📨 Procesando mensaje {i}:")
                logger.info(f"   👤 De: {scenario['buyer_name']}")
                logger.info(f"   💬 Contenido: '{scenario['buyer_message']}'")
                
                # Procesar con bot integrado (esto activa AI Engine + Dashboard)
                await bot._process_message(test_message)
                
                logger.info(f"   ✅ Mensaje procesado y datos enviados al dashboard")
                await asyncio.sleep(2)  # Pausa para ver updates en dashboard
                
        except Exception as e:
            logger.error(f"❌ Error en demo bot integrado: {e}")
            return False
            
        return True
    
    async def run_complete_demo(self):
        """Ejecuta la demostración completa del sistema"""
        logger.info("🚀 INICIANDO DEMOSTRACIÓN COMPLETA DEL SISTEMA WALL-E")
        logger.info("=" * 60)
        
        logger.info(f"📱 PRODUCTO DEMO: {self.product_demo['name']}")
        logger.info(f"💰 Precio: {self.product_demo['price']}€")
        logger.info(f"📍 Ubicación: {self.product_demo['location']}")
        logger.info(f"⭐ Estado: {self.product_demo['condition']}")
        
        results = {
            "ai_engine": False,
            "price_analysis": False, 
            "bot_integration": False
        }
        
        # 1. Demo AI Engine
        results["ai_engine"] = await self.demo_ai_engine_responses()
        
        # 2. Demo análisis de precios
        results["price_analysis"] = await self.demo_price_analysis()
        
        # 3. Demo bot integrado
        results["bot_integration"] = await self.demo_bot_integration()
        
        # Resumen final
        logger.info("\n" + "=" * 60)
        logger.info("📊 RESUMEN DE LA DEMOSTRACIÓN:")
        
        for component, success in results.items():
            status = "✅ ÉXITO" if success else "❌ FALLO"
            logger.info(f"   {component.upper()}: {status}")
        
        total_success = all(results.values())
        if total_success:
            logger.info("\n🎉 DEMOSTRACIÓN COMPLETA EXITOSA!")
            logger.info("🎯 Todos los componentes funcionando perfectamente")
            logger.info("📊 Revisa el dashboard en: http://localhost:3000")
        else:
            logger.info("\n⚠️ Algunos componentes tuvieron problemas")
            
        return total_success

async def main():
    """Función principal de la demostración"""
    demo = WallESystemDemo()
    success = await demo.run_complete_demo()
    
    if success:
        print("\n🎯 SUCCESS: Sistema Wall-E demostrado completamente!")
        sys.exit(0)
    else:
        print("\n💥 Algunos componentes fallaron en la demostración")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚡ Demo cancelada por usuario")
        sys.exit(1)