from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Annotated
from datetime import datetime

from app.db.session import get_db
from app.models import User, Message, Conversation, MessageDirection, MessageStatus, Platform
from app.schemas import MessageResponse, MessageListResponse, SendMessageRequest
from app.api.deps import get_current_user
from app.workers.tasks.message_tasks import send_message_task

router = APIRouter()


@router.get("/{conversation_id}", response_model=MessageListResponse)
async def get_messages(
    conversation_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 50,
    offset: int = 0
):
    """Get messages for a conversation"""
    # Verify conversation exists
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conv = conv_result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(desc(Message.created_at))
        .offset(offset)
        .limit(limit)
    )
    messages = result.scalars().all()
    
    # Mark as read
    conv.unread_count = 0
    await db.commit()
    
    return MessageListResponse(
        items=[MessageResponse.model_validate(m) for m in reversed(messages)],
        total=len(messages)
    )


@router.post("/send", response_model=MessageResponse)
async def send_message(
    data: SendMessageRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Send a message"""
    # Verify conversation exists
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == data.conversation_id)
    )
    conv = conv_result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Create message
    message = Message(
        conversation_id=conv.id,
        content=data.content,
        platform=Platform(data.platform),
        direction=MessageDirection.OUTBOUND,
        status=MessageStatus.PENDING,
        sender_id=str(current_user.id),
        sender_name=current_user.name
    )
    db.add(message)
    
    # Update conversation
    conv.last_message_at = datetime.utcnow().isoformat()
    
    await db.commit()
    await db.refresh(message)
    
    # Queue message for sending
    send_message_task.delay(str(message.id))
    
    return MessageResponse.model_validate(message)
