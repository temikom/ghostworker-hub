from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from app.models.integration import IntegrationStatus


# Integration schemas
class IntegrationCredentials(BaseModel):
    # WhatsApp
    phone_id: Optional[str] = None
    access_token: Optional[str] = None
    verify_token: Optional[str] = None
    
    # Instagram
    instagram_access_token: Optional[str] = None
    
    # TikTok
    app_id: Optional[str] = None
    secret: Optional[str] = None
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None


class IntegrationConnect(BaseModel):
    platform: str
    credentials: Dict[str, Any]


class IntegrationDisconnect(BaseModel):
    platform: str


class IntegrationResponse(BaseModel):
    id: UUID
    platform: str
    status: IntegrationStatus
    connected_at: Optional[str] = None
    last_sync_at: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class IntegrationListResponse(BaseModel):
    items: List[IntegrationResponse]


# Analytics schemas
class AnalyticsQuery(BaseModel):
    start_date: date
    end_date: date
    platform: Optional[str] = None


class MessageAnalytics(BaseModel):
    date: str
    total: int
    inbound: int
    outbound: int
    whatsapp: int
    instagram: int
    tiktok: int
    email: int


class ResponseTimeAnalytics(BaseModel):
    avg_response_time_seconds: int
    avg_first_response_time_seconds: int
    trend: str  # "up", "down", "stable"


class ChannelDistribution(BaseModel):
    whatsapp: int
    instagram: int
    tiktok: int
    email: int
    total: int


class TopCustomer(BaseModel):
    id: UUID
    name: str
    message_count: int
    order_count: int
    total_revenue: float


class OrdersSummary(BaseModel):
    total_orders: int
    total_revenue: float
    pending: int
    processing: int
    shipped: int
    delivered: int
    cancelled: int


class AnalyticsDashboard(BaseModel):
    messages_per_day: List[MessageAnalytics]
    response_time: ResponseTimeAnalytics
    channel_distribution: ChannelDistribution
    top_customers: List[TopCustomer]
    orders_summary: OrdersSummary
