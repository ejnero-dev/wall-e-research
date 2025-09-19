"""
SQLAlchemy models for Wallapop Bot with GDPR Compliance
Schema includes core functionality plus comprehensive compliance features:
- GDPR consent management and tracking
- Audit trails for all data operations
- Data retention policies and automatic cleanup
- Compliance monitoring and reporting
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Index,
    Enum,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum
from sqlalchemy.dialects.postgresql import UUID
import uuid

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


class ConsentType(enum.Enum):
    """Types of user consent for GDPR compliance"""

    DATA_PROCESSING = "data_processing"
    AUTOMATED_COMMUNICATION = "automated_communication"
    CONVERSATION_LOGGING = "conversation_logging"
    ANALYTICS_COLLECTION = "analytics_collection"
    MARKETING_COMMUNICATION = "marketing_communication"


class ConsentStatus(enum.Enum):
    """Status of user consent"""

    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"


class AuditAction(enum.Enum):
    """Types of auditable actions"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    CONSENT_GRANTED = "consent_granted"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    DATA_EXPORTED = "data_exported"
    DATA_DELETED = "data_deleted"
    FRAUD_DETECTED = "fraud_detected"
    COMPLIANCE_VIOLATION = "compliance_violation"


class DataRetentionPolicy(enum.Enum):
    """Data retention policies"""

    PERSONAL_DATA = "personal_data"  # 30 days
    CONVERSATION_DATA = "conversation_data"  # 90 days
    ANALYTICS_DATA = "analytics_data"  # 365 days
    AUDIT_DATA = "audit_data"  # 7 years
    CONSENT_RECORDS = "consent_records"  # Permanent


class Product(Base):
    """Product listing model"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    wallapop_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    status = Column(
        Enum(ProductStatus), default=ProductStatus.AVAILABLE, nullable=False
    )

    # Product details
    category = Column(String(100))
    condition = Column(String(50))  # new, like_new, good, fair
    location = Column(String(100))

    # Tracking
    views_count = Column(Integer, default=0)
    favorites_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    listed_at = Column(DateTime(timezone=True))
    sold_at = Column(DateTime(timezone=True))

    # Relationships
    conversations = relationship(
        "Conversation", back_populates="product", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_product_status_created", "status", "created_at"),
        Index("idx_product_price", "price"),
    )

    def __repr__(self):
        return f"<Product(id={self.id}, wallapop_id={self.wallapop_id}, title={self.title[:30]}...)>"


class Buyer(Base):
    """Buyer/User model with GDPR compliance features"""

    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True)
    wallapop_user_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    display_name = Column(String(100))

    # Trust metrics
    is_verified = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    trust_score = Column(Float, default=0.5)  # 0-1 scale

    # Contact info (optional, for completed sales) - GDPR sensitive
    phone = Column(String(20))
    email = Column(String(100))

    # Behavior tracking
    total_conversations = Column(Integer, default=0)
    completed_purchases = Column(Integer, default=0)
    cancelled_conversations = Column(Integer, default=0)

    # GDPR Compliance fields
    gdpr_consent_given = Column(Boolean, default=False)
    gdpr_consent_date = Column(DateTime(timezone=True))
    data_processing_consent = Column(Boolean, default=False)
    marketing_consent = Column(Boolean, default=False)
    anonymized = Column(Boolean, default=False)
    pseudonymized = Column(Boolean, default=False)
    deletion_requested = Column(Boolean, default=False)
    deletion_scheduled_at = Column(DateTime(timezone=True))
    data_export_requested = Column(Boolean, default=False)

    # Metadata
    profile_data = Column(JSON)  # Store additional profile info
    last_active_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    conversations = relationship(
        "Conversation", back_populates="buyer", cascade="all, delete-orphan"
    )
    messages = relationship(
        "Message", back_populates="buyer", cascade="all, delete-orphan"
    )
    consent_records = relationship(
        "ConsentRecord", back_populates="buyer", cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="buyer", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_buyer_active", "is_blocked", "last_active_at"),
        Index("idx_buyer_gdpr_consent", "gdpr_consent_given", "gdpr_consent_date"),
        Index("idx_buyer_deletion", "deletion_requested", "deletion_scheduled_at"),
    )

    def __repr__(self):
        return f"<Buyer(id={self.id}, username={self.username}, verified={self.is_verified}, gdpr_consent={self.gdpr_consent_given})>"


class Conversation(Base):
    """Conversation between bot and buyer about a product"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    wallapop_chat_id = Column(String(50), unique=True, nullable=False, index=True)

    # Foreign keys
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)

    # Conversation state
    status = Column(
        Enum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False
    )
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
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    product = relationship("Product", back_populates="conversations")
    buyer = relationship("Buyer", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    # Indexes
    __table_args__ = (
        Index("idx_conversation_status_updated", "status", "updated_at"),
        Index("idx_conversation_product_buyer", "product_id", "buyer_id"),
        UniqueConstraint("product_id", "buyer_id", name="uq_product_buyer"),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, product_id={self.product_id}, buyer_id={self.buyer_id}, status={self.status.value})>"


class Message(Base):
    """Individual message within a conversation"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    wallapop_message_id = Column(String(50), unique=True, index=True)

    # Foreign keys
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("buyers.id"))  # Null for bot messages

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
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    processed_at = Column(DateTime(timezone=True))

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    buyer = relationship("Buyer", back_populates="messages")

    # Indexes
    __table_args__ = (
        Index("idx_message_conversation_created", "conversation_id", "created_at"),
        Index("idx_message_type_processed", "message_type", "is_processed"),
    )

    def __repr__(self):
        return f"<Message(id={self.id}, type={self.message_type.value}, content={self.content[:50]}...)>"


# Optional: Session tracking for Redis integration
class BotSession(Base):
    """Track bot sessions for rate limiting and state management"""

    __tablename__ = "bot_sessions"

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
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<BotSession(id={self.id}, session_id={self.session_id}, active={self.active_conversations_count})>"


class ConsentRecord(Base):
    """GDPR consent tracking model"""

    __tablename__ = "consent_records"

    id = Column(Integer, primary_key=True)
    consent_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)

    # Foreign keys
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)

    # Consent details
    consent_type = Column(Enum(ConsentType), nullable=False)
    status = Column(Enum(ConsentStatus), default=ConsentStatus.PENDING, nullable=False)

    # Legal basis for processing (GDPR Article 6)
    legal_basis = Column(String(50))  # consent, contract, legal_obligation, vital_interests, public_task, legitimate_interests
    purpose = Column(Text)  # Specific purpose of data processing

    # Consent metadata
    granted_at = Column(DateTime(timezone=True))
    withdrawn_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))

    # Technical details
    ip_address = Column(String(45))  # IPv4/IPv6
    user_agent = Column(Text)
    consent_version = Column(String(20))  # Version of consent form

    # Evidence and audit
    consent_evidence = Column(JSON)  # Store evidence of consent (form data, etc.)
    withdrawal_evidence = Column(JSON)  # Store evidence of withdrawal

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    buyer = relationship("Buyer", back_populates="consent_records")

    # Indexes
    __table_args__ = (
        Index("idx_consent_buyer_type", "buyer_id", "consent_type"),
        Index("idx_consent_status_expires", "status", "expires_at"),
        Index("idx_consent_granted_withdrawn", "granted_at", "withdrawn_at"),
    )

    def __repr__(self):
        return f"<ConsentRecord(id={self.id}, buyer_id={self.buyer_id}, type={self.consent_type.value}, status={self.status.value})>"


class AuditLog(Base):
    """Comprehensive audit trail for GDPR compliance"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    audit_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)

    # What happened
    action = Column(Enum(AuditAction), nullable=False)
    entity_type = Column(String(50), nullable=False)  # table/model name
    entity_id = Column(String(50))  # ID of affected record

    # Who did it
    buyer_id = Column(Integer, ForeignKey("buyers.id"))  # Null for system actions
    user_identifier = Column(String(100))  # Username, email, or system identifier

    # When and where
    ip_address = Column(String(45))
    user_agent = Column(Text)
    session_id = Column(String(100))

    # Details
    description = Column(Text, nullable=False)
    old_values = Column(JSON)  # Previous state
    new_values = Column(JSON)  # New state
    audit_metadata = Column(JSON)  # Additional context

    # Risk assessment
    risk_level = Column(String(20))  # low, medium, high, critical
    compliance_relevant = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    buyer = relationship("Buyer", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_audit_action_entity", "action", "entity_type"),
        Index("idx_audit_buyer_created", "buyer_id", "created_at"),
        Index("idx_audit_compliance_risk", "compliance_relevant", "risk_level"),
        Index("idx_audit_created_desc", created_at.desc()),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action.value}, entity={self.entity_type}, buyer_id={self.buyer_id})>"


class DataRetentionSchedule(Base):
    """Schedule for automatic data deletion per GDPR requirements"""

    __tablename__ = "data_retention_schedules"

    id = Column(Integer, primary_key=True)
    schedule_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)

    # What to delete
    entity_type = Column(String(50), nullable=False)  # table/model name
    entity_id = Column(String(50), nullable=False)  # ID of record to delete
    policy = Column(Enum(DataRetentionPolicy), nullable=False)

    # Scheduling
    scheduled_deletion_at = Column(DateTime(timezone=True), nullable=False)
    processed = Column(Boolean, default=False)
    processing_attempted_at = Column(DateTime(timezone=True))
    processing_completed_at = Column(DateTime(timezone=True))

    # Results
    deletion_successful = Column(Boolean)
    deletion_error = Column(Text)

    # Metadata
    reason = Column(String(200))  # Reason for deletion
    legal_basis = Column(String(100))  # Legal requirement or user request
    retention_metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_retention_scheduled", "scheduled_deletion_at", "processed"),
        Index("idx_retention_entity", "entity_type", "entity_id"),
        Index("idx_retention_policy", "policy"),
    )

    def __repr__(self):
        return f"<DataRetentionSchedule(id={self.id}, entity={self.entity_type}:{self.entity_id}, scheduled={self.scheduled_deletion_at})>"


class ComplianceReport(Base):
    """Compliance monitoring and reporting"""

    __tablename__ = "compliance_reports"

    id = Column(Integer, primary_key=True)
    report_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)

    # Report details
    report_type = Column(String(50), nullable=False)  # daily, weekly, monthly, incident
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Metrics
    total_users = Column(Integer, default=0)
    consents_granted = Column(Integer, default=0)
    consents_withdrawn = Column(Integer, default=0)
    data_exports_requested = Column(Integer, default=0)
    data_deletions_requested = Column(Integer, default=0)
    data_breaches_detected = Column(Integer, default=0)
    compliance_violations = Column(Integer, default=0)

    # Detailed data
    report_data = Column(JSON)  # Detailed metrics and analysis
    issues_identified = Column(JSON)  # List of compliance issues
    recommendations = Column(JSON)  # Recommended actions

    # Status
    generated_by = Column(String(100))  # System or user who generated
    reviewed_by = Column(String(100))  # Who reviewed the report
    status = Column(String(20), default="draft")  # draft, final, archived

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime(timezone=True))

    # Indexes
    __table_args__ = (
        Index("idx_compliance_report_period", "period_start", "period_end"),
        Index("idx_compliance_report_type", "report_type", "status"),
    )

    def __repr__(self):
        return f"<ComplianceReport(id={self.id}, type={self.report_type}, period={self.period_start} to {self.period_end})>"
