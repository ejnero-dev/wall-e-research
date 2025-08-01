# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Wallapop automation bot project written in Python. It's designed to automate sales conversations, detect fraud attempts, provide competitive price analysis, and manage product listings on Wallapop (Spanish second-hand marketplace).

## Development Commands

### Initial Setup
```bash
# Initialize project (creates directories, configs, installs dependencies)
python scripts/init_project.py

# Install Python dependencies
pip install -r requirements.txt

# Install spaCy Spanish model
python -m spacy download es_core_news_sm

# Install Playwright browsers
playwright install chromium
```

### Running the Application
```bash
# Start the main bot
python src/bot/wallapop_bot.py

# Run price analysis example
python scripts/price_analysis_example.py
```

### Testing and Development
```bash
# Run tests (when implemented)
pytest tests/

# Check logs
tail -f logs/wallapop_bot.log

# Format code
black src/
flake8 src/
```

## Architecture Overview

### Core Components

**Main Bot (`src/bot/wallapop_bot.py`)**
- Central orchestrator that coordinates all bot functionality
- Manages conversation monitoring, response processing, and stats tracking
- Uses async/await patterns for concurrent operations
- Implements human-like behavior with configurable delays and active hours
- Currently has placeholders for integrations with other modules

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
- Placeholder imports indicate incomplete integration between modules
- Spanish language support is built-in (spaCy model, response templates)
- Designed to be self-hosted with no external paid dependencies
- Follows defensive security practices for marketplace automation

## Project Status

This appears to be a well-structured but partially implemented project. The core architecture is in place with sophisticated fraud detection and price analysis capabilities, but some integrations between modules are still pending completion.