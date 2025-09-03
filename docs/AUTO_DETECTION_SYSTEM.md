# Wall-E Auto-Detection System

## Overview

The Wall-E Auto-Detection System automatically discovers and monitors new products when users upload them to their Wallapop accounts. This eliminates the need for manual product addition and keeps the dashboard synchronized with the user's actual Wallapop listings.

## Key Features

### 🔍 Automatic Product Discovery
- **Periodic Scanning**: Scans user's "My Products" section every 10-15 minutes
- **Smart Detection**: Identifies new products not yet in the monitoring system
- **Change Tracking**: Detects status changes (sold, paused, price changes)
- **Anti-Detection**: Uses advanced evasion techniques to avoid Wallapop detection

### 🔄 Real-Time Synchronization
- **Auto-Add**: Automatically adds detected products to the dashboard
- **Status Updates**: Syncs product status changes in real-time
- **Data Enrichment**: Extracts comprehensive product information
- **WebSocket Updates**: Real-time dashboard updates

### 📊 Intelligent Monitoring
- **Session Management**: Maintains secure, encrypted authentication
- **Rate Limiting**: Respects Wallapop's rate limits (max 1 scan per 10 minutes)
- **Error Recovery**: Circuit breaker patterns and automatic retry logic
- **Health Monitoring**: Continuous system health checks

### 🔔 Multi-Channel Notifications
- **WebSocket**: Real-time dashboard notifications
- **Email**: High-priority alerts and daily summaries
- **Console**: Development and debugging notifications
- **File Logging**: Persistent notification history

## Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   AccountScanner    │────│  DetectionManager    │────│ NotificationManager │
│                     │    │                      │    │                     │
│ • Product Detection │    │ • Background Tasks   │    │ • Multi-Channel     │
│ • Change Analysis   │    │ • API Integration    │    │ • Priority Routing  │
│ • Anti-Detection    │    │ • Queue Management   │    │ • WebSocket/Email   │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
           │                           │                           │
           └───────────────────────────┼───────────────────────────┘
                                       │
                    ┌─────────────────────────────────┐
                    │        Dashboard API            │
                    │                                 │
                    │ • Product CRUD Operations       │
                    │ • Auto-Detection Endpoints      │
                    │ • Real-Time Updates             │
                    │ • Configuration Management      │
                    └─────────────────────────────────┘
```

## Components

### 1. AccountScanner (`src/scraper/account_scanner.py`)

**Core functionality for automatic product discovery:**

- **Navigation**: Navigates to user's "My Products" section
- **Extraction**: Scrapes product data (title, price, description, images)
- **Detection**: Identifies new products and status changes
- **Persistence**: Stores known products with change tracking
- **Anti-Detection**: Implements human-like behavior patterns

**Key Methods:**
```python
async def scan_user_products() -> ScanResults
async def start_scanning(scan_interval: int) -> bool
def set_new_product_callback(callback: callable)
```

### 2. DetectionManager (`src/auto_detection/detection_manager.py`)

**Orchestrates the entire auto-detection system:**

- **Scanner Management**: Controls AccountScanner lifecycle
- **Queue Processing**: Manages product update queue
- **API Integration**: Communicates with dashboard API
- **Background Tasks**: Handles periodic scanning and health checks
- **Configuration**: Manages system settings and callbacks

**Key Methods:**
```python
async def start() -> bool
async def manual_scan() -> Dict[str, Any]
def update_config(config_updates: Dict[str, Any])
```

### 3. NotificationManager (`src/auto_detection/notifications.py`)

**Handles multi-channel notifications:**

- **Channel Management**: WebSocket, Email, Slack, Console, File
- **Priority Routing**: Different channels based on priority
- **Template Formatting**: HTML/text email templates
- **Subscriber System**: Custom notification callbacks
- **Logging**: Persistent notification history

**Key Methods:**
```python
async def notify_new_product(product_data: Dict[str, Any])
async def send_notification(type, title, message, data, priority)
def subscribe(channel: NotificationChannel, callback: Callable)
```

## API Endpoints

### Auto-Detection Management

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/dashboard/auto-detection/status` | GET | Get system status and statistics |
| `/api/dashboard/auto-detection/start` | POST | Start auto-detection system |
| `/api/dashboard/auto-detection/stop` | POST | Stop auto-detection system |
| `/api/dashboard/auto-detection/scan` | POST | Execute manual scan |
| `/api/dashboard/auto-detection/config` | GET/PUT | Manage configuration |
| `/api/dashboard/auto-detection/statistics` | GET | Detailed statistics |
| `/api/dashboard/auto-detection/detected-products` | GET | List detected products |

### Enhanced Product Endpoints

The existing product endpoints now support auto-detected products:

| Endpoint | Method | Enhancement |
|----------|---------|-------------|
| `/api/dashboard/products` | POST | Accepts auto-detected product data |
| `/api/dashboard/products/{id}` | PUT | Supports status change updates |
| `/api/dashboard/ws/live` | WebSocket | Real-time product notifications |

## Usage

### 1. Service Mode (Recommended)

```bash
# Start as background service
python scripts/start_auto_detection.py

# With custom configuration
python scripts/start_auto_detection.py --config config/detection.json

# Dry run mode (no dashboard updates)
python scripts/start_auto_detection.py --dry-run

# Custom scan interval
python scripts/start_auto_detection.py --scan-interval 15
```

### 2. API Mode

```python
# Via Dashboard API
curl -X POST http://localhost:8000/api/dashboard/auto-detection/start

# Check status
curl http://localhost:8000/api/dashboard/auto-detection/status

# Manual scan
curl -X POST http://localhost:8000/api/dashboard/auto-detection/scan
```

### 3. Programmatic Usage

```python
from src.auto_detection import DetectionManager

# Initialize and start
manager = DetectionManager()
await manager.start()

# Manual scan
results = await manager.manual_scan()
print(f"Found {results['new_products']} new products")

# Configure notifications
manager.update_config({
    "scan_interval_minutes": 15,
    "auto_respond_new_products": True,
    "enable_notifications": True
})
```

## Configuration

### Detection Settings

```json
{
  "scan_interval_minutes": 10,
  "auto_add_products": true,
  "auto_respond_new_products": true,
  "ai_personality": "professional",
  "response_delay_min": 15,
  "response_delay_max": 60,
  "max_products_per_scan": 50,
  "enable_notifications": true
}
```

### Notification Configuration

```json
{
  "email": {
    "enabled": true,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "from_email": "wall-e@yourdomain.com",
    "to_emails": ["admin@yourdomain.com"]
  },
  "slack": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/services/...",
    "channel": "#wall-e-alerts",
    "username": "Wall-E Bot"
  },
  "websocket": {
    "enabled": true,
    "broadcast_to_dashboard": true
  }
}
```

## Security & Anti-Detection

### 🛡️ Anti-Detection Measures

- **Human-like Delays**: Randomized delays between actions (30-120 seconds)
- **Session Persistence**: Encrypted cookie storage and rotation
- **User Agent Rotation**: Realistic browser fingerprints
- **Rate Limiting**: Respects Wallapop's rate limits
- **Error Handling**: Graceful degradation and circuit breakers

### 🔐 Security Features

- **Encrypted Sessions**: All session data is encrypted
- **Secure Headers**: Proper HTTP headers and CSRF protection
- **Input Validation**: All scraped data is validated and sanitized
- **Error Logging**: Comprehensive audit trails
- **Resource Limits**: Memory and CPU usage monitoring

## Monitoring & Diagnostics

### System Status

```python
# Get comprehensive status
status = detection_manager.get_status()

# Key metrics:
# - is_running: System operational status
# - products_detected: Total products found
# - products_auto_added: Successfully added to dashboard
# - success_rate: Detection accuracy percentage
# - last_scan_time: Most recent scan timestamp
```

### Health Checks

The system includes multiple health check layers:

- **Scanner Health**: Browser session and authentication status
- **API Health**: Dashboard API connectivity
- **Queue Health**: Background task processing status
- **Notification Health**: Delivery channel status

### Logging

Structured logging with different levels:

```bash
# Main application logs
tail -f logs/auto_detection.log

# Scraper-specific logs
tail -f logs/wallapop_scraper.log

# Notification logs
tail -f logs/notifications.log
```

## Testing

### Unit Tests

```bash
# Run comprehensive test suite
python scripts/test_auto_detection.py

# Test specific components
python -m pytest tests/auto_detection/
```

### Manual Testing

```bash
# Test scanner without dashboard integration
python scripts/test_auto_detection.py --component scanner

# Test notification system
python scripts/test_auto_detection.py --component notifications

# Test API integration
python scripts/test_auto_detection.py --component api
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failures
```bash
# Check session status
curl http://localhost:8000/api/dashboard/auto-detection/status

# Look for authentication errors in logs
grep "auth" logs/auto_detection.log
```

#### 2. No Products Detected
```bash
# Verify Wallapop access
python scripts/test_auto_detection.py --component scanner

# Check scan logs for navigation issues
grep "navigate" logs/wallapop_scraper.log
```

#### 3. Dashboard Integration Issues
```bash
# Test API connectivity
curl http://localhost:8000/api/dashboard/health

# Check queue processing
grep "queue" logs/auto_detection.log
```

#### 4. High Resource Usage
```bash
# Monitor system resources
python scripts/monitor_auto_detection.py

# Adjust scan intervals
curl -X PUT http://localhost:8000/api/dashboard/auto-detection/config \
  -d '{"scan_interval_minutes": 20}'
```

### Debug Mode

```bash
# Enable verbose logging
python scripts/start_auto_detection.py --verbose

# Enable debug mode in configuration
{
  "debug_mode": true,
  "screenshot_on_error": true,
  "detailed_logging": true
}
```

## Performance Optimization

### Recommended Settings

**Production Environment:**
- Scan interval: 10-15 minutes
- Max concurrent: 1 scanner instance
- Rate limit: 6 requests per hour
- Session timeout: 24 hours

**Development Environment:**
- Scan interval: 5 minutes (for testing)
- Dry run mode: Enabled
- Debug logging: Enabled
- Screenshot capture: Enabled

### Resource Usage

- **Memory**: ~50-100MB per scanner instance
- **CPU**: Low impact (periodic spikes during scans)
- **Network**: Minimal (respects rate limits)
- **Storage**: ~1MB per 1000 products tracked

## Future Enhancements

### Planned Features

- **🤖 AI-Powered Detection**: Machine learning for better product categorization
- **🔍 Advanced Filtering**: Custom rules for product selection
- **📱 Mobile App**: Real-time notifications on mobile devices
- **📈 Analytics Dashboard**: Detailed insights and trends
- **🔧 Plugin System**: Extensible notification channels

### Integration Roadmap

- **Phase 1**: Basic auto-detection (✅ Complete)
- **Phase 2**: Enhanced notifications and dashboard
- **Phase 3**: AI-powered insights and automation
- **Phase 4**: Multi-platform support and advanced analytics

---

## Quick Start Checklist

1. **✅ Prerequisites**: Ensure scraper dependencies are installed
2. **✅ Configuration**: Set up notification channels (optional)
3. **✅ Authentication**: Verify Wallapop session works
4. **✅ Start System**: Run `python scripts/start_auto_detection.py`
5. **✅ Monitor**: Check dashboard for auto-detected products
6. **✅ Notifications**: Verify you receive new product alerts

## Support

- **Documentation**: `/docs/` directory
- **Examples**: `/examples/auto_detection/`
- **Issues**: Check logs in `/logs/` directory
- **Testing**: Use `/scripts/test_auto_detection.py`

The Wall-E Auto-Detection System brings full automation to product management, eliminating manual work while maintaining the security and reliability that Wall-E is known for.