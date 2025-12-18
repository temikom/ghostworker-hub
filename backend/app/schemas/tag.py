from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Tag schemas
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#6366f1", pattern="^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


class TagResponse(TagBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    items: List[TagResponse]
    total: int


class AttachTagRequest(BaseModel):
    tag_ids: List[UUID]


# Template schemas
class TemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    shortcut: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)


class TemplateCreate(TemplateBase):
    is_global: bool = False


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    shortcut: Optional[str] = None
    category: Optional[str] = None
    is_global: Optional[bool] = None


class TemplateResponse(TemplateBase):
    id: UUID
    is_global: bool
    usage_count: int
    owner_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    items: List[TemplateResponse]
    total: int
