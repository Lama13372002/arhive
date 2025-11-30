"""Order service."""

from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from models.order import Order, OrderStatus
from models.lyrics_version import LyricsVersion
from models.audio_asset import AudioAsset
from models.payment import Payment
from schemas.order import OrderCreate, OrderUpdate, LyricsGenerateRequest, LyricsEditRequest
from .lyrics_service import LyricsService

from core.database import get_db


class OrderService:
    """Order service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.lyrics_service = LyricsService(db)
    
    async def create_order(self, user_id: int, order_data: OrderCreate) -> Order:
        """Create a new order."""
        order = Order(
            user_id=user_id,
            language=order_data.language,
            genre=order_data.genre,
            mood=order_data.mood,
            tempo=order_data.tempo,
            occasion=order_data.occasion,
            recipient=order_data.recipient,
            notes=order_data.notes,
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID with related data."""
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.lyrics_versions),
                selectinload(Order.audio_assets),
                selectinload(Order.payments)
            )
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_orders(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[Order], int]:
        """Get user's orders with pagination."""
        
        # Build query
        query = select(Order).where(Order.user_id == user_id)
        
        if status:
            try:
                order_status = OrderStatus(status)
                query = query.where(Order.status == order_status)
            except ValueError:
                pass  # Invalid status, ignore filter
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get orders with pagination
        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        return list(orders), total
    
    async def update_order(self, order_id: int, order_data: OrderUpdate) -> Order:
        """Update order."""
        order = await self.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Update fields
        update_data = order_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def generate_lyrics(self, order_id: int, request: LyricsGenerateRequest) -> str:
        """Generate lyrics for order."""
        order = await self.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Update order status
        order.status = OrderStatus.PENDING_LYRICS
        await self.db.commit()
        
        # Start lyrics generation task
        task_id = await self.lyrics_service.generate_lyrics_async(order_id, request)
        
        return task_id
    
    async def get_latest_lyrics(self, order_id: int) -> Optional[LyricsVersion]:
        """Get latest lyrics version for order."""
        result = await self.db.execute(
            select(LyricsVersion)
            .where(LyricsVersion.order_id == order_id)
            .order_by(LyricsVersion.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def submit_lyrics_edit(self, order_id: int, request: LyricsEditRequest) -> LyricsVersion:
        """Submit edited lyrics."""
        order = await self.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Get latest version number
        latest = await self.get_latest_lyrics(order_id)
        next_version = (latest.version + 1) if latest else 1
        
        # Create new lyrics version
        lyrics_version = LyricsVersion(
            order_id=order_id,
            version=next_version,
            text=request.text,
            status="ready"
        )
        
        self.db.add(lyrics_version)
        
        # Update order status
        order.status = OrderStatus.LYRICS_READY
        await self.db.commit()
        await self.db.refresh(lyrics_version)
        
        return lyrics_version
    
    async def approve_order(self, order_id: int) -> Order:
        """Approve order for processing."""
        order = await self.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        order.status = OrderStatus.APPROVED
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def create_payment(self, order_id: int) -> Payment:
        """Create payment for order."""
        order = await self.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # For now, create a simple payment record
        # In real implementation, integrate with payment provider
        payment = Payment(
            order_id=order_id,
            provider="stripe",  # Default provider
            amount=order.price or 0,
            currency=order.currency,
            status="pending"
        )
        
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        
        return payment
    
    async def generate_audio(self, order_id: int) -> str:
        """Generate audio for order."""
        order = await self.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Update order status
        order.status = OrderStatus.GENERATING
        await self.db.commit()
        
        # Create audio asset
        audio_asset = AudioAsset(
            order_id=order_id,
            kind="full",
            provider="suno",
            status="queued"
        )
        
        self.db.add(audio_asset)
        await self.db.commit()
        await self.db.refresh(audio_asset)
        
        # Start audio generation task (placeholder)
        # In real implementation, integrate with Suno API
        task_id = f"audio_{audio_asset.id}"
        
        return task_id

