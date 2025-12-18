from sqlalchemy import Column, String, Boolean, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.db.base import Base, TimestampMixin, UUIDMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(500))
    phone = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Team relationship
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    team = relationship("Team", back_populates="members")
    
    # Role relationship
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    
    # Other relationships
    templates = relationship("Template", back_populates="owner")
    assigned_customers = relationship("Customer", back_populates="assigned_owner")
    activities = relationship("Activity", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"


class UserRoleAssignment(Base, UUIDMixin, TimestampMixin):
    """User role assignments table - separate from users for security"""
    __tablename__ = "user_roles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.MEMBER)
    
    user = relationship("User", back_populates="roles")
    
    __table_args__ = (
        {"schema": "public"},
    )


class Team(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "teams"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    logo_url = Column(String(500))
    
    # Relationships
    members = relationship("User", back_populates="team")
    integrations = relationship("Integration", back_populates="team")
    
    def __repr__(self):
        return f"<Team {self.name}>"
