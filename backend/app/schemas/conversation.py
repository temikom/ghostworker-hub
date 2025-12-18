from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.conversation import Platform, MessageStatus, MessageDirection


class ConversationBase(BaseModel):
    platform: Platform
    subject: Optional[str] = None


class ConversationCreate(ConversationBase):
    customer_id: Optional[UUID] = None
    platform_conversation_id: Optional[str] = None


class ConversationUpdate(BaseModel):
    subject: Optional[str] = None
    is_archived: Optional[bool] = None
    is_starred: Optional[bool] = None


class ConversationResponse(ConversationBase):
    id: UUID
    platform_conversation_id: Optional[str] = None
    is_archived: bool
    is_starred: bool
    unread_count: int
    last_message_at: Optional[str] = None
    customer_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationWithCustomer(ConversationResponse):
    customer_name: Optional[str] = None
    last_message: Optional[str] = None


class ConversationListResponse(BaseModel):
    items: List[ConversationWithCustomer]
    total: int
    page: int
    page_size: int


# Message schemas
class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    platform: Platform


class MessageCreate(MessageBase):
    conversation_id: UUID


class SendMessageRequest(BaseModel):
    conversation_id: str
    content: str
    platform: str


class MessageResponse(MessageBase):
    id: UUID
    conversation_id: UUID
    platform_message_id: Optional[str] = None
    direction: MessageDirection
    status: MessageStatus
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    is_ai_generated: bool
    attachments: List[Dict[str, Any]] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    items: List[MessageResponse]
    total: int


# Inbox unified response
class InboxItem(BaseModel):
    id: UUID
    platform: Platform
    customer_name: str
    last_message: str
    last_message_time: str
    unread_count: int
    is_starred: bool
    tags: List[str] = []


class InboxResponse(BaseModel):
    items: List[InboxItem]
    total: int
    page: int
    page_size: int
