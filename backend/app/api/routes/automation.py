"""Workflows API routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models import Workflow, ChatbotFlow, ScheduledMessage, AutoResponder, User
from app.services.workflow_service import workflow_engine

router = APIRouter()


# Workflows
@router.get("/workflows")
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Workflow).where(Workflow.team_id == current_user.team_id))
    return result.scalars().all()


@router.post("/workflows")
async def create_workflow(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workflow = Workflow(team_id=current_user.team_id, **data)
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow


@router.put("/workflows/{workflow_id}")
async def update_workflow(
    workflow_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id, Workflow.team_id == current_user.team_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    for key, value in data.items():
        if hasattr(workflow, key):
            setattr(workflow, key, value)
    await db.commit()
    return workflow


@router.post("/workflows/{workflow_id}/activate")
async def activate_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id, Workflow.team_id == current_user.team_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    workflow.is_active = True
    await db.commit()
    return workflow


# Chatbots
@router.get("/chatbots")
async def list_chatbots(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(ChatbotFlow).where(ChatbotFlow.team_id == current_user.team_id))
    return result.scalars().all()


@router.post("/chatbots")
async def create_chatbot(data: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    chatbot = ChatbotFlow(team_id=current_user.team_id, **data)
    db.add(chatbot)
    await db.commit()
    return chatbot


# Scheduled Messages
@router.get("/scheduled-messages")
async def list_scheduled_messages(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(ScheduledMessage).where(ScheduledMessage.team_id == current_user.team_id))
    return result.scalars().all()


@router.post("/scheduled-messages")
async def create_scheduled_message(data: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = ScheduledMessage(team_id=current_user.team_id, created_by=current_user.id, **data)
    db.add(msg)
    await db.commit()
    return msg


# Auto Responders
@router.get("/auto-responders")
async def list_auto_responders(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(AutoResponder).where(AutoResponder.team_id == current_user.team_id))
    return result.scalars().all()


@router.post("/auto-responders")
async def create_auto_responder(data: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    responder = AutoResponder(team_id=current_user.team_id, **data)
    db.add(responder)
    await db.commit()
    return responder


@router.post("/auto-responders/{responder_id}/toggle")
async def toggle_auto_responder(responder_id: UUID, data: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(AutoResponder).where(AutoResponder.id == responder_id, AutoResponder.team_id == current_user.team_id))
    responder = result.scalar_one_or_none()
    if not responder:
        raise HTTPException(status_code=404, detail="Auto responder not found")
    responder.is_active = data.get("is_active", not responder.is_active)
    await db.commit()
    return responder
