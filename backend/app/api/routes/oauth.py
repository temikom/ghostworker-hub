from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, Optional
import httpx
import secrets

from app.db.session import get_db
from app.models import User, UserRoleAssignment, UserRole
from app.schemas import UserResponse, TokenResponse
from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.core.config import settings

router = APIRouter()

# OAuth state storage (in production, use Redis)
oauth_states: dict = {}


@router.get("/oauth/{provider}")
async def oauth_login(
    provider: str,
    redirect_url: str = Query(...)
):
    """Initiate OAuth flow"""
    if provider not in ['google', 'microsoft', 'facebook']:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    
    # Generate state token
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"provider": provider, "redirect_url": redirect_url}
    
    # Build authorization URL based on provider
    if provider == 'google':
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.API_BASE_URL}/auth/oauth/callback"
            f"&response_type=code"
            f"&scope=openid email profile"
            f"&state={state}"
        )
    elif provider == 'microsoft':
        auth_url = (
            f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
            f"?client_id={settings.MICROSOFT_CLIENT_ID}"
            f"&redirect_uri={settings.API_BASE_URL}/auth/oauth/callback"
            f"&response_type=code"
            f"&scope=openid email profile"
            f"&state={state}"
        )
    elif provider == 'facebook':
        auth_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth"
            f"?client_id={settings.FACEBOOK_APP_ID}"
            f"&redirect_uri={settings.API_BASE_URL}/auth/oauth/callback"
            f"&scope=email,public_profile"
            f"&state={state}"
        )
    
    return RedirectResponse(url=auth_url)


@router.get("/oauth/callback")
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Handle OAuth callback"""
    # Verify state
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    state_data = oauth_states.pop(state)
    provider = state_data["provider"]
    redirect_url = state_data["redirect_url"]
    
    try:
        # Exchange code for tokens based on provider
        if provider == 'google':
            user_info = await _get_google_user_info(code)
        elif provider == 'microsoft':
            user_info = await _get_microsoft_user_info(code)
        elif provider == 'facebook':
            user_info = await _get_facebook_user_info(code)
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")
        
        # Find or create user
        email = user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                name=user_info.get("name", email.split("@")[0]),
                hashed_password=get_password_hash(secrets.token_urlsafe(32)),
                is_verified=True,
                avatar_url=user_info.get("picture")
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
        
        # Redirect back to frontend with tokens
        return RedirectResponse(
            url=f"{redirect_url}?token={access_token}&refresh={refresh_token}"
        )
        
    except Exception as e:
        return RedirectResponse(url=f"{redirect_url}?error={str(e)}")


async def _get_google_user_info(code: str) -> dict:
    """Exchange Google code for user info"""
    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": f"{settings.API_BASE_URL}/auth/oauth/callback",
                "grant_type": "authorization_code"
            }
        )
        tokens = token_response.json()
        
        # Get user info
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        return user_response.json()


async def _get_microsoft_user_info(code: str) -> dict:
    """Exchange Microsoft code for user info"""
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            data={
                "code": code,
                "client_id": settings.MICROSOFT_CLIENT_ID,
                "client_secret": settings.MICROSOFT_CLIENT_SECRET,
                "redirect_uri": f"{settings.API_BASE_URL}/auth/oauth/callback",
                "grant_type": "authorization_code",
                "scope": "openid email profile"
            }
        )
        tokens = token_response.json()
        
        user_response = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        user_data = user_response.json()
        return {
            "email": user_data.get("mail") or user_data.get("userPrincipalName"),
            "name": user_data.get("displayName"),
            "picture": None
        }


async def _get_facebook_user_info(code: str) -> dict:
    """Exchange Facebook code for user info"""
    async with httpx.AsyncClient() as client:
        token_response = await client.get(
            "https://graph.facebook.com/v18.0/oauth/access_token",
            params={
                "code": code,
                "client_id": settings.FACEBOOK_APP_ID,
                "client_secret": settings.FACEBOOK_APP_SECRET,
                "redirect_uri": f"{settings.API_BASE_URL}/auth/oauth/callback"
            }
        )
        tokens = token_response.json()
        
        user_response = await client.get(
            "https://graph.facebook.com/me",
            params={
                "fields": "id,name,email,picture",
                "access_token": tokens['access_token']
            }
        )
        user_data = user_response.json()
        return {
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "picture": user_data.get("picture", {}).get("data", {}).get("url")
        }
