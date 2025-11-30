"""Audio asset model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
import enum

from core.database import Base


class AudioKind(str, enum.Enum):
    """Audio kind enum."""
    PREVIEW = "preview"
    FULL = "full"


class AudioProvider(str, enum.Enum):
    """Audio provider enum."""
    NONE = "none"
    SUNO = "suno"
    INNER = "inner"


class AudioStatus(str, enum.Enum):
    """Audio status enum."""
    QUEUED = "queued"
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


class AudioAsset(Base):
    """Audio asset model."""
    
    __tablename__ = "audio_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    kind = Column(Enum(AudioKind), nullable=False)
    url = Column(String(500), nullable=True)
    duration_sec = Column(Float, nullable=True)
    provider = Column(Enum(AudioProvider), default=AudioProvider.NONE, nullable=False)
    meta = Column(JSON, nullable=True)
    status = Column(Enum(AudioStatus), default=AudioStatus.QUEUED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="audio_assets")
    
    def __repr__(self):
        return f"<AudioAsset(id={self.id}, order_id={self.order_id}, kind={self.kind}, status={self.status})>"

