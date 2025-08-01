# Database Documentation

This directory contains the database layer for the Wallapop Bot MVP, including PostgreSQL models, Redis caching, and database management utilities.

## Architecture Overview

The database architecture follows a simple, normalized design focused on the Happy Path:

- **Products**: Store product listings from Wallapop
- **Buyers**: User profiles and trust metrics
- **Conversations**: Chat sessions between bot and buyers
- **Messages**: Individual messages within conversations
- **BotSessions**: Session tracking for rate limiting

## Quick Start

### 1. Start Database Services

```bash
# Start PostgreSQL and Redis with Docker Compose
docker-compose up -d postgres redis

# Check services are running
docker-compose ps
```

### 2. Initialize Database

```bash
# Create tables and setup database
python scripts/init_database.py

# Or with sample data for testing
python scripts/init_database.py --sample-data
```

### 3. Verify Setup

```bash
# Test connections
python scripts/db_manager.py test

# View database stats
python scripts/db_manager.py stats
```

## Database Schema

### Products Table
- **id**: Primary key
- **wallapop_id**: Unique identifier from Wallapop
- **title, description**: Product information
- **price, currency**: Pricing information
- **status**: AVAILABLE, RESERVED, SOLD, INACTIVE
- **category, condition, location**: Product details
- **views_count, favorites_count**: Engagement metrics
- **created_at, updated_at, listed_at, sold_at**: Timestamps

### Buyers Table
- **id**: Primary key
- **wallapop_user_id**: Unique Wallapop user identifier
- **username, display_name**: User information
- **is_verified, is_blocked**: Trust flags
- **trust_score**: 0-1 trust metric
- **phone, email**: Contact info (for completed sales)
- **total_conversations, completed_purchases**: Statistics
- **profile_data**: JSON field for additional data

### Conversations Table
- **id**: Primary key
- **wallapop_chat_id**: Unique Wallapop chat identifier
- **product_id, buyer_id**: Foreign keys
- **status**: ACTIVE, COMPLETED, CANCELLED, BLOCKED
- **message_count, last_message_at**: Activity tracking
- **negotiated_price**: Final price if different from listing
- **meeting_location, meeting_time**: Sale logistics
- **intent_detected, sentiment_score**: AI analysis results

### Messages Table
- **id**: Primary key
- **wallapop_message_id**: Unique Wallapop message identifier
- **conversation_id, buyer_id**: Foreign keys
- **content**: Message text
- **message_type**: USER_MESSAGE, BOT_MESSAGE, SYSTEM_MESSAGE
- **intent, entities, sentiment**: NLP analysis results
- **is_read, is_processed**: Status flags

## Usage Examples

### Basic Database Operations

```python
from src.database import DatabaseManager, DatabaseConfig

# Initialize
config = DatabaseConfig()
db_manager = DatabaseManager(config.get_database_url())

# Create a product
product = db_manager.create_product(
    wallapop_id="12345",
    title="iPhone 13 Pro",
    price=650.0,
    status=ProductStatus.AVAILABLE
)

# Create a buyer
buyer = db_manager.create_or_update_buyer(
    wallapop_user_id="buyer123",
    username="juan_comprador"
)

# Start a conversation
conversation = db_manager.create_conversation(
    wallapop_chat_id="chat456",
    product_id=product.id,
    buyer_id=buyer.id
)

# Add messages
db_manager.create_message(
    conversation_id=conversation.id,
    content="¡Hola! Me interesa tu iPhone",
    message_type=MessageType.USER_MESSAGE,
    buyer_id=buyer.id
)
```

### Redis Operations

```python
from src.database.redis_manager import RedisManager
from src.database.config import DatabaseConfig

# Initialize Redis
config = DatabaseConfig()
redis_manager = RedisManager(config.get_redis_config())

# Cache data
redis_manager.set_cache("product:123", {"title": "iPhone", "price": 650})

# Get cached data
product_data = redis_manager.get_cache("product:123")

# Session management
redis_manager.set_session("session123", {"user_id": 456, "active": True})

# Rate limiting
is_limited = redis_manager.is_rate_limited("user456", limit=10, window_seconds=60)
```

## Database Management Commands

```bash
# Initialize database
python scripts/db_manager.py setup

# Show statistics
python scripts/db_manager.py stats

# Test connections
python scripts/db_manager.py test

# Clean up old sessions
python scripts/db_manager.py cleanup --days 7

# Export data
python scripts/db_manager.py export -o backup.json

# Drop all tables (dangerous!)
python scripts/db_manager.py drop --force
```

## Migration Management

The project uses Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Show migration history
alembic history
```

## Configuration

Database configuration is loaded from `config/config.yaml`:

```yaml
database:
  host: "localhost"
  port: 5432
  name: "wallapop_bot"
  user: "wallapop_user"
  password: "change_this_password"

redis:
  host: "localhost"
  port: 6379
  db: 0
  password: null
```

Environment variables override config file values:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD`

## Performance Considerations

### Indexes
The schema includes optimized indexes for common queries:
- `idx_product_status_created`: Fast product lookups by status
- `idx_conversation_status_updated`: Recent active conversations
- `idx_message_conversation_created`: Message history retrieval

### Connection Pooling
- SQLAlchemy connection pool: 5 connections, max overflow 10
- Connection recycling after 1 hour
- Pre-ping verification to handle dropped connections

### Redis Caching
- Session data cached for 24 hours
- Conversation state cached during active chats
- Rate limiting with sliding windows
- Product data cached for faster lookups

## Monitoring and Maintenance

### Health Checks
```python
# Database health
config = DatabaseConfig()
health = config.validate_connection()

# Redis health
redis_health = redis_manager.health_check()
```

### Daily Maintenance
- Clean up old bot sessions (7+ days)
- Archive completed conversations (30+ days)
- Update user trust scores based on activity
- Generate daily analytics reports

### Backup Strategy
- PostgreSQL: Daily automated backups via Docker
- Redis: AOF persistence with daily snapshots
- Export critical data via `db_manager.py export`

## Security Notes

1. **Connection Security**: Use SSL in production
2. **Password Management**: Store credentials in environment variables
3. **Data Privacy**: Limit personal data storage, encrypt sensitive fields
4. **Access Control**: Restrict database access to application user only
5. **SQL Injection**: All queries use parameterized statements via SQLAlchemy

## Troubleshooting

### Common Issues

**Connection Failed**
```bash
# Check if services are running
docker-compose ps

# Check logs
docker-compose logs postgres
docker-compose logs redis
```

**Migration Errors**
```bash
# Reset migration head
alembic stamp head

# Force migration
alembic upgrade head --sql
```

**Performance Issues**
```bash
# Check slow queries in PostgreSQL
docker exec -it wallapop_postgres psql -U wallapop_user -d wallapop_bot -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Monitor Redis memory
docker exec -it wallapop_redis redis-cli info memory
```

## Development Workflow

1. **Model Changes**: Modify models in `models.py`
2. **Generate Migration**: `alembic revision --autogenerate -m "Description"`
3. **Review Migration**: Check generated SQL in `alembic/versions/`
4. **Test Migration**: Apply to development database
5. **Update Tests**: Add tests for new functionality
6. **Deploy**: Apply migration to production

For more details, see the main project documentation.