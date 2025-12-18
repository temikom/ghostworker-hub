"""Notification models"""
from sqlalchemy import Column, String, Boolean, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum

from app.db.base import Base, TimestampMixin, UUIDMixin


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"


class NotificationSettings(Base, UUIDMixin, TimestampMixin):
    """Team notification settings"""
    __tablename__ = "notification_settings"
    
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), unique=True, nullable=False)
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    triggers = Column(JSONB, default={})  # {order_created: true, payment_received: true, ...}
    
    team = relationship("Team", back_populates="notification_settings")


class OrderNotification(Base, UUIDMixin, TimestampMixin):
    """Order notification records"""
    __tablename__ = "order_notifications"
    
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # order_created, payment_received, shipped, delivered
    channel = Column(Enum(NotificationChannel), nullable=False)
    status = Column(String(20), default="pending")
    sent_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    order = relationship("Order", back_populates="notifications")
