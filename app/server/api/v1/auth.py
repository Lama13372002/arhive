"""Authentication endpoints."""

import hashlib
import hmac
import json
import urllib.parse
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.config import settings
from models.user import User
from schemas.auth import TelegramAuthRequest, AuthResponse
from domain.auth_service import AuthService

router = APIRouter()


class TelegramInitData(BaseModel):
    """Telegram WebApp init data."""
    query_id: str
    user: dict
    auth_date: int
    hash: str


def verify_telegram_webapp_data(init_data: str, bot_token: str) -> Optional[TelegramInitData]:
    """Verify Telegram WebApp init data signature."""
    try:
        # Parse init data
        parsed_data = urllib.parse.parse_qs(init_data)
        
        # Extract hash
        received_hash = parsed_data.get('hash', [None])[0]
        if not received_hash:
            return None
        
        # Remove hash from data
        data_check_string_parts = []
        for key, value in parsed_data.items():
            if key != 'hash':
                data_check_string_parts.append(f"{key}={value[0]}")
        
        data_check_string = '\n'.join(sorted(data_check_string_parts))
        
        # Create secret key
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify hash
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None
        
        # Parse user data
        user_data = json.loads(parsed_data.get('user', ['{}'])[0])
        
        return TelegramInitData(
            query_id=parsed_data.get('query_id', [''])[0],
            user=user_data,
            auth_date=int(parsed_data.get('auth_date', ['0'])[0]),
            hash=received_hash
        )
        
    except Exception:
        return None


@router.post("/auth/telegram/verify", response_model=AuthResponse)
async def verify_telegram_auth(
    request: TelegramAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify Telegram WebApp authentication."""
    
    # Verify init data
    init_data = verify_telegram_webapp_data(
        request.init_data,
        settings.telegram_bot_token
    )
    
    if not init_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid Telegram authentication data"
        )
    
    # Get user data
    user_data = init_data.user
    telegram_id = user_data.get('id')
    
    if not telegram_id:
        raise HTTPException(
            status_code=400,
            detail="Missing user ID in Telegram data"
        )
    
    # Get or create user
    auth_service = AuthService(db)
    user = await auth_service.get_or_create_user(
        telegram_id=telegram_id,
        username=user_data.get('username'),
        first_name=user_data.get('first_name'),
        last_name=user_data.get('last_name'),
        language_code=user_data.get('language_code', 'ru')
    )
    
    # Generate JWT token
    token = auth_service.create_access_token(user.id)
    
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user
    )


@router.get("/auth/me")
async def get_current_user(
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get current user information."""
    return current_user

