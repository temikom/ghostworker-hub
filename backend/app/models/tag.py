from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin, UUIDMixin


class Tag(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tags"
    
    name = Column(String(100), nullable=False)
    color = Column(String(7), default="#6366f1")  # Hex color
    description = Column(Text)
    
    # Team scope
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    
    # Relationships
    conversations = relationship("ConversationTag", back_populates="tag", cascade="all, delete-orphan")
    customers = relationship("CustomerTag", back_populates="tag", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tag {self.name}>"


class Template(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "templates"
    
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    shortcut = Column(String(50), index=True)  # e.g., "/greeting"
    category = Column(String(100))
    is_global = Column(Boolean, default=False)
    
    # Owner (null = global template)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    
    # Relationships
    owner = relationship("User", back_populates="templates")
    
    def __repr__(self):
        return f"<Template {self.name}>"


from sqlalchemy import Integer
