from sqlalchemy import Column, String, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum
from app.db.base import Base, TimestampMixin, UUIDMixin


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AssistantTask(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assistant_tasks"
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(String(20), default="medium")
    
    # AI suggestions
    suggested_by_ai = Column(Boolean, default=False)
    ai_context = Column(JSONB, default={})
    
    # User ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    
    # Due date
    due_date = Column(String(50))
    completed_at = Column(String(50))
    
    def __repr__(self):
        return f"<AssistantTask {self.title}>"


class AIConversation(Base, UUIDMixin, TimestampMixin):
    """Store AI assistant chat history"""
    __tablename__ = "ai_conversations"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    messages = Column(JSONB, default=[])  # Array of {role, content, timestamp}
    context = Column(JSONB, default={})
    
    def __repr__(self):
        return f"<AIConversation {self.id}>"


class Settings(Base, UUIDMixin, TimestampMixin):
    """Application settings per team"""
    __tablename__ = "settings"
    
    key = Column(String(100), nullable=False, index=True)
    value = Column(JSONB)
    description = Column(Text)
    
    # Team scope (null = global)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    
    def __repr__(self):
        return f"<Settings {self.key}>"


from sqlalchemy import Boolean
