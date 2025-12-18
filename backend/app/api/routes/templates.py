from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from app.db.session import get_db
from app.models import User, Template
from app.schemas import TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """List all templates (global + user's own)"""
    result = await db.execute(
        select(Template).where(
            (Template.is_global == True) |
            (Template.owner_id == current_user.id) |
            (Template.team_id == current_user.team_id)
        )
    )
    templates = result.scalars().all()
    
    return TemplateListResponse(
        items=[TemplateResponse.model_validate(t) for t in templates],
        total=len(templates)
    )


@router.post("", response_model=TemplateResponse)
async def create_template(
    data: TemplateCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Create a new template"""
    template = Template(
        **data.model_dump(),
        owner_id=current_user.id if not data.is_global else None,
        team_id=current_user.team_id
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return TemplateResponse.model_validate(template)


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get template by ID"""
    result = await db.execute(
        select(Template).where(Template.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Increment usage count
    template.usage_count += 1
    await db.commit()
    
    return TemplateResponse.model_validate(template)


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    data: TemplateUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update template"""
    result = await db.execute(
        select(Template).where(Template.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Only owner can update
    if template.owner_id and template.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other user's template"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    
    return TemplateResponse.model_validate(template)


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Delete template"""
    result = await db.execute(
        select(Template).where(Template.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Only owner can delete
    if template.owner_id and template.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other user's template"
        )
    
    await db.delete(template)
    await db.commit()
    
    return {"message": "Template deleted"}
