"""Session management and 2FA endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Annotated
from datetime import datetime, timedelta
import hashlib
import secrets

from app.db.session import get_db
from app.models import User
from app.models.session import UserSession
from app.schemas.session import (
    Setup2FAResponse, Verify2FARequest, Verify2FAResponse,
    SessionResponse, SessionListResponse, RevokeSessionRequest
)
from app.core.totp import setup_2fa, verify_2fa
from app.core.security import create_access_token, create_refresh_token
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()


def parse_user_agent(user_agent: str) -> dict:
    """Parse user agent string for device info"""
    ua_lower = user_agent.lower() if user_agent else ""
    
    # Detect device type
    if any(m in ua_lower for m in ["mobile", "android", "iphone", "ipad"]):
        device_type = "mobile" if "mobile" in ua_lower else "tablet"
    else:
        device_type = "desktop"
    
    # Detect browser
    browser = "Unknown"
    if "chrome" in ua_lower and "edg" not in ua_lower:
        browser = "Chrome"
    elif "firefox" in ua_lower:
        browser = "Firefox"
    elif "safari" in ua_lower and "chrome" not in ua_lower:
        browser = "Safari"
    elif "edg" in ua_lower:
        browser = "Edge"
    
    # Detect OS
    os = "Unknown"
    if "windows" in ua_lower:
        os = "Windows"
    elif "mac" in ua_lower:
        os = "macOS"
    elif "linux" in ua_lower:
        os = "Linux"
    elif "android" in ua_lower:
        os = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower:
        os = "iOS"
    
    return {
        "device_type": device_type,
        "browser": browser,
        "os": os,
        "device_name": f"{browser} on {os}"
    }


async def create_session(
    db: AsyncSession,
    user: User,
    request: Request,
    refresh_token: str
) -> UserSession:
    """Create a new user session"""
    user_agent = request.headers.get("User-Agent", "")
    device_info = parse_user_agent(user_agent)
    
    # Hash the refresh token
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    
    session = UserSession(
        user_id=user.id,
        device_name=device_info["device_name"],
        device_type=device_info["device_type"],
        browser=device_info["browser"],
        os=device_info["os"],
        ip_address=request.client.host if request.client else None,
        refresh_token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session


# 2FA Endpoints
@router.post("/2fa/setup", response_model=Setup2FAResponse)
async def setup_two_factor(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Setup 2FA for user account"""
    if current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )
    
    encrypted_secret, uri, qr_code = setup_2fa(current_user.email)
    
    # Store temporarily - user must verify before it's active
    current_user.totp_secret_pending = encrypted_secret
    await db.commit()
    
    return Setup2FAResponse(qr_code=qr_code, provisioning_uri=uri)


@router.post("/2fa/verify", response_model=Verify2FAResponse)
async def verify_two_factor_setup(
    data: Verify2FARequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Verify 2FA setup with code from authenticator"""
    if not current_user.totp_secret_pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending 2FA setup"
        )
    
    if not verify_2fa(current_user.totp_secret_pending, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Activate 2FA
    current_user.totp_secret = current_user.totp_secret_pending
    current_user.totp_secret_pending = None
    current_user.two_factor_enabled = True
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    current_user.backup_codes = ",".join(backup_codes)
    
    await db.commit()
    
    return Verify2FAResponse(
        success=True,
        backup_codes=backup_codes,
        message="2FA enabled successfully. Save your backup codes!"
    )


@router.post("/2fa/disable")
async def disable_two_factor(
    data: Verify2FARequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Disable 2FA (requires current code)"""
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    if not verify_2fa(current_user.totp_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    current_user.totp_secret = None
    current_user.two_factor_enabled = False
    current_user.backup_codes = None
    
    await db.commit()
    
    return {"message": "2FA disabled successfully"}


# Session Management Endpoints
@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """List all active sessions for current user"""
    result = await db.execute(
        select(UserSession)
        .where(UserSession.user_id == current_user.id)
        .where(UserSession.is_active == True)
        .order_by(UserSession.last_activity.desc())
    )
    sessions = result.scalars().all()
    
    # Get current session token hash
    auth_header = request.headers.get("Authorization", "")
    current_token_hash = None
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        current_token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
    
    session_responses = []
    for session in sessions:
        resp = SessionResponse.model_validate(session)
        # Check if this is the current session
        if current_token_hash and session.refresh_token_hash.startswith(current_token_hash):
            resp.is_current = True
        session_responses.append(resp)
    
    return SessionListResponse(sessions=session_responses, total=len(sessions))


@router.post("/sessions/{session_id}/revoke")
async def revoke_session(
    session_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    reason: str = "User requested revocation"
):
    """Revoke a specific session"""
    result = await db.execute(
        select(UserSession)
        .where(UserSession.id == session_id)
        .where(UserSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.is_active = False
    session.revoked_at = datetime.utcnow()
    session.revocation_reason = reason
    
    await db.commit()
    
    return {"message": "Session revoked successfully"}


@router.post("/sessions/revoke-all")
async def revoke_all_sessions(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    reason: str = "User requested revocation of all sessions"
):
    """Revoke all sessions except current"""
    # Get current session token hash
    auth_header = request.headers.get("Authorization", "")
    current_token_hash = None
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        current_token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Revoke all sessions
    await db.execute(
        update(UserSession)
        .where(UserSession.user_id == current_user.id)
        .where(UserSession.is_active == True)
        .where(UserSession.refresh_token_hash != current_token_hash)
        .values(
            is_active=False,
            revoked_at=datetime.utcnow(),
            revocation_reason=reason
        )
    )
    
    await db.commit()
    
    return {"message": "All other sessions revoked successfully"}
