"""
Dashboard Simple para Wall-E Bot
=================================
Backend minimalista sin WebSockets ni complejidad innecesaria.
Solo endpoints REST esenciales para el control total del bot.
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import asyncio
import time

# Configuración de logging simple
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# MODELOS DE DATOS (Simples y directos)
# ============================================

class Product(BaseModel):
    """Producto en venta"""
    id: str
    title: str
    price: float
    description: str
    status: str  # 'active', 'sold', 'reserved', 'paused'
    views: int
    messages_count: int
    created_at: str
    image_url: Optional[str] = None

class Message(BaseModel):
    """Mensaje de conversación"""
    id: int
    conversation_id: str
    product_id: str
    buyer_name: str
    content: str
    is_from_bot: bool
    timestamp: str
    requires_attention: bool
    fraud_score: int

class MessageReply(BaseModel):
    """Respuesta manual a un mensaje"""
    conversation_id: str
    content: str

class BotStatus(BaseModel):
    """Estado del bot"""
    is_running: bool
    messages_per_hour: int
    active_conversations: int
    last_activity: str

# ============================================
# BASE DE DATOS SIMPLE (SQLite)
# ============================================

DB_PATH = Path("/home/emilio/wall-e-research/data/dashboard.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

@contextmanager
def get_db():
    """Context manager para conexiones a la base de datos"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Inicializa las tablas de la base de datos"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Tabla de productos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                views INTEGER DEFAULT 0,
                messages_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_url TEXT
            )
        """)
        
        # Tabla de conversaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                product_id TEXT,
                buyer_name TEXT,
                buyer_id TEXT,
                status TEXT DEFAULT 'active',
                last_message TIMESTAMP,
                messages_count INTEGER DEFAULT 0,
                requires_attention BOOLEAN DEFAULT 0,
                fraud_score INTEGER DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Tabla de mensajes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                content TEXT,
                is_from_bot BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        
        # Tabla de configuración del bot
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        logger.info("Base de datos inicializada")

# ============================================
# APLICACIÓN FASTAPI
# ============================================

app = FastAPI(
    title="Wall-E Dashboard Simple",
    description="Control directo y simple del bot de Wallapop",
    version="2.0.0"
)

# CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ENDPOINTS - PRODUCTOS
# ============================================

@app.get("/api/products", response_model=List[Product])
async def get_products(status: Optional[str] = None):
    """Obtiene todos los productos o filtrados por estado"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT * FROM products WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
        else:
            cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
        
        products = []
        for row in cursor.fetchall():
            products.append(Product(
                id=row["id"],
                title=row["title"],
                price=row["price"],
                description=row["description"] or "",
                status=row["status"],
                views=row["views"],
                messages_count=row["messages_count"],
                created_at=row["created_