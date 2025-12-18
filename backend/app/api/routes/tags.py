from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Annotated

from app.db.session import get_db
from app.models import User, Tag
from app.schemas import TagCreate, TagUpdate, TagResponse, TagListResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=TagListResponse)
async def list_tags(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """List all tags"""
    result = await db.execute(
        select(Tag).where(
            (Tag.team_id == current_user.team_id) | (Tag.team_id.is_(None))
        )
    )
    tags = result.scalars().all()
    
    return TagListResponse(
        items=[TagResponse.model_validate(t) for t in tags],
        total=len(tags)
    )


@router.post("", response_model=TagResponse)
async def create_tag(
    data: TagCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Create a new tag"""
    # Check for duplicate
    existing = await db.execute(
        select(Tag).where(
            Tag.name == data.name,
            Tag.team_id == current_user.team_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists"
        )
    
    tag = Tag(**data.model_dump(), team_id=current_user.team_id)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    
    return TagResponse.model_validate(tag)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    data: TagUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update tag"""
    result = await db.execute(
        select(Tag).where(Tag.id == tag_id)
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)
    
    await db.commit()
    await db.refresh(tag)
    
    return TagResponse.model_validate(tag)


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Delete tag"""
    result = await db.execute(
        select(Tag).where(Tag.id == tag_id)
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    await db.delete(tag)
    await db.commit()
    
    return {"message": "Tag deleted"}
