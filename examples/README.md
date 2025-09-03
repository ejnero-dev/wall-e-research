# Wall-E Examples

This directory contains demonstration scripts that showcase the various capabilities of the Wall-E system.

## Available Examples

### `demo_complete_system.py`
Complete system demonstration showing all Wall-E capabilities working together:
- AI Engine with IA generativa integration
- Anti-fraud detection
- Competitive price analysis
- Real-time dashboard
- Advanced scraper functionality

**Usage:**
```bash
cd examples
python demo_complete_system.py
```

### `demo_price_analysis.py`
Focused demonstration of the competitive price analysis system:
- Market data collection and analysis
- Price strategy recommendations
- Statistical analysis with confidence scoring
- Market trend detection

**Usage:**
```bash
cd examples
python demo_price_analysis.py
```

## Requirements

All examples require the full Wall-E system to be properly installed and configured. Make sure you have:

1. Installed all dependencies: `pip install -r requirements.txt`
2. Configured your environment variables in `.env`
3. Initialized the database: `python scripts/init_database.py`
4. Set up the AI Engine: `python scripts/setup_ai_engine.py`

## Notes

- Examples are designed to work with simulated data for demonstration purposes
- They showcase the system capabilities without requiring actual Wallapop integration
- All import paths are configured to work from the examples directory