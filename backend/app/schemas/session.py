"""Session and 2FA schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# 2FA Schemas
class Setup2FAResponse(BaseModel):
    qr_code: str  # Base64 encoded QR code
    provisioning_uri: str
    message: str = "Scan the QR code with your authenticator app"


class Verify2FARequest(BaseModel):
    code: str


class Verify2FAResponse(BaseModel):
    success: bool
    backup_codes: Optional[List[str]] = None
    message: str


class Login2FARequest(BaseModel):
    code: str
    temp_token: str  # Temporary token from initial login


# Session Schemas
class SessionResponse(BaseModel):
    id: UUID
    device_name: Optional[str]
    device_type: Optional[str]
    browser: Optional[str]
    os: Optional[str]
    ip_address: Optional[str]
    country: Optional[str]
    city: Optional[str]
    is_active: bool
    last_activity: datetime
    created_at: datetime
    is_current: bool = False

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    total: int


class RevokeSessionRequest(BaseModel):
    session_id: UUID
    reason: Optional[str] = "User requested revocation"


class RevokeAllSessionsRequest(BaseModel):
    reason: Optional[str] = "User requested revocation of all sessions"


# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    method: Optional[str]
    path: Optional[str]
    ip_address: Optional[str]
    status_code: Optional[str]
    success: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
