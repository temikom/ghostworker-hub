from fastapi import APIRouter, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends
import hmac
import hashlib

from app.db.session import get_db
from app.models import WebhookEvent
from app.schemas import WhatsAppWebhook, InstagramWebhook, TikTokWebhook, WebhookResponse
from app.core.config import settings
from app.workers.tasks.webhook_tasks import process_webhook_task

router = APIRouter()


@router.get("/whatsapp")
async def verify_whatsapp_webhook(
    mode: str = None,
    challenge: str = None,
    verify_token: str = None
):
    """Verify WhatsApp webhook"""
    if mode == "subscribe" and verify_token == settings.META_VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/whatsapp", response_model=WebhookResponse)
async def whatsapp_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Handle WhatsApp webhook"""
    payload = await request.json()
    
    # Store webhook event
    event = WebhookEvent(
        platform="whatsapp",
        event_type="message",
        payload=payload
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    # Queue for processing
    process_webhook_task.delay(str(event.id))
    
    return WebhookResponse(success=True)


@router.get("/instagram")
async def verify_instagram_webhook(
    mode: str = None,
    challenge: str = None,
    verify_token: str = None
):
    """Verify Instagram webhook"""
    if mode == "subscribe" and verify_token == settings.META_VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/instagram", response_model=WebhookResponse)
async def instagram_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Handle Instagram webhook"""
    payload = await request.json()
    
    # Store webhook event
    event = WebhookEvent(
        platform="instagram",
        event_type="message",
        payload=payload
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    # Queue for processing
    process_webhook_task.delay(str(event.id))
    
    return WebhookResponse(success=True)


@router.post("/tiktok", response_model=WebhookResponse)
async def tiktok_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Handle TikTok webhook"""
    payload = await request.json()
    
    # Store webhook event
    event = WebhookEvent(
        platform="tiktok",
        event_type=payload.get("event", "message"),
        payload=payload
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    # Queue for processing
    process_webhook_task.delay(str(event.id))
    
    return WebhookResponse(success=True)
