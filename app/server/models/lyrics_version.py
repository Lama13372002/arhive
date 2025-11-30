"""Lyrics version model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
import enum

from core.database import Base


class LyricsStatus(str, enum.Enum):
    """Lyrics status enum."""
    DRAFT = "draft"
    READY = "ready"
    REJECTED = "rejected"


class LyricsVersion(Base):
    """Lyrics version model."""
    
    __tablename__ = "lyrics_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    gpt_model = Column(String(100), nullable=True)
    prompt_used = Column(JSON, nullable=True)
    tokens_in = Column(Integer, nullable=True)
    tokens_out = Column(Integer, nullable=True)
    quality_score = Column(Float, nullable=True)
    status = Column(Enum(LyricsStatus), default=LyricsStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="lyrics_versions")
    
    def __repr__(self):
        return f"<LyricsVersion(id={self.id}, order_id={self.order_id}, version={self.version})>"

