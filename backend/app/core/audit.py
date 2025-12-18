"""Audit logging middleware and utilities"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import structlog
import json

from app.core.config import settings

logger = structlog.get_logger()


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware to log all user actions for compliance"""
    
    # Endpoints that modify data (require audit logging)
    AUDITABLE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    
    # Sensitive fields to mask in logs
    SENSITIVE_FIELDS = {"password", "token", "secret", "api_key", "access_token", "refresh_token"}
    
    async def dispatch(self, request: Request, call_next):
        # Skip non-auditable requests
        if request.method not in self.AUDITABLE_METHODS:
            return await call_next(request)
        
        # Extract user info from token if available
        user_id = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from app.core.security import decode_token
                token = auth_header[7:]
                payload = decode_token(token)
                user_id = payload.get("sub")
            except Exception:
                pass
        
        # Capture request body (mask sensitive data)
        body = {}
        try:
            body_bytes = await request.body()
            if body_bytes:
                body = json.loads(body_bytes.decode())
                body = self._mask_sensitive_fields(body)
        except Exception:
            pass
        
        # Execute request
        response = await call_next(request)
        
        # Log the audit entry
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("User-Agent"),
            "status_code": response.status_code,
            "request_body": body,
        }
        
        logger.info("audit_log", **audit_entry)
        
        return response
    
    def _mask_sensitive_fields(self, data: dict) -> dict:
        """Mask sensitive fields in data"""
        if not isinstance(data, dict):
            return data
        
        masked = {}
        for key, value in data.items():
            if any(sf in key.lower() for sf in self.SENSITIVE_FIELDS):
                masked[key] = "***REDACTED***"
            elif isinstance(value, dict):
                masked[key] = self._mask_sensitive_fields(value)
            else:
                masked[key] = value
        return masked
