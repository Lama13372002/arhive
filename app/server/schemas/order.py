"""Order schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from models.order import OrderStatus, OrderLanguage, PaymentStatus
from models.lyrics_version import LyricsStatus
from models.audio_asset import AudioKind, AudioStatus


class OrderCreate(BaseModel):
    """Order creation schema."""
    language: OrderLanguage
    genre: Optional[str] = None
    mood: Optional[str] = None
    tempo: Optional[str] = None
    occasion: Optional[str] = None
    recipient: Optional[str] = None
    notes: Optional[str] = None


class OrderUpdate(BaseModel):
    """Order update schema."""
    genre: Optional[str] = None
    mood: Optional[str] = None
    tempo: Optional[str] = None
    occasion: Optional[str] = None
    recipient: Optional[str] = None
    notes: Optional[str] = None


class LyricsResponse(BaseModel):
    """Lyrics response schema."""
    id: int
    version: int
    text: str
    status: LyricsStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class AudioAssetResponse(BaseModel):
    """Audio asset response schema."""
    id: int
    kind: AudioKind
    url: Optional[str] = None
    duration_sec: Optional[float] = None
    status: AudioStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Order response schema."""
    id: int
    status: OrderStatus
    language: OrderLanguage
    genre: Optional[str] = None
    mood: Optional[str] = None
    tempo: Optional[str] = None
    occasion: Optional[str] = None
    recipient: Optional[str] = None
    notes: Optional[str] = None
    price: Optional[Decimal] = None
    currency: str
    payment_status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    
    # Related data
    lyrics_versions: List[LyricsResponse] = []
    audio_assets: List[AudioAssetResponse] = []
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Order list response schema."""
    items: List[OrderResponse]
    total: int
    skip: int
    limit: int


class LyricsGenerateRequest(BaseModel):
    """Lyrics generation request."""
    prompt: Optional[str] = None
    regenerate: bool = False


class LyricsEditRequest(BaseModel):
    """Lyrics edit request."""
    text: str = Field(..., min_length=1, description="Edited lyrics text")

