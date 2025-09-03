# test_happy_path.py
"""
Test de integración para el Happy Path simple:
Recibir mensaje → Detectar saludo → Responder
"""

import pytest
from datetime import datetime
from conversation_engine.engine import (
    ConversationEngine,
    Buyer,
    Product,
    ConversationState,
    IntentionType,
)


class TestHappyPath:
    """Tests de integración para el flujo básico Happy Path"""

    @pytest.mark.integration
    def test_complete_happy_path_greeting(
        self, conversation_engine, sample_buyer, sample_product
    ):
        """Test del flujo completo para un saludo simple"""
        # 1. Mensaje de entrada
        incoming_message = "Hola, está disponible el iPhone?"

        # 2. Analizar mensaje
        analysis = conversation_engine.analyze_message(
            incoming_message, sample_buyer, sample_product
        )

        # Verificar análisis correcto
        assert analysis["intention"] == IntentionType.SALUDO
        assert analysis["state"] == ConversationState.INICIAL
        assert analysis["fraud_risk"] < 50
        assert not analysis["requires_human"]

        # 3. Generar respuesta
        response = conversation_engine.generate_response(
            analysis, incoming_message, sample_buyer, sample_product
        )

        # Verificar respuesta generada
        assert response is not None
        assert len(response) > 0
        assert "disponible" in response.lower() or "hola" in response.lower()

        # 4. Verificar estado de conversación
        summary = conversation_engine.get_conversation_summary(sample_buyer.id)
        assert summary["exists"]
        assert summary["state"] == ConversationState.INICIAL.value
        assert summary["messages_count"] == 1

    @pytest.mark.integration
    def test_happy_path_price_inquiry(
        self, conversation_engine, sample_buyer, sample_product
    ):
        """Test del flujo para consulta de precio"""
        # Primera interacción - saludo
        conversation_engine.analyze_message("Hola", sample_buyer, sample_product)

        # Segunda interacción - precio
        price_message = "Cuánto cuesta el iPhone?"
        analysis = conversation_engine.analyze_message(
            price_message, sample_buyer, sample_product
        )

        assert analysis["intention"] == IntentionType.PRECIO

        response = conversation_engine.generate_response(
            analysis, price_message, sample_buyer, sample_product
        )

        # Verificar que la respuesta incluye el precio
        assert response is not None
        assert str(sample_product.precio) in response or "precio" in response.lower()

    @pytest.mark.integration
    def test_happy_path_purchase_intent(
        self, conversation_engine, sample_buyer, sample_product
    ):
        """Test del flujo cuando el comprador quiere comprar"""
        # Flujo: Saludo → Precio → Compra
        messages = [
            ("Hola, está disponible?", IntentionType.SALUDO),
            ("Cuál es el precio?", IntentionType.PRECIO),
            ("Lo quiero, cuando podemos quedar?", IntentionType.COMPRA_DIRECTA),
        ]

        for msg, expected_intention in messages:
            analysis = conversation_engine.analyze_message(
                msg, sample_buyer, sample_product
            )

            assert analysis["intention"] == expected_intention

            response = conversation_engine.generate_response(
                analysis, msg, sample_buyer, sample_product
            )

            assert response is not None

        # Verificar que el estado final es COMPROMETIDO
        summary = conversation_engine.get_conversation_summary(sample_buyer.id)
        assert summary["state"] == ConversationState.COMPROMETIDO.value
        assert summary[
            "requires_attention"
        ]  # Requiere atención por ser venta comprometida

    @pytest.mark.integration
    def test_happy_path_fraud_detection(
        self, conversation_engine, new_buyer, sample_product
    ):
        """Test del flujo cuando se detecta posible fraude"""
        fraud_message = "Hola, dame tu whatsapp para pagarte por western union"

        analysis = conversation_engine.analyze_message(
            fraud_message, new_buyer, sample_product  # Usuario nuevo, más riesgo
        )

        # Verificar detección de fraude
        assert analysis["intention"] == IntentionType.FRAUDE
        assert analysis["fraud_risk"] > 70
        assert analysis["requires_human"]

        # Verificar respuesta de seguridad
        response = conversation_engine.generate_response(
            analysis, fraud_message, new_buyer, sample_product
        )

        assert response is not None
        assert any(
            word in response.lower() for word in ["wallapop", "seguro", "prefiero"]
        )

    @pytest.mark.integration
    def test_happy_path_negotiation_flow(
        self, conversation_engine, sample_buyer, sample_product
    ):
        """Test del flujo de negociación"""
        # Iniciar conversación
        conversation_engine.analyze_message(
            "Hola, me interesa el iPhone", sample_buyer, sample_product
        )

        # Intento de negociación
        negotiation_message = "Puedes dejarlo en 400€?"
        analysis = conversation_engine.analyze_message(
            negotiation_message, sample_buyer, sample_product
        )

        assert analysis["intention"] == IntentionType.NEGOCIACION
        assert analysis["state"] == ConversationState.NEGOCIANDO

        response = conversation_engine.generate_response(
            analysis, negotiation_message, sample_buyer, sample_product
        )

        assert response is not None
        # La respuesta debe mencionar precio o negociación
        assert any(
            word in response.lower() for word in ["precio", "€", "fijo", "menos"]
        )

    @pytest.mark.integration
    def test_happy_path_location_coordination(
        self, conversation_engine, sample_buyer, sample_product
    ):
        """Test del flujo de coordinación de entrega"""
        # Flujo hasta compromiso de compra
        conversation_engine.analyze_message("Hola", sample_buyer, sample_product)

        conversation_engine.analyze_message(
            "Lo quiero comprar", sample_buyer, sample_product
        )

        # Coordinar ubicación
        location_message = "Dónde podemos quedar?"
        analysis = conversation_engine.analyze_message(
            location_message, sample_buyer, sample_product
        )

        assert analysis["intention"] == IntentionType.UBICACION
        assert analysis["state"] == ConversationState.COORDINANDO

        response = conversation_engine.generate_response(
            analysis, location_message, sample_buyer, sample_product
        )

        assert response is not None
        assert sample_product.zona in response  # Debe mencionar la zona

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "message,expected_intention",
        [
            ("Está disponible?", IntentionType.DISPONIBILIDAD),
            ("En qué estado está?", IntentionType.ESTADO_PRODUCTO),
            ("Haces envíos?", IntentionType.ENVIO),
            ("Aceptas bizum?", IntentionType.PAGO),
            ("Necesito más información", IntentionType.INFORMACION),
        ],
    )
    def test_happy_path_various_intentions(
        self,
        conversation_engine,
        sample_buyer,
        sample_product,
        message,
        expected_intention,
    ):
        """Test parametrizado para varias intenciones"""
        analysis = conversation_engine.analyze_message(
            message, sample_buyer, sample_product
        )

        assert analysis["intention"] == expected_intention

        response = conversation_engine.generate_response(
            analysis, message, sample_buyer, sample_product
        )

        assert response is not None
        assert len(response) > 0
