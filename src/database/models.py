"""
SQLAlchemy models for Wallapop Bot MVP
Minimal schema focusing on Happy Path: products, buyers, conversations, messages
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    ForeignKey, Index, Enum, JSON, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class ConversationStatus(enum.Enum):
    """Status of a conversation"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class MessageType(enum.Enum):
    """Type of message in conversation"""
    USER_MESSAGE = "user_message"
    BOT_MESSAGE = "bot_message"
    SYSTEM_MESSAGE = "system_message"


class ProductStatus(enum.Enum):
    """Status of a product listing"""
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    INACTIVE = "inactive"


class Product(Base):
    """Product listing model"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    wallapop_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default='EUR')
    status = Column(Enum(ProductStatus), default=ProductStatus.AVAILABLE, nullable=False)
    
    # Product details
    category = Column(String(100))
    condition = Column(String(50))  # new, like_new, good, fair
    location = Column(String(100))
    
    # Tracking
    views_count = Column(Integer, default=0)
    favorites_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    listed_at = Column(DateTime(timezone=True))
    sold_at = Column(DateTime(timezone=True))
    
    # Relationships
    conversations = relationship("Conversation", back_populates="product", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_product_status_created', 'status', 'created_at'),
        Index('idx_product_price', 'price'),
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, wallapop_id={self.wallapop_id}, title={self.title[:30]}...)>"


class Buyer(Base):
    """Buyer/User model"""
    __tablename__ = 'buyers'
    
    id = Column(Integer, primary_key=True)
    wallapop_user_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    display_name = Column(String(100))
    
    # Trust metrics
    is_verified = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    trust_score = Column(Float, default=0.5)  # 0-1 scale
    
    # Contact info (optional, for completed sales)
    phone = Column(String(20))
    email = Column(String(100))
    
    # Behavior tracking
    total_conversations = Column(Integer, default=0)
    completed_purchases = Column(Integer, default=0)
    cancelled_conversations = Column(Integer, default=0)
    
    # Metadata
    profile_data = Column(JSON)  # Store additional profile info
    last_active_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    conversations = relationship("Conversation", back_populates="buyer", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="buyer", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_buyer_active', 'is_blocked', 'last_active_at'),
    )
    
    def __repr__(self):
        return f"<Buyer(id={self.id}, username={self.username}, verified={self.is_verified})>"


class Conversation(Base):
    """Conversation between bot and buyer about a product"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    wallapop_chat_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign keys
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    buyer_id = Column(Integer, ForeignKey('buyers.id'), nullable=False)
    
    # Conversation state
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False)
    last_message_at = Column(DateTime(timezone=True))
    message_count = Column(Integer, default=0)
    
    # Business logic
    negotiated_price = Column(Float)  # Final agreed price if different from listing
    meeting_location = Column(String(200))
    meeting_time = Column(DateTime(timezone=True))
    
    # AI/Bot metadata
    intent_detected = Column(String(50))  # buy, negotiate, question, spam
    sentiment_score = Column(Float)  # -1 to 1
    bot_confidence = Column(Float)  # 0 to 1
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    product = relationship("Product", back_populates="conversations")
    buyer = relationship("Buyer", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", 
                          order_by="Message.created_at")
    
    # Indexes
    __table_args__ = (
        Index('idx_conversation_status_updated', 'status', 'updated_at'),
        Index('idx_conversation_product_buyer', 'product_id', 'buyer_id'),
        UniqueConstraint('product_id', 'buyer_id', name='uq_product_buyer'),
    )
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, product_id={self.product_id}, buyer_id={self.buyer_id}, status={self.status.value})>"


class Message(Base):
    """Individual message within a conversation"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    wallapop_message_id = Column(String(50), unique=True, index=True)
    
    # Foreign keys
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    buyer_id = Column(Integer, ForeignKey('buyers.id'))  # Null for bot messages
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), nullable=False)
    
    # Analysis results
    intent = Column(String(50))  # Detected intent
    entities = Column(JSON)  # Extracted entities (price, location, etc.)
    sentiment = Column(Float)  # -1 to 1
    
    # Status
    is_read = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    buyer = relationship("Buyer", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_message_conversation_created', 'conversation_id', 'created_at'),
        Index('idx_message_type_processed', 'message_type', 'is_processed'),
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, type={self.message_type.value}, content={self.content[:50]}...)>"


# Optional: Session tracking for Redis integration
class BotSession(Base):
    """Track bot sessions for rate limiting and state management"""
    __tablename__ = 'bot_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Session data
    active_conversations_count = Column(Integer, default=0)
    messages_sent_today = Column(Integer, default=0)
    last_activity_at = Column(DateTime(timezone=True))
    
    # Rate limiting
    is_rate_limited = Column(Boolean, default=False)
    rate_limit_expires_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<BotSession(id={self.id}, session_id={self.session_id}, active={self.active_conversations_count})>"