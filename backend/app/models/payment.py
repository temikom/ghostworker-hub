"""Payment models"""
from sqlalchemy import Column, String, Boolean, Text, DECIMAL, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum

from app.db.base import Base, TimestampMixin, UUIDMixin


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentConfig(Base, UUIDMixin, TimestampMixin):
    """Payment provider configuration per team"""
    __tablename__ = "payment_configs"
    
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), unique=True, nullable=False)
    provider = Column(String(50), default="stripe")
    is_configured = Column(Boolean, default=False)
    public_key = Column(Text)
    secret_key_encrypted = Column(Text)
    webhook_secret_encrypted = Column(Text)
    webhook_url = Column(Text)
    metadata = Column(JSONB, default={})
    
    team = relationship("Team", back_populates="payment_config")


class Payment(Base, UUIDMixin, TimestampMixin):
    """Payment records"""
    __tablename__ = "payments"
    
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"))
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="SET NULL"))
    provider = Column(String(50), nullable=False)
    provider_payment_id = Column(String(255))
    amount = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String(50))
    metadata = Column(JSONB, default={})
    
    team = relationship("Team", back_populates="payments")
    order = relationship("Order", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")
