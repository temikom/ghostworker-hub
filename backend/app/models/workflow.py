"""Workflow and Automation models"""
from sqlalchemy import Column, String, Boolean, Text, Integer, ForeignKey, Enum, ARRAY, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.conversation import Platform


class WorkflowTriggerType(str, enum.Enum):
    MESSAGE_RECEIVED = "message_received"
    ORDER_CREATED = "order_created"
    TAG_ADDED = "tag_added"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"


class ScheduledMessageStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    CANCELLED = "cancelled"


class Workflow(Base, UUIDMixin, TimestampMixin):
    """Automation workflows"""
    __tablename__ = "workflows"
    
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trigger = Column(JSONB, nullable=False)
    nodes = Column(JSONB, default=[])
    connections = Column(JSONB, default=[])
    is_active = Column(Boolean, default=False)
    last_run = Column(DateTime(timezone=True))
    run_count = Column(Integer, default=0)
    
    team = relationship("Team", back_populates="workflows")
    runs = relationship("WorkflowRun", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowRun(Base, UUIDMixin):
    """Workflow execution records"""
    __tablename__ = "workflow_runs"
    
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="pending")
    trigger_data = Column(JSONB)
    execution_log = Column(JSONB, default=[])
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    workflow = relationship("Workflow", back_populates="runs")


class ChatbotFlow(Base, UUIDMixin, TimestampMixin):
    """Chatbot conversation flows"""
    __tablename__ = "chatbot_flows"
    
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    nodes = Column(JSONB, default=[])
    connections = Column(JSONB, default=[])
    platforms = Column(ARRAY(String), default=[])
    is_active = Column(Boolean, default=False)
    conversation_count = Column(Integer, default=0)
    
    team = relationship("Team", back_populates="chatbot_flows")


class ScheduledMessage(Base, UUIDMixin, TimestampMixin):
    """Scheduled broadcast messages"""
    __tablename__ = "scheduled_messages"
    
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    recipients = Column(JSONB, nullable=False)
    schedule = Column(JSONB, nullable=False)
    platforms = Column(ARRAY(String), default=[])
    status = Column(Enum(ScheduledMessageStatus), default=ScheduledMessageStatus.DRAFT)
    sent_count = Column(Integer, default=0)
    last_sent = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    team = relationship("Team", back_populates="scheduled_messages")
    creator = relationship("User", back_populates="scheduled_messages")


class AutoResponder(Base, UUIDMixin, TimestampMixin):
    """Automatic response rules"""
    __tablename__ = "auto_responders"
    
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    trigger_type = Column(String(50), nullable=False)  # keyword, first_message, no_agent, outside_hours
    trigger_config = Column(JSONB, default={})
    response_type = Column(String(50), nullable=False)  # text, template, ai_generated
    response_config = Column(JSONB, nullable=False)
    platforms = Column(ARRAY(String), default=[])
    is_active = Column(Boolean, default=False)
    triggered_count = Column(Integer, default=0)
    
    team = relationship("Team", back_populates="auto_responders")
