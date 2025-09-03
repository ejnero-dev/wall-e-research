# 🏗️ Wall-E System Architecture Overview

Comprehensive technical architecture documentation for the Wall-E advanced Wallapop automation system.

---

## 📋 Table of Contents

- [🌟 System Overview](#-system-overview)
- [🏗️ High-Level Architecture](#️-high-level-architecture)
- [🤖 AI Engine Architecture](#-ai-engine-architecture)
- [🔄 Data Flow](#-data-flow)
- [💾 Database Architecture](#-database-architecture)
- [🔌 Integration Patterns](#-integration-patterns)
- [⚡ Performance Architecture](#-performance-architecture)

---

## 🌟 System Overview

Wall-E is a **microservices-based architecture** designed for **high-performance marketplace automation** with enterprise-grade reliability, security, and scalability.

### Core Design Principles

**🎯 Performance First:**
- Sub-3-second response times
- 10+ concurrent conversation support
- Linear scalability architecture
- Memory-efficient processing

**🛡️ Security by Design:**
- Multi-layer fraud detection
- Zero-trust security model
- Privacy-focused data handling
- Comprehensive audit trails

**🔄 Reliability & Availability:**
- 99.9% uptime target
- Graceful degradation patterns
- Circuit breaker implementations
- Automatic recovery mechanisms

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        WALL-E SYSTEM                           │
├─────────────────────────────────────────────────────────────────┤
│  🌐 PRESENTATION LAYER                                         │
│  ├── NextJS Dashboard (Real-time monitoring)                   │
│  ├── FastAPI REST API (System integration)                    │
│  └── WebSocket API (Real-time updates)                        │
├─────────────────────────────────────────────────────────────────┤
│  🧠 AI ENGINE LAYER                                           │
│  ├── LLM Manager (Ollama + Llama 3.2)                        │
│  ├── Response Generator (Natural conversations)               │
│  ├── Validator (Multi-layer fraud detection)                 │
│  ├── Fallback Handler (Template system)                      │
│  └── Performance Monitor (Real-time metrics)                 │
├─────────────────────────────────────────────────────────────────┤
│  💼 BUSINESS LOGIC LAYER                                      │
│  ├── Conversation Engine (State management)                   │
│  ├── Price Analyzer (Market intelligence)                     │
│  ├── Bot Orchestrator (Main coordination)                     │
│  └── Security Engine (Fraud protection)                       │
├─────────────────────────────────────────────────────────────────┤
│  🕷️ DATA ACQUISITION LAYER                                   │
│  ├── Wallapop Scraper (Anti-detection)                       │
│  ├── Price Scrapers (Multi-platform)                         │
│  ├── Session Manager (Cookie persistence)                     │
│  └── Circuit Breaker (Error handling)                         │
├─────────────────────────────────────────────────────────────────┤
│  💾 DATA LAYER                                               │
│  ├── PostgreSQL (Primary database)                            │
│  ├── Redis (Caching + sessions)                              │
│  ├── File System (Logs + screenshots)                         │
│  └── Backup Systems (Data protection)                         │
└─────────────────────────────────────────────────────────────────┘
```

## 🤖 AI Engine Architecture

### Core Components

```
AI Engine Detailed Architecture
┌─────────────────────────────────────────────────────────────────┐
│  🎯 AIEngine (Main Orchestrator)                              │
│  ├── Request Processing Pipeline                               │
│  ├── Concurrent Request Management                            │
│  ├── Performance Monitoring Integration                       │
│  └── Error Handling & Recovery                               │
├─────────────────────────────────────────────────────────────────┤
│  🧠 LLMManager (Ollama Integration)                           │
│  ├── Connection Pool Management                               │
│  ├── Model Loading & Optimization                            │
│  ├── Hardware-aware Configuration                            │
│  └── Response Streaming                                       │
├─────────────────────────────────────────────────────────────────┤
│  📝 ResponseGenerator (Conversation Creation)                  │
│  ├── Spanish Prompt Templates                                 │
│  ├── Personality System (3 personas)                          │
│  ├── Context-aware Generation                                │
│  └── Response Quality Scoring                                │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Validator (Security & Quality)                           │
│  ├── Fraud Pattern Detection                                  │
│  ├── Content Appropriateness Checking                        │
│  ├── Risk Score Calculation                                  │
│  └── Response Quality Validation                             │
├─────────────────────────────────────────────────────────────────┤
│  🔄 FallbackHandler (Reliability)                            │
│  ├── Template Response System                                │
│  ├── Graceful Degradation Logic                              │
│  ├── AI Availability Monitoring                              │
│  └── Hybrid Mode Management                                  │
└─────────────────────────────────────────────────────────────────┘
```

### AI Processing Pipeline

```
Request Flow:
ConversationRequest → AIEngine → LLMManager → ResponseGenerator
                                      ↓
PerformanceMonitor ← FallbackHandler ← Validator ← GeneratedResponse
                                      ↓
                              Final Validated Response
```

## 🔄 Data Flow

### Primary Data Flow

```
1. 🕷️ Scraper detects new message
   ↓
2. 💼 Bot Orchestrator processes message
   ↓
3. 🧠 AI Engine generates response
   ↓
4. ✅ Security validation occurs
   ↓
5. 📤 Response sent to Wallapop
   ↓
6. 💾 All data persisted to database
   ↓
7. 📊 Real-time dashboard updates
```

### Error Handling Flow

```
Error Detected → Circuit Breaker → Fallback Strategy → Recovery Attempt
                       ↓                    ↓
               Log & Monitor        Alternative Response
                       ↓                    ↓
              Dashboard Alert        Continue Operation
```

## 💾 Database Architecture

### PostgreSQL Schema

```sql
-- Core conversation tracking
conversations (
    id, buyer_name, product_name, state, 
    risk_score, priority, created_at
)

-- AI Engine performance
ai_responses (
    id, conversation_id, response_text, confidence,
    generation_time, model_used, personality
)

-- Security audit trail
security_events (
    id, event_type, risk_score, patterns_detected,
    action_taken, timestamp
)

-- Price analysis data
price_analysis (
    id, product_name, platform, price, confidence,
    market_position, analysis_date
)
```

### Redis Cache Strategy

```
Session Data:
- wallapop_session:{user_id} → Cookie data (TTL: 24h)
- conversation_state:{conv_id} → Current state (TTL: 7d)

Performance Cache:
- ai_response_cache:{hash} → Generated responses (TTL: 1h)
- price_cache:{product} → Market data (TTL: 6h)

Metrics Cache:
- performance_metrics → Real-time stats (TTL: 5m)
- system_health → Health checks (TTL: 1m)
```

## 🔌 Integration Patterns

### External Service Integration

**🕷️ Web Scraping Integration:**
- Playwright browser automation
- Anti-detection mechanisms
- Session persistence
- Error recovery patterns

**🤖 AI Model Integration:**
- Ollama REST API
- Local model inference
- Hardware optimization
- Performance monitoring

**📊 Dashboard Integration:**
- WebSocket real-time updates
- REST API data endpoints
- Authentication middleware
- Performance metrics streaming

### Internal Service Communication

```python
# Async service communication pattern
async def process_conversation_request(request: ConversationRequest) -> Response:
    # 1. Pre-processing
    validated_request = await validate_request(request)
    
    # 2. AI Generation
    ai_response = await ai_engine.generate_response(validated_request)
    
    # 3. Security validation
    security_result = await security_validator.validate(ai_response)
    
    # 4. Post-processing
    final_response = await post_process(ai_response, security_result)
    
    return final_response
```

## ⚡ Performance Architecture

### Concurrency Model

**🔄 Async/Await Architecture:**
- Non-blocking I/O operations
- Connection pooling
- Resource management
- Memory optimization

**🎯 Performance Targets:**
```python
PERFORMANCE_TARGETS = {
    "response_time": "< 3.0 seconds",
    "concurrent_conversations": "> 10",
    "memory_usage": "< 80% available RAM",
    "throughput": "> 20 requests/minute",
    "availability": "> 99.9%"
}
```

### Optimization Strategies

**💾 Memory Management:**
- Connection pooling for database and AI
- Cache layer optimization
- Garbage collection tuning
- Resource monitoring

**⚡ Processing Optimization:**
- Async processing pipelines
- Batch operation support
- Lazy loading patterns
- Intelligent caching

### Monitoring & Observability

**📊 Key Metrics:**
- Response time percentiles
- Error rates by component
- Resource utilization
- Business metrics (conversions, fraud detection)

**🔍 Logging Strategy:**
```python
LOGGING_LEVELS = {
    "ai_engine": "INFO",  # Performance and generation metrics
    "security": "WARNING",  # Fraud detection and security events
    "scraper": "DEBUG",  # Detailed scraping operations
    "database": "ERROR"  # Critical database issues only
}
```

---

## 🚀 Deployment Architecture

### Production Environment

```
Load Balancer (Nginx)
├── App Server 1 (Main Bot + AI Engine)
├── App Server 2 (Dashboard + API)
├── Database Server (PostgreSQL Primary)
├── Cache Server (Redis Cluster)
└── Monitoring Server (Prometheus + Grafana)
```

### Scalability Considerations

**📈 Horizontal Scaling:**
- Stateless application design
- Database connection pooling
- Redis clustering support
- Load balancer integration

**📊 Vertical Scaling:**
- Hardware-aware AI configuration
- Dynamic memory allocation
- CPU core utilization
- Storage optimization

---

## 🛠️ Development Architecture

### Code Organization

```
src/
├── ai_engine/          # AI Engine modules (9 files)
├── bot/               # Main bot orchestration
├── conversation_engine/ # Conversation management
├── scraper/           # Web scraping system
├── price_analyzer/    # Market analysis
├── database/          # Data layer
└── api/              # REST API and dashboard
```

### Testing Architecture

```
tests/
├── unit/             # Component unit tests
├── integration/      # System integration tests
├── performance/      # Load and performance tests
└── security/        # Security validation tests
```

**🧪 Test Coverage Targets:**
- AI Engine: 95%+ coverage
- Security components: 100% coverage
- Critical business logic: 90%+ coverage
- Integration points: 85%+ coverage

---

**🏗️ Wall-E Architecture: Enterprise-grade system design for production-ready marketplace automation.**