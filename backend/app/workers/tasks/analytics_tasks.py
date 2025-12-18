"""Analytics background tasks"""
from celery import shared_task
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from decimal import Decimal

from app.db.session import SyncSessionLocal
from app.models import (
    AnalyticsSnapshot, Message, Conversation, Order,
    MessageDirection, Platform
)


@shared_task
def generate_daily_analytics():
    """Generate daily analytics snapshots for all teams"""
    with SyncSessionLocal() as db:
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        yesterday_start = datetime.combine(yesterday, datetime.min.time())
        yesterday_end = datetime.combine(yesterday, datetime.max.time())
        
        # Get all unique team IDs from conversations
        team_ids = db.execute(
            select(Conversation.team_id).distinct()
        ).scalars().all()
        
        for team_id in team_ids:
            if not team_id:
                continue
            
            # Check if snapshot already exists
            existing = db.execute(
                select(AnalyticsSnapshot).where(
                    AnalyticsSnapshot.team_id == team_id,
                    AnalyticsSnapshot.period_type == 'daily',
                    AnalyticsSnapshot.period_start == yesterday
                )
            ).scalar_one_or_none()
            
            if existing:
                continue
            
            # Messages sent
            messages_sent = db.execute(
                select(func.count(Message.id)).select_from(Message).join(Conversation).where(
                    Conversation.team_id == team_id,
                    Message.direction == MessageDirection.OUTBOUND,
                    Message.created_at >= yesterday_start,
                    Message.created_at <= yesterday_end
                )
            ).scalar() or 0
            
            # Messages received
            messages_received = db.execute(
                select(func.count(Message.id)).select_from(Message).join(Conversation).where(
                    Conversation.team_id == team_id,
                    Message.direction == MessageDirection.INBOUND,
                    Message.created_at >= yesterday_start,
                    Message.created_at <= yesterday_end
                )
            ).scalar() or 0
            
            # Conversations opened
            conversations_opened = db.execute(
                select(func.count(Conversation.id)).where(
                    Conversation.team_id == team_id,
                    Conversation.created_at >= yesterday_start,
                    Conversation.created_at <= yesterday_end
                )
            ).scalar() or 0
            
            # Conversations closed
            conversations_closed = db.execute(
                select(func.count(Conversation.id)).where(
                    Conversation.team_id == team_id,
                    Conversation.closed_at >= yesterday_start,
                    Conversation.closed_at <= yesterday_end
                )
            ).scalar() or 0
            
            # Orders created
            orders_created = db.execute(
                select(func.count(Order.id)).where(
                    Order.team_id == team_id,
                    Order.created_at >= yesterday_start,
                    Order.created_at <= yesterday_end
                )
            ).scalar() or 0
            
            # Revenue
            revenue = db.execute(
                select(func.sum(Order.total)).where(
                    Order.team_id == team_id,
                    Order.created_at >= yesterday_start,
                    Order.created_at <= yesterday_end
                )
            ).scalar() or Decimal(0)
            
            # Platform distribution
            platform_counts = db.execute(
                select(
                    Message.platform,
                    func.count(Message.id).label('count')
                ).select_from(Message).join(Conversation).where(
                    Conversation.team_id == team_id,
                    Message.created_at >= yesterday_start,
                    Message.created_at <= yesterday_end
                ).group_by(Message.platform)
            ).all()
            
            platform_distribution = {
                str(row.platform.value): row.count for row in platform_counts
            }
            
            # Create snapshot
            snapshot = AnalyticsSnapshot(
                team_id=team_id,
                period_type='daily',
                period_start=yesterday,
                period_end=yesterday,
                messages_sent=messages_sent,
                messages_received=messages_received,
                conversations_opened=conversations_opened,
                conversations_closed=conversations_closed,
                orders_created=orders_created,
                revenue=revenue,
                platform_distribution=platform_distribution
            )
            db.add(snapshot)
        
        db.commit()


@shared_task
def generate_weekly_analytics():
    """Generate weekly analytics snapshots"""
    with SyncSessionLocal() as db:
        today = datetime.utcnow().date()
        # Get last Monday
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        week_start = datetime.combine(last_monday, datetime.min.time())
        week_end = datetime.combine(last_sunday, datetime.max.time())
        
        # Get all unique team IDs
        team_ids = db.execute(
            select(Conversation.team_id).distinct()
        ).scalars().all()
        
        for team_id in team_ids:
            if not team_id:
                continue
            
            # Check if snapshot already exists
            existing = db.execute(
                select(AnalyticsSnapshot).where(
                    AnalyticsSnapshot.team_id == team_id,
                    AnalyticsSnapshot.period_type == 'weekly',
                    AnalyticsSnapshot.period_start == last_monday
                )
            ).scalar_one_or_none()
            
            if existing:
                continue
            
            # Aggregate daily snapshots
            daily_snapshots = db.execute(
                select(AnalyticsSnapshot).where(
                    AnalyticsSnapshot.team_id == team_id,
                    AnalyticsSnapshot.period_type == 'daily',
                    AnalyticsSnapshot.period_start >= last_monday,
                    AnalyticsSnapshot.period_end <= last_sunday
                )
            ).scalars().all()
            
            if not daily_snapshots:
                continue
            
            # Sum up metrics
            messages_sent = sum(s.messages_sent or 0 for s in daily_snapshots)
            messages_received = sum(s.messages_received or 0 for s in daily_snapshots)
            conversations_opened = sum(s.conversations_opened or 0 for s in daily_snapshots)
            conversations_closed = sum(s.conversations_closed or 0 for s in daily_snapshots)
            orders_created = sum(s.orders_created or 0 for s in daily_snapshots)
            revenue = sum(s.revenue or Decimal(0) for s in daily_snapshots)
            
            snapshot = AnalyticsSnapshot(
                team_id=team_id,
                period_type='weekly',
                period_start=last_monday,
                period_end=last_sunday,
                messages_sent=messages_sent,
                messages_received=messages_received,
                conversations_opened=conversations_opened,
                conversations_closed=conversations_closed,
                orders_created=orders_created,
                revenue=revenue
            )
            db.add(snapshot)
        
        db.commit()


@shared_task
def calculate_response_times():
    """Calculate average response times for conversations"""
    with SyncSessionLocal() as db:
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        yesterday_start = datetime.combine(yesterday, datetime.min.time())
        yesterday_end = datetime.combine(yesterday, datetime.max.time())
        
        # Get conversations with messages from yesterday
        conversations = db.execute(
            select(Conversation).where(
                Conversation.updated_at >= yesterday_start,
                Conversation.updated_at <= yesterday_end
            )
        ).scalars().all()
        
        for conv in conversations:
            # Get messages for this conversation
            messages = db.execute(
                select(Message).where(
                    Message.conversation_id == conv.id,
                    Message.created_at >= yesterday_start,
                    Message.created_at <= yesterday_end
                ).order_by(Message.created_at)
            ).scalars().all()
            
            response_times = []
            last_inbound = None
            
            for msg in messages:
                if msg.direction == MessageDirection.INBOUND:
                    last_inbound = msg.created_at
                elif msg.direction == MessageDirection.OUTBOUND and last_inbound:
                    response_time = (msg.created_at - last_inbound).total_seconds()
                    response_times.append(response_time)
                    last_inbound = None
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                # Store in metadata or update analytics snapshot
                # This is a simplified version
        
        db.commit()
