"""Security alerts and notifications service"""
from datetime import datetime
from typing import Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.session import AuditLog, UserSession
from app.models import User
from app.core.config import settings

logger = structlog.get_logger()


class SecurityAlertType:
    NEW_DEVICE_LOGIN = "new_device_login"
    FAILED_LOGIN_ATTEMPT = "failed_login_attempt"
    PASSWORD_CHANGED = "password_changed"
    TWO_FACTOR_ENABLED = "2fa_enabled"
    TWO_FACTOR_DISABLED = "2fa_disabled"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SESSION_REVOKED = "session_revoked"
    ALL_SESSIONS_REVOKED = "all_sessions_revoked"
    ACCOUNT_LOCKED = "account_locked"


async def log_security_event(
    db: AsyncSession,
    user_id: Optional[str],
    action: str,
    resource_type: str = "auth",
    resource_id: Optional[str] = None,
    method: Optional[str] = None,
    path: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    old_values: Optional[str] = None,
    new_values: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None,
) -> AuditLog:
    """Create a persistent audit log entry"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        method=method,
        path=path,
        ip_address=ip_address,
        user_agent=user_agent,
        old_values=old_values,
        new_values=new_values,
        success=success,
        error_message=error_message,
    )
    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)
    
    # Log to structured logging as well
    logger.info(
        "security_event",
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        ip_address=ip_address,
        success=success,
    )
    
    return audit_log


async def check_new_device(
    db: AsyncSession,
    user_id: str,
    device_fingerprint: str,
    ip_address: str,
) -> bool:
    """Check if this is a new device for the user"""
    result = await db.execute(
        select(UserSession)
        .where(UserSession.user_id == user_id)
        .where(UserSession.ip_address == ip_address)
    )
    existing_session = result.scalar_one_or_none()
    
    return existing_session is None


async def send_security_alert_email(
    email: str,
    alert_type: str,
    details: dict,
) -> None:
    """
    Send security alert email to user
    In production, integrate with email service (Resend, SendGrid, etc.)
    """
    # TODO: Implement email sending
    # For now, just log the alert
    logger.info(
        "security_alert_email",
        email=email,
        alert_type=alert_type,
        details=details,
    )


async def track_failed_login(
    db: AsyncSession,
    email: str,
    ip_address: str,
    user_agent: Optional[str] = None,
) -> int:
    """
    Track failed login attempts and return count
    Returns the number of recent failed attempts
    """
    # Log the failed attempt
    await log_security_event(
        db=db,
        user_id=None,
        action=SecurityAlertType.FAILED_LOGIN_ATTEMPT,
        resource_type="auth",
        ip_address=ip_address,
        user_agent=user_agent,
        success=False,
        new_values=f'{{"email": "{email}"}}',
    )
    
    # Count recent failed attempts from this IP
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(minutes=15)
    
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.action == SecurityAlertType.FAILED_LOGIN_ATTEMPT)
        .where(AuditLog.ip_address == ip_address)
        .where(AuditLog.created_at > cutoff)
    )
    failed_attempts = len(result.scalars().all())
    
    # If too many failures, trigger lockout alert
    if failed_attempts >= 5:
        logger.warning(
            "account_lockout_triggered",
            email=email,
            ip_address=ip_address,
            failed_attempts=failed_attempts,
        )
    
    return failed_attempts


async def on_successful_login(
    db: AsyncSession,
    user: User,
    ip_address: str,
    user_agent: Optional[str] = None,
    is_new_device: bool = False,
) -> None:
    """Handle successful login - log and send alerts if needed"""
    await log_security_event(
        db=db,
        user_id=str(user.id),
        action="login_success",
        resource_type="auth",
        ip_address=ip_address,
        user_agent=user_agent,
        success=True,
    )
    
    if is_new_device:
        await log_security_event(
            db=db,
            user_id=str(user.id),
            action=SecurityAlertType.NEW_DEVICE_LOGIN,
            resource_type="auth",
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
        )
        
        # Send email alert for new device
        await send_security_alert_email(
            email=user.email,
            alert_type=SecurityAlertType.NEW_DEVICE_LOGIN,
            details={
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


async def on_password_changed(
    db: AsyncSession,
    user: User,
    ip_address: str,
) -> None:
    """Handle password change - log and notify"""
    await log_security_event(
        db=db,
        user_id=str(user.id),
        action=SecurityAlertType.PASSWORD_CHANGED,
        resource_type="user",
        resource_id=str(user.id),
        ip_address=ip_address,
        success=True,
    )
    
    await send_security_alert_email(
        email=user.email,
        alert_type=SecurityAlertType.PASSWORD_CHANGED,
        details={
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def on_2fa_status_changed(
    db: AsyncSession,
    user: User,
    enabled: bool,
    ip_address: str,
) -> None:
    """Handle 2FA enable/disable - log and notify"""
    action = SecurityAlertType.TWO_FACTOR_ENABLED if enabled else SecurityAlertType.TWO_FACTOR_DISABLED
    
    await log_security_event(
        db=db,
        user_id=str(user.id),
        action=action,
        resource_type="user",
        resource_id=str(user.id),
        ip_address=ip_address,
        success=True,
    )
    
    await send_security_alert_email(
        email=user.email,
        alert_type=action,
        details={
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
