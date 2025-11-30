"""Audit event model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from core.database import Base


class AuditEvent(Base):
    """Audit event model for tracking all important events."""
    
    __tablename__ = "events_audit"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    type = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="audit_events")
    user = relationship("User", back_populates="audit_events")
    
    def __repr__(self):
        return f"<AuditEvent(id={self.id}, type={self.type}, order_id={self.order_id}, user_id={self.user_id})>"

