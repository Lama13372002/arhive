"""User schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from models.user import UserLanguage


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    locale: UserLanguage
    created_at: datetime
    
    class Config:
        from_attributes = True

