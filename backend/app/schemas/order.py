from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.order import OrderStatus


class OrderItem(BaseModel):
    name: str
    quantity: int = Field(..., ge=1)
    price: float = Field(..., ge=0)
    sku: Optional[str] = None


class AddressSchema(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class OrderBase(BaseModel):
    items: List[OrderItem] = []
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    customer_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    shipping_address: Optional[AddressSchema] = None
    billing_address: Optional[AddressSchema] = None


class OrderUpdate(BaseModel):
    items: Optional[List[OrderItem]] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    shipping_address: Optional[AddressSchema] = None


class UpdateOrderStatus(BaseModel):
    order_id: str
    status: str


class OrderResponse(OrderBase):
    id: UUID
    order_number: str
    status: OrderStatus
    subtotal: float
    tax: float
    shipping: float
    discount: float
    total: float
    currency: str
    customer_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    shipping_address: Dict[str, Any] = {}
    billing_address: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderWithCustomer(OrderResponse):
    customer_name: Optional[str] = None


class OrderListResponse(BaseModel):
    items: List[OrderWithCustomer]
    total: int
    page: int
    page_size: int


class OrderTimelineItem(BaseModel):
    id: UUID
    action: str
    description: Optional[str] = None
    actor_name: Optional[str] = None
    created_at: datetime
    metadata: Dict[str, Any] = {}


class OrderDetailResponse(OrderWithCustomer):
    timeline: List[OrderTimelineItem] = []
