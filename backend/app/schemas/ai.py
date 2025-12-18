from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.assistant import TaskStatus


# AI schemas
class AIReplyRequest(BaseModel):
    conversation_id: UUID
    context: Optional[str] = None


class AIReplyResponse(BaseModel):
    reply: str
    confidence: int  # 0-100
    alternatives: List[str] = []


class AISuggestRequest(BaseModel):
    conversation_id: UUID


class AISuggestion(BaseModel):
    action: str
    description: str
    priority: str


class AISuggestResponse(BaseModel):
    suggestions: List[AISuggestion]


class AISummarizeRequest(BaseModel):
    conversation_id: UUID


class AISummarizeResponse(BaseModel):
    summary: str
    key_points: List[str]
    sentiment: str  # positive, negative, neutral


class AIExtractOrderRequest(BaseModel):
    message_content: str


class AIExtractOrderResponse(BaseModel):
    has_order_intent: bool
    items: List[Dict[str, Any]]
    total_estimate: Optional[float] = None
    confidence: int


class AICategorizeRequest(BaseModel):
    message_content: str


class AICategorizeResponse(BaseModel):
    category: str
    subcategory: Optional[str] = None
    confidence: int
    tags: List[str]


class AIChatRequest(BaseModel):
    message: str


class AIChatResponse(BaseModel):
    response: str


# Assistant Task schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="medium")


class TaskCreate(TaskBase):
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[str] = None


class TaskResponse(TaskBase):
    id: UUID
    status: TaskStatus
    suggested_by_ai: bool
    due_date: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int
