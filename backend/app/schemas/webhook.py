from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID


# N8N schemas
class N8NTriggerRequest(BaseModel):
    event_type: str  # conversation.new, order.created, etc.
    payload: Dict[str, Any]


class N8NTriggerResponse(BaseModel):
    success: bool
    workflow_id: Optional[str] = None
    execution_id: Optional[str] = None
    error: Optional[str] = None


class N8NWorkflow(BaseModel):
    id: str
    name: str
    active: bool
    trigger_event: Optional[str] = None


class N8NWorkflowList(BaseModel):
    workflows: List[N8NWorkflow]


class N8NWebhookPayload(BaseModel):
    workflow_id: str
    execution_id: str
    status: str  # success, error
    data: Dict[str, Any] = {}


# Webhook schemas
class WhatsAppWebhook(BaseModel):
    object: str
    entry: List[Dict[str, Any]]


class InstagramWebhook(BaseModel):
    object: str
    entry: List[Dict[str, Any]]


class TikTokWebhook(BaseModel):
    event: str
    data: Dict[str, Any]


class WebhookResponse(BaseModel):
    success: bool
    message: str = "Webhook received"
