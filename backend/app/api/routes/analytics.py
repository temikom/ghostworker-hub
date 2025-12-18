from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Annotated
from datetime import date, timedelta

from app.db.session import get_db
from app.models import User, AnalyticsSnapshot, Message, Order, Customer, OrderStatus
from app.schemas import (
    MessageAnalytics, ResponseTimeAnalytics, ChannelDistribution,
    TopCustomer, OrdersSummary, AnalyticsDashboard
)
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/messages")
async def get_message_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    start_date: date = Query(default=None),
    end_date: date = Query(default=None)
):
    """Get messages per day analytics"""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    result = await db.execute(
        select(AnalyticsSnapshot)
        .where(
            AnalyticsSnapshot.team_id == current_user.team_id,
            AnalyticsSnapshot.date >= start_date,
            AnalyticsSnapshot.date <= end_date
        )
        .order_by(AnalyticsSnapshot.date)
    )
    snapshots = result.scalars().all()
    
    return [
        MessageAnalytics(
            date=str(s.date),
            total=s.total_messages,
            inbound=s.inbound_messages,
            outbound=s.outbound_messages,
            whatsapp=s.whatsapp_messages,
            instagram=s.instagram_messages,
            tiktok=s.tiktok_messages,
            email=s.email_messages
        )
        for s in snapshots
    ]


@router.get("/response-time")
async def get_response_time_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get response time metrics"""
    # Get latest snapshot
    result = await db.execute(
        select(AnalyticsSnapshot)
        .where(AnalyticsSnapshot.team_id == current_user.team_id)
        .order_by(AnalyticsSnapshot.date.desc())
        .limit(1)
    )
    snapshot = result.scalar_one_or_none()
    
    if not snapshot:
        return ResponseTimeAnalytics(
            avg_response_time_seconds=0,
            avg_first_response_time_seconds=0,
            trend="stable"
        )
    
    return ResponseTimeAnalytics(
        avg_response_time_seconds=snapshot.avg_response_time_seconds or 0,
        avg_first_response_time_seconds=snapshot.avg_first_response_time_seconds or 0,
        trend="stable"  # Calculate trend from historical data
    )


@router.get("/channels")
async def get_channel_distribution(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get channel distribution"""
    # Get last 30 days
    start_date = date.today() - timedelta(days=30)
    
    result = await db.execute(
        select(
            func.sum(AnalyticsSnapshot.whatsapp_messages),
            func.sum(AnalyticsSnapshot.instagram_messages),
            func.sum(AnalyticsSnapshot.tiktok_messages),
            func.sum(AnalyticsSnapshot.email_messages)
        ).where(
            AnalyticsSnapshot.team_id == current_user.team_id,
            AnalyticsSnapshot.date >= start_date
        )
    )
    row = result.one()
    
    whatsapp = int(row[0] or 0)
    instagram = int(row[1] or 0)
    tiktok = int(row[2] or 0)
    email = int(row[3] or 0)
    
    return ChannelDistribution(
        whatsapp=whatsapp,
        instagram=instagram,
        tiktok=tiktok,
        email=email,
        total=whatsapp + instagram + tiktok + email
    )


@router.get("/customers")
async def get_top_customers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 10
):
    """Get top customers by activity"""
    # This would ideally be aggregated in analytics snapshots
    result = await db.execute(
        select(Customer)
        .where(Customer.team_id == current_user.team_id)
        .limit(limit)
    )
    customers = result.scalars().all()
    
    top_customers = []
    for c in customers:
        # Get order stats
        order_result = await db.execute(
            select(
                func.count(Order.id),
                func.coalesce(func.sum(Order.total), 0)
            ).where(Order.customer_id == c.id)
        )
        order_count, revenue = order_result.one()
        
        # Get message count (simplified)
        top_customers.append(TopCustomer(
            id=c.id,
            name=c.name,
            message_count=0,  # Would need to aggregate from messages
            order_count=order_count,
            total_revenue=float(revenue)
        ))
    
    return sorted(top_customers, key=lambda x: x.total_revenue, reverse=True)


@router.get("/orders")
async def get_orders_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get orders summary"""
    # Get counts by status
    result = await db.execute(
        select(Order.status, func.count(Order.id), func.sum(Order.total))
        .where(Order.team_id == current_user.team_id)
        .group_by(Order.status)
    )
    rows = result.all()
    
    summary = {
        "pending": 0,
        "processing": 0,
        "shipped": 0,
        "delivered": 0,
        "cancelled": 0
    }
    total_orders = 0
    total_revenue = 0
    
    for status, count, revenue in rows:
        summary[status.value] = count
        total_orders += count
        if status != OrderStatus.CANCELLED:
            total_revenue += float(revenue or 0)
    
    return OrdersSummary(
        total_orders=total_orders,
        total_revenue=total_revenue,
        **summary
    )


@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get complete analytics dashboard"""
    messages = await get_message_analytics(db, current_user)
    response_time = await get_response_time_analytics(db, current_user)
    channels = await get_channel_distribution(db, current_user)
    top_customers = await get_top_customers(db, current_user, limit=5)
    orders = await get_orders_summary(db, current_user)
    
    return AnalyticsDashboard(
        messages_per_day=messages,
        response_time=response_time,
        channel_distribution=channels,
        top_customers=top_customers,
        orders_summary=orders
    )
