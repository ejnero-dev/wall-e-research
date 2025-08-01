# conftest.py
"""
Configuración global de pytest y fixtures compartidas
"""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path
import sys
import json

# Añadir src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from conversation_engine.engine import (
    ConversationEngine, 
    Buyer, 
    Product,
    ConversationState,
    IntentionType,
    BuyerPriority
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def conversation_engine():
    """Fixture que proporciona una instancia del motor de conversaciones"""
    # Usar templates de test si existen, si no usar las reales
    test_templates_path = Path(__file__).parent / "fixtures" / "test_responses.json"
    if not test_templates_path.exists():
        test_templates_path = None
    
    return ConversationEngine(templates_path=test_templates_path)


@pytest.fixture
def sample_buyer():
    """Fixture que proporciona un comprador de ejemplo"""
    return Buyer(
        id="test_buyer_123",
        username="compradortest",
        valoraciones=15,
        num_compras=5,
        distancia_km=10.5,
        ultima_actividad=datetime.now(),
        perfil_verificado=True,
        tiene_foto=True
    )


@pytest.fixture
def new_buyer():
    """Fixture que proporciona un comprador nuevo (potencial fraude)"""
    return Buyer(
        id="new_buyer_456",
        username="usuario_nuevo",
        valoraciones=0,
        num_compras=0,
        distancia_km=850.0,
        ultima_actividad=datetime.now(),
        perfil_verificado=False,
        tiene_foto=False
    )


@pytest.fixture
def sample_product():
    """Fixture que proporciona un producto de ejemplo"""
    return Product(
        id="prod_123",
        titulo="iPhone 12 128GB",
        precio=450.0,
        precio_minimo=400.0,
        descripcion="iPhone 12 en perfecto estado, con caja y cargador",
        estado="Como nuevo",
        categoria="Móviles y Telefonía",
        permite_envio=True,
        zona="Centro Madrid"
    )


@pytest.fixture
def test_messages():
    """Fixture que proporciona mensajes de prueba categorizados"""
    return {
        "saludos": [
            "Hola, está disponible?",
            "Buenas tardes, sigue en venta?",
            "Hey! Me interesa el producto"
        ],
        "negociacion": [
            "Cuánto es lo menos que aceptas?",
            "Te doy 200€ en mano ahora mismo",
            "Puedes hacer descuento?"
        ],
        "fraude": [
            "Dame tu whatsapp para hablar mejor",
            "Pago por western union, mi hijo te recoge",
            "Entra en este link bit.ly/12345 para el pago"
        ],
        "compra_directa": [
            "Lo quiero, cuando podemos quedar?",
            "Me lo llevo, dime donde quedamos",
            "Lo compro ya mismo"
        ]
    }


@pytest.fixture
def mock_templates():
    """Fixture que proporciona templates simplificadas para tests"""
    return {
        "saludos": {
            "inicial": ["¡Hola! Sí, está disponible"],
            "respuesta": ["Hola, ¿qué tal?"]
        },
        "disponibilidad": {
            "disponible": ["Sí, está disponible"],
            "vendido": ["Lo siento, ya está vendido"]
        },
        "precio": {
            "informacion": ["El precio es {precio}€"]
        },
        "respuestas_seguridad": {
            "no_whatsapp": ["Prefiero hablar por Wallapop"],
            "sospecha_fraude": ["No me parece seguro"]
        },
        "variables_sistema": {
            "tiempo_respuesta": {
                "min": 1,
                "max": 2
            }
        }
    }


@pytest.fixture(autouse=True)
def reset_conversation_state(conversation_engine):
    """Resetea el estado de las conversaciones antes de cada test"""
    conversation_engine.conversations.clear()
    yield
    conversation_engine.conversations.clear()


# Markers para diferentes tipos de tests
def pytest_configure(config):
    """Registra markers personalizados"""
    config.addinivalue_line("markers", "unit: marca tests unitarios rápidos")
    config.addinivalue_line("markers", "integration: marca tests de integración")
    config.addinivalue_line("markers", "slow: marca tests lentos")
    config.addinivalue_line("markers", "scraper: marca tests de scraping")
    config.addinivalue_line("markers", "database: marca tests que requieren BD")