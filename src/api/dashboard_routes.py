"""
Dashboard API Routes for Wall-E Research
Minimal endpoints for MVP dashboard functionality
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union, Any
from pathlib import Path
import weakref
import uuid

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl
import redis.asyncio as redis

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Redis connection (will be initialized in server)
redis_client: Optional[redis.Redis] = None


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for the dashboard"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._connection_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket) -> str:
        """Accept new WebSocket connection and return connection ID"""
        connection_id = str(uuid.uuid4())
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(
            f"WebSocket connection {connection_id} established. Total connections: {len(self.active_connections)}"
        )
        return connection_id

    def disconnect(self, websocket: WebSocket, connection_id: str = None):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if connection_id and connection_id in self._connection_tasks:
            task = self._connection_tasks.pop(connection_id)
            if not task.done():
                task.cancel()

        logger.info(
            f"WebSocket connection {connection_id} disconnected. Total connections: {len(self.active_connections)}"
        )

    async def send_to_connection(self, websocket: WebSocket, message: dict) -> bool:
        """Send message to specific connection with error handling"""
        try:
            if websocket in self.active_connections:
                await websocket.send_json(message)
                return True
        except Exception as e:
            logger.warning(f"Failed to send message to WebSocket: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        return False

    async def broadcast(self, message: dict):
        """Broadcast message to all active connections"""
        if not self.active_connections:
            return

        disconnected = set()
        for websocket in self.active_connections.copy():
            success = await self.send_to_connection(websocket, message)
            if not success:
                disconnected.add(websocket)

        # Clean up disconnected connections
        for websocket in disconnected:
            self.active_connections.discard(websocket)

    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)


# Global connection manager instance
connection_manager = ConnectionManager()


# ============= Pydantic Models =============
class MetricsSummary(BaseModel):
    """Summary metrics for dashboard overview"""

    msg_rate: float  # Messages per hour
    active_scrapers: int  # Number of active scrapers
    success_rate: float  # Success rate percentage
    avg_response_time: float  # Average response time in seconds
    total_messages_today: int
    total_errors_today: int
    timestamp: str


class ScraperStatus(BaseModel):
    """Status of a scraper instance"""

    scraper_id: str
    status: str  # 'active', 'idle', 'error', 'stopped'
    last_activity: str
    messages_processed: int
    uptime_seconds: int
    current_task: Optional[str] = None


class LogEntry(BaseModel):
    """Log entry for live monitoring"""

    id: str
    timestamp: str
    level: str  # 'info', 'warning', 'error', 'debug'
    message: str
    source: str  # Component that generated the log
    metadata: Optional[Dict] = None


class ConfigUpdate(BaseModel):
    """Configuration update request"""

    key: str
    value: Union[str, int, float, bool]
    apply_immediately: bool = True


# ============= Product Management Models =============


class ProductCondition(str):
    """Product condition types"""

    NUEVO = "nuevo"
    COMO_NUEVO = "como_nuevo"
    BUEN_ESTADO = "buen_estado"
    USADO = "usado"
    PARA_PIEZAS = "para_piezas"


class ProductStatus(str):
    """Product status types"""

    ACTIVE = "active"
    PAUSED = "paused"
    SOLD = "sold"
    EXPIRED = "expired"
    REMOVED = "removed"
    ERROR = "error"


class ProductFormData(BaseModel):
    """Product creation form data"""

    wallapop_url: HttpUrl
    auto_respond: bool = True
    ai_personality: Optional[str] = "professional"
    response_delay_min: int = Field(default=15, ge=1, le=180)
    response_delay_max: int = Field(default=60, ge=1, le=180)


class Product(BaseModel):
    """Product model for dashboard"""

    id: str
    title: str
    description: str
    price: float
    original_price: Optional[float] = None
    sku: Optional[str] = None
    category: str
    condition: str  # ProductCondition
    status: str  # ProductStatus
    wallapop_url: str
    image_url: Optional[str] = None
    images: Optional[List[str]] = None

    # Analytics & Performance
    views: int = 0
    messages_received: int = 0
    last_activity: Optional[str] = None
    created_at: str
    updated_at: str

    # AI & Automation Settings
    auto_respond: bool = False
    ai_personality: Optional[str] = None
    response_delay_min: Optional[int] = None
    response_delay_max: Optional[int] = None

    # Location & Shipping
    location: Optional[str] = None
    shipping_available: bool = False
    shipping_cost: Optional[float] = None

    # Performance Metrics
    conversion_rate: Optional[float] = None
    avg_response_time: Optional[float] = None
    fraud_attempts: int = 0
    successful_sales: int = 0


class ProductStats(BaseModel):
    """Product statistics summary"""

    total: int
    active: int
    paused: int
    sold: int
    total_views: int
    total_messages: int
    conversion_rate: float
    revenue_this_month: float


class BulkProductUpdate(BaseModel):
    """Bulk product update request"""

    product_ids: List[str]
    updates: Dict[str, Union[str, int, float, bool]]


# ============= Helper Functions =============
async def get_redis_client():
    """Get or create Redis client"""
    global redis_client
    if not redis_client:
        try:
            redis_client = await redis.from_url(
                "redis://localhost:6379", encoding="utf-8", decode_responses=True
            )
            await redis_client.ping()
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Return None to allow fallback to mock data
            return None
    return redis_client


async def get_mock_metrics() -> MetricsSummary:
    """Generate mock metrics for development"""
    import random

    return MetricsSummary(
        msg_rate=random.uniform(30, 60),
        active_scrapers=random.randint(1, 5),
        success_rate=random.uniform(85, 99),
        avg_response_time=random.uniform(1.5, 3.5),
        total_messages_today=random.randint(200, 500),
        total_errors_today=random.randint(0, 20),
        timestamp=datetime.now().isoformat(),
    )


async def get_mock_logs(limit: int = 50) -> List[LogEntry]:
    """Generate mock logs for development"""
    import random
    import uuid

    log_templates = [
        ("info", "Scraper initialized", "scraper"),
        ("info", "Login successful", "auth"),
        ("info", "Message sent to user", "bot"),
        ("warning", "Rate limit approaching", "scraper"),
        ("error", "Failed to parse message", "parser"),
        ("info", "Configuration reloaded", "config"),
        ("debug", "Cache hit for price data", "cache"),
    ]

    logs = []
    base_time = datetime.now()

    for i in range(limit):
        level, msg, source = random.choice(log_templates)
        log_time = base_time - timedelta(seconds=i * 10)

        logs.append(
            LogEntry(
                id=str(uuid.uuid4())[:8],
                timestamp=log_time.isoformat(),
                level=level,
                message=f"{msg} #{random.randint(1000, 9999)}",
                source=source,
                metadata=(
                    {"session_id": str(uuid.uuid4())[:8]} if level == "error" else None
                ),
            )
        )

    return logs


# AI Engine integration
ai_engine_instance = None


def get_ai_engine():
    """Get or initialize AI Engine instance"""
    global ai_engine_instance
    if not ai_engine_instance:
        try:
            from src.ai_engine import AIEngine, AIEngineConfig

            config = AIEngineConfig.for_research()
            ai_engine_instance = AIEngine(config)
            logger.info("AI Engine initialized for dashboard metrics")
        except Exception as e:
            logger.error(f"Failed to initialize AI Engine: {e}")
            return None
    return ai_engine_instance


# ============= API Endpoints =============
@router.get("/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary():
    """
    Get summary metrics for dashboard overview
    Returns key performance indicators
    """
    try:
        client = await get_redis_client()

        if client:
            # Try to get real metrics from Redis
            metrics_data = await client.get("dashboard:metrics:summary")
            if metrics_data:
                return MetricsSummary(**json.loads(metrics_data))

        # Try to get AI Engine metrics if available
        ai_engine = get_ai_engine()
        if ai_engine:
            try:
                ai_stats = ai_engine.get_performance_stats()
                # Calculate derived metrics
                total_reqs = ai_stats.get("total_requests", 0)
                success_count = int(total_reqs * ai_stats.get("success_rate", 0.0))

                return MetricsSummary(
                    msg_rate=ai_stats.get("requests_per_second", 0.0)
                    * 3600,  # Convert to per hour
                    active_scrapers=(
                        2 if ai_stats.get("engine_status") == "ready" else 0
                    ),
                    success_rate=ai_stats.get("success_rate", 0.0) * 100,
                    avg_response_time=ai_stats.get("average_response_time", 0.0),
                    total_messages_today=total_reqs,
                    total_errors_today=total_reqs - success_count,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.warning(f"Error getting AI Engine metrics: {e}")

        # Fallback to mock data for development
        return await get_mock_metrics()

    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        # Return mock data on error
        return await get_mock_metrics()


@router.get("/scraper/status", response_model=List[ScraperStatus])
async def get_scraper_status():
    """
    Get status of all active scrapers
    Returns detailed information about each scraper instance
    """
    try:
        client = await get_redis_client()

        if client:
            # Try to get real scraper status
            scraper_keys = await client.keys("scraper:status:*")
            if scraper_keys:
                scrapers = []
                for key in scraper_keys:
                    data = await client.get(key)
                    if data:
                        scrapers.append(ScraperStatus(**json.loads(data)))
                return scrapers

        # Mock data for development
        return [
            ScraperStatus(
                scraper_id="scraper-001",
                status="active",
                last_activity=datetime.now().isoformat(),
                messages_processed=47,
                uptime_seconds=3600,
                current_task="Processing message queue",
            ),
            ScraperStatus(
                scraper_id="scraper-002",
                status="idle",
                last_activity=(datetime.now() - timedelta(minutes=5)).isoformat(),
                messages_processed=123,
                uptime_seconds=7200,
                current_task=None,
            ),
        ]

    except Exception as e:
        logger.error(f"Error fetching scraper status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/recent", response_model=List[LogEntry])
async def get_recent_logs(
    limit: int = 50, level: Optional[str] = None, source: Optional[str] = None
):
    """
    Get recent log entries

    Args:
        limit: Maximum number of logs to return (default: 50, max: 200)
        level: Filter by log level (info, warning, error, debug)
        source: Filter by source component
    """
    try:
        # Validate parameters
        limit = min(limit, 200)  # Cap at 200

        client = await get_redis_client()

        if client:
            # Try to get real logs from Redis
            logs_data = await client.lrange("dashboard:logs", 0, limit - 1)
            if logs_data:
                logs = [LogEntry(**json.loads(log)) for log in logs_data]

                # Apply filters if provided
                if level:
                    logs = [log for log in logs if log.level == level]
                if source:
                    logs = [log for log in logs if log.source == source]

                return logs[:limit]

        # Fallback to mock data
        logs = await get_mock_logs(limit)

        # Apply filters
        if level:
            logs = [log for log in logs if log.level == level]
        if source:
            logs = [log for log in logs if log.source == source]

        return logs

    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        # Return mock data on error
        return await get_mock_logs(limit)


@router.post("/config/update")
async def update_configuration(config: ConfigUpdate):
    """
    Update configuration with hot-reload

    Args:
        config: Configuration key-value pair to update
    """
    try:
        client = await get_redis_client()

        # Validate config key (add your valid keys here)
        valid_keys = [
            "msg_per_hour",
            "retry_attempts",
            "timeout",
            "rate_limit",
            "debug_mode",
            "auto_response",
        ]

        if config.key not in valid_keys:
            raise HTTPException(
                status_code=400, detail=f"Invalid configuration key: {config.key}"
            )

        if client:
            # Store in Redis
            await client.set(
                f"config:{config.key}",
                json.dumps(
                    {
                        "value": config.value,
                        "updated_at": datetime.now().isoformat(),
                        "updated_by": "dashboard",
                    }
                ),
            )

            # Publish update event if immediate apply requested
            if config.apply_immediately:
                await client.publish(
                    "config:updates",
                    json.dumps({"key": config.key, "value": config.value}),
                )

        return {
            "status": "success",
            "message": f"Configuration '{config.key}' updated",
            "applied": config.apply_immediately,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-engine/stats")
async def get_ai_engine_stats():
    """
    Get AI Engine performance statistics
    Returns detailed metrics from the AI Engine
    """
    try:
        ai_engine = get_ai_engine()

        if not ai_engine:
            # Return mock/fallback stats if AI Engine not available
            return {
                "status": "unavailable",
                "engine_status": "error",
                "uptime_seconds": 0,
                "total_requests": 0,
                "success_rate": 0.0,
                "ai_response_rate": 0.0,
                "average_response_time": 0.0,
                "requests_per_second": 0.0,
                "error": "AI Engine not available",
            }

        # Get real performance stats
        stats = ai_engine.get_performance_stats()
        stats["status"] = "available"

        return stats

    except Exception as e:
        logger.error(f"Error fetching AI Engine stats: {e}")
        return {
            "status": "error",
            "error": str(e),
            "engine_status": "error",
            "uptime_seconds": 0,
            "total_requests": 0,
            "success_rate": 0.0,
            "ai_response_rate": 0.0,
            "average_response_time": 0.0,
            "requests_per_second": 0.0,
        }


@router.get("/config/current")
async def get_current_configuration():
    """
    Get current configuration values
    """
    try:
        client = await get_redis_client()

        config = {
            "msg_per_hour": 50,
            "retry_attempts": 3,
            "timeout": 30,
            "rate_limit": 100,
            "debug_mode": True,
            "auto_response": True,
        }

        if client:
            # Get config from Redis
            for key in config.keys():
                data = await client.get(f"config:{key}")
                if data:
                    config_data = json.loads(data)
                    config[key] = config_data.get("value", config[key])

        return config

    except Exception as e:
        logger.error(f"Error fetching configuration: {e}")
        # Return default config on error
        return {
            "msg_per_hour": 50,
            "retry_attempts": 3,
            "timeout": 30,
            "rate_limit": 100,
            "debug_mode": True,
            "auto_response": True,
        }


# ============= Product Management API Endpoints =============

# In-memory mock storage for products (in production, use database)
mock_products: Dict[str, Product] = {}


def generate_mock_products() -> None:
    """Initialize mock products if empty"""
    if not mock_products:
        products = [
            Product(
                id="prod-001",
                title="iPhone 14 Pro 256GB Space Black",
                description="iPhone 14 Pro en perfecto estado, apenas usado, viene con todos los accesorios originales.",
                price=850.0,
                original_price=1200.0,
                sku="IPHONE14-PRO-256-BLK",
                category="Electrónica",
                condition="como_nuevo",
                status="active",
                wallapop_url="https://wallapop.com/item/iphone-14-pro-256gb-123456",
                image_url="https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400",
                views=1247,
                messages_received=23,
                last_activity=(datetime.now() - timedelta(hours=2)).isoformat(),
                created_at=(datetime.now() - timedelta(days=7)).isoformat(),
                updated_at=(datetime.now() - timedelta(hours=1)).isoformat(),
                auto_respond=True,
                ai_personality="professional",
                response_delay_min=15,
                response_delay_max=60,
                location="Madrid",
                shipping_available=True,
                shipping_cost=5.99,
                conversion_rate=18.5,
                successful_sales=0,
            ),
            Product(
                id="prod-002",
                title="MacBook Air M2 2022 16GB 512GB",
                description="MacBook Air con chip M2, prácticamente nuevo, ideal para estudiantes y profesionales.",
                price=1100.0,
                original_price=1499.0,
                category="Informática",
                condition="como_nuevo",
                status="active",
                wallapop_url="https://wallapop.com/item/macbook-air-m2-789012",
                image_url="https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400",
                views=892,
                messages_received=15,
                last_activity=(datetime.now() - timedelta(hours=4)).isoformat(),
                created_at=(datetime.now() - timedelta(days=5)).isoformat(),
                updated_at=(datetime.now() - timedelta(minutes=30)).isoformat(),
                auto_respond=True,
                ai_personality="friendly",
                response_delay_min=10,
                response_delay_max=45,
                location="Barcelona",
                shipping_available=True,
                shipping_cost=9.99,
                conversion_rate=16.8,
                successful_sales=0,
            ),
            Product(
                id="prod-003",
                title="PlayStation 5 + 2 Mandos + 5 Juegos",
                description="PlayStation 5 en perfecto estado con mandos adicionales y juegos premium.",
                price=650.0,
                original_price=799.0,
                category="Videojuegos",
                condition="buen_estado",
                status="sold",
                wallapop_url="https://wallapop.com/item/ps5-bundle-345678",
                image_url="https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400",
                views=2156,
                messages_received=47,
                last_activity=(datetime.now() - timedelta(days=1)).isoformat(),
                created_at=(datetime.now() - timedelta(days=12)).isoformat(),
                updated_at=(datetime.now() - timedelta(days=1)).isoformat(),
                auto_respond=False,
                location="Valencia",
                shipping_available=False,
                conversion_rate=21.8,
                successful_sales=1,
            ),
        ]

        for product in products:
            mock_products[product.id] = product


@router.get("/products", response_model=List[Product])
async def get_products():
    """
    Get all products
    Returns list of all managed products
    """
    try:
        generate_mock_products()  # Ensure mock data exists

        client = await get_redis_client()

        if client:
            # Try to get products from Redis
            product_keys = await client.keys("product:*")
            if product_keys:
                products = []
                for key in product_keys:
                    data = await client.get(key)
                    if data:
                        products.append(Product(**json.loads(data)))
                return products

        # Return mock products
        return list(mock_products.values())

    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        generate_mock_products()
        return list(mock_products.values())


@router.post("/products", response_model=Product)
async def add_product(product_data: Union[ProductFormData, Dict[str, Any]]):
    """
    Add a new product from Wallapop URL
    Supports both manual addition and auto-detected products
    """
    try:
        generate_mock_products()  # Ensure mock data exists

        # Handle both ProductFormData and raw dict (from auto-detection)
        if isinstance(product_data, dict):
            # Auto-detected product data
            wallapop_url = product_data["wallapop_url"]
            auto_respond = product_data.get("auto_respond", True)
            ai_personality = product_data.get("ai_personality", "professional")
            response_delay_min = product_data.get("response_delay_min", 15)
            response_delay_max = product_data.get("response_delay_max", 60)
            detected_data = product_data.get("_detected_data", {})
            is_auto_detected = product_data.get("_auto_detected", False)
        else:
            # Manual product form data
            wallapop_url = str(product_data.wallapop_url)
            auto_respond = product_data.auto_respond
            ai_personality = product_data.ai_personality
            response_delay_min = product_data.response_delay_min
            response_delay_max = product_data.response_delay_max
            detected_data = {}
            is_auto_detected = False

        product_id = f"prod-{len(mock_products) + 1:03d}"

        # Create product with detected or default data
        if detected_data:
            # Use auto-detected product information
            new_product = Product(
                id=product_id,
                title=detected_data.get("title", "Auto-detected Product"),
                description=detected_data.get(
                    "description", "Product automatically imported from Wallapop"
                ),
                price=detected_data.get("price", 0.0),
                category=detected_data.get("category", "General"),
                condition=detected_data.get("condition", "unknown"),
                status=detected_data.get("status", "active"),
                wallapop_url=wallapop_url,
                image_url=(
                    detected_data.get("image_urls", [None])[0]
                    if detected_data.get("image_urls")
                    else None
                ),
                images=detected_data.get("image_urls", []),
                views=detected_data.get("views", 0),
                messages_received=detected_data.get("messages_count", 0),
                location=detected_data.get("location", ""),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                auto_respond=auto_respond,
                ai_personality=ai_personality,
                response_delay_min=response_delay_min,
                response_delay_max=response_delay_max,
                # Add auto-detection metadata
                **(
                    {
                        "sku": f"AUTO-{product_id}",
                        "original_price": None,
                        "shipping_available": False,
                        "shipping_cost": None,
                        "conversion_rate": None,
                        "avg_response_time": None,
                        "fraud_attempts": 0,
                        "successful_sales": 0,
                        "last_activity": detected_data.get("detected_at"),
                    }
                    if is_auto_detected
                    else {}
                ),
            )
        else:
            # Default/manual product creation (scrape URL in real implementation)
            new_product = Product(
                id=product_id,
                title="New Product from URL",
                description="Product manually added from Wallapop URL",
                price=99.99,
                category="General",
                condition="buen_estado",
                status="active",
                wallapop_url=wallapop_url,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                auto_respond=auto_respond,
                ai_personality=ai_personality,
                response_delay_min=response_delay_min,
                response_delay_max=response_delay_max,
            )

        # Store in mock storage
        mock_products[product_id] = new_product

        # In production, store in Redis/database
        client = await get_redis_client()
        if client:
            await client.set(
                f"product:{product_id}",
                json.dumps(new_product.model_dump(), default=str),
            )

        # Log with appropriate context
        source = "auto-detection" if is_auto_detected else "manual"
        logger.info(f"Added new product ({source}): {product_id} - {new_product.title}")

        # Broadcast update via WebSocket
        await connection_manager.broadcast(
            {
                "type": "product_added",
                "data": {
                    "product": new_product.model_dump(),
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

        return new_product

    except Exception as e:
        logger.error(f"Error adding product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: str, updates: Dict[str, Union[str, int, float, bool]]
):
    """
    Update a product's settings
    """
    try:
        generate_mock_products()  # Ensure mock data exists

        # Check if product exists
        if product_id not in mock_products:
            raise HTTPException(status_code=404, detail="Product not found")

        # Update the product
        product = mock_products[product_id]
        product_dict = product.model_dump()

        # Apply updates
        for key, value in updates.items():
            if hasattr(product, key):
                product_dict[key] = value

        # Update timestamp
        product_dict["updated_at"] = datetime.now().isoformat()

        # Create updated product
        updated_product = Product(**product_dict)
        mock_products[product_id] = updated_product

        # In production, update in Redis/database
        client = await get_redis_client()
        if client:
            await client.set(
                f"product:{product_id}",
                json.dumps(updated_product.model_dump(), default=str),
            )

        logger.info(f"Updated product: {product_id}")
        return updated_product

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """
    Delete a product and stop monitoring
    """
    try:
        generate_mock_products()  # Ensure mock data exists

        # Check if product exists
        if product_id not in mock_products:
            raise HTTPException(status_code=404, detail="Product not found")

        # Remove from mock storage
        del mock_products[product_id]

        # In production, remove from Redis/database
        client = await get_redis_client()
        if client:
            await client.delete(f"product:{product_id}")

        logger.info(f"Deleted product: {product_id}")
        return {"message": "Product deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/stats", response_model=ProductStats)
async def get_product_stats():
    """
    Get product statistics summary
    """
    try:
        generate_mock_products()  # Ensure mock data exists

        products = list(mock_products.values())

        stats = ProductStats(
            total=len(products),
            active=len([p for p in products if p.status == "active"]),
            paused=len([p for p in products if p.status == "paused"]),
            sold=len([p for p in products if p.status == "sold"]),
            total_views=sum(p.views for p in products),
            total_messages=sum(p.messages_received for p in products),
            conversion_rate=0.0,
            revenue_this_month=sum(p.price for p in products if p.status == "sold"),
        )

        # Calculate conversion rate
        if stats.total_messages > 0:
            stats.conversion_rate = (stats.sold / stats.total_messages) * 100

        return stats

    except Exception as e:
        logger.error(f"Error fetching product stats: {e}")
        # Return default stats on error
        return ProductStats(
            total=0,
            active=0,
            paused=0,
            sold=0,
            total_views=0,
            total_messages=0,
            conversion_rate=0.0,
            revenue_this_month=0.0,
        )


@router.put("/products/bulk")
async def bulk_update_products(bulk_update: BulkProductUpdate):
    """
    Bulk update multiple products
    """
    try:
        generate_mock_products()  # Ensure mock data exists

        updated_products = []

        for product_id in bulk_update.product_ids:
            if product_id in mock_products:
                # Update product
                product = mock_products[product_id]
                product_dict = product.model_dump()

                # Apply updates
                for key, value in bulk_update.updates.items():
                    if hasattr(product, key):
                        product_dict[key] = value

                product_dict["updated_at"] = datetime.now().isoformat()
                updated_product = Product(**product_dict)
                mock_products[product_id] = updated_product
                updated_products.append(updated_product)

        logger.info(f"Bulk updated {len(updated_products)} products")
        return {"message": f"Successfully updated {len(updated_products)} products"}

    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= WebSocket Data Generation =============
async def generate_live_data(connection_id: str, websocket: WebSocket):
    """
    Generate and send live data updates for a specific WebSocket connection
    This function runs in a separate task for each connection
    """
    import random

    last_metrics_update = 0
    last_log_update = 0
    last_scraper_update = 0

    try:
        while websocket in connection_manager.active_connections:
            current_time = datetime.now().timestamp()

            # Send metrics update every 5 seconds (reduced frequency)
            if current_time - last_metrics_update >= 5:
                metrics_data = await get_mock_metrics()
                success = await connection_manager.send_to_connection(
                    websocket,
                    {"type": "metrics_update", "data": metrics_data.model_dump()},
                )
                if not success:
                    break
                last_metrics_update = current_time

            # Send new log every 3-7 seconds (randomized)
            if current_time - last_log_update >= random.uniform(3, 7):
                logs = await get_mock_logs(1)
                success = await connection_manager.send_to_connection(
                    websocket, {"type": "new_log", "data": logs[0].model_dump()}
                )
                if not success:
                    break
                last_log_update = current_time

            # Send scraper update every 8-12 seconds (randomized)
            if current_time - last_scraper_update >= random.uniform(8, 12):
                scraper_data = {
                    "scraper_id": f"scraper-{random.randint(1, 3):03d}",
                    "status": random.choice(["active", "idle", "processing"]),
                    "messages_processed": random.randint(40, 150),
                    "current_task": random.choice(
                        [
                            "Processing message queue",
                            "Analyzing user responses",
                            "Updating conversation state",
                            None,
                        ]
                    ),
                }
                success = await connection_manager.send_to_connection(
                    websocket, {"type": "scraper_update", "data": scraper_data}
                )
                if not success:
                    break
                last_scraper_update = current_time

            # Check every 1 second, but send updates at different intervals
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        logger.info(f"Live data generation cancelled for connection {connection_id}")
    except Exception as e:
        logger.error(
            f"Error in live data generation for connection {connection_id}: {e}"
        )
    finally:
        # Clean up connection
        connection_manager.disconnect(websocket, connection_id)


# ============= WebSocket Endpoint =============
@router.websocket("/ws/live")
async def websocket_live_data(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard data
    Sends updates for metrics, logs, and scraper status with connection stability
    """
    connection_id = None

    try:
        # Establish connection with connection manager
        connection_id = await connection_manager.connect(websocket)

        # Send initial data immediately after connection
        try:
            initial_metrics = await get_mock_metrics()
            initial_logs = await get_mock_logs(10)

            initial_data = {
                "type": "initial",
                "data": {
                    "metrics": initial_metrics.model_dump(),
                    "logs": [log.model_dump() for log in initial_logs],
                    "connection_id": connection_id,
                    "server_time": datetime.now().isoformat(),
                },
            }

            success = await connection_manager.send_to_connection(
                websocket, initial_data
            )
            if not success:
                logger.warning(
                    f"Failed to send initial data to connection {connection_id}"
                )
                return

        except Exception as e:
            logger.error(
                f"Error sending initial data to connection {connection_id}: {e}"
            )
            return

        # Start continuous data generation in background task
        data_task = asyncio.create_task(generate_live_data(connection_id, websocket))
        connection_manager._connection_tasks[connection_id] = data_task

        # Keep connection alive and wait for disconnection
        try:
            while True:
                try:
                    # Wait for potential client messages (ping/pong, etc.)
                    message = await asyncio.wait_for(
                        websocket.receive_json(), timeout=30.0
                    )

                    # Handle client heartbeat or other messages
                    if message.get("type") == "ping":
                        await connection_manager.send_to_connection(
                            websocket,
                            {"type": "pong", "timestamp": datetime.now().isoformat()},
                        )
                    elif message.get("type") == "get_status":
                        # Calculate uptime from when this connection was established
                        connection_start_time = (
                            datetime.now().timestamp() - 10
                        )  # Approximate, since we don't store exact start time
                        uptime = datetime.now().timestamp() - connection_start_time

                        await connection_manager.send_to_connection(
                            websocket,
                            {
                                "type": "status_response",
                                "data": {
                                    "connection_id": connection_id,
                                    "active_connections": connection_manager.get_connection_count(),
                                    "uptime_seconds": int(uptime),
                                    "server_time": datetime.now().isoformat(),
                                },
                            },
                        )

                except asyncio.TimeoutError:
                    # No message received within timeout - this is normal
                    # Send a heartbeat to check connection health
                    success = await connection_manager.send_to_connection(
                        websocket,
                        {"type": "heartbeat", "timestamp": datetime.now().isoformat()},
                    )
                    if not success:
                        logger.info(
                            f"Connection {connection_id} failed heartbeat check"
                        )
                        break
                    continue

        except WebSocketDisconnect:
            logger.info(f"WebSocket connection {connection_id} disconnected by client")
        except Exception as e:
            logger.warning(f"WebSocket connection {connection_id} error: {e}")

    except Exception as e:
        logger.error(f"WebSocket connection setup failed: {e}")

    finally:
        # Ensure cleanup
        if connection_id:
            connection_manager.disconnect(websocket, connection_id)
            logger.info(f"WebSocket connection {connection_id} cleaned up")


# ============= WebSocket Status Endpoint =============
@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket connection status and statistics
    """
    return {
        "active_connections": connection_manager.get_connection_count(),
        "connection_manager_status": "running",
        "websocket_endpoint": "/api/dashboard/ws/live",
        "supported_message_types": [
            "initial",
            "metrics_update",
            "new_log",
            "scraper_update",
            "heartbeat",
            "ping",
            "pong",
            "status_response",
        ],
        "update_intervals": {
            "metrics": "5 seconds",
            "logs": "3-7 seconds (randomized)",
            "scrapers": "8-12 seconds (randomized)",
            "heartbeat": "30 seconds",
        },
    }


# ============= Auto-Detection API Endpoints =============

# Global detection manager instance
detection_manager_instance = None


def get_detection_manager():
    """Get or initialize Detection Manager instance"""
    global detection_manager_instance
    if not detection_manager_instance:
        try:
            import sys
            from pathlib import Path

            # Ensure src is in path
            src_path = str(Path(__file__).parent.parent)
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            from auto_detection import DetectionManager

            detection_manager_instance = DetectionManager()
            logger.info("Detection Manager initialized for dashboard")
        except Exception as e:
            logger.error(f"Failed to initialize Detection Manager: {e}")
            return None
    return detection_manager_instance


class AutoDetectionConfig(BaseModel):
    """Auto-detection configuration"""

    enabled: bool = True
    scan_interval_minutes: int = Field(default=10, ge=5, le=120)
    auto_add_products: bool = True
    auto_respond_new_products: bool = True
    ai_personality: str = "professional"
    response_delay_min: int = Field(default=15, ge=1, le=180)
    response_delay_max: int = Field(default=60, ge=1, le=180)
    enable_notifications: bool = True


@router.get("/auto-detection/status")
async def get_auto_detection_status():
    """
    Get auto-detection system status
    Returns current status, statistics, and configuration
    """
    try:
        detection_manager = get_detection_manager()

        if not detection_manager:
            return {
                "status": "unavailable",
                "error": "Detection manager not available",
                "is_running": False,
            }

        return detection_manager.get_status()

    except Exception as e:
        logger.error(f"Error getting auto-detection status: {e}")
        return {"status": "error", "error": str(e), "is_running": False}


@router.post("/auto-detection/start")
async def start_auto_detection():
    """
    Start the auto-detection system
    """
    try:
        detection_manager = get_detection_manager()

        if not detection_manager:
            raise HTTPException(
                status_code=503, detail="Detection manager not available"
            )

        success = await detection_manager.start()

        if success:
            return {
                "status": "started",
                "message": "Auto-detection system started successfully",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to start auto-detection system"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting auto-detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-detection/stop")
async def stop_auto_detection():
    """
    Stop the auto-detection system
    """
    try:
        detection_manager = get_detection_manager()

        if not detection_manager:
            raise HTTPException(
                status_code=503, detail="Detection manager not available"
            )

        await detection_manager.stop()

        return {
            "status": "stopped",
            "message": "Auto-detection system stopped successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error stopping auto-detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-detection/scan")
async def manual_scan():
    """
    Execute a manual product scan
    Returns scan results immediately
    """
    try:
        detection_manager = get_detection_manager()

        if not detection_manager:
            raise HTTPException(
                status_code=503, detail="Detection manager not available"
            )

        scan_results = await detection_manager.manual_scan()

        return scan_results

    except Exception as e:
        logger.error(f"Error in manual scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auto-detection/config", response_model=AutoDetectionConfig)
async def get_auto_detection_config():
    """
    Get current auto-detection configuration
    """
    try:
        detection_manager = get_detection_manager()

        if not detection_manager:
            # Return default config if manager not available
            return AutoDetectionConfig()

        config = detection_manager.config

        return AutoDetectionConfig(
            enabled=detection_manager.is_running,
            scan_interval_minutes=config.get("scan_interval_minutes", 10),
            auto_add_products=detection_manager.auto_add_enabled,
            auto_respond_new_products=config.get("auto_respond_new_products", True),
            ai_personality=config.get("ai_personality", "professional"),
            response_delay_min=config.get("response_delay_min", 15),
            response_delay_max=config.get("response_delay_max", 60),
            enable_notifications=detection_manager.notification_enabled,
        )

    except Exception as e:
        logger.error(f"Error getting auto-detection config: {e}")
        return AutoDetectionConfig()  # Return defaults on error


@router.put("/auto-detection/config")
async def update_auto_detection_config(config: AutoDetectionConfig):
    """
    Update auto-detection configuration
    """
    try:
        detection_manager = get_detection_manager()

        if not detection_manager:
            raise HTTPException(
                status_code=503, detail="Detection manager not available"
            )

        # Update detection manager configuration
        detection_manager.update_config(
            {
                "scan_interval_minutes": config.scan_interval_minutes,
                "auto_respond_new_products": config.auto_respond_new_products,
                "ai_personality": config.ai_personality,
                "response_delay_min": config.response_delay_min,
                "response_delay_max": config.response_delay_max,
                "enable_notifications": config.enable_notifications,
            }
        )

        # Update manager settings
        detection_manager.set_auto_add_enabled(config.auto_add_products)
        detection_manager.set_notification_enabled(config.enable_notifications)

        # Start/stop detection based on enabled flag
        if config.enabled and not detection_manager.is_running:
            await detection_manager.start()
        elif not config.enabled and detection_manager.is_running:
            await detection_manager.stop()

        return {
            "status": "updated",
            "message": "Auto-detection configuration updated successfully",
            "config": config.model_dump(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating auto-detection config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auto-detection/statistics")
async def get_auto_detection_statistics():
    """
    Get detailed auto-detection statistics
    """
    try:
        detection_manager = get_detection_manager()

        if not detection_manager:
            return {"available": False, "error": "Detection manager not available"}

        stats = detection_manager.get_statistics()

        return {
            "available": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting auto-detection statistics: {e}")
        return {"available": False, "error": str(e)}


@router.get("/auto-detection/detected-products")
async def get_detected_products():
    """
    Get list of currently detected products (not yet in dashboard)
    """
    try:
        detection_manager = get_detection_manager()

        if not detection_manager:
            return []

        scanner = detection_manager.scanner
        known_products = scanner.get_known_products()

        # Convert to JSON-serializable format
        products_data = []
        for product in known_products:
            products_data.append(
                {
                    "id": product.id,
                    "title": product.title,
                    "price": product.price,
                    "description": product.description,
                    "status": product.status.value,
                    "wallapop_url": product.wallapop_url,
                    "image_urls": product.image_urls,
                    "views": product.views,
                    "favorites": product.favorites,
                    "messages_count": product.messages_count,
                    "created_at": product.created_at.isoformat(),
                    "last_seen": product.last_seen.isoformat(),
                    "last_modified": product.last_modified.isoformat(),
                }
            )

        return products_data

    except Exception as e:
        logger.error(f"Error getting detected products: {e}")
        return []


# ============= Health Check =============
@router.get("/health")
async def health_check():
    """
    Health check endpoint for dashboard API
    """
    try:
        # Check Redis connection
        client = await get_redis_client()
        redis_status = "connected" if client else "disconnected"

        if client:
            try:
                await client.ping()
                redis_status = "healthy"
            except Exception:
                redis_status = "unhealthy"

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "running",
                "redis": redis_status,
                "websocket": {
                    "status": "running",
                    "active_connections": connection_manager.get_connection_count(),
                },
            },
        }
    except Exception as e:
        return JSONResponse(
            status_code=503, content={"status": "unhealthy", "error": str(e)}
        )
