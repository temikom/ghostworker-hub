from fastapi import APIRouter, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends
import json

from app.db.session import get_db
from app.models import WebhookEvent
from app.schemas import WhatsAppWebhook, InstagramWebhook, TikTokWebhook, WebhookResponse
from app.core.config import settings
from app.core.webhook_security import (
    verify_meta_signature, verify_tiktok_signature, verify_n8n_signature
)
from app.workers.tasks import process_webhook_task

router = APIRouter()


async def _verify_and_store_webhook(
    request: Request,
    db: AsyncSession,
    platform: str
) -> WebhookEvent:
    """Verify webhook signature and store event"""
    payload = await request.body()
    
    # Verify signature based on platform
    if platform in ["whatsapp", "instagram", "facebook"]:
        signature = request.headers.get("X-Hub-Signature-256", "")
        if settings.META_APP_SECRET and not verify_meta_signature(payload, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    elif platform == "tiktok":
        signature = request.headers.get("X-Tiktok-Signature", "")
        timestamp = request.headers.get("X-Tiktok-Timestamp", "")
        if settings.TIKTOK_APP_SECRET and not verify_tiktok_signature(payload, signature, timestamp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    # Parse and store
    payload_json = json.loads(payload.decode())
    event = WebhookEvent(
        platform=platform,
        event_type=payload_json.get("event", "message"),
        payload=payload_json
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    return event


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
    """Handle WhatsApp webhook with signature verification"""
    event = await _verify_and_store_webhook(request, db, "whatsapp")
    process_webhook_task.delay(str(event.id))
    return WebhookResponse(success=True)


@router.get("/facebook")
async def verify_facebook_webhook(
    mode: str = None,
    challenge: str = None,
    verify_token: str = None
):
    """Verify Facebook Messenger webhook"""
    if mode == "subscribe" and verify_token == settings.FACEBOOK_VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/facebook", response_model=WebhookResponse)
async def facebook_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Handle Facebook Messenger webhook with signature verification"""
    event = await _verify_and_store_webhook(request, db, "facebook")
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
    """Handle Instagram webhook with signature verification"""
    event = await _verify_and_store_webhook(request, db, "instagram")
    process_webhook_task.delay(str(event.id))
    return WebhookResponse(success=True)


@router.post("/tiktok", response_model=WebhookResponse)
async def tiktok_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Handle TikTok webhook with signature verification"""
    event = await _verify_and_store_webhook(request, db, "tiktok")
    process_webhook_task.delay(str(event.id))
    return WebhookResponse(success=True)
