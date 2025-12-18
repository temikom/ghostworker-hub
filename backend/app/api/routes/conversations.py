from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Annotated, List
from uuid import UUID

from app.db.session import get_db
from app.models import User, Conversation, Customer, ConversationTag, Tag
from app.schemas import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    ConversationListResponse, ConversationWithCustomer, AttachTagRequest
)
from app.api.deps import get_current_user, PaginationParams

router = APIRouter()


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    pagination: Annotated[PaginationParams, Depends()]
):
    """List all conversations"""
    query = select(Conversation).where(Conversation.team_id == current_user.team_id)
    
    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(Conversation).where(
            Conversation.team_id == current_user.team_id
        )
    )
    total = count_result.scalar()
    
    # Get paginated results
    query = query.order_by(desc(Conversation.last_message_at))
    query = query.offset(pagination.offset).limit(pagination.page_size)
    
    result = await db.execute(query)
    conversations = result.scalars().all()
    
    items = []
    for conv in conversations:
        item = ConversationWithCustomer.model_validate(conv)
        if conv.customer_id:
            customer_result = await db.execute(
                select(Customer).where(Customer.id == conv.customer_id)
            )
            customer = customer_result.scalar_one_or_none()
            if customer:
                item.customer_name = customer.name
        items.append(item)
    
    return ConversationListResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get("/{conversation_id}", response_model=ConversationWithCustomer)
async def get_conversation(
    conversation_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get conversation by ID"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    response = ConversationWithCustomer.model_validate(conv)
    
    if conv.customer_id:
        customer_result = await db.execute(
            select(Customer).where(Customer.id == conv.customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        if customer:
            response.customer_name = customer.name
    
    return response


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Create a new conversation"""
    conv = Conversation(
        **data.model_dump(),
        team_id=current_user.team_id
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    
    return ConversationResponse.model_validate(conv)


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update conversation"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conv, field, value)
    
    await db.commit()
    await db.refresh(conv)
    
    return ConversationResponse.model_validate(conv)


@router.post("/{conversation_id}/tags")
async def attach_tags(
    conversation_id: str,
    data: AttachTagRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Attach tags to conversation"""
    # Verify conversation exists
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Remove existing tags
    await db.execute(
        ConversationTag.__table__.delete().where(
            ConversationTag.conversation_id == conversation_id
        )
    )
    
    # Add new tags
    for tag_id in data.tag_ids:
        conv_tag = ConversationTag(
            conversation_id=UUID(conversation_id),
            tag_id=tag_id
        )
        db.add(conv_tag)
    
    await db.commit()
    
    return {"message": "Tags updated"}


@router.delete("/{conversation_id}/tags/{tag_id}")
async def remove_tag(
    conversation_id: str,
    tag_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Remove tag from conversation"""
    await db.execute(
        ConversationTag.__table__.delete().where(
            ConversationTag.conversation_id == conversation_id,
            ConversationTag.tag_id == tag_id
        )
    )
    await db.commit()
    
    return {"message": "Tag removed"}
