"""Product and Commerce models"""
from sqlalchemy import Column, String, Boolean, Text, DECIMAL, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base, TimestampMixin, UUIDMixin


class Product(Base, UUIDMixin, TimestampMixin):
    """Product catalog"""
    __tablename__ = "products"
    
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    sku = Column(String(100))
    images = Column(ARRAY(Text), default=[])
    category = Column(String(100))
    stock_quantity = Column(Integer)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSONB, default={})
    
    team = relationship("Team", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")


class OrderItem(Base, UUIDMixin):
    """Order line items"""
    __tablename__ = "order_items"
    
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"))
    name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(12, 2), nullable=False)
    total = Column(DECIMAL(12, 2), nullable=False)
    metadata = Column(JSONB, default={})
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
