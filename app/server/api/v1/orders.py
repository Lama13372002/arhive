"""Orders API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from models.order import Order
from schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse,
    LyricsGenerateRequest, LyricsEditRequest
)
from domain.auth_service import AuthService
from domain.order_service import OrderService

router = APIRouter()


@router.get("/orders", response_model=OrderListResponse)
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's orders with pagination."""
    order_service = OrderService(db)
    
    orders, total = await order_service.get_user_orders(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return OrderListResponse(
        items=orders,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new order."""
    order_service = OrderService(db)
    
    order = await order_service.create_order(
        user_id=current_user.id,
        order_data=order_data
    )
    
    return order


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get order by ID."""
    order_service = OrderService(db)
    
    order = await order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return order


@router.patch("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update order."""
    order_service = OrderService(db)
    
    order = await order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated_order = await order_service.update_order(order_id, order_data)
    
    return updated_order


@router.post("/orders/{order_id}/lyrics/generate")
async def generate_lyrics(
    order_id: int,
    request: LyricsGenerateRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate lyrics for order."""
    order_service = OrderService(db)
    
    order = await order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Start lyrics generation task
    task_id = await order_service.generate_lyrics(order_id, request)
    
    return {"task_id": task_id, "message": "Lyrics generation started"}


@router.get("/orders/{order_id}/lyrics/latest")
async def get_latest_lyrics(
    order_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get latest lyrics version for order."""
    order_service = OrderService(db)
    
    order = await order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    lyrics = await order_service.get_latest_lyrics(order_id)
    
    if not lyrics:
        raise HTTPException(status_code=404, detail="No lyrics found")
    
    return lyrics


@router.post("/orders/{order_id}/lyrics/submit_edit")
async def submit_lyrics_edit(
    order_id: int,
    request: LyricsEditRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit edited lyrics."""
    order_service = OrderService(db)
    
    order = await order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    lyrics = await order_service.submit_lyrics_edit(order_id, request)
    
    return lyrics


@router.post("/orders/{order_id}/approve")
async def approve_order(
    order_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve order for processing."""
    order_service = OrderService(db)
    
    order = await order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated_order = await order_service.approve_order(order_id)
    
    return updated_order


@router.post("/orders/{order_id}/pay")
async def create_payment(
    order_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create payment for order."""
    order_service = OrderService(db)
    
    order = await order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    payment = await order_service.create_payment(order_id)
    
    return payment


@router.post("/orders/{order_id}/generate_audio")
async def generate_audio(
    order_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate audio for order."""
    order_service = OrderService(db)
    
    order = await order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    task_id = await order_service.generate_audio(order_id)
    
    return {"task_id": task_id, "message": "Audio generation started"}

