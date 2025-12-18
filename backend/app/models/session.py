"""User session and device tracking models"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.db.base import Base, TimestampMixin, UUIDMixin


class UserSession(Base, UUIDMixin, TimestampMixin):
    """Track user sessions and devices"""
    __tablename__ = "user_sessions"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Device info
    device_name = Column(String(255))
    device_type = Column(String(50))  # desktop, mobile, tablet
    browser = Column(String(100))
    os = Column(String(100))
    ip_address = Column(String(45))  # IPv6 compatible
    
    # Location (optional, from IP)
    country = Column(String(100))
    city = Column(String(100))
    
    # Session tokens (hashed)
    refresh_token_hash = Column(String(255), nullable=False, index=True)
    
    # Session state
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    revocation_reason = Column(String(255))
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession {self.device_name} - {self.user_id}>"


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """Persistent audit log for compliance"""
    __tablename__ = "audit_logs"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Action details
    action = Column(String(100), nullable=False, index=True)  # login, logout, update_profile, etc.
    resource_type = Column(String(100))  # user, order, conversation, etc.
    resource_id = Column(String(100))
    
    # Request context
    method = Column(String(10))
    path = Column(String(500))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Changes
    old_values = Column(Text)  # JSON
    new_values = Column(Text)  # JSON
    
    # Result
    status_code = Column(String(3))
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"
