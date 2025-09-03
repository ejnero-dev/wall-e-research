# 🔧 Wall-E API Reference

Complete API documentation for the Wall-E Wallapop automation system with AI Engine integration.

---

## 📋 Table of Contents

- [🌟 Overview](#-overview)
- [🤖 AI Engine API](#-ai-engine-api)
- [💬 Conversation Engine API](#-conversation-engine-api)
- [🛡️ Security & Validation API](#️-security--validation-api)
- [📊 Performance Monitoring API](#-performance-monitoring-api)
- [🔧 Configuration API](#-configuration-api)
- [💰 Price Analysis API](#-price-analysis-api)
- [🕷️ Scraper API](#️-scraper-api)
- [🌐 REST API Endpoints](#-rest-api-endpoints)
- [📚 Data Models](#-data-models)
- [⚠️ Error Handling](#️-error-handling)

---

## 🌟 Overview

### API Design Principles

**Consistency:** All APIs follow consistent naming conventions and response formats  
**Type Safety:** Full type annotations with runtime validation  
**Async Support:** Native async/await for high-performance operations  
**Error Handling:** Comprehensive exception hierarchy with detailed error information  
**Extensibility:** Plugin architecture for custom functionality  

### Authentication & Security

**No External API Keys Required:** All AI processing runs locally  
**Internal Security:** Multi-layer fraud detection and validation  
**Rate Limiting:** Configurable request throttling  
**Audit Logging:** Complete request/response tracking for compliance  

### Response Format

All APIs return consistent response objects:
```python
@dataclass
class APIResponse:
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

---

## 🤖 AI Engine API

### Core Classes

#### AIEngine

**Main orchestrator for AI-powered conversation generation.**

```python
from src.ai_engine import AIEngine, AIEngineConfig
from src.ai_engine.ai_engine import ConversationRequest, ConversationResponse

class AIEngine:
    def __init__(self, config: AIEngineConfig) -> None
    async def initialize(self) -> None
    def generate_response(self, request: ConversationRequest) -> ConversationResponse
    async def generate_response_async(self, request: ConversationRequest) -> ConversationResponse
    def get_status(self) -> EngineStatus
    def get_performance_stats(self) -> Dict[str, Any]
    async def test_engine_async(self) -> Dict[str, Any]
    async def warm_up(self) -> None
    async def shutdown(self) -> None
```

**Methods:**

##### `__init__(config: AIEngineConfig)`
Initialize AI Engine with configuration.

**Parameters:**
- `config` (AIEngineConfig): Configuration object with AI Engine settings

**Raises:**
- `ConfigurationError`: Invalid configuration parameters
- `ModelNotAvailableError`: Required AI model not found

**Example:**
```python
config = AIEngineConfig.for_research()
engine = AIEngine(config)
```

##### `async initialize()`
Initialize AI Engine components asynchronously.

**Returns:** None

**Raises:**
- `InitializationError`: Failed to initialize components
- `OllamaConnectionError`: Cannot connect to Ollama server

**Example:**
```python
await engine.initialize()
```

##### `generate_response(request: ConversationRequest) -> ConversationResponse`
Generate AI-powered conversation response (synchronous).

**Parameters:**
- `request` (ConversationRequest): Conversation request object

**Returns:** ConversationResponse with generated text and metadata

**Raises:**
- `GenerationError`: AI generation failed
- `ValidationError`: Security validation failed
- `TimeoutError`: Generation exceeded timeout

**Example:**
```python
request = ConversationRequest(
    buyer_message="¡Hola! ¿Está disponible?",
    buyer_name="TestBuyer",
    product_name="iPhone 12",
    price=400
)

response = engine.generate_response(request)
print(f"Response: {response.response_text}")
print(f"Risk Score: {response.risk_score}")
```

##### `async generate_response_async(request: ConversationRequest) -> ConversationResponse`
Generate AI-powered conversation response (asynchronous).

**Parameters:**
- `request` (ConversationRequest): Conversation request object

**Returns:** ConversationResponse with generated text and metadata

**Raises:**
- `GenerationError`: AI generation failed
- `ValidationError`: Security validation failed
- `TimeoutError`: Generation exceeded timeout

**Example:**
```python
response = await engine.generate_response_async(request)
```

##### `get_status() -> EngineStatus`
Get current AI Engine status.

**Returns:** EngineStatus enum value

**Possible Values:**
- `EngineStatus.INITIALIZING`: Engine starting up
- `EngineStatus.READY`: Ready for requests
- `EngineStatus.BUSY`: Processing requests
- `EngineStatus.ERROR`: Error state
- `EngineStatus.MAINTENANCE`: Maintenance mode

**Example:**
```python
status = engine.get_status()
if status == EngineStatus.READY:
    print("Engine ready for requests")
```

##### `get_performance_stats() -> Dict[str, Any]`
Get detailed performance statistics.

**Returns:** Dictionary with performance metrics

**Response Format:**
```python
{
    "requests_processed": 1250,
    "average_response_time": 2.34,
    "success_rate": 0.997,
    "memory_usage_mb": 6840,
    "cache_hit_rate": 0.45,
    "uptime_seconds": 86400,
    "generation_stats": {
        "ai_generated": 1100,
        "template_fallback": 150,
        "fraud_blocked": 25
    },
    "llm_stats": {
        "model_name": "llama3.2:11b-vision-instruct-q4_0",
        "avg_inference_time": 1.8,
        "cache": {
            "hits": 450,
            "misses": 800,
            "hit_rate": 0.36
        }
    }
}
```

##### `async test_engine_async() -> Dict[str, Any]`
Comprehensive engine testing and validation.

**Returns:** Dictionary with test results

**Response Format:**
```python
{
    "engine_status": "ready",
    "ollama_connection": "connected",
    "model_available": True,
    "test_generation": {
        "success": True,
        "response_time": 1.85,
        "response_text": "Test response generated successfully"
    },
    "security_validation": {
        "fraud_detection": "active",
        "patterns_loaded": 156
    },
    "performance": {
        "memory_usage_mb": 6200,
        "cache_size": 450
    }
}
```

#### ConversationRequest

**Input data structure for conversation generation.**

```python
@dataclass
class ConversationRequest:
    # Required fields
    buyer_message: str
    buyer_name: str
    product_name: str
    price: float
    
    # Optional fields with defaults
    conversation_history: List[Dict] = field(default_factory=list)
    buyer_profile: Optional[Dict] = None
    personality: str = "profesional_cordial"
    condition: str = "buen estado"
    location: str = "Madrid"
    require_validation: bool = True
    max_retries: int = 3
    
    # Advanced options
    custom_context: Optional[Dict] = None
    force_personality: bool = False
    disable_fallback: bool = False
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `buyer_message` | str | ✅ | The buyer's message to respond to |
| `buyer_name` | str | ✅ | Buyer's name or identifier |
| `product_name` | str | ✅ | Name of the product being sold |
| `price` | float | ✅ | Product price in euros |
| `conversation_history` | List[Dict] | ❌ | Previous messages in conversation |
| `buyer_profile` | Dict | ❌ | Buyer profile information |
| `personality` | str | ❌ | Seller personality to use |
| `condition` | str | ❌ | Product condition |
| `location` | str | ❌ | Seller location |
| `require_validation` | bool | ❌ | Enable fraud detection |
| `max_retries` | int | ❌ | Maximum generation retries |

**Example Usage:**
```python
# Basic request
request = ConversationRequest(
    buyer_message="¿Acepta cambios?",
    buyer_name="CompradirInteresado",
    product_name="MacBook Pro 2019",
    price=750
)

# Advanced request with buyer profile
request = ConversationRequest(
    buyer_message="¿Es negociable el precio?",
    buyer_name="CompradirExperimentado",
    product_name="iPhone 13",
    price=550,
    conversation_history=[
        {"role": "buyer", "message": "¿Está disponible?", "timestamp": "2025-01-16T10:00:00Z"},
        {"role": "seller", "message": "Sí, disponible", "timestamp": "2025-01-16T10:01:00Z"}
    ],
    buyer_profile={
        "ratings_count": 25,
        "avg_rating": 4.8,
        "account_age": 365,
        "distance": 15,
        "successful_purchases": 12,
        "preferred_categories": ["electronics", "technology"]
    },
    personality="vendedor_experimentado",
    condition="muy buen estado",
    location="Barcelona"
)
```

#### ConversationResponse

**Output data structure with generated response and metadata.**

```python
@dataclass
class ConversationResponse:
    # Core response
    response_text: str
    confidence: float
    risk_score: int
    source: str
    
    # Performance metrics
    response_time: float
    generation_time: float
    validation_time: float
    
    # AI details
    personality_used: str
    model_name: str
    temperature_used: float
    tokens_generated: int
    
    # Security details
    validation_result: ValidationResult
    
    # Metadata
    metadata: Dict[str, Any]
    timestamp: datetime
    request_id: str
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `response_text` | str | Generated response text |
| `confidence` | float | Response quality score (0.0-1.0) |
| `risk_score` | int | Fraud risk score (0-100) |
| `source` | str | Response source: "ai_engine", "template", "fraud_protection" |
| `response_time` | float | Total response time in seconds |
| `generation_time` | float | AI generation time in seconds |
| `validation_time` | float | Security validation time in seconds |
| `personality_used` | str | Actual personality used |
| `model_name` | str | AI model used for generation |
| `validation_result` | ValidationResult | Detailed security analysis |
| `metadata` | Dict | Additional context and debugging info |

**Response Analysis Example:**
```python
response = engine.generate_response(request)

# Quality assessment
if response.confidence > 0.8:
    quality = "High"
elif response.confidence > 0.6:
    quality = "Good"
else:
    quality = "Template fallback"

# Security assessment
if response.risk_score > 50:
    security = "High risk - blocked"
elif response.risk_score > 25:
    security = "Medium risk - monitored"
else:
    security = "Safe"

# Performance assessment
if response.response_time < 2.0:
    performance = "Excellent"
elif response.response_time < 3.0:
    performance = "Good"
else:
    performance = "Needs optimization"

print(f"Quality: {quality} | Security: {security} | Performance: {performance}")
```

### Configuration API

#### AIEngineConfig

**Comprehensive configuration management.**

```python
from src.ai_engine.config import AIEngineConfig, AIEngineMode

class AIEngineConfig:
    # Factory methods
    @classmethod
    def for_research(cls) -> 'AIEngineConfig'
    @classmethod
    def for_compliance(cls) -> 'AIEngineConfig'
    @classmethod
    def for_hardware(cls, ram_gb: int = None, cpu_cores: int = None) -> 'AIEngineConfig'
    
    # File operations
    @classmethod
    def from_file(cls, file_path: str) -> 'AIEngineConfig'
    @classmethod
    def from_env(cls) -> 'AIEngineConfig'
    def save_to_file(self, file_path: str) -> None
    def to_dict(self) -> Dict[str, Any]
    
    # Validation
    def validate(self) -> None
    def get_validation_errors(self) -> List[str]
    def update_from_env(self) -> None
```

**Factory Methods:**

##### `for_research() -> AIEngineConfig`
Create configuration optimized for research and development.

**Returns:** AIEngineConfig with research-friendly settings

**Configuration:**
- `mode`: AI_FIRST
- `fraud_detection_threshold`: 25 (balanced)
- `debug_mode`: True
- `enable_profiling`: True
- `strict_validation`: False

**Example:**
```python
config = AIEngineConfig.for_research()
```

##### `for_compliance() -> AIEngineConfig`
Create configuration optimized for commercial compliance.

**Returns:** AIEngineConfig with compliance-focused settings

**Configuration:**
- `mode`: AI_FIRST
- `fraud_detection_threshold`: 20 (stricter)
- `audit_all_responses`: True
- `strict_validation`: True
- `debug_mode`: False

**Example:**
```python
config = AIEngineConfig.for_compliance()
```

##### `for_hardware(ram_gb: int = None, cpu_cores: int = None) -> AIEngineConfig`
Create hardware-optimized configuration.

**Parameters:**
- `ram_gb` (int, optional): Available RAM in GB (auto-detected if None)
- `cpu_cores` (int, optional): CPU cores (auto-detected if None)

**Returns:** AIEngineConfig optimized for detected/specified hardware

**Auto-Detection Example:**
```python
# Auto-detect hardware and optimize
config = AIEngineConfig.for_hardware()

# Manual hardware specification
config = AIEngineConfig.for_hardware(ram_gb=16, cpu_cores=8)
```

**Configuration Properties:**

```python
# Core AI settings
config.mode: AIEngineMode                    # Operation mode
config.model_name: str                       # LLM model name
config.temperature: float                    # Generation creativity (0.0-1.0)
config.max_tokens: int                       # Maximum response length
config.timeout: int                          # Generation timeout (seconds)

# Performance settings
config.max_concurrent_requests: int          # Concurrent request limit
config.connection_pool_size: int             # Ollama connection pool size
config.thread_pool_size: int                 # Worker thread count
config.memory_threshold_mb: int              # Memory usage threshold

# Caching settings
config.enable_caching: bool                  # Enable response caching
config.cache_size: int                       # Local cache entries
config.cache_ttl: int                        # Cache TTL (seconds)
config.redis_host: str                       # Redis server host
config.redis_port: int                       # Redis server port

# Security settings
config.fraud_detection_threshold: int        # Risk score threshold (0-100)
config.critical_fraud_threshold: int         # Critical risk threshold
config.enable_url_analysis: bool            # Enable URL threat detection
config.enable_pattern_matching: bool        # Enable pattern matching
config.strict_validation: bool              # Enable strict validation

# Personality settings
config.default_personality: str             # Default seller personality
config.adaptive_personality: bool           # Enable adaptive selection
config.custom_personalities: Dict           # Custom personality definitions

# Debug settings
config.debug_mode: bool                      # Enable debug logging
config.log_level: str                        # Logging level
config.enable_profiling: bool               # Enable performance profiling
config.save_prompts: bool                    # Save prompts for analysis
config.save_responses: bool                  # Save responses for analysis
```

### Personality Management

#### Available Personalities

```python
from src.ai_engine.prompt_templates import SpanishPromptTemplates

templates = SpanishPromptTemplates()

# Get available personalities
personalities = templates.get_available_personalities()
print(personalities)
# Output: ["amigable_casual", "profesional_cordial", "vendedor_experimentado"]

# Get personality details
details = templates.get_personality_details("amigable_casual")
print(details)
# Output: {
#     "name": "amigable_casual",
#     "description": "Informal, friendly, moderate emojis",
#     "tone": "casual",
#     "formality": "informal",
#     "emoji_usage": "moderate"
# }
```

#### Custom Personality Creation

```python
# Define custom personality
config.custom_personalities = {
    "technical_expert": {
        "name": "Experto Técnico",
        "description": "Technical expert with detailed knowledge",
        "tone": "knowledgeable, precise, helpful",
        "style": "technical but accessible",
        "examples": [
            "Las especificaciones técnicas confirman...",
            "Según el análisis técnico...",
            "Los componentes incluyen..."
        ],
        "guidelines": [
            "Use technical terminology when appropriate",
            "Provide detailed specifications",
            "Reference technical documentation",
            "Maintain professional credibility"
        ]
    }
}

# Use custom personality
request = ConversationRequest(
    buyer_message="¿Qué procesador tiene?",
    buyer_name="TechBuyer",
    product_name="MacBook Pro",
    price=1200,
    personality="technical_expert"
)
```

---

## 💬 Conversation Engine API

### Enhanced Conversation Engine

#### AIEnhancedConversationEngine

**AI-powered conversation management with traditional compatibility.**

```python
from src.conversation_engine.ai_enhanced_engine import AIEnhancedConversationEngine
from src.ai_engine.config import AIEngineConfig

class AIEnhancedConversationEngine:
    def __init__(self, ai_config: AIEngineConfig = None) -> None
    async def initialize(self) -> None
    async def analyze_and_respond(self, message: str, buyer: Dict, product: Dict) -> ConversationResult
    def get_conversation_state(self, conversation_id: str) -> ConversationState
    def update_conversation_state(self, conversation_id: str, new_state: ConversationState) -> None
    def get_conversation_history(self, conversation_id: str) -> List[Dict]
    async def shutdown(self) -> None
```

**Methods:**

##### `__init__(ai_config: AIEngineConfig = None)`
Initialize enhanced conversation engine.

**Parameters:**
- `ai_config` (AIEngineConfig, optional): AI Engine configuration. Uses default if None.

**Example:**
```python
config = AIEngineConfig.for_compliance()
engine = AIEnhancedConversationEngine(ai_config=config)
```

##### `async analyze_and_respond(message: str, buyer: Dict, product: Dict) -> ConversationResult`
Analyze message and generate AI-powered response.

**Parameters:**
- `message` (str): Buyer's message
- `buyer` (Dict): Buyer profile information
- `product` (Dict): Product information

**Returns:** ConversationResult with response and analysis

**Example:**
```python
buyer = {
    "name": "Juan García",
    "rating": 4.5,
    "ratings_count": 18,
    "location": "Madrid",
    "distance": 12
}

product = {
    "name": "iPhone 12",
    "price": 450,
    "condition": "muy buen estado",
    "category": "electronics"
}

result = await engine.analyze_and_respond(
    message="¿Acepta 400€?",
    buyer=buyer,
    product=product
)

print(f"Response: {result.response}")
print(f"Confidence: {result.confidence}")
print(f"Risk Level: {result.risk_level}")
print(f"New State: {result.new_state}")
```

#### ConversationResult

**Enhanced result object with AI insights.**

```python
@dataclass
class ConversationResult:
    # Traditional fields
    response: str
    new_state: ConversationState
    buyer_intent: str
    confidence: float
    
    # AI enhancements
    ai_confidence: float
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    risk_score: int
    personality_used: str
    response_source: str
    
    # Analysis details
    intent_analysis: Dict[str, Any]
    fraud_analysis: Dict[str, Any]
    conversation_insights: Dict[str, Any]
    
    # Performance metrics
    processing_time: float
    ai_generation_time: float
    analysis_time: float
```

### Conversation State Management

#### ConversationState

**Conversation state enumeration.**

```python
from enum import Enum

class ConversationState(Enum):
    INICIAL = "inicial"                    # Initial contact
    EXPLORANDO = "explorando"              # Exploring interest
    NEGOCIANDO = "negociando"              # Price negotiation
    COMPROMETIDO = "comprometido"          # Buyer committed
    COORDINANDO = "coordinando"            # Arranging meetup
    FINALIZADO = "finalizado"              # Sale completed
    ABANDONADO = "abandonado"              # Conversation abandoned
    BLOQUEADO = "bloqueado"                # Blocked (fraud)
```

#### State Transition Rules

```python
# Valid state transitions
VALID_TRANSITIONS = {
    ConversationState.INICIAL: [
        ConversationState.EXPLORANDO,
        ConversationState.NEGOCIANDO,
        ConversationState.BLOQUEADO
    ],
    ConversationState.EXPLORANDO: [
        ConversationState.NEGOCIANDO,
        ConversationState.COMPROMETIDO,
        ConversationState.ABANDONADO,
        ConversationState.BLOQUEADO
    ],
    ConversationState.NEGOCIANDO: [
        ConversationState.COMPROMETIDO,
        ConversationState.COORDINANDO,
        ConversationState.ABANDONADO,
        ConversationState.BLOQUEADO
    ],
    ConversationState.COMPROMETIDO: [
        ConversationState.COORDINANDO,
        ConversationState.FINALIZADO,
        ConversationState.ABANDONADO
    ],
    ConversationState.COORDINANDO: [
        ConversationState.FINALIZADO,
        ConversationState.ABANDONADO
    ]
}
```

### Intent Detection

#### Intent Classification

```python
from src.conversation_engine.intent_detector import IntentDetector

detector = IntentDetector()

# Detect buyer intent
intent = detector.detect_intent("¿Acepta 300€?")
print(intent)
# Output: {
#     "primary_intent": "negociacion_precio",
#     "confidence": 0.94,
#     "secondary_intents": ["confirmacion_interes"],
#     "intent_details": {
#         "negotiation_type": "price_reduction",
#         "proposed_price": 300,
#         "negotiation_severity": "moderate"
#     }
# }

# Available intents
intents = detector.get_available_intents()
print(intents)
# Output: [
#     "saludo_inicial",
#     "consulta_disponibilidad", 
#     "consulta_precio",
#     "negociacion_precio",
#     "consulta_estado",
#     "consulta_ubicacion",
#     "propuesta_intercambio",
#     "solicitud_informacion",
#     "confirmacion_compra",
#     "coordinacion_encuentro",
#     "despedida"
# ]
```

---

## 🛡️ Security & Validation API

### Fraud Detection System

#### AIResponseValidator

**Multi-layer security validation system.**

```python
from src.ai_engine.validator import AIResponseValidator, ValidationResult

class AIResponseValidator:
    def __init__(self, config: AIEngineConfig) -> None
    def validate_request(self, request: ConversationRequest) -> ValidationResult
    def validate_response(self, response_text: str, request: ConversationRequest) -> ValidationResult
    def validate_buyer_message(self, message: str, buyer_profile: Dict = None) -> ValidationResult
    def get_fraud_patterns(self) -> Dict[str, List[str]]
    def add_custom_pattern(self, pattern: str, risk_points: int) -> None
    def update_patterns(self) -> None
```

**Methods:**

##### `validate_buyer_message(message: str, buyer_profile: Dict = None) -> ValidationResult`
Validate buyer message for fraud patterns.

**Parameters:**
- `message` (str): Buyer's message to validate
- `buyer_profile` (Dict, optional): Buyer profile for context

**Returns:** ValidationResult with security analysis

**Example:**
```python
validator = AIResponseValidator(config)

# Test legitimate message
result = validator.validate_buyer_message("¿Incluye el cargador original?")
print(f"Safe: {result.is_safe}")
print(f"Risk Score: {result.risk_score}")

# Test fraudulent message
result = validator.validate_buyer_message("¿Acepta pago por Western Union?")
print(f"Safe: {result.is_safe}")
print(f"Risk Score: {result.risk_score}")
print(f"Critical Violations: {result.critical_violations}")
```

#### ValidationResult

**Detailed security validation results.**

```python
@dataclass
class ValidationResult:
    is_safe: bool
    risk_score: int
    risk_factors: List[str]
    critical_violations: List[str]
    recommendations: List[str]
    validation_time: float
    patterns_matched: List[str]
    context_analysis: Dict[str, Any]
```

**Security Risk Levels:**

| Risk Score | Level | Action | Description |
|------------|-------|--------|-------------|
| 0-24 | LOW | ✅ Allow | Safe conversation |
| 25-49 | MEDIUM | ⚠️ Monitor | Increased vigilance |
| 50-74 | HIGH | 🔍 Review | Manual review recommended |
| 75-100 | CRITICAL | 🚨 Block | Automatic blocking |

**Example Analysis:**
```python
result = validator.validate_buyer_message("Mi primo puede recogerlo por Bitcoin")

print(f"Is Safe: {result.is_safe}")                    # False
print(f"Risk Score: {result.risk_score}")              # 100
print(f"Risk Factors: {result.risk_factors}")          # ["third_party_pickup", "cryptocurrency_payment"]
print(f"Critical Violations: {result.critical_violations}")  # ["bitcoin", "tercera_persona"]
print(f"Recommendations: {result.recommendations}")     # ["Block conversation", "Report suspicious activity"]
```

### Fraud Pattern Management

#### Pattern Categories

```python
# Critical fraud patterns (auto-block)
CRITICAL_PATTERNS = {
    "payment_methods": [
        "western union", "money gram", "bitcoin", "ethereum",
        "paypal familia", "paypal friends", "paypal amigos"
    ],
    "personal_data": [
        "dni", "nif", "tarjeta credito", "numero cuenta",
        "cvv", "pin", "contraseña"
    ],
    "external_communication": [
        "whatsapp", "telegram", "email directo",
        "llamame", "mi telefono"
    ],
    "shipping_scams": [
        "envio pagado", "transportista", "correos pago",
        "recogida casa", "entrega sin ver"
    ]
}

# High-risk patterns (monitor)
HIGH_RISK_PATTERNS = {
    "urgency_tactics": [
        "urgente hoy", "inmediatamente", "ahora mismo",
        "solo hoy", "ultima oportunidad"
    ],
    "location_fishing": [
        "direccion exacta", "donde vives", "tu casa",
        "codigo postal", "ubicacion privada"
    ],
    "value_manipulation": [
        "gratis", "sin coste", "regalo",
        "pago extra", "dinero adicional"
    ]
}
```

#### Custom Pattern Management

```python
# Add custom fraud pattern
validator.add_custom_pattern("nuevo patron sospechoso", risk_points=30)

# Add multiple patterns
custom_patterns = [
    ("patron empresa falsa", 25),
    ("solicitud foto dni", 50),
    ("pago criptomoneda", 75)
]

for pattern, risk in custom_patterns:
    validator.add_custom_pattern(pattern, risk)

# Update patterns from external source
validator.update_patterns()
```

### URL Security Analysis

#### URL Threat Detection

```python
from src.ai_engine.url_analyzer import URLAnalyzer

analyzer = URLAnalyzer()

# Analyze URL for threats
url_result = analyzer.analyze_url("https://suspicious-site.com/fake-payment")
print(url_result)
# Output: {
#     "is_safe": False,
#     "threat_type": "phishing",
#     "risk_score": 85,
#     "details": {
#         "domain_age": 2,  # days
#         "ssl_valid": False,
#         "reputation": "malicious",
#         "redirects": 3
#     }
# }

# Bulk URL analysis
urls = [
    "https://wallapop.com/item/123",
    "https://suspicious-site.com",
    "https://paypal.com/fake-login"
]

results = analyzer.analyze_urls(urls)
for url, result in results.items():
    print(f"{url}: {'Safe' if result['is_safe'] else 'Threat'}")
```

---

## 📊 Performance Monitoring API

### Performance Monitor

#### PerformanceMonitor

**Real-time performance monitoring and optimization.**

```python
from src.ai_engine.performance_monitor import get_performance_monitor, PerformanceMonitor

class PerformanceMonitor:
    def get_current_metrics(self) -> Dict[str, Any]
    def get_health_status(self) -> Dict[str, Any]
    def get_cache_stats(self) -> Dict[str, Any]
    def get_dashboard_data(self) -> Dict[str, Any]
    def record_request(self, response_time: float, success: bool) -> None
    def record_ai_generation(self, generation_time: float, tokens: int) -> None
    def clear_cache(self) -> None
    def optimize_cache(self) -> None
    def generate_performance_report(self) -> str
```

**Singleton Access:**
```python
# Get global performance monitor instance
monitor = get_performance_monitor()
```

**Methods:**

##### `get_current_metrics() -> Dict[str, Any]`
Get current performance metrics.

**Returns:** Dictionary with current performance data

**Response Format:**
```python
{
    "requests": {
        "total": 1250,
        "successful": 1235,
        "failed": 15,
        "success_rate": 0.988
    },
    "response_times": {
        "avg": 2.34,
        "min": 0.45,
        "max": 8.12,
        "p95": 4.67,
        "p99": 6.89
    },
    "throughput": {
        "requests_per_minute": 18.5,
        "requests_per_hour": 1110
    },
    "memory": {
        "usage_mb": 6840,
        "threshold_mb": 12000,
        "usage_percent": 57.0
    },
    "cache": {
        "size": 450,
        "hits": 287,
        "misses": 163,
        "hit_rate": 0.638
    }
}
```

##### `get_health_status() -> Dict[str, Any]`
Get overall system health assessment.

**Returns:** Dictionary with health status and score

**Response Format:**
```python
{
    "status": "healthy",  # "healthy", "degraded", "unhealthy"
    "score": 92,          # Health score (0-100)
    "issues": [],         # List of detected issues
    "recommendations": [  # Optimization recommendations
        "Consider increasing cache size",
        "Memory usage within acceptable range"
    ],
    "uptime": 86400,      # Uptime in seconds
    "last_check": "2025-01-16T15:30:00Z"
}
```

##### `get_dashboard_data() -> Dict[str, Any]`
Get comprehensive dashboard data for monitoring interfaces.

**Returns:** Dictionary with formatted dashboard data

**Response Format:**
```python
{
    "overview": {
        "status": "healthy",
        "requests_today": 2400,
        "avg_response_time": 2.1,
        "success_rate": 99.2
    },
    "ai_engine": {
        "model_name": "llama3.2:11b-vision-instruct-q4_0",
        "generation_stats": {
            "ai_generated": 2100,
            "template_fallback": 300,
            "fraud_blocked": 45
        },
        "response_time": {
            "avg": 1.8,
            "trend": "stable"
        }
    },
    "security": {
        "fraud_detected": 45,
        "false_positives": 2,
        "accuracy": 95.6,
        "patterns_active": 156
    },
    "system": {
        "memory_usage_mb": {
            "latest": 6840,
            "trend": "stable"
        },
        "cpu_usage": {
            "latest": 45.2,
            "trend": "low"
        }
    },
    "alerts": [
        {
            "type": "info",
            "message": "Cache hit rate below target (35%)",
            "timestamp": "2025-01-16T15:25:00Z"
        }
    ]
}
```

### Performance Metrics

#### Metric Collection

```python
# Record custom metrics
monitor.record_request(response_time=2.1, success=True)
monitor.record_ai_generation(generation_time=1.8, tokens=150)

# Record with additional context
monitor.record_metric("conversation.negotiation", value=1, tags={
    "personality": "vendedor_experimentado",
    "risk_level": "low",
    "buyer_rating": 4.5
})
```

#### Alert Management

```python
from src.ai_engine.performance_monitor import AlertRule, AlertManager

# Create performance alert
alert_rule = AlertRule(
    name="high_response_time",
    metric_name="response_time",
    threshold=5.0,
    operator="gt",
    window_seconds=300,
    callback=lambda: print("⚠️ High response time detected!")
)

# Add to monitor
monitor.alert_manager.add_alert_rule(alert_rule)

# Custom alert callback
def handle_memory_alert(metric_value, threshold):
    print(f"🚨 Memory usage {metric_value}MB exceeds threshold {threshold}MB")
    # Trigger garbage collection
    monitor.trigger_cleanup()

memory_alert = AlertRule(
    name="high_memory",
    metric_name="memory_usage_mb",
    threshold=10000,
    operator="gt",
    callback=handle_memory_alert
)
```

---

## 🔧 Configuration API

### Configuration Management

#### Configuration Loading

```python
from src.ai_engine.config import AIEngineConfig

# Load from file
config = AIEngineConfig.from_file("config/ai_engine.yaml")

# Load from environment variables
config = AIEngineConfig.from_env()

# Mixed loading (file + env overrides)
config = AIEngineConfig.from_file("config/ai_engine.yaml")
config.update_from_env()

# Save current configuration
config.save_to_file("config/current_config.yaml")
```

#### Dynamic Configuration Updates

```python
# Update configuration at runtime
config.max_concurrent_requests = 15
config.fraud_detection_threshold = 20

# Validate changes
try:
    config.validate()
    print("✅ Configuration valid")
except ConfigurationError as e:
    print(f"❌ Configuration error: {e}")

# Apply to running engine
engine.update_config(config)
```

#### Environment-Specific Configurations

```python
# Development configuration
dev_config = AIEngineConfig(
    debug_mode=True,
    log_level="DEBUG",
    enable_profiling=True,
    save_prompts=True,
    test_mode=True
)

# Production configuration
prod_config = AIEngineConfig(
    debug_mode=False,
    log_level="INFO",
    enable_profiling=False,
    audit_all_responses=True,
    strict_validation=True
)

# Load environment-specific config
import os
env = os.getenv("WALL_E_ENV", "development")

if env == "production":
    config = AIEngineConfig.for_compliance()
elif env == "development":
    config = AIEngineConfig.for_research()
else:
    config = AIEngineConfig()
```

---

## 💰 Price Analysis API

### Price Analyzer

#### PriceAnalyzer

**Multi-platform price analysis and market intelligence.**

```python
from src.price_analyzer.analyzer import PriceAnalyzer, PriceAnalysisRequest

class PriceAnalyzer:
    def __init__(self, config: Dict[str, Any] = None) -> None
    async def analyze_price(self, request: PriceAnalysisRequest) -> PriceAnalysis
    async def get_market_data(self, product_name: str, category: str) -> MarketData
    async def suggest_optimal_price(self, product: Product, strategy: str) -> PriceSuggestion
    def get_supported_platforms(self) -> List[str]
    async def update_market_cache(self) -> None
```

**Usage Example:**
```python
analyzer = PriceAnalyzer()

# Analyze product price
request = PriceAnalysisRequest(
    product_name="iPhone 12 128GB",
    category="smartphones",
    condition="muy buen estado",
    current_price=450,
    location="Madrid"
)

analysis = await analyzer.analyze_price(request)
print(f"Market average: {analysis.market_average}€")
print(f"Confidence: {analysis.confidence:.2f}")
print(f"Recommendation: {analysis.recommendation}")
```

#### PriceAnalysisRequest

```python
@dataclass
class PriceAnalysisRequest:
    product_name: str
    category: str
    condition: str
    current_price: float
    location: str = "Madrid"
    brand: str = None
    model: str = None
    year: int = None
    features: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
```

#### PriceAnalysis

```python
@dataclass
class PriceAnalysis:
    market_average: float
    price_range: Dict[str, float]  # {"min": 300, "max": 600}
    confidence: float
    recommendation: str
    competitive_position: str      # "below_market", "at_market", "above_market"
    
    # Market data
    platform_data: Dict[str, List[Dict]]
    similar_listings: List[Dict]
    market_trends: Dict[str, Any]
    
    # Suggestions
    suggested_price: float
    price_justification: str
    optimization_tips: List[str]
```

---

## 🕷️ Scraper API

### Web Scraping System

#### WallapopScraper

**Anti-detection web scraping with Playwright.**

```python
from src.scraper.wallapop_scraper import WallapopScraper, ScrapingRequest

class WallapopScraper:
    def __init__(self, config: Dict[str, Any] = None) -> None
    async def initialize(self) -> None
    async def scrape_conversations(self) -> List[Dict]
    async def scrape_product_data(self, product_url: str) -> Dict
    async def send_message(self, conversation_id: str, message: str) -> bool
    async def get_conversation_history(self, conversation_id: str) -> List[Dict]
    async def shutdown(self) -> None
```

**Security Features:**
- **Anti-detection:** Human-like browsing patterns
- **Session management:** Encrypted cookie persistence  
- **Rate limiting:** Configurable request throttling
- **Circuit breaker:** Automatic error recovery
- **User agent rotation:** Random browser fingerprints

**Usage Example:**
```python
scraper = WallapopScraper()
await scraper.initialize()

# Get new conversations
conversations = await scraper.scrape_conversations()
for conv in conversations:
    print(f"New message from {conv['buyer_name']}: {conv['last_message']}")

# Send AI-generated response
success = await scraper.send_message(
    conversation_id="conv_123",
    message="¡Hola! Sí, está disponible. ¿Te interesa?"
)

await scraper.shutdown()
```

---

## 🌐 REST API Endpoints

### HTTP API Server

The Wall-E system can be deployed as a REST API server for integration with external systems.

#### Server Setup

```python
from fastapi import FastAPI, HTTPException
from src.ai_engine import AIEngine, AIEngineConfig
from src.ai_engine.api import router as ai_router

app = FastAPI(
    title="Wall-E AI Engine API",
    version="2.0.0",
    description="AI-powered Wallapop conversation automation"
)

# Include AI Engine routes
app.include_router(ai_router, prefix="/api/v2")

# Start server
# uvicorn main:app --host 0.0.0.0 --port 8000
```

### Conversation Endpoints

#### POST `/api/v2/conversation/generate`

Generate AI-powered conversation response.

**Request Body:**
```json
{
    "buyer_message": "¡Hola! ¿Está disponible el iPhone?",
    "buyer_name": "CompradirTest",
    "product_name": "iPhone 12",
    "price": 400,
    "personality": "amigable_casual",
    "buyer_profile": {
        "ratings_count": 15,
        "avg_rating": 4.5,
        "distance": 12
    }
}
```

**Response:**
```json
{
    "success": true,
    "response": {
        "text": "¡Hola! 😊 Sí, está disponible. Son 400€ como aparece en el anuncio. ¿Te interesa?",
        "confidence": 0.92,
        "risk_score": 0,
        "source": "ai_engine",
        "response_time": 1.85,
        "personality_used": "amigable_casual"
    },
    "security": {
        "is_safe": true,
        "risk_factors": [],
        "critical_violations": []
    },
    "metadata": {
        "model_name": "llama3.2:11b-vision-instruct-q4_0",
        "tokens_generated": 24,
        "request_id": "req_abc123"
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "AI generation timeout",
    "error_code": "GENERATION_TIMEOUT",
    "details": {
        "timeout": 30,
        "fallback_available": true
    }
}
```

#### POST `/api/v2/conversation/batch`

Process multiple conversations concurrently.

**Request Body:**
```json
{
    "conversations": [
        {
            "buyer_message": "¿Precio final?",
            "buyer_name": "Buyer1",
            "product_name": "iPhone 12",
            "price": 400
        },
        {
            "buyer_message": "¿Acepta cambios?",
            "buyer_name": "Buyer2", 
            "product_name": "MacBook Pro",
            "price": 800
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "count": 2,
    "responses": [
        {
            "text": "Son 400€ como aparece en el anuncio",
            "confidence": 0.89,
            "risk_score": 5,
            "error": null
        },
        {
            "text": "No acepto cambios, solo venta",
            "confidence": 0.94,
            "risk_score": 0,
            "error": null
        }
    ],
    "batch_metadata": {
        "total_time": 3.2,
        "concurrent_requests": 2,
        "average_response_time": 1.6
    }
}
```

### Health & Monitoring Endpoints

#### GET `/api/v2/health`

Get system health status.

**Response:**
```json
{
    "status": "healthy",
    "health_score": 92,
    "components": {
        "ai_engine": "ready",
        "ollama": "connected",
        "database": "connected",
        "cache": "active"
    },
    "performance": {
        "avg_response_time": 2.1,
        "requests_per_minute": 18.5,
        "memory_usage_mb": 6840,
        "cache_hit_rate": 0.65
    }
}
```

#### GET `/api/v2/metrics`

Get detailed performance metrics.

**Response:**
```json
{
    "requests": {
        "total": 1250,
        "successful": 1235,
        "failed": 15,
        "success_rate": 0.988
    },
    "ai_engine": {
        "generations": {
            "ai_generated": 1100,
            "template_fallback": 150,
            "fraud_blocked": 25
        },
        "performance": {
            "avg_generation_time": 1.8,
            "avg_validation_time": 0.12,
            "model_name": "llama3.2:11b-vision-instruct-q4_0"
        }
    },
    "security": {
        "fraud_detected": 25,
        "false_positives": 1,
        "accuracy": 96.0,
        "patterns_active": 156
    }
}
```

### Configuration Endpoints

#### GET `/api/v2/config`

Get current configuration.

**Response:**
```json
{
    "mode": "ai_first",
    "model_name": "llama3.2:11b-vision-instruct-q4_0",
    "performance": {
        "max_concurrent_requests": 10,
        "timeout": 30,
        "enable_caching": true
    },
    "security": {
        "fraud_detection_threshold": 25,
        "critical_fraud_threshold": 50,
        "strict_validation": false
    }
}
```

#### PUT `/api/v2/config`

Update configuration (admin only).

**Request Body:**
```json
{
    "fraud_detection_threshold": 20,
    "max_concurrent_requests": 15,
    "enable_caching": true
}
```

**Response:**
```json
{
    "success": true,
    "message": "Configuration updated successfully",
    "changes_applied": [
        "fraud_detection_threshold: 25 → 20",
        "max_concurrent_requests: 10 → 15"
    ]
}
```

---

## 📚 Data Models

### Core Data Structures

#### Buyer Profile

```python
@dataclass
class BuyerProfile:
    name: str
    user_id: str
    rating: float
    ratings_count: int
    account_age: int          # days
    location: str
    distance: float           # km from seller
    successful_purchases: int
    preferred_categories: List[str]
    communication_style: str  # "formal", "casual", "brief"
    response_time_avg: float  # hours
    negotiation_tendency: str # "aggressive", "moderate", "passive"
    risk_factors: List[str]
    
    def calculate_priority(self) -> str:
        """Calculate buyer priority: HIGH, MEDIUM, LOW"""
        score = 0
        
        # Rating influence
        if self.rating >= 4.5 and self.ratings_count >= 10:
            score += 3
        elif self.rating >= 4.0:
            score += 2
        elif self.rating >= 3.5:
            score += 1
            
        # Experience influence
        if self.successful_purchases >= 10:
            score += 2
        elif self.successful_purchases >= 5:
            score += 1
            
        # Distance influence
        if self.distance <= 10:
            score += 2
        elif self.distance <= 25:
            score += 1
            
        # Account age influence
        if self.account_age >= 365:
            score += 1
            
        if score >= 7:
            return "HIGH"
        elif score >= 4:
            return "MEDIUM"
        else:
            return "LOW"
```

#### Product Information

```python
@dataclass
class ProductInfo:
    name: str
    product_id: str
    category: str
    brand: str
    model: str
    condition: str            # "nuevo", "como nuevo", "buen estado", "usado"
    price: float
    original_price: float
    description: str
    features: List[str]
    images: List[str]
    location: str
    shipping_available: bool
    shipping_cost: float
    views_count: int
    favorites_count: int
    published_date: datetime
    last_updated: datetime
    
    def get_depreciation_rate(self) -> float:
        """Calculate depreciation rate vs original price"""
        if self.original_price > 0:
            return (self.original_price - self.price) / self.original_price
        return 0.0
        
    def get_condition_score(self) -> int:
        """Get numeric condition score (1-5)"""
        condition_scores = {
            "nuevo": 5,
            "como nuevo": 4,
            "buen estado": 3,
            "usado": 2,
            "para reparar": 1
        }
        return condition_scores.get(self.condition.lower(), 2)
```

#### Conversation Context

```python
@dataclass
class ConversationContext:
    conversation_id: str
    buyer: BuyerProfile
    product: ProductInfo
    current_state: ConversationState
    message_history: List[Dict]
    last_activity: datetime
    response_count: int
    seller_personality: str
    negotiation_rounds: int
    price_offers: List[float]
    meeting_proposals: List[Dict]
    flags: List[str]          # ["urgent", "high_value", "potential_fraud"]
    
    def get_conversation_age(self) -> int:
        """Get conversation age in hours"""
        return int((datetime.utcnow() - self.last_activity).total_seconds() / 3600)
        
    def get_engagement_level(self) -> str:
        """Calculate engagement level: HIGH, MEDIUM, LOW"""
        if self.response_count >= 10:
            return "HIGH"
        elif self.response_count >= 5:
            return "MEDIUM"
        else:
            return "LOW"
            
    def should_follow_up(self) -> bool:
        """Determine if follow-up is needed"""
        hours_since_last = self.get_conversation_age()
        
        if self.current_state == ConversationState.COMPROMETIDO:
            return hours_since_last > 6
        elif self.current_state == ConversationState.NEGOCIANDO:
            return hours_since_last > 12
        else:
            return hours_since_last > 24
```

### API Response Models

#### Standard API Response

```python
@dataclass
class APIResponse:
    success: bool
    data: Any = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
```

#### Paginated Response

```python
@dataclass
class PaginatedResponse(APIResponse):
    data: List[Any]
    pagination: Dict[str, Any]
    
    @classmethod
    def create(cls, items: List[Any], page: int, per_page: int, total: int):
        return cls(
            success=True,
            data=items,
            pagination={
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": math.ceil(total / per_page),
                "has_next": page * per_page < total,
                "has_prev": page > 1
            }
        )
```

---

## ⚠️ Error Handling

### Exception Hierarchy

```python
# Base exception
class WallEError(Exception):
    """Base exception for Wall-E system"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        super().__init__(self.message)

# AI Engine exceptions
class AIEngineError(WallEError):
    """Base AI Engine exception"""
    pass

class ModelNotAvailableError(AIEngineError):
    """AI model not available"""
    pass

class GenerationTimeoutError(AIEngineError):
    """AI generation timeout"""
    pass

class GenerationError(AIEngineError):
    """AI generation failed"""
    pass

# Configuration exceptions
class ConfigurationError(WallEError):
    """Configuration validation error"""
    pass

class InvalidModelError(ConfigurationError):
    """Invalid model configuration"""
    pass

# Security exceptions
class SecurityError(WallEError):
    """Security validation error"""
    pass

class FraudDetectedError(SecurityError):
    """Fraud pattern detected"""
    pass

class ValidationError(SecurityError):
    """Response validation failed"""
    pass

# Performance exceptions
class PerformanceError(WallEError):
    """Performance threshold exceeded"""
    pass

class MemoryExhaustedError(PerformanceError):
    """Memory usage exceeded threshold"""
    pass

class ConcurrencyLimitError(PerformanceError):
    """Concurrent request limit exceeded"""
    pass
```

### Error Response Format

```python
# Standard error response
{
    "success": false,
    "error": "AI generation timeout after 30 seconds",
    "error_code": "GENERATION_TIMEOUT",
    "details": {
        "timeout": 30,
        "model_name": "llama3.2:11b-vision-instruct-q4_0",
        "fallback_available": true,
        "request_id": "req_abc123"
    },
    "timestamp": "2025-01-16T15:30:00Z"
}

# Validation error response
{
    "success": false,
    "error": "Configuration validation failed",
    "error_code": "CONFIGURATION_ERROR",
    "details": {
        "validation_errors": [
            "max_concurrent_requests must be between 1 and 50",
            "fraud_detection_threshold must be between 0 and 100"
        ],
        "invalid_fields": ["max_concurrent_requests", "fraud_detection_threshold"]
    }
}

# Security error response
{
    "success": false,
    "error": "Critical fraud pattern detected",
    "error_code": "FRAUD_DETECTED",
    "details": {
        "risk_score": 100,
        "critical_violations": ["western_union_payment"],
        "blocked_patterns": ["western union"],
        "recommendation": "Block conversation immediately"
    }
}
```

### Error Handling Best Practices

#### Try-Catch with Specific Handling

```python
from src.ai_engine.exceptions import *

try:
    engine = AIEngine(config)
    response = engine.generate_response(request)
    
except ModelNotAvailableError as e:
    logger.error(f"Model unavailable: {e}")
    # Fall back to template system
    response = template_engine.generate_response(request)
    
except GenerationTimeoutError as e:
    logger.warning(f"Generation timeout: {e}")
    # Retry with shorter timeout or use template
    response = handle_generation_timeout(request)
    
except FraudDetectedError as e:
    logger.critical(f"Fraud detected: {e}")
    # Use security response
    response = security_response_generator.get_safe_response()
    
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    # Use default configuration
    config = AIEngineConfig()
    engine = AIEngine(config)
    
except AIEngineError as e:
    logger.error(f"AI Engine error: {e}")
    # General AI Engine fallback
    response = handle_ai_engine_error(request, e)
    
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    # Last resort fallback
    response = emergency_fallback_response()
```

#### Async Error Handling

```python
import asyncio

async def safe_ai_generation(request: ConversationRequest) -> ConversationResponse:
    """Safely generate AI response with comprehensive error handling"""
    try:
        # Try AI generation with timeout
        response = await asyncio.wait_for(
            engine.generate_response_async(request),
            timeout=30.0
        )
        return response
        
    except asyncio.TimeoutError:
        logger.warning("AI generation timeout, using template fallback")
        return template_engine.generate_response(request)
        
    except FraudDetectedError as e:
        logger.critical(f"Fraud detected: {e.details}")
        return create_security_response(e.details)
        
    except AIEngineError as e:
        logger.error(f"AI Engine error: {e}")
        if e.error_code == "MODEL_NOT_AVAILABLE":
            return handle_model_unavailable(request)
        else:
            return template_engine.generate_response(request)
            
    except Exception as e:
        logger.exception("Unexpected error in AI generation")
        return create_error_response(str(e))

# Usage
response = await safe_ai_generation(request)
```

#### Circuit Breaker Pattern

```python
from typing import Callable
import time

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
            
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

# Usage
ai_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

def safe_ai_call(request):
    try:
        return ai_circuit_breaker.call(engine.generate_response, request)
    except CircuitBreakerOpenError:
        return template_engine.generate_response(request)
```

### Logging and Monitoring

#### Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Log with context
logger.info(
    "AI response generated",
    request_id=request.request_id,
    buyer_name=request.buyer_name,
    product_name=request.product_name,
    response_time=response.response_time,
    confidence=response.confidence,
    risk_score=response.risk_score,
    source=response.source
)

# Log errors with full context
logger.error(
    "AI generation failed",
    error=str(e),
    error_code=e.error_code,
    request_id=request.request_id,
    model_name=config.model_name,
    timeout=config.timeout,
    retry_count=retry_count
)
```

#### Error Metrics

```python
from prometheus_client import Counter, Histogram

# Define error metrics
error_counter = Counter('wall_e_errors_total', 'Total errors', ['error_type', 'component'])
error_rate = Histogram('wall_e_error_rate', 'Error rate by component')

# Record errors
def record_error(error: Exception, component: str):
    error_type = error.__class__.__name__
    error_counter.labels(error_type=error_type, component=component).inc()
    
    # Record in performance monitor
    monitor = get_performance_monitor()
    monitor.record_error(error_type, component, str(error))

# Usage
try:
    response = engine.generate_response(request)
except AIEngineError as e:
    record_error(e, "ai_engine")
    raise
```

---

**🚀 This comprehensive API reference provides everything needed to integrate and extend the Wall-E AI Engine system. The APIs are designed for production use with robust error handling, performance monitoring, and security validation.**

*For implementation examples and advanced usage patterns, see the [AI Engine Guide](AI_ENGINE_GUIDE.md) and [Development Guide](DEVELOPMENT_GUIDE.md).*