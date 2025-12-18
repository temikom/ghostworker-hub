from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from app.db.base import Base, TimestampMixin, UUIDMixin


class Customer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "customers"
    
    name = Column(String(255), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(50), index=True)
    avatar_url = Column(String(500))
    
    # Social IDs
    whatsapp_id = Column(String(255), index=True)
    instagram_id = Column(String(255), index=True)
    tiktok_id = Column(String(255), index=True)
    
    # Additional info
    company = Column(String(255))
    notes = Column(Text)
    metadata = Column(JSONB, default={})
    
    # Team assignment
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    assigned_owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Full-text search
    search_vector = Column(TSVECTOR)
    
    # Relationships
    assigned_owner = relationship("User", back_populates="assigned_customers")
    conversations = relationship("Conversation", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    activities = relationship("Activity", back_populates="customer")
    tags = relationship("CustomerTag", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer {self.name}>"


class CustomerTag(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "customer_tags"
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="tags")
    tag = relationship("Tag", back_populates="customers")
