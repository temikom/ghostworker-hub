"""Invoice models"""
from sqlalchemy import Column, String, Boolean, Text, DECIMAL, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import enum

from app.db.base import Base, TimestampMixin, UUIDMixin


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(Base, UUIDMixin, TimestampMixin):
    """Invoices"""
    __tablename__ = "invoices"
    
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"))
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    subtotal = Column(DECIMAL(12, 2), nullable=False)
    tax = Column(DECIMAL(12, 2), default=0)
    total = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    due_date = Column(Date)
    paid_at = Column(Date)
    pdf_url = Column(Text)
    notes = Column(Text)
    metadata = Column(JSONB, default={})
    
    team = relationship("Team", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    order = relationship("Order", back_populates="invoice")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base, UUIDMixin):
    """Invoice line items"""
    __tablename__ = "invoice_items"
    
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit_price = Column(DECIMAL(12, 2), nullable=False)
    total = Column(DECIMAL(12, 2), nullable=False)
    
    invoice = relationship("Invoice", back_populates="items")
