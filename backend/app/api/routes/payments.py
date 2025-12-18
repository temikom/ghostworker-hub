"""Payments API routes"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models import PaymentConfig, Payment, Order, User
from app.services.payment_service import payment_service

router = APIRouter()


@router.get("/config")
async def get_payment_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(PaymentConfig).where(PaymentConfig.team_id == current_user.team_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        return {"provider": "stripe", "is_configured": False}
    return {
        "provider": config.provider,
        "is_configured": config.is_configured,
        "public_key": config.public_key,
        "webhook_url": config.webhook_url
    }


@router.put("/config")
async def update_payment_config(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(PaymentConfig).where(PaymentConfig.team_id == current_user.team_id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        config = PaymentConfig(team_id=current_user.team_id)
        db.add(config)
    
    for key, value in data.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    config.is_configured = bool(config.public_key and config.secret_key_encrypted)
    await db.commit()
    return config


@router.post("/checkout")
async def create_checkout_session(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order_id = data.get("order_id")
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    line_items = [{
        "price_data": {
            "currency": order.currency.lower(),
            "product_data": {"name": f"Order #{str(order.id)[:8]}"},
            "unit_amount": int(order.total * 100)
        },
        "quantity": 1
    }]
    
    session = await payment_service.create_checkout_session(
        order_id=str(order.id),
        line_items=line_items,
        success_url=data.get("success_url", "https://example.com/success"),
        cancel_url=data.get("cancel_url", "https://example.com/cancel")
    )
    
    return session


@router.post("/refund")
async def refund_payment(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment_id = data.get("payment_id")
    amount = data.get("amount")
    
    result = await payment_service.refund_payment(payment_id, amount)
    return result


@router.post("/webhook")
async def handle_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    
    # In production, get webhook secret from config
    webhook_secret = "whsec_..."
    
    verification = payment_service.verify_webhook_signature(payload, signature, webhook_secret)
    if not verification.get("valid"):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event = verification.get("event")
    result = await payment_service.handle_webhook_event(event)
    
    # Update order status if needed
    if result.get("order_id") and result.get("payment_status"):
        order_result = await db.execute(select(Order).where(Order.id == result["order_id"]))
        order = order_result.scalar_one_or_none()
        if order:
            order.payment_status = result["payment_status"]
            await db.commit()
    
    return {"received": True}
