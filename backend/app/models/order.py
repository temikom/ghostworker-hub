from sqlalchemy import Column, String, Numeric, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum
from app.db.base import Base, TimestampMixin, UUIDMixin


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "orders"
    
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    # Pricing
    subtotal = Column(Numeric(12, 2), default=0)
    tax = Column(Numeric(12, 2), default=0)
    shipping = Column(Numeric(12, 2), default=0)
    discount = Column(Numeric(12, 2), default=0)
    total = Column(Numeric(12, 2), default=0, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Items (JSON array)
    items = Column(JSONB, default=[])
    
    # Shipping info
    shipping_address = Column(JSONB, default={})
    billing_address = Column(JSONB, default={})
    
    # Notes
    notes = Column(Text)
    internal_notes = Column(Text)
    
    # Foreign keys
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    
    # Metadata
    metadata = Column(JSONB, default={})
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    timeline = relationship("OrderTimeline", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.order_number}>"


class OrderTimeline(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "order_timeline"
    
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)
    description = Column(Text)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    metadata = Column(JSONB, default={})
    
    # Relationships
    order = relationship("Order", back_populates="timeline")
