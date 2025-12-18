from sqlalchemy import Column, String, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum
from app.db.base import Base, TimestampMixin, UUIDMixin


class IntegrationStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class Integration(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "integrations"
    
    platform = Column(String(50), nullable=False, index=True)
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.DISCONNECTED)
    
    # Credentials (encrypted in production)
    credentials = Column(JSONB, default={})
    
    # Webhook info
    webhook_url = Column(String(500))
    webhook_secret = Column(String(255))
    
    # Metadata
    metadata = Column(JSONB, default={})
    last_sync_at = Column(String(50))
    error_message = Column(Text)
    
    # Team scope
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    
    # Relationships
    team = relationship("Team", back_populates="integrations")
    
    def __repr__(self):
        return f"<Integration {self.platform}>"


class WebhookEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "webhook_events"
    
    platform = Column(String(50), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSONB, nullable=False)
    
    # Processing status
    processed = Column(Boolean, default=False)
    processed_at = Column(String(50))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Reference
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=True)
    
    def __repr__(self):
        return f"<WebhookEvent {self.platform}/{self.event_type}>"


from sqlalchemy import Boolean, Integer
