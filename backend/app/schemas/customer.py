from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None


class CustomerCreate(CustomerBase):
    whatsapp_id: Optional[str] = None
    instagram_id: Optional[str] = None
    tiktok_id: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    whatsapp_id: Optional[str] = None
    instagram_id: Optional[str] = None
    tiktok_id: Optional[str] = None
    assigned_owner_id: Optional[UUID] = None


class CustomerResponse(CustomerBase):
    id: UUID
    avatar_url: Optional[str] = None
    whatsapp_id: Optional[str] = None
    instagram_id: Optional[str] = None
    tiktok_id: Optional[str] = None
    notes: Optional[str] = None
    assigned_owner_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CustomerWithActivity(CustomerResponse):
    total_conversations: int = 0
    total_orders: int = 0
    total_revenue: float = 0
    last_activity: Optional[str] = None
    tags: List[str] = []


class CustomerListResponse(BaseModel):
    items: List[CustomerWithActivity]
    total: int
    page: int
    page_size: int


class ActivityResponse(BaseModel):
    id: UUID
    action: str
    description: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    user_name: Optional[str] = None
    created_at: datetime
    metadata: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class CustomerActivityResponse(BaseModel):
    items: List[ActivityResponse]
    total: int
