"""Suno API client for audio generation."""

import httpx
import json
from typing import Dict, Any, Optional, List
import structlog

from core.config import settings

logger = structlog.get_logger()


class SunoClient:
    """Suno API client."""
    
    def __init__(self):
        self.api_key = settings.suno_api_key
        self.base_url = settings.suno_api_base
        self.enabled = settings.use_suno
    
    async def generate_music(
        self,
        lyrics: str,
        prompt: str,
        title: str,
        style: str,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate music using Suno API."""
        
        if not self.enabled:
            raise Exception("Suno integration is disabled")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Try custom mode first
        custom_payload = {
            "customMode": True,
            "instrumental": False,
            "title": title,
            "style": style,
            "prompt": lyrics,  # In custom mode, prompt = lyrics
            "model": "V4_5"
        }
        
        if callback_url:
            custom_payload["callBackUrl"] = callback_url
        
        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/generate",
                    headers=headers,
                    json=custom_payload
                )
                
                if 200 <= response.status_code < 300:
                    try:
                        data = response.json()
                        code = data.get("code")
                        if code in (None, 200):
                            task_id = (data.get("data") or {}).get("taskId") or data.get("taskId")
                            if task_id:
                                logger.info("Suno custom mode generation started", task_id=task_id)
                                return {
                                    "task_id": task_id,
                                    "mode": "custom",
                                    "status": "queued"
                                }
                    except Exception as e:
                        logger.warning("Suno custom mode parse error, falling back", error=str(e))
                
                # Fallback to non-custom mode
                non_custom_payload = {
                    "customMode": False,
                    "instrumental": False,
                    "prompt": prompt[:400],  # Limit prompt length
                    "model": "V4_5"
                }
                
                if callback_url:
                    non_custom_payload["callBackUrl"] = callback_url
                
                response = await client.post(
                    f"{self.base_url}/api/v1/generate",
                    headers=headers,
                    json=non_custom_payload
                )
                
                if response.status_code >= 400:
                    raise Exception(f"Suno API error: {response.status_code} - {response.text}")
                
                data = response.json()
                code = data.get("code")
                if code not in (None, 200):
                    raise Exception(f"Suno error code={code}: {data.get('msg') or data.get('message')}")
                
                task_id = (data.get("data") or {}).get("taskId") or data.get("taskId")
                if not task_id:
                    raise Exception(f"Suno response without taskId: {data}")
                
                logger.info("Suno non-custom mode generation started", task_id=task_id)
                return {
                    "task_id": task_id,
                    "mode": "non-custom",
                    "status": "queued"
                }
                
            except httpx.TimeoutException:
                logger.error("Suno API timeout")
                raise Exception("Suno API timeout")
            except Exception as e:
                logger.error("Suno API error", error=str(e))
                raise Exception(f"Suno API error: {str(e)}")
    
    async def get_record_info(self, task_id: str) -> Dict[str, Any]:
        """Get record information by task ID."""
        
        if not self.enabled:
            raise Exception("Suno integration is disabled")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/generate/record-info",
                    headers=headers,
                    params={"taskId": task_id}
                )
                
                if response.status_code >= 400:
                    logger.warning("Suno record info error", status_code=response.status_code)
                    return {"status": "error", "message": "Failed to get record info"}
                
                data = response.json()
                logger.info("Suno record info retrieved", task_id=task_id)
                
                return data
                
            except httpx.TimeoutException:
                logger.error("Suno record info timeout", task_id=task_id)
                return {"status": "timeout"}
            except Exception as e:
                logger.error("Suno record info error", error=str(e), task_id=task_id)
                return {"status": "error", "message": str(e)}
    
    def extract_audio_urls(self, data: Any) -> List[str]:
        """Extract audio URLs from Suno response."""
        urls = []
        
        if isinstance(data, dict):
            for key in ["audioUrl", "downloadUrl", "streamUrl"]:
                value = data.get(key)
                if isinstance(value, str) and value.startswith("http"):
                    urls.append(value)
            
            # Recursively search in nested objects
            for value in data.values():
                urls.extend(self.extract_audio_urls(value))
        
        elif isinstance(data, list):
            for item in data:
                urls.extend(self.extract_audio_urls(item))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    async def poll_generation_status(
        self,
        task_id: str,
        timeout_seconds: int = 420,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """Poll generation status until completion or timeout."""
        
        import asyncio
        
        deadline = asyncio.get_event_loop().time() + timeout_seconds
        sent_any = False
        
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(poll_interval)
            
            try:
                data = await self.get_record_info(task_id)
                
                if data.get("status") == "error":
                    continue
                
                urls = self.extract_audio_urls(data.get("data", {}))
                
                if urls:
                    logger.info("Suno generation completed", task_id=task_id, urls_count=len(urls))
                    return {
                        "status": "completed",
                        "task_id": task_id,
                        "audio_urls": urls[:4],  # Limit to 4 versions
                        "data": data
                    }
                
            except Exception as e:
                logger.warning("Suno polling error", error=str(e), task_id=task_id)
                continue
        
        logger.warning("Suno generation timeout", task_id=task_id, timeout=timeout_seconds)
        return {
            "status": "timeout",
            "task_id": task_id,
            "message": f"Generation timeout after {timeout_seconds} seconds"
        }

