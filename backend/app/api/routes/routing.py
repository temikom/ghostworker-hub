"""Smart Routing API routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.api.deps import get_db, get_current_user
from app.models import SmartRoutingRule, User

router = APIRouter()


@router.get("/rules")
async def list_routing_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(SmartRoutingRule)
        .where(SmartRoutingRule.team_id == current_user.team_id)
        .order_by(SmartRoutingRule.priority)
    )
    return result.scalars().all()


@router.post("/rules")
async def create_routing_rule(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rule = SmartRoutingRule(team_id=current_user.team_id, **data)
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.put("/rules/{rule_id}")
async def update_routing_rule(
    rule_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(SmartRoutingRule).where(
            SmartRoutingRule.id == rule_id,
            SmartRoutingRule.team_id == current_user.team_id
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    for key, value in data.items():
        if hasattr(rule, key):
            setattr(rule, key, value)
    
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}")
async def delete_routing_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(SmartRoutingRule).where(
            SmartRoutingRule.id == rule_id,
            SmartRoutingRule.team_id == current_user.team_id
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    await db.delete(rule)
    await db.commit()
    return {"success": True}


@router.post("/rules/reorder")
async def reorder_rules(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rule_ids = data.get("rule_ids", [])
    for priority, rule_id in enumerate(rule_ids):
        result = await db.execute(
            select(SmartRoutingRule).where(
                SmartRoutingRule.id == rule_id,
                SmartRoutingRule.team_id == current_user.team_id
            )
        )
        rule = result.scalar_one_or_none()
        if rule:
            rule.priority = priority
    
    await db.commit()
    return {"success": True}
