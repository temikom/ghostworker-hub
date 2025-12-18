from sqlalchemy import Column, String, Text, Enum, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
import enum
from app.db.base import Base, TimestampMixin, UUIDMixin


class Platform(str, enum.Enum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    EMAIL = "email"


class MessageStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class MessageDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Conversation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversations"
    
    platform = Column(Enum(Platform), nullable=False, index=True)
    platform_conversation_id = Column(String(255), index=True)
    subject = Column(String(500))
    is_archived = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    unread_count = Column(Integer, default=0)
    last_message_at = Column(String(50))
    
    # Foreign keys
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    
    # Full-text search
    search_vector = Column(TSVECTOR)
    
    # Relationships
    customer = relationship("Customer", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    tags = relationship("ConversationTag", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.id} ({self.platform})>"


class Message(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "messages"
    
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_message_id = Column(String(255), index=True)
    content = Column(Text, nullable=False)
    direction = Column(Enum(MessageDirection), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.PENDING)
    platform = Column(Enum(Platform), nullable=False)
    
    # Metadata
    metadata = Column(JSONB, default={})
    attachments = Column(JSONB, default=[])
    
    # AI generated
    is_ai_generated = Column(Boolean, default=False)
    ai_confidence = Column(Integer)
    
    # Sender info
    sender_id = Column(String(255))
    sender_name = Column(String(255))
    
    # Full-text search
    search_vector = Column(TSVECTOR)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.id} ({self.direction})>"


class ConversationTag(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversation_tags"
    
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="tags")
    tag = relationship("Tag", back_populates="conversations")
