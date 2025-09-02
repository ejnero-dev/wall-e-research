# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Wallapop automation system with an advanced AI engine and professional web dashboard. It automates sales conversations, detects fraud attempts, provides competitive price analysis, and manages product listings on Wallapop (Spanish second-hand marketplace). The project now includes a complete React-based dashboard for real-time monitoring and control.

## Development Commands

### Initial Setup
```bash
# Initialize project (creates directories, configs, installs dependencies)
python scripts/init_project.py

# Install Python dependencies with uv (recommended)
uv sync

# Or with pip if uv is not available
pip install -r requirements.txt

# Install spaCy Spanish model
python -m spacy download es_core_news_sm

# Install Playwright browsers
playwright install chromium

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### Running the Application
```bash
# Start complete dashboard system (backend + frontend)
./start_dashboard.sh

# Or start services individually:
# Start backend API server
uv run python -m uvicorn src.api.dashboard_server:app --reload --port 8000

# Start frontend development server (in another terminal)
cd frontend && npm run dev

# Start the main bot (legacy)
python src/bot/wallapop_bot.py

# Run price analysis example
python scripts/price_analysis_example.py
```

### Testing and Development
```bash
# Run tests
pytest tests/

# Run dashboard tests specifically
pytest tests/unit/test_dashboard_api.py -v

# Build frontend for production
cd frontend && npm run build

# Check logs
tail -f logs/wallapop_bot.log

# Format code
black src/
flake8 src/

# Lint frontend
cd frontend && npm run lint
```

## Architecture Overview

### Core Components

**Web Dashboard (`frontend/` + `src/api/`)**
- **Frontend**: React 18 + TypeScript + Vite development environment
- **Backend**: FastAPI with WebSocket support for real-time updates
- **UI Components**: Professional shadcn-ui components with Tailwind CSS
- **Real-time Data**: WebSocket integration for live metrics and updates
- **Responsive Design**: Mobile-first approach with modern UX patterns
- **API Integration**: Complete REST API for product management and system control

**Dashboard Components:**
- `QuickStats`: Real-time system metrics and performance indicators
- `ActiveListings`: Product management with CRUD operations
- `AutomatedResponses`: AI response configuration and template management
- `AutoDetectionPanel`: Automated product discovery controls

**Main Bot (`src/bot/wallapop_bot.py`)**
- Central orchestrator that coordinates all bot functionality
- Manages conversation monitoring, response processing, and stats tracking
- Uses async/await patterns for concurrent operations
- Implements human-like behavior with configurable delays and active hours
- Integrates with dashboard API for real-time monitoring

**API Server (`src/api/dashboard_server.py`)**
- FastAPI application with auto-reload and development features
- WebSocket endpoint for real-time dashboard updates
- CORS configured for frontend development (port 8080)
- Health checks and system status endpoints
- Integration with existing bot components

**Conversation Engine (`src/conversation_engine/engine.py`)**
- Intelligent conversation management system with NLP capabilities
- Defines conversation states: INICIAL → EXPLORANDO → NEGOCIANDO → COMPROMETIDO → COORDINANDO → FINALIZADO
- Intention detection for messages (saludo, precio, negociacion, etc.)
- Advanced fraud detection with risk scoring (0-100)
- Buyer priority classification (ALTA, MEDIA, BAJA)
- State-based conversation flow management

**Price Analyzer (`src/price_analyzer/analyzer.py`)**
- Multi-platform price analysis (Wallapop, Amazon, eBay, etc.)
- Statistical analysis with confidence scoring
- Price suggestions based on market conditions and selling strategy
- Market trend analysis and competitive positioning
- Condition-based price adjustments (nuevo, como nuevo, buen estado, usado)

### Data Models

The system uses dataclasses for structured data:
- `Buyer`: User profile with ratings, purchase history, location
- `Product`: Item details with pricing, condition, shipping options
- `PriceData`: Market price information from various platforms
- `PriceAnalysis`: Complete price analysis results with suggestions

### Configuration System

**Main Config (`config/config.yaml`)**
- Wallapop behavior settings (delays, active hours, conversation limits)
- Database connections (PostgreSQL, Redis)
- NLP configuration (spaCy models, confidence thresholds)
- Security settings (fraud detection patterns, auto-blocking)
- Logging, metrics, and backup configurations

**Environment Variables (`.env`)**
- Database URLs and credentials
- API keys and session cookies
- Security secrets and debug flags

## Key Features

**Fraud Prevention**
- Pattern matching for suspicious keywords ("western union", "paypal familia", etc.)
- User profile risk assessment (new accounts, no ratings, distant locations)
- URL analysis for phishing attempts
- Automatic blocking and reporting capabilities

**Web Dashboard Management**
- Real-time monitoring of system performance and metrics
- Product management with visual interfaces
- Automated response configuration and control
- Auto-detection system with manual override capabilities
- WebSocket-based live updates every 5 seconds

**Intelligent Conversation Management**
- Context-aware response generation
- Conversation state tracking and appropriate transitions
- Abandoned conversation recovery
- A/B testing for response optimization

**Competitive Price Analysis**
- Real-time market data collection
- Statistical analysis with confidence scoring
- Strategy-based pricing (quick sale vs maximum profit)
- Market trend detection and alerts

## Security Considerations

- All sensitive data should be stored in environment variables or encrypted
- The bot respects Wallapop's Terms of Service and rate limits
- Implements human-like behavior patterns to avoid detection
- Comprehensive logging for audit trails
- Backup systems for data preservation

## Development Notes

- The project uses async/await extensively for concurrent operations
- Modern React 18 + TypeScript frontend with professional UI components
- FastAPI backend with WebSocket support for real-time updates
- Spanish language support is built-in (spaCy model, response templates)
- Designed to be self-hosted with no external paid dependencies
- Follows defensive security practices for marketplace automation
- Complete dashboard system with GitHub Actions CI/CD pipeline
- Package management with `uv` for faster dependency resolution

## URLs and Access Points

### Development Environment
- **Dashboard Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/dashboard/health
- **WebSocket**: ws://localhost:8000/api/dashboard/ws/live

### GitHub Repository
- **Main Repository**: https://github.com/ejnero-dev/wall-e-research
- **Pull Requests**: Automated CI/CD pipeline with testing
- **Documentation**: Complete README and technical guides

## Project Status

### ✅ COMPLETED - Phase 2B: Web Dashboard
This is a **production-ready** system with comprehensive functionality:

**✅ Completed Components:**
- **Web Dashboard**: Complete React frontend with TypeScript
- **Backend API**: FastAPI server with 15+ endpoints
- **Real-time Updates**: WebSocket integration working
- **CI/CD Pipeline**: GitHub Actions with automated testing
- **Documentation**: Comprehensive guides and API documentation
- **Package Management**: Modern `uv` workflow implemented
- **Button Functionality**: All interactive elements working correctly

**Current Capabilities:**
- Real-time system monitoring and metrics
- Product management with CRUD operations
- Automated response configuration
- Auto-detection system control
- Professional UI with responsive design
- Type-safe development environment
- Automated testing and deployment pipeline

The system is ready for production use and further feature expansion.