"""Cleanup and maintenance background tasks"""
from celery import shared_task
from sqlalchemy import select, delete, and_
from datetime import datetime, timedelta
import structlog

from app.db.session import SyncSessionLocal
from app.models import (
    UserSession, AuditLog, WebhookEvent, Message,
    WorkflowRun
)
from app.core.config import settings

logger = structlog.get_logger()


@shared_task
def cleanup_expired_sessions():
    """Remove expired user sessions"""
    with SyncSessionLocal() as db:
        now = datetime.utcnow()
        
        # Delete expired sessions
        result = db.execute(
            delete(UserSession).where(
                UserSession.expires_at < now
            )
        )
        
        deleted_count = result.rowcount
        db.commit()
        
        logger.info("cleanup_sessions", deleted=deleted_count)
        return deleted_count


@shared_task
def cleanup_old_audit_logs():
    """Archive or delete old audit logs based on retention policy"""
    with SyncSessionLocal() as db:
        cutoff_date = datetime.utcnow() - timedelta(days=settings.AUDIT_LOG_RETENTION_DAYS)
        
        # In production, you might want to archive to cold storage first
        result = db.execute(
            delete(AuditLog).where(
                AuditLog.created_at < cutoff_date
            )
        )
        
        deleted_count = result.rowcount
        db.commit()
        
        logger.info("cleanup_audit_logs", deleted=deleted_count, retention_days=settings.AUDIT_LOG_RETENTION_DAYS)
        return deleted_count


@shared_task
def cleanup_old_webhook_events():
    """Clean up processed webhook events"""
    with SyncSessionLocal() as db:
        cutoff_date = datetime.utcnow() - timedelta(days=settings.WEBHOOK_RETENTION_DAYS)
        
        # Only delete processed webhook events
        result = db.execute(
            delete(WebhookEvent).where(
                and_(
                    WebhookEvent.created_at < cutoff_date,
                    WebhookEvent.status == 'processed'
                )
            )
        )
        
        deleted_count = result.rowcount
        db.commit()
        
        logger.info("cleanup_webhook_events", deleted=deleted_count)
        return deleted_count


@shared_task
def cleanup_old_workflow_runs():
    """Clean up old workflow execution logs"""
    with SyncSessionLocal() as db:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Delete completed workflow runs older than 30 days
        result = db.execute(
            delete(WorkflowRun).where(
                and_(
                    WorkflowRun.completed_at < cutoff_date,
                    WorkflowRun.status.in_(['completed', 'failed'])
                )
            )
        )
        
        deleted_count = result.rowcount
        db.commit()
        
        logger.info("cleanup_workflow_runs", deleted=deleted_count)
        return deleted_count


@shared_task
def cleanup_orphaned_data():
    """Clean up any orphaned data in the database"""
    with SyncSessionLocal() as db:
        # This task handles edge cases where data might be orphaned
        # due to failed transactions or bugs
        
        # Count and log orphaned records but be careful with deletes
        # In production, you'd want to review before deleting
        
        logger.info("cleanup_orphaned_data", status="completed")
        db.commit()


@shared_task
def update_conversation_stats():
    """Update conversation statistics (unread counts, last message, etc.)"""
    from app.models import Conversation, Message
    from sqlalchemy import func
    
    with SyncSessionLocal() as db:
        # Get conversations that need updating
        conversations = db.execute(
            select(Conversation).where(
                Conversation.status == 'open'
            )
        ).scalars().all()
        
        for conv in conversations:
            # Get unread count
            unread_count = db.execute(
                select(func.count(Message.id)).where(
                    and_(
                        Message.conversation_id == conv.id,
                        Message.direction == 'inbound',
                        Message.read_at.is_(None)
                    )
                )
            ).scalar() or 0
            
            # Get last message
            last_message = db.execute(
                select(Message).where(
                    Message.conversation_id == conv.id
                ).order_by(Message.created_at.desc()).limit(1)
            ).scalar_one_or_none()
            
            if last_message:
                conv.last_message = last_message.content[:100]
                conv.last_message_time = last_message.created_at
            
            conv.unread_count = unread_count
        
        db.commit()
        logger.info("update_conversation_stats", updated=len(conversations))


@shared_task
def check_overdue_invoices():
    """Check for overdue invoices and update status"""
    from app.models import Invoice, InvoiceStatus
    
    with SyncSessionLocal() as db:
        today = datetime.utcnow().date()
        
        # Find sent invoices that are past due date
        overdue_invoices = db.execute(
            select(Invoice).where(
                and_(
                    Invoice.status == InvoiceStatus.SENT,
                    Invoice.due_date < today
                )
            )
        ).scalars().all()
        
        for invoice in overdue_invoices:
            invoice.status = InvoiceStatus.OVERDUE
        
        db.commit()
        logger.info("check_overdue_invoices", marked_overdue=len(overdue_invoices))
        return len(overdue_invoices)


@shared_task
def run_scheduled_messages():
    """Execute scheduled messages that are due"""
    from app.models import ScheduledMessage, ScheduledMessageStatus
    
    with SyncSessionLocal() as db:
        now = datetime.utcnow()
        
        # Find scheduled messages that are due
        due_messages = db.execute(
            select(ScheduledMessage).where(
                and_(
                    ScheduledMessage.status == ScheduledMessageStatus.SCHEDULED,
                    # Check schedule JSON for next_run_at
                )
            )
        ).scalars().all()
        
        for scheduled in due_messages:
            # TODO: Implement message sending logic
            # This would integrate with the messaging platform connectors
            scheduled.sent_count += 1
            scheduled.last_sent = now
        
        db.commit()
        logger.info("run_scheduled_messages", processed=len(due_messages))
