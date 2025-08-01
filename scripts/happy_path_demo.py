#!/usr/bin/env python3
"""
Demo del Happy Path simple:
Recibir mensaje → Detectar saludo → Responder

Este script demuestra el funcionamiento básico del motor de conversaciones
sin necesidad de base de datos o scrapers.
"""

import sys
from pathlib import Path
from datetime import datetime
import asyncio
import logging
from typing import List, Tuple

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from conversation_engine.engine import (
    ConversationEngine,
    Buyer,
    Product,
    ConversationState,
    IntentionType
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HappyPathDemo:
    """Demostración del flujo básico del bot"""
    
    def __init__(self):
        self.engine = ConversationEngine()
        self.setup_demo_data()
        
    def setup_demo_data(self):
        """Configura datos de demostración"""
        # Comprador de ejemplo
        self.buyer = Buyer(
            id="demo_buyer_001",
            username="maria_garcia",
            valoraciones=25,
            num_compras=10,
            distancia_km=5.2,
            ultima_actividad=datetime.now(),
            perfil_verificado=True,
            tiene_foto=True
        )
        
        # Producto de ejemplo
        self.product = Product(
            id="demo_product_001",
            titulo="iPhone 13 128GB Azul",
            precio=599.0,
            precio_minimo=550.0,
            descripcion="iPhone 13 en excelente estado, con caja y accesorios originales",
            estado="Como nuevo",
            categoria="Móviles y Telefonía",
            permite_envio=True,
            zona="Chamberí, Madrid"
        )
    
    def display_message(self, sender: str, message: str, is_bot: bool = False):
        """Muestra un mensaje en la consola con formato"""
        icon = "🤖" if is_bot else "👤"
        prefix = "Bot" if is_bot else sender
        print(f"\n{icon} {prefix}: {message}")
    
    def display_analysis(self, analysis: dict):
        """Muestra el análisis del mensaje"""
        print("\n📊 Análisis del mensaje:")
        print(f"   - Intención detectada: {analysis['intention'].value}")
        print(f"   - Prioridad: {analysis['priority'].value}")
        print(f"   - Riesgo de fraude: {analysis['fraud_risk']}%")
        print(f"   - Estado conversación: {analysis['state'].value}")
        print(f"   - Requiere humano: {'Sí' if analysis['requires_human'] else 'No'}")
    
    async def simulate_conversation(self, messages: List[str]):
        """Simula una conversación completa"""
        print("\n" + "="*60)
        print("🎯 DEMO: Happy Path - Flujo de Conversación Simple")
        print("="*60)
        
        print(f"\n📱 Producto: {self.product.titulo}")
        print(f"💰 Precio: {self.product.precio}€")
        print(f"📍 Zona: {self.product.zona}")
        print(f"\n👤 Comprador: {self.buyer.username} (⭐ {self.buyer.valoraciones} valoraciones)")
        
        print("\n" + "-"*60)
        print("💬 CONVERSACIÓN:")
        print("-"*60)
        
        for message in messages:
            # Mostrar mensaje del comprador
            self.display_message(self.buyer.username, message)
            
            # Analizar mensaje
            analysis = self.engine.analyze_message(
                message,
                self.buyer,
                self.product
            )
            
            # Mostrar análisis
            self.display_analysis(analysis)
            
            # Generar respuesta
            response = self.engine.generate_response(
                analysis,
                message,
                self.buyer,
                self.product
            )
            
            # Simular delay humano
            await asyncio.sleep(1)
            
            # Mostrar respuesta del bot
            if response:
                self.display_message("Bot", response, is_bot=True)
            else:
                self.display_message("Bot", "No se generó respuesta", is_bot=True)
            
            # Pausa entre mensajes
            await asyncio.sleep(1.5)
        
        # Mostrar resumen final
        self.display_conversation_summary()
    
    def display_conversation_summary(self):
        """Muestra el resumen de la conversación"""
        print("\n" + "="*60)
        print("📈 RESUMEN DE LA CONVERSACIÓN:")
        print("="*60)
        
        summary = self.engine.get_conversation_summary(self.buyer.id)
        
        if summary["exists"]:
            print(f"✅ Estado final: {summary['state']}")
            print(f"📬 Total mensajes: {summary['messages_count']}")
            print(f"⚠️  Requiere atención: {'Sí' if summary['requires_attention'] else 'No'}")
            print(f"🚨 Score de fraude: {summary['fraud_score']}")
        else:
            print("❌ No se encontró información de la conversación")


async def main():
    """Función principal de demostración"""
    demo = HappyPathDemo()
    
    # Escenario 1: Conversación exitosa de venta
    print("\n🎬 ESCENARIO 1: Venta exitosa")
    print("="*80)
    
    messages_venta = [
        "Hola! Está disponible el iPhone?",
        "Qué tal está? Funciona todo bien?",
        "Cuál es tu último precio?",
        "Vale, lo quiero. Cuándo podemos quedar?",
        "Perfecto, nos vemos mañana entonces"
    ]
    
    await demo.simulate_conversation(messages_venta)
    
    # Reset para nuevo escenario
    demo.engine.conversations.clear()
    await asyncio.sleep(3)
    
    # Escenario 2: Intento de fraude detectado
    print("\n\n🎬 ESCENARIO 2: Detección de fraude")
    print("="*80)
    
    # Cambiar a comprador sospechoso
    demo.buyer = Buyer(
        id="suspicious_buyer",
        username="usuario12345",
        valoraciones=0,
        num_compras=0,
        distancia_km=1200,
        ultima_actividad=datetime.now(),
        perfil_verificado=False,
        tiene_foto=False
    )
    
    messages_fraude = [
        "Hola, me interesa",
        "Dame tu whatsapp para hablar mejor",
        "Te pago por western union, mi transportista lo recoge"
    ]
    
    await demo.simulate_conversation(messages_fraude)
    
    print("\n\n✅ Demo completada con éxito!")
    print("📝 Los tests pueden ejecutarse con: pytest tests/")


if __name__ == "__main__":
    asyncio.run(main())