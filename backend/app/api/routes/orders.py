from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Annotated
from datetime import datetime
import uuid

from app.db.session import get_db
from app.models import User, Order, OrderTimeline, Customer, OrderStatus
from app.schemas import (
    OrderCreate, OrderUpdate, UpdateOrderStatus, OrderResponse,
    OrderWithCustomer, OrderListResponse, OrderDetailResponse, OrderTimelineItem
)
from app.api.deps import get_current_user, PaginationParams
from app.workers.tasks.order_tasks import process_order_task

router = APIRouter()


@router.get("", response_model=OrderListResponse)
async def list_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    pagination: Annotated[PaginationParams, Depends()],
    status_filter: str = None
):
    """List all orders"""
    query = select(Order).where(Order.team_id == current_user.team_id)
    
    if status_filter:
        query = query.where(Order.status == status_filter)
    
    if pagination.search:
        query = query.where(
            Order.order_number.ilike(f"%{pagination.search}%")
        )
    
    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()
    
    # Get paginated results
    query = query.order_by(desc(Order.created_at))
    query = query.offset(pagination.offset).limit(pagination.page_size)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    items = []
    for o in orders:
        item = OrderWithCustomer.model_validate(o)
        if o.customer_id:
            customer_result = await db.execute(
                select(Customer).where(Customer.id == o.customer_id)
            )
            customer = customer_result.scalar_one_or_none()
            if customer:
                item.customer_name = customer.name
        items.append(item)
    
    return OrderListResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get order by ID"""
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get customer name
    customer_name = None
    if order.customer_id:
        customer_result = await db.execute(
            select(Customer).where(Customer.id == order.customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        if customer:
            customer_name = customer.name
    
    # Get timeline
    timeline_result = await db.execute(
        select(OrderTimeline)
        .where(OrderTimeline.order_id == order.id)
        .order_by(desc(OrderTimeline.created_at))
    )
    timeline = timeline_result.scalars().all()
    
    response = OrderDetailResponse.model_validate(order)
    response.customer_name = customer_name
    response.timeline = [OrderTimelineItem.model_validate(t) for t in timeline]
    
    return response


@router.post("", response_model=OrderResponse)
async def create_order(
    data: OrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Create a new order"""
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in data.items)
    total = subtotal  # Add tax, shipping, discount logic as needed
    
    order = Order(
        order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
        items=[item.model_dump() for item in data.items],
        subtotal=subtotal,
        total=total,
        customer_id=data.customer_id,
        conversation_id=data.conversation_id,
        user_id=current_user.id,
        team_id=current_user.team_id,
        shipping_address=data.shipping_address.model_dump() if data.shipping_address else {},
        billing_address=data.billing_address.model_dump() if data.billing_address else {},
        notes=data.notes
    )
    db.add(order)
    await db.flush()
    
    # Add timeline entry
    timeline = OrderTimeline(
        order_id=order.id,
        action="order_created",
        description="Order created",
        actor_id=current_user.id
    )
    db.add(timeline)
    
    await db.commit()
    await db.refresh(order)
    
    # Queue for processing
    process_order_task.delay(str(order.id))
    
    return OrderResponse.model_validate(order)


@router.post("/update-status", response_model=OrderResponse)
async def update_order_status(
    data: UpdateOrderStatus,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update order status"""
    result = await db.execute(
        select(Order).where(Order.id == data.order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    old_status = order.status
    order.status = OrderStatus(data.status)
    
    # Add timeline entry
    timeline = OrderTimeline(
        order_id=order.id,
        action="status_changed",
        description=f"Status changed from {old_status} to {data.status}",
        actor_id=current_user.id,
        metadata={"old_status": old_status, "new_status": data.status}
    )
    db.add(timeline)
    
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse.model_validate(order)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    data: OrderUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update order details"""
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    
    if "items" in update_data:
        update_data["items"] = [item.model_dump() for item in data.items]
        subtotal = sum(item.price * item.quantity for item in data.items)
        update_data["subtotal"] = subtotal
        update_data["total"] = subtotal
    
    if "shipping_address" in update_data and data.shipping_address:
        update_data["shipping_address"] = data.shipping_address.model_dump()
    
    for field, value in update_data.items():
        setattr(order, field, value)
    
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse.model_validate(order)
