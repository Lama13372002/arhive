"""OpenAI client for lyrics generation."""

import httpx
from typing import Dict, Any, Optional
import structlog

from core.config import settings

logger = structlog.get_logger()


class OpenAIClient:
    """OpenAI API client."""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com/v1"
        self.model = settings.openai_model
    
    async def generate_lyrics(self, prompt_data: Dict[str, Any]) -> str:
        """Generate lyrics using OpenAI."""
        
        messages = [
            {"role": "system", "content": prompt_data["system"]},
            {"role": "user", "content": prompt_data["user"]}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": prompt_data.get("temperature", 0.8),
            "max_tokens": prompt_data.get("max_tokens", 2000),
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code >= 400:
                    logger.error(
                        "OpenAI API error",
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise Exception(f"OpenAI API error: {response.status_code}")
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                logger.info(
                    "Lyrics generated successfully",
                    model=self.model,
                    tokens_used=data.get("usage", {}).get("total_tokens", 0)
                )
                
                return content
                
            except httpx.TimeoutException:
                logger.error("OpenAI API timeout")
                raise Exception("OpenAI API timeout")
            except Exception as e:
                logger.error("OpenAI API error", error=str(e))
                raise Exception(f"OpenAI API error: {str(e)}")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text with custom parameters."""
        
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code >= 400:
                    raise Exception(f"OpenAI API error: {response.status_code}")
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
            except Exception as e:
                logger.error("OpenAI text generation error", error=str(e))
                raise Exception(f"OpenAI API error: {str(e)}")

