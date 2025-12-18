"""Webhook signature verification utilities"""
import hmac
import hashlib
from fastapi import Request, HTTPException, status

from app.core.config import settings


def verify_meta_signature(payload: bytes, signature: str) -> bool:
    """Verify Facebook/Instagram/WhatsApp webhook signature"""
    if not signature or not settings.META_APP_SECRET:
        return False
    
    expected_signature = hmac.new(
        settings.META_APP_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Signature format: sha256=xxxxx
    if signature.startswith("sha256="):
        signature = signature[7:]
    
    return hmac.compare_digest(expected_signature, signature)


def verify_tiktok_signature(payload: bytes, signature: str, timestamp: str) -> bool:
    """Verify TikTok webhook signature"""
    if not signature or not settings.TIKTOK_APP_SECRET:
        return False
    
    # TikTok signature: HMAC-SHA256(app_secret, timestamp + payload)
    message = f"{timestamp}{payload.decode()}"
    expected_signature = hmac.new(
        settings.TIKTOK_APP_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


def verify_n8n_signature(payload: bytes, signature: str) -> bool:
    """Verify N8N webhook signature"""
    if not signature or not settings.N8N_WEBHOOK_SECRET:
        return False
    
    expected_signature = hmac.new(
        settings.N8N_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


async def require_webhook_signature(
    request: Request,
    platform: str
) -> bytes:
    """Middleware function to verify webhook signature"""
    payload = await request.body()
    
    if platform in ["whatsapp", "instagram", "facebook"]:
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not verify_meta_signature(payload, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    elif platform == "tiktok":
        signature = request.headers.get("X-Tiktok-Signature", "")
        timestamp = request.headers.get("X-Tiktok-Timestamp", "")
        if not verify_tiktok_signature(payload, signature, timestamp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    elif platform == "n8n":
        signature = request.headers.get("X-N8N-Signature", "")
        if not verify_n8n_signature(payload, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    return payload
