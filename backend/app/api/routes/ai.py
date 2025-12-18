from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Annotated

from app.db.session import get_db
from app.models import User, Conversation, Message, AssistantTask, AIConversation, TaskStatus
from app.schemas import (
    AIReplyRequest, AIReplyResponse,
    AISuggestRequest, AISuggestResponse, AISuggestion,
    AISummarizeRequest, AISummarizeResponse,
    AIExtractOrderRequest, AIExtractOrderResponse,
    AICategorizeRequest, AICategorizeResponse,
    AIChatRequest, AIChatResponse,
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
)
from app.api.deps import get_current_user
from app.workers.tasks.ai_tasks import generate_ai_reply_task
from app.services.ai_service import AIService

router = APIRouter()


@router.post("/reply", response_model=AIReplyResponse)
async def generate_ai_reply(
    data: AIReplyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Generate AI reply for a conversation"""
    # Get conversation messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == data.conversation_id)
        .order_by(desc(Message.created_at))
        .limit(10)
    )
    messages = list(reversed(result.scalars().all()))
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages in conversation"
        )
    
    ai_service = AIService()
    reply = await ai_service.generate_reply(messages, data.context)
    
    return AIReplyResponse(
        reply=reply["content"],
        confidence=reply["confidence"],
        alternatives=reply.get("alternatives", [])
    )


@router.post("/suggest", response_model=AISuggestResponse)
async def suggest_actions(
    data: AISuggestRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get AI-suggested actions for a conversation"""
    # Get conversation
    result = await db.execute(
        select(Conversation).where(Conversation.id == data.conversation_id)
    )
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get recent messages
    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == data.conversation_id)
        .order_by(desc(Message.created_at))
        .limit(5)
    )
    messages = list(reversed(msg_result.scalars().all()))
    
    ai_service = AIService()
    suggestions = await ai_service.suggest_actions(messages)
    
    return AISuggestResponse(
        suggestions=[AISuggestion(**s) for s in suggestions]
    )


@router.post("/summarize", response_model=AISummarizeResponse)
async def summarize_conversation(
    data: AISummarizeRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Summarize a conversation"""
    # Get all messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == data.conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages to summarize"
        )
    
    ai_service = AIService()
    summary = await ai_service.summarize_conversation(messages)
    
    return AISummarizeResponse(**summary)


@router.post("/extract-order", response_model=AIExtractOrderResponse)
async def extract_order_intent(
    data: AIExtractOrderRequest,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Extract order intent from a message"""
    ai_service = AIService()
    result = await ai_service.extract_order_intent(data.message_content)
    
    return AIExtractOrderResponse(**result)


@router.post("/categorize", response_model=AICategorizeResponse)
async def categorize_message(
    data: AICategorizeRequest,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Categorize a message"""
    ai_service = AIService()
    result = await ai_service.categorize_message(data.message_content)
    
    return AICategorizeResponse(**result)


@router.post("/chat", response_model=AIChatResponse)
async def ai_assistant_chat(
    data: AIChatRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Chat with AI assistant"""
    ai_service = AIService()
    response = await ai_service.chat(data.message)
    
    return AIChatResponse(response=response)


# Task endpoints
@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """List all tasks for current user"""
    result = await db.execute(
        select(AssistantTask)
        .where(AssistantTask.user_id == current_user.id)
        .order_by(desc(AssistantTask.created_at))
    )
    tasks = result.scalars().all()
    
    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=len(tasks)
    )


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    data: TaskCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Create a new task"""
    task = AssistantTask(
        **data.model_dump(),
        user_id=current_user.id,
        team_id=current_user.team_id
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return TaskResponse.model_validate(task)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update a task"""
    result = await db.execute(
        select(AssistantTask).where(
            AssistantTask.id == task_id,
            AssistantTask.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    return TaskResponse.model_validate(task)


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Delete a task"""
    result = await db.execute(
        select(AssistantTask).where(
            AssistantTask.id == task_id,
            AssistantTask.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    await db.delete(task)
    await db.commit()
    
    return {"message": "Task deleted"}
