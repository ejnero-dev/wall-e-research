"""
Database Manager for Wallapop Bot with GDPR Compliance
Handles database connections, CRUD operations, and compliance features:
- GDPR consent management
- Audit logging for all operations
- Data retention and automatic cleanup
- Compliance reporting and monitoring
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
    Base,
    Product,
    Buyer,
    Conversation,
    Message,
    BotSession,
    ConsentRecord,
    AuditLog,
    DataRetentionSchedule,
    ComplianceReport,
    ProductStatus,
    ConversationStatus,
    MessageType,
    ConsentType,
    ConsentStatus,
    AuditAction,
    DataRetentionPolicy,
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
            pool_recycle=3600,  # Recycle connections after 1 hour
        )

        # Create session factory
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
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

    def get_product(
        self, product_id: int = None, wallapop_id: str = None
    ) -> Optional[Product]:
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
            return (
                session.query(Product)
                .filter(Product.status == ProductStatus.AVAILABLE)
                .order_by(Product.created_at.desc())
                .limit(limit)
                .all()
            )

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
            buyer = (
                session.query(Buyer)
                .filter(Buyer.wallapop_user_id == wallapop_user_id)
                .first()
            )

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

    def get_buyer(
        self, buyer_id: int = None, wallapop_user_id: str = None
    ) -> Optional[Buyer]:
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
            buyer = (
                session.query(Buyer)
                .filter(Buyer.wallapop_user_id == wallapop_user_id)
                .first()
            )
            return buyer.is_blocked if buyer else False

    # Conversation CRUD Operations

    def create_conversation(
        self, wallapop_chat_id: str, product_id: int, buyer_id: int
    ) -> Conversation:
        """Create a new conversation"""
        with self.get_session() as session:
            # Check if conversation already exists
            existing = (
                session.query(Conversation)
                .filter(
                    and_(
                        Conversation.product_id == product_id,
                        Conversation.buyer_id == buyer_id,
                    )
                )
                .first()
            )

            if existing:
                return existing

            conversation = Conversation(
                wallapop_chat_id=wallapop_chat_id,
                product_id=product_id,
                buyer_id=buyer_id,
            )
            session.add(conversation)
            session.flush()
            session.refresh(conversation)

            # Update buyer conversation count
            buyer = session.query(Buyer).filter(Buyer.id == buyer_id).first()
            if buyer:
                buyer.total_conversations += 1

            return conversation

    def get_conversation(
        self, conversation_id: int = None, wallapop_chat_id: str = None
    ) -> Optional[Conversation]:
        """Get conversation by ID or Wallapop chat ID"""
        with self.get_session() as session:
            query = session.query(Conversation)
            if conversation_id:
                conv = query.filter(Conversation.id == conversation_id).first()
            elif wallapop_chat_id:
                conv = query.filter(
                    Conversation.wallapop_chat_id == wallapop_chat_id
                ).first()
            else:
                return None
            return conv

    def get_active_conversations(self, limit: int = 10) -> List[Conversation]:
        """Get active conversations"""
        with self.get_session() as session:
            return (
                session.query(Conversation)
                .filter(Conversation.status == ConversationStatus.ACTIVE)
                .order_by(Conversation.updated_at.desc())
                .limit(limit)
                .all()
            )

    def update_conversation_status(
        self, conversation_id: int, status: ConversationStatus
    ) -> bool:
        """Update conversation status"""
        with self.get_session() as session:
            conversation = (
                session.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )

            if conversation:
                conversation.status = status
                if status == ConversationStatus.COMPLETED:
                    conversation.completed_at = datetime.utcnow()
                    # Update buyer stats
                    buyer = (
                        session.query(Buyer)
                        .filter(Buyer.id == conversation.buyer_id)
                        .first()
                    )
                    if buyer:
                        buyer.completed_purchases += 1
                elif status == ConversationStatus.CANCELLED:
                    # Update buyer stats
                    buyer = (
                        session.query(Buyer)
                        .filter(Buyer.id == conversation.buyer_id)
                        .first()
                    )
                    if buyer:
                        buyer.cancelled_conversations += 1
                return True
            return False

    # Message CRUD Operations

    def create_message(
        self,
        conversation_id: int,
        content: str,
        message_type: MessageType,
        buyer_id: Optional[int] = None,
        wallapop_message_id: Optional[str] = None,
        **kwargs,
    ) -> Message:
        """Create a new message"""
        with self.get_session() as session:
            message = Message(
                conversation_id=conversation_id,
                content=content,
                message_type=message_type,
                buyer_id=buyer_id,
                wallapop_message_id=wallapop_message_id,
                **kwargs,
            )
            session.add(message)
            session.flush()

            # Update conversation
            conversation = (
                session.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )
            if conversation:
                conversation.last_message_at = datetime.utcnow()
                conversation.message_count += 1

            session.refresh(message)
            return message

    def get_conversation_messages(
        self, conversation_id: int, limit: int = 50
    ) -> List[Message]:
        """Get messages for a conversation"""
        with self.get_session() as session:
            return (
                session.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
                .all()
            )

    def mark_message_as_processed(
        self,
        message_id: int,
        intent: Optional[str] = None,
        entities: Optional[Dict] = None,
        sentiment: Optional[float] = None,
    ):
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
            bot_session = (
                session.query(BotSession)
                .filter(BotSession.session_id == session_id)
                .first()
            )

            if not bot_session:
                bot_session = BotSession(
                    session_id=session_id,
                    expires_at=datetime.utcnow() + timedelta(days=1),
                )
                session.add(bot_session)
                session.flush()
                session.refresh(bot_session)

            return bot_session

    def update_session_activity(
        self,
        session_id: str,
        messages_sent: int = 0,
        active_conversations: Optional[int] = None,
    ):
        """Update bot session activity"""
        with self.get_session() as session:
            bot_session = (
                session.query(BotSession)
                .filter(BotSession.session_id == session_id)
                .first()
            )

            if bot_session:
                bot_session.last_activity_at = datetime.utcnow()
                bot_session.messages_sent_today += messages_sent
                if active_conversations is not None:
                    bot_session.active_conversations_count = active_conversations

    def is_rate_limited(self, session_id: str) -> bool:
        """Check if session is rate limited"""
        with self.get_session() as session:
            bot_session = (
                session.query(BotSession)
                .filter(BotSession.session_id == session_id)
                .first()
            )

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
            conversations_today = (
                session.query(func.count(Conversation.id))
                .filter(func.date(Conversation.created_at) == date)
                .scalar()
            )

            # Count messages sent today
            messages_today = (
                session.query(func.count(Message.id))
                .filter(func.date(Message.created_at) == date)
                .scalar()
            )

            # Count active buyers today
            active_buyers = (
                session.query(func.count(Buyer.id.distinct()))
                .join(Conversation)
                .filter(func.date(Conversation.created_at) == date)
                .scalar()
            )

            # Count completed sales today
            completed_sales = (
                session.query(func.count(Conversation.id))
                .filter(
                    and_(
                        func.date(Conversation.completed_at) == date,
                        Conversation.status == ConversationStatus.COMPLETED,
                    )
                )
                .scalar()
            )

            return {
                "date": date,
                "conversations_created": conversations_today,
                "messages_sent": messages_today,
                "active_buyers": active_buyers,
                "completed_sales": completed_sales,
            }

    def cleanup_old_sessions(self, days: int = 7):
        """Clean up old bot sessions"""
        with self.get_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted = (
                session.query(BotSession)
                .filter(BotSession.last_activity_at < cutoff_date)
                .delete()
            )
            logger.info(f"Cleaned up {deleted} old bot sessions")

    # GDPR Compliance Methods

    def create_audit_log(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: str = None,
        buyer_id: int = None,
        user_identifier: str = None,
        description: str = "",
        old_values: Dict = None,
        new_values: Dict = None,
        ip_address: str = None,
        user_agent: str = None,
        session_id: str = None,
        risk_level: str = "low",
        compliance_relevant: bool = True,
        **kwargs,
    ) -> AuditLog:
        """Create an audit log entry for compliance tracking"""
        with self.get_session() as session:
            audit_log = AuditLog(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                buyer_id=buyer_id,
                user_identifier=user_identifier,
                description=description,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                risk_level=risk_level,
                compliance_relevant=compliance_relevant,
                audit_metadata=kwargs,
            )
            session.add(audit_log)
            session.flush()
            session.refresh(audit_log)
            return audit_log

    def create_consent_record(
        self,
        buyer_id: int,
        consent_type: ConsentType,
        status: ConsentStatus = ConsentStatus.PENDING,
        legal_basis: str = "consent",
        purpose: str = "",
        ip_address: str = None,
        user_agent: str = None,
        consent_version: str = "1.0",
        **kwargs,
    ) -> ConsentRecord:
        """Create a consent record for GDPR compliance"""
        with self.get_session() as session:
            consent = ConsentRecord(
                buyer_id=buyer_id,
                consent_type=consent_type,
                status=status,
                legal_basis=legal_basis,
                purpose=purpose,
                ip_address=ip_address,
                user_agent=user_agent,
                consent_version=consent_version,
                consent_evidence=kwargs,
            )
            session.add(consent)
            session.flush()
            session.refresh(consent)

            # Create audit log for consent creation
            self.create_audit_log(
                action=(
                    AuditAction.CONSENT_GRANTED
                    if status == ConsentStatus.GRANTED
                    else AuditAction.CREATE
                ),
                entity_type="consent_records",
                entity_id=str(consent.id),
                buyer_id=buyer_id,
                description=f"Consent record created for {consent_type.value}",
                new_values={"consent_type": consent_type.value, "status": status.value},
                ip_address=ip_address,
                user_agent=user_agent,
                compliance_relevant=True,
            )

            return consent

    def grant_consent(
        self,
        buyer_id: int,
        consent_type: ConsentType,
        purpose: str = "",
        ip_address: str = None,
        user_agent: str = None,
        consent_version: str = "1.0",
        evidence: Dict = None,
    ) -> ConsentRecord:
        """Grant consent for a specific purpose"""
        with self.get_session() as session:
            # Check if consent already exists
            existing_consent = (
                session.query(ConsentRecord)
                .filter(
                    and_(
                        ConsentRecord.buyer_id == buyer_id,
                        ConsentRecord.consent_type == consent_type,
                    )
                )
                .first()
            )

            if existing_consent:
                # Update existing consent
                existing_consent.status = ConsentStatus.GRANTED
                existing_consent.granted_at = datetime.utcnow()
                existing_consent.purpose = purpose
                existing_consent.consent_evidence = evidence or {}
                consent = existing_consent
            else:
                # Create new consent
                consent = ConsentRecord(
                    buyer_id=buyer_id,
                    consent_type=consent_type,
                    status=ConsentStatus.GRANTED,
                    granted_at=datetime.utcnow(),
                    legal_basis="consent",
                    purpose=purpose,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    consent_version=consent_version,
                    consent_evidence=evidence or {},
                )
                session.add(consent)

            session.flush()

            # Update buyer GDPR fields
            buyer = session.query(Buyer).filter(Buyer.id == buyer_id).first()
            if buyer:
                buyer.gdpr_consent_given = True
                buyer.gdpr_consent_date = datetime.utcnow()
                if consent_type == ConsentType.DATA_PROCESSING:
                    buyer.data_processing_consent = True
                elif consent_type == ConsentType.MARKETING_COMMUNICATION:
                    buyer.marketing_consent = True

            # Create audit log
            self.create_audit_log(
                action=AuditAction.CONSENT_GRANTED,
                entity_type="consent_records",
                entity_id=str(consent.id),
                buyer_id=buyer_id,
                description=f"Consent granted for {consent_type.value}",
                new_values={"status": "granted", "purpose": purpose},
                ip_address=ip_address,
                user_agent=user_agent,
                compliance_relevant=True,
            )

            session.refresh(consent)
            return consent

    def withdraw_consent(
        self,
        buyer_id: int,
        consent_type: ConsentType,
        reason: str = "",
        ip_address: str = None,
        user_agent: str = None,
        evidence: Dict = None,
    ) -> bool:
        """Withdraw consent and schedule data deletion if required"""
        with self.get_session() as session:
            consent = (
                session.query(ConsentRecord)
                .filter(
                    and_(
                        ConsentRecord.buyer_id == buyer_id,
                        ConsentRecord.consent_type == consent_type,
                        ConsentRecord.status == ConsentStatus.GRANTED,
                    )
                )
                .first()
            )

            if not consent:
                return False

            # Update consent record
            consent.status = ConsentStatus.WITHDRAWN
            consent.withdrawn_at = datetime.utcnow()
            consent.withdrawal_evidence = evidence or {"reason": reason}

            # Update buyer GDPR fields
            buyer = session.query(Buyer).filter(Buyer.id == buyer_id).first()
            if buyer:
                if consent_type == ConsentType.DATA_PROCESSING:
                    buyer.data_processing_consent = False
                    buyer.deletion_requested = True
                elif consent_type == ConsentType.MARKETING_COMMUNICATION:
                    buyer.marketing_consent = False

            # Schedule data deletion based on consent type
            if consent_type == ConsentType.DATA_PROCESSING:
                self.schedule_data_deletion(
                    entity_type="buyers",
                    entity_id=str(buyer_id),
                    policy=DataRetentionPolicy.PERSONAL_DATA,
                    reason="Consent withdrawn for data processing",
                    legal_basis="GDPR Article 17 - Right to be forgotten",
                )

            # Create audit log
            self.create_audit_log(
                action=AuditAction.CONSENT_WITHDRAWN,
                entity_type="consent_records",
                entity_id=str(consent.id),
                buyer_id=buyer_id,
                description=f"Consent withdrawn for {consent_type.value}",
                old_values={"status": "granted"},
                new_values={"status": "withdrawn", "reason": reason},
                ip_address=ip_address,
                user_agent=user_agent,
                compliance_relevant=True,
            )

            return True

    def get_buyer_consents(self, buyer_id: int) -> List[ConsentRecord]:
        """Get all consent records for a buyer"""
        with self.get_session() as session:
            return (
                session.query(ConsentRecord)
                .filter(ConsentRecord.buyer_id == buyer_id)
                .order_by(ConsentRecord.created_at.desc())
                .all()
            )

    def check_consent(self, buyer_id: int, consent_type: ConsentType) -> bool:
        """Check if buyer has granted specific consent"""
        with self.get_session() as session:
            consent = (
                session.query(ConsentRecord)
                .filter(
                    and_(
                        ConsentRecord.buyer_id == buyer_id,
                        ConsentRecord.consent_type == consent_type,
                        ConsentRecord.status == ConsentStatus.GRANTED,
                    )
                )
                .first()
            )
            return consent is not None

    def schedule_data_deletion(
        self,
        entity_type: str,
        entity_id: str,
        policy: DataRetentionPolicy,
        reason: str = "",
        legal_basis: str = "",
        deletion_date: datetime = None,
    ) -> DataRetentionSchedule:
        """Schedule data for deletion based on retention policy"""
        with self.get_session() as session:
            if not deletion_date:
                # Calculate deletion date based on policy
                now = datetime.utcnow()
                if policy == DataRetentionPolicy.PERSONAL_DATA:
                    deletion_date = now + timedelta(days=30)
                elif policy == DataRetentionPolicy.CONVERSATION_DATA:
                    deletion_date = now + timedelta(days=90)
                elif policy == DataRetentionPolicy.ANALYTICS_DATA:
                    deletion_date = now + timedelta(days=365)
                elif policy == DataRetentionPolicy.AUDIT_DATA:
                    deletion_date = now + timedelta(days=7 * 365)  # 7 years
                else:
                    deletion_date = now + timedelta(days=30)  # Default

            schedule = DataRetentionSchedule(
                entity_type=entity_type,
                entity_id=entity_id,
                policy=policy,
                scheduled_deletion_at=deletion_date,
                reason=reason,
                legal_basis=legal_basis,
            )
            session.add(schedule)
            session.flush()
            session.refresh(schedule)

            # Create audit log
            self.create_audit_log(
                action=AuditAction.CREATE,
                entity_type="data_retention_schedules",
                entity_id=str(schedule.id),
                description=f"Data deletion scheduled for {entity_type}:{entity_id}",
                new_values={
                    "scheduled_for": deletion_date.isoformat(),
                    "policy": policy.value,
                },
                compliance_relevant=True,
            )

            return schedule

    def process_data_deletions(self) -> int:
        """Process scheduled data deletions that are due"""
        with self.get_session() as session:
            now = datetime.utcnow()
            due_deletions = (
                session.query(DataRetentionSchedule)
                .filter(
                    and_(
                        DataRetentionSchedule.scheduled_deletion_at <= now,
                        DataRetentionSchedule.processed.is_(False),
                    )
                )
                .all()
            )

            processed_count = 0
            for deletion in due_deletions:
                try:
                    deletion.processing_attempted_at = now

                    # Perform actual deletion based on entity type
                    if deletion.entity_type == "buyers":
                        buyer = (
                            session.query(Buyer)
                            .filter(Buyer.id == deletion.entity_id)
                            .first()
                        )
                        if buyer:
                            # Anonymize instead of delete to preserve referential integrity
                            buyer.anonymized = True
                            buyer.email = None
                            buyer.phone = None
                            buyer.username = f"anonymous_{buyer.id}"
                            buyer.display_name = "Anonymous User"
                            buyer.profile_data = {}

                    deletion.processed = True
                    deletion.processing_completed_at = now
                    deletion.deletion_successful = True
                    processed_count += 1

                    # Create audit log
                    self.create_audit_log(
                        action=AuditAction.DATA_DELETED,
                        entity_type=deletion.entity_type,
                        entity_id=deletion.entity_id,
                        description="Data deleted/anonymized according to retention policy",
                        audit_metadata={"policy": deletion.policy.value},
                        compliance_relevant=True,
                    )

                except Exception as e:
                    deletion.deletion_successful = False
                    deletion.deletion_error = str(e)
                    logger.error(f"Failed to process deletion {deletion.id}: {e}")

            return processed_count

    def export_user_data(self, buyer_id: int) -> Dict[str, Any]:
        """Export all user data for GDPR data portability"""
        with self.get_session() as session:
            buyer = session.query(Buyer).filter(Buyer.id == buyer_id).first()
            if not buyer:
                return {}

            # Get related data
            conversations = (
                session.query(Conversation)
                .filter(Conversation.buyer_id == buyer_id)
                .all()
            )

            messages = session.query(Message).filter(Message.buyer_id == buyer_id).all()

            consents = (
                session.query(ConsentRecord)
                .filter(ConsentRecord.buyer_id == buyer_id)
                .all()
            )

            # Create audit log
            self.create_audit_log(
                action=AuditAction.DATA_EXPORTED,
                entity_type="buyers",
                entity_id=str(buyer_id),
                buyer_id=buyer_id,
                description="User data exported for GDPR compliance",
                compliance_relevant=True,
            )

            # Mark export as requested
            buyer.data_export_requested = True

            return {
                "export_date": datetime.utcnow().isoformat(),
                "buyer": {
                    "id": buyer.id,
                    "username": buyer.username,
                    "display_name": buyer.display_name,
                    "email": buyer.email,
                    "phone": buyer.phone,
                    "created_at": (
                        buyer.created_at.isoformat() if buyer.created_at else None
                    ),
                    "profile_data": buyer.profile_data,
                },
                "conversations": [
                    {
                        "id": conv.id,
                        "product_id": conv.product_id,
                        "status": conv.status.value,
                        "created_at": (
                            conv.created_at.isoformat() if conv.created_at else None
                        ),
                        "negotiated_price": conv.negotiated_price,
                        "meeting_location": conv.meeting_location,
                    }
                    for conv in conversations
                ],
                "messages": [
                    {
                        "id": msg.id,
                        "conversation_id": msg.conversation_id,
                        "content": msg.content,
                        "message_type": msg.message_type.value,
                        "created_at": (
                            msg.created_at.isoformat() if msg.created_at else None
                        ),
                    }
                    for msg in messages
                ],
                "consents": [
                    {
                        "consent_type": consent.consent_type.value,
                        "status": consent.status.value,
                        "granted_at": (
                            consent.granted_at.isoformat()
                            if consent.granted_at
                            else None
                        ),
                        "withdrawn_at": (
                            consent.withdrawn_at.isoformat()
                            if consent.withdrawn_at
                            else None
                        ),
                        "purpose": consent.purpose,
                    }
                    for consent in consents
                ],
            }

    def generate_compliance_report(
        self,
        report_type: str = "daily",
        period_start: datetime = None,
        period_end: datetime = None,
    ) -> ComplianceReport:
        """Generate compliance report for monitoring"""
        with self.get_session() as session:
            if not period_start:
                period_start = datetime.utcnow().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            if not period_end:
                period_end = period_start + timedelta(days=1)

            # Gather metrics
            total_users = session.query(func.count(Buyer.id)).scalar()

            consents_granted = (
                session.query(func.count(ConsentRecord.id))
                .filter(
                    and_(
                        ConsentRecord.granted_at.between(period_start, period_end),
                        ConsentRecord.status == ConsentStatus.GRANTED,
                    )
                )
                .scalar()
            )

            consents_withdrawn = (
                session.query(func.count(ConsentRecord.id))
                .filter(
                    and_(
                        ConsentRecord.withdrawn_at.between(period_start, period_end),
                        ConsentRecord.status == ConsentStatus.WITHDRAWN,
                    )
                )
                .scalar()
            )

            data_exports_requested = (
                session.query(func.count(Buyer.id))
                .filter(
                    and_(
                        Buyer.data_export_requested.is_(True),
                        Buyer.updated_at.between(period_start, period_end),
                    )
                )
                .scalar()
            )

            data_deletions_requested = (
                session.query(func.count(Buyer.id))
                .filter(
                    and_(
                        Buyer.deletion_requested.is_(True),
                        Buyer.updated_at.between(period_start, period_end),
                    )
                )
                .scalar()
            )

            compliance_violations = (
                session.query(func.count(AuditLog.id))
                .filter(
                    and_(
                        AuditLog.action == AuditAction.COMPLIANCE_VIOLATION,
                        AuditLog.created_at.between(period_start, period_end),
                    )
                )
                .scalar()
            )

            report = ComplianceReport(
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                total_users=total_users,
                consents_granted=consents_granted,
                consents_withdrawn=consents_withdrawn,
                data_exports_requested=data_exports_requested,
                data_deletions_requested=data_deletions_requested,
                compliance_violations=compliance_violations,
                generated_by="system",
            )

            session.add(report)
            session.flush()
            session.refresh(report)

            return report
