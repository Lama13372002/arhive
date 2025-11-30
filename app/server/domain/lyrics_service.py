"""Lyrics generation service."""

import json
import re
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from models.order import Order
from models.lyrics_version import LyricsVersion
from schemas.order import LyricsGenerateRequest
from integrations.ai.openai_client import OpenAIClient


class LyricsService:
    """Lyrics generation service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = OpenAIClient()
    
    async def generate_lyrics_async(self, order_id: int, request: LyricsGenerateRequest) -> str:
        """Generate lyrics asynchronously (returns task ID)."""
        # In real implementation, this would start a Celery task
        # For now, return a placeholder task ID
        return f"lyrics_task_{order_id}_{hash(str(request))}"
    
    async def generate_lyrics_sync(self, order_id: int, request: LyricsGenerateRequest) -> LyricsVersion:
        """Generate lyrics synchronously."""
        # Get order
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError("Order not found")
        
        # Build prompt
        prompt = self._build_lyrics_prompt(order, request)
        
        # Generate lyrics with OpenAI
        response = await self.openai_client.generate_lyrics(prompt)
        
        # Parse response
        lyrics_data = self._parse_lyrics_response(response)
        
        # Get next version number
        latest = await self._get_latest_lyrics_version(order_id)
        next_version = (latest.version + 1) if latest else 1
        
        # Create lyrics version
        lyrics_version = LyricsVersion(
            order_id=order_id,
            version=next_version,
            text=lyrics_data["text"],
            gpt_model=settings.openai_model,
            prompt_used=lyrics_data.get("prompt_used"),
            tokens_in=lyrics_data.get("tokens_in"),
            tokens_out=lyrics_data.get("tokens_out"),
            quality_score=lyrics_data.get("quality_score"),
            status="ready"
        )
        
        self.db.add(lyrics_version)
        await self.db.commit()
        await self.db.refresh(lyrics_version)
        
        return lyrics_version
    
    def _build_lyrics_prompt(self, order: Order, request: LyricsGenerateRequest) -> Dict[str, Any]:
        """Build lyrics generation prompt."""
        
        # System prompt
        system_prompt = (
            "Ты — профессиональный русско- и казахскоязычный поэт-песенник-редактор. "
            "Строго соблюдай структуру, ритм и чистоту рифм, избегай штампов. "
            "Учитывай повод, адресата и желаемые эмоции. "
            "Текст должен быть оригинальным, без плагиата и без запрещенного контента. "
            "Если пользователь просит что-то спорное — предложи мягкую альтернативу."
        )
        
        # User prompt
        user_prompt = f"""
Цель: персональная песня.
Язык: {order.language.value}
Жанр/стиль: {order.genre or 'поп'}
Настрой: {order.mood or 'романтичный'}
Темп/размер: {order.tempo or 'средний, 90–110 BPM, 4/4'}
Повод: {order.occasion or 'общий'}
Получатель: {order.recipient or 'друг'}
Ключевые фразы: {order.notes or 'нет'}
Структура: 2 куплета по 8–12 строк, припев 4–6 строк (повторяется), при необходимости бридж 4 строки.
Длительность текста: ~60-90 слов.
Тон: искренний, образный, без пошлости.

Отвечай в формате JSON:
{{
  "title": "Короткий заголовок",
  "tags": ["жанр","настрой","повод","язык"],
  "sections": [
    {{"type":"verse","label":"Куплет 1","lines":["...","..."]}},
    {{"type":"chorus","label":"Припев","lines":["...","..."]}},
    {{"type":"verse","label":"Куплет 2","lines":["...","..."]}},
    {{"type":"bridge","label":"Бридж","lines":["...","..."]}},
    {{"type":"chorus","label":"Припев","lines":["...","..."]}}
  ],
  "notes":"краткие пояснения если есть"
}}
""".strip()
        
        return {
            "system": system_prompt,
            "user": user_prompt,
            "model": settings.openai_model,
            "temperature": 0.8,
            "max_tokens": 2000
        }
    
    def _parse_lyrics_response(self, response: str) -> Dict[str, Any]:
        """Parse OpenAI response and convert to lyrics text."""
        try:
            # Try to parse as JSON first
            data = json.loads(response)
            
            # Convert to markdown format
            lines = []
            lines.append(f"# {data.get('title', 'Песня')}")
            lines.append("")
            
            for section in data.get("sections", []):
                section_type = section.get("type", "")
                label = section.get("label", "")
                section_lines = section.get("lines", [])
                
                if section_type == "verse":
                    lines.append(f"**[{label}]**")
                elif section_type == "chorus":
                    lines.append(f"**[{label}]**")
                elif section_type == "bridge":
                    lines.append(f"**[{label}]**")
                
                for line in section_lines:
                    lines.append(line)
                lines.append("")
            
            text = "\n".join(lines)
            
            return {
                "text": text,
                "prompt_used": data,
                "tokens_in": len(response.split()),
                "tokens_out": len(text.split()),
                "quality_score": 0.8  # Placeholder
            }
            
        except json.JSONDecodeError:
            # Fallback: treat as plain text
            return {
                "text": response,
                "prompt_used": None,
                "tokens_in": len(response.split()),
                "tokens_out": len(response.split()),
                "quality_score": 0.6
            }
    
    async def _get_latest_lyrics_version(self, order_id: int) -> Optional[LyricsVersion]:
        """Get latest lyrics version for order."""
        result = await self.db.execute(
            select(LyricsVersion)
            .where(LyricsVersion.order_id == order_id)
            .order_by(LyricsVersion.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

