# test_conversation_engine.py
"""
Tests unitarios para el motor de conversaciones
"""

import pytest
from datetime import datetime, timedelta
from conversation_engine.engine import (
    ConversationEngine,
    ConversationState,
    IntentionType,
    BuyerPriority,
)


class TestConversationEngine:
    """Tests para la clase ConversationEngine"""

    @pytest.mark.unit
    def test_engine_initialization(self, conversation_engine):
        """Test que el motor se inicializa correctamente"""
        assert conversation_engine is not None
        assert isinstance(conversation_engine.conversations, dict)
        assert len(conversation_engine.conversations) == 0
        assert conversation_engine.fraud_patterns is not None
        assert conversation_engine.intention_keywords is not None

    @pytest.mark.unit
    def test_detect_intention_saludo(self, conversation_engine):
        """Test detección de intención de saludo"""
        messages = ["Hola, está disponible?", "Buenas tardes", "Hey! me interesa"]

        for msg in messages:
            intention = conversation_engine._detect_intention(msg.lower())
            assert intention == IntentionType.SALUDO

    @pytest.mark.unit
    def test_detect_intention_precio(self, conversation_engine):
        """Test detección de intención de precio"""
        messages = ["Cuánto cuesta?", "Qué precio tiene?", "Son 300€?"]

        for msg in messages:
            intention = conversation_engine._detect_intention(msg.lower())
            assert intention == IntentionType.PRECIO

    @pytest.mark.unit
    def test_detect_intention_fraude(self, conversation_engine):
        """Test detección de intención fraudulenta"""
        messages = [
            "Pago por western union",
            "Mi transportista lo recoge",
            "Dame tu whatsapp para verificar tarjeta",
        ]

        for msg in messages:
            intention = conversation_engine._detect_intention(msg.lower())
            assert intention == IntentionType.FRAUDE

    @pytest.mark.unit
    def test_calculate_priority_alta(self, conversation_engine, sample_buyer):
        """Test cálculo de prioridad alta"""
        # Compra directa siempre es prioridad alta
        priority = conversation_engine._calculate_priority(
            IntentionType.COMPRA_DIRECTA, sample_buyer, "lo quiero ya"
        )
        assert priority == BuyerPriority.ALTA

        # Pago inmediato
        priority = conversation_engine._calculate_priority(
            IntentionType.PAGO, sample_buyer, "te pago ahora mismo"
        )
        assert priority == BuyerPriority.ALTA

    @pytest.mark.unit
    def test_calculate_priority_baja(self, conversation_engine, new_buyer):
        """Test cálculo de prioridad baja"""
        # Usuario nuevo sin valoraciones
        priority = conversation_engine._calculate_priority(
            IntentionType.PRECIO, new_buyer, "cuánto cuesta?"
        )
        assert priority == BuyerPriority.BAJA

        # Intento de fraude
        priority = conversation_engine._calculate_priority(
            IntentionType.FRAUDE, new_buyer, "western union"
        )
        assert priority == BuyerPriority.BAJA

    @pytest.mark.unit
    def test_fraud_risk_calculation(self, conversation_engine, sample_buyer, new_buyer):
        """Test cálculo de riesgo de fraude"""
        # Usuario confiable con mensaje normal
        risk = conversation_engine._calculate_fraud_risk(
            "hola, está disponible?", sample_buyer
        )
        assert risk < 30

        # Usuario nuevo con mensaje sospechoso
        risk = conversation_engine._calculate_fraud_risk(
            "dame tu whatsapp para pagarte", new_buyer
        )
        assert risk > 70

        # URL sospechosa
        risk = conversation_engine._calculate_fraud_risk(
            "entra aquí bit.ly/pago123", sample_buyer
        )
        assert risk >= 40

    @pytest.mark.unit
    def test_conversation_state_transitions(
        self, conversation_engine, sample_buyer, sample_product
    ):
        """Test transiciones de estado de conversación"""
        buyer_id = sample_buyer.id

        # Estado inicial
        state = conversation_engine._detect_conversation_state(
            IntentionType.SALUDO, buyer_id
        )
        assert state == ConversationState.INICIAL

        # Transición a negociando
        state = conversation_engine._detect_conversation_state(
            IntentionType.NEGOCIACION, buyer_id
        )
        assert state == ConversationState.NEGOCIANDO

        # Transición a comprometido
        state = conversation_engine._detect_conversation_state(
            IntentionType.COMPRA_DIRECTA, buyer_id
        )
        assert state == ConversationState.COMPROMETIDO

    @pytest.mark.unit
    def test_analyze_message_complete(
        self, conversation_engine, sample_buyer, sample_product
    ):
        """Test análisis completo de mensaje"""
        # Mensaje normal
        analysis = conversation_engine.analyze_message(
            "Hola, está disponible el producto?", sample_buyer, sample_product
        )

        assert analysis["intention"] == IntentionType.SALUDO
        assert analysis["priority"] == BuyerPriority.MEDIA
        assert analysis["fraud_risk"] < 50
        assert analysis["state"] == ConversationState.INICIAL
        assert not analysis["requires_human"]

        # Mensaje fraudulento
        analysis = conversation_engine.analyze_message(
            "Dame tu whatsapp para pagarte por western union",
            sample_buyer,
            sample_product,
        )

        assert analysis["intention"] == IntentionType.FRAUDE
        assert analysis["fraud_risk"] >= 50  # Western union + whatsapp request = high risk
        assert analysis["requires_human"]

    @pytest.mark.unit
    def test_generate_response(self, conversation_engine, sample_buyer, sample_product):
        """Test generación de respuestas"""
        # Respuesta a saludo
        analysis = {
            "intention": IntentionType.SALUDO,
            "priority": BuyerPriority.MEDIA,
            "fraud_risk": 10,
            "state": ConversationState.INICIAL,
            "requires_human": False,
        }

        response = conversation_engine.generate_response(
            analysis, "Hola", sample_buyer, sample_product
        )

        assert response is not None
        assert len(response) > 0

        # Respuesta de seguridad para fraude
        analysis["fraud_risk"] = 80
        response = conversation_engine.generate_response(
            analysis, "dame tu whatsapp", sample_buyer, sample_product
        )

        assert response is not None
        assert "wallapop" in response.lower() or "seguro" in response.lower()

    @pytest.mark.unit
    def test_should_respond_timing(self, conversation_engine, sample_buyer):
        """Test timing de respuestas"""
        # Dentro de horario activo (simulado)
        last_message_time = datetime.now() - timedelta(minutes=2)

        # Mock de hora actual (día a las 15:00)
        import datetime as dt_module

        original_datetime = dt_module.datetime

        class MockDatetime:
            @classmethod
            def now(cls):
                return original_datetime(2024, 1, 15, 15, 0, 0)

        dt_module.datetime = MockDatetime

        should_respond = conversation_engine.should_respond(
            sample_buyer, last_message_time
        )

        assert should_respond

        # Restaurar datetime
        dt_module.datetime = original_datetime

    @pytest.mark.unit
    def test_personalize_response(
        self, conversation_engine, sample_buyer, sample_product
    ):
        """Test personalización de respuestas"""
        template = "El precio de {producto} es {precio}€ y estoy en {zona}"

        personalized = conversation_engine._personalize_response(
            template, sample_product, sample_buyer
        )

        assert sample_product.titulo in personalized
        assert str(sample_product.precio) in personalized
        assert sample_product.zona in personalized

    @pytest.mark.unit
    def test_conversation_recovery(
        self, conversation_engine, sample_buyer, sample_product
    ):
        """Test recuperación de conversaciones abandonadas"""
        buyer_id = sample_buyer.id

        # Simular conversación abandonada
        conversation_engine.conversations[buyer_id] = {
            "state": ConversationState.ABANDONADO,
            "messages": 5,
            "last_activity": datetime.now() - timedelta(hours=25),
            "fraud_score": 0,
        }
        
        # Mock recovery templates for test  
        from unittest.mock import patch
        with patch.object(conversation_engine, '_get_recovery_message', return_value="Hola! ¿Sigues interesado en el producto?"):
            result = conversation_engine.handle_conversation_flow(
                buyer_id, [], sample_product
            )

        assert result["action"] == "recuperar"
        assert result["message"] is not None

    @pytest.mark.unit
    def test_get_conversation_summary(self, conversation_engine, sample_buyer):
        """Test resumen de conversación"""
        buyer_id = sample_buyer.id

        # Sin conversación
        summary = conversation_engine.get_conversation_summary(buyer_id)
        assert not summary["exists"]

        # Con conversación activa
        conversation_engine._detect_conversation_state(IntentionType.SALUDO, buyer_id)
        summary = conversation_engine.get_conversation_summary(buyer_id)

        assert summary["exists"]
        assert summary["state"] == ConversationState.INICIAL.value
        assert summary["messages_count"] == 1
        assert not summary["requires_attention"]
