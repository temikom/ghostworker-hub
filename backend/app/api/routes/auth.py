from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from app.db.session import get_db
from app.models import User, UserRoleAssignment, UserRole
from app.schemas import (
    UserCreate, UserResponse, LoginRequest, TokenResponse,
    RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token,
    decode_token, create_password_reset_token, verify_password_reset_token
)
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(
    data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register a new user"""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=data.email,
        name=data.name,
        phone=data.phone,
        hashed_password=get_password_hash(data.password)
    )
    db.add(user)
    await db.flush()
    
    # Assign default role
    role = UserRoleAssignment(user_id=user.id, role=UserRole.MEMBER)
    db.add(role)
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Login user"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Refresh access token"""
    payload = decode_token(data.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    access_token = create_access_token(str(user.id))
    new_refresh_token = create_refresh_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Request password reset"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if user:
        token = create_password_reset_token(user.email)
        # TODO: Send email with reset link
        # await send_password_reset_email(user.email, token)
    
    return {"message": "If the email exists, a reset link will be sent"}


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Reset password with token"""
    email = verify_password_reset_token(data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.hashed_password = get_password_hash(data.new_password)
    await db.commit()
    
    return {"message": "Password reset successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get current user"""
    return UserResponse.model_validate(current_user)
