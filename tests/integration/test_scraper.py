"""
Tests de integración comprehensivos para el scraper de Wallapop
Valida el funcionamiento completo del sistema de scraping
"""
import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

# Importar módulos del scraper
from src.scraper import (
    WallapopScraper, ScraperStatus, SessionManager, SessionStatus, 
    AuthMethod, MessageData, ConversationData, ProductData
)
from src.scraper.scraper_integration import ScraperIntegration
from src.scraper.anti_detection import anti_detection
from src.scraper.error_handler import error_handler, ErrorSeverity
from src.scraper.config import scraper_config


class TestScraperBasics:
    """Tests básicos del scraper"""
    
    @pytest.mark.asyncio
    async def test_scraper_initialization(self):
        """Test inicialización del scraper"""
        scraper = WallapopScraper(AuthMethod.COOKIES)
        
        assert scraper.status == ScraperStatus.STOPPED
        assert scraper.session_manager.auth_method == AuthMethod.COOKIES
        assert not scraper.is_running
        assert scraper.total_messages_processed == 0
    
    @pytest.mark.asyncio
    async def test_scraper_status_reporting(self):
        """Test reporte de estado del scraper"""
        scraper = WallapopScraper()
        status = scraper.get_status()
        
        assert "status" in status
        assert "is_running" in status
        assert "total_messages_processed" in status
        assert "session_info" in status
        
        assert status["status"] == ScraperStatus.STOPPED.value
        assert not status["is_running"]


class TestSessionManager:
    """Tests del gestor de sesiones"""
    
    @pytest.mark.asyncio
    async def test_session_manager_initialization(self):
        """Test inicialización del session manager"""
        session_manager = SessionManager(AuthMethod.AUTO)
        
        assert session_manager.auth_method == AuthMethod.AUTO
        assert session_manager.current_session is None
        assert session_manager.login_attempts == 0
    
    @pytest.mark.asyncio
    async def test_session_info_creation(self):
        """Test creación de información de sesión"""
        from src.scraper.session_manager import SessionInfo
        
        session_info = SessionInfo(
            status=SessionStatus.AUTHENTICATED,
            auth_method=AuthMethod.COOKIES,
            username="test_user",
            login_time=datetime.now()
        )
        
        assert session_info.status == SessionStatus.AUTHENTICATED
        assert session_info.auth_method == AuthMethod.COOKIES
        assert session_info.username == "test_user"
        assert session_info.login_time is not None


class TestAntiDetection:
    """Tests del sistema anti-detección"""
    
    @pytest.mark.asyncio
    async def test_fingerprint_generation(self):
        """Test generación de fingerprints"""
        fingerprint = anti_detection._generate_realistic_fingerprint()
        
        assert fingerprint.user_agent is not None
        assert fingerprint.viewport is not None
        assert fingerprint.screen_resolution is not None
        assert fingerprint.timezone in ["Europe/Madrid", "Europe/Barcelona", "Europe/Valencia"]
        assert fingerprint.canvas_fingerprint is not None
    
    def test_human_delay_generation(self):
        """Test generación de delays humanos"""
        delay = scraper_config.get_human_delay()
        
        assert isinstance(delay, float)
        assert scraper_config.MIN_DELAY <= delay <= scraper_config.MAX_DELAY + 5  # +5 para variaciones
    
    def test_typing_delay_calculation(self):
        """Test cálculo de delay de escritura"""
        text = "Hola, ¿está disponible el producto?"
        delay = scraper_config.get_typing_delay(len(text))
        
        assert isinstance(delay, float)
        assert delay > 0
        # Para texto de ~35 caracteres, debería tomar entre 5-25 segundos
        assert 5 <= delay <= 25


class TestErrorHandler:
    """Tests del manejador de errores"""
    
    def test_error_recording(self):
        """Test registro de errores"""
        initial_count = len(error_handler.error_history)
        
        test_error = Exception("Test error")
        error_handler.record_error(test_error, {"test": "context"}, ErrorSeverity.MEDIUM)
        
        assert len(error_handler.error_history) == initial_count + 1
        
        latest_error = error_handler.error_history[-1]
        assert latest_error.error_type == "Exception"
        assert latest_error.message == "Test error"
        assert latest_error.severity == ErrorSeverity.MEDIUM
        assert latest_error.context["test"] == "context"
    
    def test_circuit_breaker_functionality(self):
        """Test funcionalidad del circuit breaker"""
        breaker_name = "test_breaker"
        
        # Verificar que el circuit breaker existe
        assert breaker_name in error_handler.circuit_breakers
        
        breaker = error_handler.circuit_breakers[breaker_name]
        
        # Estado inicial debe ser CLOSED
        assert breaker.state.value == "closed"
        assert breaker.can_execute()
        
        # Simular fallos
        for _ in range(breaker.config.failure_threshold):
            breaker.record_failure()
        
        # Después de suficientes fallos, debe estar OPEN
        assert breaker.state.value == "open"
        assert not breaker.can_execute()
    
    def test_error_statistics(self):
        """Test estadísticas de errores"""
        stats = error_handler.get_error_stats()
        
        assert "total_errors" in stats
        assert "error_types" in stats
        assert "severity_counts" in stats
        assert "circuit_breakers" in stats
        
        assert isinstance(stats["total_errors"], int)
        assert isinstance(stats["error_types"], dict)
        assert isinstance(stats["circuit_breakers"], dict)


class TestDataStructures:
    """Tests de estructuras de datos"""
    
    def test_message_data_creation(self):
        """Test creación de MessageData"""
        message = MessageData(
            id="msg_123",
            conversation_id="conv_456",
            sender_id="user_789",
            sender_name="Test User",
            content="Hola, ¿está disponible?",
            timestamp=datetime.now(),
            is_read=True,
            is_from_me=False
        )
        
        assert message.id == "msg_123"
        assert message.conversation_id == "conv_456"
        assert message.sender_name == "Test User"
        assert not message.is_from_me
    
    def test_conversation_data_creation(self):
        """Test creación de ConversationData"""
        conversation = ConversationData(
            id="conv_123",
            buyer_id="buyer_456",
            buyer_name="Test Buyer",
            product_id="product_789",
            product_title="iPhone 12",
            last_message=None,
            unread_count=2,
            last_activity=datetime.now(),
            status="active"
        )
        
        assert conversation.id == "conv_123"
        assert conversation.buyer_name == "Test Buyer"
        assert conversation.product_title == "iPhone 12"
        assert conversation.unread_count == 2
    
    def test_product_data_creation(self):
        """Test creación de ProductData"""
        product = ProductData(
            id="product_123",
            title="iPhone 12 Pro",
            price=650.0,
            description="En perfecto estado",
            condition="like_new",
            location="Madrid",
            images=["img1.jpg", "img2.jpg"],
            views=150,
            favorites=25,
            is_active=True
        )
        
        assert product.id == "product_123"
        assert product.title == "iPhone 12 Pro"
        assert product.price == 650.0
        assert len(product.images) == 2
        assert product.is_active


class TestUtilities:
    """Tests de utilidades"""
    
    def test_text_cleaner(self):
        """Test limpiador de texto"""
        from src.scraper.utils import TextCleaner
        
        # Test limpieza de mensaje
        dirty_text = "  Hola!!!   ¿está disponible?  \n\n  "
        clean_text = TextCleaner.clean_message_text(dirty_text)
        
        assert clean_text == "Hola!!! ¿está disponible?"
        
        # Test extracción de precio
        price_texts = [
            "El precio es 150€",
            "€ 1.500,50",
            "Cuesta 2.300 euros",
            "1500 eur"
        ]
        
        expected_prices = [150.0, 1500.50, 2300.0, 1500.0]
        
        for text, expected in zip(price_texts, expected_prices):
            extracted = TextCleaner.extract_price(text)
            assert extracted == expected, f"Failed for '{text}': got {extracted}, expected {expected}"
        
        # Test normalización de username
        usernames = ["  TestUser123  ", "TESTUSER", "test_user"]
        for username in usernames:
            normalized = TextCleaner.normalize_username(username)
            assert normalized == normalized.lower().strip()
    
    def test_data_validator(self):
        """Test validador de datos"""
        from src.scraper.utils import DataValidator
        
        # Test validación de email
        valid_emails = ["test@example.com", "user.name@domain.co.uk"]
        invalid_emails = ["invalid-email", "@domain.com", "user@"]
        
        for email in valid_emails:
            assert DataValidator.is_valid_email(email), f"Should be valid: {email}"
        
        for email in invalid_emails:
            assert not DataValidator.is_valid_email(email), f"Should be invalid: {email}"
        
        # Test validación de teléfono español
        valid_phones = ["+34 666 777 888", "666777888", "7555551234"]
        invalid_phones = ["123456", "+1 555 123 4567", "555-1234"]
        
        for phone in valid_phones:
            assert DataValidator.is_valid_phone(phone), f"Should be valid: {phone}"
        
        for phone in invalid_phones:
            assert not DataValidator.is_valid_phone(phone), f"Should be invalid: {phone}"
    
    def test_conversation_analyzer(self):
        """Test analizador de conversaciones"""
        from src.scraper.utils import ConversationAnalyzer
        
        # Test detección de urgencia
        urgent_messages = [
            "¡Es urgente! Lo necesito hoy",
            "¿Puedes responder rápido?",
            "Lo quiero ya!!!"
        ]
        
        normal_messages = [
            "Hola, ¿está disponible?",
            "Me interesa el producto",
            "¿Cuál es el precio?"
        ]
        
        for msg in urgent_messages:
            urgency = ConversationAnalyzer.detect_urgency(msg)
            assert urgency > 0.5, f"Should detect urgency in: {msg}"
        
        for msg in normal_messages:
            urgency = ConversationAnalyzer.detect_urgency(msg)
            assert urgency <= 0.3, f"Should not detect urgency in: {msg}"
        
        # Test detección de intención de compra
        purchase_messages = [
            "Lo quiero, ¿cuándo puedo recogerlo?",
            "Me lo llevo, ¿dónde quedamos?",
            "¿Aceptas Bizum?"
        ]
        
        for msg in purchase_messages:
            intent = ConversationAnalyzer.detect_purchase_intent(msg)
            assert intent > 0.6, f"Should detect purchase intent in: {msg}"


class TestConfiguration:
    """Tests de configuración"""
    
    def test_scraper_config_defaults(self):
        """Test valores por defecto de configuración"""
        assert scraper_config.MIN_DELAY >= 30
        assert scraper_config.MAX_DELAY >= scraper_config.MIN_DELAY
        assert scraper_config.MAX_CONCURRENT_CONVERSATIONS > 0
        assert scraper_config.ACTIVE_HOURS_START < scraper_config.ACTIVE_HOURS_END
    
    def test_user_agent_rotation(self):
        """Test rotación de user agents"""
        agents = set()
        
        # Generar varios user agents
        for _ in range(10):
            agent = scraper_config.get_random_user_agent()
            agents.add(agent)
        
        # Debe haber variedad (al menos 2 diferentes en 10 intentos)
        assert len(agents) >= 2
        
        # Todos deben ser válidos
        for agent in agents:
            assert "Mozilla" in agent
            assert "Chrome" in agent or "Firefox" in agent or "Safari" in agent
    
    def test_active_hours_checking(self):
        """Test verificación de horario activo"""
        # Mock datetime para probar diferentes horas
        with patch('src.scraper.config.datetime') as mock_datetime:
            # Hora activa (14:00)
            mock_datetime.now.return_value.hour = 14
            assert scraper_config.is_within_active_hours()
            
            # Hora inactiva (3:00)
            mock_datetime.now.return_value.hour = 3
            assert not scraper_config.is_within_active_hours()


@pytest.mark.integration
class TestScraperIntegration:
    """Tests de integración completa"""
    
    @pytest.mark.asyncio
    async def test_integration_initialization(self):
        """Test inicialización del integrador"""
        with patch('src.scraper.scraper_integration.DatabaseManager') as mock_db:
            mock_db.return_value.init_db = AsyncMock()
            
            integration = ScraperIntegration(AuthMethod.COOKIES)
            
            assert integration.scraper is not None
            assert integration.conversation_engine is not None
            assert not integration.is_running
    
    @pytest.mark.asyncio
    async def test_mock_message_processing(self):
        """Test procesamiento de mensajes con mocks"""
        with patch('src.scraper.scraper_integration.DatabaseManager') as mock_db:
            # Configurar mocks
            mock_db.return_value.init_db = AsyncMock()
            mock_conversation = Mock()
            mock_conversation.id = 1
            mock_conversation.buyer_id = 1
            mock_conversation.product_id = 1
            
            integration = ScraperIntegration()
            
            # Crear mensaje de prueba
            test_message = MessageData(
                id="test_msg_1",
                conversation_id="test_conv_1",
                sender_id="test_buyer",
                sender_name="Test Buyer",
                content="Hola, ¿está disponible el producto?",
                timestamp=datetime.now(),
                is_read=False,
                is_from_me=False
            )
            
            # Mock métodos necesarios
            with patch.object(integration, '_save_message_to_db', return_value=AsyncMock()):
                with patch.object(integration, '_create_buyer_object'):
                    with patch.object(integration, '_create_product_object'):
                        with patch.object(integration.scraper, 'send_message', return_value=True):
                            with patch.object(integration, '_save_response_to_db'):
                                result = await integration._process_single_message(test_message, mock_conversation)
                                
                                # Verificar que el procesamiento fue exitoso
                                assert result.success


@pytest.mark.performance
class TestPerformance:
    """Tests de rendimiento"""
    
    def test_delay_generation_performance(self):
        """Test rendimiento de generación de delays"""
        start_time = time.time()
        
        # Generar 1000 delays
        delays = []
        for _ in range(1000):
            delay = scraper_config.get_human_delay()
            delays.append(delay)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Debe ser rápido (menos de 1 segundo para 1000 delays)
        assert generation_time < 1.0
        
        # Verificar variedad
        unique_delays = set(delays)
        assert len(unique_delays) > 500  # Debe haber buena variedad
    
    def test_text_processing_performance(self):
        """Test rendimiento de procesamiento de texto"""
        from src.scraper.utils import TextCleaner
        
        # Texto largo
        long_text = "Hola! " * 1000 + "¿Está disponible por 150€?"
        
        start_time = time.time()
        
        # Procesar 100 veces
        for _ in range(100):
            cleaned = TextCleaner.clean_message_text(long_text)
            price = TextCleaner.extract_price(cleaned)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Debe ser razonable (menos de 1 segundo)
        assert processing_time < 1.0


class TestRealWorldScenarios:
    """Tests de escenarios del mundo real"""
    
    def test_suspicious_message_detection(self):
        """Test detección de mensajes sospechosos"""
        from src.scraper.utils import DataValidator
        
        suspicious_messages = [
            "Envío por Western Union",
            "Mi transportista lo recogerá",
            "Pago por PayPal familia",
            "Necesito tu WhatsApp",
            "Envía a este link: http://bit.ly/scam"
        ]
        
        legitimate_messages = [
            "Hola, ¿está disponible?",
            "¿Puedo recogerlo en persona?",
            "¿Aceptas Bizum?",
            "¿En qué zona estás?",
            "Me interesa mucho el producto"
        ]
        
        for msg in suspicious_messages:
            assert DataValidator.is_suspicious_message(msg), f"Should detect as suspicious: {msg}"
        
        for msg in legitimate_messages:
            assert not DataValidator.is_suspicious_message(msg), f"Should NOT detect as suspicious: {msg}"
    
    def test_conversation_flow_simulation(self):
        """Test simulación de flujo de conversación"""
        from src.conversation_engine.engine import ConversationEngine, Buyer, Product
        from datetime import datetime
        
        # Crear objetos de test
        engine = ConversationEngine()
        
        buyer = Buyer(
            id="buyer_123",
            username="test_buyer",
            valoraciones=5,
            num_compras=3,
            distancia_km=15.0,
            ultima_actividad=datetime.now(),
            perfil_verificado=True,
            tiene_foto=True
        )
        
        product = Product(
            id="product_456",
            titulo="iPhone 12",
            precio=650.0,
            precio_minimo=600.0,
            descripcion="En perfecto estado",
            estado="como nuevo",
            categoria="móviles",
            permite_envio=True,
            zona="Madrid"
        )
        
        # Simular secuencia de mensajes
        messages = [
            "Hola, ¿está disponible?",
            "¿Cuál es el precio final?",
            "¿Puedo recogerlo hoy?",
            "Lo quiero, ¿dónde quedamos?"
        ]
        
        responses = []
        
        for message in messages:
            analysis = engine.analyze_message(message, buyer, product)
            response = engine.generate_response(analysis, message, buyer, product)
            
            if response:
                responses.append(response)
        
        # Verificar que se generaron respuestas
        assert len(responses) > 0
        
        # Verificar que las respuestas contienen información del producto
        product_mentioned = any(product.titulo.lower() in resp.lower() for resp in responses)
        price_mentioned = any(str(int(product.precio)) in resp for resp in responses)
        
        # Al menos una respuesta debe mencionar el producto o precio
        assert product_mentioned or price_mentioned


# Fixtures globales para tests
@pytest.fixture
def mock_browser_context():
    """Mock de contexto de navegador"""
    context = AsyncMock()
    context.cookies.return_value = []
    context.new_page.return_value = AsyncMock()
    return context


@pytest.fixture
def sample_conversation_data():
    """Datos de conversación de ejemplo"""
    return ConversationData(
        id="conv_test_123",
        buyer_id="buyer_test_456",
        buyer_name="Test Buyer",
        product_id="product_test_789",
        product_title="Test Product",
        last_message=None,
        unread_count=1,
        last_activity=datetime.now(),
        status="active"
    )


@pytest.fixture
def sample_message_data():
    """Datos de mensaje de ejemplo"""
    return MessageData(
        id="msg_test_123",
        conversation_id="conv_test_456",
        sender_id="buyer_test_789",
        sender_name="Test Buyer",
        content="Hola, ¿está disponible el producto?",
        timestamp=datetime.now(),
        is_read=False,
        is_from_me=False
    )


if __name__ == "__main__":
    # Ejecutar tests básicos si se ejecuta directamente
    pytest.main([__file__, "-v"])