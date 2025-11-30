"""Payment model."""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
import enum

from core.database import Base


class PaymentProvider(str, enum.Enum):
    """Payment provider enum."""
    STRIPE = "stripe"
    KASPI = "kaspi"
    YUKASSA = "yukassa"


class PaymentStatus(str, enum.Enum):
    """Payment status enum."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class Payment(Base):
    """Payment model."""
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    provider = Column(Enum(PaymentProvider), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    external_id = Column(String(255), nullable=True, index=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, provider={self.provider}, status={self.status})>"

