from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, List

from app.db.session import get_db
from app.models import User, Team
from app.schemas import TeamCreate, TeamUpdate, TeamResponse, TeamWithMembers, UserResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=List[TeamResponse])
async def list_teams(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """List all teams (for admin)"""
    result = await db.execute(select(Team))
    teams = result.scalars().all()
    return [TeamResponse.model_validate(t) for t in teams]


@router.post("", response_model=TeamResponse)
async def create_team(
    data: TeamCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Create a new team"""
    team = Team(**data.model_dump())
    db.add(team)
    await db.commit()
    await db.refresh(team)
    
    # Add creator to team
    current_user.team_id = team.id
    await db.commit()
    
    return TeamResponse.model_validate(team)


@router.get("/{team_id}", response_model=TeamWithMembers)
async def get_team(
    team_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get team with members"""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Get members
    members_result = await db.execute(select(User).where(User.team_id == team_id))
    members = members_result.scalars().all()
    
    response = TeamWithMembers.model_validate(team)
    response.members = [UserResponse.model_validate(m) for m in members]
    
    return response


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    data: TeamUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update team"""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(team, field, value)
    
    await db.commit()
    await db.refresh(team)
    
    return TeamResponse.model_validate(team)


@router.post("/{team_id}/members/{user_id}")
async def add_team_member(
    team_id: str,
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Add user to team"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.team_id = team_id
    await db.commit()
    
    return {"message": "User added to team"}


@router.delete("/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: str,
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Remove user from team"""
    result = await db.execute(
        select(User).where(User.id == user_id, User.team_id == team_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in team"
        )
    
    user.team_id = None
    await db.commit()
    
    return {"message": "User removed from team"}
