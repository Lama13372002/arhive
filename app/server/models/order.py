"""Order model."""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Numeric, JSON
from sqlalchemy.orm import relationship
import enum

from core.database import Base


class OrderStatus(str, enum.Enum):
    """Order status enum."""
    DRAFT = "draft"
    PENDING_LYRICS = "pending_lyrics"
    LYRICS_READY = "lyrics_ready"
    USER_EDITING = "user_editing"
    APPROVED = "approved"
    GENERATING = "generating"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class OrderLanguage(str, enum.Enum):
    """Order language enum."""
    RU = "ru"
    KZ = "kz"
    EN = "en"


class PaymentStatus(str, enum.Enum):
    """Payment status enum."""
    NONE = "none"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(Base):
    """Order model."""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.DRAFT, nullable=False, index=True)
    language = Column(Enum(OrderLanguage), nullable=False)
    genre = Column(String(100), nullable=True)
    mood = Column(String(100), nullable=True)
    tempo = Column(String(100), nullable=True)
    occasion = Column(String(255), nullable=True)
    recipient = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.NONE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Additional metadata
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    lyrics_versions = relationship("LyricsVersion", back_populates="order", cascade="all, delete-orphan")
    audio_assets = relationship("AudioAsset", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="order")
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status})>"

