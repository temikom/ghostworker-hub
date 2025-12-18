from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from datetime import datetime

from app.db.session import get_db
from app.models import User, Integration, IntegrationStatus
from app.schemas import IntegrationConnect, IntegrationDisconnect, IntegrationResponse, IntegrationListResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=IntegrationListResponse)
async def list_integrations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """List all integrations"""
    result = await db.execute(
        select(Integration).where(Integration.team_id == current_user.team_id)
    )
    integrations = result.scalars().all()
    
    # Ensure all platforms are represented
    platforms = ["whatsapp", "instagram", "tiktok", "email"]
    existing = {i.platform: i for i in integrations}
    
    items = []
    for platform in platforms:
        if platform in existing:
            items.append(IntegrationResponse.model_validate(existing[platform]))
        else:
            items.append(IntegrationResponse(
                id=None,
                platform=platform,
                status=IntegrationStatus.DISCONNECTED,
                connected_at=None
            ))
    
    return IntegrationListResponse(items=items)


@router.post("/connect", response_model=IntegrationResponse)
async def connect_integration(
    data: IntegrationConnect,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Connect an integration"""
    # Check if already exists
    result = await db.execute(
        select(Integration).where(
            Integration.platform == data.platform,
            Integration.team_id == current_user.team_id
        )
    )
    integration = result.scalar_one_or_none()
    
    if integration:
        # Update existing
        integration.credentials = data.credentials
        integration.status = IntegrationStatus.CONNECTED
        integration.error_message = None
    else:
        # Create new
        integration = Integration(
            platform=data.platform,
            credentials=data.credentials,
            status=IntegrationStatus.CONNECTED,
            team_id=current_user.team_id
        )
        db.add(integration)
    
    await db.commit()
    await db.refresh(integration)
    
    return IntegrationResponse(
        id=integration.id,
        platform=integration.platform,
        status=integration.status,
        connected_at=str(integration.created_at)
    )


@router.post("/disconnect")
async def disconnect_integration(
    data: IntegrationDisconnect,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Disconnect an integration"""
    result = await db.execute(
        select(Integration).where(
            Integration.platform == data.platform,
            Integration.team_id == current_user.team_id
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    integration.status = IntegrationStatus.DISCONNECTED
    integration.credentials = {}
    
    await db.commit()
    
    return {"success": True, "message": "Integration disconnected"}
