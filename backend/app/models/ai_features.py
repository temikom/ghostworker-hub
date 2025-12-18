"""AI Feature models"""
from sqlalchemy import Column, String, Text, DECIMAL, ForeignKey, Enum, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum

from app.db.base import Base, TimestampMixin, UUIDMixin


class SentimentLabel(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class VoiceTranscription(Base, UUIDMixin, TimestampMixin):
    """Voice message transcriptions"""
    __tablename__ = "voice_transcriptions"
    
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"))
    audio_url = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    language = Column(String(10))
    duration = Column(DECIMAL(10, 2))
    confidence = Column(DECIMAL(5, 4))
    
    message = relationship("Message", back_populates="voice_transcription")


class SmartRoutingRule(Base, UUIDMixin, TimestampMixin):
    """Smart routing rules for conversation assignment"""
    __tablename__ = "smart_routing_rules"
    
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    conditions = Column(JSONB, nullable=False)  # [{field, operator, value}]
    action = Column(JSONB, nullable=False)  # {type, target_id, template_id}
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    matched_count = Column(Integer, default=0)
    
    team = relationship("Team", back_populates="routing_rules")


class SentimentAnalysis(Base, UUIDMixin):
    """Sentiment analysis records"""
    __tablename__ = "sentiment_analyses"
    
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"))
    text = Column(Text, nullable=False)
    label = Column(Enum(SentimentLabel), nullable=False)
    score = Column(DECIMAL(5, 4), nullable=False)
    confidence = Column(DECIMAL(5, 4), nullable=False)
    
    message = relationship("Message", back_populates="sentiment_analysis")


class Translation(Base, UUIDMixin, TimestampMixin):
    """Message translations"""
    __tablename__ = "translations"
    
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"))
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    
    message = relationship("Message", back_populates="translation")
