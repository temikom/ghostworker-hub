from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from pydantic import BaseModel

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
from app.core.totp import verify_2fa
from app.api.deps import get_current_user

router = APIRouter()


class CheckEmailRequest(BaseModel):
    email: str

class CheckEmailResponse(BaseModel):
    exists: bool

class Login2FARequest(BaseModel):
    temp_token: str
    code: str

class VerifyEmailRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    email: str


@router.post("/check-email", response_model=CheckEmailResponse)
async def check_email(
    data: CheckEmailRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Check if email exists (for multi-step login)"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    return CheckEmailResponse(exists=user is not None)


@router.post("/register")
async def register(
    data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register a new user - requires email verification"""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user = User(
        email=data.email,
        name=data.name,
        phone=data.phone,
        hashed_password=get_password_hash(data.password),
        is_verified=False  # Require email verification
    )
    db.add(user)
    await db.flush()
    
    role = UserRoleAssignment(user_id=user.id, role=UserRole.MEMBER)
    db.add(role)
    await db.commit()
    
    # TODO: Send verification email
    
    return {"message": "Registration successful. Please verify your email.", "requires_verification": True}


@router.post("/login")
async def login(
    data: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Login user with multi-step security"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")
    
    # Check email verification
    if not user.is_verified:
        return {"requires_verification": True, "message": "Please verify your email first"}
    
    # Check 2FA
    if user.two_factor_enabled and user.totp_secret:
        temp_token = create_access_token(str(user.id), expires_delta=None)
        return {"requires_2fa": True, "temp_token": temp_token}
    
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    
    return {
        "token": access_token,
        "refresh_token": refresh_token,
        "user": UserResponse.model_validate(user).model_dump()
    }


@router.post("/2fa/login")
async def login_with_2fa(
    data: Login2FARequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Complete login with 2FA code"""
    payload = decode_token(data.temp_token)
    user_id = payload.get("sub")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.totp_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid request")
    
    if not verify_2fa(user.totp_secret, data.code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid verification code")
    
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    
    return {
        "token": access_token,
        "refresh_token": refresh_token,
        "user": UserResponse.model_validate(user).model_dump()
    }


@router.post("/verify-email")
async def verify_email(
    data: VerifyEmailRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Verify user email with token"""
    email = verify_password_reset_token(data.token)  # Reuse token verification
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.is_verified = True
    await db.commit()
    
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    
    return {
        "token": access_token,
        "user": UserResponse.model_validate(user).model_dump()
    }


@router.post("/resend-verification")
async def resend_verification(
    data: ResendVerificationRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Resend verification email"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    
    if user and not user.is_verified:
        # TODO: Send verification email
        pass
    
    return {"message": "If the email exists and is unverified, a verification link will be sent"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Refresh access token"""
    payload = decode_token(data.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    
    access_token = create_access_token(str(user.id))
    new_refresh_token = create_refresh_token(str(user.id))
    
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token, user=UserResponse.model_validate(user))


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """Request password reset"""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        # TODO: Send email with reset link
        pass
    return {"message": "If the email exists, a reset link will be sent"}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """Reset password with token"""
    email = verify_password_reset_token(data.token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.hashed_password = get_password_hash(data.new_password)
    await db.commit()
    return {"message": "Password reset successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Get current user"""
    return UserResponse.model_validate(current_user)
