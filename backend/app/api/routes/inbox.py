from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Annotated, Optional, List

from app.db.session import get_db
from app.models import User, Conversation, Message, Customer, ConversationTag, Tag
from app.schemas import InboxResponse, InboxItem
from app.api.deps import get_current_user, PaginationParams

router = APIRouter()


@router.get("", response_model=InboxResponse)
async def get_inbox(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    pagination: Annotated[PaginationParams, Depends()],
    platform: Optional[str] = Query(None),
    is_starred: Optional[bool] = Query(None),
    is_archived: Optional[bool] = Query(False),
    tag_id: Optional[str] = Query(None)
):
    """Get unified inbox with all conversations"""
    
    # Build query
    query = select(Conversation).where(Conversation.team_id == current_user.team_id)
    
    if platform:
        query = query.where(Conversation.platform == platform)
    
    if is_starred is not None:
        query = query.where(Conversation.is_starred == is_starred)
    
    if is_archived is not None:
        query = query.where(Conversation.is_archived == is_archived)
    
    if tag_id:
        query = query.join(ConversationTag).where(ConversationTag.tag_id == tag_id)
    
    if pagination.search:
        query = query.join(Customer, isouter=True).where(
            Customer.name.ilike(f"%{pagination.search}%") |
            Conversation.subject.ilike(f"%{pagination.search}%")
        )
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.order_by(desc(Conversation.last_message_at))
    query = query.offset(pagination.offset).limit(pagination.page_size)
    
    result = await db.execute(query)
    conversations = result.scalars().all()
    
    # Build inbox items
    items = []
    for conv in conversations:
        # Get customer name
        customer_name = "Unknown"
        if conv.customer_id:
            customer_result = await db.execute(
                select(Customer).where(Customer.id == conv.customer_id)
            )
            customer = customer_result.scalar_one_or_none()
            if customer:
                customer_name = customer.name
        
        # Get last message
        last_msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_msg = last_msg_result.scalar_one_or_none()
        last_message = last_msg.content[:100] if last_msg else ""
        
        # Get tags
        tags_result = await db.execute(
            select(Tag)
            .join(ConversationTag)
            .where(ConversationTag.conversation_id == conv.id)
        )
        tags = [t.name for t in tags_result.scalars().all()]
        
        items.append(InboxItem(
            id=conv.id,
            platform=conv.platform,
            customer_name=customer_name,
            last_message=last_message,
            last_message_time=conv.last_message_at or str(conv.created_at),
            unread_count=conv.unread_count,
            is_starred=conv.is_starred,
            tags=tags
        ))
    
    return InboxResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )
