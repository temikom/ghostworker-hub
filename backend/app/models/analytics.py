from sqlalchemy import Column, String, Integer, Numeric, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base, TimestampMixin, UUIDMixin


class AnalyticsSnapshot(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analytics_snapshots"
    
    date = Column(Date, nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    
    # Message metrics
    total_messages = Column(Integer, default=0)
    inbound_messages = Column(Integer, default=0)
    outbound_messages = Column(Integer, default=0)
    
    # Per platform
    whatsapp_messages = Column(Integer, default=0)
    instagram_messages = Column(Integer, default=0)
    tiktok_messages = Column(Integer, default=0)
    email_messages = Column(Integer, default=0)
    
    # Response metrics
    avg_response_time_seconds = Column(Integer)
    avg_first_response_time_seconds = Column(Integer)
    
    # Conversation metrics
    new_conversations = Column(Integer, default=0)
    resolved_conversations = Column(Integer, default=0)
    
    # Order metrics
    total_orders = Column(Integer, default=0)
    order_revenue = Column(Numeric(12, 2), default=0)
    
    # Customer metrics
    new_customers = Column(Integer, default=0)
    active_customers = Column(Integer, default=0)
    
    # AI metrics
    ai_replies_generated = Column(Integer, default=0)
    ai_replies_used = Column(Integer, default=0)
    
    # Template usage
    template_usage = Column(JSONB, default={})
    
    def __repr__(self):
        return f"<AnalyticsSnapshot {self.date}>"


class Activity(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "activities"
    
    action = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    
    # Actor
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Target entity
    entity_type = Column(String(50), index=True)  # conversation, order, customer, etc.
    entity_id = Column(UUID(as_uuid=True), index=True)
    
    # Related customer
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    
    # Additional data
    metadata = Column(JSONB, default={})
    
    # Team scope
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    customer = relationship("Customer", back_populates="activities")
    
    def __repr__(self):
        return f"<Activity {self.action}>"


# Import relationship for User model
from sqlalchemy.orm import relationship
