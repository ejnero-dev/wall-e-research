"""
Database Manager for Wallapop Bot MVP
Handles database connections and basic CRUD operations
"""
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import create_engine, and_, or_, func
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool

from .models import (
    Base, Product, Buyer, Conversation, Message, BotSession,
    ProductStatus, ConversationStatus, MessageType
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and provides CRUD operations"""
    
    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize database manager
        
        Args:
            database_url: PostgreSQL connection string
            echo: Enable SQLAlchemy logging
        """
        # Create engine with connection pooling
        self.engine = create_engine(
            database_url,
            echo=echo,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections after 1 hour
        )
        
        # Create session factory
        self.SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        )
        
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
        
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")
        
    @contextmanager
    def get_session(self) -> Session:
        """
        Provide a transactional scope for database operations
        
        Usage:
            with db_manager.get_session() as session:
                # Do database operations
                session.add(obj)
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
            
    # Product CRUD Operations
    
    def create_product(self, **kwargs) -> Product:
        """Create a new product"""
        with self.get_session() as session:
            product = Product(**kwargs)
            session.add(product)
            session.flush()
            session.refresh(product)
            return product
            
    def get_product(self, product_id: int = None, wallapop_id: str = None) -> Optional[Product]:
        """Get product by ID or Wallapop ID"""
        with self.get_session() as session:
            query = session.query(Product)
            if product_id:
                product = query.filter(Product.id == product_id).first()
            elif wallapop_id:
                product = query.filter(Product.wallapop_id == wallapop_id).first()
            else:
                return None
            return product
            
    def get_active_products(self, limit: int = 100) -> List[Product]:
        """Get all active products"""
        with self.get_session() as session:
            return session.query(Product).filter(
                Product.status == ProductStatus.AVAILABLE
            ).order_by(Product.created_at.desc()).limit(limit).all()
            
    def update_product_status(self, product_id: int, status: ProductStatus) -> bool:
        """Update product status"""
        with self.get_session() as session:
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                product.status = status
                if status == ProductStatus.SOLD:
                    product.sold_at = datetime.utcnow()
                return True
            return False
            
    # Buyer CRUD Operations
    
    def create_or_update_buyer(self, wallapop_user_id: str, **kwargs) -> Buyer:
        """Create a new buyer or update existing one"""
        with self.get_session() as session:
            buyer = session.query(Buyer).filter(
                Buyer.wallapop_user_id == wallapop_user_id
            ).first()
            
            if buyer:
                # Update existing buyer
                for key, value in kwargs.items():
                    if hasattr(buyer, key):
                        setattr(buyer, key, value)
                buyer.last_active_at = datetime.utcnow()
            else:
                # Create new buyer
                buyer = Buyer(wallapop_user_id=wallapop_user_id, **kwargs)
                session.add(buyer)
                
            session.flush()
            session.refresh(buyer)
            return buyer
            
    def get_buyer(self, buyer_id: int = None, wallapop_user_id: str = None) -> Optional[Buyer]:
        """Get buyer by ID or Wallapop user ID"""
        with self.get_session() as session:
            query = session.query(Buyer)
            if buyer_id:
                buyer = query.filter(Buyer.id == buyer_id).first()
            elif wallapop_user_id:
                buyer = query.filter(Buyer.wallapop_user_id == wallapop_user_id).first()
            else:
                return None
            return buyer
            
    def is_buyer_blocked(self, wallapop_user_id: str) -> bool:
        """Check if buyer is blocked"""
        with self.get_session() as session:
            buyer = session.query(Buyer).filter(
                Buyer.wallapop_user_id == wallapop_user_id
            ).first()
            return buyer.is_blocked if buyer else False
            
    # Conversation CRUD Operations
    
    def create_conversation(self, wallapop_chat_id: str, product_id: int, buyer_id: int) -> Conversation:
        """Create a new conversation"""
        with self.get_session() as session:
            # Check if conversation already exists
            existing = session.query(Conversation).filter(
                and_(
                    Conversation.product_id == product_id,
                    Conversation.buyer_id == buyer_id
                )
            ).first()
            
            if existing:
                return existing
                
            conversation = Conversation(
                wallapop_chat_id=wallapop_chat_id,
                product_id=product_id,
                buyer_id=buyer_id
            )
            session.add(conversation)
            session.flush()
            session.refresh(conversation)
            
            # Update buyer conversation count
            buyer = session.query(Buyer).filter(Buyer.id == buyer_id).first()
            if buyer:
                buyer.total_conversations += 1
                
            return conversation
            
    def get_conversation(self, conversation_id: int = None, wallapop_chat_id: str = None) -> Optional[Conversation]:
        """Get conversation by ID or Wallapop chat ID"""
        with self.get_session() as session:
            query = session.query(Conversation)
            if conversation_id:
                conv = query.filter(Conversation.id == conversation_id).first()
            elif wallapop_chat_id:
                conv = query.filter(Conversation.wallapop_chat_id == wallapop_chat_id).first()
            else:
                return None
            return conv
            
    def get_active_conversations(self, limit: int = 10) -> List[Conversation]:
        """Get active conversations"""
        with self.get_session() as session:
            return session.query(Conversation).filter(
                Conversation.status == ConversationStatus.ACTIVE
            ).order_by(Conversation.updated_at.desc()).limit(limit).all()
            
    def update_conversation_status(self, conversation_id: int, status: ConversationStatus) -> bool:
        """Update conversation status"""
        with self.get_session() as session:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                conversation.status = status
                if status == ConversationStatus.COMPLETED:
                    conversation.completed_at = datetime.utcnow()
                    # Update buyer stats
                    buyer = session.query(Buyer).filter(
                        Buyer.id == conversation.buyer_id
                    ).first()
                    if buyer:
                        buyer.completed_purchases += 1
                elif status == ConversationStatus.CANCELLED:
                    # Update buyer stats
                    buyer = session.query(Buyer).filter(
                        Buyer.id == conversation.buyer_id
                    ).first()
                    if buyer:
                        buyer.cancelled_conversations += 1
                return True
            return False
            
    # Message CRUD Operations
    
    def create_message(self, conversation_id: int, content: str, message_type: MessageType,
                      buyer_id: Optional[int] = None, wallapop_message_id: Optional[str] = None,
                      **kwargs) -> Message:
        """Create a new message"""
        with self.get_session() as session:
            message = Message(
                conversation_id=conversation_id,
                content=content,
                message_type=message_type,
                buyer_id=buyer_id,
                wallapop_message_id=wallapop_message_id,
                **kwargs
            )
            session.add(message)
            session.flush()
            
            # Update conversation
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if conversation:
                conversation.last_message_at = datetime.utcnow()
                conversation.message_count += 1
                
            session.refresh(message)
            return message
            
    def get_conversation_messages(self, conversation_id: int, limit: int = 50) -> List[Message]:
        """Get messages for a conversation"""
        with self.get_session() as session:
            return session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).limit(limit).all()
            
    def mark_message_as_processed(self, message_id: int, intent: Optional[str] = None,
                                 entities: Optional[Dict] = None, sentiment: Optional[float] = None):
        """Mark message as processed with analysis results"""
        with self.get_session() as session:
            message = session.query(Message).filter(Message.id == message_id).first()
            if message:
                message.is_processed = True
                message.processed_at = datetime.utcnow()
                if intent:
                    message.intent = intent
                if entities:
                    message.entities = entities
                if sentiment is not None:
                    message.sentiment = sentiment
                    
    # Bot Session Management
    
    def get_or_create_session(self, session_id: str) -> BotSession:
        """Get or create bot session"""
        with self.get_session() as session:
            bot_session = session.query(BotSession).filter(
                BotSession.session_id == session_id
            ).first()
            
            if not bot_session:
                bot_session = BotSession(
                    session_id=session_id,
                    expires_at=datetime.utcnow() + timedelta(days=1)
                )
                session.add(bot_session)
                session.flush()
                session.refresh(bot_session)
                
            return bot_session
            
    def update_session_activity(self, session_id: str, messages_sent: int = 0,
                              active_conversations: Optional[int] = None):
        """Update bot session activity"""
        with self.get_session() as session:
            bot_session = session.query(BotSession).filter(
                BotSession.session_id == session_id
            ).first()
            
            if bot_session:
                bot_session.last_activity_at = datetime.utcnow()
                bot_session.messages_sent_today += messages_sent
                if active_conversations is not None:
                    bot_session.active_conversations_count = active_conversations
                    
    def is_rate_limited(self, session_id: str) -> bool:
        """Check if session is rate limited"""
        with self.get_session() as session:
            bot_session = session.query(BotSession).filter(
                BotSession.session_id == session_id
            ).first()
            
            if bot_session and bot_session.is_rate_limited:
                if bot_session.rate_limit_expires_at > datetime.utcnow():
                    return True
                else:
                    # Rate limit expired, remove it
                    bot_session.is_rate_limited = False
                    bot_session.rate_limit_expires_at = None
                    
            return False
            
    # Analytics and Reporting
    
    def get_daily_stats(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get daily statistics"""
        if not date:
            date = datetime.utcnow().date()
            
        with self.get_session() as session:
            # Count conversations created today
            conversations_today = session.query(func.count(Conversation.id)).filter(
                func.date(Conversation.created_at) == date
            ).scalar()
            
            # Count messages sent today
            messages_today = session.query(func.count(Message.id)).filter(
                func.date(Message.created_at) == date
            ).scalar()
            
            # Count active buyers today
            active_buyers = session.query(func.count(Buyer.id.distinct())).join(
                Conversation
            ).filter(
                func.date(Conversation.created_at) == date
            ).scalar()
            
            # Count completed sales today
            completed_sales = session.query(func.count(Conversation.id)).filter(
                and_(
                    func.date(Conversation.completed_at) == date,
                    Conversation.status == ConversationStatus.COMPLETED
                )
            ).scalar()
            
            return {
                'date': date,
                'conversations_created': conversations_today,
                'messages_sent': messages_today,
                'active_buyers': active_buyers,
                'completed_sales': completed_sales
            }
            
    def cleanup_old_sessions(self, days: int = 7):
        """Clean up old bot sessions"""
        with self.get_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted = session.query(BotSession).filter(
                BotSession.last_activity_at < cutoff_date
            ).delete()
            logger.info(f"Cleaned up {deleted} old bot sessions")