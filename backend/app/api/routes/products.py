"""Products API routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models import Product, User

router = APIRouter()


@router.get("")
async def list_products(
    category: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all products"""
    query = select(Product).where(Product.team_id == current_user.team_id)
    if category:
        query = query.where(Product.category == category)
    if is_active is not None:
        query = query.where(Product.is_active == is_active)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("")
async def create_product(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product"""
    product = Product(team_id=current_user.team_id, **data)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/{product_id}")
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific product"""
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.team_id == current_user.team_id
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}")
async def update_product(
    product_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a product"""
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.team_id == current_user.team_id
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in data.items():
        if hasattr(product, key):
            setattr(product, key, value)
    
    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a product"""
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.team_id == current_user.team_id
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.delete(product)
    await db.commit()
    return {"success": True}
