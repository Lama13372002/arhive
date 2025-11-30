"""Authentication schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from models.user import UserLanguage


class TelegramAuthRequest(BaseModel):
    """Telegram authentication request."""
    init_data: str = Field(..., description="Telegram WebApp init data")


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


class AuthResponse(BaseModel):
    """Authentication response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

