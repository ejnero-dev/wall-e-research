# 👩‍💻 Wall-E Development Guide

Comprehensive guide for developers contributing to the Wall-E Wallapop automation system with AI Engine.

---

## 📋 Table of Contents

- [🚀 Getting Started](#-getting-started)
- [🏗️ Project Architecture](#️-project-architecture)
- [🔧 Development Setup](#-development-setup)
- [🎯 Contributing Guidelines](#-contributing-guidelines)
- [🧪 Testing Standards](#-testing-standards)
- [📚 Code Standards](#-code-standards)
- [🤖 AI Engine Development](#-ai-engine-development)
- [🔌 API Development](#-api-development)
- [🛡️ Security Development](#️-security-development)
- [📊 Performance Guidelines](#-performance-guidelines)
- [🚀 Release Process](#-release-process)

---

## 🚀 Getting Started

### Prerequisites

**Required Skills:**
- **Python 3.11+** with async/await patterns
- **FastAPI** for API development
- **PostgreSQL** and **Redis** for data management
- **Docker** and containerization concepts
- **Testing** with pytest and test-driven development
- **Git** workflow and collaboration

**AI Engine Specific:**
- **LLM concepts** and local inference
- **NLP** with spaCy for Spanish language processing
- **Security patterns** for fraud detection
- **Performance optimization** for concurrent systems

### Quick Start for Contributors

```bash
# 1. Fork and clone the repository
git clone https://github.com/your-username/wall-e-research.git
cd wall-e-research

# 2. Set up development environment
python scripts/setup_dev.py

# 3. Install pre-commit hooks
pre-commit install

# 4. Run initial tests
pytest tests/ -v

# 5. Start coding!
```

### Development Environment Setup

**Complete development setup:**
```bash
# Create development virtual environment
python3.11 -m venv wall_e_dev
source wall_e_dev/bin/activate

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install spaCy Spanish model
python -m spacy download es_core_news_sm

# Install Playwright browsers
playwright install chromium

# Set up AI Engine (optional for core development)
python scripts/setup_ollama.py

# Initialize development database
python scripts/init_database_advanced.py --dev

# Validate setup
python scripts/validate_setup.py --dev
```

### IDE Configuration

**VS Code Configuration (`.vscode/settings.json`):**
```json
{
    "python.defaultInterpreterPath": "./wall_e_dev/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=100"],
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true
    }
}
```

**PyCharm Configuration:**
- **Interpreter:** Set to `./wall_e_dev/bin/python`
- **Code Style:** Black formatter with 100 character line length
- **Testing:** pytest as default test runner
- **Type Checking:** Enable mypy integration

---

## 🏗️ Project Architecture

### High-Level Architecture

```
Wall-E System Architecture
├── 🤖 AI Engine Layer
│   ├── LLM Manager (Ollama integration)
│   ├── Response Generator (Conversation creation)
│   ├── Validator (Security & fraud detection)
│   ├── Fallback Handler (Hybrid AI + templates)
│   └── Performance Monitor (Real-time optimization)
├── 💬 Conversation Layer
│   ├── Conversation Engine (State management)
│   ├── Intent Detection (NLP analysis)
│   ├── Buyer Classification (Priority system)
│   └── AI Enhanced Engine (AI integration)
├── 🕷️ Scraper Layer
│   ├── Wallapop Scraper (Anti-detection automation)
│   ├── Session Manager (Cookie persistence)
│   ├── Anti-Detection (Human-like behavior)
│   └── Error Handler (Circuit breaker patterns)
├── 💰 Analysis Layer
│   ├── Price Analyzer (Multi-platform analysis)
│   ├── Market Intelligence (Trend analysis)
│   ├── Competitive Positioning (Strategy optimization)
│   └── Statistical Engine (Confidence scoring)
├── 🗄️ Data Layer
│   ├── PostgreSQL (Primary data store)
│   ├── Redis (Caching & sessions)
│   ├── Database Models (SQLAlchemy ORM)
│   └── Migration System (Alembic)
└── 🌐 API Layer
    ├── FastAPI (RESTful endpoints)
    ├── WebSocket (Real-time communication)
    ├── Authentication (JWT & API keys)
    └── Rate Limiting (Request throttling)
```

### Module Structure

```
src/
├── ai_engine/                  # AI Engine core (Phase 2A - COMPLETED)
│   ├── __init__.py            # Public API exports
│   ├── ai_engine.py           # Main orchestrator (580 lines)
│   ├── config.py              # Hardware-aware configuration
│   ├── llm_manager.py         # Ollama integration + caching
│   ├── prompt_templates.py    # Spanish conversation templates
│   ├── response_generator.py  # AI response generation
│   ├── validator.py           # Multi-layer fraud detection
│   ├── fallback_handler.py    # Hybrid AI + template system
│   └── performance_monitor.py # Real-time performance tracking
├── conversation_engine/        # Conversation management
│   ├── engine.py              # Traditional conversation engine
│   └── ai_enhanced_engine.py  # AI-enhanced version
├── scraper/                   # Web scraping system
│   ├── wallapop_scraper.py    # Main scraper with anti-detection
│   ├── session_manager.py     # Cookie and session management
│   ├── anti_detection.py      # Human-like behavior patterns
│   └── error_handler.py       # Circuit breaker and retry logic
├── price_analyzer/            # Price analysis system
│   ├── analyzer.py            # Main price analysis engine
│   └── scrapers/              # Platform-specific scrapers
│       ├── amazon_scraper.py  # Amazon price data
│       └── wallapop_scraper.py # Wallapop market data
├── database/                  # Database layer
│   ├── models.py              # SQLAlchemy models
│   ├── db_manager.py          # Database operations
│   └── redis_manager.py       # Redis operations
├── bot/                       # Main bot orchestration
│   └── wallapop_bot.py        # Central bot coordinator
└── api/                       # REST API (Future Phase 2B)
    ├── main.py                # FastAPI application
    ├── auth.py                # Authentication middleware
    └── endpoints/             # API endpoint modules
```

### Specialized Subagents Integration

**Wall-E uses 11 specialized Claude Code subagents:**

| Subagent | Status | Responsibility | When to Use |
|----------|--------|----------------|-------------|
| `web-scraper-security` | ✅ Active | Anti-detection scraping implementation | Scraper modifications |
| `test-automation-specialist` | ✅ Active | Comprehensive testing infrastructure | Test development |
| `security-compliance-auditor` | ✅ Active | Security audits and compliance | Security features |
| `nlp-fraud-detector` | ✅ Active | AI Engine and fraud detection | AI/NLP development |
| `performance-optimizer` | ✅ Active | System optimization | Performance work |
| `config-manager` | 🔄 Available | Configuration management | Config systems |
| `devops-deploy-specialist` | 🔄 Available | Docker & CI/CD | Infrastructure |
| `technical-documentation-writer` | 🔄 Available | Documentation automation | Docs generation |
| `ux-dashboard-creator` | 🔄 Available | Dashboard development | UI work |
| `price-intelligence-analyst` | 🔄 Available | Price analysis enhancement | Market analysis |
| `database-architect` | 🔄 Available | Database optimization | DB design |

**Usage Guidelines:**
- **Never duplicate subagent expertise** - Always use the appropriate specialist
- **Combine subagents** for complex features requiring multiple skills
- **Document subagent usage** in PRs and commit messages

---

## 🔧 Development Setup

### Environment Configuration

**Development Environment Variables (`.env.dev`):**
```bash
# Environment
WALL_E_ENV=development
DEBUG=true

# Database Configuration
POSTGRES_URL=postgresql://wall_e:dev_password@localhost:5432/wall_e_dev
REDIS_URL=redis://localhost:6379/1

# AI Engine Configuration
OLLAMA_HOST=http://localhost:11434
AI_MODEL=phi3.5:3.8b-mini-instruct-q4_0  # Lightweight for development
AI_MODE=hybrid
MAX_CONCURRENT_REQUESTS=3

# Security Configuration (relaxed for development)
FRAUD_DETECTION_THRESHOLD=30
STRICT_VALIDATION=false
ENABLE_DEBUG_LOGS=true

# Performance Configuration
ENABLE_CACHING=true
CACHE_SIZE=100
ENABLE_PROFILING=true
```

### Development Scripts

**Available development scripts:**
```bash
# Setup and initialization
python scripts/setup_dev.py              # Complete dev environment setup
python scripts/init_database_advanced.py # Initialize dev database
python scripts/quick_setup.py --dev      # Quick development setup

# Testing and validation
python scripts/test_ai_engine_basic.py   # AI Engine functionality test
python scripts/validate_setup.py --dev  # Development setup validation
python scripts/run_all_tests.py          # Complete test suite

# Development tools
python scripts/generate_test_data.py     # Generate test conversation data
python scripts/analyze_performance.py   # Performance analysis
python scripts/check_code_quality.py    # Code quality validation
```

### Development Database

**Initialize development database:**
```bash
# Create development database
createdb wall_e_dev

# Run migrations
alembic upgrade head

# Seed with test data
python scripts/seed_dev_database.py

# Create test users and conversations
python scripts/generate_test_data.py --conversations 100
```

**Development database schema:**
```sql
-- Key tables for development
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) UNIQUE,
    buyer_name VARCHAR(255),
    product_name VARCHAR(255),
    state VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ai_responses (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255),
    buyer_message TEXT,
    ai_response TEXT,
    confidence FLOAT,
    risk_score INTEGER,
    source VARCHAR(50),
    personality VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE security_logs (
    id SERIAL PRIMARY KEY,
    message TEXT,
    risk_score INTEGER,
    risk_factors JSONB,
    critical_violations JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Hot Reloading Development

**FastAPI development server with hot reload:**
```bash
# Start development server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# With custom configuration
WALL_E_CONFIG=config/development.yaml uvicorn src.api.main:app --reload
```

**Development configuration for hot reload:**
```yaml
# config/development.yaml
ai_engine:
  mode: hybrid
  debug_mode: true
  enable_profiling: true
  save_prompts: true
  save_responses: true
  
  # Faster iteration
  model_name: phi3.5:3.8b-mini-instruct-q4_0
  max_tokens: 100
  timeout: 15

development:
  hot_reload: true
  auto_restart: true
  debug_toolbar: true
  
logging:
  level: DEBUG
  format: detailed
  enable_sql_logging: true
```

---

## 🎯 Contributing Guidelines

### Git Workflow

**Branch Naming Convention:**
```bash
# Feature branches
feature/ai-engine-performance-optimization
feature/new-fraud-detection-patterns
feature/spanish-conversation-personalities

# Bug fixes
fix/memory-leak-in-llm-manager
fix/rate-limiting-configuration
fix/database-connection-timeout

# Documentation
docs/api-reference-update
docs/installation-guide-improvements

# Performance improvements
perf/concurrent-request-optimization
perf/cache-efficiency-improvements
```

**Commit Message Format:**
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Examples:**
```bash
feat(ai-engine): add Spanish conversation personality system

Implement three distinct seller personalities for AI-generated responses:
- amigable_casual: Informal, friendly tone with moderate emojis
- profesional_cordial: Professional but warm, detailed responses
- vendedor_experimentado: Confident, market-savvy, efficient

- Add personality selection logic based on buyer profile
- Include personality-specific prompt templates
- Add comprehensive test coverage for all personalities
- Update API documentation with personality parameters

Closes #123

fix(security): resolve false positive in PayPal detection

The fraud detection system was incorrectly flagging legitimate PayPal
business transactions. Updated pattern matching to distinguish between
PayPal family/friends (fraud) and PayPal business (legitimate).

- Refine PayPal fraud detection regex patterns
- Add test cases for legitimate PayPal business usage
- Update security documentation

Fixes #456

perf(llm-manager): implement connection pooling for Ollama

Optimize LLM inference performance by implementing connection pooling:
- Reduce connection overhead from 200ms to 20ms per request
- Support up to 8 concurrent connections
- Add automatic connection health monitoring
- Implement graceful connection recovery

Performance impact:
- 40% reduction in average response time
- 60% improvement in concurrent request handling
- Memory usage reduced by 15%

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Pull Request Process

**Pull Request Template:**
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Security enhancement

## AI Engine Changes
- [ ] LLM model modifications
- [ ] Prompt template updates
- [ ] Security/fraud detection changes
- [ ] Performance optimizations
- [ ] Configuration changes

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] AI Engine tests pass
- [ ] Security tests pass
- [ ] Performance benchmarks run

## Documentation
- [ ] Code comments updated
- [ ] API documentation updated
- [ ] README updated
- [ ] CHANGELOG updated

## Deployment Considerations
- [ ] Database migrations required
- [ ] Configuration changes required
- [ ] Environment variable updates needed
- [ ] Docker image rebuild required

## Subagent Usage
Which specialized subagents were used:
- [ ] web-scraper-security
- [ ] test-automation-specialist
- [ ] security-compliance-auditor
- [ ] nlp-fraud-detector
- [ ] performance-optimizer
- [ ] Other: ___________

## Screenshots/Evidence
Add screenshots, performance graphs, or test results if applicable.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No sensitive information exposed
```

### Code Review Guidelines

**For Reviewers:**

1. **Functionality Review:**
   - Does the code solve the intended problem?
   - Are edge cases handled appropriately?
   - Is error handling comprehensive?

2. **AI Engine Specific:**
   - Are security validations maintained?
   - Is performance impact measured and acceptable?
   - Are Spanish language considerations addressed?

3. **Code Quality:**
   - Follows PEP 8 and project conventions
   - Appropriate use of type hints
   - Clear variable and function names
   - Adequate test coverage

4. **Security Review:**
   - No hardcoded secrets or credentials
   - Proper input validation
   - Security patterns not weakened

**Review Checklist:**
```markdown
## Code Review Checklist

### Functionality
- [ ] Code solves the stated problem
- [ ] Edge cases are handled
- [ ] Error handling is comprehensive
- [ ] API contracts are maintained

### AI Engine Specific
- [ ] Security validations preserved
- [ ] Performance impact acceptable
- [ ] Spanish language support maintained
- [ ] Fraud detection not weakened

### Code Quality
- [ ] Follows coding standards
- [ ] Type hints properly used
- [ ] Clear naming conventions
- [ ] Appropriate documentation

### Testing
- [ ] Unit tests cover new functionality
- [ ] Integration tests updated
- [ ] AI Engine tests pass
- [ ] Performance benchmarks acceptable

### Security
- [ ] No hardcoded credentials
- [ ] Input validation present
- [ ] Security patterns maintained
- [ ] Fraud detection tested
```

---

## 🧪 Testing Standards

### Testing Architecture

**Testing Pyramid for Wall-E:**
```
                    /\
                   /  \
                  /E2E \          End-to-End Tests (5%)
                 /Tests\         - Complete user workflows
                /______\        - AI Engine integration
               /        \
              /Integration\      Integration Tests (25%)
             /   Tests    \     - Component interactions
            /______________\    - Database operations
           /                \   - API endpoint testing
          /   Unit Tests     \  Unit Tests (70%)
         /                    \ - Individual functions
        /______________________\ - Mocked dependencies
```

### Test Categories

#### Unit Tests (70% of test suite)

**Example: AI Engine Unit Test**
```python
# tests/ai_engine/test_response_generator.py
import pytest
from unittest.mock import Mock, AsyncMock
from src.ai_engine.response_generator import AIResponseGenerator
from src.ai_engine.config import AIEngineConfig

class TestAIResponseGenerator:
    def setup_method(self):
        """Set up test fixtures"""
        self.config = AIEngineConfig.for_research()
        self.mock_llm_manager = Mock()
        self.generator = AIResponseGenerator(
            config=self.config,
            llm_manager=self.mock_llm_manager
        )
    
    def test_generate_response_success(self):
        """Test successful response generation"""
        # Arrange
        self.mock_llm_manager.generate.return_value = {
            "response": "¡Hola! Sí, está disponible.",
            "confidence": 0.92,
            "tokens_used": 24
        }
        
        request = ConversationRequest(
            buyer_message="¿Está disponible?",
            buyer_name="TestBuyer",
            product_name="iPhone 12",
            price=400
        )
        
        # Act
        result = self.generator.generate_response(request)
        
        # Assert
        assert result.response_text == "¡Hola! Sí, está disponible."
        assert result.confidence == 0.92
        assert result.source == "ai_engine"
        assert result.tokens_generated == 24
        
        # Verify LLM manager was called correctly
        self.mock_llm_manager.generate.assert_called_once()
        call_args = self.mock_llm_manager.generate.call_args[0][0]
        assert "iPhone 12" in call_args
        assert "TestBuyer" in call_args
    
    def test_generate_response_with_personality(self):
        """Test response generation with specific personality"""
        # Arrange
        self.mock_llm_manager.generate.return_value = {
            "response": "Buenos días. Sí, está disponible.",
            "confidence": 0.89,
            "tokens_used": 18
        }
        
        request = ConversationRequest(
            buyer_message="¿Está disponible?",
            buyer_name="TestBuyer",
            product_name="iPhone 12",
            price=400,
            personality="profesional_cordial"
        )
        
        # Act
        result = self.generator.generate_response(request)
        
        # Assert
        assert "Buenos días" in result.response_text
        assert result.personality_used == "profesional_cordial"
    
    @pytest.mark.asyncio
    async def test_generate_response_timeout(self):
        """Test timeout handling"""
        # Arrange
        self.mock_llm_manager.generate = AsyncMock(
            side_effect=asyncio.TimeoutError("Generation timeout")
        )
        
        request = ConversationRequest(
            buyer_message="¿Está disponible?",
            buyer_name="TestBuyer",
            product_name="iPhone 12",
            price=400
        )
        
        # Act & Assert
        with pytest.raises(GenerationTimeoutError):
            await self.generator.generate_response_async(request)
    
    def test_spanish_language_validation(self):
        """Test that responses are in proper Spanish"""
        # This test ensures AI responses maintain Spanish language quality
        responses_to_test = [
            "¡Hola! Sí, está disponible. ¿Te interesa?",
            "Buenos días. El precio es 400€ como aparece en el anuncio.",
            "Perfecto. ¿Cuándo te viene bien quedar?"
        ]
        
        for response in responses_to_test:
            # Validate Spanish grammar markers
            assert any(marker in response.lower() for marker in ["está", "es", "son", "¿", "¡"])
            # Validate no English artifacts
            assert not any(word in response.lower() for word in ["the", "and", "is", "are"])
```

#### Integration Tests (25% of test suite)

**Example: AI Engine Integration Test**
```python
# tests/integration/test_ai_engine_integration.py
import pytest
from src.ai_engine import AIEngine, AIEngineConfig
from src.ai_engine.ai_engine import ConversationRequest

@pytest.mark.integration
class TestAIEngineIntegration:
    @pytest.fixture(scope="class")
    def ai_engine(self):
        """Create AI Engine for integration testing"""
        config = AIEngineConfig.for_research()
        engine = AIEngine(config)
        yield engine
    
    def test_full_conversation_flow(self, ai_engine):
        """Test complete conversation flow with real AI Engine"""
        # Test greeting
        request = ConversationRequest(
            buyer_message="¡Hola! ¿Está disponible el iPhone?",
            buyer_name="IntegrationTestBuyer",
            product_name="iPhone 12",
            price=400
        )
        
        response = ai_engine.generate_response(request)
        
        assert response.response_text is not None
        assert len(response.response_text) > 10
        assert response.confidence > 0.0
        assert response.risk_score >= 0
        assert response.source in ["ai_engine", "template", "fraud_protection"]
        
        # Test follow-up question
        follow_up = ConversationRequest(
            buyer_message="¿Cuál es el estado exacto?",
            buyer_name="IntegrationTestBuyer",
            product_name="iPhone 12",
            price=400,
            conversation_history=[
                {"role": "buyer", "message": request.buyer_message},
                {"role": "seller", "message": response.response_text}
            ]
        )
        
        response2 = ai_engine.generate_response(follow_up)
        
        assert response2.response_text != response.response_text  # Different responses
        assert "estado" in response2.response_text.lower() or "condición" in response2.response_text.lower()
    
    def test_fraud_detection_integration(self, ai_engine):
        """Test fraud detection in real AI Engine"""
        fraud_request = ConversationRequest(
            buyer_message="¿Acepta pago por Western Union?",
            buyer_name="SuspiciousBuyer",
            product_name="iPhone 12",
            price=400
        )
        
        response = ai_engine.generate_response(fraud_request)
        
        assert response.risk_score >= 50  # High risk
        assert response.source == "fraud_protection"
        assert "efectivo" in response.response_text.lower() or "bizum" in response.response_text.lower()
    
    def test_performance_requirements(self, ai_engine):
        """Test that performance requirements are met"""
        import time
        
        request = ConversationRequest(
            buyer_message="¿Acepta cambios?",
            buyer_name="PerformanceTestBuyer",
            product_name="iPhone 12",
            price=400
        )
        
        start_time = time.time()
        response = ai_engine.generate_response(request)
        response_time = time.time() - start_time
        
        assert response_time < 5.0  # Should respond within 5 seconds
        assert response.response_time < 5.0
        
        # Test concurrent requests
        import asyncio
        async def concurrent_test():
            tasks = [
                ai_engine.generate_response_async(request)
                for _ in range(5)
            ]
            responses = await asyncio.gather(*tasks)
            return responses
        
        start_time = time.time()
        responses = asyncio.run(concurrent_test())
        total_time = time.time() - start_time
        
        assert len(responses) == 5
        assert all(r.response_text for r in responses)
        assert total_time < 10.0  # 5 concurrent requests in under 10 seconds
```

#### End-to-End Tests (5% of test suite)

**Example: Complete User Workflow Test**
```python
# tests/e2e/test_complete_workflow.py
import pytest
from src.bot.wallapop_bot import WallapopBot
from src.conversation_engine.ai_enhanced_engine import AIEnhancedConversationEngine

@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteWorkflow:
    def test_buyer_to_seller_conversation_flow(self):
        """Test complete conversation from initial contact to sale coordination"""
        # This would test the entire flow in a realistic scenario
        # Note: This test might use mocked external services
        
        bot = WallapopBot()
        
        # Simulate incoming message
        buyer_message = "¡Hola! Estoy interesado en el iPhone 12. ¿Está disponible?"
        buyer_profile = {
            "name": "Juan García",
            "rating": 4.5,
            "ratings_count": 15,
            "location": "Madrid"
        }
        product_info = {
            "name": "iPhone 12",
            "price": 450,
            "condition": "muy buen estado"
        }
        
        # Process through complete system
        result = bot.process_incoming_message(
            conversation_id="e2e_test_conv_001",
            message=buyer_message,
            buyer_info=buyer_profile,
            product_info=product_info
        )
        
        # Validate response
        assert result.success
        assert result.response_sent
        assert result.conversation_state is not None
        assert result.risk_assessment["level"] == "LOW"
        
        # Continue conversation with price negotiation
        negotiation_message = "¿Acepta 400€?"
        
        result2 = bot.process_incoming_message(
            conversation_id="e2e_test_conv_001",
            message=negotiation_message,
            buyer_info=buyer_profile,
            product_info=product_info
        )
        
        assert result2.success
        assert "negociación" in result2.conversation_state.lower() or "comprometido" in result2.conversation_state.lower()
        
        # Test coordination phase
        coordination_message = "Perfecto. ¿Cuándo podemos quedar?"
        
        result3 = bot.process_incoming_message(
            conversation_id="e2e_test_conv_001",
            message=coordination_message,
            buyer_info=buyer_profile,
            product_info=product_info
        )
        
        assert result3.success
        assert "coordinando" in result3.conversation_state.lower()
        assert any(place in result3.response.lower() for place in ["metro", "centro", "plaza"])
```

### Test Utilities and Fixtures

**Common Test Fixtures (`tests/conftest.py`):**
```python
import pytest
import asyncio
from src.ai_engine import AIEngine, AIEngineConfig
from src.database.db_manager import DatabaseManager

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def ai_config():
    """Create AI Engine configuration for testing"""
    return AIEngineConfig(
        mode=AIEngineMode.HYBRID,
        model_name="phi3.5:3.8b-mini-instruct-q4_0",  # Lightweight for testing
        timeout=10,
        max_concurrent_requests=2,
        debug_mode=True,
        enable_caching=False  # Disable caching for consistent tests
    )

@pytest.fixture
def mock_ai_engine(ai_config):
    """Create mocked AI Engine for unit tests"""
    with patch('src.ai_engine.llm_manager.LLMManager') as mock_llm:
        mock_llm.return_value.generate.return_value = {
            "response": "Test response",
            "confidence": 0.85,
            "tokens_used": 20
        }
        
        engine = AIEngine(ai_config)
        yield engine

@pytest.fixture(scope="session")
def test_database():
    """Create test database for integration tests"""
    db_manager = DatabaseManager("postgresql://wall_e:test@localhost:5432/wall_e_test")
    db_manager.create_all_tables()
    yield db_manager
    db_manager.drop_all_tables()

@pytest.fixture
def sample_conversation_request():
    """Create sample conversation request for testing"""
    return ConversationRequest(
        buyer_message="¿Está disponible el producto?",
        buyer_name="TestBuyer",
        product_name="Test Product",
        price=100,
        personality="profesional_cordial"
    )

@pytest.fixture
def spanish_test_messages():
    """Provide Spanish test messages for language testing"""
    return {
        "greetings": [
            "¡Hola! ¿Cómo estás?",
            "Buenos días, ¿está disponible?",
            "Buenas tardes, me interesa el producto"
        ],
        "price_questions": [
            "¿Cuál es el precio final?",
            "¿Acepta 300€?",
            "¿Es negociable el precio?"
        ],
        "fraud_patterns": [
            "¿Acepta pago por Western Union?",
            "Mi primo puede recogerlo",
            "¿Me da su DNI?"
        ]
    }
```

### Performance Testing

**Performance Test Example:**
```python
# tests/performance/test_ai_engine_performance.py
import pytest
import time
import asyncio
from src.ai_engine import AIEngine, AIEngineConfig

@pytest.mark.performance
class TestAIEnginePerformance:
    def test_response_time_benchmark(self):
        """Benchmark single request response time"""
        config = AIEngineConfig.for_research()
        engine = AIEngine(config)
        
        request = ConversationRequest(
            buyer_message="¿Está disponible?",
            buyer_name="BenchmarkBuyer",
            product_name="iPhone 12",
            price=400
        )
        
        # Warm up
        engine.generate_response(request)
        
        # Benchmark
        times = []
        for _ in range(10):
            start = time.time()
            response = engine.generate_response(request)
            end = time.time()
            times.append(end - start)
            
            assert response.response_text is not None
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # Performance assertions
        assert avg_time < 3.0, f"Average response time {avg_time:.2f}s exceeds 3s limit"
        assert max_time < 5.0, f"Max response time {max_time:.2f}s exceeds 5s limit"
        
        print(f"Average response time: {avg_time:.2f}s")
        print(f"Max response time: {max_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self):
        """Test performance under concurrent load"""
        config = AIEngineConfig.for_research()
        engine = AIEngine(config)
        
        requests = [
            ConversationRequest(
                buyer_message=f"Mensaje de prueba {i}",
                buyer_name=f"Buyer{i}",
                product_name="Test Product",
                price=100
            )
            for i in range(10)
        ]
        
        start = time.time()
        
        # Execute concurrent requests
        tasks = [engine.generate_response_async(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        
        end = time.time()
        total_time = end - start
        
        # Validate all responses
        assert len(responses) == 10
        assert all(r.response_text for r in responses)
        
        # Performance assertions
        assert total_time < 15.0, f"10 concurrent requests took {total_time:.2f}s (limit: 15s)"
        
        avg_response_time = sum(r.response_time for r in responses) / len(responses)
        assert avg_response_time < 5.0, f"Average response time {avg_response_time:.2f}s too high"
        
        print(f"10 concurrent requests completed in {total_time:.2f}s")
        print(f"Average individual response time: {avg_response_time:.2f}s")
```

---

## 📚 Code Standards

### Python Coding Standards

**Follow PEP 8 with these project-specific guidelines:**

#### Type Hints
```python
# Required for all public functions and methods
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass

@dataclass
class ConversationRequest:
    buyer_message: str
    buyer_name: str
    product_name: str
    price: float
    conversation_history: List[Dict[str, Any]] = None
    buyer_profile: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        if self.conversation_history is None:
            self.conversation_history = []

def generate_response(
    request: ConversationRequest,
    config: AIEngineConfig
) -> ConversationResponse:
    """
    Generate AI-powered conversation response.
    
    Args:
        request: Conversation request with buyer message and context
        config: AI Engine configuration
        
    Returns:
        ConversationResponse with generated text and metadata
        
    Raises:
        GenerationError: When AI generation fails
        ValidationError: When response validation fails
    """
    pass
```

#### Error Handling
```python
# Use specific exception types
class AIEngineError(Exception):
    """Base exception for AI Engine errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        super().__init__(self.message)

class GenerationTimeoutError(AIEngineError):
    """Raised when AI generation times out"""
    pass

# Proper exception handling
try:
    response = ai_engine.generate_response(request)
except GenerationTimeoutError as e:
    logger.warning(f"Generation timeout: {e}")
    response = fallback_handler.generate_fallback(request)
except AIEngineError as e:
    logger.error(f"AI Engine error: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise AIEngineError(f"Unexpected error: {e}")
```

#### Async/Await Patterns
```python
# Proper async patterns
async def process_conversation_async(
    message: str,
    buyer: BuyerProfile,
    product: ProductInfo
) -> ConversationResult:
    """Process conversation with async operations"""
    
    # Use async context managers
    async with DatabaseManager() as db:
        # Use asyncio.gather for concurrent operations
        analysis_task = asyncio.create_task(analyze_intent(message))
        ai_task = asyncio.create_task(generate_ai_response(message))
        
        intent_result, ai_response = await asyncio.gather(
            analysis_task,
            ai_task,
            return_exceptions=True
        )
        
        # Handle potential exceptions
        if isinstance(intent_result, Exception):
            logger.error(f"Intent analysis failed: {intent_result}")
            intent_result = default_intent()
        
        if isinstance(ai_response, Exception):
            logger.error(f"AI generation failed: {ai_response}")
            ai_response = fallback_response()
        
        # Save to database
        await db.save_conversation(message, ai_response, intent_result)
        
        return ConversationResult(
            response=ai_response.text,
            intent=intent_result.intent,
            confidence=ai_response.confidence
        )

# Use proper timeout handling
async def with_timeout(coro, timeout: float):
    """Helper for timeout handling"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise GenerationTimeoutError(f"Operation timed out after {timeout}s")
```

#### Logging Standards
```python
import logging
import structlog

# Use structured logging
logger = structlog.get_logger(__name__)

def process_request(request: ConversationRequest) -> ConversationResponse:
    """Example of proper logging"""
    
    # Log with context
    logger.info(
        "Processing conversation request",
        buyer_name=request.buyer_name,
        product_name=request.product_name,
        personality=request.personality,
        request_id=request.request_id
    )
    
    try:
        response = generate_response(request)
        
        # Log success with metrics
        logger.info(
            "Conversation response generated",
            request_id=request.request_id,
            response_time=response.response_time,
            confidence=response.confidence,
            risk_score=response.risk_score,
            source=response.source
        )
        
        return response
        
    except Exception as e:
        # Log error with full context
        logger.error(
            "Failed to generate conversation response",
            request_id=request.request_id,
            buyer_name=request.buyer_name,
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

### Documentation Standards

#### Docstring Format
```python
def analyze_fraud_patterns(
    message: str, 
    buyer_profile: Optional[Dict] = None
) -> ValidationResult:
    """
    Analyze message for fraud patterns using multi-layer detection.
    
    This function implements a comprehensive fraud detection system that
    examines the buyer's message for known fraud patterns, contextual
    risk factors, and behavioral indicators.
    
    Args:
        message: The buyer's message to analyze for fraud patterns
        buyer_profile: Optional buyer profile information including:
            - ratings_count: Number of ratings (int)
            - avg_rating: Average rating (float)
            - account_age: Account age in days (int)
            - location: Buyer location (str)
    
    Returns:
        ValidationResult containing:
            - is_safe: Whether the message is considered safe (bool)
            - risk_score: Risk score from 0-100 (int)
            - risk_factors: List of detected risk factors (List[str])
            - critical_violations: Critical fraud patterns found (List[str])
            - recommendations: Security recommendations (List[str])
    
    Raises:
        ValidationError: When validation process fails
        ConfigurationError: When fraud detection patterns are invalid
    
    Example:
        >>> result = analyze_fraud_patterns("¿Acepta Western Union?")
        >>> print(result.risk_score)
        100
        >>> print(result.critical_violations)
        ['western_union_payment']
    
    Note:
        This function uses Spanish language NLP models and is optimized
        for Wallapop marketplace fraud patterns.
    """
    pass
```

#### Code Comments
```python
class AIResponseGenerator:
    """Generates AI-powered conversation responses with validation."""
    
    def __init__(self, config: AIEngineConfig, llm_manager: LLMManager):
        self.config = config
        self.llm_manager = llm_manager
        
        # Initialize prompt templates for Spanish conversations
        self.prompt_templates = SpanishPromptTemplates()
        
        # Set up retry mechanism for failed generations
        self.max_retries = config.max_retries or 3
        self.retry_delay = 1.0  # seconds
    
    def _build_prompt(self, request: ConversationRequest) -> str:
        """
        Build context-aware prompt for AI generation.
        
        Constructs a prompt that includes:
        - Seller personality instructions
        - Product context and pricing
        - Buyer profile information
        - Conversation history
        - Spanish language guidelines
        """
        # Select appropriate personality template
        personality = request.personality or self.config.default_personality
        template = self.prompt_templates.get_personality_template(personality)
        
        # Build context dictionary for template rendering
        context = {
            'buyer_name': request.buyer_name,
            'product_name': request.product_name,
            'price': request.price,
            'condition': request.condition,
            'conversation_history': request.conversation_history,
            'personality_instructions': template.instructions,
            'example_responses': template.examples
        }
        
        # Render template with context
        return template.render(context)
```

### Configuration Management

#### Configuration Classes
```python
@dataclass
class AIEngineConfig:
    """Configuration for AI Engine with validation and factory methods."""
    
    # Core AI settings
    mode: AIEngineMode = AIEngineMode.AI_FIRST
    model_name: str = "llama3.2:11b-vision-instruct-q4_0"
    temperature: float = 0.7
    max_tokens: int = 200
    timeout: int = 30
    
    # Performance settings
    max_concurrent_requests: int = 10
    connection_pool_size: int = 5
    memory_threshold_mb: int = 12000
    
    # Security settings
    fraud_detection_threshold: int = 25
    critical_fraud_threshold: int = 50
    enable_url_analysis: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate configuration parameters.
        
        Raises:
            ConfigurationError: When configuration is invalid
        """
        errors = []
        
        if not 0.0 <= self.temperature <= 2.0:
            errors.append("temperature must be between 0.0 and 2.0")
        
        if self.max_tokens < 10 or self.max_tokens > 1000:
            errors.append("max_tokens must be between 10 and 1000")
        
        if self.timeout < 5 or self.timeout > 120:
            errors.append("timeout must be between 5 and 120 seconds")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {', '.join(errors)}")
    
    @classmethod
    def for_research(cls) -> 'AIEngineConfig':
        """Create configuration optimized for research and development."""
        return cls(
            mode=AIEngineMode.AI_FIRST,
            fraud_detection_threshold=25,
            debug_mode=True,
            enable_profiling=True
        )
    
    @classmethod
    def for_compliance(cls) -> 'AIEngineConfig':
        """Create configuration optimized for commercial compliance."""
        return cls(
            mode=AIEngineMode.AI_FIRST,
            fraud_detection_threshold=20,  # Stricter
            strict_validation=True,
            audit_all_responses=True
        )
```

---

## 🤖 AI Engine Development

### LLM Integration Guidelines

#### Working with Ollama
```python
class LLMManager:
    """Manages Ollama LLM integration with connection pooling and caching."""
    
    def __init__(self, config: AIEngineConfig):
        self.config = config
        self.connection_pool = ConnectionPool(
            host=config.ollama_host,
            pool_size=config.connection_pool_size
        )
        self.cache = LRUCache(maxsize=config.cache_size)
        
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate response using Ollama with caching and error handling.
        
        Args:
            prompt: The input prompt for generation
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing:
                - response: Generated text
                - confidence: Confidence score
                - tokens_used: Number of tokens consumed
                - model_name: Model used for generation
        """
        # Check cache first
        cache_key = self._generate_cache_key(prompt, kwargs)
        if cached_result := self.cache.get(cache_key):
            return cached_result
        
        # Get connection from pool
        client = await self.connection_pool.get_connection()
        
        try:
            # Prepare request
            request_data = {
                'model': self.config.model_name,
                'prompt': prompt,
                'options': {
                    'temperature': kwargs.get('temperature', self.config.temperature),
                    'num_predict': kwargs.get('max_tokens', self.config.max_tokens),
                    'top_p': kwargs.get('top_p', 0.9),
                    'top_k': kwargs.get('top_k', 40)
                }
            }
            
            # Make request with timeout
            response = await asyncio.wait_for(
                client.generate(**request_data),
                timeout=self.config.timeout
            )
            
            # Process response
            result = {
                'response': response['response'],
                'confidence': self._calculate_confidence(response),
                'tokens_used': response.get('eval_count', 0),
                'model_name': self.config.model_name,
                'generation_time': response.get('total_duration', 0) / 1e9  # Convert to seconds
            }
            
            # Cache result
            self.cache.set(cache_key, result)
            
            return result
            
        except asyncio.TimeoutError:
            raise GenerationTimeoutError(f"Generation timed out after {self.config.timeout}s")
        except Exception as e:
            raise GenerationError(f"LLM generation failed: {e}")
        finally:
            # Return connection to pool
            await self.connection_pool.return_connection(client)
    
    def _calculate_confidence(self, response: Dict) -> float:
        """Calculate confidence score based on response metadata."""
        # Implementation depends on available response metadata
        # This is a simplified example
        if 'eval_duration' in response and 'eval_count' in response:
            avg_token_time = response['eval_duration'] / response['eval_count']
            # Lower token generation time often indicates higher confidence
            confidence = max(0.0, min(1.0, 1.0 - (avg_token_time / 1e9)))
            return confidence
        
        return 0.8  # Default confidence
```

#### Prompt Engineering for Spanish
```python
class SpanishPromptTemplates:
    """Manages Spanish conversation prompts with personality support."""
    
    def __init__(self):
        self.personalities = self._load_personalities()
        self.conversation_contexts = self._load_contexts()
    
    def get_personality_template(self, personality: str) -> PromptTemplate:
        """Get prompt template for specific personality."""
        if personality not in self.personalities:
            raise ValueError(f"Unknown personality: {personality}")
        
        return self.personalities[personality]
    
    def build_conversation_prompt(
        self,
        buyer_message: str,
        context: Dict[str, Any],
        personality: str = "profesional_cordial"
    ) -> str:
        """
        Build complete conversation prompt with Spanish language optimization.
        
        This method constructs prompts that:
        - Maintain authentic Spanish conversation flow
        - Include regional expressions and colloquialisms
        - Respect Spanish grammar and syntax rules
        - Adapt to seller personality and buyer context
        """
        personality_template = self.get_personality_template(personality)
        
        # Build base prompt with Spanish language instructions
        base_prompt = """
Eres un vendedor español en Wallapop que responde de manera natural y auténtica.

PERSONALIDAD: {personality_name}
DESCRIPCIÓN: {personality_description}
TONO: {personality_tone}

CONTEXTO DE LA VENTA:
- Producto: {product_name}
- Precio: {price}€
- Estado: {condition}
- Ubicación: {location}

INFORMACIÓN DEL COMPRADOR:
- Nombre: {buyer_name}
- Mensaje: "{buyer_message}"

INSTRUCCIONES ESPECÍFICAS:
{personality_instructions}

EJEMPLOS DE RESPUESTAS DE ESTA PERSONALIDAD:
{personality_examples}

REGLAS IMPORTANTES:
1. Responde ÚNICAMENTE en español de España
2. Usa expresiones naturales españolas
3. Mantén el tono de la personalidad asignada
4. NO menciones métodos de pago no seguros
5. NO compartas información personal
6. Respuesta debe ser concisa (máximo 2-3 líneas)

RESPUESTA DEL VENDEDOR:
"""
        
        # Fill template with context
        return base_prompt.format(
            personality_name=personality_template.name,
            personality_description=personality_template.description,
            personality_tone=personality_template.tone,
            personality_instructions=personality_template.instructions,
            personality_examples="\n".join(personality_template.examples),
            product_name=context['product_name'],
            price=context['price'],
            condition=context.get('condition', 'buen estado'),
            location=context.get('location', 'Madrid'),
            buyer_name=context['buyer_name'],
            buyer_message=buyer_message
        )
    
    def _load_personalities(self) -> Dict[str, PromptTemplate]:
        """Load personality templates with Spanish conversation patterns."""
        return {
            "amigable_casual": PromptTemplate(
                name="Amigable Casual",
                description="Vendedor cercano e informal que usa emojis moderadamente",
                tone="informal, cercano, empático",
                instructions=[
                    "Usa tratamiento de 'tú'",
                    "Incluye emojis ocasionales (😊, 👍, ✨)",
                    "Expresiones como 'venga', 'vale', 'genial'",
                    "Tono conversacional y relajado"
                ],
                examples=[
                    "¡Hola! 😊 Sí, está disponible. ¿Te gusta lo que ves?",
                    "¡Claro que sí! Sin problema para quedar",
                    "Vale, perfecto. ¿Te va bien el sábado?"
                ]
            ),
            
            "profesional_cordial": PromptTemplate(
                name="Profesional Cordial",
                description="Vendedor educado y profesional pero cercano",
                tone="cortés, informativo, servicial",
                instructions=[
                    "Trato educado sin ser excesivamente formal",
                    "Información clara y detallada",
                    "Emojis mínimos y estratégicos",
                    "Enfoque en generar confianza"
                ],
                examples=[
                    "Buenos días. Sí, está disponible. El estado es excelente.",
                    "Por supuesto, incluye todos los accesorios originales.",
                    "Perfecto. ¿Le va bien quedar en zona centro?"
                ]
            ),
            
            "vendedor_experimentado": PromptTemplate(
                name="Vendedor Experimentado",
                description="Vendedor con conocimiento del mercado, seguro y eficiente",
                tone="seguro, conocedor, pragmático",
                instructions=[
                    "Muestra experiencia en Wallapop",
                    "Referencias al mercado y valoraciones",
                    "Directo pero no agresivo",
                    "Eficiente en cerrar ventas"
                ],
                examples=[
                    "Según mi experiencia, está muy bien de precio para el estado que tiene.",
                    "He vendido muchos iguales. Tengo 47 valoraciones positivas.",
                    "Para ese precio tengo otros interesados. Necesito decisión rápida."
                ]
            )
        }
```

### Security Integration

#### Fraud Detection Development
```python
class FraudPatternMatcher:
    """Advanced fraud pattern matching with Spanish language support."""
    
    def __init__(self, config: AIEngineConfig):
        self.config = config
        self.patterns = self._load_fraud_patterns()
        self.nlp = spacy.load("es_core_news_sm")
        
    def analyze_message(self, message: str, context: Dict = None) -> FraudAnalysis:
        """
        Analyze message for fraud patterns with contextual understanding.
        
        This method performs:
        1. Direct pattern matching for known fraud keywords
        2. NLP analysis for semantic fraud detection
        3. Contextual risk assessment based on buyer profile
        4. URL analysis for phishing attempts
        """
        analysis = FraudAnalysis(message=message)
        
        # Step 1: Direct pattern matching
        self._check_critical_patterns(message, analysis)
        
        # Step 2: NLP semantic analysis
        self._analyze_semantic_patterns(message, analysis)
        
        # Step 3: Contextual risk assessment
        if context:
            self._assess_contextual_risk(message, context, analysis)
        
        # Step 4: URL analysis
        self._analyze_urls(message, analysis)
        
        # Calculate final risk score
        analysis.calculate_final_score()
        
        return analysis
    
    def _check_critical_patterns(self, message: str, analysis: FraudAnalysis):
        """Check for critical fraud patterns that require immediate blocking."""
        message_lower = message.lower()
        
        # Payment method fraud
        payment_patterns = [
            r'western\s+union',
            r'money\s*gram',
            r'paypal\s+(familia|friends|amigos)',
            r'bitcoin|ethereum|cripto',
            r'transferencia\s+sin\s+seguro'
        ]
        
        for pattern in payment_patterns:
            if re.search(pattern, message_lower):
                analysis.add_critical_violation(
                    pattern="payment_fraud",
                    matched_text=re.search(pattern, message_lower).group(),
                    risk_points=50
                )
        
        # Personal data fishing
        data_patterns = [
            r'\b(dni|nif)\b',
            r'numero\s+(tarjeta|cuenta)',
            r'\b(cvv|pin)\b',
            r'contraseña|password'
        ]
        
        for pattern in data_patterns:
            if re.search(pattern, message_lower):
                analysis.add_critical_violation(
                    pattern="data_fishing",
                    matched_text=re.search(pattern, message_lower).group(),
                    risk_points=50
                )
    
    def _analyze_semantic_patterns(self, message: str, analysis: FraudAnalysis):
        """Use NLP to detect semantic fraud patterns."""
        doc = self.nlp(message)
        
        # Analyze for urgency pressure
        urgency_keywords = ['urgente', 'inmediatamente', 'rápido', 'ya', 'ahora']
        urgency_count = sum(1 for token in doc if token.lemma_ in urgency_keywords)
        
        if urgency_count >= 2:
            analysis.add_risk_factor(
                factor="urgency_pressure",
                description="Multiple urgency indicators detected",
                risk_points=15
            )
        
        # Analyze for third-party pickup
        third_party_patterns = ['hermano', 'primo', 'amigo', 'otra persona']
        for pattern in third_party_patterns:
            if pattern in message.lower():
                analysis.add_risk_factor(
                    factor="third_party_pickup",
                    description=f"Third party pickup indicator: {pattern}",
                    risk_points=20
                )
    
    def _assess_contextual_risk(self, message: str, context: Dict, analysis: FraudAnalysis):
        """Assess risk based on buyer profile and conversation context."""
        buyer_profile = context.get('buyer_profile', {})
        
        # New account with no ratings
        if buyer_profile.get('ratings_count', 0) == 0:
            analysis.add_risk_factor(
                factor="new_account",
                description="Buyer has no ratings",
                risk_points=10
            )
        
        # Low rating
        if buyer_profile.get('avg_rating', 5.0) < 3.0:
            analysis.add_risk_factor(
                factor="low_rating",
                description=f"Low buyer rating: {buyer_profile['avg_rating']}",
                risk_points=15
            )
        
        # Distant location
        distance = buyer_profile.get('distance', 0)
        if distance > 100:  # km
            analysis.add_risk_factor(
                factor="distant_location",
                description=f"Buyer is {distance}km away",
                risk_points=10
            )
```

---

## 🔌 API Development

### FastAPI Integration

#### Endpoint Development
```python
# src/api/endpoints/conversation.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from src.ai_engine import AIEngine, AIEngineConfig
from src.api.models import ConversationRequest, ConversationResponse
from src.api.auth import verify_api_key
from src.api.rate_limit import rate_limit

router = APIRouter(prefix="/api/v2/conversation", tags=["conversation"])
security = HTTPBearer()

@router.post("/generate", response_model=ConversationResponse)
@rate_limit(max_requests=60, window_seconds=60)
async def generate_conversation_response(
    request: ConversationRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
    ai_engine: AIEngine = Depends(get_ai_engine)
) -> ConversationResponse:
    """
    Generate AI-powered conversation response.
    
    This endpoint provides natural Spanish conversation generation
    with built-in fraud detection and security validation.
    """
    try:
        # Convert API request to internal format
        internal_request = request.to_internal_format()
        
        # Generate response using AI Engine
        ai_response = await ai_engine.generate_response_async(internal_request)
        
        # Convert to API response format
        api_response = ConversationResponse.from_internal(ai_response)
        
        # Log request for analytics (background task)
        background_tasks.add_task(
            log_conversation_request,
            request=request,
            response=api_response,
            api_key=api_key
        )
        
        return api_response
        
    except GenerationTimeoutError as e:
        raise HTTPException(
            status_code=408,
            detail={
                "error": "Generation timeout",
                "message": str(e),
                "fallback_available": True
            }
        )
    except FraudDetectedError as e:
        # Return security response instead of error
        security_response = ConversationResponse(
            response_text="Lo siento, solo acepto efectivo o Bizum en persona.",
            confidence=1.0,
            risk_score=100,
            source="fraud_protection",
            security_info={
                "blocked": True,
                "reason": str(e),
                "risk_factors": e.details.get("risk_factors", [])
            }
        )
        
        # Still log for security analysis
        background_tasks.add_task(
            log_security_incident,
            request=request,
            fraud_details=e.details,
            api_key=api_key
        )
        
        return security_response
        
    except AIEngineError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "AI Engine error",
                "message": str(e),
                "error_code": e.error_code
            }
        )

@router.post("/batch", response_model=BatchConversationResponse)
@rate_limit(max_requests=10, window_seconds=60)
async def batch_generate_responses(
    batch_request: BatchConversationRequest,
    api_key: str = Depends(verify_api_key),
    ai_engine: AIEngine = Depends(get_ai_engine)
) -> BatchConversationResponse:
    """
    Process multiple conversation requests concurrently.
    
    Efficiently handles multiple conversations with proper
    error handling and performance optimization.
    """
    # Validate batch size
    if len(batch_request.conversations) > 20:
        raise HTTPException(
            status_code=400,
            detail="Batch size cannot exceed 20 conversations"
        )
    
    # Convert to internal format
    internal_requests = [
        conv.to_internal_format() 
        for conv in batch_request.conversations
    ]
    
    # Process concurrently
    tasks = [
        ai_engine.generate_response_async(req)
        for req in internal_requests
    ]
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    api_responses = []
    for i, response in enumerate(responses):
        if isinstance(response, Exception):
            # Handle individual failures
            api_responses.append(ConversationResponse(
                response_text="Error processing request",
                confidence=0.0,
                risk_score=0,
                source="error",
                error=str(response)
            ))
        else:
            api_responses.append(ConversationResponse.from_internal(response))
    
    return BatchConversationResponse(
        responses=api_responses,
        total_count=len(api_responses),
        success_count=sum(1 for r in api_responses if not r.error),
        processing_time=sum(r.response_time for r in api_responses if r.response_time)
    )
```

#### API Models
```python
# src/api/models.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class ConversationRequest(BaseModel):
    """API model for conversation requests."""
    
    buyer_message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The buyer's message to respond to"
    )
    buyer_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Buyer's name or identifier"
    )
    product_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the product being sold"
    )
    price: float = Field(
        ...,
        gt=0,
        le=100000,
        description="Product price in euros"
    )
    personality: Optional[str] = Field(
        "profesional_cordial",
        regex="^(amigable_casual|profesional_cordial|vendedor_experimentado)$",
        description="Seller personality to use"
    )
    buyer_profile: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional buyer profile information"
    )
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Previous messages in conversation"
    )
    
    @validator('buyer_message')
    def validate_message_content(cls, v):
        """Validate message content for basic safety."""
        # Basic content validation
        if not v.strip():
            raise ValueError("Message cannot be empty")
        
        # Check for obviously malicious content
        malicious_patterns = ['<script', 'javascript:', 'data:']
        if any(pattern in v.lower() for pattern in malicious_patterns):
            raise ValueError("Message contains potentially malicious content")
        
        return v.strip()
    
    @validator('conversation_history')
    def validate_conversation_history(cls, v):
        """Validate conversation history format."""
        if v is None:
            return v
        
        if len(v) > 50:  # Limit history size
            raise ValueError("Conversation history too long (max 50 messages)")
        
        for message in v:
            if not isinstance(message, dict):
                raise ValueError("Each message must be a dictionary")
            
            required_keys = {'role', 'message'}
            if not required_keys.issubset(message.keys()):
                raise ValueError("Each message must have 'role' and 'message' keys")
            
            if message['role'] not in ['buyer', 'seller']:
                raise ValueError("Message role must be 'buyer' or 'seller'")
        
        return v
    
    def to_internal_format(self) -> 'InternalConversationRequest':
        """Convert API request to internal format."""
        from src.ai_engine.ai_engine import ConversationRequest as InternalRequest
        
        return InternalRequest(
            buyer_message=self.buyer_message,
            buyer_name=self.buyer_name,
            product_name=self.product_name,
            price=self.price,
            personality=self.personality,
            buyer_profile=self.buyer_profile,
            conversation_history=self.conversation_history or []
        )

class ConversationResponse(BaseModel):
    """API model for conversation responses."""
    
    response_text: str = Field(..., description="Generated response text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Response confidence score")
    risk_score: int = Field(..., ge=0, le=100, description="Fraud risk score")
    source: str = Field(..., description="Response source (ai_engine, template, fraud_protection)")
    response_time: Optional[float] = Field(None, description="Response generation time in seconds")
    personality_used: Optional[str] = Field(None, description="Actual personality used")
    
    # Security information
    security_info: Optional[Dict[str, Any]] = Field(None, description="Security analysis details")
    
    # Error information
    error: Optional[str] = Field(None, description="Error message if processing failed")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_internal(cls, internal_response) -> 'ConversationResponse':
        """Convert internal response to API format."""
        return cls(
            response_text=internal_response.response_text,
            confidence=internal_response.confidence,
            risk_score=internal_response.risk_score,
            source=internal_response.source,
            response_time=internal_response.response_time,
            personality_used=internal_response.personality_used,
            security_info={
                "is_safe": internal_response.validation_result.is_safe,
                "risk_factors": internal_response.validation_result.risk_factors,
                "critical_violations": internal_response.validation_result.critical_violations
            } if internal_response.validation_result else None,
            metadata={
                "model_name": internal_response.model_name,
                "tokens_generated": internal_response.tokens_generated,
                "generation_time": internal_response.generation_time,
                "validation_time": internal_response.validation_time
            }
        )
```

---

## 🛡️ Security Development

### Security-First Development

#### Input Validation
```python
from functools import wraps
from typing import Callable, Any

def validate_input(
    max_length: int = 1000,
    allow_html: bool = False,
    require_spanish: bool = True
) -> Callable:
    """
    Decorator for input validation with security focus.
    
    Args:
        max_length: Maximum allowed input length
        allow_html: Whether to allow HTML content
        require_spanish: Whether to validate Spanish language
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract message from args/kwargs
            message = None
            if 'message' in kwargs:
                message = kwargs['message']
            elif 'buyer_message' in kwargs:
                message = kwargs['buyer_message']
            elif len(args) > 0 and isinstance(args[0], str):
                message = args[0]
            
            if message:
                # Length validation
                if len(message) > max_length:
                    raise ValidationError(f"Message exceeds maximum length of {max_length}")
                
                # HTML validation
                if not allow_html and '<' in message:
                    suspicious_tags = ['script', 'iframe', 'object', 'embed']
                    if any(tag in message.lower() for tag in suspicious_tags):
                        raise SecurityError("Potentially malicious HTML detected")
                
                # Spanish language validation (if required)
                if require_spanish:
                    if not _is_likely_spanish(message):
                        raise ValidationError("Message should be in Spanish")
                
                # XSS prevention
                if _contains_xss_patterns(message):
                    raise SecurityError("Cross-site scripting patterns detected")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def _is_likely_spanish(text: str) -> bool:
    """Check if text is likely in Spanish."""
    spanish_indicators = [
        'ñ', 'é', 'á', 'í', 'ó', 'ú', 'ü',
        '¿', '¡',
        'que', 'con', 'por', 'para', 'está', 'son', 'es'
    ]
    
    # If text is very short, be lenient
    if len(text) < 10:
        return True
    
    # Count Spanish indicators
    indicators_found = sum(1 for indicator in spanish_indicators if indicator in text.lower())
    return indicators_found >= 2

def _contains_xss_patterns(text: str) -> bool:
    """Check for common XSS patterns."""
    xss_patterns = [
        r'javascript:',
        r'data:text/html',
        r'<script[\s\S]*?>',
        r'onerror\s*=',
        r'onload\s*=',
        r'onclick\s*='
    ]
    
    import re
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in xss_patterns)

# Usage example
@validate_input(max_length=500, require_spanish=True)
def process_buyer_message(buyer_message: str, buyer_name: str) -> str:
    """Process buyer message with security validation."""
    # Function implementation
    pass
```

#### Security Monitoring
```python
class SecurityMonitor:
    """Real-time security monitoring and alerting system."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.alert_thresholds = config.alert_thresholds
        self.incident_tracker = IncidentTracker()
        
    def monitor_fraud_detection(self, validation_result: ValidationResult):
        """Monitor fraud detection patterns and alert on anomalies."""
        # Track fraud detection rates
        self.incident_tracker.record_validation(validation_result)
        
        # Check for unusual patterns
        recent_stats = self.incident_tracker.get_recent_stats(hours=1)
        
        # Alert on high fraud rate
        if recent_stats['fraud_rate'] > self.alert_thresholds['max_fraud_rate']:
            self._send_security_alert(
                level="HIGH",
                message=f"Fraud detection rate {recent_stats['fraud_rate']:.1%} exceeds threshold",
                details=recent_stats
            )
        
        # Alert on new fraud patterns
        if validation_result.critical_violations:
            new_patterns = self._detect_new_patterns(validation_result.critical_violations)
            if new_patterns:
                self._send_security_alert(
                    level="CRITICAL",
                    message=f"New fraud patterns detected: {new_patterns}",
                    details=validation_result.__dict__
                )
    
    def monitor_api_usage(self, endpoint: str, api_key: str, response_time: float):
        """Monitor API usage for abuse patterns."""
        usage_stats = self.incident_tracker.get_api_usage(api_key, minutes=5)
        
        # Check rate limiting
        if usage_stats['request_count'] > self.alert_thresholds['max_requests_per_5min']:
            self._send_security_alert(
                level="MEDIUM",
                message=f"API rate limit exceeded for key {api_key[:8]}...",
                details={
                    "api_key": api_key[:8] + "...",
                    "requests_in_5min": usage_stats['request_count'],
                    "endpoint": endpoint
                }
            )
        
        # Check for unusual response times (potential attack)
        if response_time > self.alert_thresholds['max_response_time']:
            self._send_security_alert(
                level="LOW",
                message=f"Unusual response time: {response_time:.2f}s",
                details={
                    "endpoint": endpoint,
                    "response_time": response_time,
                    "api_key": api_key[:8] + "..."
                }
            )
    
    def _send_security_alert(self, level: str, message: str, details: Dict):
        """Send security alert through configured channels."""
        alert = SecurityAlert(
            level=level,
            message=message,
            details=details,
            timestamp=datetime.utcnow()
        )
        
        # Log alert
        logger.critical(
            "Security alert",
            level=level,
            message=message,
            details=details
        )
        
        # Send through alert channels
        if level in ["HIGH", "CRITICAL"]:
            self._send_email_alert(alert)
            self._send_slack_alert(alert)
        
        # Store for analysis
        self.incident_tracker.store_alert(alert)
```

---

## 📊 Performance Guidelines

### Performance Optimization

#### Async Optimization
```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class OptimizedAIEngine:
    """Performance-optimized AI Engine with concurrent processing."""
    
    def __init__(self, config: AIEngineConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        self.thread_pool = ThreadPoolExecutor(max_workers=config.thread_pool_size)
        
    async def process_multiple_requests(
        self, 
        requests: List[ConversationRequest]
    ) -> List[ConversationResponse]:
        """
        Process multiple requests concurrently with optimal resource usage.
        
        This method implements:
        - Semaphore-based concurrency control
        - Intelligent batching based on system load
        - Circuit breaker pattern for failure handling
        - Memory pressure monitoring
        """
        # Monitor memory before processing
        memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        if memory_usage > self.config.memory_threshold_mb:
            # Reduce concurrency if memory pressure is high
            effective_semaphore = asyncio.Semaphore(max(1, self.config.max_concurrent_requests // 2))
        else:
            effective_semaphore = self.semaphore
        
        # Create tasks with semaphore control
        async def process_with_semaphore(request: ConversationRequest):
            async with effective_semaphore:
                try:
                    return await self.generate_response_async(request)
                except Exception as e:
                    # Return error response instead of failing
                    return ConversationResponse(
                        response_text="Error procesando solicitud",
                        confidence=0.0,
                        risk_score=0,
                        source="error",
                        error=str(e)
                    )
        
        # Process all requests concurrently
        tasks = [process_with_semaphore(req) for req in requests]
        
        # Use gather with return_exceptions for robust error handling
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error responses
        final_responses = []
        for response in responses:
            if isinstance(response, Exception):
                final_responses.append(ConversationResponse(
                    response_text="Error interno del sistema",
                    confidence=0.0,
                    risk_score=0,
                    source="error",
                    error=str(response)
                ))
            else:
                final_responses.append(response)
        
        return final_responses
    
    async def generate_response_with_caching(
        self, 
        request: ConversationRequest
    ) -> ConversationResponse:
        """Generate response with intelligent caching strategy."""
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Check cache first
        if cached_response := await self.cache.get(cache_key):
            # Add cache hit metadata
            cached_response.metadata = cached_response.metadata or {}
            cached_response.metadata['cache_hit'] = True
            cached_response.response_time = 0.1  # Very fast cache response
            return cached_response
        
        # Generate new response
        response = await self.generate_response_async(request)
        
        # Cache if response is good quality and safe
        if (response.confidence > 0.7 and 
            response.risk_score < 25 and 
            response.source == "ai_engine"):
            
            # Set TTL based on response quality
            ttl = 3600 if response.confidence > 0.9 else 1800
            await self.cache.set(cache_key, response, ttl=ttl)
        
        return response
    
    def _generate_cache_key(self, request: ConversationRequest) -> str:
        """Generate intelligent cache key for request."""
        import hashlib
        
        # Include key factors in cache key
        cache_factors = [
            request.buyer_message.lower().strip(),
            request.product_name.lower(),
            str(request.price),
            request.personality,
            request.condition
        ]
        
        # Normalize message for better cache hits
        normalized_message = self._normalize_message(request.buyer_message)
        cache_factors[0] = normalized_message
        
        # Create hash
        cache_string = "|".join(cache_factors)
        return hashlib.sha256(cache_string.encode()).hexdigest()[:16]
    
    def _normalize_message(self, message: str) -> str:
        """Normalize message for better cache key generation."""
        # Remove punctuation and extra spaces
        import re
        normalized = re.sub(r'[^\w\s]', '', message.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Handle common variations
        replacements = {
            'hola': 'hola',
            'buenas': 'hola',
            'buenos dias': 'hola',
            'buenas tardes': 'hola',
            'está disponible': 'disponible',
            'sigue disponible': 'disponible',
            'todavia disponible': 'disponible'
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        return normalized
```

#### Memory Optimization
```python
import gc
import psutil
from typing import Optional

class MemoryOptimizer:
    """Advanced memory optimization for AI Engine operations."""
    
    def __init__(self, threshold_mb: int = 12000):
        self.threshold_mb = threshold_mb
        self.last_gc_time = time.time()
        self.gc_frequency = 60  # seconds
        
    def monitor_and_optimize(self) -> Dict[str, Any]:
        """Monitor memory usage and apply optimizations as needed."""
        memory_info = psutil.Process().memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        optimization_actions = []
        
        # Check if we need garbage collection
        if (time.time() - self.last_gc_time > self.gc_frequency or 
            memory_mb > self.threshold_mb * 0.8):
            
            collected = gc.collect()
            optimization_actions.append(f"garbage_collection:{collected}")
            self.last_gc_time = time.time()
        
        # Check for memory pressure
        if memory_mb > self.threshold_mb:
            # Clear caches
            if hasattr(self, 'cache'):
                self.cache.clear()
                optimization_actions.append("cache_cleared")
            
            # Force garbage collection
            for generation in range(3):
                gc.collect(generation)
            optimization_actions.append("forced_gc")
        
        # Memory statistics
        memory_stats = {
            "memory_mb": memory_mb,
            "threshold_mb": self.threshold_mb,
            "usage_percent": (memory_mb / self.threshold_mb) * 100,
            "optimizations_applied": optimization_actions
        }
        
        return memory_stats
    
    @contextmanager
    def memory_managed_operation(self):
        """Context manager for memory-intensive operations."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            yield
        finally:
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_increase = final_memory - initial_memory
            
            # If significant memory increase, trigger cleanup
            if memory_increase > 100:  # 100MB increase
                gc.collect()
                logger.info(
                    "Memory cleanup after operation",
                    initial_memory_mb=initial_memory,
                    final_memory_mb=final_memory,
                    memory_increase_mb=memory_increase
                )
```

---

## 🚀 Release Process

### Version Management

#### Semantic Versioning
```
Wall-E follows semantic versioning (semver):

MAJOR.MINOR.PATCH

Examples:
- 1.0.0 - Initial release
- 1.1.0 - New feature (AI Engine integration)
- 1.1.1 - Bug fix
- 2.0.0 - Breaking change (API restructure)

Pre-release versions:
- 2.1.0-alpha.1 - Alpha release
- 2.1.0-beta.1 - Beta release
- 2.1.0-rc.1 - Release candidate
```

#### Release Workflow
```bash
# 1. Prepare release branch
git checkout -b release/v2.1.0
git push -u origin release/v2.1.0

# 2. Update version numbers
echo "__version__ = '2.1.0'" > src/_version.py
git add src/_version.py
git commit -m "chore: bump version to 2.1.0"

# 3. Update CHANGELOG.md
# Add release notes and changes

# 4. Run full test suite
pytest tests/ --cov=src --cov-report=html
python scripts/run_performance_benchmark.py --full

# 5. Create release PR
gh pr create --title "Release v2.1.0" --body "$(cat RELEASE_NOTES.md)"

# 6. After PR approval and merge, create tag
git checkout main
git pull origin main
git tag -a v2.1.0 -m "Release version 2.1.0"
git push origin v2.1.0

# 7. Create GitHub release
gh release create v2.1.0 --title "Wall-E v2.1.0" --notes-file RELEASE_NOTES.md
```

### Release Checklist

**Pre-Release Checklist:**
- [ ] All tests pass (unit, integration, e2e)
- [ ] Performance benchmarks meet targets
- [ ] Security scan completed (no critical issues)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Database migrations tested
- [ ] Docker images build successfully
- [ ] AI Engine compatibility verified

**Release Checklist:**
- [ ] Release branch created
- [ ] Code review completed
- [ ] Release notes written
- [ ] Staging deployment successful
- [ ] User acceptance testing completed
- [ ] Production deployment plan ready
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured

**Post-Release Checklist:**
- [ ] Production deployment successful
- [ ] Health checks passing
- [ ] Performance metrics normal
- [ ] Error rates within expected range
- [ ] User feedback collected
- [ ] Post-mortem scheduled (if issues)
- [ ] Next release planning initiated

### Deployment Automation

**Create release script (`scripts/release.py`):**
```python
#!/usr/bin/env python3
"""Automated release script for Wall-E"""

import subprocess
import sys
import json
from typing import List

class ReleaseManager:
    def __init__(self, version: str, release_type: str = "minor"):
        self.version = version
        self.release_type = release_type
        
    def validate_version(self) -> bool:
        """Validate version format"""
        import re
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, self.version))
    
    def run_tests(self) -> bool:
        """Run complete test suite"""
        try:
            # Unit tests
            subprocess.run(["pytest", "tests/", "--cov=src"], check=True)
            
            # Security tests
            subprocess.run(["bandit", "-r", "src/"], check=True)
            
            # Performance tests
            subprocess.run(["python", "scripts/run_performance_benchmark.py", "--quick"], check=True)
            
            return True
        except subprocess.CalledProcessError:
            return False
    
    def update_version_files(self):
        """Update version in all relevant files"""
        files_to_update = [
            ("src/_version.py", f'__version__ = "{self.version}"'),
            ("pyproject.toml", f'version = "{self.version}"'),
            ("docker/Dockerfile.prod", f'LABEL version="{self.version}"')
        ]
        
        for file_path, version_line in files_to_update:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Update version line (simplified)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'version' in line.lower():
                        lines[i] = version_line
                        break
                
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                    
            except FileNotFoundError:
                print(f"Warning: {file_path} not found")
    
    def create_release_notes(self) -> str:
        """Generate release notes from git history"""
        try:
            # Get commits since last tag
            result = subprocess.run(
                ["git", "log", "--oneline", "--since", "$(git describe --tags --abbrev=0)..HEAD"],
                capture_output=True,
                text=True
            )
            
            commits = result.stdout.strip().split('\n')
            
            # Categorize commits
            features = []
            fixes = []
            other = []
            
            for commit in commits:
                if commit.startswith('feat'):
                    features.append(commit)
                elif commit.startswith('fix'):
                    fixes.append(commit)
                else:
                    other.append(commit)
            
            # Generate release notes
            notes = f"# Release v{self.version}\n\n"
            
            if features:
                notes += "## 🚀 New Features\n"
                for feature in features:
                    notes += f"- {feature}\n"
                notes += "\n"
            
            if fixes:
                notes += "## 🐛 Bug Fixes\n"
                for fix in fixes:
                    notes += f"- {fix}\n"
                notes += "\n"
            
            if other:
                notes += "## 🔧 Other Changes\n"
                for change in other:
                    notes += f"- {change}\n"
                notes += "\n"
            
            return notes
            
        except subprocess.CalledProcessError:
            return f"# Release v{self.version}\n\nManual release notes needed."
    
    def create_release(self):
        """Execute complete release process"""
        print(f"🚀 Starting release process for v{self.version}")
        
        # Validate version
        if not self.validate_version():
            print("❌ Invalid version format")
            sys.exit(1)
        
        # Run tests
        print("🧪 Running test suite...")
        if not self.run_tests():
            print("❌ Tests failed")
            sys.exit(1)
        print("✅ Tests passed")
        
        # Update version files
        print("📝 Updating version files...")
        self.update_version_files()
        
        # Generate release notes
        print("📋 Generating release notes...")
        release_notes = self.create_release_notes()
        with open(f"RELEASE_NOTES_v{self.version}.md", 'w') as f:
            f.write(release_notes)
        
        # Create release branch
        print("🌿 Creating release branch...")
        subprocess.run(["git", "checkout", "-b", f"release/v{self.version}"], check=True)
        
        # Commit changes
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"chore: prepare release v{self.version}"], check=True)
        
        # Push branch
        subprocess.run(["git", "push", "-u", "origin", f"release/v{self.version}"], check=True)
        
        print(f"✅ Release v{self.version} prepared successfully!")
        print(f"📋 Release notes written to RELEASE_NOTES_v{self.version}.md")
        print("🔄 Create a PR to merge the release branch")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/release.py <version>")
        print("Example: python scripts/release.py 2.1.0")
        sys.exit(1)
    
    version = sys.argv[1]
    release_manager = ReleaseManager(version)
    release_manager.create_release()
```

**Usage:**
```bash
# Create new release
python scripts/release.py 2.1.0

# Create hotfix release
python scripts/release.py 2.0.1
```

---

**👩‍💻 This comprehensive development guide provides everything needed to contribute effectively to the Wall-E project. The combination of clear standards, comprehensive testing, and specialized subagent integration ensures high-quality, maintainable code that advances the state of marketplace automation.**

*For additional development resources, see the [API Reference](API_REFERENCE.md), [AI Engine Guide](AI_ENGINE_GUIDE.md), and [Troubleshooting Guide](TROUBLESHOOTING.md).*