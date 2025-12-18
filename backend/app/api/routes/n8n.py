from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import httpx

from app.db.session import get_db
from app.models import User
from app.schemas import N8NTriggerRequest, N8NTriggerResponse, N8NWorkflowList, N8NWebhookPayload
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()


@router.post("/trigger", response_model=N8NTriggerResponse)
async def trigger_n8n_workflow(
    data: N8NTriggerRequest,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Trigger an N8N workflow"""
    if not settings.N8N_BASE_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="N8N integration not configured"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.N8N_BASE_URL}/webhook/ghostworker",
                json={
                    "event_type": data.event_type,
                    "payload": data.payload,
                    "user_id": str(current_user.id),
                    "team_id": str(current_user.team_id)
                },
                headers={
                    "Authorization": f"Bearer {settings.N8N_API_KEY}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return N8NTriggerResponse(
                    success=True,
                    workflow_id=result.get("workflow_id"),
                    execution_id=result.get("execution_id")
                )
            else:
                return N8NTriggerResponse(
                    success=False,
                    error=f"N8N returned status {response.status_code}"
                )
                
    except Exception as e:
        return N8NTriggerResponse(
            success=False,
            error=str(e)
        )


@router.get("/workflows", response_model=N8NWorkflowList)
async def list_n8n_workflows(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """List available N8N workflows"""
    if not settings.N8N_BASE_URL or not settings.N8N_API_KEY:
        return N8NWorkflowList(workflows=[])
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.N8N_BASE_URL}/api/v1/workflows",
                headers={
                    "X-N8N-API-KEY": settings.N8N_API_KEY
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                workflows = [
                    {
                        "id": w["id"],
                        "name": w["name"],
                        "active": w.get("active", False),
                        "trigger_event": None
                    }
                    for w in data.get("data", [])
                ]
                return N8NWorkflowList(workflows=workflows)
            
    except Exception:
        pass
    
    return N8NWorkflowList(workflows=[])


@router.post("/webhook")
async def n8n_callback_webhook(
    data: N8NWebhookPayload,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Receive callback from N8N workflow execution"""
    # Log the callback
    # Could update related records based on workflow_id/execution_id
    
    return {"success": True, "message": "Callback received"}
