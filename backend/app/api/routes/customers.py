from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Annotated

from app.db.session import get_db
from app.models import User, Customer, CustomerTag, Tag, Activity, Conversation, Order
from app.schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerWithActivity, CustomerListResponse,
    ActivityResponse, CustomerActivityResponse
)
from app.api.deps import get_current_user, PaginationParams

router = APIRouter()


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    pagination: Annotated[PaginationParams, Depends()]
):
    """List all customers"""
    query = select(Customer).where(Customer.team_id == current_user.team_id)
    
    if pagination.search:
        query = query.where(
            Customer.name.ilike(f"%{pagination.search}%") |
            Customer.email.ilike(f"%{pagination.search}%") |
            Customer.phone.ilike(f"%{pagination.search}%")
        )
    
    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()
    
    # Get paginated results
    query = query.order_by(desc(Customer.created_at))
    query = query.offset(pagination.offset).limit(pagination.page_size)
    
    result = await db.execute(query)
    customers = result.scalars().all()
    
    items = []
    for c in customers:
        # Get conversation count
        conv_count = await db.execute(
            select(func.count()).select_from(Conversation).where(
                Conversation.customer_id == c.id
            )
        )
        
        # Get order stats
        order_stats = await db.execute(
            select(
                func.count(Order.id),
                func.coalesce(func.sum(Order.total), 0)
            ).where(Order.customer_id == c.id)
        )
        order_count, total_revenue = order_stats.one()
        
        # Get tags
        tags_result = await db.execute(
            select(Tag).join(CustomerTag).where(CustomerTag.customer_id == c.id)
        )
        tags = [t.name for t in tags_result.scalars().all()]
        
        item = CustomerWithActivity.model_validate(c)
        item.total_conversations = conv_count.scalar()
        item.total_orders = order_count
        item.total_revenue = float(total_revenue)
        item.tags = tags
        items.append(item)
    
    return CustomerListResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get("/{customer_id}", response_model=CustomerWithActivity)
async def get_customer(
    customer_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get customer by ID"""
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Get stats
    conv_count = await db.execute(
        select(func.count()).select_from(Conversation).where(
            Conversation.customer_id == customer.id
        )
    )
    
    order_stats = await db.execute(
        select(
            func.count(Order.id),
            func.coalesce(func.sum(Order.total), 0)
        ).where(Order.customer_id == customer.id)
    )
    order_count, total_revenue = order_stats.one()
    
    tags_result = await db.execute(
        select(Tag).join(CustomerTag).where(CustomerTag.customer_id == customer.id)
    )
    tags = [t.name for t in tags_result.scalars().all()]
    
    response = CustomerWithActivity.model_validate(customer)
    response.total_conversations = conv_count.scalar()
    response.total_orders = order_count
    response.total_revenue = float(total_revenue)
    response.tags = tags
    
    return response


@router.post("", response_model=CustomerResponse)
async def create_customer(
    data: CustomerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Create a new customer"""
    customer = Customer(
        **data.model_dump(),
        team_id=current_user.team_id
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    
    return CustomerResponse.model_validate(customer)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update customer"""
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    await db.commit()
    await db.refresh(customer)
    
    return CustomerResponse.model_validate(customer)


@router.get("/{customer_id}/activity", response_model=CustomerActivityResponse)
async def get_customer_activity(
    customer_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 50
):
    """Get customer activity timeline"""
    result = await db.execute(
        select(Activity)
        .where(Activity.customer_id == customer_id)
        .order_by(desc(Activity.created_at))
        .limit(limit)
    )
    activities = result.scalars().all()
    
    items = []
    for a in activities:
        item = ActivityResponse.model_validate(a)
        if a.user_id:
            user_result = await db.execute(
                select(User).where(User.id == a.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                item.user_name = user.name
        items.append(item)
    
    return CustomerActivityResponse(
        items=items,
        total=len(items)
    )
