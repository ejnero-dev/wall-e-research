# Wall-E Dashboard API

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/emilio/wall-e-research/
pip install fastapi uvicorn websockets aioredis
```

### 2. Start the Dashboard Server

```bash
# From the wall-e-research directory
python src/api/dashboard_server.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/api/dashboard/ws/live

### 3. Test the Endpoints

```bash
# Run the test suite
python src/api/test_dashboard.py
```

## 📊 Available Endpoints

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/api/dashboard/health` | GET | Health check |
| `/api/dashboard/metrics/summary` | GET | Dashboard metrics |
| `/api/dashboard/scraper/status` | GET | Scraper status |
| `/api/dashboard/logs/recent` | GET | Recent logs |
| `/api/dashboard/config/current` | GET | Current configuration |
| `/api/dashboard/config/update` | POST | Update configuration |

### WebSocket Endpoint

| Endpoint | Description |
|----------|-------------|
| `/api/dashboard/ws/live` | Real-time updates for metrics, logs, and status |

## 📝 Example Usage

### Get Metrics
```bash
curl http://localhost:8000/api/dashboard/metrics/summary
```

### Update Configuration
```bash
curl -X POST http://localhost:8000/api/dashboard/config/update \
  -H "Content-Type: application/json" \
  -d '{"key": "msg_per_hour", "value": 75, "apply_immediately": true}'
```

### WebSocket Connection (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/api/dashboard/ws/live');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data.type, data.data);
};
```

## 🔧 Development Mode

The server runs with auto-reload enabled by default. Any changes to files in `src/api/` will automatically restart the server.

## 🐛 Troubleshooting

### Redis Connection Issues
The API works with or without Redis. If Redis is not available, it will use mock data for development.

To install and start Redis:
```bash
# Install Redis (if not installed)
sudo apt-get install redis-server

# Start Redis
redis-server
```

### Port Already in Use
If port 8000 is already in use, modify the port in `dashboard_server.py`:
```python
"port": 8001,  # Change to available port
```

## 📦 Next Steps

1. **Frontend Development**: Create the Next.js dashboard UI
2. **Redis Integration**: Connect to actual bot data through Redis
3. **Authentication**: Add auth for production use
4. **Monitoring**: Integrate with actual scraper and bot metrics

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Next.js   │────▶│  FastAPI    │────▶│    Redis    │
│  Dashboard  │     │     API     │     │    Cache    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                    │
       │                   ▼                    ▼
       │            ┌─────────────┐     ┌─────────────┐
       └───────────▶│  WebSocket  │     │  Wall-E     │
                    │   Updates   │◀────│     Bot     │
                    └─────────────┘     └─────────────┘
```

## 📄 License

Part of Wall-E Research Project
